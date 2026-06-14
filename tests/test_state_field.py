#!/usr/bin/env python3
"""
Tests for StateField observed/expected drift tracking.
"""

import unittest

import numpy as np

from state_field import StateField


class TestStateField(unittest.TestCase):
    def test_topology_mapping_and_inject(self):
        field = StateField(["sensor", "actuator", "power"])
        field.inject("actuator", obs=3.5, exp=2.0)

        np.testing.assert_array_equal(field.observed, np.array([0.0, 3.5, 0.0]))
        np.testing.assert_array_equal(field.expected, np.array([0.0, 2.0, 0.0]))

    def test_get_drift_outputs_delta_field(self):
        field = StateField(["a", "b"])
        field.inject("a", obs=6.0, exp=4.0)
        field.inject("b", obs=1.0, exp=3.0)

        np.testing.assert_array_equal(field.get_drift(), np.array([2.0, -2.0]))

    def test_get_normalized_drift(self):
        field = StateField(["a", "b"])
        field.inject("a", obs=12.0, exp=6.0)
        field.inject("b", obs=1.0, exp=0.0)

        normalized = field.get_normalized_drift()
        self.assertAlmostEqual(normalized[0], 1.0)
        self.assertGreater(normalized[1], 1e11)

    def test_decay_applies_natural_decay_to_fields(self):
        field = StateField(["x", "y"], decay_factor=0.5)
        field.inject("x", obs=10.0, exp=4.0)
        field.inject("y", obs=6.0, exp=2.0)

        field.decay()

        np.testing.assert_array_equal(field.observed, np.array([5.0, 3.0]))
        np.testing.assert_array_equal(field.expected, np.array([2.0, 1.0]))
        np.testing.assert_array_equal(field.get_drift(), np.array([3.0, 2.0]))

    def test_unknown_subsystem_rejected(self):
        field = StateField(["known"])
        with self.assertRaises(KeyError):
            field.inject("unknown", obs=1.0, exp=1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
