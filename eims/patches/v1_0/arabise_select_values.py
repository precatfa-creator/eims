"""Convert English select values to their Arabic equivalents.

The options themselves were Arabised so the desk reads Arabic without overriding
Frappe's own translations of generic words like "Sent" or "Second". Rows saved
before that change still hold the English value, which no longer matches the
field's options, so they are rewritten here.

Only values no Python or JS reads are converted; role, gender, stage category and
staff-assignment status stay English because the code compares against them.
"""

import frappe

VALUE_MAP = {
	("EIMS Official Correspondence", "direction"): {"Outgoing": "صادر", "Incoming": "وارد"},
	("EIMS Official Correspondence", "status"): {
		"Draft": "مسودة", "Sent": "صادرة", "Received": "واردة", "Closed": "مغلقة",
	},
	("EIMS Activity Consent", "decision"): {
		"Pending": "قيد الانتظار", "Approved": "موافق", "Rejected": "مرفوض",
	},
	("EIMS Guardian", "preferred_contact_method"): {
		"Phone": "هاتف", "Email": "بريد إلكتروني",
		"School Diary": "كراسة المتابعة", "Other": "أخرى",
	},
	("EIMS Daily Lesson", "period"): {
		"First": "الحصة الأولى", "Second": "الحصة الثانية", "Third": "الحصة الثالثة",
		"Fourth": "الحصة الرابعة", "Fifth": "الحصة الخامسة", "Sixth": "الحصة السادسة",
	},
}


def execute():
	for (doctype, fieldname), mapping in VALUE_MAP.items():
		if not frappe.db.table_exists(doctype):
			continue
		for old, new in mapping.items():
			frappe.db.set_value(
				doctype, {fieldname: old}, fieldname, new, update_modified=False
			)
	frappe.db.commit()
