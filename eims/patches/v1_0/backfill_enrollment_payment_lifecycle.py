"""Move legacy one-row payment amounts into the payment transaction lifecycle."""

import frappe

from eims.educational_institution_management_system.doctype.eims_enrollment.eims_enrollment import (
	refresh_enrollment_payment_status,
)


def execute():
	for payment in frappe.get_all(
		"EIMS Student Payment", fields=["name", "student", "academic_year", "amount_paid", "docstatus"]
	):
		enrollment = frappe.db.get_value(
			"EIMS Enrollment",
			{"student": payment.student, "academic_year": payment.academic_year},
			"name",
		)
		if not enrollment:
			continue
		frappe.db.set_value("EIMS Student Payment", payment.name, "enrollment", enrollment, update_modified=False)
		if payment.amount_paid and payment.docstatus == 0:
			frappe.db.set_value("EIMS Student Payment", payment.name, "docstatus", 1, update_modified=False)

	for enrollment in frappe.get_all("EIMS Enrollment", fields=["name", "status", "enrollment_override_reason"]):
		if enrollment.status == "مسجل" and not enrollment.enrollment_override_reason:
			frappe.db.set_value(
				"EIMS Enrollment",
				enrollment.name,
				"enrollment_override_reason",
				"تم ترحيل حالة التسجيل من النظام السابق.",
				update_modified=False,
			)
		refresh_enrollment_payment_status(enrollment.name)
