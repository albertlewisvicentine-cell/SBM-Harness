#!/usr/bin/env python3
"""
Check that safety-critical modules meet coverage thresholds.
This script enforces higher coverage requirements for modules containing
guards, fault injectors, and recovery logic.
"""

import sys
import subprocess
import re
from typing import Dict, Tuple


# Coverage thresholds for safety-critical modules  
CRITICAL_MODULE_THRESHOLDS = {
    'fault_engine.py': 95.0,  # Physics-based fault injector
    'sbm_log_validator.py': 90.0,  # Log schema validator
}

# Overall minimum coverage threshold
OVERALL_THRESHOLD = 80.0


def parse_coverage_report() -> Dict[str, Tuple[float, float]]:
    """
    Parse coverage report output to extract coverage percentages.
    
    Returns:
        Dict mapping module name to (line_coverage, branch_coverage)
    """
    # Run coverage report with branch coverage
    result = subprocess.run(
        ['coverage', 'report', '--show-missing'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"ERROR: Failed to run coverage report")
        print(result.stderr)
        return {}
    
    coverage_data = {}
    
    # Parse output lines
    for line in result.stdout.split('\n'):
        # Skip headers, separators, and TOTAL line for now
        if line.startswith('Name') or line.startswith('---') or line.startswith('TOTAL'):
            continue
        
        # Parse coverage line: Name  Stmts  Miss  Cover  Missing
        match = re.match(r'(\S+)\s+\d+\s+\d+\s+(\d+)%', line)
        if match:
            module = match.group(1)
            coverage_pct = float(match.group(2))
            # For now, use line coverage as both line and branch
            # (branch coverage parsing would require different report format)
            coverage_data[module] = (coverage_pct, coverage_pct)
    
    return coverage_data


def get_branch_coverage() -> Tuple[float, Dict[str, float]]:
    """
    Get branch coverage from coverage report.
    
    Returns:
        Tuple of (overall_branch_coverage, module_coverage_dict)
    """
    # Run coverage report with branch details
    result = subprocess.run(
        ['coverage', 'report', '--skip-covered'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        # If no .coverage file, return 0
        return 0.0, {}
    
    module_coverage = {}
    overall_coverage = 0.0
    
    # Look for TOTAL line to get overall coverage
    for line in result.stdout.split('\n'):
        if line.startswith('TOTAL'):
            match = re.search(r'(\d+)%', line)
            if match:
                overall_coverage = float(match.group(1))
        else:
            # Parse individual module lines
            match = re.match(r'(\S+\.py)\s+\d+\s+\d+\s+(\d+)%', line)
            if match:
                module = match.group(1)
                coverage = float(match.group(2))
                module_coverage[module] = coverage
    
    return overall_coverage, module_coverage


def check_coverage_thresholds() -> bool:
    """
    Check that all critical modules meet their coverage thresholds.
    
    Returns:
        True if all thresholds are met, False otherwise
    """
    # Get coverage data
    overall_coverage, module_coverage = get_branch_coverage()
    
    print("=" * 70)
    print("Coverage Threshold Check")
    print("=" * 70)
    print(f"\nOverall Coverage: {overall_coverage:.2f}%")
    print(f"Threshold:        {OVERALL_THRESHOLD:.2f}%")
    
    all_passed = True
    
    # Check overall threshold (relaxed for now since we have many untested scripts)
    # Focus on critical modules first
    if overall_coverage > 0 and overall_coverage < OVERALL_THRESHOLD:
        print(f"\n⚠  WARNING: Overall coverage ({overall_coverage:.2f}%) "
              f"below threshold ({OVERALL_THRESHOLD:.2f}%)")
        print("  (This is not a hard failure yet - focus on critical modules)")
    
    # Check critical modules
    print(f"\nSafety-Critical Module Coverage:")
    print(f"{'Module':<30} {'Coverage':<10} {'Threshold':<10} {'Status'}")
    print("-" * 70)
    
    for module, threshold in CRITICAL_MODULE_THRESHOLDS.items():
        coverage = module_coverage.get(module, 0.0)
        
        status = "✓ PASS" if coverage >= threshold else "✗ FAIL"
        if coverage < threshold:
            all_passed = False
        
        print(f"{module:<30} {coverage:>6.2f}%    {threshold:>6.2f}%    {status}")
    
    print("=" * 70)
    
    if all_passed:
        print("\n✓ All critical module coverage thresholds met!")
        return True
    else:
        print("\n✗ Some critical modules need more test coverage.")
        print("\nTo improve coverage:")
        print("  1. Add more test cases for uncovered code paths")
        print("  2. Focus on branch coverage (if/else, try/except, loops)")
        print("  3. Run: PYTHONPATH=. coverage run -m pytest tests/ -v")
        print("  4. Then: coverage report -m to see missing lines")
        return False


if __name__ == "__main__":
    success = check_coverage_thresholds()
    sys.exit(0 if success else 1)
