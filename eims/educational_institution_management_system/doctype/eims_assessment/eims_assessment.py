# Copyright (c) 2026, Catfa and Contributors
# See license.txt

from frappe.model.document import Document


class EIMSAssessment(Document):
	def validate(self):
		# Components are optional. If a teacher enters أعمال السنة / الامتحان,
		# total_score is their sum; otherwise the directly-typed total_score stands.
		for row in self.students:
			if row.coursework or row.exam:
				row.total_score = (row.coursework or 0) + (row.exam or 0)
