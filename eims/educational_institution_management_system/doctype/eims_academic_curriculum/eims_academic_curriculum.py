import frappe
from frappe import _
from frappe.model.document import Document


class EIMSAcademicCurriculum(Document):
	def validate(self):
		if self.start_date and self.end_date and self.start_date > self.end_date:
			frappe.throw(_("Curriculum start date must be before the end date."))

		if self.subject and self.stage:
			subject_stage = frappe.db.get_value("EIMS Subject", self.subject, "stage")
			if subject_stage and subject_stage != self.stage:
				frappe.throw(_("The selected subject does not belong to this stage."))
