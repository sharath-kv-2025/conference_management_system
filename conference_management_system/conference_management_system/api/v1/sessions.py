import frappe
from conference_management_system.conference_management_system.utils.api_logger import log_api_call



@frappe.whitelist()
@log_api_call
def get_sessions_by_conference():
    """Get all sessions for a specific conference"""
    try:
        conference_id = frappe.form_dict.get('conference_id')
        if not conference_id:
            frappe.throw("Conference ID parameter is required")
        
        # Validate conference exists
        if not frappe.db.exists("Conference", conference_id):
            return {
                "success": False,
                "error": "Conference not found"
            }
        
        sessions = frappe.get_all("Session",
            filters={"conference": conference_id},
            fields=["name", "session_name", "speaker", "session_date", "start_time", "end_time", "max_attendees", "description"],
            order_by="session_date ASC, start_time ASC")
        
        # Get current user's attendee record
        current_user_email = frappe.session.user
        attendee_id = None
        if current_user_email and current_user_email != "Guest":
            try:
                # Handle Administrator user
                if current_user_email == 'Administrator':
                    current_user_email = 'admin@system.local'
                attendee_id = frappe.get_value("Attendee", {"email": current_user_email}, "name")
            except Exception:
                pass
        
        # Add registration info
        for session in sessions:
            try:
                # Convert time fields to strings
                if session.get('start_time'):
                    session['start_time'] = str(session['start_time'])
                if session.get('end_time'):
                    session['end_time'] = str(session['end_time'])
                if session.get('session_date'):
                    session['session_date'] = str(session['session_date'])
                
                # Ensure required fields
                session['session_name'] = session.get('session_name', '')
                session['speaker'] = session.get('speaker', '')
                session['max_attendees'] = int(session.get('max_attendees', 0) or 0)
                
                session['registered_count'] = frappe.db.count("Registration", {"session": session['name']})
                session['available_spots'] = max(0, session['max_attendees'] - session['registered_count'])
                
                # Check if current user is already registered
                session['user_registered'] = False
                if attendee_id:
                    try:
                        existing_reg = frappe.db.get_value("Registration", 
                            {"session": session['name'], "attendee": attendee_id}, "name")
                        session['user_registered'] = bool(existing_reg)
                    except Exception:
                        pass
            except Exception as session_error:
                frappe.log_error(f"Error processing session {session.get('name', 'unknown')}: {str(session_error)}", "Sessions API")
                continue
        
        return {
            "success": True,
            "data": sessions,
            "message": f"Found {len(sessions)} sessions"
        }
    except Exception as e:
        frappe.log_error(f"Error fetching sessions: {e}")
        return {
            "success": False,
            "error": str(e)
        }