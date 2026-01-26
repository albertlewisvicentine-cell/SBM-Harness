#!/usr/bin/env python3
"""
Tests for deterministic seeding in fault injection.
"""

import unittest
import os
from fault_engine import PhysicsDerivedInjector, Environment


class TestDeterministicSeeding(unittest.TestCase):
    """Test cases for deterministic fault injection seeding."""
    
    def test_explicit_seed(self):
        """Test that explicit seed produces deterministic results."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        
        # Create two injectors with same seed
        injector1 = PhysicsDerivedInjector(env, seed=42)
        injector2 = PhysicsDerivedInjector(env, seed=42)
        
        # Both should return same random results
        results1 = [injector1.inject_random_fault(0.5) for _ in range(10)]
        results2 = [injector2.inject_random_fault(0.5) for _ in range(10)]
        
        self.assertEqual(results1, results2,
                        "Same seed should produce identical random results")
    
    def test_different_seeds(self):
        """Test that different seeds produce different results."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        
        injector1 = PhysicsDerivedInjector(env, seed=42)
        injector2 = PhysicsDerivedInjector(env, seed=99)
        
        results1 = [injector1.inject_random_fault(0.5) for _ in range(20)]
        results2 = [injector2.inject_random_fault(0.5) for _ in range(20)]
        
        # Very unlikely (but not impossible) to be identical with different seeds
        self.assertNotEqual(results1, results2,
                           "Different seeds should produce different results")
    
    def test_env_variable_seed(self):
        """Test that SBM_FAULT_SEED environment variable is used."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        
        # Set environment variable
        os.environ['SBM_FAULT_SEED'] = '12345'
        
        try:
            injector = PhysicsDerivedInjector(env)
            self.assertEqual(injector.get_effective_seed(), 12345,
                           "Should use seed from SBM_FAULT_SEED env var")
        finally:
            # Clean up
            del os.environ['SBM_FAULT_SEED']
    
    def test_explicit_seed_overrides_env(self):
        """Test that explicit seed takes precedence over env variable."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        
        # Set environment variable
        os.environ['SBM_FAULT_SEED'] = '99999'
        
        try:
            # Explicit seed should override env var
            injector = PhysicsDerivedInjector(env, seed=42)
            self.assertEqual(injector.get_effective_seed(), 42,
                           "Explicit seed should override env variable")
        finally:
            # Clean up
            del os.environ['SBM_FAULT_SEED']
    
    def test_no_seed_specified(self):
        """Test that no seed results in None (non-deterministic)."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        
        # Ensure env var is not set
        if 'SBM_FAULT_SEED' in os.environ:
            del os.environ['SBM_FAULT_SEED']
        
        injector = PhysicsDerivedInjector(env)
        self.assertIsNone(injector.get_effective_seed(),
                         "Should return None when no seed specified")
    
    def test_get_effective_seed(self):
        """Test get_effective_seed method."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        
        injector_seeded = PhysicsDerivedInjector(env, seed=12345)
        self.assertEqual(injector_seeded.get_effective_seed(), 12345)
        
        injector_unseeded = PhysicsDerivedInjector(env, seed=None)
        # Could be None or from env var
        seed = injector_unseeded.get_effective_seed()
        self.assertTrue(seed is None or isinstance(seed, int))
    
    def test_inject_random_fault_deterministic(self):
        """Test that inject_random_fault is deterministic with seed."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        
        # Run same sequence twice
        injector1 = PhysicsDerivedInjector(env, seed=777)
        sequence1 = [injector1.inject_random_fault(0.3) for _ in range(50)]
        
        injector2 = PhysicsDerivedInjector(env, seed=777)
        sequence2 = [injector2.inject_random_fault(0.3) for _ in range(50)]
        
        self.assertEqual(sequence1, sequence2,
                        "Same seed should produce identical fault injection sequence")
    
    def test_inject_random_fault_probability(self):
        """Test that inject_random_fault respects probability."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        injector = PhysicsDerivedInjector(env, seed=42)
        
        # Test with probability 0 - should never inject
        results_zero = [injector.inject_random_fault(0.0) for _ in range(100)]
        self.assertTrue(all(not r for r in results_zero),
                       "Probability 0.0 should never inject faults")
        
        # Test with probability 1 - should always inject
        injector2 = PhysicsDerivedInjector(env, seed=42)
        results_one = [injector2.inject_random_fault(1.0) for _ in range(100)]
        self.assertTrue(all(r for r in results_one),
                       "Probability 1.0 should always inject faults")
    
    def test_backward_compatibility(self):
        """Test that old code without seed still works."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        
        # Old style initialization (no seed parameter)
        injector = PhysicsDerivedInjector(env)
        
        # Should still calculate probabilities correctly
        prob = injector.calculate_bit_flip_prob()
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
        
        # Should still be able to inject faults
        result = injector.inject_random_fault(0.5)
        self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main(verbosity=2)
