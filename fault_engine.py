#!/usr/bin/env python3
"""
Physics-derived fault injection engine for SBM-Harness.

This module implements fault injection based on physical principles:
- Thermal noise floor (kBT) for bit flip probability
- Speed of light constraints (c-bound) for timing jitter
"""

import math
import random
import os


class PhysicsDerivedInjector:
    """
    Fault injector that derives injection parameters from physical principles.
    
    This class calculates fault injection probabilities and timing constraints
    based on fundamental physics constants and environmental parameters.
    """
    
    # Fundamental physics constants
    BOLTZMANN_CONSTANT = 1.380649e-23  # J/K
    ELEMENTARY_CHARGE = 1.602176e-19   # C
    SPEED_OF_LIGHT = 2.99792458e8      # m/s (exact value)
    
    # Material and circuit constants
    FR4_DIELECTRIC_SQRT = 2.12  # sqrt(4.5) for FR4 PCB material effective permittivity
    
    # Tunable parameters for bit flip probability scaling
    BASE_SCALE_FACTOR = 1e-6  # Empirical scaling factor for realistic bit flip probabilities
    
    # Timing jitter calculation parameters
    SAFETY_MARGIN_RATIO = 0.2  # 20% of clock period reserved for setup/hold times
    TIMING_VIOLATION_INDICATOR = 1e-15  # 1 femtosecond - indicates timing closure violation
    
    def __init__(self, env, seed=None):
        """
        Initialize the physics-derived injector.
        
        Args:
            env: Environment object with properties:
                - temp_kelvin: Temperature in Kelvin
                - v_core_mv: Core voltage in millivolts
                - pcb_trace_length_m: PCB trace length in meters (optional)
                - clock_period_s: Clock period in seconds (optional)
            seed: Random seed for reproducibility. If None, tries SBM_FAULT_SEED env var,
                  then falls back to None (non-deterministic)
        """
        self.env = env
        
        # Handle seed initialization for reproducibility
        if seed is None:
            seed = os.environ.get('SBM_FAULT_SEED')
            if seed is not None:
                seed = int(seed)
        
        self.seed = seed
        
        # Create a dedicated Random instance for this injector
        # This ensures each injector has independent, reproducible state
        if self.seed is not None:
            self._rng = random.Random(self.seed)
        else:
            self._rng = random.Random()
    
    def calculate_bit_flip_prob(self):
        """
        Derives probability based on Thermal Noise Floor (kBT).
        
        Higher temperature = higher variance = higher injection frequency.
        
        The probability is derived from the ratio of thermal energy (kT) to
        the energy barrier for a bit flip, which is related to the core voltage
        and elementary charge.
        
        Returns:
            float: Bit flip probability (0.0 to 1.0)
        """
        # Thermal energy (J)
        thermal_variance = self.BOLTZMANN_CONSTANT * self.env.temp_kelvin
        
        # Convert core voltage from mV to V
        v_core_v = self.env.v_core_mv / 1000.0
        
        # Energy barrier for a bit flip (approximation based on core voltage)
        # This represents the energy needed to flip a bit in CMOS logic
        energy_barrier = self.ELEMENTARY_CHARGE * v_core_v
        
        # Calculate bit flip probability using Arrhenius-like relationship
        # P = exp(-E_barrier / kT)
        # We scale and clamp to ensure reasonable probabilities
        if energy_barrier <= 0:
            # If no energy barrier, probability is maximum
            return 1.0
        
        # Raw probability from thermal activation
        raw_prob = math.exp(-energy_barrier / thermal_variance)
        
        # Apply scaling factor to account for actual circuit behavior
        # Real circuits have additional noise margins and error correction
        scaling_factor = self._calculate_scaling_factor(thermal_variance, v_core_v)
        
        # Final probability (clamped to [0, 1])
        prob = min(1.0, max(0.0, raw_prob * scaling_factor))
        
        return prob
    
    def _calculate_scaling_factor(self, thermal_variance, v_core_v):
        """
        Calculate a scaling factor based on thermal variance and core voltage.
        
        This function adjusts the raw thermal probability to account for
        real-world effects like noise margins, error correction, and circuit design.
        
        Args:
            thermal_variance: Thermal energy (kT) in Joules
            v_core_v: Core voltage in Volts
            
        Returns:
            float: Scaling factor (typically << 1 for realistic probabilities)
        """
        # Use empirically-derived base scaling factor
        # Lower values = more conservative (lower bit flip probability)
        base_scale = self.BASE_SCALE_FACTOR
        
        # Adjust based on voltage - lower voltage = less margin = higher probability
        # Normalize to typical 1.0V core voltage
        voltage_factor = 1.0 / max(0.1, v_core_v)
        
        # Adjust based on thermal energy - higher temperature = higher probability
        # Normalize to room temperature (300K -> kT ≈ 4.14e-21 J)
        thermal_factor = thermal_variance / (self.BOLTZMANN_CONSTANT * 300.0)
        
        return base_scale * voltage_factor * thermal_factor
    
    def calculate_timing_jitter(self):
        """
        Derives max permissible jitter based on the c-bound 
        of the PCB trace length and clock period.
        
        The speed of light creates a fundamental limit on signal propagation.
        This method ensures jitter doesn't violate causality or timing closure.
        
        Returns:
            float: Maximum permissible timing jitter in seconds
            
        Raises:
            AttributeError: If required environment attributes are missing
        """
        # Check for required attributes
        if not hasattr(self.env, 'pcb_trace_length_m'):
            raise AttributeError("Environment must have 'pcb_trace_length_m' attribute")
        if not hasattr(self.env, 'clock_period_s'):
            raise AttributeError("Environment must have 'clock_period_s' attribute")
        
        # Calculate signal propagation delay based on speed of light
        # Using effective speed in PCB (typically ~2/3 of c in vacuum due to FR4 dielectric)
        # Effective permittivity of FR4 ≈ 4.5, so v_eff = c / sqrt(4.5) ≈ c / 2.12
        effective_speed = self.SPEED_OF_LIGHT / self.FR4_DIELECTRIC_SQRT
        
        # Propagation delay for the PCB trace (round trip for worst case)
        propagation_delay = (2 * self.env.pcb_trace_length_m) / effective_speed
        
        # Maximum jitter must not exceed the clock period minus propagation delay
        # We also add a safety margin for setup/hold times
        safety_margin = self.SAFETY_MARGIN_RATIO * self.env.clock_period_s
        
        max_jitter = self.env.clock_period_s - propagation_delay - safety_margin
        
        # Ensure we don't return negative jitter (means timing closure is impossible)
        if max_jitter < 0:
            # Timing closure violation - return indicator value
            return self.TIMING_VIOLATION_INDICATOR
        
        return max_jitter
    
    def get_effective_seed(self):
        """
        Get the effective seed being used for this injector.
        
        Returns:
            int or None: The seed value, or None if non-deterministic
        """
        return self.seed
    
    def inject_random_fault(self, fault_probability=None):
        """
        Decide whether to inject a fault based on probability.
        
        Args:
            fault_probability: Probability of injecting fault (0.0-1.0).
                              If None, uses calculated bit flip probability.
        
        Returns:
            bool: True if fault should be injected, False otherwise
        """
        if fault_probability is None:
            fault_probability = self.calculate_bit_flip_prob()
        
        return self._rng.random() < fault_probability


