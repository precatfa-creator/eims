import frappe


def before_tests():
	"""Create minimal test data if not present."""
	frappe.clear_cache()
	create_roles()


def after_install():
	"""Create default roles and the school institution record."""
	create_roles()
	create_demo_institution()


def create_roles():
	for role in ["Academic Admin", "Teacher", "Student"]:
		if not frappe.db.exists("Role", {"role_name": role}):
			frappe.get_doc({
				"doctype": "Role",
				"role_name": role,
				"desk_access": 1 if role != "Student" else 0,
			}).insert(ignore_permissions=True)


def create_demo_institution():
	if frappe.db.exists("EIMS Institution"):
		return
	frappe.get_doc({
		"doctype": "EIMS Institution",
		"institution_name": "مدرسة سهول العلم للتعليم الخاص",
		"short_name": "سهول العلم",
		"city": "طرابلس",
		"country": "ليبيا",
	}).insert(ignore_permissions=True)
