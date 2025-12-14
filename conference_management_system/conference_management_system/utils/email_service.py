import frappe
from frappe.utils import get_url

def mock_sendmail(recipients, subject, message, email_type="General", reference_doctype=None, reference_name=None):
    """Mock email sending - logs email instead of sending"""
    try:
        for recipient in recipients if isinstance(recipients, list) else [recipients]:
            email_log = frappe.new_doc("Mock Email Log")
            email_log.recipient = recipient
            email_log.subject = subject
            email_log.message = message
            email_log.email_type = email_type
            email_log.status = "Sent"
            email_log.reference_doctype = reference_doctype
            email_log.reference_name = reference_name
            email_log.insert(ignore_permissions=True)
        
        frappe.db.commit()
        return True
    except Exception as e:
        frappe.log_error(f"Failed to log mock email: {str(e)}", "Mock Email Service")
        return False

def send_registration_confirmation(registration_doc):
    """Send registration confirmation email (mock)"""
    try:
        attendee = frappe.get_doc("Attendee", registration_doc.attendee)
        session = frappe.get_doc("Session", registration_doc.session)
        conference = frappe.get_doc("Conference", registration_doc.conference)
        
        subject = f"Registration Confirmed - {session.session_name}"
        
        message = f"""
        <h3>Registration Confirmation</h3>
        <p>Dear {attendee.attendee_name},</p>
        
        <p>Your registration has been confirmed for:</p>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h4>{session.session_name}</h4>
            <p><strong>Conference:</strong> {conference.conference_name}</p>
            <p><strong>Speaker:</strong> {session.speaker}</p>
            <p><strong>Date:</strong> {conference.start_date}</p>
            <p><strong>Time:</strong> {session.start_time} - {session.end_time}</p>
            <p><strong>Location:</strong> {conference.location}</p>
        </div>
        
        <p><strong>Registration Details:</strong></p>
        <ul>
            <li>Registration ID: {registration_doc.name}</li>
            <li>Invoice ID: {registration_doc.invoice_id}</li>
            <li>Amount: ₹{registration_doc.amount}</li>
            <li>Payment Status: {registration_doc.payment_status}</li>
        </ul>
        
        {f'<p><strong>Join Link:</strong> <a href="{registration_doc.join_link}">Click here to join the session</a></p>' if registration_doc.join_link else ''}
        
        <p>Thank you for registering!</p>
        """
        
        mock_sendmail(
            recipients=[attendee.email],
            subject=subject,
            message=message,
            email_type="Registration Confirmation",
            reference_doctype="Registration",
            reference_name=registration_doc.name
        )
        
    except Exception as e:
        frappe.log_error(f"Failed to send registration confirmation: {str(e)}", "Email Service")

def send_payment_confirmation(registration_doc):
    """Send payment confirmation email (mock)"""
    try:
        attendee = frappe.get_doc("Attendee", registration_doc.attendee)
        session = frappe.get_doc("Session", registration_doc.session)
        
        subject = f"Payment Confirmed - {session.session_name}"
        
        message = f"""
        <h3>Payment Confirmation</h3>
        <p>Dear {attendee.attendee_name},</p>
        
        <p>Your payment has been successfully processed!</p>
        
        <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h4>Payment Details</h4>
            <p><strong>Amount Paid:</strong> ₹{registration_doc.amount}</p>
            <p><strong>Invoice ID:</strong> {registration_doc.invoice_id}</p>
            <p><strong>Session:</strong> {session.session_name}</p>
            <p><strong>Status:</strong> Confirmed</p>
        </div>
        
        {f'<p><strong>Join Link:</strong> <a href="{registration_doc.join_link}">Click here to join the session</a></p>' if registration_doc.join_link else ''}
        
        <p>We look forward to seeing you at the conference!</p>
        """
        
        mock_sendmail(
            recipients=[attendee.email],
            subject=subject,
            message=message,
            email_type="Payment Confirmation",
            reference_doctype="Registration",
            reference_name=registration_doc.name
        )
        
    except Exception as e:
        frappe.log_error(f"Failed to send payment confirmation: {str(e)}", "Email Service")

def send_session_recommendations(attendee_email, recommendations):
    """Send session recommendations email (mock)"""
    try:
        attendee = frappe.get_doc("Attendee", {"email": attendee_email})
        
        if not recommendations:
            return
            
        subject = "Recommended Sessions for You"
        
        recommendations_html = ""
        for rec in recommendations:
            recommendations_html += f"""
            <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px;">
                <h4>{rec.session_name}</h4>
                <p><strong>Speaker:</strong> {rec.speaker}</p>
                <p><strong>Conference:</strong> {rec.conference_name}</p>
                <p><strong>Time:</strong> {rec.start_time} - {rec.end_time}</p>
            </div>
            """
        
        message = f"""
        <h3>Recommended Sessions</h3>
        <p>Dear {attendee.attendee_name},</p>
        
        <p>Based on your interests, we recommend these upcoming sessions:</p>
        
        {recommendations_html}
        
        <p>Visit the conference portal to register for these sessions.</p>
        """
        
        mock_sendmail(
            recipients=[attendee_email],
            subject=subject,
            message=message,
            email_type="Session Recommendations",
            reference_doctype="Attendee",
            reference_name=attendee.name
        )
        
    except Exception as e:
        frappe.log_error(f"Failed to send recommendations: {str(e)}", "Email Service")

