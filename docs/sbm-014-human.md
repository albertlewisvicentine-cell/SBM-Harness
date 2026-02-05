# SBM-014: Observable State Consistency

## Human-Readable Contract

**Version**: 1.0  
**Status**: Specification  
**Related Rules**: SBM-011 (Side Effects), SBM-000 (Null Checks), SBM-002 (Bounds)

---

## Purpose

SBM-014 defines rules for maintaining consistency of observable state in safety-critical systems. This rule ensures that runtime state (memory, I/O, sensors) remains coherent and traceable across all execution paths.

## Rule Statement

> **All observable state changes must be:**
> 1. **Atomic** - Either fully complete or fully absent (no partial updates)
> 2. **Logged** - Recorded with timestamp and causality chain
> 3. **Reversible** - Can be rolled back on error detection
> 4. **Verifiable** - Can be checked for consistency via checksum/invariant

---

## Why This Matters

In safety-critical embedded systems, inconsistent state can lead to:
- **Sensor fusion failures**: IMU, GPS, LIDAR data disagree
- **Control divergence**: Actuators receive conflicting commands
- **Safety mechanism bypass**: Watchdog sees stale heartbeat
- **Audit trail corruption**: Cannot reconstruct failure sequence

SBM-014 provides a contract between code and safety subsystems to prevent these failures.

---

## The Four Guarantees

### 1. Atomicity Guarantee

**Promise**: State updates are transactional.

**Implementation**:
```c
sbm_snapshot_handle_t snapshot = sbm_snapshot_create();

// Attempt state update
if (update_sensor_fusion(&state) == SBM_OK) {
    sbm_snapshot_commit(snapshot);  // Lock in changes
} else {
    sbm_snapshot_rollback(snapshot);  // Undo all changes
}
```

**Enforcement**: Use `sbm_snapshot_*` API from `include/sbm_snapshot.h`.

### 2. Logging Guarantee

**Promise**: Every state change is traceable.

**Implementation**:
```c
void update_critical_param(int new_value) {
    sbm_log_state_change("critical_param", old_value, new_value, 
                         __FILE__, __LINE__);
    critical_param = new_value;
}
```

**Enforcement**: Logs must conform to `sbm_log_schema.json` (schema version 1.0+).

### 3. Reversibility Guarantee

**Promise**: Errors can be recovered without data loss.

**Implementation**:
```c
typedef struct {
    int altitude_cm;
    int velocity_cmps;
    uint32_t checksum;
} flight_state_t;

// Before risky operation
flight_state_t backup = current_state;
if (attempt_maneuver(&current_state) != SBM_OK) {
    current_state = backup;  // Instant rollback
    trigger_safe_mode();
}
```

**Enforcement**: Critical state must be serializable and restorable.

### 4. Verifiability Guarantee

**Promise**: State integrity is continuously checked.

**Implementation**:
```c
uint32_t compute_state_checksum(flight_state_t *state) {
    return crc32((uint8_t*)state, 
                 offsetof(flight_state_t, checksum));
}

void verify_state_integrity(flight_state_t *state) {
    SBM_ASSERT(state->checksum == compute_state_checksum(state),
               SBM_ERR_INCONSISTENT);
}
```

**Enforcement**: Checksums recomputed after every critical operation.

---

## Integration with Echo Profiles

When SBM-014 violations occur, the Echo Profile level determines response:

| Violation | warn | slow | pause | confirm |
|-----------|------|------|-------|---------|
| Checksum mismatch | Log + continue | Log + delay 50ms | Log + wait for user | Log + require crypto auth |
| Rollback failure | Log + continue | Log + delay 100ms | Block until manual recovery | Halt + require signed recovery |
| Missing log entry | Log + continue | Log + delay 10ms | Block until entry added | Halt + audit investigation |

See `SAFETY_MANUAL.md` for full Echo Profile definitions.

---

## Worked Example: Sensor Fusion Update

```c
typedef struct {
    double imu_roll_deg;
    double gps_lat;
    double gps_lon;
    uint64_t timestamp_us;
    uint32_t checksum;
} sensor_state_t;

sbm_status_t update_sensor_fusion(sensor_state_t *state) {
    GUARD_PTR(state);  // SBM-000: Null check
    
    // 1. Atomicity: Create snapshot
    sbm_snapshot_handle_t snap = sbm_snapshot_create();
    
    sensor_state_t backup = *state;
    
    // 2. Logging: Record intent
    sbm_log_event("SENSOR_FUSION_UPDATE_START", 
                  state->timestamp_us);
    
    // Attempt state update
    sbm_status_t status = read_sensors(state);
    if (status != SBM_OK) {
        // 3. Reversibility: Rollback on error
        *state = backup;
        sbm_snapshot_rollback(snap);
        sbm_log_event("SENSOR_FUSION_UPDATE_FAILED", 
                      state->timestamp_us);
        return status;
    }
    
    // 4. Verifiability: Update checksum
    state->checksum = compute_state_checksum(state);
    
    SBM_ASSERT(state->checksum == compute_state_checksum(state),
               SBM_ERR_INCONSISTENT);
    
    sbm_snapshot_commit(snap);
    sbm_log_event("SENSOR_FUSION_UPDATE_SUCCESS", 
                  state->timestamp_us);
    
    return SBM_OK;
}
```

---

## Enforcement Strategy

### Compile-Time
- Use `-DSBM_ECHO_PROFILE_LEVEL=<level>` to lock response behavior
- Enable `-DSBM_STATE_VALIDATION` to force checksum generation
- Require all state structs to include `uint32_t checksum` field

### Runtime
- Checksum validation after every critical state update
- Snapshot/rollback on all error paths
- Log validation via `sbm_log_validator.py` before commit

### Audit
- Review all state-changing functions for SBM-014 compliance
- Verify log schemas match `sbm_log_schema.json`
- Check that Echo Profile is locked to appropriate level

---

## MISRA C:2012 Alignment

SBM-014 maps to multiple MISRA guidelines:

- **Rule 1.3**: No undefined behavior (via atomicity)
- **Rule 9.1**: All variables initialized (via snapshot restore)
- **Directive 4.7**: Error information checked (via verifiability)
- **Rule 17.7**: Function return values used (via status propagation)

---

## Testing Requirements

All code claiming SBM-014 compliance must pass:

1. **Fault injection**: Verify rollback works under error conditions
2. **Checksum mutation**: Verify detection of corrupted state
3. **Log validation**: All state changes appear in logs with schema compliance
4. **Snapshot stress**: Verify snapshot/commit/rollback under high frequency

See `tests/fault_injection.c` for reference test patterns.

---

## References

- `SAFETY_MANUAL.md` - SBM rules overview and Echo Profiles
- `include/sbm_snapshot.h` - Snapshot/rollback API
- `include/sbm_harness.h` - Guard macros (GUARD_PTR, SBM_ASSERT)
- `sbm_log_schema.json` - Log entry schema specification
- `sbm_log_validator.py` - Log validation tool

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-31 | Initial specification for SBM-014 observable state consistency |

---

**Review Status**: ✅ Human-readable contract established  
**Implementation Status**: ⚠️ Partial (snapshot API exists, `sbm_echo_profile_t` enum added, checksum validation needs extension)  
**Next Steps**: Implement Echo Profile runtime handlers, add checksum helper functions
