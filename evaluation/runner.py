from __future__ import annotations

from datetime import date, timedelta

from core.config import AppConfig
from core.data_access import SyntheticDataRepository
from core.models import EvaluationReport, WorkflowRequest
from orchestrator.workflow import CertificationWorkflowOrchestrator


class EvaluationRunner:
    def __init__(self, orchestrator: CertificationWorkflowOrchestrator, repository: SyntheticDataRepository, settings: AppConfig) -> None:
        self.orchestrator = orchestrator
        self.repository = repository
        self.settings = settings

    def run(self) -> EvaluationReport:
        cases = self.repository.load_test_cases()
        if not cases:
            return EvaluationReport(
                total_cases=0,
                pass_rate=0.0,
                average_confidence=0.0,
                average_readiness=0.0,
                issues_found=0,
                notes=["No test cases available in data/test_cases.json"],
            )

        results = []
        notes: list[str] = []
        for case in cases:
            request = WorkflowRequest(
                learner_id=case.learner_id,
                role=case.role,
                certification=case.certification,
                weekly_hours=case.weekly_hours,
                practice_score=case.practice_score,
                meeting_hours=case.meeting_hours,
                focus_hours=case.focus_hours,
                exam_date=(date.today() + timedelta(days=42)).isoformat(),
            )
            result = self.orchestrator.execute(request)
            results.append(result)
            if result.critic.issues:
                notes.append(f"{case.learner_id}: {', '.join(result.critic.issues)}")

        pass_rate = round(sum(1 for item in results if item.prediction.pass_probability >= self.settings.readiness_threshold) / len(results) * 100, 1)
        average_confidence = round(sum(item.critic.confidence for item in results) / len(results), 2)
        average_readiness = round(sum(item.prediction.readiness_score for item in results) / len(results), 1)
        issues_found = sum(len(item.critic.issues) for item in results)

        return EvaluationReport(
            total_cases=len(results),
            pass_rate=pass_rate,
            average_confidence=average_confidence,
            average_readiness=average_readiness,
            issues_found=issues_found,
            notes=notes or ["All synthetic test cases passed critic validation"],
        )
