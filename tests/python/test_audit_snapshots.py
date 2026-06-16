#!/usr/bin/env python3
"""
Snapshot tests for audit report generation.
Tests that reports remain stable and comparable across runs.
"""

import unittest
from pathlib import Path
from generate_audit_report import generate_audit_report, normalize_report_for_snapshot


class TestAuditReportSnapshots(unittest.TestCase):
    """Snapshot tests for audit report generation."""
    
    def test_audit_report_golden_match(self):
        """Test that generated report matches golden snapshot after normalization."""
        # Generate fresh report
        generate_audit_report()
        
        # Read generated report
        generated_path = Path("AUDIT_REPORT_AUTO.md")
        self.assertTrue(generated_path.exists(), "Report should be generated")
        
        generated_content = generated_path.read_text()
        
        # Normalize for comparison
        normalized_generated = normalize_report_for_snapshot(generated_content)
        
        # Read golden snapshot
        golden_path = Path(__file__).parent / "golden" / "AUDIT_REPORT_GOLDEN.md"
        self.assertTrue(golden_path.exists(), 
                       f"Golden snapshot should exist at {golden_path}")
        
        golden_content = golden_path.read_text()
        
        # Compare normalized versions
        self.assertEqual(
            normalized_generated,
            golden_content,
            "Normalized generated report should match golden snapshot. "
            "If this is expected, update the golden file with:\n"
            f"  python -c \"from generate_audit_report import normalize_report_for_snapshot; "
            f"from pathlib import Path; "
            f"Path('{golden_path}').write_text(normalize_report_for_snapshot(Path('AUDIT_REPORT_AUTO.md').read_text()))\""
        )
    
    def test_report_structure_sections(self):
        """Test that generated report contains all expected sections."""
        generate_audit_report()
        
        report_path = Path("AUDIT_REPORT_AUTO.md")
        content = report_path.read_text()
        
        # Check for key sections
        required_sections = [
            "# Auto-Generated Audit Report",
            "## 1. Physical Operating Envelope",
            "## 2. Safety Goals & Evidence Traceability",
            "## 3. Deviations & Justifications",
            "## 4. Approval"
        ]
        
        for section in required_sections:
            self.assertIn(section, content,
                         f"Report should contain section: {section}")
    
    def test_report_safety_goals_table(self):
        """Test that safety goals table is present and formatted correctly."""
        generate_audit_report()
        
        report_path = Path("AUDIT_REPORT_AUTO.md")
        content = report_path.read_text()
        
        # Check for table header
        self.assertIn("| GSN ID | Description | Injections | Detected & Recovered | Success Rate |", 
                     content)
        
        # Check for at least one GSN goal (G1-G6)
        has_gsn = any(f"| G{i} |" in content for i in range(1, 7))
        self.assertTrue(has_gsn, "Report should contain at least one GSN goal")
    
    def test_report_overall_stats(self):
        """Test that overall statistics are included."""
        generate_audit_report()
        
        report_path = Path("AUDIT_REPORT_AUTO.md")
        content = report_path.read_text()
        
        # Should have overall recovery rate
        self.assertIn("**Overall:**", content)
        self.assertIn("recovery rate", content)
        
        # Should have format like "X/Y faults injected"
        import re
        match = re.search(r'\d+/\d+ faults injected', content)
        self.assertIsNotNone(match, "Should have fault injection count")
    
    def test_normalization_idempotent(self):
        """Test that report normalization is idempotent."""
        generate_audit_report()
        
        report_path = Path("AUDIT_REPORT_AUTO.md")
        original = report_path.read_text()
        
        # Normalize twice
        normalized1 = normalize_report_for_snapshot(original)
        normalized2 = normalize_report_for_snapshot(normalized1)
        
        # Should be identical
        self.assertEqual(normalized1, normalized2,
                        "Normalization should be idempotent")


class TestGoldenFileManagement(unittest.TestCase):
    """Tests for managing golden snapshot files."""
    
    def test_golden_directory_exists(self):
        """Test that golden directory exists."""
        golden_dir = Path(__file__).parent / "golden"
        self.assertTrue(golden_dir.exists(), "Golden directory should exist")
        self.assertTrue(golden_dir.is_dir(), "Golden path should be a directory")
    
    def test_golden_report_exists(self):
        """Test that golden report file exists."""
        golden_path = Path(__file__).parent / "golden" / "AUDIT_REPORT_GOLDEN.md"
        self.assertTrue(golden_path.exists(), 
                       "Golden audit report should exist. Generate it with:\n"
                       "  python generate_audit_report.py && "
                       "  python -c \"from generate_audit_report import normalize_report_for_snapshot; "
                       "from pathlib import Path; "
                       "Path('tests/golden/AUDIT_REPORT_GOLDEN.md').write_text("
                       "normalize_report_for_snapshot(Path('AUDIT_REPORT_AUTO.md').read_text()))\"")
    
    def test_golden_report_valid_markdown(self):
        """Test that golden report is valid markdown."""
        golden_path = Path(__file__).parent / "golden" / "AUDIT_REPORT_GOLDEN.md"
        
        if not golden_path.exists():
            self.skipTest("Golden report not yet created")
        
        content = golden_path.read_text()
        
        # Basic markdown validation
        self.assertTrue(content.startswith("#"), "Should start with markdown header")
        self.assertIn("##", content, "Should have subsections")
        self.assertIn("|", content, "Should have markdown tables")


if __name__ == '__main__':
    unittest.main(verbosity=2)
