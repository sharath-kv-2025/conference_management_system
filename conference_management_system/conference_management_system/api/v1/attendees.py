import frappe
from conference_management_system.conference_management_system.utils.api_logger import log_api_call
from conference_management_system.conference_management_system.utils.error_handler import handle_api_error, ValidationError


@frappe.whitelist()
@log_api_call
@handle_api_error
def get_attendee_profile():
    """Get attendee profile and preferences"""
    try:
        email = frappe.form_dict.get('email')
        if not email:
            email = frappe.session.user
        
        # Handle special users
        if email == 'Administrator':
            email = 'admin@system.local'
        elif email == 'Guest' or not email:
            return {
                "success": False,
                "error": "Authentication required"
            }
        
        # Validate email format (skip for system users)
        if email not in ['admin@system.local'] and (not email or "@" not in email):
            return {
                "success": False,
                "error": "Invalid email format"
            }
        
        try:
            attendee_name = frappe.get_value("Attendee", {"email": email}, "name")
        except Exception as db_error:
            frappe.log_error(f"Database error fetching attendee: {str(db_error)}", "Attendee API")
            return {
                "success": False,
                "error": "Database error occurred"
            }
        
        if not attendee_name:
            return {
                "success": True,
                "data": {
                    "attendee": None,
                    "preferences": [],
                    "registrations": []
                },
                "message": "No attendee profile found. Please register for a session first."
            }
        
        try:
            attendee = frappe.get_doc("Attendee", attendee_name)
        except frappe.DoesNotExistError:
            return {
                "success": False,
                "error": "Attendee profile not found"
            }
        except Exception as e:
            frappe.log_error(f"Error fetching attendee document: {str(e)}", "Attendee API")
            return {
                "success": False,
                "error": "Failed to fetch attendee profile"
            }
        
        # Get preferences with proper error handling
        preferences = []
        if hasattr(attendee, 'preferences') and attendee.preferences:
            for pref in attendee.preferences:
                try:
                    if not pref.session:
                        continue
                    session_doc = frappe.get_doc("Session", pref.session)
                    preferences.append({
                        "session_id": pref.session,
                        "session_name": getattr(session_doc, 'session_name', ''),
                        "speaker": getattr(session_doc, 'speaker', ''),
                        "preference_type": getattr(pref, 'preference_type', 'Interested')
                    })
                except frappe.DoesNotExistError:
                    # Skip preferences for deleted sessions
                    continue
                except Exception as pref_error:
                    frappe.log_error(f"Error processing preference: {str(pref_error)}", "Attendee API")
                    continue
        
        # Get registrations with comprehensive error handling
        registrations = []
        try:
            registrations = frappe.get_all("Registration",
                filters={"attendee": attendee.name},
                fields=["name", "registration_date", "payment_status", "conference", "session"],
                order_by="registration_date DESC")
        except Exception as reg_error:
            frappe.log_error(f"Error fetching registrations: {str(reg_error)}", "Attendee API")
            registrations = []
        
        # Get conference and session details with proper validation
        valid_registrations = []
        for reg in registrations:
            try:
                if not reg.get('conference') or not reg.get('session'):
                    continue
                    
                conference = frappe.get_doc("Conference", reg.conference)
                session = frappe.get_doc("Session", reg.session)
                
                reg.conference_name = getattr(conference, 'conference_name', '')
                reg.session_name = getattr(session, 'session_name', '')
                reg.speaker = getattr(session, 'speaker', '')
                reg.session_date = str(getattr(session, 'session_date', '')) if hasattr(session, 'session_date') else ''
                reg.start_time = str(getattr(session, 'start_time', '')) if hasattr(session, 'start_time') else ''
                reg.end_time = str(getattr(session, 'end_time', '')) if hasattr(session, 'end_time') else ''
                valid_registrations.append(reg)
            except frappe.DoesNotExistError:
                # Skip registrations for deleted conferences/sessions
                continue
            except Exception as detail_error:
                frappe.log_error(f"Error processing registration details: {str(detail_error)}", "Attendee API")
                continue
        
        return {
            "success": True,
            "data": {
                "attendee": attendee.as_dict() if attendee else {},
                "preferences": preferences,
                "registrations": valid_registrations
            }
        }
    except Exception as e:
        frappe.log_error(f"Unexpected error in get_attendee_profile: {str(e)}", "Attendee API")
        return {
            "success": False,
            "error": "An unexpected error occurred while fetching attendee profile"
        }

