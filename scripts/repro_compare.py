#!/usr/bin/env python3
"""
Reproducibility comparison script for SBM-Harness validation.
Compares Python and C simulation outputs within a tolerance.
"""

import argparse
import json
import sys


def load_trace(filename):
    """Load a JSONL trace file."""
    trace = []
    with open(filename, 'r') as f:
        for line in f:
            trace.append(json.loads(line.strip()))
    return trace


def compare_traces(trace1, trace2, rtol=1e-7):
    """
    Compare two traces for reproducibility.
    
    Args:
        trace1: First trace (list of events)
        trace2: Second trace (list of events)
        rtol: Relative tolerance for numeric comparisons
        
    Returns:
        (is_match, error_messages)
    """
    errors = []
    
    if len(trace1) != len(trace2):
        errors.append(f"Length mismatch: {len(trace1)} vs {len(trace2)}")
        return False, errors
    
    for i, (event1, event2) in enumerate(zip(trace1, trace2)):
        # Compare step number
        if event1.get('step') != event2.get('step'):
            errors.append(f"Step {i}: step number mismatch {event1.get('step')} vs {event2.get('step')}")
        
        # Compare state
        if event1.get('state') != event2.get('state'):
            errors.append(f"Step {i}: state mismatch '{event1.get('state')}' vs '{event2.get('state')}'")
        
        # Compare buffer_used
        val1 = event1.get('buffer_used', 0)
        val2 = event2.get('buffer_used', 0)
        if abs(val1 - val2) > rtol * max(abs(val1), abs(val2), 1.0):
            errors.append(f"Step {i}: buffer_used mismatch {val1} vs {val2}")
        
        # Compare request
        if event1.get('request') != event2.get('request'):
            errors.append(f"Step {i}: request mismatch {event1.get('request')} vs {event2.get('request')}")
        
        # Compare success
        if event1.get('success') != event2.get('success'):
            errors.append(f"Step {i}: success mismatch {event1.get('success')} vs {event2.get('success')}")
        
        # Stop after first 10 errors
        if len(errors) >= 10:
            errors.append("... (more errors omitted)")
            break
    
    return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(description="Compare simulation traces for reproducibility")
    parser.add_argument("trace1", help="First trace file (JSONL)")
    parser.add_argument("trace2", help="Second trace file (JSONL)")
    parser.add_argument("--rtol", type=float, default=1e-7,
                       help="Relative tolerance for numeric comparisons (default: 1e-7)")
    
    args = parser.parse_args()
    
    # Load traces
    try:
        trace1 = load_trace(args.trace1)
        trace2 = load_trace(args.trace2)
    except Exception as e:
        print(f"Error loading traces: {e}", file=sys.stderr)
        return 1
    
    # Compare traces
    is_match, errors = compare_traces(trace1, trace2, args.rtol)
    
    if is_match:
        print(f"✓ Reproducibility check PASSED")
        print(f"  Compared {len(trace1)} events with rtol={args.rtol}")
        return 0
    else:
        print(f"✗ Reproducibility check FAILED", file=sys.stderr)
        print(f"  Found {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"    - {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
