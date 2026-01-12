# SBM-Harness Makefile
# Build system for SBM (Safe Bounded Memory) test harness

# Compiler and flags
CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -O2 -Iinclude -Itests
BUILD_DIR = build

# Source files
SRC_FILES = src/core_guards.c src/state_manager.c
OBJ_FILES = $(patsubst src/%.c,$(BUILD_DIR)/%.o,$(SRC_FILES))

# Test executables
FAULT_INJECTION = $(BUILD_DIR)/fault_injection_suite
UNIT_TESTS = $(BUILD_DIR)/unit_tests

# Default target
.PHONY: all
all: $(BUILD_DIR) $(FAULT_INJECTION) $(UNIT_TESTS)

# Create build directory
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Compile source files to object files
$(BUILD_DIR)/%.o: src/%.c include/sbm_harness.h include/sbm_types.h
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

# Help target
.PHONY: help
help:
	@echo "SBM-Harness Makefile targets:"
	@echo "  all                  - Build all executables (default)"
	@echo "  fault_injection_suite - Build fault injection test suite"
	@echo "  unit_tests           - Build unit tests"
	@echo "  test                 - Run all tests"
	@echo "  cppcheck             - Run cppcheck static analysis"
	@echo "  clang-tidy           - Run clang-tidy static analysis"
	@echo "  clean                - Remove build artifacts"
	@echo "  help                 - Show this help message"
