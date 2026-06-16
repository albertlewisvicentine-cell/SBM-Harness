#!/usr/bin/env python3
"""
Statistical safety gate using Wilson confidence interval.
Evaluates if the upper bound of failure probability is within acceptable limits.
"""

import argparse
import json
import sys
import math


def wilson_upper_bound(successes, trials, confidence=0.95):
    """
    Calculate the upper bound of the Wilson score confidence interval.
    
    This is a more accurate method than the normal approximation for
    small sample sizes or extreme probabilities.
    
    Args:
        successes: Number of successful trials
        trials: Total number of trials
        confidence: Confidence level (default: 0.95 for 95% CI)
        
    Returns:
        Upper bound of the confidence interval for the success probability
    """
    if trials == 0:
        return 1.0
    
    # Z-score for the confidence level
    # For 95% confidence: z ≈ 1.96
    # For 99% confidence: z ≈ 2.576
    z_scores = {
        0.90: 1.645,
        0.95: 1.96,
        0.99: 2.576,
        0.999: 3.291
    }
    z = z_scores.get(confidence, 1.96)
    
    p_hat = successes / trials
    
    # Wilson score interval formula
    denominator = 1 + z**2 / trials
    center = (p_hat + z**2 / (2 * trials)) / denominator
    margin = (z / denominator) * math.sqrt(p_hat * (1 - p_hat) / trials + z**2 / (4 * trials**2))
    
    upper_bound = center + margin
    
    return min(upper_bound, 1.0)  # Cap at 1.0


def main():
    parser = argparse.ArgumentParser(description="Evaluate statistical safety using Wilson CI")
    parser.add_argument("results_file", help="Results file (JSONL format)")
    parser.add_argument("--p_max", type=float, required=True,
                       help="Maximum acceptable failure probability (e.g., 0.01 for 1%)")
    parser.add_argument("--confidence", type=float, default=0.95,
                       help="Confidence level for Wilson interval (default: 0.95)")
    
    args = parser.parse_args()
    
    # Load results
    try:
        results = []
        with open(args.results_file, 'r') as f:
            for line in f:
                results.append(json.loads(line.strip()))
    except Exception as e:
        print(f"Error loading results: {e}", file=sys.stderr)
        return 1
    
    if len(results) == 0:
        print("Error: No results found in file", file=sys.stderr)
        return 1
    
    # Count failures
    total_trials = len(results)
    failures = sum(1 for r in results if r.get('failed', False))
    
    # Calculate failure rate and Wilson upper bound for failures
    failure_rate = failures / total_trials
    failures_wilson_upper = wilson_upper_bound(failures, total_trials, args.confidence)
    
    print(f"\n{'='*60}")
    print(f"Statistical Safety Gate Results")
    print(f"{'='*60}")
    print(f"Total trials: {total_trials}")
    print(f"Failures: {failures}")
    print(f"Observed failure rate: {failure_rate:.6f} ({failure_rate * 100:.4f}%)")
    print(f"Wilson CI upper bound (p_failure): {failures_wilson_upper:.6f} ({failures_wilson_upper * 100:.4f}%)")
    print(f"Confidence level: {args.confidence * 100:.1f}%")
    print(f"Threshold (p_max): {args.p_max:.6f} ({args.p_max * 100:.4f}%)")
    print(f"{'='*60}")
    
    # Check if upper bound is within acceptable limits
    if failures_wilson_upper <= args.p_max:
        print(f"\n✓ SAFETY GATE PASSED")
        print(f"  Upper bound ({failures_wilson_upper:.6f}) ≤ threshold ({args.p_max:.6f})")
        return 0
    else:
        print(f"\n✗ SAFETY GATE FAILED", file=sys.stderr)
        print(f"  Upper bound ({failures_wilson_upper:.6f}) > threshold ({args.p_max:.6f})", file=sys.stderr)
        print(f"\n  The algorithm may not be safe enough.", file=sys.stderr)
        print(f"  Consider:", file=sys.stderr)
        print(f"    - Increasing buffer size", file=sys.stderr)
        print(f"    - Improving allocation strategy", file=sys.stderr)
        print(f"    - Running more trials for tighter bounds", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
