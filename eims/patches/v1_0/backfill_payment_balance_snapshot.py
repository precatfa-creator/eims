"""Fill the balance snapshot on receipts recorded before those fields existed.

Old receipts print zeros for fee/previous/remaining, which makes a part-paid history
unreadable. Replay each enrollment's receipts in order and store what each one left owing.
"""

import frappe
from frappe.utils import flt

from eims.educational_institution_management_system.doctype.eims_enrollment.eims_enrollment import (
	payment_split,
	refresh_enrollment_payment_status,
)


def execute():
	# Receipts recorded before payment_date existed, and the payment method the new column
	# default invented for them — neither should be guessed on a printed receipt.
	frappe.db.sql(
		"update `tabEIMS Student Payment` set payment_date = date(creation) where payment_date is null"
	)
	# Every receipt that exists when this patch runs predates the field, so none of them
	# actually recorded a method.
	frappe.db.sql("update `tabEIMS Student Payment` set payment_method = null")

	fees = {
		(f.stage, f.academic_year): flt(f.amount)
		for f in frappe.get_all("EIMS Stage Fee", fields=["stage", "academic_year", "amount"])
	}
	stages = {
		e.name: (e.stage, e.academic_year)
		for e in frappe.get_all("EIMS Enrollment", fields=["name", "stage", "academic_year"])
	}

	payments = frappe.get_all(
		"EIMS Student Payment",
		filters={"docstatus": 1},
		fields=["name", "enrollment", "amount_paid"],
		order_by="enrollment asc, payment_date asc, creation asc",
	)

	running = {}
	for p in payments:
		if not p.enrollment:
			continue
		total_fee = fees.get(stages.get(p.enrollment), 0)
		previously_paid, count = running.get(p.enrollment, (0.0, 0))
		balance_after, _status = payment_split(total_fee, previously_paid + flt(p.amount_paid))
		frappe.db.set_value(
			"EIMS Student Payment",
			p.name,
			{
				"total_fee": total_fee,
				"previously_paid": previously_paid,
				"balance_after": balance_after,
				"installment_no": count + 1,
			},
			update_modified=False,
		)
		running[p.enrollment] = (previously_paid + flt(p.amount_paid), count + 1)

	# Fill the payment history tab on enrollments saved before the table existed.
	for enrollment in frappe.get_all("EIMS Enrollment", pluck="name"):
		refresh_enrollment_payment_status(enrollment)
