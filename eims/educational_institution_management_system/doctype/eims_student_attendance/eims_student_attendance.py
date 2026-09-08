# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EIMSStudentAttendance(Document):
	def validate(self):
		self.check_duplicate_day()

	def before_submit(self):
		"""A sheet is only a record of the day once every student has been marked."""
		if not self.rows:
			frappe.throw(_("Add the section roster before submitting."))

		unmarked = [row.idx for row in self.rows if not row.status]
		if unmarked:
			frappe.throw(
				_("Set a status for every student before submitting. Missing on row(s): {0}.").format(
					", ".join(str(idx) for idx in unmarked)
				)
			)

	def check_duplicate_day(self):
		"""One attendance sheet per section per day."""
		if not (self.section and self.attendance_date):
			return

		duplicate = frappe.db.exists(
			"EIMS Student Attendance",
			{
				"section": self.section,
				"attendance_date": self.attendance_date,
				"docstatus": ["<", 2],
				"name": ["!=", self.name],
			},
		)
		if duplicate:
			frappe.throw(
				_("Attendance for section {0} on {1} already exists in {2}.").format(
					self.section, frappe.format(self.attendance_date, "Date"), duplicate
				)
			)


@frappe.whitelist()
def get_section_students(section, academic_year):
	"""Return the enrolled roster of a section, ordered by student name."""
	return frappe.db.sql(
		"""
			select distinct student.name as student, student.student_name
			from `tabEIMS Enrollment` enrollment
			inner join `tabEIMS Student` student on student.name = enrollment.student
			where enrollment.docstatus < 2
				and enrollment.status = 'مسجل'
				and enrollment.section = %(section)s
				and enrollment.academic_year = %(academic_year)s
			order by student.student_name, student.name
		""",
		{"section": section, "academic_year": academic_year},
		as_dict=True,
	)
