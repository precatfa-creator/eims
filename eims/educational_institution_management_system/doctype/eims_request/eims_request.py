# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EIMSRequest(Document):
	ROLE_DOCTYPE = {"طالب": "EIMS Student", "ولي أمر": "EIMS Guardian", "معلم": "EIMS Staff"}

	def validate(self):
		expected_doctype = self.ROLE_DOCTYPE.get(self.raised_by_role)
		if not expected_doctype:
			frappe.throw(_("Select whether the request was raised by a student, guardian, or teacher."))
		if self.raised_by_doctype != expected_doctype:
			self.raised_by_doctype = expected_doctype
		if not self.raised_by or not frappe.db.exists(expected_doctype, self.raised_by):
			frappe.throw(_("Select a valid requester for the selected role."))

		self.raised_by_user = frappe.db.get_value(expected_doctype, self.raised_by, "user_id")
		if expected_doctype == "EIMS Student":
			self.student = self.raised_by
		elif expected_doctype == "EIMS Guardian":
			self.student = frappe.db.get_value(
				"EIMS Guardian Student", {"parent": self.raised_by}, "student"
			)
		if self.student:
			from eims.academic_year import _validate_student_enrollment

			_validate_student_enrollment(self.student, self.academic_year)
