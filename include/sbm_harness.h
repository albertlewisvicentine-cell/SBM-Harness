/**
 * @file sbm_harness.h
 * @brief Public macros and runtime guards for SBM harness
 * 
 * This header provides macros for runtime safety checks including pointer
 * validation, bounds checking, and loop limit enforcement. These macros
 * implement SBM (Safe Bounded Memory) rules aligned with MISRA C:2012.
 */

#ifndef SBM_HARNESS_H
#define SBM_HARNESS_H

#include "sbm_types.h"
#include <stdio.h>
#include <stdint.h>

/**
 * @brief Validate pointer is non-null
 * 
 * Checks that a pointer is not NULL before dereferencing.
 * Implements SBM-000: Null pointer check enforcement.
 * 
 * @param p Pointer to validate
 * @return Returns SBM_ERR_NULL if pointer is NULL, otherwise continues
 */
#define GUARD_PTR(p) \
    do { \
        if ((p) == NULL) { \
            sbm_failure_handler(__FILE__, __LINE__, "Null pointer: " #p, SBM_ERR_NULL); \
            return SBM_ERR_NULL; \
        } \
    } while(0)

/**
 * @brief Validate array index is within bounds
 * 
 * Checks that an index is within the valid range [0, len).
 * Implements SBM-002: Array bounds checking.
 * 
 * Note: Both idx and len should be unsigned types. Signed integer
 * types may cause unexpected behavior with negative values.
 * 
 * @param idx Index value to check (should be unsigned)
 * @param len Length of the array (should be unsigned)
 * @return Returns SBM_ERR_OOB if index is out of bounds
 */
#define GUARD_INDEX(idx, len) \
    do { \
        if ((idx) >= (len)) { \
            sbm_failure_handler(__FILE__, __LINE__, "Index out of bounds: " #idx, SBM_ERR_OOB); \
            return SBM_ERR_OOB; \
        } \
    } while(0)

/**
 * @brief Check loop iteration limit
 * 
 * Enforces bounded loop behavior by checking iteration count against
 * the maximum specified in the context structure.
 * Implements SBM-005: Loop bound enforcement.
 * 
 * @param ctx Loop context structure (must have max_iterations set)
 * @return Returns SBM_ERR_TIMEOUT if iteration limit exceeded
 */
#define CHECK_LOOP_LIMIT(ctx) \
    do { \
        (ctx).iteration++; \
        if ((ctx).iteration > (ctx).max_iterations) { \
            sbm_failure_handler(__FILE__, __LINE__, "Loop limit exceeded", SBM_ERR_TIMEOUT); \
            return SBM_ERR_TIMEOUT; \
        } \
    } while(0)

/**
 * @brief Propagate error status up the call stack
 * 
 * Checks a status value and returns immediately if it indicates an error.
 * Implements SBM-010: Error propagation without loss of context.
 * 
 * @param s Status value to check
 * @return Returns s if it is not SBM_OK
 */
#define SBM_PROPAGATE_STATUS(s) \
    do { \
        sbm_status_t _status = (s); \
        if (_status != SBM_OK) { \
            return _status; \
        } \
    } while(0)

/**
 * @brief Assert a condition and return status on failure
 * 
 * Validates a runtime condition and returns the specified status on failure.
 * 
 * @param cond Condition to assert
 * @param status Status to return if condition is false
 */
#define SBM_ASSERT(cond, status) \
    do { \
        if (!(cond)) { \
            sbm_failure_handler(__FILE__, __LINE__, "Assertion failed: " #cond, status); \
            return status; \
        } \
    } while(0)

/**
 * @brief Failure handler called when safety checks fail
 * 
 * This function is invoked when any SBM guard macro detects a violation.
 * It logs diagnostic information for safety auditing and debugging.
 * 
 * @param file Source file where failure occurred
 * @param line Line number of failure
 * @param msg Descriptive error message
 * @param status Error status code
 */
void sbm_failure_handler(const char *file, int line, const char *msg, sbm_status_t status);

/**
 * @brief Runtime index bounds check helper
 * 
 * Validates that an index is within bounds at runtime.
 * 
 * @param idx Index to validate
 * @param length Array length
 * @return SBM_OK if in bounds, SBM_ERR_OOB otherwise
 */
sbm_status_t sbm_check_bounds(size_t idx, size_t length);

/**
 * @brief Simple checksum for data validation
 * 
 * Computes a basic checksum over a memory region.
 * 
 * @param data Pointer to data buffer
 * @param size Size of buffer in bytes
 * @return 32-bit checksum value
 */
uint32_t sbm_checksum(const void *data, size_t size);

/**
 * @brief Begin a state snapshot
 * 
 * Creates a snapshot of the specified state that can be committed or rolled back.
 * 
 * @param state Pointer to state to snapshot
 * @param size Size of state in bytes
 * @param snapshot_handle Output parameter for snapshot handle
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_begin(void *state, size_t size, void **snapshot_handle);

/**
 * @brief Commit a snapshot and release resources
 * 
 * Finalizes changes and releases snapshot resources.
 * 
 * @param snapshot_handle Snapshot handle from sbm_snapshot_begin
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_commit(void *snapshot_handle);

/**
 * @brief Rollback state to snapshot and release resources
 * 
 * Restores the original state from the snapshot and releases resources.
 * 
 * @param snapshot_handle Snapshot handle from sbm_snapshot_begin
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_rollback(void *snapshot_handle);

#endif /* SBM_HARNESS_H */
