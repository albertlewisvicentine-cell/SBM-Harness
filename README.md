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
- Optional: cppcheck and clang-tidy for static analysis

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
└── Makefile          # Build system
```

## License

See LICENSE file for details.

## Important Note

This harness provides illustrative examples for safety auditors and integrators. All code must be reviewed and validated before use in production safety-critical systems.
