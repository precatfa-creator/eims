# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe


def execute(filters=None):
	if not filters:
		return [], []

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_report_summary(data)

	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{
			"fieldname": "student_name",
			"label": "اسم الطالب",
			"fieldtype": "Link",
			"options": "EIMS Student",
			"width": 250,
		},
		{
			"fieldname": "enrollment_number",
			"label": "رقم القيد",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"fieldname": "total_score",
			"label": "المجموع الكلي",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"fieldname": "status",
			"label": "النتيجة",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"fieldname": "rank",
			"label": "الترتيب",
			"fieldtype": "Int",
			"width": 80,
		},
	]


def get_data(filters):
	enrollment_filters = {
		"academic_year": filters.get("academic_year"),
		"stage": filters.get("stage"),
		"status": "مسجل",
	}
	if filters.get("section"):
		enrollment_filters["section"] = filters.get("section")

	enrollments = frappe.get_all(
		"EIMS Enrollment",
		filters=enrollment_filters,
		fields=["student"],
		order_by="student",
	)

	data = []
	for enr in enrollments:
		results = frappe.get_all(
			"EIMS Result",
			filters={"student": enr.student, "academic_year": filters.get("academic_year")},
			fields=["pass_percentage", "status", "overall_rank"],
			limit=1,
		)

		result = results[0] if results else None
		assessment_total = 0

		if not result:
			# Calculate from assessments
			assessments = frappe.get_all(
				"EIMS Assessment",
				filters={
					"academic_year": filters.get("academic_year"),
					"stage": filters.get("stage"),
				},
				pluck="name",
			)

			for a_name in assessments:
				a = frappe.get_doc("EIMS Assessment", a_name)
				for ge in a.students:
					if ge.student == enr.student:
						assessment_total += ge.total_score or 0

		data.append({
			"student": enr.student,
			"student_name": frappe.db.get_value("EIMS Student", enr.student, "student_name"),
			"enrollment_number": frappe.db.get_value("EIMS Student", enr.student, "enrollment_number"),
			"total_score": result.pass_percentage if result else assessment_total,
			"status": result.status if result else "--",
			"rank": result.overall_rank if result else None,
		})

	# Sort and assign rank
	data.sort(key=lambda x: x.get("total_score", 0), reverse=True)
	for i, row in enumerate(data, 1):
		row["rank"] = i

	return data


def get_chart(data):
	if not data or len(data) < 2:
		return None
	top_n = data[:10]
	return {
		"data": {
			"labels": [d["student_name"] for d in top_n],
			"datasets": [{"name": "المجموع", "values": [d["total_score"] for d in top_n]}],
		},
		"type": "bar",
	}


def get_report_summary(data):
	if not data:
		return []

	total = len(data)
	passed = sum(1 for d in data if (d.get("status") or "").startswith("ناجح"))
	avg = round(sum(d.get("total_score", 0) for d in data) / total, 1) if total else 0
	max_score = max((d.get("total_score", 0) for d in data), default=0)
	min_score = min((d.get("total_score", 0) for d in data), default=0)

	return [
		{"label": "إجمالي الطلاب", "value": total, "datatype": "Int"},
		{"label": "ناجحون", "value": passed, "datatype": "Int"},
		{"label": "المعدل", "value": avg, "datatype": "Float"},
		{"label": "أعلى درجة", "value": max_score, "datatype": "Float"},
		{"label": "أدنى درجة", "value": min_score, "datatype": "Float"},
	]
