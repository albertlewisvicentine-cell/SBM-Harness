/**
 * @file unit_tests.c
 * @brief Unit tests for SBM harness components
 * 
 * This file provides minimal unit tests for the SBM harness functionality.
 * Uses a simple assert-based runner without external dependencies.
 */

#include "sbm_harness.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>

/**
 * @brief Test snapshot and commit functionality
 */
static void test_snapshot_commit(void) {
    printf("Test: Snapshot commit...\n");
    
    int state = 42;
    void *snapshot_handle = NULL;
    
    sbm_status_t status = sbm_snapshot_begin(&state, sizeof(state), &snapshot_handle);
    assert(status == SBM_OK);
    assert(snapshot_handle != NULL);
    
    state = 100;  /* Modify state */
    
    status = sbm_snapshot_commit(snapshot_handle);
    assert(status == SBM_OK);
    assert(state == 100);  /* State should remain modified */
    
    printf("  [PASS]\n");
}

/**
 * @brief Test snapshot and rollback functionality
 */
static void test_snapshot_rollback(void) {
    printf("Test: Snapshot rollback...\n");
    
    int state = 42;
    void *snapshot_handle = NULL;
    
    sbm_status_t status = sbm_snapshot_begin(&state, sizeof(state), &snapshot_handle);
    assert(status == SBM_OK);
    
    state = 100;  /* Modify state */
    assert(state == 100);
    
    status = sbm_snapshot_rollback(snapshot_handle);
    assert(status == SBM_OK);
    assert(state == 42);  /* State should be restored */
    
    printf("  [PASS]\n");
}

/**
 * @brief Test bounds checking function
 */
static void test_bounds_check(void) {
    printf("Test: Bounds checking...\n");
    
    extern sbm_status_t sbm_check_bounds(size_t idx, size_t length);
    
    assert(sbm_check_bounds(0, 10) == SBM_OK);
    assert(sbm_check_bounds(9, 10) == SBM_OK);
    assert(sbm_check_bounds(10, 10) == SBM_ERR_OOB);
    assert(sbm_check_bounds(100, 10) == SBM_ERR_OOB);
    
    printf("  [PASS]\n");
}

/**
 * @brief Test checksum function
 */
static void test_checksum(void) {
    printf("Test: Checksum function...\n");
    
    extern uint32_t sbm_checksum(const void *data, size_t size);
    
    char data1[] = "test";
    char data2[] = "test";
    char data3[] = "TEST";
    
    uint32_t sum1 = sbm_checksum(data1, strlen(data1));
    uint32_t sum2 = sbm_checksum(data2, strlen(data2));
    uint32_t sum3 = sbm_checksum(data3, strlen(data3));
    
    assert(sum1 == sum2);  /* Same data should have same checksum */
    assert(sum1 != sum3);  /* Different data should have different checksum */
    assert(sbm_checksum(NULL, 10) == 0);  /* Null pointer should return 0 */
    
    printf("  [PASS]\n");
}

/**
 * @brief Test macro functionality (compile-time verification)
 */
static sbm_status_t helper_for_macro_test(int *ptr) {
    GUARD_PTR(ptr);
    return SBM_OK;
}

static void test_macros(void) {
    printf("Test: Guard macros...\n");
    
    int value = 10;
    assert(helper_for_macro_test(&value) == SBM_OK);
    assert(helper_for_macro_test(NULL) == SBM_ERR_NULL);
    
    printf("  [PASS]\n");
}

/**
 * @brief Main test runner
 */
int main(void) {
    printf("=== SBM Unit Tests ===\n\n");
    
    test_snapshot_commit();
    test_snapshot_rollback();
    test_bounds_check();
    test_checksum();
    test_macros();
    
    printf("\n=== All unit tests passed ===\n");
    return 0;
}
