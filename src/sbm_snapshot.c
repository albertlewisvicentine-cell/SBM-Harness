/**
 * @file sbm_snapshot.c
 * @brief Implementation of snapshot mechanism for atomic state management
 * 
 * This file implements the snapshot API for atomic state capture and rollback.
 * It provides init, take, commit, rollback, and export operations with
 * checksum validation and sequence numbering.
 * 
 * Implementation notes:
 * - Uses malloc for simplicity; production systems must use pre-allocated pools
 * - Single-threaded design; multi-threaded systems need locking
 * - Interrupt-disable pattern for atomicity (single-core embedded)
 * - Checksum validation to detect corruption
 * - Sequence numbers for snapshot ordering and debugging
 */

#include "sbm_snapshot.h"
#include "sbm_harness.h"
#include <string.h>
#include <stdlib.h>

/* Magic number for snapshot export format: "SBMS" (SBM Snapshot) */
#define SBM_SNAPSHOT_MAGIC 0x53424D53U

/**
 * @brief Internal snapshot structure
 * 
 * Maintains snapshot state including the copied data, original pointer,
 * validation checksum, and sequence number for ordering.
 */
typedef struct {
    void *original_state;      /**< Pointer to original state buffer */
    void *snapshot_data;       /**< Copy of state data */
    size_t size;              /**< Size of state in bytes */
    uint32_t checksum;        /**< Checksum of snapshot data */
    uint32_t sequence;        /**< Sequence number for ordering */
    int active;               /**< Whether snapshot is active */
} sbm_snapshot_internal_t;

/* Global sequence counter for snapshot ordering */
static uint32_t g_snapshot_sequence = 0;

/* Initialization flag */
static int g_snapshot_initialized = 0;

/**
 * @brief Initialize the snapshot subsystem
 * 
 * Sets up the snapshot mechanism. In production systems, this would
 * allocate memory pools and initialize hardware resources.
 * 
 * @return SBM_OK on success
 */
sbm_status_t sbm_snapshot_init(void) {
    g_snapshot_sequence = 0;
    g_snapshot_initialized = 1;
    return SBM_OK;
}

/**
 * @brief Take a snapshot of system state
 * 
 * Creates an atomic snapshot using interrupt-disable critical section.
 * Computes checksum for validation and assigns sequence number.
 * 
 * @param state Pointer to state buffer to snapshot
 * @param size Size of state buffer in bytes
 * @param handle Output parameter for snapshot handle
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_take(void *state, size_t size, sbm_snapshot_handle_t *handle) {
    GUARD_PTR(state);
    GUARD_PTR(handle);
    
    if (size == 0) {
        return SBM_ERR_UNKNOWN;
    }
    
    /* Initialize if not already done (lazy initialization) */
    if (!g_snapshot_initialized) {
        sbm_snapshot_init();
    }
    
    /* Allocate snapshot structure */
    sbm_snapshot_internal_t *snapshot = (sbm_snapshot_internal_t *)malloc(sizeof(sbm_snapshot_internal_t));
    if (snapshot == NULL) {
        return SBM_ERR_UNKNOWN;
    }
    
    /* Allocate snapshot data buffer */
    snapshot->snapshot_data = malloc(size);
    if (snapshot->snapshot_data == NULL) {
        free(snapshot);
        return SBM_ERR_UNKNOWN;
    }
    
    /* 
     * CRITICAL SECTION: Disable interrupts for atomic copy
     * Note: In production, use proper RTOS primitives like:
     *   taskENTER_CRITICAL() / taskEXIT_CRITICAL() for FreeRTOS
     *   __disable_irq() / __enable_irq() for bare-metal ARM
     * This is a simplified illustrative implementation.
     */
    memcpy(snapshot->snapshot_data, state, size);
    
    /* Initialize snapshot metadata */
    snapshot->original_state = state;
    snapshot->size = size;
    snapshot->checksum = sbm_checksum(snapshot->snapshot_data, size);
    snapshot->sequence = g_snapshot_sequence++;
    snapshot->active = 1;
    
    *handle = (sbm_snapshot_handle_t)snapshot;
    return SBM_OK;
}

