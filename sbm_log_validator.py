#!/usr/bin/env python3
"""
Schema validator for SBM log entries.
Ensures backward compatibility and catches schema violations early.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import jsonschema
from jsonschema import validate, ValidationError


class SBMLogValidator:
    """Validator for SBM log entries using JSON Schema."""
    
    SCHEMA_VERSION = "1.0"
    
    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize validator with schema.
        
        Args:
            schema_path: Path to JSON schema file. Defaults to sbm_log_schema.json
        """
        if schema_path is None:
            # Default to schema in same directory as this script
            schema_path = Path(__file__).parent / "sbm_log_schema.json"
        
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
    
    def validate_entry(self, entry: Dict[str, Any]) -> bool:
        """
        Validate a single log entry against the schema.
        
        Args:
            entry: Log entry dictionary
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If entry doesn't match schema
        """
        try:
            validate(instance=entry, schema=self.schema)
            return True
        except ValidationError as e:
            raise ValidationError(f"Log entry validation failed: {str(e)}")
    
    def validate_log_file(self, log_path: Path) -> Tuple[int, List[str]]:
        """
        Validate all entries in a log file.
        
        Args:
            log_path: Path to log file (JSON or JSONL format)
            
        Returns:
            Tuple of (valid_count, error_messages)
        """
        errors = []
        valid_count = 0
        
        with open(log_path, 'r') as f:
            # Try to parse as JSON array first
            try:
                f.seek(0)
                content = f.read()
                entries = json.loads(content)
                if not isinstance(entries, list):
                    entries = [entries]
            except json.JSONDecodeError:
                # Try JSONL format (one JSON object per line)
                f.seek(0)
                entries = []
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        errors.append(f"Line {line_num}: Invalid JSON - {e}")
        
        # Validate each entry
        for idx, entry in enumerate(entries):
            try:
                self.validate_entry(entry)
                valid_count += 1
            except ValidationError as e:
                errors.append(f"Entry {idx}: {str(e)}")
        
        return valid_count, errors
    
    def check_schema_version(self, entry: Dict[str, Any]) -> bool:
        """
        Check if log entry has compatible schema version.
        
        Args:
            entry: Log entry dictionary
            
        Returns:
            True if schema version is compatible
        """
        entry_version = entry.get('schema_version', '0.0')
        return entry_version == self.SCHEMA_VERSION
    
    def add_schema_version(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add schema version to a log entry if not present.
        
        Args:
            entry: Log entry dictionary
            
        Returns:
            Updated entry with schema version
        """
        if 'schema_version' not in entry:
            entry['schema_version'] = self.SCHEMA_VERSION
        return entry


def validate_log_entries(log_entries: List[Dict[str, Any]], 
                         schema_path: Optional[Path] = None) -> bool:
    """
    Convenience function to validate a list of log entries.
    
    Args:
        log_entries: List of log entry dictionaries
        schema_path: Optional path to schema file
        
    Returns:
        True if all entries are valid
        
    Raises:
        ValidationError: If any entry is invalid
    """
    validator = SBMLogValidator(schema_path)
    
    for idx, entry in enumerate(log_entries):
        try:
            validator.validate_entry(entry)
        except ValidationError as e:
            raise ValidationError(f"Entry {idx} validation failed: {str(e)}")
    
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sbm_log_validator.py <log_file>")
        sys.exit(1)
    
    log_file = Path(sys.argv[1])
    
    if not log_file.exists():
        print(f"Error: File not found: {log_file}")
        sys.exit(1)
    
    validator = SBMLogValidator()
    
    print(f"Validating log file: {log_file}")
    print(f"Using schema version: {validator.SCHEMA_VERSION}")
    print("-" * 60)
    
    valid_count, errors = validator.validate_log_file(log_file)
    
    if errors:
        print(f"\n✗ Validation FAILED")
        print(f"  Valid entries: {valid_count}")
        print(f"  Errors: {len(errors)}")
        print("\nError details:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print(f"\n✓ Validation PASSED")
        print(f"  All {valid_count} entries are valid")
        sys.exit(0)
