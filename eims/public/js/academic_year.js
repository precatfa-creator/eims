const YEAR_AWARE_DOCTYPES = [
	"EIMS Academic Curriculum",
	"EIMS Assessment",
	"EIMS Daily Accomplishment",
	"EIMS Disciplinary Action",
	"EIMS Enrollment",
	"EIMS Request",
	"EIMS Result",
	"EIMS School Activity",
	"EIMS Staff Academic Assignment",
	"EIMS Staff Attendance",
	"EIMS Stage Fee",
	"EIMS Student Attendance",
	"EIMS Student Payment",
	"EIMS Teacher Assignment",
	"EIMS Timetable",
];

const SUBJECT_DRIVEN_DOCTYPES = [
	"EIMS Academic Curriculum",
	"EIMS Assessment",
	"EIMS Daily Accomplishment",
	"EIMS Teacher Assignment",
];

const TEACHER_FIELDS = {
	"EIMS Daily Accomplishment": "teacher",
	"EIMS Student Attendance": "teacher",
	"EIMS Teacher Assignment": "staff",
	"EIMS Timetable": "staff",
};

function set_active_academic_year(frm) {
	if (!frm.is_new() || frm.doc.academic_year || frm.__eims_loading_active_year) {
		return;
	}

	frm.__eims_loading_active_year = true;
	frappe.db.get_value("EIMS Academic Year", { is_active: 1 }, "name").then(({ message }) => {
		if (message?.name && !frm.doc.academic_year) {
			frm.set_value("academic_year", message.name);
		}
	});
}

function section_filters(stage) {
	return { filters: { stage: stage || "__none__" } };
}

function subject_filters(stage, require_stage = false) {
	return stage ? { filters: { stage } } : require_stage ? { filters: { stage: "__none__" } } : {};
}

function subject_query(frm, require_stage = false) {
	return {
		query: "eims.queries.subject_query",
		filters: {
			academic_year: frm.doc.academic_year,
			stage: frm.doc.stage || (require_stage ? "__none__" : null),
		},
	};
}

function teacher_query(frm) {
	return {
		query: "eims.queries.teacher_query",
		filters: {
			academic_year: frm.doc.academic_year,
			stage: frm.doc.stage,
			section: frm.doc.section,
			subject: frm.doc.subject,
		},
	};
}

function clear_section_if_outside_stage(frm, stage) {
	if (!frm.doc.section || !stage) return;

	frappe.db.get_value("EIMS Section", frm.doc.section, "stage").then(({ message }) => {
		if (message?.stage && message.stage !== stage && frm.doc.section) {
			frm.set_value("section", null);
		}
	});
}

function clear_subject_if_outside_stage(frm, stage) {
	if (!frm.doc.subject || !stage) return;

	frappe.db.get_value("EIMS Subject", frm.doc.subject, "stage").then(({ message }) => {
		if (message?.stage && message.stage !== stage && frm.doc.subject) {
			frm.set_value("subject", null);
		}
	});
}

function sync_subject_stage(frm) {
	if (!frm.doc.subject) return;

	frappe.db.get_value("EIMS Subject", frm.doc.subject, "stage").then(({ message }) => {
		if (!message?.stage) return;
		if (frm.doc.stage !== message.stage) {
			frm.set_value("stage", message.stage);
		}
		clear_section_if_outside_stage(frm, message.stage);
	});
}

function load_result_enrollment(frm) {
	if (!frm.doc.student || !frm.doc.academic_year) return;

	frappe.call({
		method: "eims.queries.get_student_enrollment_context",
		args: { student: frm.doc.student, academic_year: frm.doc.academic_year },
	}).then(({ message }) => {
		if (!message) return;
		frm.set_value({ stage: message.stage || null, section: message.section || null });
	});
}

