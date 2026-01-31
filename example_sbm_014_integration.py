#!/usr/bin/env python3
"""
Example integration of SBM-014-HUMAN with C-based SBM guards.

This demonstrates how causal echo translation layer operates outside
the core mirror, processing reflections from the C guard system and
presenting them to humans as informative back-pressure.
"""

import sys
import re
from sbm_014_causal_echo import CausalEcho


def parse_sbm_guard_output(output_line: str) -> dict:
    """
    Parse output from sbm_failure_handler (C code).
    
    Example input:
        [SBM-GUARD] Failure at src/core.c:42 - Null pointer: data (status=1)
    
    Returns:
        Dictionary with parsed fields or None if not a guard failure
    """
    pattern = r'\[SBM-GUARD\] Failure at ([^:]+):(\d+) - ([^(]+) \(status=(\d+)\)'
    match = re.match(pattern, output_line)
    
    if not match:
        return None
    
    file_path, line, msg, status_code_num = match.groups()
    
    # Map numeric status to SBM error code
    status_map = {
        '1': 'SBM_ERR_NULL',
        '2': 'SBM_ERR_OOB',
        '3': 'SBM_ERR_TIMEOUT',
        '4': 'SBM_ERR_INCONSISTENT',
    }
    
    status_code = status_map.get(status_code_num, 'SBM_ERR_UNKNOWN')
    
    return {
        'file': file_path,
        'line': int(line),
        'msg': msg.strip(),
        'status_code': status_code
    }


def process_guard_failure(output_line: str) -> str:
    """
    Process a guard failure line and return human-readable causal echo.
    
    This is the integration point: takes raw C guard output and returns
    structured, human-interpretable signal via SBM-014-HUMAN.
    """
    parsed = parse_sbm_guard_output(output_line)
    
    if not parsed:
        # Not a guard failure line, pass through
        return output_line
    
    # Translate via SBM-014-HUMAN
    echo = CausalEcho.translate_reflection(
        parsed['status_code'],
        context={
            'file': parsed['file'],
            'line': parsed['line'],
            'msg': parsed['msg']
        }
    )
    
    # Format for display
    return CausalEcho.format_for_display(echo)


def main():
    """
    Main integration demo: process C guard output through SBM-014-HUMAN.
    """
    print("SBM-014-HUMAN Integration Example")
    print("=" * 70)
    print()
    print("Simulating C guard failures and translating via Causal Echo...")
    print()
    
    # Example guard failure outputs from C code
    example_failures = [
        "[SBM-GUARD] Failure at src/core.c:42 - Null pointer: data (status=1)",
        "[SBM-GUARD] Failure at src/buffer.c:156 - Index out of bounds: idx (status=2)",
        "[SBM-GUARD] Failure at src/algorithm.c:89 - Loop limit exceeded (status=3)",
    ]
    
    for i, failure_line in enumerate(example_failures, 1):
        print(f"\n{'='*70}")
        print(f"Example {i}: Raw C Guard Output")
        print(f"{'='*70}")
        print(f"Raw: {failure_line}")
        print()
        
        # Process through SBM-014-HUMAN
        causal_echo = process_guard_failure(failure_line)
        print(causal_echo)
    
    print("\n" + "="*70)
    print("Integration complete: All failures translated to causal echoes")
    print("="*70)


if __name__ == "__main__":
    main()
