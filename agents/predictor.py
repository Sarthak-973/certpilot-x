from __future__ import annotations

from agents.base import BaseAgent
from core.config import AppConfig
from core.models import CertificationProfile, EngagementResult, PredictionResult, StudyPlanResult, WorkflowRequest


class PredictorAgent(BaseAgent):
    def __init__(self, settings: AppConfig, trace=None, telemetry=None) -> None:
        super().__init__("Predictor", trace=trace, telemetry=telemetry)
        self.settings = settings

    def predict(
        self,
        request: WorkflowRequest,
        profile: CertificationProfile,
        plan: StudyPlanResult,
        engagement: EngagementResult,
    ) -> PredictionResult:
        readiness_score = self._calculate_readiness(request.practice_score, request.weekly_hours, request.meeting_hours, plan)
        pass_probability = min(95, max(0, readiness_score + (10 if request.practice_score >= profile.pass_threshold else -5)))
        risk_level = self._classify_risk(pass_probability)
        recommended_study_increase = max(0, profile.recommended_hours - plan.allocated_hours)
        expected_readiness_improvement = min(25, recommended_study_increase * 2)

        contributing_factors = [
            f"Practice score {request.practice_score}",
            f"Weekly hours {request.weekly_hours}",
            f"Meeting load {request.meeting_hours}",
            f"Study window {engagement.best_study_window}",
        ]
        explanation = (
            f"Readiness is derived from practice score, total study allocation, and workload pressure. "
            f"The current profile suggests a {risk_level.lower()} risk outcome with {pass_probability}% pass probability."
        )
        confidence = 0.91 if readiness_score >= self.settings.readiness_threshold else 0.77

        result = PredictionResult(
            readiness_score=readiness_score,
            pass_probability=pass_probability,
            risk_level=risk_level,
            recommended_study_increase=recommended_study_increase,
            expected_readiness_improvement=expected_readiness_improvement,
            contributing_factors=contributing_factors,
            explanation=explanation,
            confidence=confidence,
        )
        self._record("predict", request, result, confidence, explanation, risk_level)
        return result

    def _calculate_readiness(self, practice_score: int, weekly_hours: int, meeting_hours: int, plan: StudyPlanResult) -> int:
        pressure_penalty = max(0, meeting_hours - 12) * 1.2
        study_boost = min(30, plan.allocated_hours * 1.3)
        readiness = practice_score * 0.55 + weekly_hours * 1.2 + study_boost - pressure_penalty
        return max(0, min(100, int(round(readiness))))

    def _classify_risk(self, pass_probability: int) -> str:
        if pass_probability < self.settings.high_risk_threshold:
            return "High Risk"
        if pass_probability < self.settings.moderate_risk_threshold:
            return "Moderate Risk"
        return "Ready"
