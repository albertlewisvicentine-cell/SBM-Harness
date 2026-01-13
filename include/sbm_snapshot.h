/**
 * @file sbm_snapshot.h
 * @brief Snapshot API for atomic state capture and rollback
 * 
 * This header provides the snapshot mechanism API for capturing system state,
 * enabling atomic commit or rollback operations. The implementation uses
 * interrupt-disable critical sections for single-core embedded systems.
 * 
 * Note: This is an illustrative implementation for demonstration purposes.
 * Production systems must use pre-allocated memory pools and certified RTOS
 * memory management instead of dynamic allocation.
 */

#ifndef SBM_SNAPSHOT_H
#define SBM_SNAPSHOT_H

#include "sbm_types.h"
#include <stddef.h>

/**
 * @brief Writer callback function for snapshot export
 * 
 * This callback is invoked by sbm_snapshot_export to serialize snapshot
 * data to persistent storage or transport. The writer should return the
 * number of bytes written, or a negative value on error.
 * 
 * @param data Pointer to data buffer to write
 * @param size Size of data buffer in bytes
 * @param context User-provided context pointer
 * @return Number of bytes written on success, negative on error
 */
typedef int (*sbm_snapshot_writer_t)(const void *data, size_t size, void *context);

/**
 * @brief Initialize the snapshot subsystem
 * 
 * Prepares the snapshot mechanism for use. Must be called before any
 * other snapshot operations. In production systems, this would set up
 * pre-allocated memory pools.
 * 
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_init(void);

/**
 * @brief Take a snapshot of system state
 * 
 * Creates an atomic snapshot of the specified state buffer. The snapshot
 * can later be committed (discarded) or rolled back (restored). Uses
 * interrupt-disable critical section for atomicity on single-core systems.
 * 
 * Implementation note: This function disables interrupts briefly during
 * the memory copy. For large state buffers, consider chunked operations
 * or DMA-based copying with appropriate synchronization.
 * 
 * @param state Pointer to state buffer to snapshot
 * @param size Size of state buffer in bytes
 * @param handle Output parameter for snapshot handle (must not be NULL)
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_take(void *state, size_t size, sbm_snapshot_handle_t *handle);

/**
 * @brief Commit a snapshot and release resources
 * 
 * Finalizes changes made to the state after the snapshot was taken.
 * The snapshot data is discarded and resources are released. After
 * commit, the handle is no longer valid.
 * 
 * @param handle Snapshot handle from sbm_snapshot_take
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_commit(sbm_snapshot_handle_t handle);

/**
 * @brief Rollback state to snapshot and release resources
 * 
 * Atomically restores the original state from the snapshot. Uses
 * interrupt-disable critical section for atomicity. After rollback,
 * the handle is no longer valid.
 * 
 * Implementation note: Rollback uses checksum validation to detect
 * corruption. If checksum fails, returns SBM_ERR_INCONSISTENT.
 * 
 * @param handle Snapshot handle from sbm_snapshot_take
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_rollback(sbm_snapshot_handle_t handle);

/**
 * @brief Export snapshot data via writer callback
 * 
 * Serializes the snapshot data by invoking the provided writer callback.
 * This enables persistent storage of snapshots for fault recovery or
 * debugging. The snapshot remains valid after export (can still commit
 * or rollback).
 * 
 * The export format includes:
 * - Magic number (4 bytes): 0x53424D53 ("SBMS")
 * - Sequence number (4 bytes): incrementing counter for ordering
 * - Checksum (4 bytes): validation checksum
 * - Data size (4 bytes): size of state data in bytes
 * - State data (variable): actual snapshot data
 * 
 * @param handle Snapshot handle from sbm_snapshot_take
 * @param writer Callback function for writing data
 * @param context User context passed to writer callback
 * @return SBM_OK on success, error code on failure
 */
sbm_status_t sbm_snapshot_export(sbm_snapshot_handle_t handle, 
                                  sbm_snapshot_writer_t writer, 
                                  void *context);

#endif /* SBM_SNAPSHOT_H */
