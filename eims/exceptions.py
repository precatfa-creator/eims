class GradeValidationError(Exception):
	"""Raised when grade validation fails."""
	pass

class AssessmentLockedError(Exception):
	"""Raised when trying to modify a submitted/published assessment."""
	pass

class WorkflowTransitionError(Exception):
	"""Raised when an invalid workflow transition is attempted."""
	pass
