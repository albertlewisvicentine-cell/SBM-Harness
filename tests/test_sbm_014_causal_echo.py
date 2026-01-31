#!/usr/bin/env python3
"""
Unit tests for SBM-014-HUMAN: Causal Echo Contract
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sbm_014_causal_echo import (
    CausalEcho,
    InvariantClass,
    RecoveryStrategy,
    create_causal_echo_handler
)


class TestInvariantClassification(unittest.TestCase):
    """Test invariant class inference from status codes."""
    
    def test_null_pointer_maps_to_existential(self):
        """SBM_ERR_NULL should map to EXISTENTIAL invariant class."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        self.assertEqual(echo['invariant_class'], InvariantClass.EXISTENTIAL.value)
    
    def test_out_of_bounds_maps_to_spatial(self):
        """SBM_ERR_OOB should map to SPATIAL invariant class."""
        echo = CausalEcho.translate_reflection("SBM_ERR_OOB")
        self.assertEqual(echo['invariant_class'], InvariantClass.SPATIAL.value)
    
    def test_timeout_maps_to_temporal(self):
        """SBM_ERR_TIMEOUT should map to TEMPORAL invariant class."""
        echo = CausalEcho.translate_reflection("SBM_ERR_TIMEOUT")
        self.assertEqual(echo['invariant_class'], InvariantClass.TEMPORAL.value)
    
    def test_inconsistent_maps_to_consistency(self):
        """SBM_ERR_INCONSISTENT should map to CONSISTENCY invariant class."""
        echo = CausalEcho.translate_reflection("SBM_ERR_INCONSISTENT")
        self.assertEqual(echo['invariant_class'], InvariantClass.CONSISTENCY.value)
    
    def test_unknown_maps_to_unknown(self):
        """SBM_ERR_UNKNOWN should map to UNKNOWN invariant class."""
        echo = CausalEcho.translate_reflection("SBM_ERR_UNKNOWN")
        self.assertEqual(echo['invariant_class'], InvariantClass.UNKNOWN.value)
    
    def test_invalid_status_code_defaults_to_unknown(self):
        """Invalid status codes should default to UNKNOWN invariant class."""
        echo = CausalEcho.translate_reflection("INVALID_STATUS")
        self.assertEqual(echo['invariant_class'], InvariantClass.UNKNOWN.value)


class TestRecoveryStrategies(unittest.TestCase):
    """Test recovery strategy recommendations."""
    
    def test_existential_recovery_strategies(self):
        """EXISTENTIAL violations should suggest initialization and validation."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        strategies = [s['strategy'] for s in echo['recovery_strategies']]
        
        self.assertIn(RecoveryStrategy.CHECK_INITIALIZATION.value, strategies)
        self.assertIn(RecoveryStrategy.VALIDATE_INPUTS.value, strategies)
    
    def test_spatial_recovery_strategies(self):
        """SPATIAL violations should suggest validation and bounds increase."""
        echo = CausalEcho.translate_reflection("SBM_ERR_OOB")
        strategies = [s['strategy'] for s in echo['recovery_strategies']]
        
        self.assertIn(RecoveryStrategy.VALIDATE_INPUTS.value, strategies)
        self.assertIn(RecoveryStrategy.INCREASE_BOUNDS.value, strategies)
    
    def test_temporal_recovery_strategies(self):
        """TEMPORAL violations should suggest complexity reduction."""
        echo = CausalEcho.translate_reflection("SBM_ERR_TIMEOUT")
        strategies = [s['strategy'] for s in echo['recovery_strategies']]
        
        self.assertIn(RecoveryStrategy.REDUCE_COMPLEXITY.value, strategies)
        self.assertIn(RecoveryStrategy.INCREASE_BOUNDS.value, strategies)
    
    def test_consistency_recovery_strategies(self):
        """CONSISTENCY violations should suggest logic review and retry."""
        echo = CausalEcho.translate_reflection("SBM_ERR_INCONSISTENT")
        strategies = [s['strategy'] for s in echo['recovery_strategies']]
        
        self.assertIn(RecoveryStrategy.REVIEW_LOGIC.value, strategies)
        self.assertIn(RecoveryStrategy.RETRY_WITH_BACKOFF.value, strategies)
    
    def test_all_strategies_have_guidance(self):
        """All recovery strategies should include guidance text."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        
        for strategy in echo['recovery_strategies']:
            self.assertIn('strategy', strategy)
            self.assertIn('guidance', strategy)
            self.assertTrue(len(strategy['guidance']) > 0)


