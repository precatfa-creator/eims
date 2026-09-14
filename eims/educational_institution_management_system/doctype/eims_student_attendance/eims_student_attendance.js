// Copyright (c) 2026, Catfa and contributors
// For license information, please see license.txt

const STATUSES = ["حاضر", "غائب", "متأخر", "مأذون"];

// Record one day of the month: the same load/save the school app uses, so a day
// saved here replaces only that day's rows and the rest of the month is kept.
function mark_day(frm) {
	if (frm.is_new() || frm.is_dirty()) {
		frappe.msgprint(__("Save the sheet first."));
		return;
	}

	const month = frm.doc.attendance_date.slice(0, 7);
	const today = frappe.datetime.get_today();
	let dialog; // the date field's change can fire while the dialog is still being built
	const args = () => ({ section: frm.doc.section, year: frm.doc.academic_year, date: dialog.get_value("date") });
	const table = () => dialog.fields_dict.students;
	const set_all = (status) => {
		table().df.data.forEach((row) => (row.status = status));
		table().grid.refresh();
	};

	const load = () => {
		const date = dialog?.get_value("date");
		if (!date) return;
		if (!date.startsWith(month)) {
			frappe.msgprint(__("Pick a day inside the sheet's month."));
			return;
		}
		frappe.call("eims.api.school.get_attendance_sheet", args()).then(({ message }) => {
			table().df.data = message.rows.map((row) => ({
				student: row.student,
				student_name: row.studentName,
				status: row.status,
			}));
			table().grid.refresh();
		});
	};

	dialog = new frappe.ui.Dialog({
		title: __("Mark Day"),
		size: "large",
		fields: [
			{
				fieldname: "date",
				fieldtype: "Date",
				label: __("Date"),
				reqd: 1,
				default: today.startsWith(month) ? today : frm.doc.attendance_date,
				change: load,
			},
			{ fieldtype: "Column Break" },
			{ fieldname: "all_present", fieldtype: "Button", label: __("All Present"), click: () => set_all("حاضر") },
			{ fieldtype: "Column Break" },
			{ fieldname: "all_absent", fieldtype: "Button", label: __("All Absent"), click: () => set_all("غائب") },
			{ fieldtype: "Section Break" },
			{
				fieldname: "students",
				fieldtype: "Table",
				cannot_add_rows: 1,
				cannot_delete_rows: 1,
				in_place_edit: 1,
				data: [],
				fields: [
					{ fieldname: "student", fieldtype: "Link", options: "EIMS Student", label: __("Student"), read_only: 1 },
					{ fieldname: "student_name", fieldtype: "Data", label: __("Student Full Name"), read_only: 1, in_list_view: 1, columns: 6 },
					{ fieldname: "status", fieldtype: "Select", options: STATUSES.join("\n"), label: __("Status"), in_list_view: 1, columns: 4 },
				],
			},
		],
		primary_action_label: __("Save"),
		primary_action() {
			const rows = table().df.data.map(({ student, status }) => ({ student, status }));
			frappe.call({
				method: "eims.api.school.save_attendance",
				args: { ...args(), stage: frm.doc.stage, subject: frm.doc.subject, rows },
				freeze: true,
			}).then(() => {
				dialog.hide();
				frappe.show_alert({ message: __("Day saved."), indicator: "green" });
				frm.reload_doc();
			});
		},
	});

	dialog.show();
	load();
}

frappe.ui.form.on("EIMS Student Attendance", {
	refresh(frm) {
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			frm.add_custom_button(__("Mark Day"), () => mark_day(frm)).addClass("btn-primary");
		}
	},
});
