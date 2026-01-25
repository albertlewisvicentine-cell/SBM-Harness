# Copilot Agent Validation Gate

This directory contains the implementation of a two-stage validation gate for the SBM-Harness project. The validation gate ensures that code changes maintain both **implementation parity** and **statistical safety**.

## Overview

The validation gate consists of two jobs that run automatically on pull requests:

### Gate 1: Reproducibility Check (Parity Gate)
**Purpose**: Verify that Python and C implementations produce identical results.

This gate:
- Runs both Python (`simulation.py`) and C (`sim.c`) simulations with the same seed
- Compares outputs within a relative tolerance (`rtol=1e-7`)
- **Fails if** the implementations diverge, indicating a broken implementation

**When to use**: Run this check whenever you modify simulation logic in either Python or C.

### Gate 2: Statistical Safety Gate
**Purpose**: Verify that the algorithm maintains acceptable failure rates using Wilson confidence intervals.

This gate:
- Runs 1000 Monte Carlo trials using `run_batch.py`
- Evaluates the Wilson upper bound for failure probability
- **Fails if** the upper bound exceeds the threshold (default: 1%)

**When to use**: Run after any algorithmic change that might affect safety properties.

## Files

### Workflow
- `.github/workflows/validation-gate.yml` - GitHub Actions workflow definition

### Simulation Scripts
- `simulation.py` - Python reference implementation with Simple LCG
- `sim.c` - C implementation with matching LCG for exact reproducibility
- `repro_compare.py` - Parity comparison tool (checks Python vs C outputs)

### Statistical Analysis Scripts
- `run_batch.py` - Batch Monte Carlo simulation runner
- `safety_gate.py` - Wilson confidence interval evaluator

## Usage

### Running Locally

#### Using Makefile (Recommended)

The project includes Makefile targets for convenience:

```bash
# Run reproducibility check (Gate 1)
make repro-check

# Run statistical safety gate (Gate 2)
make safety-gate

# Run both gates
make repro-check && make safety-gate
```

#### Manual Execution

#### Test Reproducibility (Gate 1)
```bash
# Run Python simulation
python simulation.py --seed 42 --out py_trace.jsonl

# Compile and run C simulation  
gcc -O3 sim.c -o sim_c -lm
./sim_c --seed 42 --out c_trace.jsonl

# Compare outputs
python repro_compare.py py_trace.jsonl c_trace.jsonl --rtol 1e-7
```

#### Test Statistical Safety (Gate 2)
```bash
# Run batch simulation (1000 trials)
python run_batch.py --trials 1000 --out results.jsonl

# Evaluate safety with Wilson CI
python safety_gate.py results.jsonl --p_max 0.01
```

### Interpreting Results

#### Reproducibility Check
- ✓ **PASSED**: Python and C implementations match within tolerance
- ✗ **FAILED**: Implementations diverge - check for logic errors or RNG differences

#### Statistical Safety Gate
- ✓ **PASSED**: Wilson upper bound ≤ p_max (algorithm is safe enough)
- ✗ **FAILED**: Wilson upper bound > p_max (algorithm may be unsafe)

If the safety gate fails:
1. Check the Wilson CI bounds in the logs
2. Increase buffer size or improve allocation strategy
3. Run more trials to get tighter confidence bounds
4. Re-evaluate the p_max threshold if appropriate

## Implementation Notes

### Random Number Generation
- **Python**: Uses a simple Linear Congruential Generator (LCG) with parameters from Numerical Recipes
- **C**: Identical LCG implementation for exact cross-platform reproducibility
- Both are seeded identically for perfect reproducibility

The LCG uses:
- `a = 1664525`
- `c = 1013904223`  
- `m = 2^32`
- Formula: `state = (a * state + c) mod m`

This provides deterministic, cross-platform reproducible random numbers that match exactly between Python and C.

### Wilson Confidence Interval
The safety gate uses the Wilson score interval rather than the normal approximation because:
- More accurate for small sample sizes
- Better behaved at extreme probabilities (near 0% or 100%)
- Provides conservative upper bounds for safety-critical applications

Formula:
```
p̂ = successes / trials
z = 1.96 (for 95% confidence)

upper_bound = (p̂ + z²/2n + z√(p̂(1-p̂)/n + z²/4n²)) / (1 + z²/n)
```

## Workflow Trigger

The validation gate runs automatically on:
- Pull requests to `main` branch
- Manual workflow dispatch (for testing)

### Artifact Upload on Failure

When a validation gate fails, the workflow automatically uploads diagnostic artifacts to the `build/repro/` directory:

- **Reproducibility Check Failures**: Artifact `repro-traces` contains `py_trace.jsonl` and `c_trace.jsonl` for manual comparison
- **Safety Gate Failures**: Artifact `safety-gate-results` contains `results.jsonl` for statistical analysis

Artifacts are retained for 7 days and can be downloaded from the GitHub Actions run page.

## Exit Codes

All scripts follow standard Unix conventions:
- `0` = Success
- `1` = Failure

This allows the GitHub Actions workflow to fail fast on errors.

## Dependencies

### Python
- Python 3.11+ (no external dependencies)

### C
- GCC with C11 support
- Math library (`-lm`)

## Future Enhancements

- [ ] Configurable safety thresholds per file/module
- [ ] Integration with existing test suite
- [ ] Performance benchmarking gate
- [ ] Automated tuning of p_max based on historical data
