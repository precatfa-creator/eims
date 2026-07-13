import frappe
from frappe import _
from frappe.model.document import Document


class EIMSStaffAcademicAssignment(Document):
	def validate(self):
		if self.start_date and self.end_date and self.start_date > self.end_date:
			frappe.throw(_("Assignment start date must be before the end date."))
