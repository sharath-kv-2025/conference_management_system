import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "label": _("Timestamp"),
            "fieldname": "timestamp",
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "label": _("API Endpoint"),
            "fieldname": "api_endpoint",
            "fieldtype": "Data",
            "width": 300
        },
        {
            "label": _("Method"),
            "fieldname": "method",
            "fieldtype": "Data",
            "width": 80
        },
        {
            "label": _("Status Code"),
            "fieldname": "status_code",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("User"),
            "fieldname": "owner",
            "fieldtype": "Link",
            "options": "User",
            "width": 150
        },
        {
            "label": _("Request Size"),
            "fieldname": "request_size",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": _("Response Size"),
            "fieldname": "response_size",
            "fieldtype": "Int",
            "width": 120
        }
    ]

def get_data(filters):
    try:
        conditions = get_conditions(filters)
        
        data = frappe.db.sql(f"""
            SELECT 
                timestamp,
                COALESCE(api_endpoint, '') as api_endpoint,
                COALESCE(method, '') as method,
                COALESCE(status_code, 0) as status_code,
                COALESCE(owner, '') as owner,
                COALESCE(CHAR_LENGTH(request_body), 0) as request_size,
                COALESCE(CHAR_LENGTH(response_body), 0) as response_size
            FROM `tabAPI Log`
            {conditions}
            ORDER BY timestamp DESC
            LIMIT 1000
        """, as_dict=True)
        
        # Clean up data
        for row in data:
            row['status_code'] = int(row.get('status_code', 0) or 0)
            row['request_size'] = int(row.get('request_size', 0) or 0)
            row['response_size'] = int(row.get('response_size', 0) or 0)
        
        return data
    except Exception as e:
        frappe.log_error(f"Error fetching API usage data: {str(e)}", "API Usage Report")
        return []

def get_conditions(filters):
    try:
        conditions = "WHERE 1=1"
        
        if filters and filters.get("method"):
            conditions += f" AND method = '{frappe.db.escape(filters.get('method'))}'"
        
        if filters and filters.get("status_code"):
            try:
                status_code = int(filters.get('status_code'))
                conditions += f" AND status_code = {status_code}"
            except (ValueError, TypeError):
                pass  # Skip invalid status codes
        
        if filters and filters.get("api_endpoint"):
            conditions += f" AND api_endpoint LIKE '%{frappe.db.escape(filters.get('api_endpoint'))}%'"
        
        if filters and filters.get("from_date"):
            from_date = filters.get('from_date')
            conditions += f" AND DATE(timestamp) >= '{from_date}'"
        
        if filters and filters.get("to_date"):
            to_date = filters.get('to_date')
            conditions += f" AND DATE(timestamp) <= '{to_date}'"
        
        return conditions
    except Exception as e:
        frappe.log_error(f"Error building filter conditions: {str(e)}", "API Usage Report")
        return "WHERE 1=1"