class TestSeverityAssessment(unittest.TestCase):
    """Test severity level assessment."""
    
    def test_null_pointer_is_critical(self):
        """Null pointer violations should be CRITICAL severity."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        self.assertEqual(echo['severity'], 'critical')
    
    def test_out_of_bounds_is_critical(self):
        """Out of bounds violations should be CRITICAL severity."""
        echo = CausalEcho.translate_reflection("SBM_ERR_OOB")
        self.assertEqual(echo['severity'], 'critical')
    
    def test_timeout_is_high(self):
        """Timeout violations should be HIGH severity."""
        echo = CausalEcho.translate_reflection("SBM_ERR_TIMEOUT")
        self.assertEqual(echo['severity'], 'high')
    
    def test_inconsistent_is_high(self):
        """Consistency violations should be HIGH severity."""
        echo = CausalEcho.translate_reflection("SBM_ERR_INCONSISTENT")
        self.assertEqual(echo['severity'], 'high')
    
    def test_unknown_is_medium(self):
        """Unknown violations should be MEDIUM severity."""
        echo = CausalEcho.translate_reflection("SBM_ERR_UNKNOWN")
        self.assertEqual(echo['severity'], 'medium')


class TestContextSanitization(unittest.TestCase):
    """Test context sanitization to prevent internal mechanics exposure."""
    
    def test_context_includes_operation(self):
        """Sanitized context should include operation name."""
        context = {
            'operation': 'test_operation',
            'file': '/full/path/to/file.c',
            'line': 42,
            'msg': 'Test message'
        }
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL", context)
        
        self.assertIn('operation', echo['context'])
        self.assertEqual(echo['context']['operation'], 'test_operation')
    
    def test_context_sanitizes_file_path(self):
        """Sanitized context should only include filename, not full path."""
        context = {
            'file': '/full/path/to/src/core_guards.c',
            'line': 42
        }
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL", context)
        
        self.assertIn('location', echo['context'])
        self.assertEqual(echo['context']['location'], 'core_guards.c:42')
        # Should NOT contain full path
        self.assertNotIn('/full/path', echo['context']['location'])
    
    def test_context_sanitizes_message(self):
        """Sanitized context should remove variable names from messages."""
        context = {
            'msg': 'Null pointer: internal_data_ptr'
        }
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL", context)
        
        self.assertIn('message', echo['context'])
        # Should remove variable name
        self.assertEqual(echo['context']['message'], 'Null pointer')
    
    def test_empty_context_handled_gracefully(self):
        """Empty context should not cause errors."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL", {})
        
        # Should still have a context field (may be empty)
        self.assertIn('context', echo)
    
    def test_none_context_handled_gracefully(self):
        """None context should not cause errors."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL", None)
        
        # Should still have a context field
        self.assertIn('context', echo)


class TestStructuredSignal(unittest.TestCase):
    """Test that structured signal contains required fields."""
    
    def test_echo_has_invariant_class(self):
        """Causal echo must include invariant_class field."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        self.assertIn('invariant_class', echo)
    
    def test_echo_has_description(self):
        """Causal echo must include description field."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        self.assertIn('description', echo)
        self.assertTrue(len(echo['description']) > 0)
    
    def test_echo_has_recovery_strategies(self):
        """Causal echo must include recovery_strategies field."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        self.assertIn('recovery_strategies', echo)
        self.assertIsInstance(echo['recovery_strategies'], list)
        self.assertGreater(len(echo['recovery_strategies']), 0)
    
    def test_echo_has_severity(self):
        """Causal echo must include severity field."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        self.assertIn('severity', echo)
        self.assertIn(echo['severity'], ['critical', 'high', 'medium', 'low'])
    
    def test_echo_has_context(self):
        """Causal echo must include context field."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        self.assertIn('context', echo)


