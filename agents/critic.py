from __future__ import annotations

from agents.base import BaseAgent
from core.config import AppConfig
from core.models import CriticReviewResult, EngagementResult, PredictionResult, StudyPlanResult, WorkflowRequest


class CriticAgent(BaseAgent):
    def __init__(self, settings: AppConfig, trace=None, telemetry=None) -> None:
        super().__init__("Critic", trace=trace, telemetry=telemetry)
        self.settings = settings

    def review(
        self,
        request: WorkflowRequest,
        study_plan: StudyPlanResult,
        engagement: EngagementResult,
        prediction: PredictionResult,
        has_prerequisites: bool,
    ) -> CriticReviewResult:
        issues: list[str] = []
        warnings: list[str] = []
        self_reflection: list[str] = []

        if not has_prerequisites:
            issues.append("Missing prerequisites for the selected certification pathway")
        if request.weekly_hours > self.settings.max_weekly_hours:
            issues.append("Weekly hours exceed the configured cap")
        if study_plan.allocated_hours < study_plan.recommended_hours:
            warnings.append("Plan under-allocates hours relative to the certification target")
        if engagement.workload_band == "High meeting load":
            warnings.append("Workload is heavy; reinforce early-morning or weekend study blocks")
        if prediction.pass_probability < self.settings.high_risk_threshold:
            issues.append("Predicted pass probability is below the safe threshold")

        if prediction.confidence < self.settings.minimum_confidence:
            self_reflection.append("Confidence is below the production threshold; a second planning pass is recommended.")

        verdict = "Ready" if not issues and prediction.pass_probability >= self.settings.moderate_risk_threshold else "Needs Revision"
        confidence = max(0.55, 0.96 - 0.1 * len(issues) - 0.05 * len(warnings))
        explanation = (
            f"Critic review checks plan realism, prerequisites, workload alignment, and predicted success. "
            f"Final verdict: {verdict}."
        )

        result = CriticReviewResult(
            verdict=verdict,
            issues=issues,
            warnings=warnings,
            confidence=confidence,
            self_reflection=self_reflection,
            explanation=explanation,
        )
        self._record(
            "review",
            {"request": request, "study_plan": study_plan, "engagement": engagement, "prediction": prediction},
            result,
            confidence,
            explanation,
            verdict,
        )
        return result
