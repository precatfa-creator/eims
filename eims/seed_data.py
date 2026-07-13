# بذر بيانات مدرسة سهول العلم (يطابق src/data/seed.ts في الفرونت-إند)
# Idempotent seeding. Run:  bench --site catfa.local execute eims.seed_data.run
import frappe

CURRENT_YEAR = "2025-2026"
ACTIVE_YEAR = "2026-2027"

YEARS = [
	("2023-2024", "2023-09-01", "2024-06-30", 0),
	("2024-2025", "2024-09-01", "2025-06-30", 0),
	("2025-2026", "2025-09-01", "2026-06-30", 0),
	("2026-2027", "2026-09-01", "2027-06-30", 1),
]

# (key, name_ar, name_en, order, category)
STAGES = [
	("st-kg", "الروضة", "Kindergarten", 1, "kindergarten"),
	("st-pre", "التمهيدي", "Pre-Primary", 2, "kindergarten"),
	("st-g1", "الأول الابتدائي", "Grade 1 (Primary)", 3, "primary"),
	("st-g2", "الثاني الابتدائي", "Grade 2 (Primary)", 4, "primary"),
	("st-g3", "الثالث الابتدائي", "Grade 3 (Primary)", 5, "primary"),
	("st-g4", "الرابع الابتدائي", "Grade 4 (Primary)", 6, "primary"),
	("st-g5", "الخامس الابتدائي", "Grade 5 (Primary)", 7, "primary"),
	("st-g6", "السادس الابتدائي", "Grade 6 (Primary)", 8, "primary"),
	("st-g7", "السابع الإعدادي", "Grade 7 (Preparatory)", 9, "preparatory"),
	("st-g8", "الثامن الإعدادي", "Grade 8 (Preparatory)", 10, "preparatory"),
	("st-g9", "التاسع الإعدادي", "Grade 9 (Preparatory)", 11, "preparatory"),
]
STAGE_AR = {k: ar for (k, ar, en, o, c) in STAGES}
TWO_SECTIONS = {"st-g1", "st-g5", "st-g7"}

SUBJECT_SETS = {
	"kindergarten": [
		("القرآن الكريم", "Holy Quran"), ("اللغة العربية", "Arabic"),
		("مهارات أساسية", "Basic Skills"), ("الرياضيات التمهيدية", "Early Math"),
		("الرسم والتلوين", "Drawing"),
	],
	"primary": [
		("التربية الإسلامية", "Islamic Studies"), ("اللغة العربية", "Arabic"),
		("الرياضيات", "Mathematics"), ("العلوم", "Science"), ("اللغة الإنجليزية", "English"),
		("الدراسات الاجتماعية", "Social Studies"), ("التربية الفنية", "Art"),
	],
	"preparatory": [
		("التربية الإسلامية", "Islamic Studies"), ("اللغة العربية", "Arabic"),
		("الرياضيات", "Mathematics"), ("العلوم", "Science"), ("اللغة الإنجليزية", "English"),
		("الدراسات الاجتماعية", "Social Studies"), ("الحاسوب", "Computer"),
	],
}

