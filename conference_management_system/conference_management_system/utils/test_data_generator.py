import frappe
import random
import uuid
import json
from datetime import datetime, timedelta
from conference_management_system.conference_management_system.utils.payment_processor import PaymentProcessor
from conference_management_system.conference_management_system.utils.email_service import mock_sendmail

def create_sample_data():
    """Create comprehensive sample data with 100+ records"""
    try:
        print("Creating comprehensive sample data...")
        
        # Clean existing sample data first
        cleanup_sample_data()
        
        # Create data in stages with error handling
        conferences = []
        sessions = []
        attendees = []
        registrations = []
        payments = []
        emails = []
        
        try:
            create_test_users()
            print("✓ Created test users")
        except Exception as e:
            print(f"✗ Test user creation failed: {e}")
        
        try:
            conferences = create_conferences()
            print(f"✓ Created {len(conferences)} conferences")
        except Exception as e:
            print(f"✗ Conference creation failed: {e}")
            return
        
        try:
            sessions = create_sessions(conferences)
            print(f"✓ Created {len(sessions)} sessions")
        except Exception as e:
            print(f"✗ Session creation failed: {e}")
        
        try:
            attendees = create_attendees()
            print(f"✓ Created {len(attendees)} attendees")
        except Exception as e:
            print(f"✗ Attendee creation failed: {e}")
        
        if sessions and attendees:
            try:
                registrations = create_registrations(sessions, attendees)
                print(f"✓ Created {len(registrations)} registrations")
            except Exception as e:
                print(f"✗ Registration creation failed: {e}")
        
        if registrations:
            try:
                payments = process_sample_payments(registrations)
                print(f"✓ Processed {len(payments)} payments")
            except Exception as e:
                print(f"✗ Payment processing failed: {e}")
            
            try:
                emails = generate_email_logs(registrations, attendees)
                print(f"✓ Generated {len(emails)} email logs")
            except Exception as e:
                print(f"✗ Email log generation failed: {e}")
        
        frappe.db.commit()
        print("\n✅ Sample data creation completed!")
        print(f"Summary: {len(conferences)} conferences, {len(sessions)} sessions, {len(attendees)} attendees, {len(registrations)} registrations, {len(payments)} payments, {len(emails)} emails")
        print("\n👤 Test Users Created:")
        print("Admin: admin@conference.com / confadmin")
        print("Attendee: attendee@conference.com / confattendee")
        
    except Exception as e:
        frappe.log_error(f"Error creating sample data: {str(e)}")
        frappe.db.rollback()
        print(f"❌ Critical error: {str(e)}")
        print("Sample data creation rolled back")

def cleanup_sample_data():
    """Clean up existing sample data safely"""
    try:
        # Delete in reverse dependency order with proper error handling
        cleanup_tables = [
            "tabMock Email Log",
            "tabMock Payment Details", 
            "tabAttendee Preference",
            "tabRegistration",
            "tabSession",
            "tabAttendee",
            "tabConference"
        ]
        
        for table in cleanup_tables:
            try:
                count = frappe.db.sql(f"SELECT COUNT(*) FROM `{table}`")[0][0]
                if count > 0:
                    frappe.db.sql(f"DELETE FROM `{table}`")
                    print(f"Cleaned {count} records from {table}")
            except Exception as table_error:
                print(f"Warning cleaning {table}: {table_error}")
                continue
        
        frappe.db.commit()
        print("Sample data cleanup completed")
    except Exception as e:
        print(f"Cleanup error: {e}")
        frappe.db.rollback()