function set_context_queries(frm) {
	if (["EIMS Assessment", "EIMS Daily Accomplishment", "EIMS Enrollment", "EIMS Teacher Assignment"].includes(frm.doctype)) {
		frm.set_query("section", () => section_filters(frm.doc.stage));
	}

	if (frm.fields_dict.subject) {
		if (frm.doctype === "EIMS Academic Curriculum") {
			frm.set_query("subject", () => subject_filters(frm.doc.stage));
		} else {
			frm.set_query("subject", () => subject_query(frm));
		}
	}

	const teacher_field = TEACHER_FIELDS[frm.doctype];
	if (teacher_field && frm.fields_dict[teacher_field]) {
		frm.set_query(teacher_field, () => teacher_query(frm));
	}

	if (frm.doctype === "EIMS School Activity") {
		frm.set_query("supervisor", () => ({
			query: "eims.queries.staff_query",
			filters: { academic_year: frm.doc.academic_year },
		}));
		frm.set_query("student", "participants", () => ({
			query: "eims.queries.student_query",
			filters: { academic_year: frm.doc.academic_year },
		}));
	}

	if (frm.doctype === "EIMS Staff Attendance") {
		frm.set_query("staff", "rows", () => ({
			query: "eims.queries.staff_query",
			filters: { academic_year: frm.doc.academic_year },
		}));
	}

	if (frm.doctype === "EIMS Assessment") {
		frm.set_query("student", "students", () => ({
			query: "eims.queries.student_query",
			filters: {
				academic_year: frm.doc.academic_year,
				stage: frm.doc.stage,
				section: frm.doc.section,
				subject: frm.doc.subject,
			},
		}));
	}

	if (frm.doctype === "EIMS Student Attendance") {
		frm.set_query("subject", () => subject_query(frm, true));
		frm.set_query("student", "rows", () => ({
			query: "eims.queries.student_query",
			filters: {
				academic_year: frm.doc.academic_year,
				stage: frm.doc.stage,
				section: frm.doc.section,
				subject: frm.doc.subject,
			},
		}));
	}

	if (frm.doctype === "EIMS Result") {
		frm.set_query("student", () => ({
			query: "eims.queries.student_query",
			filters: { academic_year: frm.doc.academic_year },
		}));
		frm.set_query("subject", "results", () => subject_query(frm, true));
	}

	if (["EIMS Disciplinary Action", "EIMS Request", "EIMS Student Payment"].includes(frm.doctype)) {
		frm.set_query("student", () => ({
			query: "eims.queries.student_query",
			filters: { academic_year: frm.doc.academic_year },
		}));
	}

	if (frm.doctype === "EIMS Student Payment") {
		frm.set_query("enrollment", () => ({
			filters: { academic_year: frm.doc.academic_year || "__none__" },
		}));
	}

	if (frm.doctype === "EIMS Timetable") {
		frm.set_query("subject", "slots", () => subject_query(frm, true));
		frm.set_query("section", "slots", (doc, cdt, cdn) => {
			const row = locals[cdt][cdn];
			return section_filters(row.stage || frm.doc.stage);
		});
	}
}

for (const doctype of YEAR_AWARE_DOCTYPES) {
	frappe.ui.form.on(doctype, {
		setup: set_context_queries,
		onload: set_active_academic_year,
		academic_year(frm) {
			if (frm.doctype === "EIMS Result") load_result_enrollment(frm);
		},
		section(frm) {
			if (frm.doctype === "EIMS Student Attendance") {
				frappe.db.get_value("EIMS Section", frm.doc.section, "stage").then(({ message }) => {
					if (message?.stage) clear_subject_if_outside_stage(frm, message.stage);
				});
			}
			if (frm.doctype === "EIMS Timetable" && frm.doc.section) {
				frappe.db.get_value("EIMS Section", frm.doc.section, "stage").then(({ message }) => {
					if (message?.stage) frm.set_value("stage", message.stage);
				});
			}
		},
		student(frm) {
			if (frm.doctype === "EIMS Result") load_result_enrollment(frm);
		},
		stage(frm) {
			if (frm.doctype === "EIMS Enrollment") clear_section_if_outside_stage(frm, frm.doc.stage);
		},
	});
}

for (const doctype of SUBJECT_DRIVEN_DOCTYPES) {
	frappe.ui.form.on(doctype, { subject: sync_subject_stage });
}

frappe.ui.form.on("EIMS Enrollment", {
	refresh(frm) {
		if (frm.is_new() || ["منسحب", "منقول", "متخرج"].includes(frm.doc.status)) return;
		frm.add_custom_button(__("Create Payment"), () => {
			frappe.new_doc("EIMS Student Payment", { enrollment: frm.doc.name });
		}, __("Actions"));
	},
});

const REQUESTER_DOCTYPES = { "طالب": "EIMS Student", "ولي أمر": "EIMS Guardian", "معلم": "EIMS Staff" };

frappe.ui.form.on("EIMS Request", {
	raised_by_role(frm) {
		const doctype = REQUESTER_DOCTYPES[frm.doc.raised_by_role];
		frm.set_value({ raised_by_doctype: doctype || null, raised_by: null, raised_by_user: null });
	},
	raised_by(frm) {
		if (!frm.doc.raised_by || !frm.doc.raised_by_doctype) return;
		frappe.db.get_value(frm.doc.raised_by_doctype, frm.doc.raised_by, "user_id").then(({ message }) => {
			frm.set_value("raised_by_user", message?.user_id || null);
		});
	},
});
