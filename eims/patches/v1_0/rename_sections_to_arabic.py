"""Rename sections that still carry the English suffix.

EIMS Section is named `format:{stage}-{name_ar}`; it used to be `{stage}-{name_en}`.
Autoname only runs on insert, so every section saved before the change kept a name
like "السابع الإعدادي-A". rename_doc rewrites the eight doctypes that link to it.
"""

import frappe


def execute():
	if not frappe.db.table_exists("EIMS Section"):
		return

	for section in frappe.get_all("EIMS Section", fields=["name", "stage", "name_ar"]):
		if not (section.stage and section.name_ar):
			continue
		new_name = f"{section.stage}-{section.name_ar}"
		# A section already Arabic, or a collision with one, is left as it is.
		if new_name == section.name or frappe.db.exists("EIMS Section", new_name):
			continue
		# force: the doctype does not allow renaming from the desk.
		frappe.rename_doc("EIMS Section", section.name, new_name, force=True, show_alert=False)

	frappe.db.commit()
