# Auto-Generated Audit Report – SBM-HARNESS Safety Case
**Generated:** 2026-01-01T00:00:00.000Z
**Run Environment:** {'temperature': 298.15, 'pressure': 101325, 'gravity': 9.80665, 'max_iterations': 1000000, 'watchdog_timeout': 5.0, 'memory_limit': 268435456}

## 1. Physical Operating Envelope (Auto-Populated)
| Symbol | Name | Config Value | Constant Value | Units | Notes |
|--------|------|--------------|----------------|-------|-------|
| g | Standard Gravity | 9.80665 | 9.80665 | m/s² | From config/env |

## 2. Safety Goals & Evidence Traceability
| GSN ID | Description | Injections | Detected & Recovered | Success Rate | Key Evidence |
|--------|-------------|------------|-----------------------|--------------|--------------|
| G1 | All null pointer dereferences shall be detected and prevented | 1 | 1 | 100.0% | See linked logs |
| G2 | All array bounds violations shall be detected and prevented | 1 | 1 | 100.0% | See linked logs |
| G3 | All loop bounds shall be enforced with configurable limits | 1 | 1 | 100.0% | See linked logs |
| G4 | All error statuses shall be checked and propagated | 1 | 1 | 100.0% | See linked logs |
| G5 | Numerical overflow violations shall be prevented | 1 | 1 | 100.0% | See linked logs |
| G6 | Spatial memory violations shall be prevented | 1 | 1 | 100.0% | See linked logs |
| G7 | All reflected actions shall provide structured human-interpretable signals | 0 | 0 | N/A | See linked logs |

**Overall:** 5/5 faults injected → 100.00% recovery rate

## 3. Deviations & Justifications
[Manual review section – insert any observed deviations here]

## 4. Approval
Reviewed & Approved by: _______________________ Date: _______________ Signature: _______________