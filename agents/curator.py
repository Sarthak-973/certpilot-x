from __future__ import annotations

from core.config import AppConfig
from core.data_access import SyntheticDataRepository
from core.models import CertificationProfile, CuratorResult, WorkflowRequest

from agents.base import BaseAgent


class CuratorAgent(BaseAgent):
    def __init__(self, repository: SyntheticDataRepository, settings: AppConfig, trace=None, telemetry=None) -> None:
        super().__init__("Curator", trace=trace, telemetry=telemetry)
        self.repository = repository
        self.settings = settings

    def curate(self, request: WorkflowRequest) -> tuple[CertificationProfile, CuratorResult]:
        profile = self.repository.get_profile_for(request.role, request.certification)
        if profile is None:
            profile = CertificationProfile(
                role=request.role,
                certification=request.certification,
                skills=[],
                recommended_hours=self.settings.default_weekly_hours,
                pass_threshold=self.settings.readiness_threshold,
                source="fallback",
            )
            explanation = f"No exact synthetic profile found for {request.role}; using a safe fallback pathway."
            confidence = 0.58
        else:
            explanation = (
                f"Mapped {request.role} to {profile.certification} and grounded the path in approved synthetic skills: "
                f"{', '.join(profile.skills)}."
            )
            confidence = 0.96

        result = CuratorResult(
            role=profile.role,
            certification=profile.certification,
            skills=profile.skills,
            recommended_hours=profile.recommended_hours,
            pathway=f"{profile.role} -> {profile.certification}",
            explanation=explanation,
            confidence=confidence,
        )
        self._record("curate", request, result, confidence, explanation, result.pathway)
        return profile, result
