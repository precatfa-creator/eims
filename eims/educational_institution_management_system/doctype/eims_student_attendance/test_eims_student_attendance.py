# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from eims.api.school import get_attendance_sheet, save_attendance
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

	def test_second_sheet_for_the_same_month_is_rejected(self):
		enrollment = self.get_populated_section()
		roster = get_section_students(enrollment.section, enrollment.academic_year)

		def build_sheet(date):
			return frappe.get_doc({
				"doctype": "EIMS Student Attendance",
				"attendance_date": date,
				"section": enrollment.section,
				"academic_year": enrollment.academic_year,
				"rows": [{"date": date, "student": row.student, "status": "حاضر"} for row in roster],
			})

		sheet = build_sheet("2026-01-15")
		sheet.insert()
		self.addCleanup(sheet.delete)

		self.assertEqual(str(sheet.attendance_date), "2026-01-01")
		self.assertRaises(frappe.ValidationError, build_sheet("2026-01-20").insert)

	def test_rows_must_fall_inside_the_month_once_per_student_a_day(self):
		enrollment = self.get_populated_section()
		student = get_section_students(enrollment.section, enrollment.academic_year)[0].student

		def build_sheet(dates):
			return frappe.get_doc({
				"doctype": "EIMS Student Attendance",
				"attendance_date": "2026-02-01",
				"section": enrollment.section,
				"academic_year": enrollment.academic_year,
				"rows": [{"date": date, "student": student, "status": "حاضر"} for date in dates],
			})

		self.assertRaises(frappe.ValidationError, build_sheet(["2026-03-01"]).insert)
		self.assertRaises(frappe.ValidationError, build_sheet(["2026-02-03", "2026-02-03"]).insert)

	def test_saving_a_day_from_the_school_app_keeps_the_rest_of_the_month(self):
		enrollment = self.get_populated_section()
		roster = get_section_students(enrollment.section, enrollment.academic_year)
		args = {"section": enrollment.section, "year": enrollment.academic_year}

		def save(date, status):
			return save_attendance(
				date=date, rows=frappe.as_json([{"student": row.student, "status": status} for row in roster]), **args
			)

		first = save("2026-05-04", "حاضر")
		# save_attendance commits, so the class-level rollback would not undo the sheet.
		self.addCleanup(lambda: (frappe.delete_doc("EIMS Student Attendance", first["attendance"]), frappe.db.commit()))
		save("2026-05-05", "غائب")
		again = save("2026-05-04", "متأخر")

		# Both days land in one sheet, and re-saving 4 May left 5 May as it was.
		self.assertEqual(again["attendance"], first["attendance"])
		self.assertEqual(again["count"], len(roster))
		self.assertEqual(len(frappe.get_doc("EIMS Student Attendance", first["attendance"]).rows), 2 * len(roster))
		statuses = lambda date: {row["status"] for row in get_attendance_sheet(date=date, **args)["rows"]}
		self.assertEqual(statuses("2026-05-04"), {"متأخر"})
		self.assertEqual(statuses("2026-05-05"), {"غائب"})

	def test_report_buckets_blank_status_apart_and_ignores_drafts(self):
		enrollment = self.get_populated_section()
		roster = get_section_students(enrollment.section, enrollment.academic_year)
		if len(roster) < 3:
			self.skipTest("need three students to tell the buckets apart")

		def sheet(days):
			return frappe.get_doc({
				"doctype": "EIMS Student Attendance",
				"attendance_date": next(iter(days)),
				"section": enrollment.section,
				"academic_year": enrollment.academic_year,
				"rows": [
					{"date": date, "student": row.student, "status": status}
					for date, statuses in days.items()
					for row, status in zip(roster, statuses)
				],
			})

		# 25 April is submitted too, but falls after the report's to_date.
		submitted = sheet({"2026-04-10": ["حاضر", "غائب", None], "2026-04-25": ["غائب"] * 3})
		submitted.insert()
		# before_submit refuses a blank status, so mark the sheet submitted directly.
		frappe.db.set_value("EIMS Student Attendance", submitted.name, "docstatus", 1)
		frappe.db.sql("update `tabEIMS Student Attendance Row` set docstatus = 1 where parent = %s", submitted.name)
		self.addCleanup(lambda: frappe.db.delete("EIMS Student Attendance", submitted.name))
		self.addCleanup(lambda: frappe.db.delete("EIMS Student Attendance Row", {"parent": submitted.name}))

		draft = sheet({"2026-03-11": ["غائب"] * len(roster)})
		draft.insert()
		self.addCleanup(draft.delete)

		_columns, data, *_rest = attendance_summary({
			"academic_year": enrollment.academic_year,
			"section": enrollment.section,
			"from_date": "2026-03-01",
			"to_date": "2026-04-20",
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
			"rows": [{"date": "2026-04-01", "student": roster[0].student, "status": "حاضر"}]
			+ [{"date": "2026-04-01", "student": row.student} for row in roster[1:]],
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

	def test_saving_a_class_without_rows_fetches_its_roster(self):
		enrollment = self.get_populated_section()
		roster = get_section_students(enrollment.section, enrollment.academic_year)
		sheet = frappe.get_doc({
			"doctype": "EIMS Student Attendance",
			"attendance_date": "2026-05-20",
			"section": enrollment.section,
			"academic_year": enrollment.academic_year,
		})
		sheet.insert()
		self.addCleanup(sheet.delete)

		# The roster is recorded on the day picked, while the sheet itself holds the month.
		self.assertEqual({row.student for row in sheet.rows}, {row.student for row in roster})
		self.assertEqual({str(row.date) for row in sheet.rows}, {"2026-05-20"})
		self.assertEqual(str(sheet.attendance_date), "2026-05-01")
		# Fetched rows carry no status yet, so the month cannot be submitted.
		self.assertRaises(frappe.ValidationError, sheet.submit)

	def test_a_month_cannot_be_submitted_before_it_ends(self):
		enrollment = self.get_populated_section()
		# Two months ahead: not over yet, and no real sheet to collide with.
		day = frappe.utils.add_months(frappe.utils.getdate(), 2)
		sheet = frappe.get_doc({
			"doctype": "EIMS Student Attendance",
			"attendance_date": day,
			"section": enrollment.section,
			"academic_year": enrollment.academic_year,
		})
		sheet.insert()
		self.addCleanup(sheet.delete)
		for row in sheet.rows:
			row.status = "حاضر"
		sheet.save()

		# Fully marked, but submitting would close days that have not happened yet.
		self.assertRaises(frappe.ValidationError, sheet.submit)
