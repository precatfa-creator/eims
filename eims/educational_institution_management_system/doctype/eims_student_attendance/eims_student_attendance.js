// Copyright (c) 2026, Catfa and contributors
// For license information, please see license.txt

function load_roster(frm) {
	if (!frm.doc.section || !frm.doc.academic_year || frm.doc.docstatus !== 0) return;

	const fill = () =>
		frappe.call({
			method: "eims.educational_institution_management_system.doctype.eims_student_attendance.eims_student_attendance.get_section_students",
			args: { section: frm.doc.section, academic_year: frm.doc.academic_year },
		}).then(({ message }) => {
			frm.clear_table("rows");
			(message || []).forEach((student) => frm.add_child("rows", student));
			frm.refresh_field("rows");
			if (!message?.length) {
				frappe.show_alert({ message: __("No enrolled students in this section."), indicator: "orange" });
			}
		});

	if ((frm.doc.rows || []).length) {
		frappe.confirm(__("Replace the current rows with the section roster?"), fill);
	} else {
		fill();
	}
}

frappe.ui.form.on("EIMS Student Attendance", {
	refresh(frm) {
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__("Get Students"), () => load_roster(frm));
		}
	},
	section: load_roster,
	academic_year: load_roster,
});
