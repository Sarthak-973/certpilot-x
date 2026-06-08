from __future__ import annotations

from datetime import datetime

from core.config import AppConfig
from core.models import WorkflowRequest


class ValidationError(ValueError):
    pass


def validate_request(request: WorkflowRequest, settings: AppConfig) -> None:
    errors: list[str] = []

    if not request.learner_id.strip():
        errors.append("learner_id is required")
    if request.weekly_hours < settings.min_weekly_hours:
        errors.append("weekly_hours must be at least 1")
    if request.weekly_hours > settings.max_weekly_hours:
        errors.append("weekly_hours must be 20 or less")
    if request.practice_score < 0 or request.practice_score > 100:
        errors.append("practice_score must be between 0 and 100")
    if request.meeting_hours < 0 or request.focus_hours < 0:
        errors.append("meeting_hours and focus_hours must be non-negative")
    if request.meeting_hours + request.focus_hours > settings.max_weekly_commitment_hours:
        errors.append("workload signals exceed the maximum weekly commitment")

    try:
        datetime.fromisoformat(request.exam_date)
    except ValueError:
        errors.append("exam_date must be ISO formatted as YYYY-MM-DD")

    if errors:
        raise ValidationError("; ".join(errors))
