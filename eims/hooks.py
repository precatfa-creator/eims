app_name = "eims"
app_title = "Educational Institution Management System"
app_publisher = "Catfa"
app_description = "Educational Institution Management System"
app_email = "precatfa@gmail.com"
app_license = "mit"

# Public school website. The authenticated school portal remains available at
# /school for teachers, students, and guardians.
home_page = "index"

after_install = "eims.install.after_install"

# Bounce logged-out visitors off the desk (/app) to the SPA (/school).
before_request = ["eims.guards.redirect_deskless_from_app"]

# School-branded login page (loads on /login; scoped to the auth card).
web_include_css = "/assets/eims/css/login.css"

doctype_js = {
	"EIMS Academic Curriculum": "public/js/academic_year.js",
	"EIMS Assessment": "public/js/academic_year.js",
	"EIMS Daily Accomplishment": "public/js/academic_year.js",
	"EIMS Disciplinary Action": "public/js/academic_year.js",
	"EIMS Enrollment": "public/js/academic_year.js",
	"EIMS Request": "public/js/academic_year.js",
	"EIMS Result": "public/js/academic_year.js",
	"EIMS School Activity": "public/js/academic_year.js",
	"EIMS Staff Academic Assignment": "public/js/academic_year.js",
	"EIMS Staff Attendance": "public/js/academic_year.js",
	"EIMS Stage Fee": "public/js/academic_year.js",
	"EIMS Student Attendance": "public/js/academic_year.js",
	"EIMS Student Payment": "public/js/academic_year.js",
	"EIMS Teacher Assignment": "public/js/academic_year.js",
	"EIMS Timetable": "public/js/academic_year.js",
}

fixtures = [
	{"dt": "Role", "filters": [["doctype", "=", "Role"], ["role_name", "in", ["Academic Admin", "Teacher", "Student", "Guardian"]]]},
]

# Non-desk roles land on the SPA (/school) after login instead of the desk.
role_home_page = {
	"Teacher": "school",
	"Student": "school",
	"Guardian": "school",
}

# All operational records belong to an Academic Year. The active year is used
# as a default, but historic records may explicitly reference an earlier year.
doc_events = {
	"EIMS Assessment": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Daily Accomplishment": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Disciplinary Action": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Enrollment": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Request": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Result": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS School Activity": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Staff Academic Assignment": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Staff Attendance": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Stage Fee": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Student Attendance": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Student Payment": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Teacher Assignment": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Timetable": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Academic Curriculum": {"before_validate": "eims.academic_year.apply_active_academic_year"},
	"EIMS Staff": {"after_insert": "eims.academic_year.ensure_staff_academic_assignment"},
}
