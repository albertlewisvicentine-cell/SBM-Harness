#!/usr/bin/env python3
"""Runtime event validation against a registry container."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional


@dataclass(frozen=True)
class Event:
    """Raw runtime event input."""

    code: str
    subsystem: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidatedEvent:
    """Typed output after successful registry validation."""

    code: str
    subsystem: str
    payload: Dict[str, Any]
    definition: Dict[str, Any]


class EventValidator:
    """Validate and resolve events against a registry container."""

    def __init__(self, registry: Mapping[str, Any], logger: Optional[logging.Logger] = None):
        self.registry = registry
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def validate(self, raw_event: Mapping[str, Any] | Event) -> Optional[ValidatedEvent]:
        """Validate a raw event and return a resolved validated event."""
        event = self._coerce_event(raw_event)
        if event is None:
            return None

        subsystem = event.subsystem or self.registry.get("DefaultSubsystem")
        if not subsystem:
            self.logger.warning("Missing subsystem and no Registry DefaultSubsystem for code=%s", event.code)
            return None

        definition = self._resolve_definition(event.code)
        if definition is None:
            self.logger.warning("Unknown event code '%s'", event.code)
            return None

        allowed_subsystem = definition.get("Subsystem") or definition.get("subsystem")
        if allowed_subsystem and allowed_subsystem != subsystem:
            self.logger.warning(
                "Subsystem mismatch for code=%s (event=%s, registry=%s)",
                event.code,
                subsystem,
                allowed_subsystem,
            )
            return None

        return ValidatedEvent(
            code=event.code,
            subsystem=subsystem,
            payload=event.payload,
            definition=definition,
        )

    def _coerce_event(self, raw_event: Mapping[str, Any] | Event) -> Optional[Event]:
        if isinstance(raw_event, Event):
            return raw_event
        if not isinstance(raw_event, Mapping):
            self.logger.warning("Invalid event payload type: %s", type(raw_event).__name__)
            return None

        code = raw_event.get("code")
        if not isinstance(code, str) or not code.strip():
            self.logger.warning("Invalid event: missing or non-string 'code'")
            return None

        subsystem = raw_event.get("subsystem")
        if subsystem is not None and not isinstance(subsystem, str):
            self.logger.warning("Invalid event: non-string 'subsystem' for code=%s", code)
            return None

        payload = raw_event.get("payload", {})
        if not isinstance(payload, dict):
            self.logger.warning("Invalid event: non-object 'payload' for code=%s", code)
            return None

        return Event(code=code, subsystem=subsystem, payload=payload)

    def _resolve_definition(self, code: str) -> Optional[Dict[str, Any]]:
        events = self.registry.get("Events", {})
        if isinstance(events, Mapping):
            definition = events.get(code)
            if isinstance(definition, Mapping):
                return dict(definition)
            return None

        if isinstance(events, list):
            for item in events:
                if isinstance(item, Mapping) and item.get("Code") == code:
                    return dict(item)
                if isinstance(item, Mapping) and item.get("code") == code:
                    return dict(item)
        return None
