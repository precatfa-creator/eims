# واجهة بيانات المدرسة للفرونت-إند (SPA).
# Returns/accepts the exact shape expected by src/data/types.ts (SchoolData),
# plus full CRUD. Student placement is resolved from EIMS Enrollment of the active year.
import frappe

from eims.academic_year import ensure_staff_academic_assignment

CURRENCY = {"ar": "د.ل", "en": "LYD"}
SCHOOL_FALLBACK = {"nameAr": "مدرسة سهول العلم للتعليم الخاص", "nameEn": "Suhool Al-Ilm Private School"}


# ─────────────────────────────  READ  ─────────────────────────────
@frappe.whitelist()
def get_school_data():
	"""Full SchoolData snapshot consumed by the SPA store."""
	inst = frappe.get_all("EIMS Institution", fields=["institution_name"], limit=1)
	school = dict(SCHOOL_FALLBACK)
	if inst:
		school["nameAr"] = inst[0].institution_name or school["nameAr"]

	years = [
		{"id": y.name, "label": y.year_name, "isCurrent": bool(y.is_active)}
		for y in frappe.get_all("EIMS Academic Year", fields=["name", "year_name", "is_active"], order_by="year_name")
	]
	active_id = next((y["id"] for y in years if y["isCurrent"]), None)

	stages = [
		{"id": s.name, "nameAr": s.name_ar, "nameEn": s.name_en, "order": s.order, "category": s.category}
		for s in frappe.get_all("EIMS Stage", fields=["name", "name_ar", "name_en", "order", "category"], order_by="`order`")
	]
	sections = [
		{"id": s.name, "stageId": s.stage, "nameAr": s.name_ar, "nameEn": s.name_en}
		for s in frappe.get_all("EIMS Section", fields=["name", "stage", "name_ar", "name_en"], order_by="name")
	]
	subjects = [
		{"id": s.name, "stageId": s.stage, "nameAr": s.subject_name, "nameEn": s.subject_name_en}
		for s in frappe.get_all("EIMS Subject", fields=["name", "stage", "subject_name", "subject_name_en"], order_by="name")
	]
	staff = [
		{
			"id": s.name, "nameAr": s.name_ar, "nameEn": s.name_en, "gender": s.gender, "role": s.role,
			"titleAr": s.title_ar, "titleEn": s.title_en, "phone": s.phone, "email": s.email,
			"hiredYearId": s.hired_year, "image": s.image, "nationality": s.nationality,
			"nationalId": s.national_id, "passportNumber": s.passport_number,
			"dob": str(s.date_of_birth) if s.date_of_birth else "", "address": s.address,
			"qualification": s.qualification, "hireDate": str(s.hire_date) if s.hire_date else "",
		}
		for s in frappe.get_all(
			"EIMS Staff",
			fields=[
				"name", "name_ar", "name_en", "gender", "role", "title_ar", "title_en", "phone", "email",
				"hired_year", "image", "nationality", "national_id", "passport_number", "date_of_birth",
				"address", "qualification", "hire_date",
			],
			order_by="creation",
		)
	]
	assignments = [
		{"id": a.name, "teacherId": a.staff, "stageId": a.stage, "sectionId": a.section, "subjectId": a.subject, "yearId": a.academic_year}
		for a in frappe.get_all("EIMS Teacher Assignment", fields=["name", "staff", "stage", "section", "subject", "academic_year"])
	]

	enrollments = [
		{"id": e.name, "studentId": e.student, "yearId": e.academic_year, "stageId": e.stage, "sectionId": e.section, "status": e.status}
		for e in frappe.get_all("EIMS Enrollment", fields=["name", "student", "academic_year", "stage", "section", "status"])
	]
	active_enr = {e["studentId"]: e for e in enrollments if e["yearId"] == active_id}

	students = []
	for s in frappe.get_all(
		"EIMS Student",
		fields=[
			"name", "enrollment_number", "student_name", "student_name_en", "gender", "date_of_birth",
			"place_of_birth", "nationality", "national_id", "passport_number", "image", "address", "notes",
			"parent_name", "parent_phone", "second_guardian_phone", "phone", "email",
		],
		order_by="creation",
	):
		enr = active_enr.get(s.name)
		students.append({
			"id": s.name, "code": s.enrollment_number, "nameAr": s.student_name, "nameEn": s.student_name_en,
			"gender": s.gender, "dob": str(s.date_of_birth) if s.date_of_birth else "",
			"placeOfBirth": s.place_of_birth, "nationality": s.nationality, "nationalId": s.national_id,
			"passportNumber": s.passport_number, "image": s.image, "address": s.address, "notes": s.notes,
			"guardianNameAr": s.parent_name, "guardianPhone": s.parent_phone,
			"secondGuardianPhone": s.second_guardian_phone, "phone": s.phone, "email": s.email,
			"stageId": enr["stageId"] if enr else None,
			"sectionId": enr["sectionId"] if enr else None,
			"enrollmentYearId": active_id,
		})

	fees = [
		{"stageId": f.stage, "yearId": f.academic_year, "amount": f.amount}
		for f in frappe.get_all("EIMS Stage Fee", fields=["stage", "academic_year", "amount"])
	]
	payments = [
		{"studentId": p.student, "yearId": p.academic_year, "amountPaid": p.amount_paid}
		for p in frappe.get_all(
			"EIMS Student Payment",
			filters={"docstatus": 1},
			fields=["student", "academic_year", "sum(amount_paid) as amount_paid"],
			group_by="student, academic_year",
		)
	]
	nationalities = frappe.get_all("EIMS Nationality", pluck="name", order_by="nationality_name")

	return {
		"school": school, "currency": CURRENCY, "years": years, "stages": stages, "sections": sections,
		"subjects": subjects, "staff": staff, "assignments": assignments, "enrollments": enrollments,
		"students": students, "fees": fees, "payments": payments, "nationalities": nationalities,
		"me": _me(),
	}