class Environment:
    """
    Simple environment configuration for fault injection.
    
    This class holds the environmental parameters used by PhysicsDerivedInjector.
    """
    
    def __init__(self, temp_kelvin, v_core_mv, pcb_trace_length_m=None, clock_period_s=None):
        """
        Initialize environment parameters.
        
        Args:
            temp_kelvin: Temperature in Kelvin
            v_core_mv: Core voltage in millivolts
            pcb_trace_length_m: PCB trace length in meters (optional)
            clock_period_s: Clock period in seconds (optional)
        """
        self.temp_kelvin = temp_kelvin
        self.v_core_mv = v_core_mv
        if pcb_trace_length_m is not None:
            self.pcb_trace_length_m = pcb_trace_length_m
        if clock_period_s is not None:
            self.clock_period_s = clock_period_s


if __name__ == "__main__":
    # Example usage
    print("Physics-Derived Fault Injector Example")
    print("=" * 50)
    
    # Example 0: Demonstrate reproducibility with seeding
    print("\nScenario 0: Reproducibility with seeding")
    env0 = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
    injector0a = PhysicsDerivedInjector(env0, seed=42)
    injector0b = PhysicsDerivedInjector(env0, seed=42)
    print(f"  Both injectors use seed: {injector0a.get_effective_seed()}")
    # Both should give same results
    for i in range(3):
        fault_a = injector0a.inject_random_fault(0.5)
        fault_b = injector0b.inject_random_fault(0.5)
        print(f"  Trial {i+1}: Injector A={fault_a}, Injector B={fault_b}, Match={fault_a==fault_b}")
    
    # Example 1: Room temperature, 1.0V core
    env1 = Environment(temp_kelvin=300.0, v_core_mv=1000.0)
    injector1 = PhysicsDerivedInjector(env1, seed=12345)
    prob1 = injector1.calculate_bit_flip_prob()
    print(f"\nScenario 1: T=300K, V_core=1.0V, seed={injector1.get_effective_seed()}")
    print(f"  Bit flip probability: {prob1:.2e}")
    
    # Example 2: High temperature, lower voltage
    env2 = Environment(temp_kelvin=400.0, v_core_mv=800.0)
    injector2 = PhysicsDerivedInjector(env2)
    prob2 = injector2.calculate_bit_flip_prob()
    print(f"\nScenario 2: T=400K, V_core=0.8V")
    print(f"  Bit flip probability: {prob2:.2e}")
    print(f"  Increase factor: {prob2/prob1:.2f}x")
    
    # Example 3: Timing jitter calculation
    # 5cm PCB trace, 100MHz clock (10ns period)
    env3 = Environment(
        temp_kelvin=300.0,
        v_core_mv=1000.0,
        pcb_trace_length_m=0.05,
        clock_period_s=10e-9
    )
    injector3 = PhysicsDerivedInjector(env3)
    jitter3 = injector3.calculate_timing_jitter()
    print(f"\nScenario 3: PCB trace=5cm, Clock=100MHz")
    print(f"  Max permissible jitter: {jitter3*1e12:.2f} ps")
    print(f"  Jitter budget: {(jitter3/env3.clock_period_s)*100:.1f}% of clock period")
    
    # Example 4: Timing closure violation case
    env4 = Environment(
        temp_kelvin=300.0,
        v_core_mv=1000.0,
        pcb_trace_length_m=0.5,  # Long trace
        clock_period_s=1e-9      # Fast clock
    )
    injector4 = PhysicsDerivedInjector(env4)
    jitter4 = injector4.calculate_timing_jitter()
    print(f"\nScenario 4: PCB trace=50cm, Clock=1GHz (violation)")
    print(f"  Max permissible jitter: {jitter4*1e15:.2e} fs")
    print(f"  Status: Timing closure violation detected!")
