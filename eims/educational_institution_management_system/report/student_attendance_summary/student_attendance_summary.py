# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe

PRESENT = "حاضر"
ABSENT = "غائب"
LATE = "متأخر"
EXCUSED = "مأذون"

# ponytail: attendance rate counts a late student as attending; مأذون is an
# authorised absence, so it stays out of the numerator but inside the denominator.
ATTENDED = (PRESENT, LATE)


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not (filters.academic_year and filters.from_date and filters.to_date):
		return [], []

	data = get_data(filters)
	return get_columns(), data, None, get_chart(data), get_report_summary(data)


def get_columns():
	return [
		{"fieldname": "student", "label": "الطالب", "fieldtype": "Link", "options": "EIMS Student", "width": 130},
		{"fieldname": "student_name", "label": "اسم الطالب", "fieldtype": "Data", "width": 220},
		{"fieldname": "enrollment_number", "label": "رقم القيد", "fieldtype": "Data", "width": 100},
		{"fieldname": "section", "label": "الشعبة", "fieldtype": "Link", "options": "EIMS Section", "width": 120},
		{"fieldname": "present", "label": "حاضر", "fieldtype": "Int", "width": 80},
		{"fieldname": "absent", "label": "غائب", "fieldtype": "Int", "width": 80},
		{"fieldname": "late", "label": "متأخر", "fieldtype": "Int", "width": 80},
		{"fieldname": "excused", "label": "مأذون", "fieldtype": "Int", "width": 80},
		{"fieldname": "not_recorded", "label": "غير مسجل", "fieldtype": "Int", "width": 90},
		{"fieldname": "recorded_days", "label": "الأيام المسجلة", "fieldtype": "Int", "width": 110},
		{"fieldname": "attendance_rate", "label": "نسبة الحضور", "fieldtype": "Percent", "width": 120},
	]


def get_roster(filters):
	"""Every enrolled student in scope, so zero-attendance students still appear."""
	enrollment_filters = {"academic_year": filters.academic_year, "status": "مسجل", "docstatus": ["<", 2]}
	for key in ("stage", "section"):
		if filters.get(key):
			enrollment_filters[key] = filters.get(key)

	roster = {}
	for enrollment in frappe.get_all(
		"EIMS Enrollment",
		filters=enrollment_filters,
		fields=["student", "section"],
		order_by="modified desc",
	):
		roster.setdefault(enrollment.student, enrollment)
	return list(roster.values())


def get_counts(filters):
	"""{student: {status: count}} over submitted sheets in the date range."""
	conditions = ["att.attendance_date between %(from_date)s and %(to_date)s"]
	params = {
		"academic_year": filters.academic_year,
		"from_date": filters.from_date,
		"to_date": filters.to_date,
	}
	for key in ("stage", "section"):
		if filters.get(key):
			conditions.append(f"att.{key} = %({key})s")
			params[key] = filters.get(key)

	rows = frappe.db.sql(
		"""
			select row.student, coalesce(row.status, '') as status, count(*) as count
			from `tabEIMS Student Attendance Row` row
			inner join `tabEIMS Student Attendance` att on att.name = row.parent
			where row.parenttype = 'EIMS Student Attendance'
				and att.docstatus = 1
				and att.academic_year = %(academic_year)s
				and {conditions}
			group by row.student, row.status
		""".format(conditions=" and ".join(conditions)),
		params,
		as_dict=True,
	)

	counts = {}
	for row in rows:
		counts.setdefault(row.student, {})[row.status] = row.count
	return counts


def get_data(filters):
	roster = get_roster(filters)
	if not roster:
		return []

	counts = get_counts(filters)
	students = {
		s.name: s
		for s in frappe.get_all(
			"EIMS Student",
			filters={"name": ["in", [e.student for e in roster]]},
			fields=["name", "student_name", "enrollment_number"],
		)
	}

	data = []
	for enrollment in roster:
		student = students.get(enrollment.student)
		if not student:
			continue

		tally = counts.get(enrollment.student, {})
		recorded = sum(count for status, count in tally.items() if status)
		attended = sum(tally.get(status, 0) for status in ATTENDED)

		data.append({
			"student": student.name,
			"student_name": student.student_name,
			"enrollment_number": student.enrollment_number,
			"section": enrollment.section,
			"present": tally.get(PRESENT, 0),
			"absent": tally.get(ABSENT, 0),
			"late": tally.get(LATE, 0),
			"excused": tally.get(EXCUSED, 0),
			"not_recorded": tally.get("", 0),
			"recorded_days": recorded,
			"attendance_rate": round(attended / recorded * 100, 1) if recorded else 0,
		})

	# Worst attendance first; students with nothing recorded yet sink to the bottom.
	data.sort(key=lambda row: (not row["recorded_days"], row["attendance_rate"], row["student_name"] or ""))
	return data


def get_chart(data):
	if not data:
		return None

	return {
		"data": {
			"labels": ["حاضر", "غائب", "متأخر", "مأذون"],
			"datasets": [{
				"name": "عدد السجلات",
				"values": [sum(row[key] for row in data) for key in ("present", "absent", "late", "excused")],
			}],
		},
		"type": "bar",
		"colors": ["#28a745"],
	}


def get_report_summary(data):
	if not data:
		return []

	recorded = sum(row["recorded_days"] for row in data)
	attended = sum(row["present"] + row["late"] for row in data)
	at_risk = sum(1 for row in data if row["recorded_days"] and row["attendance_rate"] < 75)

	return [
		{"label": "إجمالي الطلاب", "value": len(data), "datatype": "Int"},
		{
			"label": "نسبة الحضور العامة",
			"value": round(attended / recorded * 100, 1) if recorded else 0,
			"datatype": "Percent",
			"indicator": "Green" if recorded and attended / recorded >= 0.9 else "Orange",
		},
		{"label": "إجمالي الغياب", "value": sum(row["absent"] for row in data), "datatype": "Int"},
		{
			"label": "طلاب دون 75%",
			"value": at_risk,
			"datatype": "Int",
			"indicator": "Red" if at_risk else "Green",
		},
		{"label": "سجلات غير مكتملة", "value": sum(row["not_recorded"] for row in data), "datatype": "Int"},
	]
