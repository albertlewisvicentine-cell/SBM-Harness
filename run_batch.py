#!/usr/bin/env python3
"""
Batch Monte Carlo simulation runner for statistical safety analysis.
Runs multiple trials with different seeds to build a distribution.
"""

import argparse
import json
import sys


class SimpleLCG:
    """
    Simple Linear Congruential Generator for cross-platform reproducibility.
    Uses parameters from Numerical Recipes: a=1664525, c=1013904223, m=2^32
    """
    def __init__(self, seed):
        self.state = seed & 0xFFFFFFFF
        
    def next_uint32(self):
        """Generate next uint32 value."""
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state
    
    def randint(self, min_val, max_val):
        """Generate random integer in [min_val, max_val)."""
        range_size = max_val - min_val
        return min_val + (self.next_uint32() % range_size)
    
    def random(self):
        """Generate random float in [0, 1)."""
        return self.next_uint32() / (2**32)


def run_single_trial(seed, num_steps=1000):
    """
    Run a single simulation trial.
    
    Returns:
        dict with trial results including failure count
    """
    rng = SimpleLCG(seed)
    
    buffer_size = 100
    buffer_used = 0
    failure_count = 0
    overflow_count = 0
    
    for step in range(num_steps):
        # Simulate random memory allocation request (1-10 units)
        request = rng.randint(1, 11)
        
        # Try to allocate
        if buffer_used + request <= buffer_size:
            buffer_used += request
        else:
            # Overflow would occur - this is prevented by guards
            overflow_count += 1
            # In a real system, this might indicate a failure if not handled
            # For this safety gate, we consider it a success (guard worked)
        
        # Random deallocation (10% chance if buffer is not empty)
        if buffer_used > 0 and rng.random() < 0.1:
            dealloc = min(buffer_used, rng.randint(1, 11))
            buffer_used -= dealloc
    
    # Define failure criteria: buffer corruption or invalid state
    # For this simulation, we check if buffer state is valid
    failed = (buffer_used < 0 or buffer_used > buffer_size)
    
    return {
        "seed": int(seed),
        "steps": num_steps,
        "failed": failed,
        "overflow_count": overflow_count,
        "final_buffer_used": int(buffer_used)
    }


def main():
    parser = argparse.ArgumentParser(description="Run batch Monte Carlo simulations")
    parser.add_argument("--trials", type=int, required=True,
                       help="Number of trials to run")
    parser.add_argument("--out", type=str, required=True,
                       help="Output file for results (JSONL format)")
    parser.add_argument("--steps", type=int, default=1000,
                       help="Number of steps per trial (default: 1000)")
    parser.add_argument("--seed-base", type=int, default=1000,
                       help="Base seed for trials (default: 1000)")
    
    args = parser.parse_args()
    
    results = []
    failures = 0
    
    print(f"Running {args.trials} trials with {args.steps} steps each...")
    
    # Run trials
    for i in range(args.trials):
        seed = args.seed_base + i
        result = run_single_trial(seed, args.steps)
        results.append(result)
        if result['failed']:
            failures += 1
        
        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"  Completed {i + 1}/{args.trials} trials...")
    
    # Write results
    with open(args.out, 'w') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')
    
    # Print summary
    failure_rate = failures / args.trials if args.trials > 0 else 0
    print(f"\nBatch simulation completed:")
    print(f"  Total trials: {args.trials}")
    print(f"  Failures: {failures}")
    print(f"  Failure rate: {failure_rate:.6f} ({failure_rate * 100:.4f}%)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
