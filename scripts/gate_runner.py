#!/usr/bin/env python3
"""
Enhanced gate runner with three-gate validation system.
Implements Wilson confidence intervals, performance floor checks,
and critical sequence limit validation.
"""

import argparse
import json
import math
import sys
from statistics import mean, stdev


def wilson_upper(k, n, z=1.96):
    """
    Calculate the upper bound of the Wilson score confidence interval.
    
    Args:
        k: Number of failures
        n: Total number of trials
        z: Z-score for confidence level (default: 1.96 for 95% CI)
        
    Returns:
        Upper bound of the confidence interval for the failure probability
    """
    if n == 0:
        return 1.0
    p = k / n
    # Wilson Score Interval Formula
    denominator = 1 + z**2/n
    centre_adj = p + z**2/(2*n)
    adj_std = z * math.sqrt((p*(1-p)/n) + (z**2/(4*n**2)))
    return (centre_adj + adj_std) / denominator


def run_gate(args, runs):
    """
    Execute the three-gate validation system.
    
    Args:
        args: Parsed command-line arguments with gate thresholds
        runs: List of run results, each containing:
            - R: Performance metric
            - max_consecutive_supercritical: Maximum consecutive supercritical steps
            
    Returns:
        None (exits with code 0 on pass, 1 on failure)
    """
    Rs = [r["R"] for r in runs if "R" in r]
    n = len(Rs)
    # k is the number of failures (R below minimum)
    k = sum(1 for r in Rs if r < args.r_min)
    
    p_fail = k / n if n > 0 else 1.0
    wilson_u = wilson_upper(k, n)
    
    meanR = mean(Rs) if n > 0 else 0.0
    stdR = stdev(Rs) if n > 1 else 0.0
    stderr = stdR / math.sqrt(n) if n > 0 else 0.0
    meanR_lower95 = meanR - 1.96 * stderr

    # Track maximum consecutive supercritical steps across all runs
    max_consec = 0
    for r in runs:
        v = r.get("max_consecutive_supercritical", 0)
        if isinstance(v, int) and v > max_consec:
            max_consec = v

    report = {
        "n_runs": n,
        "p_failure_obs": p_fail,
        "wilson_upper95": wilson_u,
        "mean_R": meanR,
        "meanR_lower95": meanR_lower95,
        "max_consec_observed": max_consec
    }

    failed = False
    # Gate 1: Wilson Upper Bound for Safety
    if wilson_u >= args.p_max:
        print(f"FAIL: Wilson Upper {wilson_u:.4f} >= {args.p_max}", file=sys.stderr)
        failed = True
    
    # Gate 2: Performance Floor
    if meanR_lower95 < args.r_min:
        print(f"FAIL: Mean R Lower Bound {meanR_lower95:.4f} < {args.r_min}", file=sys.stderr)
        failed = True

    # Gate 3: Critical Sequence Limit
    if max_consec >= args.t_crit:
        print(f"FAIL: Max Consec {max_consec} >= {args.t_crit}", file=sys.stderr)
        failed = True

    print("\nGATE REPORT:")
    print(json.dumps(report, indent=2))
    
    if failed:
        sys.exit(1)  # Signal failure to CI/Copilot Agent


def main():
    """
    Main entry point for the gate runner CLI.
    """
    parser = argparse.ArgumentParser(
        description="Run enhanced three-gate validation system"
    )
    parser.add_argument(
        "results_file",
        help="Results file (JSONL format) with R values and max_consecutive_supercritical"
    )
    parser.add_argument(
        "--p_max",
        type=float,
        required=True,
        help="Maximum acceptable failure probability (Wilson upper bound threshold)"
    )
    parser.add_argument(
        "--r_min",
        type=float,
        required=True,
        help="Minimum acceptable R value for performance floor"
    )
    parser.add_argument(
        "--t_crit",
        type=int,
        required=True,
        help="Critical threshold for max consecutive supercritical steps"
    )
    
    args = parser.parse_args()
    
    # Load results
    try:
        runs = []
        with open(args.results_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    runs.append(json.loads(line))
    except FileNotFoundError:
        print(f"Error: Results file '{args.results_file}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in results file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading results: {e}", file=sys.stderr)
        sys.exit(1)
    
    if len(runs) == 0:
        print("Error: No results found in file", file=sys.stderr)
        sys.exit(1)
    
    # Run the gate validation
    run_gate(args, runs)
    
    print("\n✓ ALL GATES PASSED")
    sys.exit(0)


if __name__ == "__main__":
    main()
