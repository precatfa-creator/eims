"""Academic Year defaults and validation shared by EIMS operational documents."""

import frappe
from frappe import _


CURRICULUM_GUARDED_DOCTYPES = {
	"EIMS Assessment",
	"EIMS Daily Accomplishment",
	"EIMS Student Attendance",
	"EIMS Teacher Assignment",
}


def apply_active_academic_year(doc, method=None):
	"""Default year-aware records to the active year and validate their context."""
	if not doc.meta.has_field("academic_year"):
		return

	if not doc.academic_year:
		doc.academic_year = frappe.db.get_value("EIMS Academic Year", {"is_active": 1}, "name")

	if not doc.academic_year:
		frappe.throw(_("Create and activate an Academic Year before creating academic records."))

	if not frappe.db.exists("EIMS Academic Year", doc.academic_year):
		frappe.throw(_("Academic Year {0} does not exist.").format(doc.academic_year))

	_resolve_result_enrollment(doc)
	_validate_subject_and_section_context(doc)
	_validate_curriculum_context(doc)
	_validate_student_context(doc)
	_validate_staff_context(doc)
	_validate_child_context(doc)


def _resolve_result_enrollment(doc):
	"""Results always use the student's placement for the selected year."""
	if doc.doctype != "EIMS Result" or not doc.student or not doc.academic_year:
		return

	enrollment = frappe.db.get_value(
		"EIMS Enrollment",
		{"student": doc.student, "academic_year": doc.academic_year, "status": "مسجل"},
		["stage", "section"],
		as_dict=True,
	)
	if not enrollment:
		frappe.throw(
			_("Create an Enrollment for this student and Academic Year before recording results.")
		)

	doc.stage = enrollment.stage
	doc.section = enrollment.section


def _validate_subject_and_section_context(doc):
	"""Keep direct subject, stage, and section links on the same curriculum path."""
	if doc.meta.has_field("subject") and doc.subject and doc.meta.has_field("stage"):
		subject_stage = frappe.db.get_value("EIMS Subject", doc.subject, "stage")
		if subject_stage:
			if doc.stage and doc.stage != subject_stage:
				frappe.throw(_("The selected subject does not belong to this stage."))
			doc.stage = subject_stage

	if not (doc.meta.has_field("section") and doc.section and doc.meta.has_field("stage")):
		return

	section_stage = frappe.db.get_value("EIMS Section", doc.section, "stage")
	if not section_stage:
		return
	if doc.stage and doc.stage != section_stage:
		frappe.throw(_("The selected section does not belong to this stage."))
	doc.stage = section_stage


def _validate_curriculum_context(doc):
	"""Require configured subject offerings once a year/stage curriculum exists."""
	if doc.doctype not in CURRICULUM_GUARDED_DOCTYPES or not doc.subject:
		return

	if not doc.stage:
		return

	curriculum_filters = {"academic_year": doc.academic_year, "stage": doc.stage}
	if not frappe.db.exists("EIMS Academic Curriculum", curriculum_filters):
		return

	curriculum_filters.update({"subject": doc.subject, "is_active": 1})
	if not frappe.db.exists("EIMS Academic Curriculum", curriculum_filters):
		frappe.throw(
			_("Subject {0} is not active in the Academic Year curriculum for this stage.").format(doc.subject)
		)


def _validate_child_context(doc):
	"""Validate parent-controlled links held in child tables."""
	if doc.doctype == "EIMS Assessment":
		_validate_enrolled_students(doc.students, doc.academic_year, doc.stage, doc.section, doc.subject)
	elif doc.doctype == "EIMS Student Attendance":
		_validate_enrolled_students(doc.rows, doc.academic_year, doc.stage, doc.section, doc.subject)
	elif doc.doctype == "EIMS School Activity":
		_validate_enrolled_students(doc.participants, doc.academic_year)
	elif doc.doctype == "EIMS Staff Attendance":
		for row in doc.rows or []:
			_validate_staff_membership(row.staff, doc.academic_year)
	elif doc.doctype == "EIMS Result":
		_validate_result_subjects(doc)
	elif doc.doctype == "EIMS Timetable":
		_validate_timetable_slots(doc)


def _validate_student_context(doc):
	if doc.doctype in {"EIMS Disciplinary Action", "EIMS Request"}:
		_validate_student_enrollment(doc.student, doc.academic_year)


def _validate_staff_context(doc):
	staff_field = {
		"EIMS Daily Accomplishment": "teacher",
		"EIMS School Activity": "supervisor",
		"EIMS Student Attendance": "teacher",
		"EIMS Teacher Assignment": "staff",
		"EIMS Timetable": "staff",
	}.get(doc.doctype)
	if staff_field:
		_validate_staff_membership(doc.get(staff_field), doc.academic_year)
	if doc.doctype in {"EIMS Daily Accomplishment", "EIMS Student Attendance", "EIMS Timetable"}:
		_validate_teacher_assignment(
			doc.get(staff_field), doc.academic_year, doc.stage, doc.section, doc.get("subject")
		)


def _validate_staff_membership(staff, academic_year):
	"""Enforce staff-year assignments once the year has been configured."""
	if not staff or not academic_year:
		return

	year_filters = {"academic_year": academic_year}
	if not frappe.db.exists("EIMS Staff Academic Assignment", year_filters):
		return
	if not frappe.db.exists("EIMS Staff Academic Assignment", {**year_filters, "staff": staff, "status": "Active"}):
		frappe.throw(_("Staff member {0} is not assigned to the selected Academic Year.").format(staff))


