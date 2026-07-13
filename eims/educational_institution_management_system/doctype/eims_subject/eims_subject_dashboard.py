from frappe import _


def get_data():
	return {
		"fieldname": "subject",
		"transactions": [
			{
				"label": _("Academic History"),
				"items": ["EIMS Academic Curriculum", "EIMS Teacher Assignment", "EIMS Assessment"],
			}
		],
	}
