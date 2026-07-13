# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from frappe.model.document import Document

from eims.educational_institution_management_system.doctype.eims_enrollment.eims_enrollment import (
	refresh_enrollment_payment_status,
)


class EIMSStageFee(Document):
	def on_update(self):
		for enrollment in frappe.get_all(
			"EIMS Enrollment",
			filters={"stage": self.stage, "academic_year": self.academic_year},
			pluck="name",
		):
			refresh_enrollment_payment_status(enrollment)