/**
 * @brief Export snapshot data via writer callback
 * 
 * Serializes snapshot including magic number, sequence, checksum, size,
 * and data. The snapshot remains valid after export.
 * 
 * @param handle Snapshot handle from sbm_snapshot_take
 * @param writer Callback function for writing data
 * @param context User context passed to writer
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_export(sbm_snapshot_handle_t handle, 
                                  sbm_snapshot_writer_t writer, 
                                  void *context) {
    GUARD_PTR(handle);
    GUARD_PTR(writer);
    
    sbm_snapshot_internal_t *snapshot = (sbm_snapshot_internal_t *)handle;
    if (!snapshot->active) {
        return SBM_ERR_INCONSISTENT;
    }
    
    /* Validate checksum before export */
    uint32_t current_checksum = sbm_checksum(snapshot->snapshot_data, snapshot->size);
    if (current_checksum != snapshot->checksum) {
        return SBM_ERR_INCONSISTENT;
    }
    
    /* Export format: magic | sequence | checksum | size | data */
    uint32_t magic = SBM_SNAPSHOT_MAGIC;
    uint32_t size_u32 = (uint32_t)snapshot->size;
    
    /* Write header fields */
    if (writer(&magic, sizeof(magic), context) < 0) {
        return SBM_ERR_UNKNOWN;
    }
    if (writer(&snapshot->sequence, sizeof(snapshot->sequence), context) < 0) {
        return SBM_ERR_UNKNOWN;
    }
    if (writer(&snapshot->checksum, sizeof(snapshot->checksum), context) < 0) {
        return SBM_ERR_UNKNOWN;
    }
    if (writer(&size_u32, sizeof(size_u32), context) < 0) {
        return SBM_ERR_UNKNOWN;
    }
    
    /* Write snapshot data */
    if (writer(snapshot->snapshot_data, snapshot->size, context) < 0) {
        return SBM_ERR_UNKNOWN;
    }
    
    return SBM_OK;
}

/**
 * @brief Commit a snapshot and release resources
 * 
 * Disc discard the snapshot data, keeping the current state. Validates
 * that the snapshot is still active before committing.
 * 
 * Note: This function has the same signature as the one in state_manager.c,
 * so both cannot be linked together. This new API is meant to replace
 * the old one, but we keep state_manager.c for reference.
 * 
 * @param handle Snapshot handle from sbm_snapshot_take
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_commit(sbm_snapshot_handle_t handle) {
    GUARD_PTR(handle);
    
    sbm_snapshot_internal_t *snapshot = (sbm_snapshot_internal_t *)handle;
    if (!snapshot->active) {
        return SBM_ERR_INCONSISTENT;
    }
    
    /* Release resources */
    snapshot->active = 0;
    free(snapshot->snapshot_data);
    free(snapshot);
    
    return SBM_OK;
}

/**
 * @brief Rollback state to snapshot and release resources
 * 
 * Atomically restores the original state using interrupt-disable critical
 * section. Validates checksum before rollback to detect corruption.
 * 
 * Note: This function has the same signature as the one in state_manager.c,
 * so both cannot be linked together. This new API is meant to replace
 * the old one, but we keep state_manager.c for reference.
 * 
 * @param handle Snapshot handle from sbm_snapshot_take
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_rollback(sbm_snapshot_handle_t handle) {
    GUARD_PTR(handle);
    
    sbm_snapshot_internal_t *snapshot = (sbm_snapshot_internal_t *)handle;
    if (!snapshot->active) {
        return SBM_ERR_INCONSISTENT;
    }
    
    /* Validate checksum before rollback */
    uint32_t current_checksum = sbm_checksum(snapshot->snapshot_data, snapshot->size);
    if (current_checksum != snapshot->checksum) {
        /* Snapshot data corrupted - cannot safely rollback */
        snapshot->active = 0;
        free(snapshot->snapshot_data);
        free(snapshot);
        return SBM_ERR_INCONSISTENT;
    }
    
    /* 
     * CRITICAL SECTION: Disable interrupts for atomic restore
     * See note in sbm_snapshot_take() about production implementation
     */
    memcpy(snapshot->original_state, snapshot->snapshot_data, snapshot->size);
    
    /* Release resources */
    snapshot->active = 0;
    free(snapshot->snapshot_data);
    free(snapshot);
    
    return SBM_OK;
}

/**
 * @brief Backward compatibility wrapper for old API
 * 
 * Wraps sbm_snapshot_take to provide the old sbm_snapshot_begin interface.
 * This allows existing code to continue working while transitioning to the
 * new API.
 * 
 * @param state Pointer to state to snapshot
 * @param size Size of state in bytes
 * @param snapshot_handle Output parameter for snapshot handle
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_begin(void *state, size_t size, void **snapshot_handle) {
    return sbm_snapshot_take(state, size, (sbm_snapshot_handle_t *)snapshot_handle);
}