@frappe.whitelist()
@log_api_call
@handle_api_error
def update_preferences():
    """Update attendee session preferences"""
    try:
        data = frappe.local.form_dict
        email = data.get('email')
        session_id = data.get('session_id')
        preference_type = data.get('preference_type', 'Interested')
        
        # Validate required fields
        if not email or not session_id:
            return {
                "success": False,
                "error": "Email and session_id are required"
            }
        
        # Handle special users
        if email == 'Administrator':
            email = 'admin@system.local'
        elif email == 'Guest':
            return {
                "success": False,
                "error": "Authentication required"
            }
        
        # Validate email format (skip for system users)
        if email not in ['admin@system.local'] and (not email or "@" not in email):
            return {
                "success": False,
                "error": "Invalid email format"
            }
        
        # Validate preference type
        valid_preference_types = ['Interested', 'Not Interested', 'Attended', 'Wishlist']
        if preference_type not in valid_preference_types:
            return {
                "success": False,
                "error": f"Invalid preference type. Must be one of: {', '.join(valid_preference_types)}"
            }
        
        # Get or create attendee with proper error handling
        try:
            attendee = frappe.get_doc("Attendee", {"email": email})
        except frappe.DoesNotExistError:
            # Create attendee if doesn't exist
            try:
                attendee = frappe.new_doc("Attendee")
                attendee.attendee_name = frappe.session.user_fullname or email.split('@')[0]
                attendee.email = email
                attendee.insert(ignore_permissions=True)
                frappe.db.commit()
            except Exception as create_error:
                frappe.log_error(f"Error creating attendee: {str(create_error)}", "Attendee API")
                return {
                    "success": False,
                    "error": "Failed to create attendee profile"
                }
        except Exception as e:
            frappe.log_error(f"Error fetching attendee: {str(e)}", "Attendee API")
            return {
                "success": False,
                "error": "Failed to fetch attendee profile"
            }
        
        # Validate session exists
        try:
            session_doc = frappe.get_doc("Session", session_id)
        except frappe.DoesNotExistError:
            return {
                "success": False,
                "error": "Session not found"
            }
        except Exception as e:
            frappe.log_error(f"Error fetching session: {str(e)}", "Attendee API")
            return {
                "success": False,
                "error": "Failed to validate session"
            }
        
        # Check if preference already exists
        existing_pref = None
        try:
            if hasattr(attendee, 'preferences') and attendee.preferences:
                for pref in attendee.preferences:
                    if getattr(pref, 'session', None) == session_id:
                        existing_pref = pref
                        break
        except Exception as e:
            frappe.log_error(f"Error checking existing preferences: {str(e)}", "Attendee API")
            # Continue with creating new preference
        
        # Update or create preference
        try:
            if existing_pref:
                existing_pref.preference_type = preference_type
                frappe.log_error(f"Updated existing preference for session {session_id} to {preference_type}", "Attendee API Debug")
            else:
                new_pref = attendee.append("preferences", {
                    "session": session_id,
                    "preference_type": preference_type
                })
                frappe.log_error(f"Created new preference for session {session_id} with type {preference_type}", "Attendee API Debug")
        except Exception as e:
            frappe.log_error(f"Error updating preference data: {str(e)}", "Attendee API")
            return {
                "success": False,
                "error": "Failed to update preference data"
            }
        
        # Save with comprehensive error handling
        try:
            # Force reload to ensure we have latest data
            attendee.reload()
            attendee.save(ignore_permissions=True)
            frappe.db.commit()
            
            # Double-check by reloading from database
            attendee.reload()
            preference_saved = False
            saved_preference_type = None
            
            for pref in attendee.preferences:
                if getattr(pref, 'session', None) == session_id:
                    preference_saved = True
                    saved_preference_type = getattr(pref, 'preference_type', None)
                    break
            
            if not preference_saved:
                frappe.log_error(f"Preference not found after save for session {session_id}", "Attendee API")
                return {
                    "success": False,
                    "error": "Preference was not saved properly"
                }
                
        except frappe.ValidationError as ve:
            frappe.log_error(f"Validation error saving preferences: {str(ve)}", "Attendee API")
            frappe.db.rollback()
            return {
                "success": False,
                "error": f"Validation failed: {str(ve)}"
            }
        except Exception as save_error:
            frappe.log_error(f"Error saving attendee preferences: {str(save_error)}", "Attendee API")
            frappe.db.rollback()
            return {
                "success": False,
                "error": "Failed to save preferences"
            }
        
        return {
            "success": True,
            "message": "Preferences updated successfully",
            "data": {
                "session_id": session_id,
                "preference_type": saved_preference_type or preference_type,
                "session_name": getattr(session_doc, 'session_name', ''),
                "attendee_id": attendee.name
            }
        }
    except Exception as e:
        frappe.log_error(f"Unexpected error in update_preferences: {str(e)}", "Attendee API")
        return {
            "success": False,
            "error": "An unexpected error occurred while updating preferences"
        }