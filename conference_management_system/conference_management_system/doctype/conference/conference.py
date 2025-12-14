import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate

class Conference(Document):
    def validate(self):
        self.validate_dates()
        self.update_status()
    
    def validate_dates(self):
        if self.start_date and self.end_date:
            if getdate(self.start_date) > getdate(self.end_date):
                frappe.throw("Start date cannot be after end date")
    
    def update_status(self):
        if not self.status or self.status == "Upcoming":
            today = getdate(nowdate())
            start = getdate(self.start_date) if self.start_date else None
            end = getdate(self.end_date) if self.end_date else None
            
            if start and end:
                if today < start:
                    self.status = "Upcoming"
                elif start <= today <= end:
                    self.status = "Ongoing"
                elif today > end:
                    self.status = "Completed"