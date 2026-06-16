# Repository Structure

SBM-Harness is organized around a small top-level root with domain-specific subtrees:

- `artifacts/` for generated inventory and audit outputs
- `docs/architecture`, `docs/operations`, `docs/reports`, and `docs/specs` for curated documentation
- `scripts/` for standalone operational and reporting entrypoints
- `src/c/` for native C sources
- `src/js/` for the Node.js validator
- `src/sbm_harness/` for the Python package
- `tests/c/` and `tests/python/` for language-specific test suites

Repository-wide configuration and shared runtime data remain at the root, including `pyproject.toml`, `requirements.txt`, `sbm_config.yaml`, `sbm_log_schema.json`, `PHYSICAL_CONSTANTS.md`, and `RECOVERY_LOGS.json`.