def _me():
	"""Identity of the signed-in user: their staff record, role, and admin flag."""
	staff_id = _my_staff()
	return {
		"user": frappe.session.user,
		"staffId": staff_id,
		"role": frappe.db.get_value("EIMS Staff", staff_id, "role") if staff_id else None,
		"isAdmin": _is_admin(),
	}


# ─────────────────────────────  SETTINGS  ─────────────────────────────
@frappe.whitelist()
def set_current_year(year):
	doc = frappe.get_doc("EIMS Academic Year", year)
	doc.is_active = 1
	doc.save(ignore_permissions=True)  # controller deactivates the others
	frappe.db.commit()
	return {"currentYear": year}


@frappe.whitelist()
def add_academic_year(label, start_date=None, end_date=None, set_active=0):
	if not frappe.db.exists("EIMS Academic Year", label):
		frappe.get_doc({
			"doctype": "EIMS Academic Year", "year_name": label,
			"start_date": start_date or None, "end_date": end_date or None,
			"is_active": 1 if frappe.utils.cint(set_active) else 0,
		}).insert(ignore_permissions=True)
	elif frappe.utils.cint(set_active):
		set_current_year(label)
	frappe.db.commit()
	return {"id": label}


@frappe.whitelist()
def set_stage_fee(stage, year, amount):
	amount = frappe.utils.flt(amount)
	name = f"{stage}-{year}"
	if frappe.db.exists("EIMS Stage Fee", name):
		frappe.db.set_value("EIMS Stage Fee", name, "amount", amount)
	else:
		frappe.get_doc({"doctype": "EIMS Stage Fee", "stage": stage, "academic_year": year, "amount": amount}).insert(ignore_permissions=True)
	frappe.db.commit()
	return {"stageId": stage, "yearId": year, "amount": amount}


