from __future__ import annotations

from collections import Counter
from math import ceil

from core.config import AppConfig
from core.data_access import SyntheticDataRepository
from core.models import ManagerInsightBundle, PredictionResult


class ManagerInsightsEngine:
    def __init__(self, repository: SyntheticDataRepository, settings: AppConfig) -> None:
        self.repository = repository
        self.settings = settings

    def build(self) -> ManagerInsightBundle:
        learners = self.repository.load_learners()
        workloads = {row["employee_id"]: row for row in self.repository.load_workloads()}

        predictions: list[PredictionResult] = []
        for learner in learners:
            workload = workloads.get(learner["employee_id"], {})
            predicted = self._predict(
                practice_score=int(learner.get("practice_score", 0)),
                hours_studied=int(learner.get("hours_studied", 0)),
                meeting_hours=int(workload.get("meeting_hours", 0)),
                weekly_hours=max(4, int(ceil(int(learner.get("hours_studied", 0)) / 2))),
                focus_hours=int(workload.get("focus_hours", 0)),
                certification=learner.get("certification", ""),
            )
            predictions.append(predicted)

        readiness_distribution = Counter(self._bucket(pred.readiness_score) for pred in predictions)
        risk_distribution = Counter(pred.risk_level for pred in predictions)
        coverage = Counter(item["certification"] for item in learners)
        gaps = Counter(skill for item in learners for skill in item.get("weak_skills", []))
        at_risk = [learner["learner_id"] for learner, pred in zip(learners, predictions) if pred.risk_level == "High Risk"]

        readiness_pct = round(sum(pred.readiness_score for pred in predictions) / max(1, len(predictions)), 1)
        interventions = self._interventions(risk_distribution, gaps)
        pipeline = [
            {"stage": "Ready", "count": readiness_distribution.get("Ready", 0)},
            {"stage": "Watch", "count": readiness_distribution.get("Watch", 0)},
            {"stage": "At Risk", "count": readiness_distribution.get("At Risk", 0)},
        ]

        return ManagerInsightBundle(
            team_readiness_pct=readiness_pct,
            at_risk_employees=at_risk,
            readiness_distribution=dict(readiness_distribution),
            risk_distribution=dict(risk_distribution),
            certification_coverage=dict(coverage),
            skill_gap_analysis=dict(gaps),
            recommended_interventions=interventions,
            pipeline_summary=pipeline,
        )

    def _bucket(self, readiness_score: int) -> str:
        if readiness_score < self.settings.high_risk_threshold:
            return "At Risk"
        if readiness_score < self.settings.moderate_risk_threshold:
            return "Watch"
        return "Ready"

    def _predict(
        self,
        practice_score: int,
        hours_studied: int,
        meeting_hours: int,
        weekly_hours: int,
        focus_hours: int,
        certification: str,
    ) -> PredictionResult:
        readiness_score = max(
            0,
            min(100, int(round(practice_score * 0.55 + weekly_hours * 1.2 + min(30, hours_studied * 1.1) - max(0, meeting_hours - 12) * 1.2))),
        )
        pass_probability = min(95, max(0, readiness_score + (10 if practice_score >= self.settings.readiness_threshold else -5)))
        risk_level = "High Risk" if pass_probability < self.settings.high_risk_threshold else "Moderate Risk" if pass_probability < self.settings.moderate_risk_threshold else "Ready"
        recommended_study_increase = max(0, 25 - weekly_hours)
        expected_readiness_improvement = min(25, recommended_study_increase * 2)
        explanation = f"Team-level estimate for {certification} based on study hours, workload, and synthetic readiness patterns."
        return PredictionResult(
            readiness_score=readiness_score,
            pass_probability=pass_probability,
            risk_level=risk_level,
            recommended_study_increase=recommended_study_increase,
            expected_readiness_improvement=expected_readiness_improvement,
            contributing_factors=[f"Practice score {practice_score}", f"Hours studied {hours_studied}", f"Meeting load {meeting_hours}"],
            explanation=explanation,
            confidence=0.86,
        )

    def _interventions(self, risk_distribution: Counter[str], gaps: Counter[str]) -> list[str]:
        recommendations = []
        if risk_distribution.get("High Risk", 0):
            recommendations.append("Schedule manager-led coaching for high risk employees")
        if gaps:
            top_gap = gaps.most_common(1)[0][0]
            recommendations.append(f"Create a focused skill sprint for {top_gap}")
        if not recommendations:
            recommendations.append("Continue current learning cadence and monitor weekly")
        return recommendations
