# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day, getdate


class EIMSStudentAttendance(Document):
	"""One sheet per section per month; each row is one student on one day."""

	def validate(self):
		# Fill before normalising: the day picked is the day the roster is recorded on.
		self.fill_roster()
		if self.attendance_date:
			self.attendance_date = get_first_day(self.attendance_date)
		self.check_rows()
		self.check_duplicate_month()

	def fill_roster(self):
		"""Saving a sheet with a class and no rows brings in the class roster on the date picked."""
		if self.rows or self.docstatus != 0 or not (self.section and self.academic_year and self.attendance_date):
			return

		for student in get_section_students(self.section, self.academic_year):
			self.append("rows", {"date": getdate(self.attendance_date), **student})

	def before_submit(self):
		"""Submitting closes the month, so it waits for the month to end and every row to be marked."""
		if getdate() <= get_last_day(self.attendance_date):
			frappe.throw(
				_("The month is still open. Submit this sheet after {0}.").format(
					frappe.format(get_last_day(self.attendance_date), "Date")
				)
			)
		if not self.rows:
			frappe.throw(_("Add the section roster before submitting."))

		unmarked = [row.idx for row in self.rows if not row.status]
		if unmarked:
			frappe.throw(
				_("Set a status for every student before submitting. Missing on row(s): {0}.").format(
					", ".join(str(idx) for idx in unmarked)
				)
			)

	def check_rows(self):
		"""Every row falls inside the sheet's month, and a student appears once a day."""
		if not self.attendance_date:
			return

		month = getdate(self.attendance_date)
		seen = set()
		for row in self.rows:
			if not row.date:
				continue  # the mandatory check reports it
			day = getdate(row.date)
			if (day.year, day.month) != (month.year, month.month):
				frappe.throw(
					_("Row {0}: {1} is outside the sheet's month.").format(row.idx, frappe.format(day, "Date"))
				)
			if (row.student, day) in seen:
				frappe.throw(
					_("Row {0}: {1} is already recorded on {2}.").format(
						row.idx, row.student_name or row.student, frappe.format(day, "Date")
					)
				)
			seen.add((row.student, day))

		self.rows.sort(key=lambda row: (str(row.date or ""), row.student_name or row.student or ""))
		for idx, row in enumerate(self.rows, 1):
			row.idx = idx

	def check_duplicate_month(self):
		"""One attendance sheet per section per month."""
		if not (self.section and self.attendance_date):
			return

		duplicate = frappe.db.exists(
			"EIMS Student Attendance",
			{
				"section": self.section,
				"academic_year": self.academic_year,
				"attendance_date": self.attendance_date,
				"docstatus": ["<", 2],
				"name": ["!=", self.name],
			},
		)
		if duplicate:
			frappe.throw(
				_("Attendance for section {0} in {1} already exists in {2}.").format(
					self.section, getdate(self.attendance_date).strftime("%m/%Y"), duplicate
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
