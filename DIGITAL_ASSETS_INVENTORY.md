# Digital Assets Inventory and Conflict Verification Report

**Repository**: SBM-Harness  
**Report Date**: 2026-02-07  
**Tool**: check_digital_assets.py

---

## Executive Summary

This report provides a comprehensive inventory of all digital assets in the SBM-Harness repository and verifies for any conflicts.

### Key Findings

✅ **No Critical Conflicts Detected**

- **Total Files**: 60
- **Total Size**: 264,902 bytes (258.7 KB)
- **Naming Conflicts**: 0
- **Content Conflicts**: 0
- **Configuration Conflicts**: 0
- **Dependency Conflicts**: 0

⚠️ **Licensing Note**: The repository contains 2 license files (MIT and Apache 2.0). This is **intentional dual-licensing** and not a conflict. The project offers users a choice between MIT or Apache 2.0 licenses.

---

## Digital Assets Inventory

### By Category

| Category | Count | Description |
|----------|-------|-------------|
| **Source Code** | 25 | Python, C, JavaScript, Header files |
| **Configuration** | 13 | YAML, JSON configuration files |
| **Documentation** | 10 | Markdown documentation |
| **Data** | 4 | CSV, NDJSON, Binary, Log files |
| **Package** | 3 | Dependency management files |
| **License** | 2 | MIT and Apache 2.0 licenses |
| **Build** | 2 | Makefile, Coverage config |
| **Other** | 1 | .gitignore |

### By Extension

| Extension | Count | Notes |
|-----------|-------|-------|
| `.py` | 15 | Python source files |
| `.json` | 11 | Configuration and data files |
| `.md` | 10 | Markdown documentation |
| `.c` | 6 | C source and test files |
| `.h` | 3 | C header files |
| `.yml/.yaml` | 3 | YAML configuration |
| Others | 12 | Various file types |

---

## Detailed Asset Breakdown

### 1. Source Code (25 files)

**Python Scripts (15)**:
- `check_digital_assets.py` - Asset inventory tool (NEW)
- `check_coverage.py` - Code coverage checker
- `fault_engine.py` - Fault injection engine
- `gate_runner.py` - Gate execution runner
- `generate_audit_report.py` - Audit report generator
- `repro_compare.py` - Reproducibility comparison
- `run_batch.py` - Batch execution runner
- `safety_gate.py` - Safety gate implementation
- `sbm_log_validator.py` - Log validation
- `simulation.py` - Simulation runner
- `test_fault_engine.py` - Fault engine tests
- `tests/test_audit_snapshots.py`
- `tests/test_log_validation.py`
- `tests/test_report_normalization.py`
- `tests/test_seeding.py`

**C Files (6)**:
- `sim.c` - Simulation core
- `src/core_guards.c` - Core guard implementation
- `src/sbm_snapshot.c` - Snapshot functionality
- `src/state_manager.c` - State management
- `tests/fault_injection.c` - Fault injection tests
- `tests/unit_tests.c` - Unit tests

**Header Files (3)**:
- `include/sbm_harness.h`
- `include/sbm_snapshot.h`
- `include/sbm_types.h`

**JavaScript (1)**:
- `validate-sbm-log.js` - JavaScript log validator

### 2. Configuration Files (13)

**CI/CD Workflows (2)**:
- `.github/workflows/ci.yml`
- `.github/workflows/validation-gate.yml`

**Configuration Files (4)**:
- `sbm_config.yaml` - Main configuration
- `sbm_log_schema.json` - Log schema
- `RECOVERY_LOGS.json` - Recovery logs
- `samples/valid.json` - Valid sample
- `samples/invalid.json` - Invalid sample

**Evidence Files (7)**: Located in `evidence/` directory
- SBM-001_spatial: overflow_violation.json
- SBM-004_existential: null_deref_snapshot.json
- SBM-007_sampling: trajectory_gap_snapshot.json
- SBM-009_numerical: drift_envelope_violation.json
- SBM-010_observability: atomic_snapshot.json, snapshot_metadata.json

### 3. Documentation (10)

**Main Documentation**:
- `README.md` - Primary project documentation (9,888 bytes)
- `README-validator.md` - Validator documentation
- `IMPROVEMENTS.md` - Improvement tracking (11,824 bytes)
- `PHYSICAL_CONSTANTS.md` - Physical constants reference
- `SUMMARY.md` - Project summary
- `VALIDATION_GATE.md` - Validation gate documentation

**Detailed Documentation** (docs/):
- `docs/SAFETY_MANUAL.md` - Safety manual (17,526 bytes - largest doc)
- `docs/SBM-014-HUMAN-CAUSAL-ECHO.md`
- `docs/sbm-014-human.md`

**Test Documentation**:
- `tests/golden/AUDIT_REPORT_GOLDEN.md` - Golden audit report

### 4. Data Files (4)

- `samples/valid.ndjson` - Valid NDJSON sample
- `evidence/SBM-001_spatial/memory_map_before_after.bin` - Binary memory map
- `evidence/SBM-009_numerical/stability_plot.csv` - CSV data
- `evidence/SBM-007_sampling/monitor_timing.log` - Timing log

