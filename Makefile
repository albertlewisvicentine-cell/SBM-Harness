# SBM-Harness Makefile
# Build system for SBM (Safe Bounded Memory) test harness

# Compiler and flags
CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -O2 -Iinclude -Itests
SIM_CFLAGS = -O3 -std=c11 -Wall -Wextra
BUILD_DIR = build

# Reproducibility test configuration
REPRO_SEED = 42

# Source files
# Note: state_manager.c is excluded to avoid duplicate symbol definitions.
# The new sbm_snapshot.c provides the same API plus enhanced functionality
# with backward compatibility wrappers. state_manager.c is kept in the repo
# for reference and documentation purposes.
SRC_FILES = src/core_guards.c src/sbm_snapshot.c
OBJ_FILES = $(patsubst src/%.c,$(BUILD_DIR)/%.o,$(SRC_FILES))

# Test executables
FAULT_INJECTION = $(BUILD_DIR)/fault_injection_suite
UNIT_TESTS = $(BUILD_DIR)/unit_tests

# Simulation executables for reproducibility checking
SIM_C = $(BUILD_DIR)/sim_c

# Default target
.PHONY: all
all: $(BUILD_DIR) $(FAULT_INJECTION) $(UNIT_TESTS) $(SIM_C)

# Create build directory
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Compile source files to object files
$(BUILD_DIR)/%.o: src/%.c include/sbm_harness.h include/sbm_types.h include/sbm_snapshot.h
	$(CC) $(CFLAGS) -c $< -o $@

# Build fault injection test suite
$(FAULT_INJECTION): tests/fault_injection.c $(OBJ_FILES)
	$(CC) $(CFLAGS) -o $@ $^

# Alias target for fault_injection_suite
.PHONY: fault_injection_suite
fault_injection_suite: $(FAULT_INJECTION)

# Build unit tests
$(UNIT_TESTS): tests/unit_tests.c $(OBJ_FILES)
	$(CC) $(CFLAGS) -o $@ $^

# Alias target for unit_tests
.PHONY: unit_tests
unit_tests: $(UNIT_TESTS)

# Build C simulation for reproducibility checking
$(SIM_C): sim.c | $(BUILD_DIR)
	$(CC) $(SIM_CFLAGS) -o $@ $< -lm

# Run reproducibility check (compares Python vs C simulation)
.PHONY: repro-check
repro-check: $(SIM_C)
	@echo "=== Running reproducibility check ==="
	@mkdir -p $(BUILD_DIR)/repro
	python3 simulation.py --seed $(REPRO_SEED) --out $(BUILD_DIR)/repro/py_trace.jsonl
	$(SIM_C) --seed $(REPRO_SEED) --out $(BUILD_DIR)/repro/c_trace.jsonl
	python3 repro_compare.py $(BUILD_DIR)/repro/py_trace.jsonl $(BUILD_DIR)/repro/c_trace.jsonl --rtol 1e-7
	@echo "=== Reproducibility check passed ==="

# Run statistical safety gate
.PHONY: safety-gate
safety-gate:
	@echo "=== Running statistical safety gate ==="
	@mkdir -p $(BUILD_DIR)/repro
	python3 run_batch.py --trials 1000 --out $(BUILD_DIR)/repro/results.jsonl
	python3 safety_gate.py $(BUILD_DIR)/repro/results.jsonl --p_max 0.01
	@echo "=== Safety gate passed ==="

# Run all tests
.PHONY: test
test: $(UNIT_TESTS) $(FAULT_INJECTION)
	@echo "=== Running unit tests ==="
	@$(UNIT_TESTS)
	@echo ""
	@echo "=== Running fault injection tests ==="
	@$(FAULT_INJECTION)
	@echo ""
	@echo "=== All tests completed ==="

# Static analysis with cppcheck
.PHONY: cppcheck
cppcheck:
	@which cppcheck > /dev/null || (echo "cppcheck not installed. Install with: sudo apt-get install cppcheck" && exit 1)
	cppcheck --enable=all --inconclusive --std=c11 -Iinclude src/ tests/ 2>&1

# Static analysis with clang-tidy
.PHONY: clang-tidy
clang-tidy:
	@which clang-tidy > /dev/null || (echo "clang-tidy not installed. Install with: sudo apt-get install clang-tidy" && exit 1)
	clang-tidy src/*.c tests/*.c -- $(CFLAGS)

# Clean build artifacts
.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
	rm -f *.jsonl

# Help target
.PHONY: help
help:
	@echo "SBM-Harness Makefile targets:"
	@echo "  all                  - Build all executables (default)"
	@echo "  fault_injection_suite - Build fault injection test suite"
	@echo "  unit_tests           - Build unit tests"
	@echo "  test                 - Run all tests"
	@echo "  repro-check          - Run reproducibility check (Python vs C)"
	@echo "  safety-gate          - Run statistical safety gate"
	@echo "  cppcheck             - Run cppcheck static analysis"
	@echo "  clang-tidy           - Run clang-tidy static analysis"
	@echo "  clean                - Remove build artifacts"
	@echo "  help                 - Show this help message"
