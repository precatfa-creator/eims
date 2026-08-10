# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

UNPAID = "غير مدفوع"
PARTIALLY_PAID = "مدفوع جزئياً"
FULLY_PAID = "مدفوع بالكامل"


def payment_split(total_fee, paid):
	"""Outstanding balance and payment status for a fee/paid pair.

	Partial payments are simply "paid so far is less than the fee"; every extra
	instalment moves the pair without any separate schedule to keep in step.
	"""
	outstanding = max(flt(total_fee) - flt(paid), 0)
	if not flt(paid):
		return outstanding, UNPAID
	return outstanding, PARTIALLY_PAID if outstanding else FULLY_PAID


class EIMSEnrollment(Document):
	def validate(self):
		self.update_payment_summary()
		if self.status == "مسجل" and self.outstanding_amount > 0 and not self.enrollment_override_reason:
			frappe.throw(
				_("A reason is required to enroll a student before all fees have been paid.")
			)

	def update_payment_summary(self):
		"""Calculate the payment state from submitted payment transactions only."""
		self.total_fee = frappe.db.get_value(
			"EIMS Stage Fee",
			{"stage": self.stage, "academic_year": self.academic_year},
			"amount",
		) or 0
		self.paid_amount, self.last_payment_date = frappe.db.sql(
			"""
				select coalesce(sum(amount_paid), 0), max(payment_date)
				from `tabEIMS Student Payment`
				where enrollment = %s and docstatus = 1
			""",
			self.name or "",
		)[0]
		self.outstanding_amount, self.payment_status = payment_split(self.total_fee, self.paid_amount)
		if self.payment_status == FULLY_PAID:
			self.status = "مسجل"
			self.enrollment_override_reason = None


def refresh_enrollment_payment_status(enrollment_name):
	"""Refresh a saved enrolment after a payment is submitted or cancelled."""
	if not enrollment_name or not frappe.db.exists("EIMS Enrollment", enrollment_name):
		return
	enrollment = frappe.get_doc("EIMS Enrollment", enrollment_name)
	enrollment.update_payment_summary()
	# A status without an override reason can only have been granted by full payment.
	# If a payment is cancelled or the fee changes, return it to draft instead of
	# silently keeping an unpaid student enrolled.
	if (
		enrollment.status == "مسجل"
		and enrollment.payment_status != FULLY_PAID
		and not enrollment.enrollment_override_reason
	):
		enrollment.status = "مسودة"
	enrollment.save(ignore_permissions=True)
