"""
Bug-reporting widget with smart defaults and context awareness.

Features
--------
Predictive Context Extraction
    On initialisation the widget automatically captures the current page URL,
    active user-session flags, hardware environment variables, and the last
    three lines stored in the console-error buffer.

Intelligent History Autofill
    Standard report fields are pre-filled with the most recently successful
    submission values kept in a :class:`HistoryStore`.  Fields explicitly
    provided by the caller are never overwritten.
"""

from __future__ import annotations

import os
import platform
from collections import deque
from typing import Any, Deque, Dict, List, Optional

# ---------------------------------------------------------------------------
# Module-level console-error ring buffer (capped at three entries)
# ---------------------------------------------------------------------------
_CONSOLE_ERROR_BUFFER: Deque[str] = deque(maxlen=3)

# Environment-variable classification constants
_SESSION_ENV_KEYS: frozenset[str] = frozenset(
    {"SESSION", "USER", "USERNAME", "LOGNAME", "HOME", "SHELL"}
)
_HARDWARE_ENV_PREFIXES: tuple[str, ...] = (
    "CPU",
    "MEM",
    "GPU",
    "PROCESSOR",
    "HARDWARE",
    "NUMBER_OF_PROCESSORS",
)


# ---------------------------------------------------------------------------
# ContextCollector
# ---------------------------------------------------------------------------


class ContextCollector:
    """Scrapes system-state metadata at initialisation time.

    Captures:

    * ``url`` – current page/request URL extracted from the process environment.
    * ``session_flags`` – environment variables that describe the active user
      session (``USER``, ``SESSION``, ``LOGNAME``, etc.).
    * ``hardware_env`` – environment variables and ``platform.uname()`` fields
      that describe the hardware environment.
    * ``console_errors`` – up to the last three entries from the module-level
      console-error ring buffer populated via
      :meth:`BugReportWidget.record_console_error`.
    """

    def __init__(self) -> None:
        self.url: str = self._extract_url()
        self.session_flags: Dict[str, str] = self._extract_session_flags()
        self.hardware_env: Dict[str, str] = self._extract_hardware_env()
        self.console_errors: List[str] = list(_CONSOLE_ERROR_BUFFER)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_url() -> str:
        """Return the page/request URL from the process environment."""
        for var in ("REQUEST_URL", "URL", "SCRIPT_URI"):
            val = os.environ.get(var)
            if val:
                return val
        return ""

    @staticmethod
    def _extract_session_flags() -> Dict[str, str]:
        """Return session-related environment variables."""
        return {
            key: val
            for key, val in os.environ.items()
            if key.upper() in _SESSION_ENV_KEYS
            or any(key.upper().startswith(s) for s in _SESSION_ENV_KEYS)
        }

    @staticmethod
    def _extract_hardware_env() -> Dict[str, str]:
        """Return hardware-related environment variables and platform fields."""
        hardware: Dict[str, str] = {
            key: val
            for key, val in os.environ.items()
            if any(key.upper().startswith(p) for p in _HARDWARE_ENV_PREFIXES)
        }
        uname = platform.uname()
        hardware.setdefault("PLATFORM_MACHINE", uname.machine)
        hardware.setdefault("PLATFORM_PROCESSOR", uname.processor)
        hardware.setdefault("PLATFORM_SYSTEM", uname.system)
        return hardware

    def to_dict(self) -> Dict[str, Any]:
        """Serialise captured context to a plain dictionary."""
        return {
            "url": self.url,
            "session_flags": dict(self.session_flags),
            "hardware_env": dict(self.hardware_env),
            "console_errors": list(self.console_errors),
        }


# ---------------------------------------------------------------------------
# HistoryStore
# ---------------------------------------------------------------------------


