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
		{"fieldname": "subject", "label": "المادة", "fieldtype": "Link", "options": "EIMS Subject", "width": 150},
		{"fieldname": "subject_name", "label": "اسم المادة", "fieldtype": "Data", "width": 200},
		{"fieldname": "subject_type", "label": "النوع", "fieldtype": "Data", "width": 80},
		{"fieldname": "total_students", "label": "إجمالي الطلاب", "fieldtype": "Int", "width": 100},
		{"fieldname": "passed", "label": "ناجحون", "fieldtype": "Int", "width": 80},
		{"fieldname": "failed", "label": "راسبون", "fieldtype": "Int", "width": 80},
		{"fieldname": "pass_rate", "label": "نسبة النجاح", "fieldtype": "Percent", "width": 100},
		{"fieldname": "avg_score", "label": "المتوسط", "fieldtype": "Float", "width": 100},
		{"fieldname": "max_score", "label": "أعلى", "fieldtype": "Float", "width": 80},
		{"fieldname": "min_score", "label": "أدنى", "fieldtype": "Float", "width": 80},
	]


def get_data(filters):
	subjects_filter = {}
	if filters.get("stage"):
		subjects_filter["stage"] = filters.get("stage")

	subjects = frappe.get_all("EIMS Subject", filters=subjects_filter, fields=["name", "subject_name", "subject_type"])

	data = []
	for subj in subjects:
		assessments = frappe.get_all(
			"EIMS Assessment",
			filters={"subject": subj.name, "academic_year": filters.get("academic_year"), "docstatus": 1},
			pluck="name",
		)

		all_scores = []
		for a_name in assessments:
			a = frappe.get_doc("EIMS Assessment", a_name)
			for ge in a.students:
				if ge.total_score:
					all_scores.append(ge.total_score)

		if not all_scores:
			continue

		passed = sum(1 for s in all_scores if s >= 40)
		failed = len(all_scores) - passed
		data.append({
			"subject": subj.name,
			"subject_name": subj.subject_name,
			"subject_type": subj.subject_type,
			"total_students": len(all_scores),
			"passed": passed,
			"failed": failed,
			"pass_rate": round(passed / len(all_scores) * 100, 1) if all_scores else 0,
			"avg_score": round(sum(all_scores) / len(all_scores), 1),
			"max_score": max(all_scores),
			"min_score": min(all_scores),
		})

	return data


def get_chart(data):
	if not data:
		return None
	return {
		"data": {
			"labels": [d["subject_name"] for d in data],
			"datasets": [{"name": "نسبة النجاح %", "values": [d["pass_rate"] for d in data]}],
		},
		"type": "percentage",
	}


def get_report_summary(data):
	if not data:
		return []

	overall_pass_rate = round(
		sum(d["passed"] for d in data) / sum(d["total_students"] for d in data) * 100, 1
	) if data else 0

	return [
		{"label": "إجمالي المواد", "value": len(data), "datatype": "Int"},
		{"label": "نسبة النجاح الكلية", "value": overall_pass_rate, "datatype": "Percent"},
	]
