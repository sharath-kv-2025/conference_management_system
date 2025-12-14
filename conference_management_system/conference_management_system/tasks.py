import frappe
from conference_management_system.conference_management_system.utils.recommendation_engine import RecommendationEngine

def update_conference_status():
    """Daily task to update conference status based on dates"""
    try:
        conferences = []
        try:
            conferences = frappe.get_all("Conference", 
                filters={"status": ["in", ["Upcoming", "Ongoing"]]},
                fields=["name", "start_date", "end_date", "status"]
            )
        except Exception as fetch_error:
            frappe.log_error(f"Error fetching conferences: {str(fetch_error)}", "Scheduled Task")
            return
        
        if not conferences:
            return
        
        today = frappe.utils.getdate()
        updated_count = 0
        errors = []
        
        for conf in conferences:
            try:
                new_status = None
                start_date = frappe.utils.getdate(conf.start_date) if conf.start_date else None
                end_date = frappe.utils.getdate(conf.end_date) if conf.end_date else None
                
                if start_date and end_date:
                    if today < start_date and conf.status != "Upcoming":
                        new_status = "Upcoming"
                    elif start_date <= today <= end_date and conf.status != "Ongoing":
                        new_status = "Ongoing"
                    elif today > end_date and conf.status != "Completed":
                        new_status = "Completed"
                    
                    if new_status:
                        try:
                            frappe.db.set_value("Conference", conf.name, "status", new_status)
                            updated_count += 1
                        except Exception as update_error:
                            errors.append(f"Failed to update {conf.name}: {str(update_error)}")
                            
            except Exception as conf_error:
                errors.append(f"Error processing conference {conf.get('name', 'unknown')}: {str(conf_error)}")
                continue
        
        try:
            if updated_count > 0:
                frappe.db.commit()
                frappe.log_error(f"Updated {updated_count} conference statuses", "Scheduled Task")
        except Exception as commit_error:
            frappe.log_error(f"Error committing status updates: {str(commit_error)}", "Scheduled Task")
        
        if errors:
            frappe.log_error(f"Conference status update errors: {'; '.join(errors)}", "Scheduled Task")
            
    except Exception as e:
        frappe.log_error(f"Unexpected error in update_conference_status: {str(e)}", "Scheduled Task")

def send_weekly_recommendations():
    """Weekly task to send session recommendations"""
    try:
        try:
            RecommendationEngine.send_weekly_recommendations()
            frappe.log_error("Weekly recommendations sent successfully", "Scheduled Task")
        except AttributeError as attr_error:
            frappe.log_error(f"RecommendationEngine method not found: {str(attr_error)}", "Scheduled Task")
        except Exception as rec_error:
            frappe.log_error(f"Error in recommendation engine: {str(rec_error)}", "Scheduled Task")
    except Exception as e:
        frappe.log_error(f"Unexpected error in send_weekly_recommendations: {str(e)}", "Scheduled Task")

def cleanup_old_api_logs():
    """Monthly task to cleanup old API logs (keep last 3 months)"""
    try:
        try:
            three_months_ago = frappe.utils.add_months(frappe.utils.now(), -3)
        except Exception as date_error:
            frappe.log_error(f"Error calculating date: {str(date_error)}", "Scheduled Task")
            return
        
        deleted_count = 0
        try:
            # Get count first for logging
            count_result = frappe.db.sql("""
                SELECT COUNT(*) as count FROM `tabAPI Log` 
                WHERE timestamp < %s
            """, three_months_ago, as_dict=True)
            
            if count_result and count_result[0].get('count', 0) > 0:
                # Delete old logs
                frappe.db.sql("""
                    DELETE FROM `tabAPI Log` 
                    WHERE timestamp < %s
                """, three_months_ago)
                
                deleted_count = count_result[0]['count']
                
        except Exception as delete_error:
            frappe.log_error(f"Error deleting API logs: {str(delete_error)}", "Scheduled Task")
            return
        
        try:
            frappe.db.commit()
            if deleted_count > 0:
                frappe.log_error(f"Cleaned up {deleted_count} old API logs", "Scheduled Task")
            else:
                frappe.log_error("No old API logs to clean up", "Scheduled Task")
        except Exception as commit_error:
            frappe.log_error(f"Error committing API log cleanup: {str(commit_error)}", "Scheduled Task")
        
    except Exception as e:
        frappe.log_error(f"Unexpected error in cleanup_old_api_logs: {str(e)}", "Scheduled Task")

