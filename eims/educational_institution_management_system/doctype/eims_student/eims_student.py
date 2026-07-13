# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EIMSStudent(Document):
	def before_save(self):
		if self.enrollment_number and not self.name:
			self.name = self.enrollment_number
		self._previous_guardian = self.get_db_value("guardian") if not self.is_new() else None

	def on_update(self):
		"""Keep the guardian's child table as the reverse link for this student."""
		if self._previous_guardian and self._previous_guardian != self.guardian:
			previous = frappe.get_doc("EIMS Guardian", self._previous_guardian)
			previous.students = [row for row in previous.students if row.student != self.name]
			previous.save(ignore_permissions=True)
		if not self.guardian:
			return
		guardian = frappe.get_doc("EIMS Guardian", self.guardian)
		if not any(row.student == self.name for row in guardian.students):
			guardian.append("students", {"student": self.name})
			guardian.save(ignore_permissions=True)
