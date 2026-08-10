// Context filtering is shared by public/js/academic_year.js.

frappe.ui.form.on("EIMS Enrollment", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.payment_status === "مدفوع بالكامل") return;

		frm.add_custom_button(__("Record Payment"), () => {
			frappe.new_doc("EIMS Student Payment", { enrollment: frm.doc.name });
		}).addClass("btn-primary");
	},
});
