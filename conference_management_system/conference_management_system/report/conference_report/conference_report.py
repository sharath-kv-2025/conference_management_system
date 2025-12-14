import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "label": _("Conference"),
            "fieldname": "conference_name",
            "fieldtype": "Link",
            "options": "Conference",
            "width": 200
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Start Date"),
            "fieldname": "start_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("End Date"),
            "fieldname": "end_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Location"),
            "fieldname": "location",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Total Sessions"),
            "fieldname": "total_sessions",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": _("Total Attendees"),
            "fieldname": "total_attendees",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": _("Paid Registrations"),
            "fieldname": "paid_registrations",
            "fieldtype": "Int",
            "width": 130
        },
        {
            "label": _("Revenue (₹)"),
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Registration Fee (₹)"),
            "fieldname": "registration_fee",
            "fieldtype": "Currency",
            "width": 140
        }
    ]

def get_data(filters):
    try:
        conditions = get_conditions(filters)
        
        try:
            data = frappe.db.sql(f"""
                SELECT 
                    c.name,
                    c.conference_name,
                    c.status,
                    c.start_date,
                    c.end_date,
                    COALESCE(c.location, '') as location,
                    COALESCE(c.registration_fee, 0) as registration_fee,
                    COUNT(DISTINCT s.name) as total_sessions,
                    COUNT(DISTINCT r.attendee) as total_attendees,
                    COUNT(DISTINCT CASE WHEN r.payment_status = 'Paid' THEN r.name END) as paid_registrations,
                    COALESCE(SUM(CASE WHEN r.payment_status = 'Paid' THEN r.amount ELSE 0 END), 0) as revenue
                FROM `tabConference` c
                LEFT JOIN `tabSession` s ON c.name = s.conference
                LEFT JOIN `tabRegistration` r ON c.name = r.conference
                {conditions}
                GROUP BY c.name, c.conference_name, c.status, c.start_date, c.end_date, c.location, c.registration_fee
                ORDER BY c.start_date DESC
            """, as_dict=True)
        except Exception as sql_error:
            frappe.log_error(f"SQL query failed in conference report: {str(sql_error)}", "Conference Report")
            return []
        
        # Clean up data
        try:
            for row in data:
                row['total_sessions'] = int(row.get('total_sessions', 0) or 0)
                row['total_attendees'] = int(row.get('total_attendees', 0) or 0)
                row['paid_registrations'] = int(row.get('paid_registrations', 0) or 0)
                row['revenue'] = float(row.get('revenue', 0) or 0)
                row['registration_fee'] = float(row.get('registration_fee', 0) or 0)
        except Exception as data_error:
            frappe.log_error(f"Error processing report data: {str(data_error)}", "Conference Report")
            return []
        
        return data
    except Exception as e:
        frappe.log_error(f"Error fetching conference report data: {str(e)}", "Conference Report")
        return []

def get_conditions(filters):
    try:
        conditions = "WHERE 1=1"
        
        if filters and filters.get("status"):
            conditions += f" AND c.status = '{frappe.db.escape(filters.get('status'))}'"
        
        if filters and filters.get("from_date"):
            from_date = filters.get('from_date')
            conditions += f" AND c.start_date >= '{from_date}'"
        
        if filters and filters.get("to_date"):
            to_date = filters.get('to_date')
            conditions += f" AND c.end_date <= '{to_date}'"
        
        return conditions
    except Exception as e:
        frappe.log_error(f"Error building filter conditions: {str(e)}", "Conference Report")
        return "WHERE 1=1"