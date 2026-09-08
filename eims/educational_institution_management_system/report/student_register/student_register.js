frappe.query_reports["Student Register"] = {
	filters: [
		{ fieldname: "academic_year", label: __("Academic Year"), fieldtype: "Link", options: "EIMS Academic Year", reqd: 1 },
		{ fieldname: "view", label: __("View"), fieldtype: "Select", options: ["Directory", "Contacts", "Fees", "Roster", "Full Details"], default: "Directory" },
		{ fieldname: "student", label: __("Student"), fieldtype: "Link", options: "EIMS Student" },
		{ fieldname: "stage", label: __("Stage"), fieldtype: "Link", options: "EIMS Stage",
			on_change(report) { report.set_filter_value("section", ""); report.refresh(); } },
		{ fieldname: "section", label: __("Section"), fieldtype: "Link", options: "EIMS Section",
			get_query() {
				const filters = {};
				for (const key of ["stage"]) {
					const value = frappe.query_report.get_filter_value(key);
					if (value) filters[key] = value;
				}
				return { filters };
			} },
		{ fieldname: "gender", label: __("Gender"), fieldtype: "Select", options: ["", "male", "female"] },
		{ fieldname: "nationality", label: __("Nationality"), fieldtype: "Link", options: "EIMS Nationality" },
		{ fieldname: "status", label: __("Status"), fieldtype: "Select", options: ["", "مسودة", "مسجل", "منسحب", "منقول", "متخرج"] },
		{ fieldname: "payment_status", label: __("Payment Status"), fieldtype: "Select", options: ["", "غير مدفوع", "مدفوع جزئياً", "مدفوع بالكامل"] },
		{ fieldname: "from_date", label: __("Enrollment Date From"), fieldtype: "Date" },
		{ fieldname: "to_date", label: __("Enrollment Date To"), fieldtype: "Date" },
	],

	onload(report) {
		// Preserve the branded header/footer when users pick print columns.
		const get_custom_format = report.get_custom_format.bind(report);
		report.get_custom_format = async (settings) => {
			const result = await frappe.call({
				method: "eims.educational_institution_management_system.report.student_register.student_register.get_branding",
				args: { academic_year: report.get_filter_value("academic_year") },
			});
			report.school_branding = result.message;
			return get_custom_format(settings);
		};
		report.get_print_template = (settings, custom_format) => custom_format || "print_grid";

		report.page.add_inner_button(__("Export Excel with Date"), () => {
			const filters = report.get_filter_values();
			if (!filters?.academic_year) {
				frappe.msgprint(__("Please select an Academic Year"));
				return;
			}
			open_url_post(frappe.request.url, {
				cmd: "eims.educational_institution_management_system.report.student_register.student_register.export_xlsx",
				filters: JSON.stringify(filters),
			});
		});
	},

};
