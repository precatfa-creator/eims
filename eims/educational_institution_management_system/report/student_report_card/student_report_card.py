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
			"fieldname": "subject",
			"label": "المادة",
			"fieldtype": "Link",
			"options": "EIMS Subject",
			"width": 150,
		},
		{
			"fieldname": "subject_name",
			"label": "اسم المادة",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"fieldname": "subject_type",
			"label": "النوع",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"fieldname": "term_1_total",
			"label": "الفصل الأول",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "term_2_total",
			"label": "الفصل الثاني",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "yearly_total",
			"label": "المجموع الكلي",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "make_up_exam",
			"label": "الدور الثاني",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "final_total",
			"label": "المجموع النهائي",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "status",
			"label": "النتيجة",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"fieldname": "grade",
			"label": "التقدير",
			"fieldtype": "Data",
			"width": 100,
		},
	]


def get_data(filters):
	# Get result for this student
	results = frappe.get_all(
		"EIMS Result",
		filters={
			"student": filters.get("student"),
			"academic_year": filters.get("academic_year"),
		},
		pluck="name",
	)

	if not results:
		# No published result yet - show from assessments
		return get_data_from_assessments(filters)

	result_doc = frappe.get_doc("EIMS Result", results[0])
	data = []
	for entry in result_doc.get("results", []):
		if filters.get("stage") and entry.subject:
			subj_stage = frappe.db.get_value("EIMS Subject", entry.subject, "stage")
			if subj_stage != filters.get("stage"):
				continue

		data.append({
			"subject": entry.subject,
			"subject_name": entry.subject_name,
			"subject_type": entry.subject_type,
			"term_1_total": entry.term_1_total,
			"term_2_total": entry.term_2_total,
			"yearly_total": entry.yearly_total,
			"make_up_exam": entry.make_up_exam,
			"final_total": entry.final_total,
			"status": entry.status,
			"grade": entry.grade,
		})

	return data


def get_data_from_assessments(filters):
	"""Generate data from raw assessments when no result exists."""
	subjects = frappe.get_all(
		"EIMS Subject",
		filters={"stage": filters.get("stage")},
		fields=["name", "subject_name", "subject_type"],
	)

	data = []
	for subj in subjects:
		assessments = frappe.get_all(
			"EIMS Assessment",
			filters={
				"subject": subj.name,
				"academic_year": filters.get("academic_year"),
			},
			fields=["name", "term"],
		)

		term_1_total = 0
		term_2_total = 0
		for a in assessments:
			assessment = frappe.get_doc("EIMS Assessment", a.name)
			for ge in assessment.students:
				if ge.student == filters.get("student"):
					if a.term == "الفصل الدراسي الأول":
						term_1_total = ge.total_score or 0
					else:
						term_2_total = ge.total_score or 0

		yearly_total = term_1_total + term_2_total
		grade_label = _get_grade_label(yearly_total)

		data.append({
			"subject": subj.name,
			"subject_name": subj.subject_name,
			"subject_type": subj.subject_type,
			"term_1_total": term_1_total,
			"term_2_total": term_2_total,
			"yearly_total": yearly_total,
			"status": "ناجح" if yearly_total >= 40 else "راسب",
			"grade": grade_label,
		})

	return data


def _get_grade_label(score):
	if score >= 90:
		return "ممتاز"
	elif score >= 80:
		return "جيد جدا"
	elif score >= 70:
		return "جيد"
	elif score >= 60:
		return "مقبول"
	else:
		return "راسب"


def get_chart(data):
	if not data:
		return None

	datasets = [{"name": "الدرجة", "values": [d.get("yearly_total", 0) for d in data]}]
	labels = [d.get("subject_name", "") for d in data]

	return {
		"data": {
			"labels": labels,
			"datasets": datasets,
		},
		"type": "bar",
		"colors": ["#428bfc"],
	}


def get_report_summary(data):
	if not data:
		return []

	total_subjects = len(data)
	passed = sum(1 for d in data if d.get("status") == "ناجح")
	failed = total_subjects - passed
	avg_score = round(sum(d.get("yearly_total", 0) for d in data) / total_subjects, 1) if total_subjects else 0

	return [
		{"label": "إجمالي المواد", "value": total_subjects, "datatype": "Data"},
		{"label": "مواد ناجحة", "value": passed, "datatype": "Data"},
		{"label": "مواد راسبة", "value": failed, "datatype": "Data"},
		{"label": "المعدل", "value": avg_score, "datatype": "Float"},
	]
