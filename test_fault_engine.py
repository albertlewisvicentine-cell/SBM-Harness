#!/usr/bin/env python3
"""
Unit tests for fault_engine.py - PhysicsDerivedInjector class.
"""

import unittest
import math
from fault_engine import PhysicsDerivedInjector, Environment


class TestEnvironment(unittest.TestCase):
    """Test cases for the Environment class."""
    
    def test_basic_initialization(self):
        """Test basic environment initialization."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        self.assertEqual(env.temp_kelvin, 300.0)
        self.assertEqual(env.v_core_mv, 1000.0)
    
    def test_optional_parameters(self):
        """Test optional PCB and clock parameters."""
        env = Environment(
            temp_kelvin=350.0,
            v_core_mv=1200.0,
            pcb_trace_length_m=0.1,
            clock_period_s=1e-9
        )
        self.assertEqual(env.pcb_trace_length_m, 0.1)
        self.assertEqual(env.clock_period_s, 1e-9)
    
    def test_missing_optional_parameters(self):
        """Test that optional parameters can be omitted."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        self.assertFalse(hasattr(env, 'pcb_trace_length_m'))
        self.assertFalse(hasattr(env, 'clock_period_s'))


class TestPhysicsDerivedInjector(unittest.TestCase):
    """Test cases for the PhysicsDerivedInjector class."""
    
    def test_initialization(self):
        """Test injector initialization."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        injector = PhysicsDerivedInjector(env)
        
        # Check constants
        self.assertEqual(injector.k, 1.380649e-23)
        self.assertEqual(injector.e, 1.602176e-19)
        self.assertEqual(injector.c, 2.998e8)
        self.assertIs(injector.env, env)
    
    def test_bit_flip_prob_range(self):
        """Test that bit flip probability is in valid range [0, 1]."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        injector = PhysicsDerivedInjector(env)
        prob = injector.calculate_bit_flip_prob()
        
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
    
    def test_bit_flip_prob_temperature_dependency(self):
        """Test that higher temperature increases bit flip probability."""
        env_low = Environment(temp_kelvin=250.0, v_core_mv=1000.0)
        env_high = Environment(temp_kelvin=400.0, v_core_mv=1000.0)
        
        injector_low = PhysicsDerivedInjector(env_low)
        injector_high = PhysicsDerivedInjector(env_high)
        
        prob_low = injector_low.calculate_bit_flip_prob()
        prob_high = injector_high.calculate_bit_flip_prob()
        
        self.assertGreater(prob_high, prob_low,
                          "Higher temperature should increase bit flip probability")
    
    def test_bit_flip_prob_voltage_dependency(self):
        """Test that lower voltage increases bit flip probability."""
        env_high_v = Environment(temp_kelvin=300.0, v_core_mv=1200.0)
        env_low_v = Environment(temp_kelvin=300.0, v_core_mv=800.0)
        
        injector_high_v = PhysicsDerivedInjector(env_high_v)
        injector_low_v = PhysicsDerivedInjector(env_low_v)
        
        prob_high_v = injector_high_v.calculate_bit_flip_prob()
        prob_low_v = injector_low_v.calculate_bit_flip_prob()
        
        self.assertGreater(prob_low_v, prob_high_v,
                          "Lower voltage should increase bit flip probability")
    
    def test_bit_flip_prob_zero_voltage(self):
        """Test bit flip probability with zero voltage."""
        env = Environment(temp_kelvin=300.0, v_core_mv=0.0)
        injector = PhysicsDerivedInjector(env)
        prob = injector.calculate_bit_flip_prob()
        
        # Zero voltage means no energy barrier, should give max probability
        self.assertEqual(prob, 1.0)
    
    def test_timing_jitter_valid_case(self):
        """Test timing jitter calculation for a valid case."""
        # 5cm trace, 100MHz clock (10ns period)
        env = Environment(
            temp_kelvin=300.0,
            v_core_mv=1000.0,
            pcb_trace_length_m=0.05,
            clock_period_s=10e-9
        )
        injector = PhysicsDerivedInjector(env)
        jitter = injector.calculate_timing_jitter()
        
        # Jitter should be positive
        self.assertGreater(jitter, 0)
        # Jitter should be less than clock period
        self.assertLess(jitter, env.clock_period_s)
    
    def test_timing_jitter_violation_case(self):
        """Test timing jitter calculation when timing closure is violated."""
        # Very long trace or very fast clock should cause violation
        env = Environment(
            temp_kelvin=300.0,
            v_core_mv=1000.0,
            pcb_trace_length_m=1.0,  # 1 meter trace
            clock_period_s=1e-9      # 1GHz clock
        )
        injector = PhysicsDerivedInjector(env)
        jitter = injector.calculate_timing_jitter()
        
        # Should return very small value to indicate violation
        self.assertLess(jitter, 1e-12)  # Less than 1 picosecond
    
    def test_timing_jitter_missing_parameters(self):
        """Test that timing jitter raises error when parameters are missing."""
        # Environment without PCB and clock parameters
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        injector = PhysicsDerivedInjector(env)
        
        with self.assertRaises(AttributeError):
            injector.calculate_timing_jitter()
    
    def test_timing_jitter_only_missing_trace_length(self):
        """Test timing jitter with only PCB trace length missing."""
        env = Environment(
            temp_kelvin=300.0,
            v_core_mv=1000.0,
            clock_period_s=1e-9
        )
        injector = PhysicsDerivedInjector(env)
        
        with self.assertRaises(AttributeError) as context:
            injector.calculate_timing_jitter()
        self.assertIn('pcb_trace_length_m', str(context.exception))
    
    def test_timing_jitter_only_missing_clock_period(self):
        """Test timing jitter with only clock period missing."""
        env = Environment(
            temp_kelvin=300.0,
            v_core_mv=1000.0,
            pcb_trace_length_m=0.1
        )
        injector = PhysicsDerivedInjector(env)
        
        with self.assertRaises(AttributeError) as context:
            injector.calculate_timing_jitter()
        self.assertIn('clock_period_s', str(context.exception))
    
    def test_scaling_factor(self):
        """Test the internal scaling factor calculation."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        injector = PhysicsDerivedInjector(env)
        
        thermal_variance = injector.k * env.temp_kelvin
        v_core_v = env.v_core_mv / 1000.0
        
        scaling_factor = injector._calculate_scaling_factor(thermal_variance, v_core_v)
        
        # Scaling factor should be positive and typically small
        self.assertGreater(scaling_factor, 0)
        self.assertLess(scaling_factor, 1.0)
    
    def test_physics_constants(self):
        """Test that physics constants are correctly defined."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        injector = PhysicsDerivedInjector(env)
        
        # Boltzmann constant (J/K)
        self.assertAlmostEqual(injector.k, 1.380649e-23, places=30)
        
        # Elementary charge (C)
        self.assertAlmostEqual(injector.e, 1.602176e-19, places=25)
        
        # Speed of light (m/s)
        self.assertAlmostEqual(injector.c, 2.998e8, places=3)
    
    def test_realistic_scenario(self):
        """Test a realistic embedded system scenario."""
        # Typical embedded system: room temp, 3.3V logic, 10cm trace, 10MHz clock
        env = Environment(
            temp_kelvin=298.15,  # 25°C
            v_core_mv=3300.0,     # 3.3V
            pcb_trace_length_m=0.1,
            clock_period_s=100e-9  # 10MHz
        )
        injector = PhysicsDerivedInjector(env)
        
        # Calculate both metrics
        bit_flip_prob = injector.calculate_bit_flip_prob()
        timing_jitter = injector.calculate_timing_jitter()
        
        # Verify reasonable values
        self.assertGreater(bit_flip_prob, 0)
        self.assertLess(bit_flip_prob, 1)
        self.assertGreater(timing_jitter, 0)
        self.assertLess(timing_jitter, env.clock_period_s)


