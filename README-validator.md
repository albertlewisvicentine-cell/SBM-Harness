# SBM Log Validator (Node.js)

A Node.js validator for SBM-Harness log entries using [AJV](https://ajv.js.org/) (Another JSON Schema Validator).

## Features

- ✅ Validates SBM log entries against `sbm_log_schema.json`
- ✅ Supports single JSON objects, JSON arrays, and NDJSON (newline-delimited JSON)
- ✅ Strict validation mode with enhanced type checking
- ✅ Human-friendly error messages
- ✅ CLI and programmatic usage
- ✅ Custom ISO 8601 date-time validation

## Installation

```bash
npm install
```

This will install the required dependency: `ajv` (v8.12.0+)

## Usage

### Command Line Interface

**Validate a single JSON file:**
```bash
node validate-sbm-log.js samples/valid.json
```

**Validate a JSON array:**
```bash
node validate-sbm-log.js RECOVERY_LOGS.json
```

**Validate NDJSON (one JSON object per line):**
```bash
node validate-sbm-log.js samples/valid.ndjson
```

### Programmatic Usage

```javascript
const { validateLog } = require('./validate-sbm-log');

const logEntry = {
  schema_version: "1.0",
  event_type: "FAULT_INJECTION",
  timestamp: "2026-01-25T19:07:00Z",
  // ... other fields
};

const result = validateLog(logEntry);
if (result.valid) {
  console.log('Entry is valid!');
} else {
  console.error('Validation errors:', result.friendlyErrors);
}
```

## Sample Files

The `samples/` directory contains example files:

- **valid.json** - A valid SBM log entry
- **invalid.json** - An invalid entry (missing required fields)
- **valid.ndjson** - Valid NDJSON with multiple entries

## Validation Rules

The validator enforces the following rules from `sbm_log_schema.json`:

### Required Fields
- `schema_version` - Must be exactly `"1.0"`
- `event_type` - Must be one of: `FAULT_INJECTION`, `GUARD_TRIGGER`, `RECOVERY_ACTION`, `TEST_START`, `TEST_END`
- `timestamp` - Must be a valid ISO 8601 date-time string (e.g., `2026-01-25T19:07:00Z`)

### Optional Fields
- `seed` - Integer ≥ 0
- `gsn_ref` - Array of strings
- `fault_id` - String
- `description` - String
- `location` - Object with `file`, `line`, `function`
- `injected_fault` - Object with required `type` field
- `outcome` - Enum: `DETECTED_AND_RECOVERED`, `DETECTED_NOT_RECOVERED`, `NOT_DETECTED`, `N/A`
- `detection_mechanism` - String
- `recovery_action` - String
- `severity` - Enum: `critical`, `high`, `medium`, `low`
- `guard_type` - String
- `details` - Object
- `physical_params` - Object with optional fields like `temp_kelvin`, `v_core_mv`, `bit_flip_prob`, `timing_jitter_s`

## Error Messages

The validator provides human-friendly error messages:

```
❌ Invalid SBM log entry
  - / → Missing required field: "schema_version"
  - /timestamp → Invalid format (expected date-time ISO 8601)
```

## Exit Codes

- **0** - All entries are valid
- **1** - Validation failed or error processing file

## Comparison with Python Validator

This Node.js validator (`validate-sbm-log.js`) complements the existing Python validator (`sbm_log_validator.py`):

| Feature | Node.js | Python |
|---------|---------|--------|
| Schema validation | AJV (strict mode) | jsonschema |
| Date-time validation | Custom enhanced | Standard format |
| NDJSON support | ✅ | ✅ |
| CLI usage | ✅ | ✅ |
| Module export | ✅ | ✅ |

Both validators use the same schema file (`sbm_log_schema.json`) and should produce consistent results.

## Schema Improvements (Optional)

To make validation stricter, consider these schema modifications in `sbm_log_schema.json`:

1. **Disallow additional properties** (line 147):
   ```json
   "additionalProperties": false
   ```

2. **Stricter timestamp pattern** (line 32):
   ```json
   "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?(?:Z|[+-]\\d{2}:\\d{2})$"
   ```

3. **Require non-empty gsn_ref** (line 45):
   ```json
   "minItems": 1
   ```

## License

Licensed under Apache-2.0 (see LICENSE file)
