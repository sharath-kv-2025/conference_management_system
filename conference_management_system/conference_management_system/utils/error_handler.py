import frappe
import traceback
import functools

class ValidationError(Exception):
    """Validation related errors"""
    def __init__(self, message, error_code=None, details=None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

def handle_api_error(func):
    """Decorator for comprehensive API error handling"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            frappe.log_error(f"Validation error in {func.__name__}: {str(e)}", "API Validation Error")
            return {
                "success": False,
                "error": str(e),
                "error_type": "validation_error",
                "error_code": getattr(e, 'error_code', 'VALIDATION_FAILED'),
                "message": "Please check your input and try again.",
                "details": getattr(e, 'details', {})
            }

        except frappe.PermissionError as e:
            frappe.log_error(f"Permission error in {func.__name__}: {str(e)}", "API Permission Error")
            return {
                "success": False,
                "error": "Access denied",
                "error_type": "permission_error",
                "error_code": "ACCESS_DENIED",
                "message": "You don't have permission to perform this action."
            }
        except frappe.DoesNotExistError as e:
            frappe.log_error(f"Resource not found in {func.__name__}: {str(e)}", "API Not Found Error")
            return {
                "success": False,
                "error": "Resource not found",
                "error_type": "not_found_error",
                "error_code": "RESOURCE_NOT_FOUND",
                "message": "The requested resource was not found."
            }
        except frappe.ValidationError as e:
            frappe.log_error(f"Frappe validation error in {func.__name__}: {str(e)}", "API Frappe Validation Error")
            return {
                "success": False,
                "error": str(e),
                "error_type": "validation_error",
                "error_code": "FRAPPE_VALIDATION_FAILED",
                "message": "Data validation failed."
            }
        except Exception as e:
            # Log the full traceback for debugging
            error_id = frappe.log_error(
                title=f"Unexpected API Error in {func.__name__}",
                message=f"Function: {func.__name__}\nArgs: {args}\nKwargs: {kwargs}\nError: {str(e)}\nTraceback: {traceback.format_exc()}"
            )
            
            return {
                "success": False,
                "error": "Internal server error",
                "error_type": "server_error",
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "error_id": error_id.name if error_id else None
            }
    
    return wrapper

