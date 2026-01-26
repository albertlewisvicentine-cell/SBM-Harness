#!/usr/bin/env python3
"""
Tests for audit report generation and normalization.
"""

import unittest
from generate_audit_report import (
    normalize_timestamp,
    normalize_float,
    normalize_report_for_snapshot
)


class TestReportNormalization(unittest.TestCase):
    """Test cases for report normalization functions."""
    
    def test_normalize_timestamp(self):
        """Test timestamp normalization."""
        timestamps = [
            "2026-01-25T19:30:42.123Z",
            "2025-12-31T23:59:59.999Z",
            "2020-01-01T00:00:00.000Z"
        ]
        
        for ts in timestamps:
            normalized = normalize_timestamp(ts)
            self.assertEqual(normalized, "2026-01-01T00:00:00.000Z")
    
    def test_normalize_float_precision(self):
        """Test float normalization to fixed precision."""
        # Test standard rounding
        self.assertEqual(normalize_float(1.234567890123, precision=8), 1.23456789)
        self.assertEqual(normalize_float(3.14159265359, precision=6), 3.141593)
        
        # Test zero
        self.assertEqual(normalize_float(0.0, precision=8), 0.0)
        
        # Test very small numbers
        self.assertAlmostEqual(
            normalize_float(1e-10, precision=12),
            1e-10,
            places=12
        )
    
    def test_normalize_report_timestamp_replacement(self):
        """Test that all timestamps in report are normalized."""
        report = """
        Generated: 2026-01-25T19:30:42.123Z
        Test run: 2025-12-15T10:20:30.456Z
        """
        
        normalized = normalize_report_for_snapshot(report)
        
        # All timestamps should be replaced
        self.assertIn("2026-01-01T00:00:00.000Z", normalized)
        self.assertNotIn("2026-01-25T19:30:42.123Z", normalized)
        self.assertNotIn("2025-12-15T10:20:30.456Z", normalized)
    
    def test_normalize_report_path_replacement(self):
        """Test that absolute paths are normalized."""
        report = """
        File: /home/runner/work/SBM-Harness/SBM-Harness/src/file.c
        Path: /usr/local/SBM-Harness/tests/test.c
        """
        
        normalized = normalize_report_for_snapshot(report)
        
        # Absolute paths should be shortened
        self.assertIn("SBM-Harness/src/file.c", normalized)
        self.assertNotIn("/home/runner/work/", normalized)
    
    def test_normalize_report_float_rounding(self):
        """Test that long floats are rounded in reports."""
        report = """
        Probability: 0.123456789012345
        Rate: 99.999999999
        Value: 1.00000000001
        """
        
        normalized = normalize_report_for_snapshot(report)
        
        # Long floats should be rounded to 6 decimal places
        self.assertIn("0.123457", normalized)  # Rounded from 0.123456789012345
        # Shorter floats should remain
        self.assertNotIn("0.123456789012345", normalized)
    
    def test_normalize_report_combined(self):
        """Test combined normalization of multiple elements."""
        report = """
# Audit Report
**Generated:** 2026-01-25T19:30:42.123Z
**Path:** /home/runner/work/SBM-Harness/SBM-Harness/generate_audit_report.py

## Results
- Probability: 0.000123456789
- Success rate: 99.87654321098765%
- Timestamp: 2025-11-20T15:45:30.000Z
        """
        
        normalized = normalize_report_for_snapshot(report)
        
        # Check timestamp normalization
        self.assertNotIn("2026-01-25", normalized)
        self.assertNotIn("2025-11-20", normalized)
        
        # Check path normalization
        self.assertNotIn("/home/runner/work/", normalized)
        self.assertIn("SBM-Harness/generate_audit_report.py", normalized)
        
        # Check float rounding
        self.assertNotIn("0.000123456789", normalized)
        self.assertNotIn("99.87654321098765", normalized)
    
    def test_normalize_report_preserves_content(self):
        """Test that normalization doesn't damage actual content."""
        report = """
## Safety Goals
| ID | Description | Count |
|----|-------------|-------|
| G1 | Pointer guards | 42 |
| G2 | Array bounds | 128 |
        """
        
        normalized = normalize_report_for_snapshot(report)
        
        # Table structure should be preserved
        self.assertIn("| G1 | Pointer guards | 42 |", normalized)
        self.assertIn("| G2 | Array bounds | 128 |", normalized)
        self.assertIn("Safety Goals", normalized)
    
    def test_normalize_report_idempotent(self):
        """Test that normalization is idempotent (can be applied multiple times)."""
        report = """
        Generated: 2026-01-25T19:30:42.123Z
        Value: 1.234567890123
        """
        
        normalized1 = normalize_report_for_snapshot(report)
        normalized2 = normalize_report_for_snapshot(normalized1)
        
        # Second normalization shouldn't change result
        self.assertEqual(normalized1, normalized2)


class TestFloatPrecision(unittest.TestCase):
    """Test cases for floating point precision handling."""
    
    def test_scientific_notation(self):
        """Test handling of scientific notation."""
        # Very small numbers
        self.assertEqual(normalize_float(1.23e-10, precision=12), 1.23e-10)
        
        # Very large numbers
        result = normalize_float(1.23e10, precision=2)
        self.assertAlmostEqual(result, 1.23e10, places=2)
    
    def test_precision_levels(self):
        """Test different precision levels."""
        value = 3.141592653589793
        
        self.assertEqual(normalize_float(value, precision=2), 3.14)
        self.assertEqual(normalize_float(value, precision=4), 3.1416)
        self.assertEqual(normalize_float(value, precision=6), 3.141593)
        self.assertEqual(normalize_float(value, precision=10), 3.1415926536)


if __name__ == '__main__':
    unittest.main(verbosity=2)
