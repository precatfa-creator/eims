import frappe
from frappe.model.document import Document


class EIMSActivityConsent(Document):
	def validate(self):
		if self.student and not self.guardian:
			self.guardian = frappe.db.get_value("EIMS Student", self.student, "guardian")
