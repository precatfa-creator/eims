# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from eims.educational_institution_management_system.doctype.eims_enrollment.eims_enrollment import (
	refresh_enrollment_payment_status,
)


class EIMSStudentPayment(Document):
	def validate(self):
		if not self.enrollment:
			frappe.throw(_("Select the Enrollment this payment is for."))
		enrollment = frappe.get_doc("EIMS Enrollment", self.enrollment)
		if enrollment.status in {"منسحب", "منقول", "متخرج"}:
			frappe.throw(_("Payments can only be recorded for a draft or enrolled student."))
		self.student = enrollment.student
		self.academic_year = enrollment.academic_year
		if not self.amount_paid or self.amount_paid <= 0:
			frappe.throw(_("Payment amount must be greater than zero."))

	def on_submit(self):
		refresh_enrollment_payment_status(self.enrollment)

	def on_cancel(self):
		refresh_enrollment_payment_status(self.enrollment)
