# واجهة الإشعارات والأخبار المعروضة في بوابة /school.
# Visibility is resolved per signed-in user: audience "الجميع" reaches everyone,
# "حسب الدور" the listed roles, "مستخدمون محددون" the listed users.

import frappe
from frappe.utils import now_datetime

ADMIN_ROLES = {"Academic Admin", "System Manager", "Administrator"}
PUBLISHED = "منشور"


def _is_admin():
	return bool(ADMIN_ROLES & set(frappe.get_roles()))


def _visible_names(user):
	"""Names of published, in-window announcements this user is targeted by."""
	roles = frappe.get_roles(user)
	now = now_datetime()

	rows = frappe.get_all(
		"EIMS Announcement",
		filters={"status": PUBLISHED},
		fields=["name", "audience", "publish_from", "publish_until"],
	)
	in_window = [
		r
		for r in rows
		if (not r.publish_from or r.publish_from <= now)
		and (not r.publish_until or r.publish_until >= now)
	]
	if not in_window:
		return []

	names = {r.name for r in in_window if r.audience == "الجميع"}

	role_targeted = [r.name for r in in_window if r.audience == "حسب الدور"]
	if role_targeted and roles:
		names |= {
			d.parent
			for d in frappe.get_all(
				"EIMS Announcement Role",
				filters={"parent": ("in", role_targeted), "role": ("in", list(roles))},
				fields=["parent"],
			)
		}

	user_targeted = [r.name for r in in_window if r.audience == "مستخدمون محددون"]
	if user_targeted:
		names |= {
			d.parent
			for d in frappe.get_all(
				"EIMS Announcement User",
				filters={"parent": ("in", user_targeted), "user": user},
				fields=["parent"],
			)
		}

	return list(names)


@frappe.whitelist()
def get_announcements(limit=50):
	"""Feed for the signed-in user, newest first with pinned items on top."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)

	names = _visible_names(user)
	if not names:
		return {"items": [], "unread": 0}

	rows = frappe.get_all(
		"EIMS Announcement",
		filters={"name": ("in", names)},
		fields=[
			"name", "title", "body", "category", "priority",
			"attachment", "link_url", "is_pinned", "creation", "publish_from",
		],
		order_by="is_pinned desc, coalesce(publish_from, creation) desc",
		limit_page_length=frappe.utils.cint(limit) or 50,
	)

	read = {
		d.announcement
		for d in frappe.get_all(
			"EIMS Announcement Read",
			filters={"user": user, "announcement": ("in", [r.name for r in rows])},
			fields=["announcement"],
		)
	}

	items = [
		{
			"id": r.name,
			"title": r.title,
			"body": r.body,
			"category": r.category,
			"priority": r.priority,
			"attachment": r.attachment,
			"linkUrl": r.link_url,
			"isPinned": bool(r.is_pinned),
			"publishedAt": str(r.publish_from or r.creation),
			"isRead": r.name in read,
		}
		for r in rows
	]
	return {"items": items, "unread": sum(1 for i in items if not i["isRead"])}


@frappe.whitelist()
def mark_read(announcement):
	"""Idempotent: re-reading an announcement must not pile up rows."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
	if announcement not in _visible_names(user):
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)

	if not frappe.db.exists("EIMS Announcement Read", {"announcement": announcement, "user": user}):
		frappe.get_doc(
			{
				"doctype": "EIMS Announcement Read",
				"announcement": announcement,
				"user": user,
				"read_at": now_datetime(),
			}
		).insert(ignore_permissions=True)
		frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def mark_all_read():
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)

	names = _visible_names(user)
	if not names:
		return {"ok": True, "marked": 0}

	already = {
		d.announcement
		for d in frappe.get_all(
			"EIMS Announcement Read",
			filters={"user": user, "announcement": ("in", names)},
			fields=["announcement"],
		)
	}
	pending = [n for n in names if n not in already]
	for n in pending:
		frappe.get_doc(
			{
				"doctype": "EIMS Announcement Read",
				"announcement": n,
				"user": user,
				"read_at": now_datetime(),
			}
		).insert(ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True, "marked": len(pending)}


@frappe.whitelist()
def save_announcement(payload):
	"""Create/update from the portal. Admin-only; the desk form is the fuller editor."""
	if not _is_admin():
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)

	p = frappe.parse_json(payload)
	doc = (
		frappe.get_doc("EIMS Announcement", p["id"])
		if p.get("id")
		else frappe.new_doc("EIMS Announcement")
	)
	doc.update(
		{
			"title": p.get("title"),
			"body": p.get("body"),
			"category": p.get("category") or "إشعار",
			"priority": p.get("priority") or "عادي",
			"audience": p.get("audience") or "الجميع",
			"status": p.get("status") or "منشور",
			"link_url": p.get("linkUrl"),
			"attachment": p.get("attachment"),
			"is_pinned": 1 if p.get("isPinned") else 0,
			"publish_from": p.get("publishFrom") or None,
			"publish_until": p.get("publishUntil") or None,
		}
	)
	doc.set("roles", [{"role": r} for r in (p.get("roles") or [])])
	doc.set("users", [{"user": u} for u in (p.get("users") or [])])
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"id": doc.name}