def _validate_teacher_assignment(staff, academic_year, stage, section=None, subject=None):
	"""Require operational records to match a teacher's class assignment."""
	if not staff or not academic_year or not stage:
		return

	assignments = frappe.get_all(
		"EIMS Teacher Assignment",
		filters={"staff": staff, "academic_year": academic_year, "stage": stage},
		fields=["section", "subject"],
	)
	for assignment in assignments:
		section_matches = not section or not assignment.section or assignment.section == section
		subject_matches = not subject or not assignment.subject or assignment.subject == subject
		if section_matches and subject_matches:
			return

	frappe.throw(
		_("Teacher {0} is not assigned to the selected stage, section, and subject.").format(staff)
	)


def _validate_enrolled_students(rows, academic_year, stage=None, section=None, subject=None):
	if not academic_year:
		return
	if subject:
		_validate_subject_stage(subject, stage)
		_validate_active_curriculum(academic_year, stage, subject)

	for row in rows or []:
		if not row.student:
			continue
		_validate_student_enrollment(row.student, academic_year, stage, section)


def _validate_student_enrollment(student, academic_year, stage=None, section=None):
	if not student or not academic_year:
		return
	filters = {"student": student, "academic_year": academic_year, "status": "مسجل"}
	if stage:
		filters["stage"] = stage
	if section:
		filters["section"] = section
	if frappe.db.exists("EIMS Enrollment", filters):
		return

	message = (
		"Student {0} does not have an active enrollment in the selected Academic Year and section."
		if section
		else "Student {0} does not have an active enrollment in the selected Academic Year."
	)
	frappe.throw(_(message).format(student))


def _validate_result_subjects(doc):
	for row in doc.results or []:
		if not row.subject:
			continue
		_validate_subject_stage(row.subject, doc.stage)
		_validate_active_curriculum(doc.academic_year, doc.stage, row.subject)


def _validate_timetable_slots(doc):
	for row in doc.slots or []:
		if not row.subject:
			continue

		subject_stage = _validate_subject_stage(row.subject, row.stage)
		row.stage = subject_stage
		if row.section:
			section_stage = frappe.db.get_value("EIMS Section", row.section, "stage")
			if section_stage and section_stage != subject_stage:
				frappe.throw(_("The selected section does not belong to this stage."))
		if doc.section and row.section and doc.section != row.section:
			frappe.throw(_("A timetable slot must use the timetable section."))
		_validate_active_curriculum(doc.academic_year, subject_stage, row.subject)


def _validate_subject_stage(subject, stage):
	subject_stage = frappe.db.get_value("EIMS Subject", subject, "stage")
	if subject_stage and stage and subject_stage != stage:
		frappe.throw(_("The selected subject does not belong to this stage."))
	return subject_stage


def _validate_active_curriculum(academic_year, stage, subject):
	if not academic_year or not stage:
		return

	filters = {"academic_year": academic_year, "stage": stage}
	if not frappe.db.exists("EIMS Academic Curriculum", filters):
		return

	filters.update({"subject": subject, "is_active": 1})
	if not frappe.db.exists("EIMS Academic Curriculum", filters):
		frappe.throw(
			_("Subject {0} is not active in the Academic Year curriculum for this stage.").format(subject)
		)


def ensure_staff_academic_assignment(doc, method=None):
	"""Create the first staff-year record from a staff member's hiring year."""
	if not doc.hired_year:
		return

	name = f"{doc.name}-{doc.hired_year}"
	if frappe.db.exists("EIMS Staff Academic Assignment", name):
		return

	frappe.get_doc(
		{
			"doctype": "EIMS Staff Academic Assignment",
			"staff": doc.name,
			"academic_year": doc.hired_year,
			"role": doc.role,
			"title": doc.title_en or doc.title_ar,
			"start_date": doc.hire_date,
		}
	).insert(ignore_permissions=True)


def backfill_staff_academic_assignments():
	"""Create missing staff-year records from existing staff hiring data."""
	created = 0
	for staff in frappe.get_all(
		"EIMS Staff", fields=["name", "hired_year", "role", "title_ar", "title_en", "hire_date"]
	):
		if not staff.hired_year:
			continue
		name = f"{staff.name}-{staff.hired_year}"
		if frappe.db.exists("EIMS Staff Academic Assignment", name):
			continue
		frappe.get_doc(
			{
				"doctype": "EIMS Staff Academic Assignment",
				"staff": staff.name,
				"academic_year": staff.hired_year,
				"role": staff.role,
				"title": staff.title_en or staff.title_ar,
				"start_date": staff.hire_date,
			}
		).insert(ignore_permissions=True)
		created += 1

	frappe.db.commit()
	return created


def backfill_academic_curriculum():
	"""Create year/stage/subject offerings from existing assignments and assessments."""
	created = 0
	curriculum_keys = set()

	for doctype in ("EIMS Teacher Assignment", "EIMS Assessment"):
		for row in frappe.get_all(doctype, fields=["academic_year", "stage", "subject"]):
			if row.academic_year and row.stage and row.subject:
				curriculum_keys.add((row.academic_year, row.stage, row.subject))

	for academic_year, stage, subject in curriculum_keys:
		name = f"{academic_year}-{stage}-{subject}"
		if frappe.db.exists("EIMS Academic Curriculum", name):
			continue
		frappe.get_doc(
			{
				"doctype": "EIMS Academic Curriculum",
				"academic_year": academic_year,
				"stage": stage,
				"subject": subject,
			}
		).insert(ignore_permissions=True)
		created += 1

	frappe.db.commit()
	return created
