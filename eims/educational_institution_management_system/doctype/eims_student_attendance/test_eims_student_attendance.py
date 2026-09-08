# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from eims.educational_institution_management_system.doctype.eims_student_attendance.eims_student_attendance import (
	get_section_students,
)
from eims.educational_institution_management_system.report.student_attendance_summary.student_attendance_summary import (
	execute as attendance_summary,
)


class TestEIMSStudentAttendance(FrappeTestCase):
	def get_populated_section(self):
		enrollment = frappe.db.get_value(
			"EIMS Enrollment",
			{"status": "مسجل", "section": ["is", "set"]},
			["section", "academic_year"],
			as_dict=True,
		)
		if not enrollment:
			self.skipTest("no enrolled students on this site")
		return enrollment

	def test_roster_matches_enrolled_students(self):
		enrollment = self.get_populated_section()
		roster = get_section_students(enrollment.section, enrollment.academic_year)
		expected = frappe.db.count(
			"EIMS Enrollment",
			{
				"section": enrollment.section,
				"academic_year": enrollment.academic_year,
				"status": "مسجل",
			},
		)

		self.assertEqual(len(roster), expected)
		self.assertTrue(all(row.student and row.student_name for row in roster))

	def test_second_sheet_for_the_same_day_is_rejected(self):
		enrollment = self.get_populated_section()
		roster = get_section_students(enrollment.section, enrollment.academic_year)

		def build_sheet():
			return frappe.get_doc({
				"doctype": "EIMS Student Attendance",
				"attendance_date": "2026-01-15",
				"section": enrollment.section,
				"academic_year": enrollment.academic_year,
				"rows": [{"student": row.student, "status": "حاضر"} for row in roster],
			})

		sheet = build_sheet()
		sheet.insert()
		self.addCleanup(sheet.delete)

		self.assertRaises(frappe.ValidationError, build_sheet().insert)

	def test_report_buckets_blank_status_apart_and_ignores_drafts(self):
		enrollment = self.get_populated_section()
		roster = get_section_students(enrollment.section, enrollment.academic_year)
		if len(roster) < 3:
			self.skipTest("need three students to tell the buckets apart")

		def sheet(date, statuses):
			return frappe.get_doc({
				"doctype": "EIMS Student Attendance",
				"attendance_date": date,
				"section": enrollment.section,
				"academic_year": enrollment.academic_year,
				"rows": [{"student": row.student, "status": status} for row, status in zip(roster, statuses)],
			})

		submitted = sheet("2026-03-10", ["حاضر", "غائب", None])
		submitted.insert()
		submitted.submit()
		self.addCleanup(lambda: (submitted.cancel(), submitted.delete()))

		draft = sheet("2026-03-11", ["غائب"] * len(roster))
		draft.insert()
		self.addCleanup(draft.delete)

		_columns, data, *_rest = attendance_summary({
			"academic_year": enrollment.academic_year,
			"section": enrollment.section,
			"from_date": "2026-03-01",
			"to_date": "2026-03-31",
		})
		rows = {row["student"]: row for row in data}
		present, absent, blank = (rows[row.student] for row in roster[:3])

		# The draft sheet marks everyone absent; if it counted, none of these would hold.
		self.assertEqual((present["present"], present["recorded_days"], present["attendance_rate"]), (1, 1, 100.0))
		self.assertEqual((absent["absent"], absent["recorded_days"], absent["attendance_rate"]), (1, 1, 0.0))
		# A blank status is "not recorded": out of the numerator and out of the denominator.
		self.assertEqual((blank["not_recorded"], blank["recorded_days"]), (1, 0))
		self.assertEqual(data[-1]["student"], blank["student"])

	def test_submit_requires_a_status_on_every_row(self):
		enrollment = self.get_populated_section()
		roster = get_section_students(enrollment.section, enrollment.academic_year)

		partial = frappe.get_doc({
			"doctype": "EIMS Student Attendance",
			"attendance_date": "2026-04-01",
			"section": enrollment.section,
			"academic_year": enrollment.academic_year,
			"rows": [{"student": roster[0].student, "status": "حاضر"}]
			+ [{"student": row.student} for row in roster[1:]],
		})
		partial.insert()
		self.addCleanup(lambda: partial.reload() or partial.delete())

		# A half-marked sheet saves as a draft but must not become a record of the day.
		self.assertRaises(frappe.ValidationError, partial.submit)

		partial.reload()
		for row in partial.rows:
			row.status = row.status or "غائب"
		partial.save()
		partial.submit()
		self.assertEqual(partial.docstatus, 1)
		self.addCleanup(partial.cancel)

	def test_submit_rejects_an_empty_sheet(self):
		enrollment = self.get_populated_section()
		empty = frappe.get_doc({
			"doctype": "EIMS Student Attendance",
			"attendance_date": "2026-04-02",
			"section": enrollment.section,
			"academic_year": enrollment.academic_year,
			"rows": [],
		})
		empty.insert()
		self.addCleanup(empty.delete)

		self.assertRaises(frappe.ValidationError, empty.submit)
