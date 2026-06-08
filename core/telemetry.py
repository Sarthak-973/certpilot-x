from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from core.logging import get_logger


class TelemetrySink(Protocol):
    def track_event(self, event_name: str, properties: dict[str, Any] | None = None) -> None: ...


@dataclass
class NullTelemetrySink:
    def track_event(self, event_name: str, properties: dict[str, Any] | None = None) -> None:
        return None


@dataclass
class ConsoleTelemetrySink:
    logger_name: str = "certpilot.telemetry"

    def __post_init__(self) -> None:
        self.logger = get_logger(self.logger_name)

    def track_event(self, event_name: str, properties: dict[str, Any] | None = None) -> None:
        self.logger.info("telemetry_event=%s properties=%s", event_name, properties or {})
