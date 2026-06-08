from __future__ import annotations

from agents.base import BaseAgent
from core.config import AppConfig
from core.models import EngagementResult, WorkflowRequest


class EngagementAgent(BaseAgent):
    def __init__(self, settings: AppConfig, trace=None, telemetry=None) -> None:
        super().__init__("Engagement", trace=trace, telemetry=telemetry)
        self.settings = settings

    def recommend_window(self, request: WorkflowRequest) -> EngagementResult:
        meeting_hours = request.meeting_hours
        focus_hours = request.focus_hours

        if meeting_hours > 20:
            best_window = "Early morning study window"
            study_windows = ["6:00-7:30 AM", "Weekend deep work block"]
            workload_band = "High meeting load"
        elif focus_hours >= 15:
            best_window = "Afternoon deep-work block"
            study_windows = ["1:30-3:30 PM", "Post-lunch review block"]
            workload_band = "Balanced workload"
        else:
            best_window = "Evening review block"
            study_windows = ["7:00-9:00 PM", "Saturday sprint block"]
            workload_band = "Moderate workload"

        explanation = (
            f"Workload signals show {meeting_hours} meeting hours and {focus_hours} focus hours, so the best window is {best_window}."
        )
        confidence = 0.92 if meeting_hours != focus_hours else 0.78

        result = EngagementResult(
            best_study_window=best_window,
            study_windows=study_windows,
            workload_band=workload_band,
            explanation=explanation,
            confidence=confidence,
        )
        self._record("recommend_window", request, result, confidence, explanation, best_window)
        return result
