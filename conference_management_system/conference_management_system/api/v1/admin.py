import frappe
from conference_management_system.conference_management_system.utils.api_logger import log_api_call
from conference_management_system.conference_management_system.utils.error_handler import handle_api_error


@frappe.whitelist()
@log_api_call
@handle_api_error
def get_user_roles():
    """Get current user roles"""
    try:
        user = frappe.session.user
        
        # Validate user session
        if not user:
            return {
                "success": False,
                "error": "No active user session"
            }
        
        try:
            roles = frappe.get_roles(user)
            if not roles:
                roles = []
        except Exception as role_error:
            frappe.log_error(f"Error fetching user roles: {str(role_error)}", "Admin API")
            roles = []
        
        return {
            "success": True,
            "data": {
                "is_guest": user == "Guest",
                "has_attendee_role": "Attendee" in roles
            }
        }
    except Exception as e:
        frappe.log_error(f"Unexpected error in get_user_roles: {str(e)}", "Admin API")
        return {
            "success": False,
            "error": "Failed to fetch user roles"
        }

@frappe.whitelist()
@log_api_call
@handle_api_error
def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        # Initialize default values
        stats = {
            "conferences": 0,
            "sessions": 0,
            "registrations": 0,
            "active_conferences": 0,
            "total_revenue": 0,
            "processing_fees": 0,
            "net_revenue": 0,
            "email_logs": 0,
            "recent_emails": 0,
            "api_logs": 0,
            "recent_api_calls": 0
        }
        
        # Get basic counts with error handling
        try:
            stats["conferences"] = frappe.db.count("Conference")
        except Exception as e:
            frappe.log_error(f"Error counting conferences: {str(e)}", "Admin API")
        
        try:
            stats["sessions"] = frappe.db.count("Session")
        except Exception as e:
            frappe.log_error(f"Error counting sessions: {str(e)}", "Admin API")
        
        try:
            stats["registrations"] = frappe.db.count("Registration")
        except Exception as e:
            frappe.log_error(f"Error counting registrations: {str(e)}", "Admin API")
        
        try:
            stats["active_conferences"] = frappe.db.count("Conference", {"status": ["in", ["Upcoming", "Ongoing"]]})
        except Exception as e:
            frappe.log_error(f"Error counting active conferences: {str(e)}", "Admin API")
        
        # Get payment statistics with error handling
        try:
            payment_details = frappe.get_all("Mock Payment Details", 
                filters={"payment_status": "Success"},
                fields=["amount", "processing_fee", "net_amount"])
            
            if payment_details:
                stats["total_revenue"] = sum(float(pd.get('amount', 0) or 0) for pd in payment_details)
                stats["processing_fees"] = sum(float(pd.get('processing_fee', 0) or 0) for pd in payment_details)
                stats["net_revenue"] = sum(float(pd.get('net_amount', 0) or 0) for pd in payment_details)
        except Exception as e:
            frappe.log_error(f"Error calculating payment statistics: {str(e)}", "Admin API")
        
        # Get email statistics with error handling
        try:
            stats["email_logs"] = frappe.db.count("Mock Email Log")
        except Exception as e:
            frappe.log_error(f"Error counting email logs: {str(e)}", "Admin API")
        
        try:
            seven_days_ago = frappe.utils.add_days(frappe.utils.nowdate(), -7)
            stats["recent_emails"] = frappe.db.count("Mock Email Log", {"sent_date": [">=", seven_days_ago]})
        except Exception as e:
            frappe.log_error(f"Error counting recent emails: {str(e)}", "Admin API")
        
        # Get API usage with error handling
        try:
            stats["api_logs"] = frappe.db.count("API Log")
        except Exception as e:
            frappe.log_error(f"Error counting API logs: {str(e)}", "Admin API")
        
        try:
            yesterday = frappe.utils.add_days(frappe.utils.nowdate(), -1)
            stats["recent_api_calls"] = frappe.db.count("API Log", {"timestamp": [">=", yesterday]})
        except Exception as e:
            frappe.log_error(f"Error counting recent API calls: {str(e)}", "Admin API")
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        frappe.log_error(f"Unexpected error in get_dashboard_stats: {str(e)}", "Admin API")
        return {
            "success": False,
            "error": "Failed to fetch dashboard statistics"
        }