class HistoryStore:
    """In-memory store for successful bug-report field submissions.

    Values are kept in insertion order per field name.  The most recently
    recorded value is returned first by :meth:`best_value_for`.  Duplicate
    values are de-duplicated: a re-submitted value is moved to the end of its
    field bucket so it remains the "most recent".
    """

    def __init__(self) -> None:
        self._history: Dict[str, List[Any]] = {}

    def record(self, fields: Dict[str, Any]) -> None:
        """Persist a submitted set of field values to history.

        ``None`` values are silently ignored so that unfilled fields do not
        pollute future autofill suggestions.
        """
        for field, value in fields.items():
            if value is None:
                continue
            bucket = self._history.setdefault(field, [])
            if value in bucket:
                bucket.remove(value)
            bucket.append(value)

    def best_value_for(self, field: str) -> Optional[Any]:
        """Return the most recently recorded value for *field*, or ``None``."""
        bucket = self._history.get(field)
        return bucket[-1] if bucket else None

    def autofill(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Return a copy of *fields* with ``None`` values replaced by history.

        Only fields whose current value is ``None`` are overwritten; any
        explicitly supplied value is left unchanged.
        """
        return {
            field: (value if value is not None else self.best_value_for(field))
            for field, value in fields.items()
        }

    def clear(self) -> None:
        """Remove all stored submission history."""
        self._history.clear()


# ---------------------------------------------------------------------------
# BugReportWidget
# ---------------------------------------------------------------------------


class BugReportWidget:
    """Smart bug-reporting widget with context awareness and history autofill.

    On construction the widget:

    1. Runs :class:`ContextCollector` to capture the page URL, session flags,
       hardware environment variables, and the last three console-error lines.
    2. Merges caller-supplied *fields* with the set of standard default fields
       (``title``, ``description``, ``component``, ``severity``,
       ``reporter``), then autofills any ``None`` values from *history_store*.

    Parameters
    ----------
    fields:
        Initial field values.  Any field left as ``None`` (or absent from this
        mapping) will be autofilled from history.
    history_store:
        Optional shared :class:`HistoryStore`.  Pass an explicit instance to
        share submission history across widget instances within a session.
        When omitted a new, empty store is created.
    """

    _DEFAULT_FIELDS: tuple[str, ...] = (
        "title",
        "description",
        "component",
        "severity",
        "reporter",
    )

    def __init__(
        self,
        fields: Optional[Dict[str, Any]] = None,
        *,
        history_store: Optional[HistoryStore] = None,
    ) -> None:
        self.context: ContextCollector = ContextCollector()
        self.history: HistoryStore = (
            history_store if history_store is not None else HistoryStore()
        )

        # Build the field map: defaults → caller overrides → history autofill
        base: Dict[str, Any] = {f: None for f in self._DEFAULT_FIELDS}
        if fields:
            base.update(fields)
        self.fields: Dict[str, Any] = self.history.autofill(base)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_field(self, name: str, value: Any) -> None:
        """Set or overwrite a single field value before submitting."""
        self.fields[name] = value

    def submit(self, extra_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Finalise the report and persist field values to history.

        Returns the full report payload, which includes both the field values
        and the context captured at widget initialisation.

        Parameters
        ----------
        extra_fields:
            Additional fields to merge into the payload before submission.
            These are also persisted to history.
        """
        payload: Dict[str, Any] = dict(self.fields)
        if extra_fields:
            payload.update(extra_fields)

        self.history.record({k: v for k, v in payload.items() if v is not None})

        return {
            "fields": payload,
            "context": self.context.to_dict(),
        }

    # ------------------------------------------------------------------
    # Console-error buffer helpers (static so they can be called without
    # an instance, matching a typical global logger pattern)
    # ------------------------------------------------------------------

    @staticmethod
    def record_console_error(message: str) -> None:
        """Append *message* to the global console-error buffer.

        The buffer is capped at the three most recent entries.  Call this from
        your exception handler or logging hook so that :class:`ContextCollector`
        captures the relevant errors on the next widget initialisation.
        """
        _CONSOLE_ERROR_BUFFER.append(message)

    @staticmethod
    def clear_console_errors() -> None:
        """Flush the global console-error buffer."""
        _CONSOLE_ERROR_BUFFER.clear()