@frappe.whitelist()
def set_student_payment(student, year, amount_paid):
	"""Create a submitted payment transaction; never overwrite payment history."""
	amount_paid = frappe.utils.flt(amount_paid)
	enrollment = frappe.db.get_value(
		"EIMS Enrollment", {"student": student, "academic_year": year}, "name"
	)
	if not enrollment:
		frappe.throw("يجب إنشاء تسجيل للطالب قبل تسجيل الدفعة.")
	payment = frappe.get_doc(
		{"doctype": "EIMS Student Payment", "enrollment": enrollment, "amount_paid": amount_paid}
	)
	payment.insert(ignore_permissions=True)
	payment.submit()
	frappe.db.commit()
	return {
		"studentId": student,
		"yearId": year,
		"amountPaid": frappe.db.sql(
			"select coalesce(sum(amount_paid), 0) from `tabEIMS Student Payment` "
			"where enrollment = %s and docstatus = 1",
			enrollment,
		)[0][0],
	}


# ─────────────────────────────  CRUD  ─────────────────────────────
def _next_student_code():
	last = frappe.db.sql("select max(cast(enrollment_number as unsigned)) from `tabEIMS Student`")
	return str(((last and last[0][0]) or 1000) + 1)


def _upsert_enrollment(student, year, stage, section=None, status=None, override_reason=None):
	name = f"{student}-{year}"
	if frappe.db.exists("EIMS Enrollment", name):
		e = frappe.get_doc("EIMS Enrollment", name)
		e.stage, e.section = stage, section or None
		if status is not None:
			e.status = status
			e.enrollment_override_reason = override_reason
		e.save(ignore_permissions=True)
	else:
		frappe.get_doc({
			"doctype": "EIMS Enrollment", "student": student, "academic_year": year,
			"stage": stage, "section": section or None, "status": status or "مسودة",
			"enrollment_override_reason": override_reason,
			"enrollment_date": frappe.utils.nowdate(),
		}).insert(ignore_permissions=True)


def _attach_image(file_url, doctype, docname):
	"""Bind an uploaded photo to its record so private-file reads follow the
	doctype's permissions (an unattached private File is owner-only)."""
	if not file_url:
		return
	name = frappe.db.get_value("File", {"file_url": file_url}, "name")
	if not name:
		return
	f = frappe.get_doc("File", name)
	if f.attached_to_doctype == doctype and f.attached_to_name == docname and f.is_private:
		return
	f.attached_to_doctype = doctype
	f.attached_to_name = docname
	f.is_private = 1
	f.save(ignore_permissions=True)
	# handle_is_private_changed() rewrites file_url when moving to /private/files
	if f.file_url != file_url:
		frappe.db.set_value(doctype, docname, "image", f.file_url)


@frappe.whitelist()
def save_student(payload):
	p = frappe.parse_json(payload)
	if p.get("id"):
		doc = frappe.get_doc("EIMS Student", p["id"])
	else:
		doc = frappe.new_doc("EIMS Student")
		doc.enrollment_number = p.get("code") or _next_student_code()
	doc.update({
		"student_name": p.get("nameAr"), "student_name_en": p.get("nameEn"),
		"gender": p.get("gender") or "male", "date_of_birth": p.get("dob") or None,
		"place_of_birth": p.get("placeOfBirth"), "nationality": p.get("nationality") or "ليبيا",
		"national_id": p.get("nationalId"), "passport_number": p.get("passportNumber"),
		"image": p.get("image"), "address": p.get("address"), "notes": p.get("notes"),
		"parent_name": p.get("guardianNameAr"), "parent_phone": p.get("guardianPhone"),
		"second_guardian_phone": p.get("secondGuardianPhone"), "phone": p.get("phone"), "email": p.get("email"),
	})
	doc.save(ignore_permissions=True)
	_attach_image(p.get("image"), "EIMS Student", doc.name)
	if p.get("yearId") and p.get("stageId"):
		_upsert_enrollment(doc.name, p["yearId"], p["stageId"], p.get("sectionId"))
	frappe.db.commit()
	return {"id": doc.name}


