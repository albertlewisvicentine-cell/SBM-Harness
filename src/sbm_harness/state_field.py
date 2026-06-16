#!/usr/bin/env python3
"""
StateField numerical core for observed/expected integrity tracking.
"""

from __future__ import annotations

from typing import Iterable, Mapping

import numpy as np


class StateField:
    """Tracks observed/expected state vectors and computes drift."""

    def __init__(self, topology: Iterable[str] | Mapping[str, int], decay_factor: float = 0.98):
        if not 0.0 <= decay_factor <= 1.0:
            raise ValueError("decay_factor must be within [0.0, 1.0]")

        if isinstance(topology, Mapping):
            self._topology = dict(topology)
            size = len(self._topology)
        else:
            names = list(topology)
            self._topology = {name: i for i, name in enumerate(names)}
            size = len(names)

        if size == 0:
            raise ValueError("topology must define at least one subsystem")

        self.decay_factor = float(decay_factor)
        self.observed = np.zeros(size, dtype=np.float64)
        self.expected = np.zeros(size, dtype=np.float64)

    def inject(self, subsystem: str, obs: float, exp: float) -> None:
        """Inject observed/expected values for a subsystem."""
        if subsystem not in self._topology:
            raise KeyError(f"unknown subsystem '{subsystem}'")
        idx = self._topology[subsystem]
        self.observed[idx] = float(obs)
        self.expected[idx] = float(exp)

    def decay(self) -> None:
        """Apply natural decay to observed and expected fields."""
        self.observed *= self.decay_factor
        self.expected *= self.decay_factor

    def get_drift(self) -> np.ndarray:
        """Return raw drift field: u_observed - u_expected."""
        return self.observed - self.expected

    def get_normalized_drift(self, epsilon: float = 1e-12) -> np.ndarray:
        """Return drift normalized by expected magnitude."""
        denom = np.maximum(np.abs(self.expected), epsilon)
        return self.get_drift() / denom
