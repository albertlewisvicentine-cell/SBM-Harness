# SBM-Harness
Fault injection testing environment for Safe Bounded Memory (SBM) rules

## Overview

The SBM-Harness provides runtime guards and verification mechanisms for memory safety in C programs. It implements checks aligned with MISRA C:2012 guidelines and supports safety-critical embedded systems development.

## Documentation

For detailed information on SBM rules and their mapping to MISRA C:2012, see:
- [docs/SAFETY_MANUAL.md](docs/SAFETY_MANUAL.md) - Safety manual with rule mappings and enforcement strategies

## Building

The project uses a standard Makefile build system:

```bash
# Build all targets (library and tests)
make all

# Run all tests
make test

# Run individual test suites
make unit_tests
make fault_injection_suite
./build/unit_tests
./build/fault_injection_suite

# Static analysis
make cppcheck
make clang-tidy

# Clean build artifacts
make clean
```

## Requirements

- GCC with C11 support
- Make
- Python 3.7+ with PyYAML (for audit report generation)
- Optional: cppcheck and clang-tidy for static analysis

## Audit Report Generation

The SBM-Harness includes an automated audit report generator that creates safety case documentation from fault injection test results.

### Usage

```bash
# Generate an audit report from fault injection logs
python3 generate_audit_report.py
```

This reads:
- `PHYSICAL_CONSTANTS.md` - Physical constants table
- `sbm_config.yaml` - Environment configuration and safety goals
- `RECOVERY_LOGS.json` - Fault injection and recovery logs

And generates:
- `AUDIT_REPORT_AUTO.md` - Auto-generated audit report with traceability

### Configuration Files

- **PHYSICAL_CONSTANTS.md**: Defines physical constants used in safety validation
- **sbm_config.yaml**: Configures the operating environment and defines safety goals (GSN references)
- **RECOVERY_LOGS.json**: Contains fault injection test results and recovery evidence

The audit report provides:
1. Physical operating envelope validation
2. Safety goal traceability with evidence
3. Statistical success rates for fault detection/recovery
4. Sections for manual review and approval

## Project Structure

```
SBM-Harness/
├── include/          # Public header files
│   ├── sbm_types.h   # Status codes and types
│   └── sbm_harness.h # Guard macros and API
├── src/              # Implementation
│   ├── core_guards.c # Runtime checks and failure handler
│   └── state_manager.c # Snapshot/rollback mechanism
├── tests/            # Test suites
│   ├── unit_tests.c  # Unit tests
│   └── fault_injection.c # Fault injection tests
├── docs/             # Documentation
│   └── SAFETY_MANUAL.md # SBM to MISRA C:2012 mapping
├── evidence/         # Fault injection evidence artifacts
├── generate_audit_report.py  # Audit report generator
├── PHYSICAL_CONSTANTS.md      # Physical constants for validation
├── sbm_config.yaml           # Configuration and safety goals
├── RECOVERY_LOGS.json        # Fault injection test logs
└── Makefile          # Build system
```

## License

See LICENSE file for details.

## Important Note

This harness provides illustrative examples for safety auditors and integrators. All code must be reviewed and validated before use in production safety-critical systems.
