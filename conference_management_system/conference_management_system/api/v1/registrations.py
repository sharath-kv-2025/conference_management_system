import frappe
import uuid
from conference_management_system.conference_management_system.utils.api_logger import log_api_call
from conference_management_system.conference_management_system.utils.payment_processor import PaymentProcessor
from conference_management_system.conference_management_system.utils.email_service import send_registration_confirmation, send_payment_confirmation

@frappe.whitelist()
@log_api_call
def register_for_session():
    """Register an attendee for a session"""
    try:
        data = frappe.local.form_dict
        
        # Validate required fields
        required_fields = ['session_id', 'attendee_name', 'email']
        for field in required_fields:
            if not data.get(field):
                frappe.throw(f"Missing required field: {field}")
        
        # Validate email format
        email = data.get('email')
        if email and email not in ['Administrator', 'Guest'] and '@' not in email:
            frappe.throw("Please enter a valid email address")
        
        # Handle special cases for Administrator
        if email == 'Administrator':
            email = 'admin@system.local'
        elif email == 'Guest':
            frappe.throw("Guest users cannot register for sessions")
        
        # Get or create attendee
        existing_attendee = frappe.get_value("Attendee", {"email": email}, "name")
        
        if existing_attendee:
            attendee = frappe.get_doc("Attendee", existing_attendee)
        else:
            attendee = frappe.new_doc("Attendee")
            attendee.attendee_name = data.get('attendee_name')
            attendee.email = email
            attendee.insert(ignore_permissions=True)
        
        # Get session details
        session_doc = frappe.get_doc("Session", data.get('session_id'))
        
        # Get conference details for amount
        conference_doc = frappe.get_doc("Conference", session_doc.conference)
        
        # Create registration
        registration = frappe.new_doc("Registration")
        registration.update({
            "conference": session_doc.conference,
            "session": data.get('session_id'),
            "attendee": attendee.name,
            "registration_date": frappe.utils.nowdate(),
            "payment_status": "Pending",
            "amount": conference_doc.registration_fee,
            "invoice_id": f"INV-{uuid.uuid4().hex[:8].upper()}",
            "join_link": f"https://conference.local/join/{uuid.uuid4().hex[:12]}"
        })
        
        registration.insert()
        frappe.db.commit()
        
        # Send registration confirmation email
        send_registration_confirmation(registration)
        
        return {
            "success": True,
            "data": {
                "registration_id": registration.name,
                "invoice_id": registration.invoice_id,
                "join_link": registration.join_link,
                "payment_status": registration.payment_status,
                "amount": registration.amount
            },
            "message": f"Registration successful! Your registration ID is {registration.name}. Please complete payment in the Registrations tab."
        }
    except Exception as e:
        frappe.log_error(f"Error registering for session: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
@log_api_call
def process_payment():
    """Process payment for a registration"""
    try:
        data = frappe.local.form_dict
        
        required_fields = ['registration_id', 'payment_method']
        for field in required_fields:
            if not data.get(field):
                frappe.throw(f"Missing required field: {field}")
        
        # Process payment using enhanced payment processor
        payment_result = PaymentProcessor.process_payment(
            registration_id=data.get('registration_id'),
            payment_method=data.get('payment_method'),
            payment_data=data
        )
        
        # Send payment confirmation email if successful
        if payment_result.get('success'):
            registration = frappe.get_doc("Registration", data.get('registration_id'))
            send_payment_confirmation(registration)
        
        return payment_result
            
    except Exception as e:
        frappe.log_error(f"Error processing payment: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
@log_api_call
def get_attendee_registrations():
    """Get all registrations for current user"""
    try:
        email = frappe.session.user
        
        # Handle Administrator user
        if email == 'Administrator':
            email = 'admin@system.local'
        elif email == 'Guest':
            return {
                "success": False,
                "error": "Guest users cannot access registrations"
            }
        
        attendee = frappe.get_value("Attendee", {"email": email}, "name")
        if not attendee:
            return {
                "success": True,
                "data": [],
                "message": "No registrations found. Please register for sessions first."
            }
            
        registrations = frappe.get_all("Registration",
            filters={"attendee": attendee},
            fields=["name", "registration_date", "payment_status", "invoice_id", "join_link", "amount", "conference", "session", "payment_details"],
            order_by="registration_date DESC")
        
        # Get conference and session details with payment info
        for reg in registrations:
            conference = frappe.get_doc("Conference", reg.conference)
            session = frappe.get_doc("Session", reg.session)
            reg.conference_name = conference.conference_name
            reg.session_name = session.session_name
            reg.speaker = session.speaker
            reg.start_time = str(session.start_time)
            reg.end_time = str(session.end_time)
            
            # Add payment details if available
            if reg.payment_details:
                payment_details = frappe.get_doc("Mock Payment Details", reg.payment_details)
                reg.payment_method = payment_details.payment_method
                reg.transaction_id = payment_details.transaction_id
                reg.processing_fee = payment_details.processing_fee
        
        return {
            "success": True,
            "data": registrations,
            "message": f"Found {len(registrations)} registrations"
        }
    except Exception as e:
        frappe.log_error(f"Error fetching attendee registrations: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
@log_api_call
def get_recommendations():
    """Get session recommendations for an attendee"""
    try:
        attendee_id = frappe.form_dict.get('attendee_id')
        if not attendee_id:
            frappe.throw("Attendee ID parameter is required")
        
        # Get attendee preferences and past registrations
        attendee = frappe.get_doc("Attendee", attendee_id)
        
        # Get sessions from preferred topics/speakers
        preferred_sessions = []
        if attendee.preferences:
            for pref in attendee.preferences:
                if pref.session:
                    session_doc = frappe.get_doc("Session", pref.session)
                    # Find similar sessions by speaker or keywords
                    similar_sessions = frappe.db.sql("""
                        SELECT DISTINCT s.name, s.session_name, s.speaker, s.start_time, s.end_time, s.conference
                        FROM `tabSession` s
                        JOIN `tabConference` c ON s.conference = c.name
                        WHERE (s.speaker = %s OR s.session_name LIKE %s OR s.description LIKE %s)
                        AND c.status IN ('Upcoming', 'Ongoing')
                        AND s.session_date >= CURDATE()
                        LIMIT 3
                    """, (session_doc.speaker, f"%{session_doc.session_name.split()[0]}%", f"%{session_doc.session_name.split()[0]}%"), as_dict=True)
                    preferred_sessions.extend(similar_sessions)
        
        # Get popular upcoming sessions if no preferences
        if not preferred_sessions:
            preferred_sessions = frappe.db.sql("""
                SELECT s.name, s.session_name, s.speaker, s.start_time, s.end_time, s.conference,
                       COUNT(r.name) as registration_count
                FROM `tabSession` s
                JOIN `tabConference` c ON s.conference = c.name
                LEFT JOIN `tabRegistration` r ON s.name = r.session
                WHERE c.status IN ('Upcoming', 'Ongoing')
                AND s.session_date >= CURDATE()
                GROUP BY s.name
                ORDER BY registration_count DESC
                LIMIT 5
            """, as_dict=True)
        
        recommendations = preferred_sessions[:5]
        
        # Add availability info
        for rec in recommendations:
            session_doc = frappe.get_doc("Session", rec['name'])
            registered_count = frappe.db.count("Registration", {"session": rec['name']})
            rec['available_spots'] = session_doc.max_attendees - registered_count
            rec['max_attendees'] = session_doc.max_attendees
        
        return {
            "success": True,
            "data": recommendations,
            "message": f"Found {len(recommendations)} personalized recommendations"
        }
    except Exception as e:
        frappe.log_error(f"Error fetching recommendations: {e}")
        return {
            "success": False,
            "error": str(e)
        }



