# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEIMSStudentPayment(FrappeTestCase):
	def test_receipt_renders(self):
		"""The A5 receipt is Arabic whatever language the printing session is in."""
		names = frappe.get_all("EIMS Student Payment", limit=1, pluck="name")
		if not names:
			self.skipTest("no payment recorded on this site")
		frappe.local.lang = "en"
		html = frappe.get_print(
			"EIMS Student Payment", names[0], print_format="EIMS Student Payment Receipt"
		)
		self.assertIn("إيصال قبض", html)
		self.assertIn("فقط", html)
