"""Synchronize and export Arabic translations for EIMS standard records."""

import frappe
from frappe.translate import deduplicate_messages, get_messages_for_app, write_translations_file


EIMS_ARABIC_TRANSLATIONS = {
	"🎓 Suhool Al-Ilm School Management System": "🎓 نظام إدارة مدرسة سهول العلم",
	"Open School System": "فتح نظام المدرسة",
	"Add Student": "إضافة طالب",
	"New Assessment": "تقييم جديد",
	"Take Attendance": "تسجيل الحضور",
	"👥 Students and Enrollment": "👥 الطلبة والتسجيل",
	"Students": "الطلبة",
	"Enrollments": "التسجيلات",
	"Student Payments": "دفعات الطلبة",
	"📚 Academic Operations": "📚 العمليات الأكاديمية",
	"Assessments": "التقييمات",
	"Academic Curriculum": "المنهج الدراسي",
	"Results": "النتائج",
	"Student Attendance": "حضور الطلبة",
	"Timetables": "الجداول الدراسية",
	"Daily Accomplishments": "الإنجازات اليومية",
	"🧑‍🏫 People and Communication": "🧑‍🏫 الأفراد والتواصل",
	"Staff and Teachers": "الكادر والمعلمون",
	"Teacher Subject Assignments": "تعيينات المعلمين للمواد",
	"Staff Academic Assignments": "تعيينات الكادر للسنة الدراسية",
	"Guardians": "أولياء الأمور",
	"Staff Attendance": "حضور الكادر",
	"Requests": "الطلبات",
	"🌱 Student Welfare and Activities": "🌱 رعاية الطلبة والأنشطة",
	"Disciplinary Actions": "الإجراءات التأديبية",
	"School Activities": "الأنشطة المدرسية",
	"🏛️ Academic Structure": "🏛️ الهيكل الأكاديمي",
	"Academic Stages": "المراحل الدراسية",
	"Sections": "الفصول",
	"Subjects": "المواد الدراسية",
	"⚙️ Administration and Finance": "⚙️ الإدارة والمالية",
	"Academic Years": "السنوات الدراسية",
	"Stage Fees": "رسوم المراحل",
	"School Information": "بيانات المدرسة",
	"Nationalities": "الجنسيات",
	"EIMS Staff Academic Assignment": "تعيين الكادر للسنة الدراسية",
	"EIMS Academic Curriculum": "المنهج الدراسي",
	"Staff Member": "عضو الكادر",
	"Staff Name": "اسم عضو الكادر",
	"Academic Year": "السنة الدراسية",
	"Role": "الدور",
	"Title": "المسمى الوظيفي",
	"Status": "الحالة",
	"Start Date": "تاريخ البداية",
	"End Date": "تاريخ النهاية",
	"Notes": "الملاحظات",
	"Active": "نشط",
	"On Leave": "في إجازة",
	"Inactive": "غير نشط",
	"Stage": "المرحلة",
	"Subject": "المادة",
	"Subject Name": "اسم المادة",
	"Academic History": "السجل الأكاديمي",
	"Student Records": "سجل الطالب",
	"Academic Structure": "الهيكل الأكاديمي",
	"People and Enrollment": "الأفراد والتسجيل",
	"Student Operations": "عمليات الطلبة",
	"School Operations": "عمليات المدرسة",
	"Create and activate an Academic Year before creating academic records.": "أنشئ وفعّل سنة دراسية قبل إنشاء السجلات الأكاديمية.",
	"Academic Year {0} does not exist.": "السنة الدراسية {0} غير موجودة.",
	"Subject {0} is not active in the Academic Year curriculum for this stage.": "المادة {0} غير مفعّلة في منهج هذه المرحلة للسنة الدراسية.",
	"Assignment start date must be before the end date.": "يجب أن يكون تاريخ بداية التعيين قبل تاريخ النهاية.",
	"Curriculum start date must be before the end date.": "يجب أن يكون تاريخ بداية المنهج قبل تاريخ النهاية.",
	"The selected subject does not belong to this stage.": "المادة المختارة لا تنتمي إلى هذه المرحلة.",
	"The selected section does not belong to this stage.": "الفصل المختار لا ينتمي إلى هذه المرحلة.",
	"A timetable slot must use the timetable section.": "يجب أن يستخدم صف الجدول الفصل المحدد للجدول.",
	"Create an Enrollment for this student and Academic Year before recording results.": "أنشئ تسجيلاً لهذا الطالب في السنة الدراسية قبل رصد النتائج.",
	"Student {0} is not enrolled in the selected Academic Year and section.": "الطالب {0} غير مسجل في السنة الدراسية والفصل المحددين.",
	"Student {0} is not enrolled in the selected Academic Year.": "الطالب {0} غير مسجل في السنة الدراسية المحددة.",
	"Staff member {0} is not assigned to the selected Academic Year.": "عضو الكادر {0} غير معين في السنة الدراسية المحددة.",
	"Teacher {0} is not assigned to the selected stage, section, and subject.": "المعلم {0} غير مكلف بالمرحلة والفصل والمادة المحددة.",
}


def sync_arabic_translations():
	"""Create or update EIMS Arabic Translation records."""
	for source_text, translated_text in EIMS_ARABIC_TRANSLATIONS.items():
		name = frappe.db.get_value("Translation", {"language": "ar", "source_text": source_text}, "name")
		if name:
			doc = frappe.get_doc("Translation", name)
			doc.translated_text = translated_text
			doc.save()
		else:
			frappe.get_doc(
				{
					"doctype": "Translation",
					"language": "ar",
					"source_text": source_text,
					"translated_text": translated_text,
				}
			).insert()

	frappe.db.commit()
	return len(EIMS_ARABIC_TRANSLATIONS)


def export_arabic_translations():
	"""Export all EIMS messages, including Workspace strings, to ``translations/ar.csv``."""
	additional_messages = [("EIMS", source_text) for source_text in EIMS_ARABIC_TRANSLATIONS]
	messages = deduplicate_messages(get_messages_for_app("eims") + additional_messages)
	write_translations_file("eims", "ar", app_messages=messages)
	return len(messages)
