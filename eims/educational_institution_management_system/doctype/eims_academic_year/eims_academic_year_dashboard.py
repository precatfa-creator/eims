from frappe import _


def get_data():
	return {
		"fieldname": "academic_year",
		"transactions": [
			{
				"label": _("Academic Structure"),
				"items": ["EIMS Academic Curriculum", "EIMS Teacher Assignment", "EIMS Timetable"],
			},
			{
				"label": _("People and Enrollment"),
				"items": ["EIMS Enrollment", "EIMS Staff Academic Assignment", "EIMS Staff Attendance"],
			},
			{
				"label": _("Student Operations"),
				"items": [
					"EIMS Assessment",
					"EIMS Result",
					"EIMS Student Attendance",
					"EIMS Student Payment",
					"EIMS Disciplinary Action",
				],
			},
			{
				"label": _("School Operations"),
				"items": ["EIMS Daily Accomplishment", "EIMS School Activity", "EIMS Request", "EIMS Stage Fee"],
			},
		],
	}
