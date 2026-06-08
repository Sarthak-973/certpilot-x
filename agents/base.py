from __future__ import annotations

from dataclasses import asdict
from typing import Any

from core.logging import get_logger
from core.telemetry import NullTelemetrySink, TelemetrySink
from core.tracing import WorkflowAuditTrail


class BaseAgent:
    """Shared behaviour for all CertPilot agents."""

    def __init__(self, name: str, trace: WorkflowAuditTrail | None = None, telemetry: TelemetrySink | None = None) -> None:
        self.name = name
        self.trace = trace
        self.telemetry = telemetry or NullTelemetrySink()
        self.logger = get_logger(f"certpilot.{name.lower()}")

    def _record(self, action: str, inputs: Any, outputs: Any, confidence: float, rationale: str, decision: str) -> None:
        payload = {
            "agent": self.name,
            "action": action,
            "inputs": self._safe(inputs),
            "outputs": self._safe(outputs),
            "confidence": confidence,
            "rationale": rationale,
            "decision": decision,
        }
        self.logger.info("%s", payload)
        self.telemetry.track_event(f"{self.name}.{action}", payload)
        if self.trace is not None:
            self.trace.record(
                agent=self.name,
                action=action,
                inputs=inputs,
                outputs=outputs,
                confidence=confidence,
                rationale=rationale,
                decision=decision,
            )

    def _safe(self, value: Any) -> Any:
        if hasattr(value, "to_dict"):
            return value.to_dict()
        if hasattr(value, "__dataclass_fields__"):
            return asdict(value)
        return value
