/**
 * @file sbm_types.h
 * @brief Common types for SBM (Safe Bounded Memory) harness
 * 
 * This header defines status codes and types used throughout the SBM harness.
 * These types support runtime safety checks and loop bound verification.
 */

#ifndef SBM_TYPES_H
#define SBM_TYPES_H

#include <stddef.h>
#include <stdint.h>

/**
 * @brief Status codes returned by SBM harness functions
 * 
 * These status codes provide detailed information about the result of
 * safety-critical operations.
 */
typedef enum {
    SBM_OK = 0,              /**< Operation succeeded */
    SBM_ERR_NULL,            /**< Null pointer encountered */
    SBM_ERR_OOB,             /**< Out-of-bounds access detected */
    SBM_ERR_TIMEOUT,         /**< Operation timeout or loop bound exceeded */
    SBM_ERR_INCONSISTENT,    /**< Inconsistent state detected */
    SBM_ERR_UNKNOWN          /**< Unknown error */
} sbm_status_t;

/**
 * @brief Loop context for bounded iteration checking
 * 
 * This structure tracks loop iteration counts to ensure bounded behavior
 * and prevent infinite loops or excessive iterations.
 */
typedef struct {
    uint32_t iteration;      /**< Current iteration count */
    uint32_t max_iterations; /**< Maximum allowed iterations */
} sbm_loop_ctx_t;

/**
 * @brief Opaque handle for snapshot operations
 * 
 * This handle represents a snapshot of system state that can be
 * committed or rolled back. The internal structure is hidden from
 * users to maintain encapsulation.
 */
typedef void* sbm_snapshot_handle_t;

#endif /* SBM_TYPES_H */
