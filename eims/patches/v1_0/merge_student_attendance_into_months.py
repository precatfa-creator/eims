"""Fold daily EIMS Student Attendance sheets into one sheet per section per month.

Each row now carries its own date and the parent's attendance_date is the first of
the month. Sheets of the same section, year and month are merged into the lowest
name. The merged sheet keeps the lowest docstatus, so a month that mixed submitted
and draft days comes back as a draft to be checked and submitted once.
Raw SQL: submitted sheets cannot be edited through the ORM.
"""

import frappe
from frappe.utils import get_first_day

PARENT = "EIMS Student Attendance"
ROW = "EIMS Student Attendance Row"


def execute():
	if not frappe.db.has_column(ROW, "date"):
		return

	frappe.db.sql(
		f"""
			update `tab{ROW}` row
			inner join `tab{PARENT}` att on att.name = row.parent
			set row.date = att.attendance_date
			where row.parenttype = %s and row.date is null
		""",
		PARENT,
	)

	months = {}
	for sheet in frappe.get_all(
		PARENT,
		filters={"docstatus": ["<", 2]},
		fields=["name", "section", "academic_year", "attendance_date", "docstatus"],
		order_by="name asc",
	):
		key = (sheet.section, sheet.academic_year, get_first_day(sheet.attendance_date))
		months.setdefault(key, []).append(sheet)

	for (_section, _year, month), sheets in months.items():
		keeper, others = sheets[0].name, [s.name for s in sheets[1:]]
		docstatus = min(s.docstatus for s in sheets)

		frappe.db.sql(
			f"update `tab{PARENT}` set attendance_date = %s, docstatus = %s where name = %s",
			(month, docstatus, keeper),
		)
		frappe.db.sql(
			f"""
				update `tab{ROW}` set parent = %s, docstatus = %s
				where parenttype = %s and parent in %s
			""",
			(keeper, docstatus, PARENT, [keeper, *others]),
		)
		if others:
			frappe.db.sql(f"delete from `tab{PARENT}` where name in %s", [others])

		rows = frappe.get_all(
			ROW,
			filters={"parent": keeper, "parenttype": PARENT},
			order_by="date asc, student_name asc, idx asc",
			pluck="name",
		)
		for idx, name in enumerate(rows, 1):
			frappe.db.set_value(ROW, name, "idx", idx, update_modified=False)

	# Cancelled sheets are not merged, but their month follows the same shape.
	for sheet in frappe.get_all(PARENT, filters={"docstatus": 2}, fields=["name", "attendance_date"]):
		frappe.db.set_value(
			PARENT, sheet.name, "attendance_date", get_first_day(sheet.attendance_date), update_modified=False
		)

	# The daily sheet's print format left the app with the daily sheet.
	frappe.delete_doc_if_exists("Print Format", "EIMS Student Attendance Sheet", force=True)

	frappe.db.commit()
