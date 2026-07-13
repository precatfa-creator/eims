frappe.query_reports["Student Report Card"] = {
	filters: [
		{
			fieldname: "academic_year",
			label: __("Academic Year"),
			fieldtype: "Link",
			options: "EIMS Academic Year",
			reqd: 1,
		},
		{
			fieldname: "student",
			label: __("Student"),
			fieldtype: "Link",
			options: "EIMS Student",
			reqd: 1,
		},
		{
			fieldname: "stage",
			label: __("Stage"),
			fieldtype: "Link",
			options: "EIMS Stage",
		},
	],
};
