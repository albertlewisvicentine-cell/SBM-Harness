# SBM Safety Manual

## Introduction

This Safety Manual provides a mapping between Safe Bounded Memory (SBM) rules and MISRA C:2012 guidelines. The SBM-Guard-Harness implements runtime guards and verification mechanisms to enforce these rules in safety-critical embedded systems.

**Important**: This harness provides illustrative examples for safety auditors and integrators. All code must be reviewed and validated before use in production systems.

## SBM Rule Overview

The SBM (Safe Bounded Memory) rules (SBM-000 through SBM-011) define a comprehensive framework for memory safety in C programs. This manual focuses on four core rules with detailed enforcement strategies:

- **SBM-000**: Null pointer checks
- **SBM-002**: Array bounds validation
- **SBM-005**: Loop bound enforcement
- **SBM-010**: Error status propagation

Additional rules (SBM-001, SBM-003, SBM-004, SBM-006, SBM-007, SBM-008, SBM-009, SBM-011) cover initialization, lifetime management, synchronization, and resource cleanup. These are mentioned briefly with recommendations for enforcement.

---

## SBM-000: Null Pointer Checks

### Rule Description
All pointer dereferences must be preceded by an explicit null check. No pointer may be dereferenced without validation.

### Relevant MISRA C:2012 Clauses
- **Rule 1.3**: No undefined behavior shall occur
- **Rule 21.18**: The size_t type shall be used for pointer arithmetic
- **Directive 4.1**: Run-time failures shall be minimized

### Rationale
Null pointer dereferences cause undefined behavior and are a common source of safety-critical failures. Explicit validation ensures deterministic behavior and enables safe error recovery.

### Enforcement in Code

The harness provides the `GUARD_PTR(p)` macro defined in `include/sbm_harness.h`:

```c
#define GUARD_PTR(p) \
    do { \
        if ((p) == NULL) { \
            sbm_failure_handler(__FILE__, __LINE__, "Null pointer: " #p, SBM_ERR_NULL); \
            return SBM_ERR_NULL; \
        } \
    } while(0)
```

**Usage Example:**
```c
sbm_status_t process_data(int *data) {
    GUARD_PTR(data);  /* Validates data is not NULL */
    *data = 42;       /* Safe to dereference */
    return SBM_OK;
}
```

### Harness Enforcement
- The `GUARD_PTR` macro checks pointer validity before any dereference
- Failure triggers `sbm_failure_handler` with file/line diagnostics
- Returns `SBM_ERR_NULL` status for propagation up the call stack
- Static analyzers (cppcheck, clang-tidy) can verify macro usage

---

## SBM-002: Array Bounds Validation

### Rule Description
All array accesses must validate that the index is within the declared bounds [0, length). Out-of-bounds access is prohibited.

### Relevant MISRA C:2012 Clauses
- **Rule 18.1**: A pointer must not point outside of array bounds
- **Rule 21.17**: String handling functions shall not access beyond array limits
- **Directive 4.1**: Run-time failures shall be minimized

### Rationale
Buffer overflows and out-of-bounds accesses cause memory corruption and are exploitable vulnerabilities. Runtime validation prevents spatial memory errors.

### Enforcement in Code

The harness provides the `GUARD_INDEX(idx, len)` macro:

```c
#define GUARD_INDEX(idx, len) \
    do { \
        if ((idx) >= (len)) { \
            sbm_failure_handler(__FILE__, __LINE__, "Index out of bounds: " #idx, SBM_ERR_OOB); \
            return SBM_ERR_OOB; \
        } \
    } while(0)
```

**Usage Example:**
```c
sbm_status_t get_element(int *array, size_t idx, size_t length) {
    GUARD_PTR(array);
    GUARD_INDEX(idx, length);  /* Validates idx < length */
    return array[idx];
}
```

### Harness Enforcement
- Runtime bounds checking before every array access
- Helper function `sbm_check_bounds()` for programmatic validation
- Integration with static analyzers to verify all accesses are guarded
- Supports integration with hardware memory protection units (MPU)

---

## SBM-005: Loop Bound Enforcement

### Rule Description
All loops must have statically determinable or runtime-enforced iteration limits. Unbounded loops are prohibited in safety-critical code.

### Relevant MISRA C:2012 Clauses
- **Rule 14.2**: A for loop shall be well-formed
- **Directive 4.1**: Run-time failures shall be minimized
- **Rule 2.1**: Dead code shall not be present (prevents unreachable infinite loops)

### Rationale
Unbounded loops can cause system hangs, watchdog timeouts, and missed deadlines in real-time systems. Explicit bounds ensure predictable execution time.

### Enforcement in Code

The harness provides the `CHECK_LOOP_LIMIT(ctx, max)` macro with loop context tracking:

```c
typedef struct {
    uint32_t iteration;
    uint32_t max_iterations;
} sbm_loop_ctx_t;

#define CHECK_LOOP_LIMIT(ctx, max) \
    do { \
        (ctx).iteration++; \
        if ((ctx).iteration > (max)) { \
            sbm_failure_handler(__FILE__, __LINE__, "Loop limit exceeded", SBM_ERR_TIMEOUT); \
            return SBM_ERR_TIMEOUT; \
        } \
    } while(0)
```

**Usage Example:**
```c
sbm_status_t process_list(void) {
    sbm_loop_ctx_t ctx = {0, 1000};  /* Max 1000 iterations */
    
    while (has_more_data()) {
        CHECK_LOOP_LIMIT(ctx, 1000);  /* Enforce limit */
        process_next();
    }
    
    return SBM_OK;
}
```