@frappe.whitelist()
def save_staff(payload):
	p = frappe.parse_json(payload)
	doc = frappe.get_doc("EIMS Staff", p["id"]) if p.get("id") else frappe.new_doc("EIMS Staff")
	doc.update({
		"name_ar": p.get("nameAr"), "name_en": p.get("nameEn"), "role": p.get("role") or "teacher",
		"gender": p.get("gender") or "male", "title_ar": p.get("titleAr"), "title_en": p.get("titleEn"),
		"phone": p.get("phone"), "email": p.get("email"), "image": p.get("image"),
		"nationality": p.get("nationality") or "ليبيا", "national_id": p.get("nationalId"),
		"passport_number": p.get("passportNumber"), "date_of_birth": p.get("dob") or None,
		"address": p.get("address"), "qualification": p.get("qualification"),
		"hire_date": p.get("hireDate") or None, "hired_year": p.get("hiredYearId"),
	})
	doc.save(ignore_permissions=True)
	_attach_image(p.get("image"), "EIMS Staff", doc.name)
	ensure_staff_academic_assignment(doc)
	frappe.db.commit()
	return {"id": doc.name}


@frappe.whitelist()
def save_stage(payload):
	p = frappe.parse_json(payload)
	doc = frappe.get_doc("EIMS Stage", p["id"]) if p.get("id") else frappe.new_doc("EIMS Stage")
	doc.update({
		"name_ar": p.get("nameAr"), "name_en": p.get("nameEn"),
		"order": frappe.utils.cint(p.get("order") or 1), "category": p.get("category") or "primary",
	})
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"id": doc.name}


@frappe.whitelist()
def save_section(payload):
	p = frappe.parse_json(payload)
	doc = frappe.get_doc("EIMS Section", p["id"]) if p.get("id") else frappe.new_doc("EIMS Section")
	doc.update({"stage": p.get("stageId"), "name_ar": p.get("nameAr"), "name_en": p.get("nameEn")})
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"id": doc.name}


@frappe.whitelist()
def save_subject(payload):
	p = frappe.parse_json(payload)
	doc = frappe.get_doc("EIMS Subject", p["id"]) if p.get("id") else frappe.new_doc("EIMS Subject")
	doc.update({"subject_name": p.get("nameAr"), "subject_name_en": p.get("nameEn"), "stage": p.get("stageId")})
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"id": doc.name}


@frappe.whitelist()
def save_assignment(payload):
	p = frappe.parse_json(payload)
	doc = frappe.get_doc("EIMS Teacher Assignment", p["id"]) if p.get("id") else frappe.new_doc("EIMS Teacher Assignment")
	doc.update({
		"staff": p.get("teacherId"), "stage": p.get("stageId"), "section": p.get("sectionId") or None,
		"subject": p.get("subjectId") or None, "academic_year": p.get("yearId"),
	})
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"id": doc.name}


@frappe.whitelist()
def delete_assignment(name):
	frappe.delete_doc("EIMS Teacher Assignment", name, ignore_permissions=True)
	frappe.db.commit()
	return {"deleted": name}


@frappe.whitelist()
def enroll_student(student, year, stage, section=None, status="مسودة", override_reason=None):
	_upsert_enrollment(student, year, stage, section, status, override_reason)
	frappe.db.commit()
	return {"studentId": student, "yearId": year, "stageId": stage, "sectionId": section}


# ─────────────────────────────  GRADE ENTRY  ─────────────────────────────
ADMIN_ROLES = {"Academic Admin", "System Manager", "Administrator"}

TERM_ORDER = {
	"الفترة الأولى": 1,
	"الفترة الثانية": 2,
	"الفترة الثالثة": 3,
	"الفصل الدراسي الأول": 4,
	"الفصل الدراسي الثاني": 5,
	"الدور الثاني": 6,
}


def _is_admin():
	return bool(set(frappe.get_roles(frappe.session.user)) & ADMIN_ROLES)


def _my_staff():
	return frappe.db.get_value("EIMS Staff", {"user_id": frappe.session.user}, "name")


