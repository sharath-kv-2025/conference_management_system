import frappe
from conference_management_system.conference_management_system.utils.test_data_generator import create_sample_data

def after_install():
    """Setup roles, permissions and comprehensive sample data after installation"""
    
    # Create roles
    create_roles()
    
    # Set up permissions
    setup_permissions()
    
    frappe.db.commit()
    
    # Create comprehensive sample data
    print("\nGenerating comprehensive sample data...")
    create_sample_data()
    
    print("\n🎉 Conference Management System installed successfully!")
    print("📊 Sample data includes:")
    print("   • 10 Conferences with various statuses")
    print("   • 50+ Sessions across conferences")
    print("   • 100 Attendees with realistic profiles")
    print("   • 200+ Registrations with payment tracking")
    print("   • Comprehensive payment details and email logs")
    print("\n🚀 Ready to use! Visit /admin-dashboard or /attendee-portal")

def create_roles():
    """Create required roles"""
    roles = [
        {"role_name": "Conference Admin", "desk_access": 1},
        {"role_name": "Attendee", "desk_access": 1}
    ]
    
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.new_doc("Role")
            role.role_name = role_data["role_name"]
            role.desk_access = role_data["desk_access"]
            role.insert()
            print(f"Created {role_data['role_name']} role")

def setup_permissions():
    """Setup doctype permissions for roles"""
    
    # Conference Admin permissions - Full access to all doctypes
    admin_doctypes = [
        "Conference", "Session", "Registration", "Attendee", 
        "Mock Payment Details", "Mock Email Log", "API Log", "Attendee Preference"
    ]
    
    for doctype in admin_doctypes:
        try:
            if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": "Conference Admin"}):
                frappe.get_doc({
                    "doctype": "Custom DocPerm",
                    "parent": doctype,
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "role": "Conference Admin",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "submit": 0,
                    "cancel": 0,
                    "amend": 0
                }).insert()
                print(f"Set Conference Admin permissions for {doctype}")
        except Exception as e:
            print(f"Error setting admin permissions for {doctype}: {e}")
    
    # Attendee permissions - Limited access
    attendee_permissions = {
        "Conference": {"read": 1, "write": 0, "create": 0, "delete": 0},
        "Session": {"read": 1, "write": 0, "create": 0, "delete": 0},
        "Registration": {"read": 1, "write": 1, "create": 1, "delete": 0},
        "Attendee": {"read": 1, "write": 1, "create": 1, "delete": 0},
        "Mock Payment Details": {"read": 1, "write": 0, "create": 0, "delete": 0},
        "Attendee Preference": {"read": 1, "write": 1, "create": 1, "delete": 1}
    }
    
    for doctype, perms in attendee_permissions.items():
        try:
            if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": "Attendee"}):
                frappe.get_doc({
                    "doctype": "Custom DocPerm",
                    "parent": doctype,
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "role": "Attendee",
                    "read": perms["read"],
                    "write": perms["write"],
                    "create": perms["create"],
                    "delete": perms["delete"],
                    "submit": 0,
                    "cancel": 0,
                    "amend": 0
                }).insert()
                print(f"Set Attendee permissions for {doctype}")
        except Exception as e:
            print(f"Error setting attendee permissions for {doctype}: {e}")