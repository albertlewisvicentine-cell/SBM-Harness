/**
 * @file state_manager.c
 * @brief Atomic snapshot and rollback mechanism for SBM harness
 * 
 * This file implements a simple snapshot/rollback mechanism for state
 * management in safety-critical operations. The implementation uses
 * stack-allocated buffers and is intentionally simple for auditability.
 * 
 * NOTE: This is an illustrative, single-threaded implementation for
 * demonstration purposes. Production systems should implement proper
 * atomic operations and thread-safety mechanisms.
 */

#include "sbm_harness.h"
#include <string.h>
#include <stdlib.h>

/**
 * @brief Internal snapshot structure
 * 
 * Maintains a copy of state that can be restored on rollback.
 */
typedef struct {
    void *original_state;   /**< Pointer to original state */
    void *snapshot_data;    /**< Copy of state data */
    size_t size;           /**< Size of state in bytes */
    int active;            /**< Whether snapshot is active */
} sbm_snapshot_t;

/**
 * @brief Begin a state snapshot
 * 
 * Creates a snapshot of the specified state that can be committed or
 * rolled back. The snapshot buffer is allocated on the heap for this
 * illustrative example; production systems should use pre-allocated pools.
 * 
 * @param state Pointer to state to snapshot
 * @param size Size of state in bytes
 * @param snapshot_handle Output parameter for snapshot handle
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_begin(void *state, size_t size, void **snapshot_handle) {
    GUARD_PTR(state);
    GUARD_PTR(snapshot_handle);
    
    if (size == 0) {
        return SBM_ERR_UNKNOWN;
    }
    
    sbm_snapshot_t *snapshot = (sbm_snapshot_t *)malloc(sizeof(sbm_snapshot_t));
    if (snapshot == NULL) {
        return SBM_ERR_UNKNOWN;
    }
    
    snapshot->snapshot_data = malloc(size);
    if (snapshot->snapshot_data == NULL) {
        free(snapshot);
        return SBM_ERR_UNKNOWN;
    }
    
    memcpy(snapshot->snapshot_data, state, size);
    snapshot->original_state = state;
    snapshot->size = size;
    snapshot->active = 1;
    
    *snapshot_handle = snapshot;
    return SBM_OK;
}

/**
 * @brief Commit a snapshot and release resources
 * 
 * Finalizes changes and releases snapshot resources. The current state
 * is kept and the snapshot is discarded.
 * 
 * @param snapshot_handle Snapshot handle from sbm_snapshot_begin
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_commit(void *snapshot_handle) {
    GUARD_PTR(snapshot_handle);
    
    sbm_snapshot_t *snapshot = (sbm_snapshot_t *)snapshot_handle;
    if (!snapshot->active) {
        return SBM_ERR_INCONSISTENT;
    }
    
    snapshot->active = 0;
    free(snapshot->snapshot_data);
    free(snapshot);
    
    return SBM_OK;
}

/**
 * @brief Rollback state to snapshot and release resources
 * 
 * Restores the original state from the snapshot and releases resources.
 * This implements atomic rollback for error recovery.
 * 
 * @param snapshot_handle Snapshot handle from sbm_snapshot_begin
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_rollback(void *snapshot_handle) {
    GUARD_PTR(snapshot_handle);
    
    sbm_snapshot_t *snapshot = (sbm_snapshot_t *)snapshot_handle;
    if (!snapshot->active) {
        return SBM_ERR_INCONSISTENT;
    }
    
    memcpy(snapshot->original_state, snapshot->snapshot_data, snapshot->size);
    
    snapshot->active = 0;
    free(snapshot->snapshot_data);
    free(snapshot);
    
    return SBM_OK;
}
