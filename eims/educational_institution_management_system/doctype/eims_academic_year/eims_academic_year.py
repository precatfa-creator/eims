# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EIMSAcademicYear(Document):
	def validate(self):
		if self.start_date and self.end_date and self.start_date > self.end_date:
			frappe.throw(_("تاريخ البداية يجب ان يكون قبل تاريخ النهاية"))

	def on_update(self):
		# سنة نشطة واحدة فقط: عند تفعيل هذه السنة تُلغى البقية.
		if self.is_active:
			frappe.db.sql(
				"update `tabEIMS Academic Year` set is_active = 0 where name != %s and is_active = 1",
				self.name,
			)
