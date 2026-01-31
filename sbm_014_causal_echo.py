#!/usr/bin/env python3
"""
SBM-014-HUMAN: Causal Echo Contract
Registry: SBM-Harness
Version: 2026.1.0
Status: Canonical
Class: Reflection Translation Layer

Purpose:
    SBM-014-HUMAN ensures that causal reflection enforced by the core system
    is perceived by humans as *informative back-pressure*, not arbitrary failure.
    
    It preserves system equilibrium **without turning humans into entropy amplifiers**.

Invariant:
    A reflected action must return enough structured signal for a human
    to infer the violated invariant class and recover laminar behavior,
    without exposing internal system mechanics.

Placement:
    SBM-014-HUMAN operates **outside** the core mirror.
"""

from typing import Dict, Optional, Tuple
from enum import Enum


class InvariantClass(Enum):
    """
    High-level invariant classes that humans can reason about.
    These abstract away internal mechanics while preserving actionable information.
    """
    SPATIAL = "spatial"           # Memory bounds, spatial constraints
    TEMPORAL = "temporal"         # Timing, loop bounds, deadlines
    EXISTENTIAL = "existential"   # Null references, resource existence
    CONSISTENCY = "consistency"   # State consistency, data integrity
    UNKNOWN = "unknown"           # Unclassified or novel violation


class RecoveryStrategy(Enum):
    """
    High-level recovery strategies that guide human response.
    """
    VALIDATE_INPUTS = "validate_inputs"       # Check input preconditions
    INCREASE_BOUNDS = "increase_bounds"       # Expand resource limits
    CHECK_INITIALIZATION = "check_initialization"  # Verify initialization
    REVIEW_LOGIC = "review_logic"             # Review algorithm logic
    REDUCE_COMPLEXITY = "reduce_complexity"   # Simplify operation
    RETRY_WITH_BACKOFF = "retry_with_backoff" # Retry with delay


