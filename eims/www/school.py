# يقدّم تطبيق SPA (مدرسة سهول العلم) على المسار /school.
# Injects boot (user + csrf) and resolves built asset URLs from the Vite manifest.
import json
import os

import frappe

BASE = "/assets/eims/spa/"


def get_context(context):
	context.no_cache = 1
	context.boot = frappe.as_json(
		{
			"user": frappe.session.user,
			"csrf_token": frappe.sessions.get_csrf_token(),
		}
	)

	js, css = _resolve_assets()
	context.app_js = js
	context.app_css = css
	return context


def _resolve_assets():
	"""Read the Vite manifest to find hashed JS/CSS for the entry chunk."""
	manifest_path = frappe.get_app_path("eims", "public", "spa", ".vite", "manifest.json")
	if not os.path.exists(manifest_path):
		return "", []
	with open(manifest_path, encoding="utf-8") as f:
		manifest = json.load(f)

	entry = None
	for key, val in manifest.items():
		if val.get("isEntry") or key.endswith("main.tsx"):
			entry = val
			break
	if entry is None and manifest:
		entry = next(iter(manifest.values()))
	if not entry:
		return "", []

	js = BASE + entry["file"]
	css = [BASE + c for c in entry.get("css", [])]
	return js, css