### Harness Enforcement
- Explicit iteration counting with configurable limits
- Runtime detection of bound violations
- Integration with watchdog timers for system-level protection
- Static analysis can verify all loops have bounds

---

## SBM-010: Error Status Propagation

### Rule Description
Error conditions must be explicitly checked and propagated up the call stack without loss of diagnostic context. Silent failures are prohibited.

### Relevant MISRA C:2012 Clauses
- **Rule 17.7**: The value returned by a function having non-void return type shall be used
- **Directive 4.7**: Error information shall be checked after use
- **Rule 8.13**: Return values shall be checked

### Rationale
Silent error propagation masks failures and prevents proper error recovery. Explicit status checking ensures visibility of error conditions and enables defensive programming.

### Enforcement in Code

The harness provides `SBM_PROPAGATE_STATUS(s)` and `SBM_ASSERT(cond, status)` macros:

```c
#define SBM_PROPAGATE_STATUS(s) \
    do { \
        sbm_status_t _status = (s); \
        if (_status != SBM_OK) { \
            return _status; \
        } \
    } while(0)

#define SBM_ASSERT(cond, status) \
    do { \
        if (!(cond)) { \
            sbm_failure_handler(__FILE__, __LINE__, "Assertion failed: " #cond, status); \
            return status; \
        } \
    } while(0)
```

**Usage Example:**
```c
sbm_status_t high_level_operation(void) {
    sbm_status_t status;
    
    status = validate_inputs();
    SBM_PROPAGATE_STATUS(status);  /* Propagate errors */
    
    status = perform_operation();
    SBM_PROPAGATE_STATUS(status);
    
    return SBM_OK;
}
```

### Harness Enforcement
- All functions return `sbm_status_t` for explicit error indication
- Macros enforce status checking and propagation
- Compiler warnings (`-Wunused-result`) detect ignored return values
- Code reviews verify all status codes are checked

---

## Additional SBM Rules (Brief Overview)

### SBM-001: Initialization
**Rule**: All variables must be initialized before use.
**MISRA**: Rule 9.1 (automatic variable initialized before use)
**Enforcement**: Static analysis, `-Wuninitialized` compiler flag

### SBM-003: Lifetime Management
**Rule**: Memory shall not be accessed after deallocation.
**MISRA**: Rule 18.6 (pointer lifetime)
**Enforcement**: Ownership tracking, static analysis tools

### SBM-004: Alignment
**Rule**: Memory accesses must respect alignment requirements.
**MISRA**: Rule 11.1, 11.2 (pointer conversions)
**Enforcement**: Compiler alignment checks, hardware traps

### SBM-006: Synchronization
**Rule**: Shared data access requires proper synchronization.
**MISRA**: Directive 4.1 (concurrency)
**Enforcement**: Mutex guards, static race detection tools

### SBM-007: Resource Cleanup
**Rule**: All acquired resources must be released on all paths.
**MISRA**: Rule 22.1 (resource management)
**Enforcement**: RAII patterns, static leak detection

### SBM-008: Const Correctness
**Rule**: Use `const` for read-only data to prevent modification.
**MISRA**: Rule 8.9 (const qualification)
**Enforcement**: Compiler enforcement, code review

### SBM-009: Integer Overflow
**Rule**: Arithmetic operations must not overflow.
**MISRA**: Rule 12.1, 12.4 (expression evaluation)
**Enforcement**: Runtime checks, compiler sanitizers

### SBM-011: Side Effects
**Rule**: Expressions shall not have persistent side effects.
**MISRA**: Rule 13.5 (side effects)
**Enforcement**: Static analysis, code review

---

## Verification and Validation

### Static Analysis
The harness includes targets for automated checking:

```bash
make cppcheck      # Run cppcheck on all source files
make clang-tidy    # Run clang-tidy with MISRA checks
```

### Runtime Testing
```bash
make test          # Run unit tests and fault injection suite
```

### Code Review Checklist
- [ ] All pointers validated with `GUARD_PTR` before dereference
- [ ] All array accesses use `GUARD_INDEX` or equivalent bounds check
- [ ] All loops have explicit iteration limits with `CHECK_LOOP_LIMIT`
- [ ] All function return values checked with `SBM_PROPAGATE_STATUS`
- [ ] All error paths properly logged and handled
- [ ] Static analysis runs clean with no violations

### Traceability
Each guard macro failure logs:
- Source file and line number
- Descriptive error message
- Status code for classification
- Call stack context (via return path)

This enables full traceability from runtime failure to source code location for safety audits.

---

## Integration Guidelines

### Adapting for Production
1. Replace `sbm_failure_handler` with safety logging subsystem
2. Integrate with hardware watchdog and MPU
3. Pre-allocate snapshot buffers (avoid runtime malloc)
4. Add cryptographic checksums for critical data validation
5. Implement thread-safe versions with proper locking
6. Add formal verification annotations (e.g., ACSL, Frama-C)

### Safety Certification
- Document all deviations from MISRA C:2012
- Maintain traceability matrix: SBM rules → MISRA → implementation
- Perform code coverage analysis (MC/DC for safety-critical paths)
- Conduct safety audits at each integration milestone

---

## References

- **MISRA C:2012**: Guidelines for the use of the C language in critical systems
- **ISO 26262**: Road vehicles — Functional safety
- **IEC 61508**: Functional safety of electrical/electronic systems
- **SBM Rules**: Safe Bounded Memory framework (project-specific)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-12
**Review Required**: Before production use
