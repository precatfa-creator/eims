frappe.query_reports["Teacher Grade Summary"] = {
	filters: [
		{
			fieldname: "academic_year",
			label: __("Academic Year"),
			fieldtype: "Link",
			options: "EIMS Academic Year",
			reqd: 1,
		},
		{
			fieldname: "staff",
			label: __("Teacher"),
			fieldtype: "Link",
			options: "EIMS Staff",
			reqd: 1,
		},
	],
};
