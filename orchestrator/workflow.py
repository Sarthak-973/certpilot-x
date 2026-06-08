from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from typing import Any

from agents.critic import CriticAgent
from agents.curator import CuratorAgent
from agents.engagement import EngagementAgent
from agents.planner import PlannerAgent
from agents.predictor import PredictorAgent
from core.config import AppConfig, load_settings
from core.data_access import SyntheticDataRepository
from core.logging import get_logger
from core.models import ManagerInsightBundle, WorkflowRequest, WorkflowResult
from core.telemetry import ConsoleTelemetrySink, TelemetrySink
from core.tracing import WorkflowAuditTrail
from core.validators import validate_request
from orchestrator.manager_insights import ManagerInsightsEngine


class CertificationWorkflowOrchestrator:
    """Coordinates the five-agent workflow and keeps an audit trail."""

    def __init__(
        self,
        repository: SyntheticDataRepository | None = None,
        settings: AppConfig | None = None,
        telemetry: TelemetrySink | None = None,
    ) -> None:
        self.settings = settings or load_settings()
        self.repository = repository or SyntheticDataRepository(self.settings)
        self.telemetry = telemetry or ConsoleTelemetrySink()
        self.logger = get_logger("certpilot.orchestrator")
        self.manager_insights_engine = ManagerInsightsEngine(self.repository, self.settings)

    def execute(self, request: WorkflowRequest) -> WorkflowResult:
        validate_request(request, self.settings)
        trace = WorkflowAuditTrail()
        pipeline = self._run_pipeline(request=request, trace=trace)
        team_bundle = self.manager_insights_engine.build()
        result = WorkflowResult(
            request=request,
            curator=pipeline["curator"],
            study_plan=pipeline["study_plan"],
            engagement=pipeline["engagement"],
            prediction=pipeline["prediction"],
            critic=pipeline["critic"],
            manager_insights=team_bundle,
            trace=trace.steps,
            workflow_id=trace.workflow_id,
            audit_summary=self._summarize(trace.steps),
            self_reflection=pipeline["critic"].self_reflection + pipeline["self_reflection"],
        )
        self.logger.info("workflow_complete workflow_id=%s learner_id=%s", result.workflow_id, request.learner_id)
        return result

    def analyze_team(self) -> tuple[list[WorkflowResult], ManagerInsightBundle]:
        learners = self.repository.load_learners()
        workloads = {row["employee_id"]: row for row in self.repository.load_workloads()}
        team_results: list[WorkflowResult] = []

        for learner in learners:
            workload = workloads.get(learner["employee_id"], {})
            exam_date = (date.today() + timedelta(days=self.settings.default_exam_days)).isoformat()
            request = WorkflowRequest(
                learner_id=learner["learner_id"],
                role=learner["role"],
                certification=learner["certification"],
                weekly_hours=min(self.settings.default_weekly_hours, max(4, int(learner.get("hours_studied", 10) / 2))),
                practice_score=int(learner.get("practice_score", self.settings.default_practice_score)),
                meeting_hours=int(workload.get("meeting_hours", self.settings.default_meeting_hours)),
                focus_hours=int(workload.get("focus_hours", self.settings.default_focus_hours)),
                exam_date=exam_date,
            )
            team_results.append(self._run_single(request))

        return team_results, self.manager_insights_engine.build()

    def _run_single(self, request: WorkflowRequest) -> WorkflowResult:
        validate_request(request, self.settings)
        trace = WorkflowAuditTrail()
        pipeline = self._run_pipeline(request=request, trace=trace)
        return WorkflowResult(
            request=request,
            curator=pipeline["curator"],
            study_plan=pipeline["study_plan"],
            engagement=pipeline["engagement"],
            prediction=pipeline["prediction"],
            critic=pipeline["critic"],
            manager_insights=self.manager_insights_engine.build(),
            trace=trace.steps,
            workflow_id=trace.workflow_id,
            audit_summary=self._summarize(trace.steps),
            self_reflection=pipeline["critic"].self_reflection + pipeline["self_reflection"],
        )

    def _run_pipeline(
        self,
        request: WorkflowRequest,
        trace: WorkflowAuditTrail | None,
    ) -> dict[str, Any]:
        curator = CuratorAgent(self.repository, self.settings, trace=trace, telemetry=self.telemetry)
        planner = PlannerAgent(self.settings, trace=trace, telemetry=self.telemetry)
        engagement = EngagementAgent(self.settings, trace=trace, telemetry=self.telemetry)
        predictor = PredictorAgent(self.settings, trace=trace, telemetry=self.telemetry)
        critic = CriticAgent(self.settings, trace=trace, telemetry=self.telemetry)

        profile, curator_result = curator.curate(request)
        engagement_result = engagement.recommend_window(request)
        study_plan = planner.generate_plan(request, profile, engagement_result.best_study_window)
        prediction = predictor.predict(request, profile, study_plan, engagement_result)
        critic_result = critic.review(request, study_plan, engagement_result, prediction, has_prerequisites=bool(profile.skills))

        self_reflection: list[str] = []
        if critic_result.verdict != "Ready" and study_plan.recommended_study_increase > 0:
            adjusted_weekly_hours = min(self.settings.max_weekly_hours, request.weekly_hours + 2)
            if adjusted_weekly_hours > request.weekly_hours:
                self_reflection.append(
                    f"Planner-Executor loop increased weekly study hours from {request.weekly_hours} to {adjusted_weekly_hours}."
                )
                adjusted_request = replace(request, weekly_hours=adjusted_weekly_hours)
                engagement_result = engagement.recommend_window(adjusted_request)
                study_plan = planner.generate_plan(adjusted_request, profile, engagement_result.best_study_window)
                prediction = predictor.predict(adjusted_request, profile, study_plan, engagement_result)
                critic_result = critic.review(
                    adjusted_request,
                    study_plan,
                    engagement_result,
                    prediction,
                    has_prerequisites=bool(profile.skills),
                )

        return {
            "curator": curator_result,
            "study_plan": study_plan,
            "engagement": engagement_result,
            "prediction": prediction,
            "critic": critic_result,
            "self_reflection": self_reflection,
        }

    def _summarize(self, steps: list[Any]) -> str:
        if not steps:
            return "No reasoning trace captured."
        actions = [f"{step.agent}:{step.action}" for step in steps]
        return " -> ".join(actions)


def run_workflow(role: str, certification: str, weekly_hours: int, practice_score: int, meeting_hours: int, focus_hours: int, exam_date: str) -> WorkflowResult:
    orchestrator = CertificationWorkflowOrchestrator()
    request = WorkflowRequest(
        learner_id="L-UI-001",
        role=role,
        certification=certification,
        weekly_hours=weekly_hours,
        practice_score=practice_score,
        meeting_hours=meeting_hours,
        focus_hours=focus_hours,
        exam_date=exam_date,
    )
    return orchestrator.execute(request)
