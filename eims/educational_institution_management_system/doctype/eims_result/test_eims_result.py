# Copyright (c) 2026, Catfa and Contributors
# See license.txt
#
# Pure-arithmetic self-check. Run in the bench venv:
#   /home/omix/frappe-bench/env/bin/python test_eims_result.py

from eims_result import card_totals, subject_finals


def _run():
	# two terms, no make-up -> final = yearly
	row = {"term_1_total": 40, "term_2_total": 45, "max_mark": 100}
	assert subject_finals(row) == (85, 85)

	# make-up exam overrides the yearly total
	row = {"term_1_total": 15, "term_2_total": 18, "make_up_exam": 50, "max_mark": 100}
	assert subject_finals(row) == (33, 50)

	rows = [
		{"term_1_total": 40, "term_2_total": 45, "max_mark": 100},
		{"term_1_total": 30, "term_2_total": 30, "make_up_exam": 0, "max_mark": 100},
	]
	g, m, p = card_totals(rows)
	assert (g, m, p) == (145, 200, 72.5)

	# empty card: no divide-by-zero
	assert card_totals([{"subject": "X"}]) == (0, 0, 0)

	print("ok")


if __name__ == "__main__":
	_run()
