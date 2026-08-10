# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from frappe.model.document import Document


class EIMSAnnouncement(Document):
	def validate(self):
		self._require_audience()
		self._check_dates()

	def _require_audience(self):
		"""A targeted announcement with an empty target list would be invisible
		to everyone, which reads as 'published' but reaches nobody."""
		if self.audience == "حسب الدور" and not self.roles:
			frappe.throw("اختر دوراً واحداً على الأقل عند التوجيه حسب الدور.")
		if self.audience == "مستخدمون محددون" and not self.users:
			frappe.throw("اختر مستخدماً واحداً على الأقل عند التوجيه لمستخدمين محددين.")

	def _check_dates(self):
		if self.publish_from and self.publish_until and self.publish_until < self.publish_from:
			frappe.throw("تاريخ انتهاء النشر يجب أن يكون بعد تاريخ بدايته.")