def create_conferences():
    """Create 6 sample conferences"""
    conference_names = [
        "Tech Summit 2024", "AI Conference 2024", "DevOps World 2024", 
        "Cloud Computing Expo", "Cybersecurity Summit", "Data Science Conference"
    ]
    
    locations = ["Mumbai", "Bangalore", "Delhi", "Hyderabad", "Chennai", "Pune", "Kolkata"]
    conferences = []
    
    for i, name in enumerate(conference_names):
        existing = frappe.db.get_value("Conference", {"conference_name": name}, "name")
        if existing:
            conferences.append(existing)
            continue
            
        start_date = datetime.now() + timedelta(days=random.randint(10, 180))
        conf = frappe.new_doc("Conference")
        conf.conference_name = name
        conf.start_date = start_date.date()
        conf.end_date = (start_date + timedelta(days=random.randint(1, 3))).date()
        conf.location = random.choice(locations)
        conf.description = f"Professional conference on {name.lower()}"
        conf.registration_fee = random.choice([1500, 2000, 2500, 3000, 3500])
        conf.status = random.choice(["Upcoming", "Upcoming", "Upcoming", "Ongoing"]) if i < 8 else "Completed"
        conf.insert(ignore_permissions=True)
        conferences.append(conf.name)
    
    return conferences

def create_sessions(conferences):
    """Create 15-20 sessions across conferences with better conflict prevention"""
    session_topics = [
        "Introduction to AI", "Machine Learning Basics", "Deep Learning", "Neural Networks",
        "Cloud Architecture", "Microservices", "DevOps Best Practices", "CI/CD Pipeline",
        "Cybersecurity Fundamentals", "Ethical Hacking", "Data Analytics", "Big Data",
        "Mobile UI/UX", "React Native", "Flutter Development", "iOS Development",
        "Blockchain Basics", "Smart Contracts", "Cryptocurrency", "DeFi",
        "IoT Sensors", "Edge Computing", "5G Technology", "Automation",
        "Digital Strategy", "Agile Methodology", "Project Management", "Leadership"
    ]
    
    speakers = [
        "Dr. John Smith", "Prof. Jane Doe", "Mr. Alex Johnson", "Ms. Sarah Wilson",
        "Dr. Michael Brown", "Prof. Emily Davis", "Mr. David Miller", "Ms. Lisa Garcia",
        "Dr. Robert Taylor", "Prof. Jennifer Lee", "Mr. Christopher White", "Ms. Amanda Clark"
    ]
    
    sessions = []
    session_count = 0
    
    # Extended time slots to reduce conflicts
    time_slots = [(9, 10), (10, 11), (11, 12), (12, 13), (14, 15), (15, 16), (16, 17), (17, 18)]
    
    for conf_id in conferences:
        try:
            conf_doc = frappe.get_doc("Conference", conf_id)
            
            # Calculate conference duration in days
            conf_duration = (conf_doc.end_date - conf_doc.start_date).days + 1
            
            # Create sessions across multiple days if conference is multi-day
            sessions_per_conf = min(random.randint(2, 4), len(time_slots) * conf_duration)
            
            # Track used slots per date
            used_slots_by_date = {}
            
            for i in range(sessions_per_conf):
                if session_count >= 20:
                    break
                
                # Try up to 10 times to find a non-conflicting slot
                for attempt in range(10):
                    try:
                        topic = random.choice(session_topics)
                        session_name = f"{topic} - {conf_doc.conference_name[:10]} - {session_count + 1}"
                        
                        # Check if session name already exists
                        if frappe.db.exists("Session", {"session_name": session_name}):
                            session_name = f"{topic} - {uuid.uuid4().hex[:6]} - {session_count + 1}"
                        
                        # Pick a random day within conference dates
                        day_offset = random.randint(0, conf_duration - 1)
                        session_date = conf_doc.start_date + timedelta(days=day_offset)
                        
                        # Initialize date tracking if needed
                        if session_date not in used_slots_by_date:
                            used_slots_by_date[session_date] = set()
                        
                        # Get available time slots for this date
                        available_slots = [slot for slot in time_slots if slot not in used_slots_by_date[session_date]]
                        
                        if not available_slots:
                            continue  # Try another date
                        
                        start_hour, end_hour = random.choice(available_slots)
                        used_slots_by_date[session_date].add((start_hour, end_hour))
                        
                        session = frappe.new_doc("Session")
                        session.session_name = session_name
                        session.conference = conf_id
                        session.speaker = random.choice(speakers)
                        session.session_date = session_date
                        session.start_time = f"{start_hour:02d}:00:00"
                        session.end_time = f"{end_hour:02d}:00:00"
                        session.max_attendees = random.choice([30, 50, 75, 100, 150])
                        session.description = f"Comprehensive session on {topic.lower()}"
                        
                        session.insert(ignore_permissions=True)
                        sessions.append(session.name)
                        session_count += 1
                        break  # Successfully created session
                        
                    except Exception as session_error:
                        print(f"Attempt {attempt + 1} failed for session creation: {session_error}")
                        continue
                        
        except Exception as e:
            print(f"Error creating sessions for conference {conf_id}: {e}")
            continue
    
    return sessions