def _assert_can_grade(subject, section, year):
	"""Admins may grade any class; a teacher only subjects/classes assigned to them."""
	if _is_admin():
		return
	staff = _my_staff()
	if not staff:
		frappe.throw("لا تملك صلاحية إدخال الدرجات.", frappe.PermissionError)
	assigns = frappe.get_all(
		"EIMS Teacher Assignment",
		filters={"staff": staff, "academic_year": year, "subject": subject},
		fields=["section"],
	)
	if not assigns:
		frappe.throw("هذه المادة غير مُسندة إليك.", frappe.PermissionError)
	# Section-specific assignments must match the requested section; a blank
	# assignment section means "all sections of the subject".
	if section and all(a.section and a.section != section for a in assigns):
		frappe.throw("هذا الفصل غير مُسند إليك.", frappe.PermissionError)


def _find_assessment(subject, section, term, year):
	found = frappe.get_all(
		"EIMS Assessment",
		filters={"subject": subject, "section": section, "term": term, "academic_year": year},
		fields=["name", "max_mark", "docstatus"],
		limit=1,
	)
	return found[0] if found else None


@frappe.whitelist()
def get_class_grades(subject, section, term, year):
	"""Roster for a class with any existing marks pre-filled for the given term."""
	_assert_can_grade(subject, section, year)

	roster = {
		e.student
		for e in frappe.get_all(
			"EIMS Enrollment",
			filters={"academic_year": year, "section": section, "status": "مسجل"},
			fields=["student"],
		)
	}

	marks, assessment, max_mark, submitted = {}, None, 100, False
	existing = _find_assessment(subject, section, term, year)
	if existing:
		assessment = existing.name
		max_mark = existing.max_mark or 100
		submitted = existing.docstatus == 1
		for r in frappe.get_doc("EIMS Assessment", assessment).students:
			marks[r.student] = {"coursework": r.coursework, "exam": r.exam, "total": r.total_score}
			roster.add(r.student)  # keep already-graded students even if enrollment changed

	rows = []
	for sid in roster:
		m = marks.get(sid, {})
		rows.append({
			"student": sid,
			"studentName": frappe.db.get_value("EIMS Student", sid, "student_name"),
			"coursework": m.get("coursework"),
			"exam": m.get("exam"),
			"total": m.get("total"),
		})
	rows.sort(key=lambda r: r["studentName"] or "")
	return {"assessment": assessment, "submitted": submitted, "maxMark": max_mark, "rows": rows}


@frappe.whitelist()
def save_class_grades(subject, section, term, year, rows, stage=None, max_mark=100):
	"""Create/update the term's EIMS Assessment for a class from entered marks."""
	_assert_can_grade(subject, section, year)
	rows = frappe.parse_json(rows)

	existing = _find_assessment(subject, section, term, year)
	if existing:
		doc = frappe.get_doc("EIMS Assessment", existing.name)
		if doc.docstatus == 1:
			frappe.throw("النتيجة معتمدة ولا يمكن تعديلها.")
	else:
		doc = frappe.new_doc("EIMS Assessment")
		doc.subject, doc.section, doc.term, doc.academic_year = subject, section, term, year
		doc.stage = stage or None

	doc.max_mark = frappe.utils.flt(max_mark) or None
	doc.set("students", [])
	for r in rows:
		has_mark = r.get("total") not in (None, "") or r.get("coursework") or r.get("exam")
		if not has_mark:
			continue
		doc.append("students", {
			"student": r["student"],
			"coursework": frappe.utils.flt(r.get("coursework")) or None,
			"exam": frappe.utils.flt(r.get("exam")) or None,
			"total_score": frappe.utils.flt(r.get("total")) or None,
		})
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"assessment": doc.name, "graded": len(doc.students)}


def _assert_can_attend(section, year):
	"""Admins may take attendance for any class; a teacher only their sections."""
	if _is_admin():
		return
	staff = _my_staff()
	if not staff:
		frappe.throw("لا تملك صلاحية تسجيل الحضور.", frappe.PermissionError)
	if not frappe.db.exists(
		"EIMS Teacher Assignment", {"staff": staff, "academic_year": year, "section": section}
	):
		frappe.throw("هذا الفصل غير مُسند إليك.", frappe.PermissionError)