class CausalEcho:
    """
    Reflection Translation Layer for SBM-014-HUMAN.
    
    Transforms raw system reflections (error codes) into structured,
    human-interpretable signals that preserve causality without exposing
    internal mechanics.
    """
    
    # Mapping from SBM status codes to invariant classes
    INVARIANT_MAP = {
        "SBM_ERR_NULL": InvariantClass.EXISTENTIAL,
        "SBM_ERR_OOB": InvariantClass.SPATIAL,
        "SBM_ERR_TIMEOUT": InvariantClass.TEMPORAL,
        "SBM_ERR_INCONSISTENT": InvariantClass.CONSISTENCY,
        "SBM_ERR_UNKNOWN": InvariantClass.UNKNOWN,
    }
    
    # Mapping from invariant classes to recovery strategies
    RECOVERY_MAP = {
        InvariantClass.EXISTENTIAL: [
            RecoveryStrategy.CHECK_INITIALIZATION,
            RecoveryStrategy.VALIDATE_INPUTS,
        ],
        InvariantClass.SPATIAL: [
            RecoveryStrategy.VALIDATE_INPUTS,
            RecoveryStrategy.INCREASE_BOUNDS,
        ],
        InvariantClass.TEMPORAL: [
            RecoveryStrategy.REDUCE_COMPLEXITY,
            RecoveryStrategy.INCREASE_BOUNDS,
        ],
        InvariantClass.CONSISTENCY: [
            RecoveryStrategy.REVIEW_LOGIC,
            RecoveryStrategy.RETRY_WITH_BACKOFF,
        ],
        InvariantClass.UNKNOWN: [
            RecoveryStrategy.REVIEW_LOGIC,
        ],
    }
    
    # Human-readable descriptions for invariant classes
    INVARIANT_DESCRIPTIONS = {
        InvariantClass.EXISTENTIAL: (
            "A required resource or reference was not present when needed. "
            "This typically indicates missing initialization or invalid state assumptions."
        ),
        InvariantClass.SPATIAL: (
            "An operation attempted to access memory or resources outside allowed bounds. "
            "This indicates a constraint on size or position was violated."
        ),
        InvariantClass.TEMPORAL: (
            "An operation exceeded time or iteration constraints. "
            "This indicates the operation took too long or performed too many steps."
        ),
        InvariantClass.CONSISTENCY: (
            "The system detected an inconsistent state that violates safety invariants. "
            "This indicates a logic error or unexpected state transition."
        ),
        InvariantClass.UNKNOWN: (
            "The system detected a safety violation that does not fit standard patterns. "
            "This requires detailed investigation of the operation context."
        ),
    }
    
    # Human-readable recovery guidance
    RECOVERY_GUIDANCE = {
        RecoveryStrategy.CHECK_INITIALIZATION: (
            "Verify all required resources are properly initialized before use"
        ),
        RecoveryStrategy.VALIDATE_INPUTS: (
            "Check that all input parameters meet preconditions and are within valid ranges"
        ),
        RecoveryStrategy.INCREASE_BOUNDS: (
            "Consider increasing resource limits (array sizes, iteration counts, timeouts) if the operation is legitimate"
        ),
        RecoveryStrategy.REVIEW_LOGIC: (
            "Review the operation logic to ensure it correctly handles all cases and maintains invariants"
        ),
        RecoveryStrategy.REDUCE_COMPLEXITY: (
            "Simplify the operation or reduce the amount of work performed to meet constraints"
        ),
        RecoveryStrategy.RETRY_WITH_BACKOFF: (
            "Attempt the operation again after a delay, as the issue may be transient"
        ),
    }
    
    @classmethod
    def translate_reflection(
        cls,
        status_code: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Translate a raw system reflection into a structured causal echo.
        
        This is the primary interface for SBM-014-HUMAN. It takes a raw
        status code from the core system and returns a human-interpretable
        structured signal.
        
        Args:
            status_code: The SBM status code (e.g., "SBM_ERR_NULL")
            context: Optional context dictionary with keys:
                - 'file': Source file where violation occurred
                - 'line': Line number
                - 'msg': Raw error message
                - 'operation': High-level operation being performed
        
        Returns:
            Dictionary with structured causal echo containing:
                - 'invariant_class': The violated invariant category
                - 'description': Human-readable explanation
                - 'recovery_strategies': List of suggested recovery approaches
                - 'severity': Impact level (critical/high/medium/low)
                - 'context': Sanitized context (no internal mechanics)
        """
        context = context or {}
        
        # Infer invariant class from status code
        invariant_class = cls.INVARIANT_MAP.get(
            status_code,
            InvariantClass.UNKNOWN
        )
        
        # Get recovery strategies for this invariant class
        recovery_strategies = cls.RECOVERY_MAP.get(
            invariant_class,
            [RecoveryStrategy.REVIEW_LOGIC]
        )
        
        # Build structured response
        echo = {
            'invariant_class': invariant_class.value,
            'description': cls.INVARIANT_DESCRIPTIONS[invariant_class],
            'recovery_strategies': [
                {
                    'strategy': strategy.value,
                    'guidance': cls.RECOVERY_GUIDANCE[strategy]
                }
                for strategy in recovery_strategies
            ],
            'severity': cls._assess_severity(status_code, invariant_class),
            'context': cls._sanitize_context(context)
        }
        
        return echo
    
    @classmethod
    def _assess_severity(
        cls,
        status_code: str,
        invariant_class: InvariantClass
    ) -> str:
        """
        Assess the severity level of a violation.
        
        Args:
            status_code: The SBM status code
            invariant_class: The inferred invariant class
        
        Returns:
            Severity level string: 'critical', 'high', 'medium', or 'low'
        """
        # All violations are at least medium severity
        # Certain classes indicate critical issues
        if invariant_class == InvariantClass.EXISTENTIAL:
            return "critical"  # Null deref, missing resources
        elif invariant_class == InvariantClass.SPATIAL:
            return "critical"  # Memory corruption risk
        elif invariant_class == InvariantClass.CONSISTENCY:
            return "high"      # State corruption
        elif invariant_class == InvariantClass.TEMPORAL:
            return "high"      # Timing violations
        else:
            return "medium"    # Unknown or other
    
    @classmethod
    def _sanitize_context(cls, context: Dict) -> Dict:
        """
        Sanitize context to remove internal mechanics while preserving
        actionable information.
        
        Args:
            context: Raw context dictionary
        
        Returns:
            Sanitized context dictionary safe for human consumption
        """
        sanitized = {}
        
        # Include high-level operation if provided
        if 'operation' in context:
            sanitized['operation'] = context['operation']
        
        # Include location information (helps with debugging)
        # but abstract away specific implementation details
        if 'file' in context and 'line' in context:
            # Extract just filename, not full path
            filename = context['file'].split('/')[-1]
            sanitized['location'] = f"{filename}:{context['line']}"
        
        # Include sanitized message (remove internal variable names)
        if 'msg' in context:
            sanitized['message'] = cls._sanitize_message(context['msg'])
        
        return sanitized
    
    @classmethod
    def _sanitize_message(cls, msg: str) -> str:
        """
        Sanitize error message to remove internal variable names
        and implementation details.
        
        Args:
            msg: Raw error message
        
        Returns:
            Sanitized message for human consumption
        """
        # Remove specific variable names (e.g., "Null pointer: data" -> "Null pointer")
        if ': ' in msg:
            parts = msg.split(': ', 1)
            return parts[0]
        return msg
    
    @classmethod
    def format_for_display(cls, echo: Dict) -> str:
        """
        Format a causal echo for human-readable display.
        
        Args:
            echo: Structured causal echo from translate_reflection()
        
        Returns:
            Formatted string for display to humans
        """
        lines = []
        lines.append("=" * 70)
        lines.append("CAUSAL REFLECTION (SBM-014-HUMAN)")
        lines.append("=" * 70)
        lines.append(f"Severity: {echo['severity'].upper()}")
        lines.append(f"Invariant Class: {echo['invariant_class']}")
        lines.append("")
        lines.append("Description:")
        lines.append(f"  {echo['description']}")
        lines.append("")
        
        if echo.get('context'):
            lines.append("Context:")
            for key, value in echo['context'].items():
                lines.append(f"  {key}: {value}")
            lines.append("")
        
        lines.append("Recommended Recovery Strategies:")
        for i, strategy in enumerate(echo['recovery_strategies'], 1):
            lines.append(f"  {i}. {strategy['strategy']}")
            lines.append(f"     {strategy['guidance']}")
            lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)


def create_causal_echo_handler():
    """
    Create a handler function suitable for integration with C code.
    
    Returns:
        A handler function that can process SBM failures and return
        structured causal echoes.
    """
    def handler(status_code: str, file: str = "", line: int = 0, msg: str = "") -> Dict:
        """
        Handle an SBM failure and return a causal echo.
        
        Args:
            status_code: SBM error status code
            file: Source file where error occurred
            line: Line number where error occurred  
            msg: Raw error message
        
        Returns:
            Structured causal echo dictionary
        """
        context = {
            'file': file,
            'line': line,
            'msg': msg
        }
        
        return CausalEcho.translate_reflection(status_code, context)
    
    return handler


if __name__ == "__main__":
    # Demonstration of SBM-014-HUMAN
    print("SBM-014-HUMAN: Causal Echo Contract - Demonstration")
    print()
    
    # Example 1: Null pointer violation (EXISTENTIAL)
    print("Example 1: Null Pointer Violation")
    echo1 = CausalEcho.translate_reflection(
        "SBM_ERR_NULL",
        context={
            'file': 'src/core_guards.c',
            'line': 42,
            'msg': 'Null pointer: data',
            'operation': 'process_input'
        }
    )
    print(CausalEcho.format_for_display(echo1))
    
    # Example 2: Array bounds violation (SPATIAL)
    print("\nExample 2: Array Bounds Violation")
    echo2 = CausalEcho.translate_reflection(
        "SBM_ERR_OOB",
        context={
            'file': 'src/buffer_ops.c',
            'line': 156,
            'msg': 'Index out of bounds: idx',
            'operation': 'buffer_access'
        }
    )
    print(CausalEcho.format_for_display(echo2))
    
    # Example 3: Timeout violation (TEMPORAL)
    print("\nExample 3: Loop Timeout Violation")
    echo3 = CausalEcho.translate_reflection(
        "SBM_ERR_TIMEOUT",
        context={
            'file': 'src/algorithm.c',
            'line': 89,
            'msg': 'Loop limit exceeded',
            'operation': 'search_algorithm'
        }
    )
    print(CausalEcho.format_for_display(echo3))
    
    # Example 4: Consistency violation
    print("\nExample 4: State Consistency Violation")
    echo4 = CausalEcho.translate_reflection(
        "SBM_ERR_INCONSISTENT",
        context={
            'file': 'src/state_manager.c',
            'line': 203,
            'msg': 'Inconsistent state detected',
            'operation': 'state_validation'
        }
    )
    print(CausalEcho.format_for_display(echo4))