# (key, name_ar, name_en, gender, role, title_ar, title_en, phone, email, hired_year)
STAFF = [
	("sf-1", "عبدالله الفقيه", "Abdullah Al-Faqih", "male", "admin", "مدير المدرسة", "Principal", "0913001001", "principal@suhool.ly", "2023-2024"),
	("sf-2", "سعاد المبروك", "Suad Al-Mabrouk", "female", "admin", "نائبة المدير", "Vice Principal", "0913001002", "vice@suhool.ly", "2023-2024"),
	("sf-3", "خالد الورفلي", "Khaled Al-Werfalli", "male", "employee", "محاسب", "Accountant", "0913001003", "", "2023-2024"),
	("sf-4", "هند العبيدي", "Hind Al-Obeidi", "female", "employee", "سكرتيرة", "Secretary", "0913001004", "", "2024-2025"),
	("sf-5", "منصور الزوي", "Mansour Al-Zwai", "male", "employee", "مشرف عام", "Supervisor", "0913001005", "", "2023-2024"),
	("tc-1", "أحمد الهادي", "Ahmed Al-Hadi", "male", "teacher", "معلم لغة عربية", "Arabic Teacher", "0914002001", "", "2023-2024"),
	("tc-2", "فاطمة الزهراء", "Fatima Al-Zahra", "female", "teacher", "معلمة رياضيات", "Math Teacher", "0914002002", "", "2023-2024"),
	("tc-3", "محمد العالم", "Mohammed Al-Alim", "male", "teacher", "معلم علوم", "Science Teacher", "0914002003", "", "2024-2025"),
	("tc-4", "خديجة سالم", "Khadija Salem", "female", "teacher", "معلمة لغة إنجليزية", "English Teacher", "0914002004", "", "2023-2024"),
	("tc-5", "يوسف إدريس", "Yousef Idris", "male", "teacher", "معلم تربية إسلامية", "Islamic Studies Teacher", "0914002005", "", "2024-2025"),
	("tc-6", "عائشة منصور", "Aisha Mansour", "female", "teacher", "معلمة روضة", "Kindergarten Teacher", "0914002006", "", "2023-2024"),
	("tc-7", "إبراهيم قاسم", "Ibrahim Qasim", "male", "teacher", "معلم دراسات اجتماعية", "Social Studies Teacher", "0914002007", "", "2025-2026"),
	("tc-8", "زينب الطيب", "Zainab Al-Tayeb", "female", "teacher", "معلمة حاسوب", "Computer Teacher", "0914002008", "", "2024-2025"),
]

SUBJECT_KEYWORD = {
	"tc-1": "اللغة العربية", "tc-2": "الرياضيات", "tc-3": "العلوم",
	"tc-4": "اللغة الإنجليزية", "tc-5": "التربية الإسلامية",
	"tc-7": "الدراسات الاجتماعية", "tc-8": "الحاسوب",
}
# historical: (teacher_key, stage_key, subject_ar, year)
HISTORY = [
	("tc-1", "st-g9", "اللغة العربية", "2024-2025"),
	("tc-1", "st-g8", "اللغة العربية", "2023-2024"),
	("tc-2", "st-g6", "الرياضيات", "2024-2025"),
	("tc-3", "st-g7", "العلوم", "2024-2025"),
	("tc-4", "st-g5", "اللغة الإنجليزية", "2023-2024"),
]

FIRST_M = ["محمد", "أحمد", "عبدالرحمن", "يوسف", "عمر", "خالد", "إبراهيم", "علي", "حمزة", "مصعب", "أنس", "بلال"]
FIRST_F = ["فاطمة", "مريم", "عائشة", "سارة", "نور", "هبة", "رنا", "ليان", "جنى", "سلمى", "رغد", "دانية"]
FAMILY = ["الفيتوري", "الزروق", "الشريف", "بن سعود", "القذافي", "المقري", "الدرسي", "الترهوني", "الزنتاني", "المصراتي"]
EN_M = ["Mohammed", "Ahmed", "Abdulrahman", "Yousef", "Omar", "Khaled", "Ibrahim", "Ali", "Hamza", "Musab", "Anas", "Bilal"]
EN_F = ["Fatima", "Mariam", "Aisha", "Sara", "Nour", "Heba", "Rana", "Layan", "Jana", "Salma", "Raghad", "Dania"]
EN_FAMILY = ["Al-Fitouri", "Al-Zarrouq", "Al-Sharif", "Bin Saud", "Al-Qadhafi", "Al-Maqri", "Al-Dersi", "Al-Terhouni", "Al-Zintani", "Al-Misrati"]
PER_SECTION = {"st-kg": 6, "st-pre": 5, "st-g1": 4, "st-g2": 5, "st-g3": 4, "st-g4": 4, "st-g5": 4, "st-g6": 3, "st-g7": 3, "st-g8": 3, "st-g9": 3}
BASE_FEE = {"kindergarten": 1500, "primary": 1200, "preparatory": 1400}


def _ins(doc):
	frappe.get_doc(doc).insert(ignore_permissions=True)


