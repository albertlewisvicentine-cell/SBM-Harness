#!/usr/bin/env python3
"""
Tests for digital assets inventory and conflict verification tool.
"""

import unittest
import json
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
import check_digital_assets


class TestDigitalAssetsChecker(unittest.TestCase):
    """Test cases for digital assets checker."""
    
    def setUp(self):
        """Set up test environment."""
        self.repo_root = Path(__file__).parent.parent
        self.test_files = list(check_digital_assets.get_all_files())
        
    def test_file_discovery(self):
        """Test that files are discovered correctly."""
        self.assertGreater(len(self.test_files), 50, "Should find at least 50 files")
        
        # Check some expected files exist
        file_names = {f.name for f in self.test_files}
        expected_files = [
            'README.md',
            'check_digital_assets.py',
            'requirements.txt',
            'LICENSE',
            'Makefile'
        ]
        for expected in expected_files:
            self.assertIn(expected, file_names, f"Expected file {expected} not found")
    
    def test_file_categorization(self):
        """Test that files are categorized correctly."""
        # Test Python files
        py_file = Path('test.py')
        self.assertEqual(check_digital_assets.categorize_file(py_file), 'source_code')
        
        # Test C files
        c_file = Path('test.c')
        self.assertEqual(check_digital_assets.categorize_file(c_file), 'source_code')
        
        # Test markdown files
        md_file = Path('README.md')
        self.assertEqual(check_digital_assets.categorize_file(md_file), 'documentation')
        
        # Test JSON config files
        json_file = Path('config.json')
        self.assertEqual(check_digital_assets.categorize_file(json_file), 'configuration')
        
        # Test Makefile
        makefile = Path('Makefile')
        self.assertEqual(check_digital_assets.categorize_file(makefile), 'build')
        
        # Test license file
        license_file = Path('LICENSE')
        self.assertEqual(check_digital_assets.categorize_file(license_file), 'license')
    
    def test_hash_computation(self):
        """Test file hash computation."""
        # Test with README.md
        readme = self.repo_root / 'README.md'
        if readme.exists():
            hash1 = check_digital_assets.compute_file_hash(readme)
            hash2 = check_digital_assets.compute_file_hash(readme)
            self.assertEqual(hash1, hash2, "Same file should produce same hash")
            self.assertEqual(len(hash1), 64, "SHA256 hash should be 64 chars")
    
    def test_naming_conflicts(self):
        """Test naming conflict detection."""
        conflicts = check_digital_assets.check_naming_conflicts(self.test_files)
        # Repository should have no naming conflicts
        self.assertEqual(len(conflicts), 0, f"Found unexpected naming conflicts: {conflicts}")
    
    def test_content_conflicts(self):
        """Test content duplication detection."""
        conflicts = check_digital_assets.check_content_conflicts(self.test_files)
        # Repository should have no content conflicts
        self.assertEqual(len(conflicts), 0, f"Found unexpected content conflicts")
    
    def test_license_detection(self):
        """Test license file detection."""
        license_info = check_digital_assets.check_license_conflicts(self.test_files)
        self.assertGreaterEqual(license_info['count'], 1, "Should have at least one license file")
        
        # Check for dual licensing (MIT + Apache)
        if license_info['count'] == 2:
            self.assertTrue(license_info['is_dual_license'], 
                          "MIT + Apache 2.0 should be detected as dual-licensing")
            self.assertFalse(license_info['conflict'], 
                           "Dual-licensing should not be flagged as conflict")
    
    def test_dependency_conflicts(self):
        """Test dependency file conflict detection."""
        conflicts = check_digital_assets.check_dependency_conflicts(self.test_files)
        
        # Check requirements.txt
        self.assertIn('requirements.txt', conflicts)
        self.assertEqual(conflicts['requirements.txt']['count'], 1, 
                        "Should have exactly one requirements.txt")
        self.assertFalse(conflicts['requirements.txt']['conflict'],
                        "Should have no requirements.txt conflicts")
        
        # Check package.json
        self.assertIn('package.json', conflicts)
        self.assertFalse(conflicts['package.json']['conflict'],
                        "Should have no package.json conflicts")
    
    def test_config_conflicts(self):
        """Test configuration file conflict detection."""
        conflicts = check_digital_assets.check_config_conflicts(self.test_files)
        # Repository should have no config conflicts
        self.assertEqual(len(conflicts), 0, f"Found unexpected config conflicts: {conflicts}")
    
    def test_inventory_generation(self):
        """Test inventory generation."""
        inventory = check_digital_assets.generate_inventory(self.test_files)
        
        # Check structure
        self.assertIn('total_files', inventory)
        self.assertIn('by_category', inventory)
        self.assertIn('by_extension', inventory)
        self.assertIn('file_sizes', inventory)
        self.assertIn('total_size', inventory)
        
        # Check values
        self.assertEqual(inventory['total_files'], len(self.test_files))
        self.assertGreater(inventory['total_size'], 0, "Total size should be positive")
        
        # Check categories exist
        expected_categories = ['source_code', 'documentation', 'configuration']
        for category in expected_categories:
            self.assertIn(category, inventory['by_category'], 
                         f"Should have {category} category")
    
    def test_report_json_output(self):
        """Test that JSON report can be generated and parsed."""
        report_file = self.repo_root / 'DIGITAL_ASSETS_REPORT.json'
        
        # Report should exist after running the script
        if report_file.exists():
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            
            # Check structure
            self.assertIn('inventory', report_data)
            self.assertIn('conflicts', report_data)
            
            # Check conflicts section
            conflicts = report_data['conflicts']
            self.assertIn('naming', conflicts)
            self.assertIn('content', conflicts)
            self.assertIn('license', conflicts)
            self.assertIn('dependencies', conflicts)
            self.assertIn('configuration', conflicts)


class TestExcludedDirectories(unittest.TestCase):
    """Test that certain directories are excluded from scanning."""
    
    def test_git_excluded(self):
        """Test that .git directory is excluded."""
        all_files = check_digital_assets.get_all_files()
        git_files = [f for f in all_files if '.git/' in str(f)]
        # .git directory itself might be in paths, but not its contents
        self.assertEqual(len(git_files), 0, ".git directory should be excluded")
    
    def test_pycache_excluded(self):
        """Test that __pycache__ directories are excluded."""
        all_files = check_digital_assets.get_all_files()
        pycache_files = [f for f in all_files if '__pycache__' in str(f)]
        self.assertEqual(len(pycache_files), 0, "__pycache__ should be excluded")


if __name__ == '__main__':
    unittest.main()
