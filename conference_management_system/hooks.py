app_name = "conference_management_system"
app_title = "Conference Management System"
app_publisher = "Sharath Kumar"
app_description = "Conference Management System"
app_email = "imsharathkumarv@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "conference_management_system",
# 		"logo": "/assets/conference_management_system/logo.png",
# 		"title": "Conference Management System",
# 		"route": "/conference_management_system",
# 		"has_permission": "conference_management_system.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/conference_management_system/css/conference_management_system.css"
app_include_js = "/assets/conference_management_system/js/conference_management_system.js"

# include js, css files in header of web template
web_include_css = "/assets/conference_management_system/css/conference_management_system.css"
# web_include_js = "/assets/conference_management_system/js/conference_management_system.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "conference_management_system/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "conference_management_system/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "attendee-portal"

# website user home page (by Role)
role_home_page = {
	"Conference Admin": "admin-dashboard",
	"System Manager": "admin-dashboard",
	"Attendee": "attendee-portal"
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "conference_management_system.utils.jinja_methods",
# 	"filters": "conference_management_system.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "conference_management_system.install.before_install"
after_install = "conference_management_system.conference_management_system.install.after_install"

# Fixtures
# --------
# fixtures = []

# Uninstallation
# ------------

# before_uninstall = "conference_management_system.uninstall.before_uninstall"
# after_uninstall = "conference_management_system.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "conference_management_system.utils.before_app_install"
# after_app_install = "conference_management_system.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "conference_management_system.utils.before_app_uninstall"
# after_app_uninstall = "conference_management_system.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "conference_management_system.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"Registration": {
# 		"after_insert": "conference_management_system.send_registration_confirmation"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"conference_management_system.conference_management_system.tasks.update_conference_status"
	],
	"weekly": [
		"conference_management_system.conference_management_system.tasks.send_weekly_recommendations"
	],
	"monthly": [
		"conference_management_system.conference_management_system.tasks.cleanup_old_api_logs"
	]
}

# Testing
# -------

# before_tests = "conference_management_system.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "conference_management_system.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "conference_management_system.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["conference_management_system.utils.before_request"]
# after_request = ["conference_management_system.utils.after_request"]

# Job Events
# ----------
# before_job = ["conference_management_system.utils.before_job"]
# after_job = ["conference_management_system.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"conference_management_system.auth.validate"
# ]

# Website settings
website_route_rules = [
	{"from_route": "/portal", "to_route": "attendee-portal"},
	{"from_route": "/admin", "to_route": "admin-dashboard"}
]

# Include frappe JS in web pages
# web_include_js = "/assets/frappe/js/frappe-web.min.js"

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

