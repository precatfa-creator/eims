# Copyright (c) 2026, Catfa and Contributors
# See license.txt

from frappe.model.document import Document

# ponytail: arithmetic only. The ministry pass/promotion policy (per-subject min,
# carry-over مرحّل, دور ثاني eligibility) is NOT auto-applied — status, grade and
# overall_grade stay manual until the school confirms thresholds. Encode it in
# compute_status() then and call it from validate().


def subject_finals(row):
	"""Return (yearly_total, final_total) for one result-subject row.

	yearly_total = term 1 + term 2. final_total uses the make-up (الدور الثاني)
	mark when one was sat, otherwise the yearly total.
	"""
	yearly_total = (row.get("term_1_total") or 0) + (row.get("term_2_total") or 0)
	make_up = row.get("make_up_exam") or 0
	final_total = make_up if make_up else yearly_total
	return yearly_total, final_total


def card_totals(rows):
	"""Return (grand_total, max_total, pass_percentage) across result-subject rows."""
	grand_total = sum(subject_finals(r)[1] for r in rows)
	max_total = sum(float(r.get("max_mark") or 0) for r in rows)
	pass_percentage = (grand_total / max_total * 100) if max_total else 0
	return grand_total, max_total, pass_percentage


class EIMSResult(Document):
	def validate(self):
		for row in self.results:
			row.yearly_total, row.final_total = subject_finals(row)
		self.grand_total, self.max_total, self.pass_percentage = card_totals(self.results)