### 5. Package Management (3)

**Python**:
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Python project configuration

**JavaScript**:
- `package.json` - Node.js dependencies

### 6. Build Configuration (2)

- `Makefile` - Build automation
- `.coveragerc` - Coverage configuration

### 7. Licensing (2)

- `LICENSE` - MIT License (1,082 bytes)
- `LICENSE.APACHE2` - Apache 2.0 License (11,357 bytes)

**Note**: Dual licensing is intentional and provides users with flexibility to choose either MIT or Apache 2.0.

---

## Conflict Verification Results

### ✅ Naming Conflicts: NONE

No files with duplicate names in different directories were found.

### ✅ Content Conflicts: NONE

No files with identical content but different names were found.

### ✅ Configuration Conflicts: NONE

All configuration files are unique and serve different purposes:
- No duplicate YAML/YML files with the same name
- No duplicate JSON config files with the same name

### ✅ Dependency Conflicts: NONE

**Single instance of each dependency file**:
- `requirements.txt` (Python) - 1 instance
- `package.json` (Node.js) - 1 instance
- `pyproject.toml` (Python build) - 1 instance

### ⚠️ License Files: INTENTIONAL DUAL-LICENSE

The repository contains 2 license files:
- `LICENSE` (MIT)
- `LICENSE.APACHE2` (Apache 2.0)

**Analysis**: This is **not a conflict**. Dual-licensing is a common practice that gives users the choice between two compatible open-source licenses:
- **MIT License**: More permissive, simpler terms
- **Apache 2.0**: More comprehensive, includes patent protection

Users can choose whichever license better suits their needs. Both licenses are permissive and compatible with each other.

---

## Repository Structure

```
SBM-Harness/
├── .github/
│   └── workflows/          # CI/CD workflows (2 files)
├── docs/                   # Documentation (3 files)
├── evidence/               # Test evidence (7 subdirs, 9 files)
│   ├── SBM-001_spatial/
│   ├── SBM-004_existential/
│   ├── SBM-007_sampling/
│   ├── SBM-009_numerical/
│   └── SBM-010_observability/
├── include/                # C header files (3 files)
├── samples/                # Sample data (3 files)
├── src/                    # C source code (3 files)
├── tests/                  # Test files (6 files)
│   └── golden/            # Golden reference (1 file)
├── *.py                    # Python scripts (15 files)
├── *.c                     # C source (1 file)
├── *.js                    # JavaScript (1 file)
├── *.md                    # Documentation (6 files)
├── LICENSE*                # License files (2 files)
├── Makefile                # Build configuration
├── requirements.txt        # Python deps
├── package.json            # Node.js deps
├── pyproject.toml          # Python config
└── ...                     # Other config files
```

---

## Size Distribution

**Largest Files**:
1. `docs/SAFETY_MANUAL.md` - 17,526 bytes
2. `check_digital_assets.py` - 12,793 bytes
3. `IMPROVEMENTS.md` - 11,824 bytes
4. `fault_engine.py` - 11,549 bytes
5. `tests/test_log_validation.py` - 11,666 bytes

**Total Repository Size**: 264,902 bytes (258.7 KB)

---

## Recommendations

### ✅ Current State is Healthy

1. **No Conflicts**: The repository has no naming, content, configuration, or dependency conflicts.
2. **Clean Structure**: Assets are well-organized into logical directories.
3. **Clear Purpose**: Each file has a distinct purpose with no duplicates.
4. **Dual Licensing**: The MIT + Apache 2.0 dual-licensing is intentional and beneficial.

### 📝 Optional Improvements

1. **Document Dual-Licensing**: Consider adding a note in the main README about the dual-licensing choice.
2. **Maintain Inventory**: Run `check_digital_assets.py` periodically to ensure no conflicts emerge as the project grows.
3. **Asset Documentation**: The current inventory provides a good baseline for tracking changes.

---

## How to Use This Report

### Running the Inventory Tool

```bash
# Run the digital assets inventory and conflict check
python3 check_digital_assets.py

# Output:
# - Console report with summary
# - DIGITAL_ASSETS_REPORT.json (detailed JSON report)
# - Exit code 0 (no conflicts) or 1 (conflicts detected)
```

### Interpreting Results

- **Exit Code 0**: No conflicts, repository is healthy
- **Exit Code 1**: Conflicts detected (review the report)
- **JSON Report**: Detailed machine-readable inventory for automation

### Continuous Monitoring

Add to CI/CD pipeline:
```yaml
- name: Check Digital Assets
  run: python3 check_digital_assets.py
```

---

## Conclusion

The SBM-Harness repository maintains a clean and well-organized digital asset structure with:
- **60 files** across 8 categories
- **No naming conflicts**
- **No content duplication**
- **No configuration conflicts**
- **No dependency conflicts**
- **Intentional dual-licensing** (MIT + Apache 2.0)

The repository is in excellent health with no conflicts requiring resolution.

---

**Report Generated By**: check_digital_assets.py  
**Version**: 1.0  
**Date**: 2026-02-07
