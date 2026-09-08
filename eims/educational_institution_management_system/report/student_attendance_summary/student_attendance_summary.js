frappe.query_reports["Student Attendance Summary"] = {
	filters: [
		{
			fieldname: "academic_year",
			label: __("Academic Year"),
			fieldtype: "Link",
			options: "EIMS Academic Year",
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "stage",
			label: __("Stage"),
			fieldtype: "Link",
			options: "EIMS Stage",
		},
		{
			fieldname: "section",
			label: __("Section"),
			fieldtype: "Link",
			options: "EIMS Section",
			get_query() {
				const stage = frappe.query_report.get_filter_value("stage");
				return stage ? { filters: { stage } } : {};
			},
		},
	],

	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname === "attendance_rate" && data?.recorded_days) {
			const colour = data.attendance_rate >= 90 ? "#28a745" : data.attendance_rate >= 75 ? "#e58a2e" : "#e24c4c";
			value = `<span style="color: ${colour}; font-weight: 600">${value}</span>`;
		}
		if (column.fieldname === "absent" && data?.absent > 0) {
			value = `<span style="color: #e24c4c">${value}</span>`;
		}
		if (column.fieldname === "not_recorded" && data?.not_recorded > 0) {
			value = `<span style="color: #e58a2e">${value}</span>`;
		}
		return value;
	},
};
