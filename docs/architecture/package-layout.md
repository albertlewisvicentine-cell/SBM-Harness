# Package Layout

The Python implementation lives in `src/sbm_harness/` and contains the reusable runtime modules:

- `event_validator.py` for registry-backed event validation
- `fault_engine.py` for physics-derived fault injection
- `models.py` and `registry_loader.py` for registry modeling and workbook loading
- `renderer.py` and `state_field.py` for visualization and drift-state handling
- `sbm_log_validator.py` for schema validation
- `simulation.py` and `safety_gate.py` for packaged validation utilities

Operational scripts that orchestrate repository workflows remain in `scripts/` so they can read and write repository-level assets without duplicating package responsibilities.
