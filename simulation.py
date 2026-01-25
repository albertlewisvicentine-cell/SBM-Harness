#!/usr/bin/env python3
"""
Monte Carlo simulation for SBM-Harness validation.
Simulates bounded memory operations with deterministic seeding.
"""

import argparse
import json
import sys
import numpy as np


def run_simulation(seed, num_steps=1000):
    """
    Run a deterministic simulation with the given seed.
    
    Simulates bounded buffer operations with:
    - Random writes to a bounded buffer
    - Overflow detection
    - State transitions
    
    Args:
        seed: Random seed for reproducibility
        num_steps: Number of simulation steps
        
    Returns:
        List of trace events (dicts with step, state, value)
    """
    np.random.seed(seed)
    trace = []
    
    buffer_size = 100
    buffer_used = 0
    
    for step in range(num_steps):
        # Simulate random memory allocation request (1-10 units)
        request = np.random.randint(1, 11)
        
        # Try to allocate
        if buffer_used + request <= buffer_size:
            buffer_used += request
            state = "allocated"
            success = True
        else:
            state = "overflow_prevented"
            success = False
        
        # Random deallocation (10% chance if buffer is not empty)
        if buffer_used > 0 and np.random.random() < 0.1:
            dealloc = min(buffer_used, np.random.randint(1, 11))
            buffer_used -= dealloc
            state = "deallocated"
        
        # Record trace event
        event = {
            "step": step,
            "state": state,
            "buffer_used": int(buffer_used),
            "request": int(request),
            "success": success
        }
        trace.append(event)
    
    return trace


def main():
    parser = argparse.ArgumentParser(description="Run SBM simulation")
    parser.add_argument("--seed", type=int, required=True, 
                       help="Random seed for reproducibility")
    parser.add_argument("--out", type=str, required=True,
                       help="Output file for trace (JSONL format)")
    parser.add_argument("--steps", type=int, default=1000,
                       help="Number of simulation steps (default: 1000)")
    
    args = parser.parse_args()
    
    # Run simulation
    trace = run_simulation(args.seed, args.steps)
    
    # Write trace to file
    with open(args.out, 'w') as f:
        for event in trace:
            f.write(json.dumps(event) + '\n')
    
    # Print summary
    total = len(trace)
    overflows = sum(1 for e in trace if e['state'] == 'overflow_prevented')
    print(f"Simulation completed: {total} steps, {overflows} overflows prevented")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
