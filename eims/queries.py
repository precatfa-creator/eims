"""Link-field queries for year-aware EIMS forms."""

import frappe


def _filters_dict(filters):
	if isinstance(filters, str):
		filters = frappe.parse_json(filters)
	return frappe._dict(filters or {})


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def student_query(doctype, txt, searchfield, start, page_len, filters):
	"""Return students enrolled in the requested academic context."""
	filters = _filters_dict(filters)
	conditions = ["student.docstatus < 2", "enrollment.docstatus < 2", "enrollment.status = 'مسجل'"]
	params = {"txt": f"%{txt}%", "start": start, "page_len": page_len}

	if filters.academic_year:
		conditions.append("enrollment.academic_year = %(academic_year)s")
		params["academic_year"] = filters.academic_year
	if filters.section:
		conditions.append("enrollment.section = %(section)s")
		params["section"] = filters.section
	if filters.stage:
		conditions.append("enrollment.stage = %(stage)s")
		params["stage"] = filters.stage
	if filters.subject:
		subject_stage = frappe.db.get_value("EIMS Subject", filters.subject, "stage")
		if not subject_stage or (filters.stage and filters.stage != subject_stage):
			return []
		if not filters.stage:
			conditions.append("enrollment.stage = %(subject_stage)s")
			params["subject_stage"] = subject_stage
		if not _is_active_subject(filters.academic_year, subject_stage, filters.subject):
			return []

	conditions.append("(student.name like %(txt)s or student.student_name like %(txt)s)")
	return frappe.db.sql(
		"""
			select distinct student.name, student.student_name
			from `tabEIMS Enrollment` enrollment
			inner join `tabEIMS Student` student on student.name = enrollment.student
			where {conditions}
			order by student.student_name, student.name
			limit %(page_len)s offset %(start)s
		""".format(conditions=" and ".join(conditions)),
		params,
	)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def subject_query(doctype, txt, searchfield, start, page_len, filters):
	"""Return subjects offered by the selected year and stage curriculum."""
	filters = _filters_dict(filters)
	conditions = ["subject.docstatus < 2", "(subject.name like %(txt)s or subject.subject_name like %(txt)s)"]
	params = {"txt": f"%{txt}%", "start": start, "page_len": page_len}
	join = ""

	if filters.stage:
		conditions.append("subject.stage = %(stage)s")
		params["stage"] = filters.stage

	if filters.academic_year and frappe.db.exists(
		"EIMS Academic Curriculum",
		{"academic_year": filters.academic_year, **({"stage": filters.stage} if filters.stage else {})},
	):
		join = "inner join `tabEIMS Academic Curriculum` curriculum on curriculum.subject = subject.name"
		conditions.extend(
			[
				"curriculum.docstatus < 2",
				"curriculum.academic_year = %(academic_year)s",
				"curriculum.is_active = 1",
			]
		)
		params["academic_year"] = filters.academic_year

	return frappe.db.sql(
		"""
			select distinct subject.name, subject.subject_name
			from `tabEIMS Subject` subject
			{join}
			where {conditions}
			order by subject.subject_name, subject.name
			limit %(page_len)s offset %(start)s
		""".format(join=join, conditions=" and ".join(conditions)),
		params,
	)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def staff_query(doctype, txt, searchfield, start, page_len, filters):
	"""Return staff assigned to a year when year assignments have been configured."""
	filters = _filters_dict(filters)
	params = {"txt": f"%{txt}%", "start": start, "page_len": page_len}
	conditions = ["staff.docstatus < 2", "(staff.name like %(txt)s or staff.name_ar like %(txt)s)"]
	join = ""

	if filters.academic_year and frappe.db.exists(
		"EIMS Staff Academic Assignment", {"academic_year": filters.academic_year}
	):
		join = (
			"inner join `tabEIMS Staff Academic Assignment` assignment "
			"on assignment.staff = staff.name and assignment.docstatus < 2"
		)
		conditions.extend(
			["assignment.academic_year = %(academic_year)s", "assignment.status = 'Active'"]
		)
		params["academic_year"] = filters.academic_year
		if filters.role:
			conditions.append("assignment.role = %(role)s")
			params["role"] = filters.role
	elif filters.role:
		conditions.append("staff.role = %(role)s")
		params["role"] = filters.role

	return frappe.db.sql(
		"""
			select distinct staff.name, staff.name_ar
			from `tabEIMS Staff` staff
			{join}
			where {conditions}
			order by staff.name_ar, staff.name
			limit %(page_len)s offset %(start)s
		""".format(join=join, conditions=" and ".join(conditions)),
		params,
	)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def teacher_query(doctype, txt, searchfield, start, page_len, filters):
	"""Return teachers assigned to the selected academic and class context."""
	filters = _filters_dict(filters)
	if not filters.academic_year or not filters.stage:
		return []

	params = {
		"txt": f"%{txt}%",
		"academic_year": filters.academic_year,
		"stage": filters.stage,
		"start": start,
		"page_len": page_len,
	}
	conditions = [
		"staff.docstatus < 2",
		"assignment.docstatus < 2",
		"staff.role = 'teacher'",
		"assignment.academic_year = %(academic_year)s",
		"assignment.stage = %(stage)s",
		"(staff.name like %(txt)s or staff.name_ar like %(txt)s)",
	]
	if filters.section:
		conditions.append("(assignment.section = %(section)s or assignment.section is null or assignment.section = '')")
		params["section"] = filters.section
	if filters.subject:
		conditions.append("(assignment.subject = %(subject)s or assignment.subject is null or assignment.subject = '')")
		params["subject"] = filters.subject

	return frappe.db.sql(
		"""
			select distinct staff.name, staff.name_ar
			from `tabEIMS Teacher Assignment` assignment
			inner join `tabEIMS Staff` staff on staff.name = assignment.staff
			where {conditions}
			order by staff.name_ar, staff.name
			limit %(page_len)s offset %(start)s
		""".format(conditions=" and ".join(conditions)),
		params,
	)


@frappe.whitelist()
def get_student_enrollment_context(student, academic_year):
	"""Expose a student's year-specific placement to the Result form."""
	if not student or not academic_year:
		return None
	return frappe.db.get_value(
		"EIMS Enrollment",
		{"student": student, "academic_year": academic_year, "status": "مسجل"},
		["stage", "section"],
		as_dict=True,
	)


def _is_active_subject(academic_year, stage, subject):
	"""Allow master subjects until a curriculum has been configured for the context."""
	if not academic_year or not stage:
		return True
	filters = {"academic_year": academic_year, "stage": stage}
	if not frappe.db.exists("EIMS Academic Curriculum", filters):
		return True
	return bool(frappe.db.exists("EIMS Academic Curriculum", {**filters, "subject": subject, "is_active": 1}))
