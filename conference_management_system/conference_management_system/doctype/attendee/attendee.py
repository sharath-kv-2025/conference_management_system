import frappe
from frappe.model.document import Document
import random
import string
import re
from conference_management_system.conference_management_system.utils.error_handler import ValidationError

class Attendee(Document):
    def validate(self):
        try:
            self.validate_required_fields()
            self.validate_email()
            self.set_defaults()
        except Exception as e:
            frappe.log_error(f"Attendee validation error: {str(e)}", "Attendee Document")
            raise
    
    def validate_required_fields(self):
        """Validate required fields"""
        try:
            if not self.attendee_name or not self.attendee_name.strip():
                raise ValidationError("Attendee name is required")
            
            if not self.email or not self.email.strip():
                raise ValidationError("Email is required")
                
        except Exception as e:
            frappe.log_error(f"Required field validation error: {str(e)}", "Attendee Document")
            raise
    
    def validate_email(self):
        """Validate email format and uniqueness"""
        try:
            if self.email:
                email = self.email.strip().lower()
                
                # Basic email format validation
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, email):
                    raise ValidationError("Please enter a valid email address")
                
                # Check for duplicate email
                existing = frappe.db.get_value("Attendee", {"email": email, "name": ["!=", self.name or ""]}, "name")
                if existing:
                    raise ValidationError("An attendee with this email already exists")
                
                self.email = email  # Store normalized email
                
        except ValidationError:
            raise
        except Exception as e:
            frappe.log_error(f"Email validation error: {str(e)}", "Attendee Document")
            raise ValidationError("Email validation failed")
    

    
    def set_defaults(self):
        """Set default values"""
        try:
            if self.email_verified is None:
                self.email_verified = 0
                
        except Exception as e:
            frappe.log_error(f"Error setting defaults: {str(e)}", "Attendee Document")
    
    def generate_otp(self):
        """Generate 6-digit OTP for email verification"""
        try:
            otp = ''.join(random.choices(string.digits, k=6))
            self.otp_code = otp
            self.otp_generated_at = frappe.utils.now()
            
            try:
                self.save()
            except Exception as save_error:
                frappe.log_error(f"Error saving OTP: {str(save_error)}", "Attendee Document")
                raise ValidationError("Failed to generate OTP")
            
            try:
                from conference_management_system.conference_management_system.utils.email_service import send_otp_email
                send_otp_email(self.email, otp)
            except Exception as email_error:
                frappe.log_error(f"Error sending OTP email: {str(email_error)}", "Attendee Document")
                # Don't raise error - OTP was generated successfully
            
            return otp
            
        except ValidationError:
            raise
        except Exception as e:
            frappe.log_error(f"Error generating OTP: {str(e)}", "Attendee Document")
            raise ValidationError("Failed to generate OTP")
    
    def verify_otp(self, otp):
        """Verify OTP and mark email as verified"""
        try:
            if not otp or not otp.strip():
                return False, "OTP is required"
            
            otp = otp.strip()
            
            if not self.otp_code:
                return False, "No OTP generated for this attendee"
            
            # Check OTP expiry (10 minutes)
            if hasattr(self, 'otp_generated_at') and self.otp_generated_at:
                try:
                    generated_time = frappe.utils.get_datetime(self.otp_generated_at)
                    current_time = frappe.utils.now_datetime()
                    time_diff = (current_time - generated_time).total_seconds()
                    
                    if time_diff > 600:  # 10 minutes
                        self.otp_code = ""  # Clear expired OTP
                        self.save()
                        return False, "OTP has expired. Please generate a new one"
                except Exception as time_error:
                    frappe.log_error(f"Error checking OTP expiry: {str(time_error)}", "Attendee Document")
            
            if self.otp_code == otp:
                try:
                    self.email_verified = 1
                    self.otp_code = ""
                    self.otp_generated_at = None
                    self.save()
                    return True, "Email verified successfully"
                except Exception as save_error:
                    frappe.log_error(f"Error saving verification: {str(save_error)}", "Attendee Document")
                    return False, "Failed to save verification status"
            
            return False, "Invalid OTP"
            
        except Exception as e:
            frappe.log_error(f"Error verifying OTP: {str(e)}", "Attendee Document")
            return False, "OTP verification failed"
    
    def get_registration_count(self):
        """Get total number of registrations for this attendee"""
        try:
            return frappe.db.count("Registration", {"attendee": self.name})
        except Exception as e:
            frappe.log_error(f"Error counting registrations: {str(e)}", "Attendee Document")
            return 0
    
    def get_paid_registrations_count(self):
        """Get number of paid registrations for this attendee"""
        try:
            return frappe.db.count("Registration", {"attendee": self.name, "payment_status": "Paid"})
        except Exception as e:
            frappe.log_error(f"Error counting paid registrations: {str(e)}", "Attendee Document")
            return 0
    
    def is_email_verified(self):
        """Check if email is verified"""
        return bool(self.email_verified)