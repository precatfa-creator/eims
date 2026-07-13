from frappe import _


def get_data():
	return {
		"fieldname": "staff",
		"transactions": [
			{
				"label": _("Academic History"),
				"items": ["EIMS Staff Academic Assignment", "EIMS Teacher Assignment", "EIMS Timetable"],
			},
		],
	}
