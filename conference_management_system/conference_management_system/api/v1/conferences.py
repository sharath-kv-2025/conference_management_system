import frappe
from conference_management_system.conference_management_system.utils.api_logger import log_api_call
from conference_management_system.conference_management_system.utils.error_handler import handle_api_error



@frappe.whitelist()
@log_api_call
@handle_api_error
def get_upcoming_conferences():
    """Get all upcoming conferences with sessions"""
    try:
        conferences = []
        
        # Get conferences with proper error handling
        try:
            conferences = frappe.get_all("Conference", 
                filters={"status": ["in", ["Upcoming", "Ongoing"]]},
                fields=["name", "conference_name", "start_date", "end_date", "location", "description", "status", "registration_fee"],
                order_by="start_date ASC")
        except Exception as conf_error:
            frappe.log_error(f"Error fetching conferences: {str(conf_error)}", "Conferences API")
            return {
                "success": False,
                "error": "Failed to fetch conferences"
            }
        
        # Process each conference
        for conference in conferences:
            try:
                # Convert dates to strings safely
                if conference.get('start_date'):
                    conference['start_date'] = str(conference['start_date'])
                if conference.get('end_date'):
                    conference['end_date'] = str(conference['end_date'])
                
                # Ensure required fields have default values
                conference['location'] = conference.get('location', '')
                conference['description'] = conference.get('description', '')
                conference['registration_fee'] = float(conference.get('registration_fee', 0) or 0)
                
                # Get sessions for each conference
                try:
                    conference['sessions'] = frappe.get_all("Session",
                        filters={"conference": conference['name']},
                        fields=["name", "session_name", "speaker", "start_time", "end_time", "max_attendees"],
                        order_by="start_time ASC")
                except Exception as session_error:
                    frappe.log_error(f"Error fetching sessions for conference {conference['name']}: {str(session_error)}", "Conferences API")
                    conference['sessions'] = []
                
                # Add registration count for each session
                for session in conference['sessions']:
                    try:
                        # Convert time to string safely
                        if session.get('start_time'):
                            session['start_time'] = str(session['start_time'])
                        if session.get('end_time'):
                            session['end_time'] = str(session['end_time'])
                        
                        # Ensure required fields
                        session['session_name'] = session.get('session_name', '')
                        session['speaker'] = session.get('speaker', '')
                        session['max_attendees'] = int(session.get('max_attendees', 0) or 0)
                        
                        # Get registration count safely
                        try:
                            session['registered_count'] = frappe.db.count("Registration", {"session": session['name']})
                        except Exception as reg_count_error:
                            frappe.log_error(f"Error counting registrations for session {session['name']}: {str(reg_count_error)}", "Conferences API")
                            session['registered_count'] = 0
                        
                        session['available_spots'] = max(0, session['max_attendees'] - session['registered_count'])
                        
                    except Exception as session_process_error:
                        frappe.log_error(f"Error processing session data: {str(session_process_error)}", "Conferences API")
                        # Set default values for failed session processing
                        session.update({
                            'start_time': '',
                            'end_time': '',
                            'registered_count': 0,
                            'available_spots': session.get('max_attendees', 0)
                        })
                        
            except Exception as conf_process_error:
                frappe.log_error(f"Error processing conference {conference.get('name', 'unknown')}: {str(conf_process_error)}", "Conferences API")
                continue
        
        return {
            "success": True,
            "data": conferences,
            "message": f"Found {len(conferences)} upcoming conferences"
        }
    except Exception as e:
        frappe.log_error(f"Unexpected error in get_upcoming_conferences: {str(e)}", "Conferences API")
        return {
            "success": False,
            "error": "An unexpected error occurred while fetching conferences"
        }



