from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


class SerializableModel:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CertificationProfile(SerializableModel):
    role: str
    certification: str
    skills: list[str]
    recommended_hours: int
    pass_threshold: int = 75
    source: str = "synthetic"


@dataclass(frozen=True)
class WorkflowRequest(SerializableModel):
    learner_id: str
    role: str
    certification: str
    weekly_hours: int
    practice_score: int
    meeting_hours: int
    focus_hours: int
    exam_date: str


@dataclass(frozen=True)
class StudyPlanWeek(SerializableModel):
    week: int
    hours: int
    focus: str
    activities: list[str]


@dataclass(frozen=True)
class CuratorResult(SerializableModel):
    role: str
    certification: str
    skills: list[str]
    recommended_hours: int
    pathway: str
    explanation: str
    confidence: float


@dataclass(frozen=True)
class StudyPlanResult(SerializableModel):
    weeks: list[StudyPlanWeek]
    total_weeks: int
    recommended_hours: int
    allocated_hours: int
    recommended_study_increase: int
    plan_summary: str
    confidence: float


@dataclass(frozen=True)
class EngagementResult(SerializableModel):
    best_study_window: str
    study_windows: list[str]
    workload_band: str
    explanation: str
    confidence: float


@dataclass(frozen=True)
class PredictionResult(SerializableModel):
    readiness_score: int
    pass_probability: int
    risk_level: str
    recommended_study_increase: int
    expected_readiness_improvement: int
    contributing_factors: list[str]
    explanation: str
    confidence: float


@dataclass(frozen=True)
class CriticReviewResult(SerializableModel):
    verdict: str
    issues: list[str]
    warnings: list[str]
    confidence: float
    self_reflection: list[str]
    explanation: str


@dataclass(frozen=True)
class ManagerInsightBundle(SerializableModel):
    team_readiness_pct: float
    at_risk_employees: list[str]
    readiness_distribution: dict[str, int]
    risk_distribution: dict[str, int]
    certification_coverage: dict[str, int]
    skill_gap_analysis: dict[str, int]
    recommended_interventions: list[str]
    pipeline_summary: list[dict[str, Any]]


@dataclass(frozen=True)
class TraceStep(SerializableModel):
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")
    agent: str = ""
    action: str = ""
    inputs: Any = None
    outputs: Any = None
    confidence: float = 0.0
    rationale: str = ""
    decision: str = ""


@dataclass(frozen=True)
class WorkflowResult(SerializableModel):
    request: WorkflowRequest
    curator: CuratorResult
    study_plan: StudyPlanResult
    engagement: EngagementResult
    prediction: PredictionResult
    critic: CriticReviewResult
    manager_insights: ManagerInsightBundle
    trace: list[TraceStep]
    workflow_id: str
    audit_summary: str
    self_reflection: list[str]


@dataclass(frozen=True)
class EvaluationCase(SerializableModel):
    learner_id: str
    role: str
    certification: str
    practice_score: int
    weekly_hours: int
    meeting_hours: int
    focus_hours: int
    expected_risk: str


@dataclass(frozen=True)
class EvaluationReport(SerializableModel):
    total_cases: int
    pass_rate: float
    average_confidence: float
    average_readiness: float
    issues_found: int
    notes: list[str]
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")