def create_attendees():
    """Create 50 attendees"""
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", "James", "Maria",
                   "William", "Jennifer", "Richard", "Patricia", "Charles", "Linda", "Joseph", "Elizabeth",
                   "Thomas", "Barbara", "Christopher", "Susan", "Daniel", "Jessica", "Matthew", "Karen"]
    
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
                  "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson"]
    

    
    attendees = []
    
    for i in range(50):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
        
        existing = frappe.db.get_value("Attendee", {"email": email}, "name")
        if existing:
            attendees.append(existing)
            continue
            
        try:
            attendee = frappe.new_doc("Attendee")
            attendee.attendee_name = f"{first_name} {last_name}"
            attendee.email = email
            attendee.email_verified = random.choice([1, 1, 1, 0])  # 75% verified
            attendee.insert(ignore_permissions=True)
            attendees.append(attendee.name)
        except Exception as e:
            print(f"Error creating attendee {email}: {e}")
            continue
    
    return attendees

def create_registrations(sessions, attendees):
    """Create 100 registrations with improved conflict handling"""
    registrations = []
    attendee_session_map = {}  # Track attendee registrations to avoid conflicts
    
    for session_id in sessions:
        try:
            session_doc = frappe.get_doc("Session", session_id)
            conf_doc = frappe.get_doc("Conference", session_doc.conference)
            
            # Calculate reasonable number of registrations (50-80% of capacity)
            max_registrations = min(int(session_doc.max_attendees * 0.8), len(attendees))
            num_registrations = random.randint(2, max(2, max_registrations))
            
            # Get available attendees (not conflicting with this session time)
            available_attendees = []
            for attendee_id in attendees:
                # Check if attendee already registered for this session
                if frappe.db.exists("Registration", {"session": session_id, "attendee": attendee_id}):
                    continue
                
                # Check for time conflicts with existing registrations
                has_conflict = False
                if attendee_id in attendee_session_map:
                    for existing_session_id in attendee_session_map[attendee_id]:
                        try:
                            existing_session = frappe.get_doc("Session", existing_session_id)
                            # Check if same date and overlapping times
                            if (existing_session.session_date == session_doc.session_date and
                                existing_session.conference == session_doc.conference):
                                # Check time overlap
                                if (session_doc.start_time < existing_session.end_time and 
                                    session_doc.end_time > existing_session.start_time):
                                    has_conflict = True
                                    break
                        except Exception:
                            continue
                
                if not has_conflict:
                    available_attendees.append(attendee_id)
            
            # Select attendees for this session
            if available_attendees:
                num_to_select = min(num_registrations, len(available_attendees))
                selected_attendees = random.sample(available_attendees, num_to_select)
                
                for attendee_id in selected_attendees:
                    try:
                        registration = frappe.new_doc("Registration")
                        registration.conference = session_doc.conference
                        registration.session = session_id
                        registration.attendee = attendee_id
                        registration.registration_date = (datetime.now() - timedelta(days=random.randint(1, 30))).date()
                        registration.payment_status = "Pending"
                        registration.amount = conf_doc.registration_fee
                        registration.invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
                        registration.join_link = f"https://conference.local/join/{uuid.uuid4().hex[:12]}"
                        
                        registration.insert(ignore_permissions=True)
                        registrations.append(registration.name)
                        
                        # Track this registration to prevent future conflicts
                        if attendee_id not in attendee_session_map:
                            attendee_session_map[attendee_id] = []
                        attendee_session_map[attendee_id].append(session_id)
                        
                    except Exception as e:
                        print(f"Error creating registration for session {session_id}, attendee {attendee_id}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error processing session {session_id}: {e}")
            continue
    
    return registrations