class TestDisplayFormatting(unittest.TestCase):
    """Test human-readable display formatting."""
    
    def test_format_for_display_returns_string(self):
        """format_for_display should return a string."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        display = CausalEcho.format_for_display(echo)
        
        self.assertIsInstance(display, str)
        self.assertGreater(len(display), 0)
    
    def test_display_contains_header(self):
        """Display format should include SBM-014-HUMAN header."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        display = CausalEcho.format_for_display(echo)
        
        self.assertIn('SBM-014-HUMAN', display)
        self.assertIn('CAUSAL REFLECTION', display)
    
    def test_display_contains_severity(self):
        """Display format should show severity level."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        display = CausalEcho.format_for_display(echo)
        
        self.assertIn('Severity:', display)
        self.assertIn('CRITICAL', display)
    
    def test_display_contains_invariant_class(self):
        """Display format should show invariant class."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        display = CausalEcho.format_for_display(echo)
        
        self.assertIn('Invariant Class:', display)
        self.assertIn('existential', display)
    
    def test_display_contains_recovery_strategies(self):
        """Display format should list recovery strategies."""
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL")
        display = CausalEcho.format_for_display(echo)
        
        self.assertIn('Recovery Strategies:', display)
        self.assertIn('check_initialization', display)


class TestHandlerCreation(unittest.TestCase):
    """Test the handler function factory."""
    
    def test_handler_creation(self):
        """create_causal_echo_handler should return a callable."""
        handler = create_causal_echo_handler()
        self.assertTrue(callable(handler))
    
    def test_handler_accepts_parameters(self):
        """Handler should accept status_code and optional context."""
        handler = create_causal_echo_handler()
        
        # Should work with just status code
        echo1 = handler("SBM_ERR_NULL")
        self.assertIn('invariant_class', echo1)
        
        # Should work with full context
        echo2 = handler("SBM_ERR_NULL", file="test.c", line=10, msg="test")
        self.assertIn('invariant_class', echo2)
    
    def test_handler_returns_structured_echo(self):
        """Handler should return properly structured causal echo."""
        handler = create_causal_echo_handler()
        echo = handler("SBM_ERR_NULL", file="test.c", line=42, msg="Null pointer: data")
        
        # Verify structure
        self.assertIn('invariant_class', echo)
        self.assertIn('description', echo)
        self.assertIn('recovery_strategies', echo)
        self.assertIn('severity', echo)
        self.assertIn('context', echo)


class TestInvariantDescriptions(unittest.TestCase):
    """Test that all invariant classes have descriptions."""
    
    def test_all_invariant_classes_have_descriptions(self):
        """Every invariant class should have a human-readable description."""
        for invariant_class in InvariantClass:
            self.assertIn(
                invariant_class,
                CausalEcho.INVARIANT_DESCRIPTIONS,
                f"Missing description for {invariant_class}"
            )
            
            description = CausalEcho.INVARIANT_DESCRIPTIONS[invariant_class]
            self.assertIsInstance(description, str)
            self.assertGreater(len(description), 0)


class TestRecoveryGuidance(unittest.TestCase):
    """Test that all recovery strategies have guidance."""
    
    def test_all_strategies_have_guidance(self):
        """Every recovery strategy should have guidance text."""
        for strategy in RecoveryStrategy:
            self.assertIn(
                strategy,
                CausalEcho.RECOVERY_GUIDANCE,
                f"Missing guidance for {strategy}"
            )
            
            guidance = CausalEcho.RECOVERY_GUIDANCE[strategy]
            self.assertIsInstance(guidance, str)
            self.assertGreater(len(guidance), 0)


class TestNoInternalMechanicsExposure(unittest.TestCase):
    """Test that internal mechanics are not exposed in causal echoes."""
    
    def test_no_raw_pointers_in_output(self):
        """Output should not contain raw pointer addresses."""
        context = {
            'msg': 'Null pointer: data_ptr at 0x12345678'
        }
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL", context)
        display = CausalEcho.format_for_display(echo)
        
        # Should not contain memory addresses
        self.assertNotIn('0x', display)
    
    def test_no_internal_variable_names(self):
        """Output should not expose internal variable names."""
        context = {
            'msg': 'Null pointer: internal_state_machine_context_ptr'
        }
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL", context)
        
        # Sanitized message should not contain the variable name
        if 'message' in echo['context']:
            self.assertNotIn('internal_state_machine_context_ptr', echo['context']['message'])
    
    def test_no_full_file_paths(self):
        """Output should not expose full filesystem paths."""
        context = {
            'file': '/home/user/secret/project/internal/src/core.c',
            'line': 42
        }
        echo = CausalEcho.translate_reflection("SBM_ERR_NULL", context)
        
        # Should only have filename, not path
        self.assertEqual(echo['context']['location'], 'core.c:42')


if __name__ == '__main__':
    unittest.main(verbosity=2)
