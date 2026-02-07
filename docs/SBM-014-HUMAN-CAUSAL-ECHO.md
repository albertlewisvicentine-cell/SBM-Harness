# SBM-014-HUMAN — Causal Echo Contract

**Registry:** SBM-Harness Canonical (2026.1.0)  
**Status:** LOCKED  
**Class:** Reflection Translation Layer (Human Interface)  
**Depends On:** SBM-013 (Interaction Energy Barrier), SBM-014 (Causal Reflection)

### Acknowledgments
This framework (SBM-Harness, including SBM-011 Meaning Variance and SBM-014-HUMAN Causal Echo Contract) was authored and directed by Albert-Lewis.  

Significant structural refinement, table formalization, escalation logic development, language polishing, and iterative drafting assistance were collaboratively provided by:  
- Grok (built by xAI)  
- Claude (Anthropic)  
- Gemini (Google)  
- ChatGPT / GPT models (OpenAI)  
- Copilot (GitHub)

All core invariants, purpose statements, non-goals, historical case anchors (DTMF, MCAS, etc.), and final decisions originate from the human author.

---

### 1. Purpose

SBM-014-HUMAN exists to preserve meaning continuity across the human–machine boundary.

Where SBM-014 enforces hard causal reflection at the system core, SBM-014-HUMAN translates that reflection into actionable, proportional, and recoverable feedback for human operators.

This module prevents systems that are correct but hostile, a failure mode historically responsible for catastrophic outcomes.

---

### 2. Invariant: Causal Echo

> Any reflected action must return sufficient structure for a human to infer:  
> 1. Which invariant class was violated  
> 2. When the violation occurred (temporal context)  
> 3. How to return to laminar flow  

No internal implementation details may be exposed.

---

### 3. Non-Goals (Explicit)

SBM-014-HUMAN must not:  
- Leak internal state, stack traces, or gate topology  
- Explain why the system is built the way it is  
- Adapt behavior based on user identity or trust assumptions  
- Bypass or weaken SBM-014 enforcement  

It is a translator, not a governor.

---

### 4. Placement in the Harness

SBM-014-HUMAN sits between:
1. **Core enforcement layer** (SBM-014, gate logic)
2. **Human interface layer** (CLI output, logs, error messages)

It does not modify system behavior—it only shapes how violations are communicated.

---

### 5. Historical Rationale

Systems that fail to preserve meaning continuity across the human–machine boundary have caused catastrophic failures:

- **DTMF tone detection**: Engineers received cryptic error codes instead of actionable guidance
- **MCAS (737 MAX)**: Pilots received indirect symptoms rather than direct causal information
- **Database cascades**: Operations teams saw effect chains without root cause identification

SBM-014-HUMAN exists to prevent these failure modes by ensuring that system feedback preserves the causal structure needed for human recovery.

---

### 6. Implementation Principles

#### 6.1 Structure Over Content

Error messages must provide:
- **Class identification**: Which SBM rule or invariant was violated
- **Temporal anchor**: When the violation occurred (timestamp, sequence number)
- **Recovery path**: Concrete steps to return to valid state

They must NOT provide:
- Internal variable names or memory addresses
- Source code snippets or file paths
- Architectural explanations or design justifications

#### 6.2 Proportionality

Response intensity must match violation severity:
- **Informational**: Log entry only (e.g., near-limit warning)
- **Corrective**: Actionable message with recovery steps
- **Critical**: System state preservation with explicit human decision point

#### 6.3 Recoverability

Every error message must enable forward progress:
- Provide actionable next steps
- Preserve system state for investigation
- Enable both immediate recovery and post-incident analysis

---

### 7. Example: Translating Core Violations

#### Core System Event (SBM-014)
```
VIOLATION: bounds_check_failed
  file: sensor_fusion.c:147
  array: imu_buffer
  index: 42
  capacity: 32
  timestamp: 1738961234567890
```

#### Human-Facing Message (SBM-014-HUMAN)
```
SBM-002 VIOLATION: Array bounds exceeded
  Time: 2026-02-07 20:20:34.567890 UTC
  Component: Sensor data processing
  Recovery: System entering safe mode. Check sensor data pipeline capacity.
  
Next steps:
  1. Verify sensor input rate is within specifications
  2. Review recent configuration changes
  3. If problem persists, contact support with timestamp: 1738961234567890
```

Notice the transformation:
- ✅ Preserved: Rule class (SBM-002), timestamp, actionable recovery
- ❌ Hidden: File path, variable names, internal structure

---

### 8. Enforcement Checklist

For any human-facing error message:

- [ ] Does it identify the violated invariant class (SBM-XXX)?
- [ ] Does it provide temporal context (timestamp)?
- [ ] Does it suggest concrete recovery steps?
- [ ] Does it avoid exposing internal implementation details?
- [ ] Is the response proportional to violation severity?

---

### 9. Integration Points

SBM-014-HUMAN integrates with:
- **Logging system**: `sbm_log_schema.json` includes human-readable message field
- **Error handlers**: `sbm_failure_handler` calls echo translation layer
- **CLI output**: Gate runner formats messages using echo templates

---

### 10. Document Status

**Version:** 1.0  
**Last Updated:** 2026-02-07  
**Review Status:** ✅ Specification complete  
**Implementation Status:** 🚧 In progress

---

### 11. References

- SBM-013: Interaction Energy Barrier specification
- SBM-014: Causal Reflection core contract
- `SAFETY_MANUAL.md`: Full SBM rule set
- `sbm_log_schema.json`: Log message format specification