def process_sample_payments(registrations):
    """Process payments for 70% of registrations"""
    payments = []
    payment_methods = ["Credit Card", "Debit Card", "UPI", "Net Banking"]
    
    # Process 70% of registrations
    to_process = random.sample(registrations, int(len(registrations) * 0.7))
    
    for reg_name in to_process:
        try:
            payment_method = random.choice(payment_methods)
            result = PaymentProcessor.process_payment(reg_name, payment_method)
            
            if result.get("success"):
                payments.append(result.get("payment_details"))
        except Exception as e:
            print(f"Payment processing failed for {reg_name}: {e}")
    
    return payments

def generate_email_logs(registrations, attendees):
    """Generate email logs for registrations and other communications"""
    emails = []
    
    # Registration confirmation emails
    for reg_id in registrations:
        try:
            reg_doc = frappe.get_doc("Registration", reg_id)
            attendee_doc = frappe.get_doc("Attendee", reg_doc.attendee)
            
            mock_sendmail(
                recipients=[attendee_doc.email],
                subject=f"Registration Confirmed - {reg_id}",
                message="Your registration has been confirmed.",
                email_type="Registration Confirmation",
                reference_doctype="Registration",
                reference_name=reg_id
            )
            emails.append(f"Registration confirmation for {reg_id}")
            
            # Payment confirmation for paid registrations
            if reg_doc.payment_status == "Paid":
                mock_sendmail(
                    recipients=[attendee_doc.email],
                    subject=f"Payment Confirmed - {reg_id}",
                    message="Your payment has been processed successfully.",
                    email_type="Payment Confirmation",
                    reference_doctype="Registration",
                    reference_name=reg_id
                )
                emails.append(f"Payment confirmation for {reg_id}")
                
        except Exception as e:
            print(f"Email generation failed for {reg_id}: {e}")
    
    # OTP emails for some attendees
    if len(attendees) >= 20:
        sample_attendees = random.sample(attendees, 20)
        for attendee_id in sample_attendees:
            try:
                attendee_doc = frappe.get_doc("Attendee", attendee_id)
                otp = f"{random.randint(100000, 999999)}"
                mock_sendmail(
                    recipients=[attendee_doc.email],
                    subject="Email Verification - Conference Portal",
                    message=f"Your verification code is: {otp}",
                    email_type="OTP Verification"
                )
                emails.append(f"OTP email for {attendee_doc.email}")
            except Exception as e:
                print(f"OTP email failed for attendee {attendee_id}: {e}")
    
    return emails

def create_test_users():
    """Create test users with proper roles"""
    users_to_create = [
        {
            "email": "admin@conference.com",
            "first_name": "Conference",
            "last_name": "Admin",
            "password": "confadmin",
            "roles": ["Conference Admin", "System Manager"]
        },
        {
            "email": "attendee@conference.com",
            "first_name": "Test",
            "last_name": "Attendee",
            "password": "confattendee",
            "roles": ["Attendee"]
        }
    ]
    
    for user_data in users_to_create:
        try:
            # Check if user already exists
            if frappe.db.exists("User", user_data["email"]):
                print(f"✓ User {user_data['email']} already exists")
                continue
            
            # Create user
            user = frappe.new_doc("User")
            user.email = user_data["email"]
            user.first_name = user_data["first_name"]
            user.last_name = user_data["last_name"]
            user.new_password = user_data["password"]
            user.send_welcome_email = 0
            user.insert(ignore_permissions=True)
            
            # Add roles
            for role in user_data["roles"]:
                user.add_roles(role)
            
            print(f"✓ Created user: {user_data['email']} with password: {user_data['password']}")
            
        except Exception as e:
            print(f"Error creating user {user_data['email']}: {e}")
            continue