class TestPhysicsFormulas(unittest.TestCase):
    """Test that the physics formulas are correctly applied."""
    
    def test_thermal_energy_calculation(self):
        """Test that thermal energy (kT) is calculated correctly."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        injector = PhysicsDerivedInjector(env)
        
        expected_thermal_energy = injector.k * 300.0
        calculated_thermal_energy = injector.k * env.temp_kelvin
        
        self.assertAlmostEqual(calculated_thermal_energy, expected_thermal_energy)
    
    def test_energy_barrier_calculation(self):
        """Test energy barrier calculation from voltage."""
        env = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
        injector = PhysicsDerivedInjector(env)
        
        # Energy barrier should be e * V
        expected_barrier = injector.e * 1.0  # 1.0V
        thermal_variance = injector.k * env.temp_kelvin
        v_core_v = env.v_core_mv / 1000.0
        calculated_barrier = injector.e * v_core_v
        
        self.assertAlmostEqual(calculated_barrier, expected_barrier)
    
    def test_propagation_delay_physics(self):
        """Test that propagation delay follows c = distance/time."""
        env = Environment(
            temp_kelvin=300.0,
            v_core_mv=1000.0,
            pcb_trace_length_m=0.1,  # 10cm trace
            clock_period_s=100e-9
        )
        injector = PhysicsDerivedInjector(env)
        
        # In PCB (FR4), effective speed is c/2.12
        effective_speed = injector.c / 2.12
        
        # Round trip delay for 10cm trace
        expected_delay = (2 * env.pcb_trace_length_m) / effective_speed
        
        # Verify the calculation is consistent
        calculated_delay = (2 * 0.1) / (injector.c / 2.12)
        self.assertAlmostEqual(expected_delay, calculated_delay, places=15)


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
