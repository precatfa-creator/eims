frappe.query_reports["Class Performance Report"] = {
	filters: [
		{
			fieldname: "academic_year",
			label: __("Academic Year"),
			fieldtype: "Link",
			options: "EIMS Academic Year",
			reqd: 1,
		},
		{
			fieldname: "stage",
			label: __("Stage"),
			fieldtype: "Link",
			options: "EIMS Stage",
			reqd: 1,
		},
		{
			fieldname: "section",
			label: __("Section"),
			fieldtype: "Link",
			options: "EIMS Section",
		},
		{
			fieldname: "term",
			label: __("Term"),
			fieldtype: "Select",
			options: "\nالفصل الدراسي الأول\nالفصل الدراسي الثاني",
		},
	],
};
