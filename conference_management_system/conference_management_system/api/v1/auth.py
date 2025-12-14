import frappe
from conference_management_system.conference_management_system.utils.api_logger import log_api_call
from conference_management_system.conference_management_system.utils.error_handler import handle_api_error

@frappe.whitelist()
@log_api_call
@handle_api_error
def get_user_info():
    """Get current user information"""
    try:
        user = frappe.session.user
        
        # Validate session
        if not user:
            return {
                "success": False,
                "error": "No active user session"
            }
        
        is_guest = user == "Guest"
        
        # Get user roles with error handling
        roles = []
        if not is_guest:
            try:
                roles = frappe.get_roles(user)
                if not roles:
                    roles = []
            except Exception as role_error:
                frappe.log_error(f"Error fetching user roles: {str(role_error)}", "Auth API")
                roles = []
        
        # Get user full name with error handling
        user_fullname = ""
        try:
            user_fullname = frappe.session.get("user_fullname", "")
            if not user_fullname and not is_guest:
                # Try to get from User document
                user_doc = frappe.get_doc("User", user)
                user_fullname = getattr(user_doc, 'full_name', '') or getattr(user_doc, 'first_name', '')
        except Exception as name_error:
            frappe.log_error(f"Error fetching user fullname: {str(name_error)}", "Auth API")
        
        user_info = {
            "user": user,
            "is_guest": is_guest,
            "user_fullname": user_fullname,
            "roles": roles,
            "session_valid": True
        }
        
        return {
            "success": True,
            "data": user_info
        }
    except Exception as e:
        frappe.log_error(f"Unexpected error in get_user_info: {str(e)}", "Auth API")
        return {
            "success": False,
            "error": "Failed to fetch user information"
        }

@frappe.whitelist()
@log_api_call
@handle_api_error
def check_session():
    """Check if user session is valid"""
    try:
        user = frappe.session.user
        session_id = getattr(frappe.session, 'sid', None)
        
        # Validate session components
        if not user:
            return {
                "success": True,
                "data": {
                    "authenticated": False,
                    "user": None,
                    "session_id": None,
                    "session_valid": False
                }
            }
        
        is_authenticated = user != "Guest"
        
        # Additional session validation
        session_valid = True
        try:
            if is_authenticated:
                # Verify user still exists
                frappe.get_doc("User", user)
        except frappe.DoesNotExistError:
            session_valid = False
            is_authenticated = False
        except Exception as validation_error:
            frappe.log_error(f"Session validation error: {str(validation_error)}", "Auth API")
            session_valid = False
        
        return {
            "success": True,
            "data": {
                "authenticated": is_authenticated,
                "user": user,
                "session_id": session_id,
                "session_valid": session_valid,
                "timestamp": frappe.utils.now()
            }
        }
    except Exception as e:
        frappe.log_error(f"Unexpected error in check_session: {str(e)}", "Auth API")
        return {
            "success": False,
            "error": "Failed to check session status"
        }