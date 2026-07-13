# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe


def execute(filters=None):
	if not filters:
		return [], []

	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "subject", "label": "المادة", "fieldtype": "Link", "options": "EIMS Subject", "width": 150},
		{"fieldname": "subject_name", "label": "اسم المادة", "fieldtype": "Data", "width": 200},
		{"fieldname": "subject_type", "label": "النوع", "fieldtype": "Data", "width": 80},
		{"fieldname": "term", "label": "الفصل", "fieldtype": "Data", "width": 120},
		{"fieldname": "enrolled", "label": "عدد الطلاب", "fieldtype": "Int", "width": 100},
		{"fieldname": "graded", "label": "تم رصد الدرجات", "fieldtype": "Int", "width": 120},
		{"fieldname": "avg_score", "label": "متوسط الدرجات", "fieldtype": "Float", "width": 100},
		{"fieldname": "max_score", "label": "أعلى درجة", "fieldtype": "Float", "width": 100},
		{"fieldname": "min_score", "label": "أدنى درجة", "fieldtype": "Float", "width": 100},
		{"fieldname": "status", "label": "حالة التقييم", "fieldtype": "Data", "width": 100},
	]


def get_data(filters):
	staff = filters.get("staff")

	assignments = frappe.get_all(
		"EIMS Teacher Assignment",
		filters={"staff": staff, "academic_year": filters.get("academic_year")},
		fields=["subject"],
	)

	data = []
	for assignment in assignments:
		assessments = frappe.get_all(
			"EIMS Assessment",
			filters={
				"subject": assignment.subject,
				"academic_year": filters.get("academic_year"),
			},
			fields=["name", "term", "docstatus", "students"],
		)

		for assessment in assessments:
			ass_doc = frappe.get_doc("EIMS Assessment", assessment.name)
			total_scores = []
			graded = 0
			for ge in ass_doc.students:
				if ge.total_score:
					total_scores.append(ge.total_score)
					graded += 1

			data.append({
				"subject": assignment.subject,
				"subject_name": frappe.db.get_value("EIMS Subject", assignment.subject, "subject_name"),
				"subject_type": frappe.db.get_value("EIMS Subject", assignment.subject, "subject_type"),
				"term": assessment.term,
				"enrolled": len(ass_doc.students),
				"graded": graded,
				"avg_score": round(sum(total_scores) / len(total_scores), 1) if total_scores else 0,
				"max_score": max(total_scores) if total_scores else 0,
				"min_score": min(total_scores) if total_scores else 0,
				"status": "Submitted" if ass_doc.docstatus == 1 else "Draft",
			})

	return data
