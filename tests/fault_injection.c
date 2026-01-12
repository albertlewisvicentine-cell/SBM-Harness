/**
 * @file fault_injection.c
 * @brief Fault injection test suite for SBM harness
 * 
 * This executable intentionally injects faults (null pointers, out-of-bounds
 * access, etc.) to demonstrate that the SBM harness correctly detects and
 * reports violations. Returns non-zero exit code on fault detection.
 */

#include "sbm_harness.h"
#include <stdio.h>
#include <string.h>

/**
 * @brief Test function that attempts null pointer access
 */
static sbm_status_t test_null_pointer(void) {
    int *ptr = NULL;
    GUARD_PTR(ptr);  /* Should trigger SBM_ERR_NULL */
    *ptr = 42;       /* Should never reach here */
    return SBM_OK;
}

/**
 * @brief Test function that attempts out-of-bounds access
 */
static sbm_status_t test_out_of_bounds(void) {
    int array[10];
    size_t idx = 15;  /* Out of bounds */
    GUARD_INDEX(idx, 10);  /* Should trigger SBM_ERR_OOB */
    array[idx] = 99;       /* Should never reach here */
    return SBM_OK;
}

/**
 * @brief Test function that exceeds loop limits
 */
static sbm_status_t test_loop_limit(void) {
    sbm_loop_ctx_t ctx = {0, 100};
    
    for (int i = 0; i < 150; i++) {
        CHECK_LOOP_LIMIT(ctx, 100);  /* Should trigger SBM_ERR_TIMEOUT at 101 */
    }
    
    return SBM_OK;
}

/**
 * @brief Test function demonstrating error propagation
 */
static sbm_status_t test_error_propagation(void) {
    sbm_status_t status = test_null_pointer();
    SBM_PROPAGATE_STATUS(status);  /* Should propagate the error */
    return SBM_OK;
}

/**
 * @brief Main test runner
 */
int main(void) {
    int fault_detected = 0;
    
    printf("=== SBM Fault Injection Test Suite ===\n\n");
    
    printf("Test 1: Null pointer detection...\n");
    if (test_null_pointer() != SBM_OK) {
        printf("  [PASS] Null pointer detected\n");
        fault_detected++;
    } else {
        printf("  [FAIL] Null pointer NOT detected\n");
    }
    
    printf("\nTest 2: Out-of-bounds detection...\n");
    if (test_out_of_bounds() != SBM_OK) {
        printf("  [PASS] Out-of-bounds detected\n");
        fault_detected++;
    } else {
        printf("  [FAIL] Out-of-bounds NOT detected\n");
    }
    
    printf("\nTest 3: Loop limit detection...\n");
    if (test_loop_limit() != SBM_OK) {
        printf("  [PASS] Loop limit exceeded detected\n");
        fault_detected++;
    } else {
        printf("  [FAIL] Loop limit NOT detected\n");
    }
    
    printf("\nTest 4: Error propagation...\n");
    if (test_error_propagation() != SBM_OK) {
        printf("  [PASS] Error propagated correctly\n");
        fault_detected++;
    } else {
        printf("  [FAIL] Error NOT propagated\n");
    }
    
    printf("\n=== Summary: %d/4 tests passed ===\n", fault_detected);
    
    /* Return 0 if all faults detected, non-zero otherwise */
    return (fault_detected == 4) ? 0 : 1;
}
