"""
Registry runtime model.

Defines the RegistryEntry dataclass and the Registry container used by the
SBM-Harness fault-registry subsystem.  This module is intentionally decoupled
from all renderer, loader, and state-machine logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class RegistryEntry:
    """Immutable record representing a single fault-registry entry."""

    code: str
    category: str
    severity: str
    diffusion_weight: float
    recovery_weight: float
    expected_baseline: float
    default_subsystem: str
    description: str


class Registry:
    """
    Container for a collection of :class:`RegistryEntry` objects, keyed by code.

    Entries are stored in insertion order and looked up by their *code* field.
    """

    def __init__(self, entries: list[RegistryEntry]) -> None:
        self._entries: dict[str, RegistryEntry] = {}
        for entry in entries:
            if entry.code in self._entries:
                raise ValueError(f"Duplicate registry code: {entry.code!r}")
            self._entries[entry.code] = entry

    # ------------------------------------------------------------------
    # Mapping-like interface
    # ------------------------------------------------------------------

    def __getitem__(self, code: str) -> RegistryEntry:
        return self._entries[code]

    def __contains__(self, code: object) -> bool:
        return code in self._entries

    def __iter__(self) -> Iterator[str]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def get(self, code: str, default: RegistryEntry | None = None) -> RegistryEntry | None:
        return self._entries.get(code, default)

    @property
    def codes(self) -> list[str]:
        """Return an ordered list of all entry codes."""
        return list(self._entries)

    def entries(self) -> list[RegistryEntry]:
        """Return all entries in insertion order."""
        return list(self._entries.values())

    def __repr__(self) -> str:  # pragma: no cover
        return f"Registry({len(self)} entries)"
