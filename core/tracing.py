from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from core.models import TraceStep


@dataclass
class WorkflowAuditTrail:
    workflow_id: str = field(default_factory=lambda: str(uuid4()))
    steps: list[TraceStep] = field(default_factory=list)

    def record(
        self,
        agent: str,
        action: str,
        inputs: Any,
        outputs: Any,
        confidence: float,
        rationale: str,
        decision: str,
    ) -> TraceStep:
        step = TraceStep(
            agent=agent,
            action=action,
            inputs=inputs,
            outputs=outputs,
            confidence=confidence,
            rationale=rationale,
            decision=decision,
        )
        self.steps.append(step)
        return step

    def to_dict(self) -> list[dict[str, Any]]:
        return [step.to_dict() for step in self.steps]
