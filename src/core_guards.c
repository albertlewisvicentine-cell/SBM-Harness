/**
 * @file core_guards.c
 * @brief Core runtime guard implementations for SBM harness
 * 
 * This file implements the failure handler and runtime checking functions
 * used by the SBM guard macros. These functions provide diagnostic output
 * and validation logic for safety-critical operations.
 */

#include "sbm_harness.h"
#include <stdio.h>
#include <stdint.h>

/**
 * @brief Failure handler implementation
 * 
 * Called when any SBM guard detects a violation. Logs detailed diagnostic
 * information to stderr for safety auditing. In a production system, this
 * would integrate with a safety logging or fault management subsystem.
 * 
 * @param file Source file where failure occurred
 * @param line Line number of failure
 * @param msg Descriptive error message
 * @param status Error status code
 */
void sbm_failure_handler(const char *file, int line, const char *msg, sbm_status_t status) {
    fprintf(stderr, "[SBM-GUARD] Failure at %s:%d - %s (status=%d)\n", 
            file, line, msg, status);
}

/**
 * @brief Simple checksum for data validation
 * 
 * Computes a basic checksum over a memory region. Used by guards to detect
 * data corruption. This is an illustrative implementation; production systems
 * should use cryptographic hash functions or CRC for critical data.
 * 
 * @param data Pointer to data buffer
 * @param size Size of buffer in bytes
 * @return 32-bit checksum value
 */
uint32_t sbm_checksum(const void *data, size_t size) {
    if (data == NULL || size == 0) {
        return 0;
    }
    
    const uint8_t *bytes = (const uint8_t *)data;
    uint32_t sum = 0;
    
    for (size_t i = 0; i < size; i++) {
        sum = (sum << 1) | (sum >> 31);  /* Rotate left by 1 */
        sum ^= bytes[i];
    }
    
    return sum;
}

/**
 * @brief Runtime index bounds check helper
 * 
 * Validates that an index is within bounds at runtime. Returns status
 * indicating success or bounds violation.
 * 
 * @param idx Index to validate
 * @param length Array length
 * @return SBM_OK if in bounds, SBM_ERR_OOB otherwise
 */
sbm_status_t sbm_check_bounds(size_t idx, size_t length) {
    if (idx >= length) {
        return SBM_ERR_OOB;
    }
    return SBM_OK;
}
