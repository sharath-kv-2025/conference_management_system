import frappe
from frappe.model.document import Document
from frappe.utils import get_time, getdate, nowdate
from conference_management_system.conference_management_system.utils.error_handler import ValidationError

class Session(Document):
    def validate(self):
        try:
            self.validate_required_fields()
            self.validate_time_slots()
            self.validate_conference_dates()
            self.validate_session_date()
            self.validate_capacity()
        except Exception as e:
            frappe.log_error(f"Session validation error: {str(e)}", "Session Document")
            raise
    
    def validate_required_fields(self):
        """Validate required fields"""
        try:
            if not self.session_name or not self.session_name.strip():
                raise ValidationError("Session name is required")
            
            if not self.conference:
                raise ValidationError("Conference is required")
            
            if not self.session_date:
                raise ValidationError("Session date is required")
            
            if not self.start_time:
                raise ValidationError("Start time is required")
            
            if not self.end_time:
                raise ValidationError("End time is required")
                
            if not self.speaker or not self.speaker.strip():
                raise ValidationError("Speaker is required")
                
        except Exception as e:
            frappe.log_error(f"Required field validation error: {str(e)}", "Session Document")
            raise
    
    def validate_capacity(self):
        """Validate session capacity"""
        try:
            if self.max_attendees is not None:
                if self.max_attendees <= 0:
                    raise ValidationError("Maximum attendees must be greater than 0")
                
                if self.max_attendees > 1000:  # Reasonable limit
                    raise ValidationError("Maximum attendees cannot exceed 1000")
        except ValidationError:
            raise
        except Exception as e:
            frappe.log_error(f"Capacity validation error: {str(e)}", "Session Document")
            raise ValidationError("Invalid capacity value")
    
    def validate_time_slots(self):
        """Validate session time slots"""
        try:
            if self.start_time and self.end_time:
                start_time = get_time(self.start_time)
                end_time = get_time(self.end_time)
                
                if start_time >= end_time:
                    raise ValidationError("Start time must be before end time")
                
                # Check minimum session duration (15 minutes)
                duration_seconds = (end_time.hour * 3600 + end_time.minute * 60) - (start_time.hour * 3600 + start_time.minute * 60)
                if duration_seconds < 900:  # 15 minutes
                    raise ValidationError("Session must be at least 15 minutes long")
            
            # Check for overlapping sessions in same conference on same date
            if self.conference and self.session_date:
                try:
                    overlapping = frappe.db.sql("""
                        SELECT name, session_name FROM `tabSession` 
                        WHERE conference = %s AND session_date = %s AND name != %s
                        AND (
                            (start_time <= %s AND end_time > %s) OR
                            (start_time < %s AND end_time >= %s) OR
                            (start_time >= %s AND end_time <= %s)
                        )
                    """, (self.conference, self.session_date, self.name or "", 
                          self.start_time, self.start_time,
                          self.end_time, self.end_time,
                          self.start_time, self.end_time))
                    
                    if overlapping:
                        raise ValidationError(f"Session time overlaps with existing session: {overlapping[0][1]}")
                        
                except ValidationError:
                    raise
                except Exception as overlap_error:
                    frappe.log_error(f"Error checking session overlap: {str(overlap_error)}", "Session Document")
                    # Continue validation - don't fail on overlap check error
                    
        except ValidationError:
            raise
        except Exception as e:
            frappe.log_error(f"Time slot validation error: {str(e)}", "Session Document")
            raise ValidationError("Invalid time slot configuration")
    
    def validate_conference_dates(self):
        """Validate session date against conference dates"""
        try:
            if self.conference and self.session_date:
                try:
                    conf = frappe.get_doc("Conference", self.conference)
                    session_date = getdate(self.session_date)
                    start_date = getdate(conf.start_date)
                    end_date = getdate(conf.end_date)
                    
                    if session_date < start_date or session_date > end_date:
                        raise ValidationError(f"Session date must be between conference dates ({conf.start_date} to {conf.end_date})")
                        
                except frappe.DoesNotExistError:
                    raise ValidationError("Selected conference does not exist")
                except ValidationError:
                    raise
                except Exception as conf_error:
                    frappe.log_error(f"Error validating conference dates: {str(conf_error)}", "Session Document")
                    raise ValidationError("Failed to validate against conference dates")
                    
        except ValidationError:
            raise
        except Exception as e:
            frappe.log_error(f"Conference date validation error: {str(e)}", "Session Document")
            raise ValidationError("Conference date validation failed")
    
    def validate_session_date(self):
        """Validate session date"""
        try:
            if self.session_date:
                session_date = getdate(self.session_date)
                today = getdate(nowdate())
                
                # Allow past dates for completed sessions, but warn
                if session_date < today:
                    frappe.msgprint("Warning: Session date is in the past", alert=True)
                    
        except Exception as e:
            frappe.log_error(f"Session date validation error: {str(e)}", "Session Document")
            raise ValidationError("Invalid session date")
    
    def get_registered_count(self):
        """Get number of registered attendees"""
        try:
            return frappe.db.count("Registration", {"session": self.name})
        except Exception as e:
            frappe.log_error(f"Error counting registrations: {str(e)}", "Session Document")
            return 0
    
    def get_available_spots(self):
        """Get number of available spots"""
        try:
            registered = self.get_registered_count()
            max_attendees = int(self.max_attendees or 0)
            return max(0, max_attendees - registered)
        except Exception as e:
            frappe.log_error(f"Error calculating available spots: {str(e)}", "Session Document")
            return 0
    
    def is_full(self):
        """Check if session is full"""
        try:
            return self.get_available_spots() <= 0
        except Exception as e:
            frappe.log_error(f"Error checking if session is full: {str(e)}", "Session Document")
            return True  # Assume full on error for safety