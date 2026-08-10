// Shows the clerk the running balance before the receipt is saved.
// Year/context filtering for this doctype lives in public/js/academic_year.js.

frappe.ui.form.on("EIMS Student Payment", {
	refresh: show_balance,
	enrollment: show_balance,

	amount_paid(frm) {
		if (frm.__eims_balance) render_balance(frm, frm.__eims_balance);
	},
});

function show_balance(frm) {
	frm.dashboard.clear_headline();
	if (!frm.doc.enrollment) return;

	if (frm.doc.docstatus > 0) {
		// A submitted receipt keeps the balance it was taken with; never recompute it.
		return frm.dashboard.set_headline(frappe.utils.escape_html(frm.doc.payment_summary || ""));
	}

	frappe.call({
		method: "eims.educational_institution_management_system.doctype.eims_student_payment.eims_student_payment.enrollment_balance",
		args: { enrollment: frm.doc.enrollment, exclude: frm.doc.name },
	}).then(({ message }) => {
		if (!message) return;
		frm.__eims_balance = message;
		if (frm.is_new()) {
			// Prefill the full remaining balance; the clerk edits it down for a part payment.
			frm.set_value("total_fee", message.total_fee);
			frm.set_value("previously_paid", message.previously_paid);
			if (!frm.doc.amount_paid) frm.set_value("amount_paid", message.outstanding);
		}
		render_balance(frm, message);
	});
}

function render_balance(frm, balance) {
	const remaining = Math.max(balance.outstanding - (frm.doc.amount_paid || 0), 0);
	const money = (v) => format_currency(v);
	frm.dashboard.set_headline(
		__("Total fee {0} · already paid {1} · outstanding {2} · remaining after this payment {3}", [
			money(balance.total_fee),
			money(balance.previously_paid),
			money(balance.outstanding),
			money(remaining),
		])
	);
}