def _record_payment(student, year, amount):
	"""Seed a real submitted payment transaction after the enrolment exists."""
	if not amount:
		return
	enrollment = frappe.db.get_value(
		"EIMS Enrollment", {"student": student, "academic_year": year}, "name"
	)
	if not enrollment or frappe.db.exists("EIMS Student Payment", {"enrollment": enrollment, "docstatus": 1}):
		return
	payment = frappe.get_doc(
		{"doctype": "EIMS Student Payment", "enrollment": enrollment, "amount_paid": amount}
	)
	payment.insert(ignore_permissions=True)
	payment.submit()


NATIONALITIES = [
	("ليبيا", "Libya"), ("مصر", "Egypt"), ("تونس", "Tunisia"), ("الجزائر", "Algeria"),
	("المغرب", "Morocco"), ("السودان", "Sudan"), ("سوريا", "Syria"), ("فلسطين", "Palestine"),
	("الأردن", "Jordan"), ("العراق", "Iraq"), ("لبنان", "Lebanon"), ("اليمن", "Yemen"),
	("تشاد", "Chad"), ("النيجر", "Niger"), ("مالي", "Mali"), ("نيجيريا", "Nigeria"),
	("تركيا", "Turkey"), ("الهند", "India"), ("بنغلاديش", "Bangladesh"), ("الفلبين", "Philippines"),
	("أخرى", "Other"),
]


