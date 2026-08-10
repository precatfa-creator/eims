# Copyright (c) 2026, Catfa and Contributors
# See license.txt
#
# Pure-arithmetic self-check. Run in the bench venv:
#   /home/omix/frappe-bench/env/bin/python test_eims_enrollment.py

from eims_enrollment import FULLY_PAID, PARTIALLY_PAID, UNPAID, payment_split


def _run():
	# nothing paid yet
	assert payment_split(1000, 0) == (1000, UNPAID)

	# a first instalment leaves the rest outstanding
	assert payment_split(1000, 400) == (600, PARTIALLY_PAID)

	# a later instalment closes the balance
	assert payment_split(1000, 1000) == (0, FULLY_PAID)

	# more collected than the fee (fee lowered after payment) never goes negative
	assert payment_split(1000, 1200) == (0, FULLY_PAID)

	# stage fee not set yet: no payment, nothing owed
	assert payment_split(0, 0) == (0, UNPAID)

	# strings from the database are still money
	assert payment_split("1000", "250.5") == (749.5, PARTIALLY_PAID)

	print("ok")


if __name__ == "__main__":
	_run()
