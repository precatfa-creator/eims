# Excel import utility for existing grade spreadsheets
import frappe
import openpyxl
import io


@frappe.whitelist()
def upload_and_import_grades(file_name, academic_year, program, year, term, subject):
	"""
	Import grades from an uploaded Excel file.
	Returns summary of imported records.
	"""
	# Get file content
	file_doc = frappe.get_doc("File", {"file_name": file_name})
	file_path = file_doc.get_full_path()

	wb = openpyxl.load_workbook(file_path, data_only=True)
	ws = wb.active

	imported = import_worksheet(ws, academic_year, program, year, term, subject)
	return imported


def import_worksheet(ws, academic_year, program, year, term, subject):
	"""Parse a LibreOffice/Excel worksheet and create grade entries."""
	rows = list(ws.iter_rows(values_only=True))

	# Skip header rows, find student rows (they have name + number pattern)
	student_rows = []
	for i, row in enumerate(rows):
		# Student rows typically start with a number and Arabic name
		if row and len(row) > 1 and isinstance(row[0], (int, float)):
			student_rows.append((i, row))

	if not student_rows:
		frappe.throw(_("لم يتم العثور على صف طلاب في الملف"))

	imported = 0
	for row_idx, row in student_rows:
		student_name = row[1] if len(row) > 1 else None
		if not student_name:
			continue

		# Find or create student
		student_name = str(student_name).strip()
		student = frappe.db.get_value("EIMS Student", {"student_name": student_name}, "name")

		if not student:
			enrollment_num = str(int(row[0])) if row[0] else student_name
			student_doc = frappe.get_doc({
				"doctype": "EIMS Student",
				"student_name": student_name,
				"enrollment_number": enrollment_num,
			})
			student_doc.insert(ignore_permissions=True)
			student = student_doc.name

		# Check enrollment
		if not frappe.db.exists("EIMS Student Enrollment", {
			"student": student,
			"academic_year": academic_year,
			"program": program,
			"year": year,
		}):
			enrollment = frappe.get_doc({
				"doctype": "EIMS Student Enrollment",
				"student": student,
				"academic_year": academic_year,
				"program": program,
				"year": year,
				"status": "مسجل",
			})
			enrollment.insert(ignore_permissions=True)

		imported += 1

	return {"imported": imported, "total_rows": len(student_rows)}
