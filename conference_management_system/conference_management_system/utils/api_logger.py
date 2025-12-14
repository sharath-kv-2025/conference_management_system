import frappe
import json
import time
from functools import wraps

def log_api_call(func):
    """Decorator to log API calls with complete data"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Capture request data safely
        request_data = {
            "headers": {},
            "form_dict": {},
            "method": "POST",
            "ip": None,
            "user_agent": None
        }
        
        try:
            if frappe.request:
                request_data["headers"] = dict(frappe.request.headers) if frappe.request.headers else {}
                request_data["method"] = frappe.request.method or "POST"
                request_data["user_agent"] = frappe.request.headers.get('User-Agent') if frappe.request.headers else None
            
            if hasattr(frappe, 'local') and frappe.local:
                request_data["form_dict"] = frappe.local.form_dict or {}
                request_data["ip"] = getattr(frappe.local, 'request_ip', None)
                
        except Exception as req_error:
            frappe.log_error(f"Error capturing request data: {str(req_error)}", "API Logger")
        
        # Execute the API function
        result = None
        status_code = 200
        error = None
        
        try:
            result = func(*args, **kwargs)
            # Determine status code from result
            if isinstance(result, dict):
                if result.get('success') is False:
                    status_code = 400  # Bad request for business logic errors
                elif result.get('error_type') == 'permission_error':
                    status_code = 403  # Forbidden
                elif result.get('error_type') == 'not_found_error':
                    status_code = 404  # Not found
                elif result.get('error_type') == 'server_error':
                    status_code = 500  # Internal server error
        except Exception as e:
            result = {"success": False, "error": str(e), "error_type": "server_error"}
            status_code = 500
            error = str(e)
        
        # Calculate response time
        response_time = round((time.time() - start_time) * 1000, 2)
        
        # Log using frappe ORM with error handling
        try:
            # Sanitize data for JSON serialization
            safe_headers = _sanitize_for_json(request_data["headers"])
            safe_form_dict = _sanitize_for_json(request_data["form_dict"])
            safe_result = _sanitize_for_json(result)
            
            log_doc = frappe.new_doc("API Log")
            log_doc.api_endpoint = func.__name__
            log_doc.method = request_data["method"]
            log_doc.request_headers = json.dumps(safe_headers, indent=2, default=str)[:10000]  # Limit size
            log_doc.request_body = json.dumps(safe_form_dict, indent=2, default=str)[:10000]  # Limit size
            log_doc.response_body = json.dumps(safe_result, indent=2, default=str)[:10000]  # Limit size
            log_doc.status_code = status_code
            log_doc.response_time = response_time
            log_doc.ip_address = request_data["ip"]
            log_doc.user_agent = (request_data["user_agent"] or "")[:500]  # Limit size
            
            log_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            
        except Exception as log_error:
            frappe.log_error(f"API Log failed for {func.__name__}: {str(log_error)}", "API Logger")
            # Don't fail the API call if logging fails
        
        if error:
            raise Exception(error)
        
        return result
    
    return wrapper

def _sanitize_for_json(data):
    """Sanitize data for JSON serialization"""
    try:
        if data is None:
            return {}
        
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                try:
                    # Skip sensitive fields
                    if isinstance(key, str) and any(sensitive in key.lower() for sensitive in ['password', 'token', 'secret', 'key']):
                        sanitized[key] = "[REDACTED]"
                    else:
                        sanitized[key] = _sanitize_value(value)
                except Exception:
                    sanitized[key] = "[ERROR_SERIALIZING]"
            return sanitized
        
        return _sanitize_value(data)
        
    except Exception:
        return {"error": "Failed to sanitize data"}

def _sanitize_value(value):
    """Sanitize individual values for JSON serialization"""
    try:
        if value is None:
            return None
        elif isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, (list, tuple)):
            return [_sanitize_value(item) for item in value[:100]]  # Limit list size
        elif isinstance(value, dict):
            return _sanitize_for_json(value)
        else:
            return str(value)[:1000]  # Convert to string and limit size
    except Exception:
        return "[ERROR_SERIALIZING]"

