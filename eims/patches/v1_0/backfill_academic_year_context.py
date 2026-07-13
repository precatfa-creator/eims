from eims.academic_year import backfill_academic_curriculum, backfill_staff_academic_assignments


def execute():
	backfill_staff_academic_assignments()
	backfill_academic_curriculum()