def _find_attendance(section, date, year):
	found = frappe.get_all(
		"EIMS Student Attendance",
		filters={"section": section, "attendance_date": date, "academic_year": year},
		pluck="name",
		limit=1,
	)
	return found[0] if found else None


@frappe.whitelist()
def get_attendance_sheet(section, date, year):
	"""Class roster for a date with any saved statuses pre-filled (default حاضر)."""
	_assert_can_attend(section, year)

	roster = {
		e.student
		for e in frappe.get_all(
			"EIMS Enrollment",
			filters={"academic_year": year, "section": section, "status": "مسجل"},
			fields=["student"],
		)
	}
	saved = {}
	name = _find_attendance(section, date, year)
	if name:
		for r in frappe.get_doc("EIMS Student Attendance", name).rows:
			saved[r.student] = r.status
			roster.add(r.student)

	rows = [
		{
			"student": sid,
			"studentName": frappe.db.get_value("EIMS Student", sid, "student_name"),
			"status": saved.get(sid, "حاضر"),
		}
		for sid in roster
	]
	rows.sort(key=lambda r: r["studentName"] or "")
	return {"attendance": name, "rows": rows}


@frappe.whitelist()
def save_attendance(section, date, year, rows, stage=None, subject=None):
	"""Create/update the day's EIMS Student Attendance for a class."""
	_assert_can_attend(section, year)
	rows = frappe.parse_json(rows)

	name = _find_attendance(section, date, year)
	if name:
		doc = frappe.get_doc("EIMS Student Attendance", name)
	else:
		doc = frappe.new_doc("EIMS Student Attendance")
		doc.section, doc.attendance_date, doc.academic_year = section, date, year
		doc.stage = stage or None
		doc.teacher = _my_staff()
	doc.subject = subject or None
	doc.set("rows", [])
	for r in rows:
		if not r.get("student"):
			continue
		doc.append("rows", {"student": r["student"], "status": r.get("status") or "حاضر"})
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"attendance": doc.name, "count": len(doc.rows)}


@frappe.whitelist()
def get_my_grades(year=None):
	"""Read-only grade book of every class the user teaches (all classes for admins).

	Per class: students as rows, the graded terms as columns. Used by the
	"my students' grades" overview in the SPA.
	"""
	year = year or frappe.db.get_value("EIMS Academic Year", {"is_active": 1}, "name")
	filters = {"academic_year": year}
	if not _is_admin():
		staff = _my_staff()
		if not staff:
			return {"year": year, "classes": []}
		filters["staff"] = staff

	pairs, seen = [], set()
	for a in frappe.get_all("EIMS Teacher Assignment", filters=filters, fields=["subject", "section"]):
		if a.subject and a.section and (a.subject, a.section) not in seen:
			seen.add((a.subject, a.section))
			pairs.append((a.subject, a.section))

	classes = []
	for subject, section in pairs:
		roster = {
			e.student
			for e in frappe.get_all(
				"EIMS Enrollment",
				filters={"academic_year": year, "section": section, "status": "مسجل"},
				fields=["student"],
			)
		}
		terms, marks = set(), {}
		for a in frappe.get_all(
			"EIMS Assessment",
			filters={"subject": subject, "section": section, "academic_year": year},
			fields=["name", "term"],
		):
			terms.add(a.term)
			for r in frappe.get_doc("EIMS Assessment", a.name).students:
				roster.add(r.student)
				marks.setdefault(r.student, {})[a.term] = r.total_score

		students = sorted(
			(
				{
					"student": sid,
					"studentName": frappe.db.get_value("EIMS Student", sid, "student_name"),
					"marks": marks.get(sid, {}),
				}
				for sid in roster
			),
			key=lambda s: s["studentName"] or "",
		)
		classes.append({
			"subjectId": subject,
			"subjectName": frappe.db.get_value("EIMS Subject", subject, "subject_name"),
			"sectionId": section,
			"sectionName": frappe.db.get_value("EIMS Section", section, "name_ar"),
			"terms": sorted(terms, key=lambda t: TERM_ORDER.get(t, 99)),
			"students": students,
		})
	return {"year": year, "classes": classes}
