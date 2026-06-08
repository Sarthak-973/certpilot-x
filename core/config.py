from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "CertPilot X"
    app_tagline: str = "Enterprise certification intelligence for reasoning agents demos."
    data_dir: Path = Path(__file__).resolve().parents[1] / "data"
    knowledge_dir: Path = Path(__file__).resolve().parents[1] / "knowledge"
    default_role: str = "Data Engineer"
    default_certification: str = "DP-203"
    default_weekly_hours: int = 10
    default_practice_score: int = 72
    default_meeting_hours: int = 18
    default_focus_hours: int = 15
    default_exam_days: int = 42
    readiness_threshold: int = 75
    high_risk_threshold: int = 60
    moderate_risk_threshold: int = 80
    minimum_confidence: float = 0.7
    min_weekly_hours: int = 1
    max_weekly_hours: int = 20
    max_weekly_commitment_hours: int = 40
    foundry_project_endpoint: str | None = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    foundry_model_deployment: str = os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")
    workspace_name: str = "CertPilot X"

    @property
    def certifications_path(self) -> Path:
        return self.data_dir / "certifications.json"

    @property
    def learners_path(self) -> Path:
        return self.data_dir / "learners.json"

    @property
    def workload_path(self) -> Path:
        return self.data_dir / "workload.json"

    @property
    def test_cases_path(self) -> Path:
        return self.data_dir / "test_cases.json"


@lru_cache(maxsize=1)
def load_settings() -> AppConfig:
    return AppConfig()
