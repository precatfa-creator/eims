# Copyright (c) 2026, Catfa and Contributors
# See license.txt
#
# A fee is settled by one or many receipts. Each receipt stores the balance it was
# taken with, so a student can pay part now and the rest weeks later and every
# printed receipt still shows what was owed on its own day.

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, fmt_money

from eims.educational_institution_management_system.doctype.eims_enrollment.eims_enrollment import (
	payment_split,
	refresh_enrollment_payment_status,
)

CLOSED_ENROLLMENT_STATUSES = {"منسحب", "منقول", "متخرج"}


class EIMSStudentPayment(Document):
	def validate(self):
		if not self.enrollment:
			frappe.throw(_("Select the Enrollment this payment is for."))
		enrollment = frappe.get_doc("EIMS Enrollment", self.enrollment)
		if enrollment.status in CLOSED_ENROLLMENT_STATUSES:
			frappe.throw(_("Payments can only be recorded for a draft or enrolled student."))
		self.student = enrollment.student
		self.academic_year = enrollment.academic_year
		if flt(self.amount_paid) <= 0:
			frappe.throw(_("Payment amount must be greater than zero."))
		self.set_balance_snapshot()

	def set_balance_snapshot(self):
		"""Freeze the fee, the amount paid so far and the balance this receipt leaves."""
		balance = enrollment_balance(self.enrollment, exclude=self.name)
		self.total_fee = balance["total_fee"]
		self.previously_paid = balance["previously_paid"]
		# A missing stage fee means the fee was never set, so nothing can be "too much" yet.
		if self.total_fee and flt(self.amount_paid) > balance["outstanding"]:
			frappe.throw(
				_(
					"Amount is more than the outstanding balance of {0}. Correct the amount or update the stage fee."
				).format(money(balance["outstanding"]))
			)
		self.balance_after = max(balance["outstanding"] - flt(self.amount_paid), 0)
		self.installment_no = balance["paid_count"] + 1
		self.payment_summary = self.build_summary()

	def build_summary(self):
		if not self.total_fee:
			return _("Instalment {0}: {1} paid. Stage fee is not set for this year.").format(
				self.installment_no, money(self.amount_paid)
			)
		if self.balance_after:
			return _("Instalment {0}: {1} of {2}. Remaining {3}.").format(
				self.installment_no,
				money(self.amount_paid),
				money(self.total_fee),
				money(self.balance_after),
			)
		return _("Instalment {0}: {1}. Fees fully paid.").format(
			self.installment_no, money(self.amount_paid)
		)

	def amount_in_words(self):
		"""The paid amount spelled out in Arabic, the way it is written on the paper receipt."""
		from num2words import num2words

		# ponytail: Libyan dinar, 1000 dirhams. Read Currency.fraction_units if a second
		# currency ever shows up.
		amount = flt(self.amount_paid)
		dinars = int(amount)
		dirhams = round((amount - dinars) * 1000)
		words = f"{num2words(dinars, lang='ar')} دينار"
		if dirhams:
			words += f" و {num2words(dirhams, lang='ar')} درهم"
		return f"{words} فقط"

	def on_submit(self):
		refresh_enrollment_payment_status(self.enrollment)

	def on_cancel(self):
		refresh_enrollment_payment_status(self.enrollment)


def money(amount):
	# The global "currency" default belongs to whatever else shares this site; the school's
	# currency is the one in System Settings.
	return fmt_money(flt(amount), currency=frappe.db.get_single_value("System Settings", "currency"))


@frappe.whitelist()
def enrollment_balance(enrollment, exclude=None):
	"""Fee, collected so far and what is still owed, ignoring the receipt being edited."""
	frappe.has_permission("EIMS Enrollment", doc=enrollment, throw=True)
	stage, academic_year = frappe.db.get_value(
		"EIMS Enrollment", enrollment, ["stage", "academic_year"]
	)
	total_fee = flt(
		frappe.db.get_value(
			"EIMS Stage Fee", {"stage": stage, "academic_year": academic_year}, "amount"
		)
	)
	previously_paid, paid_count = frappe.db.sql(
		"""
			select coalesce(sum(amount_paid), 0), count(*)
			from `tabEIMS Student Payment`
			where enrollment = %s and docstatus = 1 and name != %s
		""",
		(enrollment, exclude or ""),
	)[0]
	outstanding, status = payment_split(total_fee, previously_paid)
	return {
		"total_fee": total_fee,
		"previously_paid": flt(previously_paid),
		"outstanding": outstanding,
		"payment_status": status,
		"paid_count": paid_count,
	}