@frappe.whitelist()
@log_api_call
@handle_api_error
def get_recent_registrations():
    """Get recent registrations with payment details"""
    try:
        registrations = []
        try:
            registrations = frappe.db.sql("""
                SELECT r.name, r.registration_date, r.payment_status, r.amount, r.payment_details,
                       c.conference_name, s.session_name, a.attendee_name, a.email as attendee_email,
                       p.payment_method, p.transaction_id
                FROM `tabRegistration` r
                LEFT JOIN `tabConference` c ON r.conference = c.name
                LEFT JOIN `tabSession` s ON r.session = s.name
                LEFT JOIN `tabAttendee` a ON r.attendee = a.name
                LEFT JOIN `tabMock Payment Details` p ON r.payment_details = p.name
                ORDER BY r.creation DESC
                LIMIT 10
            """, as_dict=True)
            
            # Sanitize data
            for reg in registrations:
                for key, value in reg.items():
                    if value is None:
                        reg[key] = ''
                        
        except Exception as sql_error:
            frappe.log_error(f"SQL error in get_recent_registrations: {str(sql_error)}", "Admin API")
            registrations = []
        
        return {
            "success": True,
            "data": registrations,
            "message": f"Found {len(registrations)} recent registrations"
        }
    except Exception as e:
        frappe.log_error(f"Unexpected error in get_recent_registrations: {str(e)}", "Admin API")
        return {
            "success": False,
            "error": "Failed to fetch recent registrations"
        }

@frappe.whitelist()
@log_api_call
@handle_api_error
def get_revenue_summary():
    """Get comprehensive revenue summary with payment breakdown"""
    try:
        # Initialize default values
        revenue_data = {
            "total_revenue": 0,
            "processing_fees": 0,
            "net_revenue": 0,
            "paid_registrations": 0,
            "conversion_rate": 0,
            "payment_methods": {}
        }
        
        # Get payment details for accurate revenue calculation
        try:
            successful_payments = frappe.get_all("Mock Payment Details", 
                filters={"payment_status": "Success"},
                fields=["amount", "processing_fee", "net_amount", "payment_method"])
            
            if successful_payments:
                revenue_data["total_revenue"] = sum(float(pd.get('amount', 0) or 0) for pd in successful_payments)
                revenue_data["processing_fees"] = sum(float(pd.get('processing_fee', 0) or 0) for pd in successful_payments)
                revenue_data["net_revenue"] = sum(float(pd.get('net_amount', 0) or 0) for pd in successful_payments)
                
                # Payment method breakdown
                method_breakdown = {}
                for payment in successful_payments:
                    method = payment.get('payment_method', 'Unknown')
                    if not method:
                        method = 'Unknown'
                        
                    if method not in method_breakdown:
                        method_breakdown[method] = {"count": 0, "amount": 0}
                    method_breakdown[method]["count"] += 1
                    method_breakdown[method]["amount"] += float(payment.get('amount', 0) or 0)
                
                revenue_data["payment_methods"] = method_breakdown
                revenue_data["paid_registrations"] = len(successful_payments)
                
        except Exception as payment_error:
            frappe.log_error(f"Error fetching payment details: {str(payment_error)}", "Admin API")
        
        # Calculate conversion rate
        try:
            total_registrations = frappe.db.count("Registration")
            if total_registrations > 0:
                revenue_data["conversion_rate"] = round((revenue_data["paid_registrations"] / total_registrations * 100), 1)
        except Exception as conversion_error:
            frappe.log_error(f"Error calculating conversion rate: {str(conversion_error)}", "Admin API")
        
        return {
            "success": True,
            "data": revenue_data
        }
    except Exception as e:
        frappe.log_error(f"Unexpected error in get_revenue_summary: {str(e)}", "Admin API")
        return {
            "success": False,
            "error": "Failed to fetch revenue summary"
        }

