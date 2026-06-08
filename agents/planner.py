from __future__ import annotations

from datetime import datetime
import math

from agents.base import BaseAgent
from core.config import AppConfig
from core.models import CertificationProfile, StudyPlanResult, StudyPlanWeek, WorkflowRequest


class PlannerAgent(BaseAgent):
    def __init__(self, settings: AppConfig, trace=None, telemetry=None) -> None:
        super().__init__("Planner", trace=trace, telemetry=telemetry)
        self.settings = settings

    def generate_plan(
        self,
        request: WorkflowRequest,
        profile: CertificationProfile,
        best_window: str,
    ) -> StudyPlanResult:
        exam_date = datetime.fromisoformat(request.exam_date).date()
        days_remaining = max(7, (exam_date - datetime.utcnow().date()).days)
        weeks_available = max(1, math.ceil(days_remaining / 7))

        target_hours = max(profile.recommended_hours, request.weekly_hours)
        allocated_hours = min(target_hours, request.weekly_hours * weeks_available)
        recommended_study_increase = max(0, target_hours - request.weekly_hours * weeks_available)

        weeks: list[StudyPlanWeek] = []
        remaining_hours = target_hours
        for week in range(1, min(weeks_available, 6) + 1):
            week_hours = min(request.weekly_hours, remaining_hours)
            if week == 1:
                focus = "Orientation and baseline assessment"
                activities = ["Review certification objectives", "Map skills to learning path"]
            elif week >= weeks_available:
                focus = "Exam rehearsal and confidence building"
                activities = ["Timed practice set", "Review weak topics"]
            elif week >= 3:
                focus = "Hands-on practice and gap closure"
                activities = ["Lab exercises", "Quiz weak areas"]
            else:
                focus = "Core concept building"
                activities = ["Study key modules", "Take notes"]

            weeks.append(StudyPlanWeek(week=week, hours=week_hours, focus=focus, activities=activities))
            remaining_hours = max(0, remaining_hours - week_hours)

        plan_summary = (
            f"Allocated {allocated_hours} hours across {len(weeks)} weeks with the best study window set to {best_window}."
        )
        confidence = 0.94 if allocated_hours >= profile.recommended_hours else 0.72

        result = StudyPlanResult(
            weeks=weeks,
            total_weeks=len(weeks),
            recommended_hours=profile.recommended_hours,
            allocated_hours=allocated_hours,
            recommended_study_increase=recommended_study_increase,
            plan_summary=plan_summary,
            confidence=confidence,
        )
        self._record(
            "generate_plan",
            {"request": request, "profile": profile, "best_window": best_window},
            result,
            confidence,
            plan_summary,
            f"Weekly plan built for {len(weeks)} weeks",
        )
        return result
