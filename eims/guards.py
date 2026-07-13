# Copyright (c) 2026, Catfa and Contributors
# See license.txt

import frappe
from werkzeug.exceptions import abort
from werkzeug.utils import redirect


def _has_desk_access(user):
	"""True if any role *explicitly assigned* to the user grants desk access.

	Mirrors User.has_desk_access(): the implicit "All"/"Guest" roles from
	frappe.get_roles() must be ignored — "All" carries desk_access=1, so it
	would falsely pass every user.
	"""
	return bool(
		frappe.db.sql(
			"""
			select 1 from `tabHas Role` hr
			join `tabRole` r on r.name = hr.role
			where hr.parent = %s and hr.parenttype = 'User' and r.desk_access = 1
			limit 1
			""",
			user,
		)
	)


def redirect_deskless_from_app():
	"""Keep desk-less visitors off /app, sending them to the SPA (/school).

	Registered as a `before_request` hook. Covers guests and any signed-in user
	whose roles carry no desk access (Teacher / Student / Guardian). Desk users
	(Academic Admin, System Manager, Administrator) pass through untouched.

	The path check runs first so the role lookup only fires on /app requests.
	A 302 with no-store is used (not a 301) so the bounce is never cached.
	"""
	request = getattr(frappe.local, "request", None)
	path = request.path if request else ""
	if not (path == "/app" or path.startswith("/app/")):
		return

	user = frappe.session.user
	if user != "Guest" and _has_desk_access(user):
		return

	response = redirect("/school", code=302)
	response.headers["Cache-Control"] = "no-store"
	abort(response)
