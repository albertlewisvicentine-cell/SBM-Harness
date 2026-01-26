// validate-sbm-log.js
const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');
const ajv = new Ajv({
  allErrors: true,
  verbose: true,
  strict: true,               // Enforce stricter rules
  strictRequired: true,
  strictTypes: true
});

// Optional: better timestamp validation (AJV's date-time is lenient)
ajv.addFormat('date-time', {
  type: 'string',
  validate: (value) => {
    return !isNaN(Date.parse(value)) && (value.includes('T') && (value.includes('Z') || value.includes('+') || value.includes('-')));
  }
});

// Load your exact schema
const schemaPath = path.join(__dirname, 'sbm_log_schema.json');
let schema;
try {
  schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
} catch (err) {
  console.error('Failed to load schema:', err.message);
  process.exit(1);
}

const validate = ajv.compile(schema);

// Human-friendly error formatting
function formatErrors(errors) {
  if (!errors) return [];
  return errors.map(err => {
    let msg = err.message;
    if (err.keyword === 'required') {
      msg = `Missing required field: "${err.params.missingProperty}"`;
    } else if (err.keyword === 'enum') {
      msg = `Invalid value: must be one of ${err.params.allowedValues.map(v => `"${v}"`).join(', ')}`;
    } else if (err.keyword === 'const') {
      msg = `Must be exactly "${err.params.allowedValue}"`;
    } else if (err.keyword === 'format') {
      msg = `Invalid format (expected date-time ISO 8601)`;
    }
    const path = err.instancePath || '/';
    return `${path} → ${msg}`;
  });
}

function validateLog(logEntry) {
  const valid = validate(logEntry);
  if (valid) {
    console.log('✅ Valid SBM log entry');
    console.log('Event type:', logEntry.event_type);
    console.log('Timestamp:', logEntry.timestamp);
    return { valid: true };
  } else {
    console.error('❌ Invalid SBM log entry');
    const friendly = formatErrors(validate.errors);
    friendly.forEach(e => console.error(`  - ${e}`));
    return { valid: false, errors: validate.errors, friendlyErrors: friendly };
  }
}

// CLI: node validate-sbm-log.js <path-to-log.json>  (or .ndjson)
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('Usage: node validate-sbm-log.js <path-to-log.json OR .ndjson>');
    console.log('Supports single object or NDJSON (one entry per line)');
    process.exit(1);
  }

  const filePath = path.resolve(args[0]);
  try {
    const content = fs.readFileSync(filePath, 'utf8').trim();
    let entries;

    // Try to parse as regular JSON first
    try {
      const parsed = JSON.parse(content);
      if (Array.isArray(parsed)) {
        entries = parsed;
        console.log(`Validating ${entries.length} log entries from JSON array...`);
      } else {
        entries = [parsed];
        console.log('Validating single log entry...');
      }
    } catch (e) {
      // If regular JSON parsing fails, try NDJSON (one JSON per line)
      entries = content.split('\n').filter(line => line.trim()).map(line => JSON.parse(line));
      console.log(`Validating ${entries.length} log entries from NDJSON file...`);
    }

    let allValid = true;
    entries.forEach((entry, index) => {
      console.log(`\nEntry #${index + 1}:`);
      const result = validateLog(entry);
      if (!result.valid) allValid = false;
    });

    if (allValid) {
      console.log('\n🎉 All entries are valid!');
      process.exit(0);
    } else {
      console.log('\nSome entries failed validation.');
      process.exit(1);
    }
  } catch (err) {
    console.error('Error processing file:', err.message);
    process.exit(1);
  }
}

module.exports = { validateLog };
