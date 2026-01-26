import json
import yaml
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Dict, List, Any


# ────────────────────────────────────────────────
# NORMALIZATION HELPERS FOR SNAPSHOT TESTING
# ────────────────────────────────────────────────
def normalize_timestamp(timestamp_str: str) -> str:
    """
    Normalize timestamp to a fixed value for snapshot testing.
    
    Args:
        timestamp_str: ISO 8601 timestamp string
        
    Returns:
        Normalized timestamp string
    """
    return "2026-01-01T00:00:00.000Z"


def normalize_float(value: float, precision: int = 8) -> float:
    """
    Normalize float to fixed precision to avoid minor differences.
    
    Args:
        value: Float value to normalize
        precision: Number of significant figures
        
    Returns:
        Normalized float value
    """
    if value == 0:
        return 0.0
    return round(value, precision)


def normalize_report_for_snapshot(content: str) -> str:
    """
    Normalize report content for snapshot testing by removing/standardizing dynamic parts.
    
    Args:
        content: Report content string
        
    Returns:
        Normalized content
    """
    # Replace timestamps
    content = re.sub(
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?',
        '2026-01-01T00:00:00.000Z',
        content
    )
    
    # Normalize file paths (remove absolute paths)
    content = re.sub(
        r'/[a-zA-Z0-9/_.-]+/SBM-Harness/',
        'SBM-Harness/',
        content
    )
    
    # Round floating point numbers to 6 decimal places
    def round_float_match(match):
        try:
            num = float(match.group(0))
            return f"{num:.6f}"
        except ValueError:
            return match.group(0)
    
    content = re.sub(
        r'\d+\.\d{7,}',
        round_float_match,
        content
    )
    
    return content

# ────────────────────────────────────────────────
# CONFIG & FILE PATHS (customize these)
# ────────────────────────────────────────────────
PHYS_CONSTANTS_MD = Path("PHYSICAL_CONSTANTS.md")   # Your constants table in markdown
SBM_CONFIG_YAML   = Path("sbm_config.yaml")
RECOVERY_LOGS_JSON = Path("RECOVERY_LOGS.json")
OUTPUT_MD         = Path("AUDIT_REPORT_AUTO.md")

# ────────────────────────────────────────────────
# Helper: Parse simple key-value table from PHYSICAL_CONSTANTS.md
# Assumes format like: | symbol | name | value | units |
# ────────────────────────────────────────────────
def parse_physical_constants_md(md_path: Path) -> Dict[str, Dict[str, str]]:
    if not md_path.exists():
        raise FileNotFoundError(f"Constants file not found: {md_path}")

    constants = {}
    in_table = False
    with md_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("|") and "symbol" in line.lower():
                in_table = True
                headers = [h.strip() for h in line.strip("|").split("|")]
                continue
            if in_table and line.startswith("|"):
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= 4:
                    symbol = cells[0].strip()
                    name   = cells[1].strip()
                    value  = cells[2].strip()
                    units  = cells[3].strip() if len(cells) > 3 else ""
                    constants[symbol] = {
                        "name": name,
                        "value": value,
                        "units": units
                    }
    return constants

# ────────────────────────────────────────────────
# Main generator
# ────────────────────────────────────────────────
def generate_audit_report():
    now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    # 1. Load physical constants
    phys_consts = parse_physical_constants_md(PHYS_CONSTANTS_MD)
    print(f"Parsed {len(phys_consts)} physical constants from {PHYS_CONSTANTS_MD}")

    # 2. Load sbm_config.yaml
    with SBM_CONFIG_YAML.open("r") as f:
        config = yaml.safe_load(f)
    env = config.get("environment", {})
    safety_goals = config.get("safety_goals", [])

    # 3. Load & analyze logs
    with RECOVERY_LOGS_JSON.open("r") as f:
        logs: List[Dict[str, Any]] = json.load(f)

    # Aggregate stats per GSN goal
    evidence_by_goal: Dict[str, Dict] = {}
    total_injections = 0
    detected_recovered = 0

    for entry in logs:
        # Only count FAULT_INJECTION events to avoid double counting
        if entry.get("event_type") == "FAULT_INJECTION":
            total_injections += 1
            is_recovered = entry.get("outcome") == "DETECTED_AND_RECOVERED"
            if is_recovered:
                detected_recovered += 1
            
            for gsn in entry.get("gsn_ref", []):
                if gsn not in evidence_by_goal:
                    evidence_by_goal[gsn] = {
                        "entries": [],
                        "detected_recovered": 0,
                        "total": 0
                    }
                evidence_by_goal[gsn]["entries"].append(entry)
                evidence_by_goal[gsn]["total"] += 1
                if is_recovered:
                    evidence_by_goal[gsn]["detected_recovered"] += 1

    # ────────────────────────────────────────────────
    # Build Markdown content
    # ────────────────────────────────────────────────
    md_lines = [
        "# Auto-Generated Audit Report – SBM-HARNESS Safety Case",
        f"**Generated:** {now}",
        f"**Run Environment:** {env}",
        "\n## 1. Physical Operating Envelope (Auto-Populated)",
        "| Symbol | Name | Config Value | Constant Value | Units | Notes |",
        "|--------|------|--------------|----------------|-------|-------|"
    ]

    # Example: pull relevant constants used in config (expand as needed)
    # Map config keys to physical constant symbols
    # Only include mappings for symbols that exist in PHYSICAL_CONSTANTS.md
    key_to_symbol = {
        "gravity": "g"
        # Future: Add "temperature": "T", "pressure": "P" when those constants are defined
    }
    
    for key, val in env.items():
        # Check for direct mapping
        sym = key_to_symbol.get(key)
        if sym and sym in phys_consts:
            c = phys_consts[sym]
            md_lines.append(f"| {sym} | {c['name']} | {val} | {c['value']} | {c['units']} | From config/env |")

    md_lines.extend([
        "\n## 2. Safety Goals & Evidence Traceability",
        "| GSN ID | Description | Injections | Detected & Recovered | Success Rate | Key Evidence |",
        "|--------|-------------|------------|-----------------------|--------------|--------------|"
    ])

    for goal in safety_goals:
        gid = goal.get("id", "N/A")
        desc = goal.get("description", "")
        stats = evidence_by_goal.get(gid, {"total": 0, "detected_recovered": 0})
        total = stats["total"]
        recovered = stats["detected_recovered"]
        rate = f"{recovered / total * 100:.1f}%" if total > 0 else "N/A"
        md_lines.append(f"| {gid} | {desc} | {total} | {recovered} | {rate} | See linked logs |")

    md_lines.extend([
        f"\n**Overall:** {detected_recovered}/{total_injections} faults injected → {detected_recovered / total_injections * 100:.2f}% recovery rate" if total_injections > 0 else "\n**Overall:** No fault injections recorded",
        "\n## 3. Deviations & Justifications",
        "[Manual review section – insert any observed deviations here]",
        "\n## 4. Approval",
        "Reviewed & Approved by: _______________________ Date: _______________ Signature: _______________"
    ])

    # Write output
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Audit report generated → {OUTPUT_MD}")

if __name__ == "__main__":
    try:
        generate_audit_report()
    except Exception as e:
        print(f"Error generating report: {e}")
