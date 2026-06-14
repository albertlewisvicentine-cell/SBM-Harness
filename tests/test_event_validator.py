#!/usr/bin/env python3
"""Tests for event validation and registry resolution."""

import unittest

from event_validator import Event, EventValidator, ValidatedEvent


class TestEventValidator(unittest.TestCase):
    def setUp(self):
        self.registry = {
            "DefaultSubsystem": "CORE",
            "Events": {
                "SBM-001": {"Code": "SBM-001", "Name": "Started", "Subsystem": "CORE"},
                "SBM-002": {"Code": "SBM-002", "Name": "Guard Triggered"},
            },
        }
        self.validator = EventValidator(self.registry)

    def test_valid_event_with_explicit_subsystem(self):
        raw = {"code": "SBM-001", "subsystem": "CORE", "payload": {"k": "v"}}
        validated = self.validator.validate(raw)
        self.assertIsInstance(validated, ValidatedEvent)
        self.assertEqual(validated.code, "SBM-001")
        self.assertEqual(validated.subsystem, "CORE")
        self.assertEqual(validated.definition["Name"], "Started")

    def test_fallback_to_default_subsystem(self):
        validated = self.validator.validate(Event(code="SBM-002", payload={"ok": True}))
        self.assertIsInstance(validated, ValidatedEvent)
        self.assertEqual(validated.subsystem, "CORE")

    def test_invalid_code_is_logged_and_rejected(self):
        with self.assertLogs("EventValidator", level="WARNING") as logs:
            validated = self.validator.validate({"code": "SBM-999", "payload": {}})
        self.assertIsNone(validated)
        self.assertTrue(any("Unknown event code" in msg for msg in logs.output))

    def test_invalid_event_is_logged_and_rejected(self):
        with self.assertLogs("EventValidator", level="WARNING") as logs:
            validated = self.validator.validate({"subsystem": "CORE", "payload": {}})
        self.assertIsNone(validated)
        self.assertTrue(any("missing or non-string 'code'" in msg for msg in logs.output))

    def test_subsystem_mismatch_is_logged_and_rejected(self):
        with self.assertLogs("EventValidator", level="WARNING") as logs:
            validated = self.validator.validate({"code": "SBM-001", "subsystem": "IO", "payload": {}})
        self.assertIsNone(validated)
        self.assertTrue(any("Subsystem mismatch" in msg for msg in logs.output))

    def test_validated_definition_mutation_does_not_affect_registry(self):
        registry = {
            "DefaultSubsystem": "CORE",
            "Events": {
                "SBM-003": {
                    "Code": "SBM-003",
                    "Subsystem": "CORE",
                    "meta": {"tags": ["safe"]},
                }
            },
        }
        validator = EventValidator(registry)
        validated = validator.validate({"code": "SBM-003", "payload": {}})
        self.assertIsNotNone(validated)
        validated.definition["meta"]["tags"].append("mutated")
        self.assertEqual(registry["Events"]["SBM-003"]["meta"]["tags"], ["safe"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
