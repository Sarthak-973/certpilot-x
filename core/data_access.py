from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.config import AppConfig, load_settings
from core.logging import get_logger
from core.models import CertificationProfile, EvaluationCase


class DataRepositoryError(RuntimeError):
    pass


@dataclass
class SyntheticDataRepository:
    settings: AppConfig = field(default_factory=load_settings)

    def __post_init__(self) -> None:
        self.logger = get_logger("certpilot.data")

    def _read_json(self, path: Path) -> Any:
        try:
            with path.open(encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError as exc:
            raise DataRepositoryError(f"Missing synthetic data file: {path}") from exc
        except json.JSONDecodeError as exc:
            raise DataRepositoryError(f"Invalid JSON in synthetic data file: {path}") from exc

    def load_certification_profiles(self) -> list[CertificationProfile]:
        raw_profiles = self._read_json(self.settings.certifications_path)
        profiles: list[CertificationProfile] = []
        for item in raw_profiles:
            profiles.append(
                CertificationProfile(
                    role=item["role"],
                    certification=item["certification"],
                    skills=list(item.get("skills", [])),
                    recommended_hours=int(item.get("recommended_hours", 0)),
                    pass_threshold=int(item.get("pass_threshold", self.settings.readiness_threshold)),
                )
            )
        return profiles

    def load_learners(self) -> list[dict[str, Any]]:
        return list(self._read_json(self.settings.learners_path))

    def load_workloads(self) -> list[dict[str, Any]]:
        return list(self._read_json(self.settings.workload_path))

    def load_test_cases(self) -> list[EvaluationCase]:
        if not self.settings.test_cases_path.exists():
            return []

        raw_cases = self._read_json(self.settings.test_cases_path)
        return [EvaluationCase(**case) for case in raw_cases]

    def get_profile_for(self, role: str, certification: str | None = None) -> CertificationProfile | None:
        for profile in self.load_certification_profiles():
            if profile.role == role and (certification is None or profile.certification == certification):
                return profile
        return None
