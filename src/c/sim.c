/*
 * Monte Carlo simulation for SBM-Harness validation (C implementation)
 * Must produce identical results to simulation.py for reproducibility check
 * Uses Simple LCG for exact cross-platform reproducibility
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

/* Simple Linear Congruential Generator (matches Python implementation) */
/* Parameters from Numerical Recipes: a=1664525, c=1013904223, m=2^32 */
typedef struct {
    uint32_t state;
} simple_lcg_t;

static void lcg_init(simple_lcg_t* rng, uint32_t seed) {
    rng->state = seed;
}

static uint32_t lcg_next_uint32(simple_lcg_t* rng) {
    rng->state = (1664525U * rng->state + 1013904223U);
    return rng->state;
}

static int lcg_randint(simple_lcg_t* rng, int min, int max) {
    /* Generate random integer in [min, max) */
    uint32_t range = (uint32_t)(max - min);
    return min + (int)(lcg_next_uint32(rng) % range);
}

static double lcg_random(simple_lcg_t* rng) {
    /* Generate random double in [0, 1) */
    return (double)lcg_next_uint32(rng) / 4294967296.0;  /* 2^32 */
}

int run_simulation(uint32_t seed, int num_steps, const char* output_file) {
    simple_lcg_t rng;
    lcg_init(&rng, seed);
    
    FILE* f = fopen(output_file, "w");
    if (!f) {
        fprintf(stderr, "Error: Cannot open output file %s\n", output_file);
        return 1;
    }
    
    int buffer_size = 100;
    int buffer_used = 0;
    int overflow_count = 0;
    
    for (int step = 0; step < num_steps; step++) {
        /* Simulate random memory allocation request (1-10 units) */
        int request = lcg_randint(&rng, 1, 11);
        
        const char* state;
        bool success;
        
        /* Try to allocate */
        if (buffer_used + request <= buffer_size) {
            buffer_used += request;
            state = "allocated";
            success = true;
        } else {
            state = "overflow_prevented";
            success = false;
            overflow_count++;
        }
        
        /* Random deallocation (10% chance if buffer is not empty) */
        if (buffer_used > 0 && lcg_random(&rng) < 0.1) {
            int dealloc_request = lcg_randint(&rng, 1, 11);
            int dealloc = dealloc_request < buffer_used ? dealloc_request : buffer_used;
            buffer_used -= dealloc;
            state = "deallocated";
        }
        
        /* Write trace event as JSONL */
        fprintf(f, "{\"step\": %d, \"state\": \"%s\", \"buffer_used\": %d, \"request\": %d, \"success\": %s}\n",
                step, state, buffer_used, request, success ? "true" : "false");
    }
    
    fclose(f);
    
    printf("Simulation completed: %d steps, %d overflows prevented\n", num_steps, overflow_count);
    
    return 0;
}

int main(int argc, char** argv) {
    uint32_t seed = 0;
    const char* output_file = NULL;
    int num_steps = 1000;
    
    /* Parse command line arguments */
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) {
            seed = (uint32_t)atoi(argv[++i]);
        } else if (strcmp(argv[i], "--out") == 0 && i + 1 < argc) {
            output_file = argv[++i];
        } else if (strcmp(argv[i], "--steps") == 0 && i + 1 < argc) {
            num_steps = atoi(argv[++i]);
        }
    }
    
    if (output_file == NULL) {
        fprintf(stderr, "Usage: %s --seed <seed> --out <output_file> [--steps <num_steps>]\n", argv[0]);
        return 1;
    }
    
    return run_simulation(seed, num_steps, output_file);
}