def run():
	"""Idempotent seed of Suhool Al-Ilm sample data."""
	# 0) Nationalities (link target)
	for (ar, en) in NATIONALITIES:
		if not frappe.db.exists("EIMS Nationality", ar):
			_ins({"doctype": "EIMS Nationality", "nationality_name": ar, "nationality_en": en})

	# 1) Academic years
	for (label, start, end, active) in YEARS:
		if not frappe.db.exists("EIMS Academic Year", label):
			_ins({"doctype": "EIMS Academic Year", "year_name": label, "start_date": start, "end_date": end, "is_active": active})

	# 2) Stages
	for (k, ar, en, order, cat) in STAGES:
		if not frappe.db.exists("EIMS Stage", ar):
			_ins({"doctype": "EIMS Stage", "name_ar": ar, "name_en": en, "order": order, "category": cat})

	# 3) Sections
	for (k, ar, en, order, cat) in STAGES:
		secs = [("أ", "A")] + ([("ب", "B")] if k in TWO_SECTIONS else [])
		for (sar, sen) in secs:
			nm = f"{ar}-{sen}"
			if not frappe.db.exists("EIMS Section", nm):
				_ins({"doctype": "EIMS Section", "stage": ar, "name_ar": sar, "name_en": sen})

	# 4) Subjects
	for (k, ar, en, order, cat) in STAGES:
		for (sar, sen) in SUBJECT_SETS[cat]:
			nm = f"{ar}-{sar}"
			if not frappe.db.exists("EIMS Subject", nm):
				_ins({"doctype": "EIMS Subject", "subject_name": sar, "subject_name_en": sen, "stage": ar})

	# 5) Staff
	staff_name = {}
	for (k, ar, en, gender, role, tar, ten, phone, email, hy) in STAFF:
		existing = frappe.db.get_value("EIMS Staff", {"name_ar": ar, "role": role}, "name")
		if existing:
			staff_name[k] = existing
			continue
		d = frappe.get_doc({
			"doctype": "EIMS Staff", "name_ar": ar, "name_en": en, "gender": gender, "role": role,
			"title_ar": tar, "title_en": ten, "phone": phone, "email": email or None, "hired_year": hy,
		})
		d.insert(ignore_permissions=True)
		staff_name[k] = d.name

	def subject_name(stage_key, subj_ar):
		return frappe.db.get_value("EIMS Subject", {"stage": STAGE_AR[stage_key], "subject_name": subj_ar}, "name")

	def add_assignment(teacher_key, stage_key, subj_name, year, section=None):
		filt = {"staff": staff_name[teacher_key], "stage": STAGE_AR[stage_key], "academic_year": year}
		if subj_name:
			filt["subject"] = subj_name
		if frappe.db.exists("EIMS Teacher Assignment", filt):
			return
		_ins({"doctype": "EIMS Teacher Assignment", "staff": staff_name[teacher_key],
			"stage": STAGE_AR[stage_key], "section": section, "subject": subj_name, "academic_year": year})

	# 6) Current assignments by subject keyword
	for tkey, kw in SUBJECT_KEYWORD.items():
		for (k, ar, en, order, cat) in STAGES:
			snm = frappe.db.get_value("EIMS Subject", {"stage": ar, "subject_name": kw}, "name")
			if snm:
				add_assignment(tkey, k, snm, CURRENT_YEAR)
	# KG teacher -> all KG + Pre subjects
	for stage_key in ("st-kg", "st-pre"):
		for snm in frappe.get_all("EIMS Subject", filters={"stage": STAGE_AR[stage_key]}, pluck="name"):
			add_assignment("tc-6", stage_key, snm, CURRENT_YEAR)
	# historical
	for (tkey, skey, subj_ar, yr) in HISTORY:
		add_assignment(tkey, skey, subject_name(skey, subj_ar), yr)

	# 7) Students
	code = 1001
	name_idx = 0
	for (k, ar, en, order, cat) in STAGES:
		secs = [("أ", "A")] + ([("ب", "B")] if k in TWO_SECTIONS else [])
		base_age = 4 + (order - 1)
		birth_year = 2025 - base_age
		enroll_year = CURRENT_YEAR if order <= 4 else "2023-2024"
		for (sar, sen) in secs:
			section_name = f"{ar}-{sen}"
			for _i in range(PER_SECTION.get(k, 4)):
				is_male = name_idx % 2 == 0
				fi = (name_idx // 2) % 12
				fam = name_idx % len(FAMILY)
				first = FIRST_M[fi] if is_male else FIRST_F[fi]
				en_first = EN_M[fi] if is_male else EN_F[fi]
				enr = str(code)
				if not frappe.db.exists("EIMS Student", enr):
					_ins({
						"doctype": "EIMS Student", "enrollment_number": enr,
						"student_name": f"{first} {FAMILY[fam]}", "student_name_en": f"{en_first} {EN_FAMILY[fam]}",
						"gender": "male" if is_male else "female", "date_of_birth": f"{birth_year}-09-01",
						"parent_name": f"{'والد' if is_male else 'والدة'} {first}", "parent_phone": f"0921{100000 + code}",
						"stage": ar, "section": section_name, "enrollment_year": enroll_year,
					})
				code += 1
				name_idx += 1

	# 8) Stage fees (all years)
	fee_bump = {"2023-2024": 0, "2024-2025": 100, "2025-2026": 200, "2026-2027": 300}
	for (label, start, end, active) in YEARS:
		bump = fee_bump.get(label, 0)
		for (k, ar, en, order, cat) in STAGES:
			nm = f"{ar}-{label}"
			if not frappe.db.exists("EIMS Stage Fee", nm):
				_ins({"doctype": "EIMS Stage Fee", "stage": ar, "academic_year": label, "amount": BASE_FEE[cat] + bump})

	# 9) Create draft enrolments before recording payment transactions.
	extend_production()

	# 10) Payments (current year)
	students = frappe.get_all("EIMS Student", fields=["name", "stage"], order_by="creation")
	for idx, stu in enumerate(students):
		nm = f"{stu.name}-{CURRENT_YEAR}"
		if frappe.db.exists("EIMS Student Payment", nm):
			continue
		fee = frappe.db.get_value("EIMS Stage Fee", {"stage": stu.stage, "academic_year": CURRENT_YEAR}, "amount") or 0
		mod = idx % 5
		paid = fee
		if mod in (1, 3):
			paid = round(fee * 0.5)
		elif mod == 4:
			paid = 0
		_record_payment(stu.name, CURRENT_YEAR, paid)

	frappe.db.commit()
	print("EIMS seed complete:",
		"stages", frappe.db.count("EIMS Stage"),
		"| sections", frappe.db.count("EIMS Section"),
		"| subjects", frappe.db.count("EIMS Subject"),
		"| staff", frappe.db.count("EIMS Staff"),
		"| assignments", frappe.db.count("EIMS Teacher Assignment"),
		"| students", frappe.db.count("EIMS Student"),
		"| enrollments", frappe.db.count("EIMS Enrollment"),
		"| fees", frappe.db.count("EIMS Stage Fee"),
		"| payments", frappe.db.count("EIMS Student Payment"))


def _staff_name(key):
	name_ar = next(s[1] for s in STAFF if s[0] == key)
	return frappe.db.get_value("EIMS Staff", {"name_ar": name_ar}, "name")


def _enroll(student, year, stage, section):
	nm = f"{student}-{year}"
	if frappe.db.exists("EIMS Enrollment", nm):
		return
	_ins({
		"doctype": "EIMS Enrollment", "student": student, "academic_year": year,
		"stage": stage, "section": section, "status": "مسودة", "enrollment_date": f"{year[:4]}-09-01",
	})


def _ensure_assignment(staff, stage, subject, year, section=None):
	filt = {"staff": staff, "stage": stage, "subject": subject, "academic_year": year}
	filt["section"] = section if section else ["is", "not set"]
	if frappe.db.exists("EIMS Teacher Assignment", filt):
		return
	_ins({"doctype": "EIMS Teacher Assignment", "staff": staff, "stage": stage,
		"subject": subject, "academic_year": year, "section": section})


def dedupe_assignments():
	"""Remove duplicate teacher assignments (same staff/stage/section/subject/year)."""
	seen = set()
	for a in frappe.get_all(
		"EIMS Teacher Assignment",
		fields=["name", "staff", "stage", "section", "subject", "academic_year"],
		order_by="creation",
	):
		key = (a.staff, a.stage, a.section or "", a.subject or "", a.academic_year)
		if key in seen:
			frappe.delete_doc("EIMS Teacher Assignment", a.name, force=1, ignore_permissions=True)
		else:
			seen.add(key)


def extend_production():
	"""Year-scoped enrollments, per-section subject teachers, and rollover into the active year."""
	g5 = STAGE_AR["st-g5"]
	math = frappe.db.get_value("EIMS Subject", {"stage": g5, "subject_name": "الرياضيات"}, "name")

	# (a) Grade 5 Math → different teacher per section (أ / ب) in 2025-2026.
	if math:
		for a in frappe.get_all(
			"EIMS Teacher Assignment",
			filters={"subject": math, "academic_year": CURRENT_YEAR, "section": ["in", ["", None]]},
			pluck="name",
		):
			frappe.delete_doc("EIMS Teacher Assignment", a, force=1, ignore_permissions=True)
		_ensure_assignment(_staff_name("tc-2"), g5, math, CURRENT_YEAR, f"{g5}-A")
		_ensure_assignment(_staff_name("tc-8"), g5, math, CURRENT_YEAR, f"{g5}-B")

	# (b) Enrollments for 2025-2026 (history) and 2026-2027 (active) from each student's placement.
	students = frappe.get_all("EIMS Student", fields=["name", "stage", "section"], order_by="creation")
	for stu in students:
		if not stu.stage:
			continue
		_enroll(stu.name, CURRENT_YEAR, stu.stage, stu.section)
		_enroll(stu.name, ACTIVE_YEAR, stu.stage, stu.section)

	# (c) Roll teacher assignments forward 2025-2026 → 2026-2027.
	dedupe_assignments()
	for a in frappe.get_all(
		"EIMS Teacher Assignment",
		filters={"academic_year": CURRENT_YEAR},
		fields=["staff", "stage", "section", "subject"],
	):
		_ensure_assignment(a.staff, a.stage, a.subject, ACTIVE_YEAR, a.section)

	# (d) Payments for the active year (fresh distribution).
	for idx, stu in enumerate(students):
		nm = f"{stu.name}-{ACTIVE_YEAR}"
		if frappe.db.exists("EIMS Student Payment", nm):
			continue
		fee = frappe.db.get_value("EIMS Stage Fee", {"stage": stu.stage, "academic_year": ACTIVE_YEAR}, "amount") or 0
		mod = idx % 5
		paid = fee
		if mod in (1, 3):
			paid = round(fee * 0.5)
		elif mod == 4:
			paid = 0
		_record_payment(stu.name, ACTIVE_YEAR, paid)
