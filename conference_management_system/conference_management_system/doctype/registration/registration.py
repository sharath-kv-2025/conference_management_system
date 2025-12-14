import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
import uuid
from conference_management_system.conference_management_system.utils.error_handler import ValidationError

class Registration(Document):
    def validate(self):
        try:
            self.validate_required_fields()
            self.validate_capacity()
            self.validate_no_overlap()
            self.set_amount()
            self.validate_payment_status()
        except Exception as e:
            frappe.log_error(f"Registration validation error: {str(e)}", "Registration Document")
            raise
    
    def before_insert(self):
        try:
            self.generate_invoice_id()
            self.generate_join_link()
            self.set_defaults()
        except Exception as e:
            frappe.log_error(f"Error in before_insert: {str(e)}", "Registration Document")
            raise
    
    def after_insert(self):
        try:
            from conference_management_system.conference_management_system.utils.email_service import send_registration_confirmation
            send_registration_confirmation(self)
        except Exception as e:
            frappe.log_error(f"Error in after_insert: {str(e)}", "Registration Document")
            # Don't raise error to prevent registration failure
    
    def on_update(self):
        try:
            if self.has_value_changed("payment_status") and self.payment_status == "Paid":
                try:
                    from conference_management_system.conference_management_system.utils.email_service import send_payment_confirmation
                    send_payment_confirmation(self)
                except Exception as e:
                    frappe.log_error(f"Error sending payment confirmation: {str(e)}", "Registration Document")
        except Exception as e:
            frappe.log_error(f"Error in on_update: {str(e)}", "Registration Document")
    
    def validate_required_fields(self):
        """Validate required fields"""
        try:
            if not self.conference:
                raise ValidationError("Conference is required")
            
            if not self.session:
                raise ValidationError("Session is required")
            
            if not self.attendee:
                raise ValidationError("Attendee is required")
                
        except Exception as e:
            frappe.log_error(f"Required field validation error: {str(e)}", "Registration Document")
            raise
    
    def set_defaults(self):
        """Set default values"""
        try:
            if not self.registration_date:
                self.registration_date = nowdate()
            
            if not self.payment_status:
                self.payment_status = "Pending"
                
        except Exception as e:
            frappe.log_error(f"Error setting defaults: {str(e)}", "Registration Document")
    
    def validate_payment_status(self):
        """Validate payment status"""
        try:
            valid_statuses = ["Pending", "Paid", "Failed", "Refunded"]
            if self.payment_status and self.payment_status not in valid_statuses:
                raise ValidationError(f"Invalid payment status. Must be one of: {', '.join(valid_statuses)}")
        except ValidationError:
            raise
        except Exception as e:
            frappe.log_error(f"Payment status validation error: {str(e)}", "Registration Document")
            raise ValidationError("Invalid payment status")
    
    def validate_capacity(self):
        """Validate session capacity"""
        try:
            if not self.session:
                return
            
            try:
                session_doc = frappe.get_doc("Session", self.session)
            except frappe.DoesNotExistError:
                raise ValidationError("Selected session does not exist")
            
            max_attendees = int(session_doc.max_attendees or 0)
            if max_attendees <= 0:
                raise ValidationError("Session has invalid capacity configuration")
            
            current_registrations = frappe.db.count("Registration", {
                "session": self.session,
                "name": ["!=", self.name or ""]
            })
            
            if current_registrations >= max_attendees:
                raise ValidationError(f"Session capacity exceeded. Maximum {max_attendees} attendees allowed.")
                
        except ValidationError:
            raise
        except Exception as e:
            frappe.log_error(f"Capacity validation error: {str(e)}", "Registration Document")
            raise ValidationError("Failed to validate session capacity")
    
    def validate_no_overlap(self):
        """Validate no time overlap with existing registrations"""
        try:
            if not self.attendee or not self.session:
                return
            
            try:
                session_doc = frappe.get_doc("Session", self.session)
            except frappe.DoesNotExistError:
                raise ValidationError("Selected session does not exist")
            
            try:
                overlapping_registrations = frappe.db.sql("""
                    SELECT r.name, s.session_name 
                    FROM `tabRegistration` r
                    JOIN `tabSession` s ON r.session = s.name
                    WHERE r.attendee = %s 
                    AND r.name != %s
                    AND s.conference = %s
                    AND s.session_date = %s
                    AND (
                        (s.start_time <= %s AND s.end_time > %s) OR
                        (s.start_time < %s AND s.end_time >= %s) OR
                        (s.start_time >= %s AND s.end_time <= %s)
                    )
                """, (self.attendee, self.name or "",
                      session_doc.conference, session_doc.session_date,
                      session_doc.start_time, session_doc.start_time,
                      session_doc.end_time, session_doc.end_time,
                      session_doc.start_time, session_doc.end_time))
                
                if overlapping_registrations:
                    raise ValidationError(f"Attendee already registered for overlapping session: {overlapping_registrations[0][1]}")
                    
            except ValidationError:
                raise
            except Exception as overlap_error:
                frappe.log_error(f"Error checking overlap: {str(overlap_error)}", "Registration Document")
                # Continue without failing - overlap check is not critical
                
        except ValidationError:
            raise
        except Exception as e:
            frappe.log_error(f"Overlap validation error: {str(e)}", "Registration Document")
            # Don't raise error for overlap validation failures
    
    def set_amount(self):
        """Set registration amount from conference"""
        try:
            if self.conference and not self.amount:
                try:
                    conference_doc = frappe.get_doc("Conference", self.conference)
                    self.amount = float(conference_doc.registration_fee or 0)
                except frappe.DoesNotExistError:
                    raise ValidationError("Selected conference does not exist")
                except Exception as amount_error:
                    frappe.log_error(f"Error setting amount: {str(amount_error)}", "Registration Document")
                    self.amount = 0
        except ValidationError:
            raise
        except Exception as e:
            frappe.log_error(f"Amount setting error: {str(e)}", "Registration Document")
    
    def generate_invoice_id(self):
        """Generate unique invoice ID"""
        try:
            if not self.invoice_id:
                self.invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        except Exception as e:
            frappe.log_error(f"Error generating invoice ID: {str(e)}", "Registration Document")
            self.invoice_id = f"INV-{frappe.utils.random_string(8).upper()}"
    
    def generate_join_link(self):
        """Generate unique join link"""
        try:
            if not self.join_link:
                self.join_link = f"https://conference.example.com/join/{uuid.uuid4().hex}"
        except Exception as e:
            frappe.log_error(f"Error generating join link: {str(e)}", "Registration Document")
            self.join_link = f"https://conference.example.com/join/{frappe.utils.random_string(32)}"
    
    def get_session_details(self):
        """Get session details for this registration"""
        try:
            if self.session:
                return frappe.get_doc("Session", self.session)
        except Exception as e:
            frappe.log_error(f"Error fetching session details: {str(e)}", "Registration Document")
        return None
    
    def get_conference_details(self):
        """Get conference details for this registration"""
        try:
            if self.conference:
                return frappe.get_doc("Conference", self.conference)
        except Exception as e:
            frappe.log_error(f"Error fetching conference details: {str(e)}", "Registration Document")
        return None
    
    def get_attendee_details(self):
        """Get attendee details for this registration"""
        try:
            if self.attendee:
                return frappe.get_doc("Attendee", self.attendee)
        except Exception as e:
            frappe.log_error(f"Error fetching attendee details: {str(e)}", "Registration Document")
        return None
    
    def is_payment_pending(self):
        """Check if payment is pending"""
        return self.payment_status == "Pending"
    
    def is_paid(self):
        """Check if registration is paid"""
        return self.payment_status == "Paid"