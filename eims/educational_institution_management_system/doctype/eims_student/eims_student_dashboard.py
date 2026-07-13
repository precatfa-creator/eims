from frappe import _


def get_data():
	return {
		"fieldname": "student",
		"transactions": [
			{"label": _("Academic History"), "items": ["EIMS Enrollment", "EIMS Result"]},
			{
				"label": _("Student Records"),
				"items": [
					"EIMS Student Payment",
					"EIMS Disciplinary Action",
					"EIMS Request",
				],
			},
		],
	}
