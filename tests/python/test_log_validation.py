#!/usr/bin/env python3
"""
Tests for SBM log schema validation.
"""

import unittest
import json
import tempfile
from pathlib import Path
from jsonschema import ValidationError
from sbm_log_validator import SBMLogValidator, validate_log_entries


class TestSBMLogValidator(unittest.TestCase):
    """Test cases for SBM log validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SBMLogValidator()
    
    def test_valid_fault_injection_entry(self):
        """Test validation of a valid fault injection entry."""
        entry = {
            "schema_version": "1.0",
            "event_type": "FAULT_INJECTION",
            "timestamp": "2026-01-25T19:30:42.123Z",
            "seed": 123456,
            "gsn_ref": ["G2", "G6"],
            "fault_id": "FI-001",
            "description": "Array bounds overflow injection",
            "outcome": "DETECTED_AND_RECOVERED",
            "severity": "critical"
        }
        
        # Should not raise
        self.assertTrue(self.validator.validate_entry(entry))
    
    def test_valid_guard_trigger_entry(self):
        """Test validation of a valid guard trigger entry."""
        entry = {
            "schema_version": "1.0",
            "event_type": "GUARD_TRIGGER",
            "timestamp": "2026-01-25T19:30:42.124Z",
            "seed": 123456,
            "gsn_ref": ["G2"],
            "guard_type": "GUARD_INDEX",
            "outcome": "DETECTED_AND_RECOVERED"
        }
        
        self.assertTrue(self.validator.validate_entry(entry))
    
    def test_missing_required_field(self):
        """Test that missing required fields are caught."""
        entry = {
            "schema_version": "1.0",
            # Missing event_type
            "timestamp": "2026-01-25T19:30:42.123Z"
        }
        
        with self.assertRaises(ValidationError):
            self.validator.validate_entry(entry)
    
    def test_invalid_event_type(self):
        """Test that invalid event types are rejected."""
        entry = {
            "schema_version": "1.0",
            "event_type": "INVALID_TYPE",
            "timestamp": "2026-01-25T19:30:42.123Z"
        }
        
        with self.assertRaises(ValidationError):
            self.validator.validate_entry(entry)
    
    def test_invalid_outcome(self):
        """Test that invalid outcomes are rejected."""
        entry = {
            "schema_version": "1.0",
            "event_type": "FAULT_INJECTION",
            "timestamp": "2026-01-25T19:30:42.123Z",
            "outcome": "INVALID_OUTCOME"
        }
        
        with self.assertRaises(ValidationError):
            self.validator.validate_entry(entry)
    
    def test_seed_field_validation(self):
        """Test seed field validation."""
        # Valid seed
        entry_valid = {
            "schema_version": "1.0",
            "event_type": "FAULT_INJECTION",
            "timestamp": "2026-01-25T19:30:42.123Z",
            "seed": 42
        }
        self.assertTrue(self.validator.validate_entry(entry_valid))
        
        # Negative seed should be rejected
        entry_negative = {
            "schema_version": "1.0",
            "event_type": "FAULT_INJECTION",
            "timestamp": "2026-01-25T19:30:42.123Z",
            "seed": -1
        }
        with self.assertRaises(ValidationError):
            self.validator.validate_entry(entry_negative)
    
    def test_schema_version_check(self):
        """Test schema version compatibility check."""
        entry_v1 = {
            "schema_version": "1.0",
            "event_type": "FAULT_INJECTION",
            "timestamp": "2026-01-25T19:30:42.123Z"
        }
        
        self.assertTrue(self.validator.check_schema_version(entry_v1))
        
        entry_old = {
            "schema_version": "0.9",
            "event_type": "FAULT_INJECTION",
            "timestamp": "2026-01-25T19:30:42.123Z"
        }
        
        self.assertFalse(self.validator.check_schema_version(entry_old))
    
    def test_add_schema_version(self):
        """Test adding schema version to entries."""
        entry = {
            "event_type": "FAULT_INJECTION",
            "timestamp": "2026-01-25T19:30:42.123Z"
        }
        
        updated = self.validator.add_schema_version(entry)
        
        self.assertIn("schema_version", updated)
        self.assertEqual(updated["schema_version"], "1.0")
    
    def test_validate_log_file_json_array(self):
        """Test validation of JSON array log file."""
        logs = [
            {
                "schema_version": "1.0",
                "event_type": "FAULT_INJECTION",
                "timestamp": "2026-01-25T19:30:42.123Z",
                "seed": 123
            },
            {
                "schema_version": "1.0",
                "event_type": "GUARD_TRIGGER",
                "timestamp": "2026-01-25T19:30:42.124Z",
                "seed": 123
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(logs, f)
            temp_path = Path(f.name)
        
        try:
            valid_count, errors = self.validator.validate_log_file(temp_path)
            self.assertEqual(valid_count, 2)
            self.assertEqual(len(errors), 0)
        finally:
            temp_path.unlink()
    
    def test_validate_log_file_jsonl(self):
        """Test validation of JSONL (line-delimited JSON) log file."""
        logs = [
            {
                "schema_version": "1.0",
                "event_type": "FAULT_INJECTION",
                "timestamp": "2026-01-25T19:30:42.123Z"
            },
            {
                "schema_version": "1.0",
                "event_type": "GUARD_TRIGGER",
                "timestamp": "2026-01-25T19:30:42.124Z"
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for log in logs:
                f.write(json.dumps(log) + '\n')
            temp_path = Path(f.name)
        
        try:
            valid_count, errors = self.validator.validate_log_file(temp_path)
            self.assertEqual(valid_count, 2)
            self.assertEqual(len(errors), 0)
        finally:
            temp_path.unlink()
    
    def test_validate_log_file_with_errors(self):
        """Test validation reports errors correctly."""
        logs = [
            {
                "schema_version": "1.0",
                "event_type": "FAULT_INJECTION",
                "timestamp": "2026-01-25T19:30:42.123Z"
            },
            {
                "schema_version": "1.0",
                "event_type": "INVALID_TYPE",  # Invalid
                "timestamp": "2026-01-25T19:30:42.124Z"
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(logs, f)
            temp_path = Path(f.name)
        
        try:
            valid_count, errors = self.validator.validate_log_file(temp_path)
            self.assertEqual(valid_count, 1)
            self.assertGreater(len(errors), 0)
        finally:
            temp_path.unlink()
    
    def test_validate_log_file_single_object(self):
        """Test validation of single JSON object (not array)."""
        log = {
            "schema_version": "1.0",
            "event_type": "FAULT_INJECTION",
            "timestamp": "2026-01-25T19:30:42.123Z"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(log, f)  # Not an array, just a single object
            temp_path = Path(f.name)
        
        try:
            valid_count, errors = self.validator.validate_log_file(temp_path)
            self.assertEqual(valid_count, 1)
            self.assertEqual(len(errors), 0)
        finally:
            temp_path.unlink()
    
    def test_validate_log_file_invalid_json(self):
        """Test validation handles invalid JSON gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write('{"valid": "json"}\n')
            f.write('invalid json here\n')  # Invalid line
            f.write('{"another": "valid"}\n')
            temp_path = Path(f.name)
        
        try:
            valid_count, errors = self.validator.validate_log_file(temp_path)
            # Should have 1 valid entry (first line might be invalid due to schema)
            # and at least 1 error for the invalid JSON line
            self.assertGreater(len(errors), 0)
        finally:
            temp_path.unlink()
    
    def test_validate_log_file_empty_lines(self):
        """Test validation skips empty lines in JSONL."""
        logs_with_empty = [
            {"schema_version": "1.0", "event_type": "FAULT_INJECTION", 
             "timestamp": "2026-01-25T19:30:42.123Z"},
            {"schema_version": "1.0", "event_type": "GUARD_TRIGGER",
             "timestamp": "2026-01-25T19:30:42.124Z"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write('\n')  # Empty line
            f.write(json.dumps(logs_with_empty[0]) + '\n')
            f.write('\n')  # Another empty line
            f.write(json.dumps(logs_with_empty[1]) + '\n')
            f.write('\n')  # Trailing empty line
            temp_path = Path(f.name)
        
        try:
            valid_count, errors = self.validator.validate_log_file(temp_path)
            self.assertEqual(valid_count, 2)
            self.assertEqual(len(errors), 0)
        finally:
            temp_path.unlink()
    
    def test_validate_log_entries_function(self):
        """Test the convenience function for validating log entries."""
        entries = [
            {
                "schema_version": "1.0",
                "event_type": "FAULT_INJECTION",
                "timestamp": "2026-01-25T19:30:42.123Z"
            },
            {
                "schema_version": "1.0",
                "event_type": "GUARD_TRIGGER",
                "timestamp": "2026-01-25T19:30:42.124Z"
            }
        ]
        
        # Should not raise
        self.assertTrue(validate_log_entries(entries))
        
        # With invalid entry
        invalid_entries = [
            {
                "schema_version": "1.0",
                "event_type": "INVALID",
                "timestamp": "2026-01-25T19:30:42.123Z"
            }
        ]
        
        with self.assertRaises(ValidationError):
            validate_log_entries(invalid_entries)
    
    def test_physical_params_validation(self):
        """Test validation of physical parameters."""
        entry = {
            "schema_version": "1.0",
            "event_type": "FAULT_INJECTION",
            "timestamp": "2026-01-25T19:30:42.123Z",
            "physical_params": {
                "temp_kelvin": 300.0,
                "v_core_mv": 1000.0,
                "bit_flip_prob": 0.00001,
                "timing_jitter_s": 1e-9
            }
        }
        
        self.assertTrue(self.validator.validate_entry(entry))
        
        # Invalid: negative temperature
        entry_invalid = {
            "schema_version": "1.0",
            "event_type": "FAULT_INJECTION",
            "timestamp": "2026-01-25T19:30:42.123Z",
            "physical_params": {
                "temp_kelvin": -10.0
            }
        }
        
        with self.assertRaises(ValidationError):
            self.validator.validate_entry(entry_invalid)


if __name__ == '__main__':
    unittest.main(verbosity=2)
