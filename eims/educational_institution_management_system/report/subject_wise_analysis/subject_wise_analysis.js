frappe.query_reports["Subject Wise Analysis"] = {
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
		},
	],
};
