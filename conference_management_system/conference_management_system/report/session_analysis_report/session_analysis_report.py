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
            "width": 180
        },
        {
            "label": _("Session"),
            "fieldname": "session_name",
            "fieldtype": "Link",
            "options": "Session",
            "width": 200
        },
        {
            "label": _("Speaker"),
            "fieldname": "speaker",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Start Time"),
            "fieldname": "start_time",
            "fieldtype": "Time",
            "width": 100
        },
        {
            "label": _("End Time"),
            "fieldname": "end_time",
            "fieldtype": "Time",
            "width": 100
        },
        {
            "label": _("Max Capacity"),
            "fieldname": "max_attendees",
            "fieldtype": "Int",
            "width": 110
        },
        {
            "label": _("Total Registrations"),
            "fieldname": "total_registrations",
            "fieldtype": "Int",
            "width": 140
        },
        {
            "label": _("Paid Registrations"),
            "fieldname": "paid_registrations",
            "fieldtype": "Int",
            "width": 130
        },
        {
            "label": _("Remaining Capacity"),
            "fieldname": "remaining_capacity",
            "fieldtype": "Int",
            "width": 140
        },
        {
            "label": _("Occupancy %"),
            "fieldname": "occupancy_percentage",
            "fieldtype": "Percent",
            "width": 110
        },
        {
            "label": _("Revenue (₹)"),
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "width": 120
        }
    ]

def get_data(filters):
    try:
        # Split conditions into WHERE and HAVING
        where_conditions = "WHERE 1=1"
        having_clause = ""
        
        if filters:
            if filters.get("conference"):
                where_conditions += f" AND s.conference = '{frappe.db.escape(filters.get('conference'))}'"
            if filters.get("speaker"):
                where_conditions += f" AND s.speaker LIKE '%{frappe.db.escape(filters.get('speaker'))}%'"
            if filters.get("session_name"):
                where_conditions += f" AND s.session_name LIKE '%{frappe.db.escape(filters.get('session_name'))}%'"
            if filters.get("from_date"):
                from_date = filters.get('from_date')
                where_conditions += f" AND c.start_date >= '{from_date}'"
            if filters.get("to_date"):
                to_date = filters.get('to_date')
                where_conditions += f" AND c.end_date <= '{to_date}'"
            if filters.get("min_occupancy"):
                try:
                    min_occ = int(filters.get('min_occupancy'))
                    having_clause = f" HAVING occupancy_percentage >= {min_occ}"
                except (ValueError, TypeError):
                    pass  # Skip invalid occupancy values
        
        data = frappe.db.sql(f"""
            SELECT 
                s.name,
                c.conference_name,
                s.session_name,
                COALESCE(s.speaker, '') as speaker,
                s.start_time,
                s.end_time,
                COALESCE(s.max_attendees, 0) as max_attendees,
                COUNT(r.name) as total_registrations,
                COUNT(CASE WHEN r.payment_status = 'Paid' THEN r.name END) as paid_registrations,
                GREATEST(0, COALESCE(s.max_attendees, 0) - COUNT(r.name)) as remaining_capacity,
                CASE 
                    WHEN COALESCE(s.max_attendees, 0) > 0 
                    THEN ROUND((COUNT(r.name) * 100.0 / s.max_attendees), 2)
                    ELSE 0 
                END as occupancy_percentage,
                COALESCE(SUM(CASE WHEN r.payment_status = 'Paid' THEN r.amount ELSE 0 END), 0) as revenue
            FROM `tabSession` s
            LEFT JOIN `tabConference` c ON s.conference = c.name
            LEFT JOIN `tabRegistration` r ON s.name = r.session
            {where_conditions}
            GROUP BY s.name, c.conference_name, s.session_name, s.speaker, s.start_time, s.end_time, s.max_attendees, c.start_date
            {having_clause}
            ORDER BY c.start_date DESC, s.start_time ASC
        """, as_dict=True)
        
        # Clean up data
        for row in data:
            row['max_attendees'] = int(row.get('max_attendees', 0) or 0)
            row['total_registrations'] = int(row.get('total_registrations', 0) or 0)
            row['paid_registrations'] = int(row.get('paid_registrations', 0) or 0)
            row['remaining_capacity'] = int(row.get('remaining_capacity', 0) or 0)
            row['occupancy_percentage'] = float(row.get('occupancy_percentage', 0) or 0)
            row['revenue'] = float(row.get('revenue', 0) or 0)
        
        return data
    except Exception as e:
        frappe.log_error(f"Error fetching session analysis data: {str(e)}", "Session Analysis Report")
        return []

def get_conditions(filters):
    try:
        conditions = "WHERE 1=1"
        
        if filters and filters.get("conference"):
            conditions += f" AND s.conference = '{frappe.db.escape(filters.get('conference'))}'"
        
        if filters and filters.get("speaker"):
            conditions += f" AND s.speaker LIKE '%{frappe.db.escape(filters.get('speaker'))}%'"
        
        if filters and filters.get("session_name"):
            conditions += f" AND s.session_name LIKE '%{frappe.db.escape(filters.get('session_name'))}%'"
        
        if filters and filters.get("from_date"):
            conditions += f" AND c.start_date >= '{frappe.db.escape(filters.get('from_date'))}'"
        
        if filters and filters.get("to_date"):
            conditions += f" AND c.end_date <= '{frappe.db.escape(filters.get('to_date'))}'"
        
        # Add HAVING clause for occupancy filter (needs to be added after GROUP BY)
        having_conditions = ""
        if filters and filters.get("min_occupancy"):
            min_occ = int(filters.get('min_occupancy'))
            having_conditions = f" HAVING occupancy_percentage >= {min_occ}"
        
        return conditions + having_conditions
    except Exception as e:
        frappe.log_error(f"Error building filter conditions: {str(e)}", "Session Analysis Report")
        return "WHERE 1=1"