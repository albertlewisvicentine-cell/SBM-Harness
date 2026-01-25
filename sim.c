/*
 * Monte Carlo simulation for SBM-Harness validation (C implementation)
 * Must produce identical results to simulation.py for reproducibility check
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

/* Simple PCG32 random number generator for cross-platform reproducibility */
typedef struct {
    uint64_t state;
    uint64_t inc;
} pcg32_random_t;

static void pcg32_init(pcg32_random_t* rng, uint64_t seed) {
    rng->state = 0;
    rng->inc = (seed << 1u) | 1u;
    (void)rand(); /* Advance state */
    rng->state += seed;
    (void)rand(); /* Advance again */
}

static uint32_t pcg32_random(pcg32_random_t* rng) {
    uint64_t oldstate = rng->state;
    rng->state = oldstate * 6364136223846793005ULL + rng->inc;
    uint32_t xorshifted = (uint32_t)(((oldstate >> 18u) ^ oldstate) >> 27u);
    uint32_t rot = (uint32_t)(oldstate >> 59u);
    return (xorshifted >> rot) | (xorshifted << ((-rot) & 31));
}

static int pcg32_randint(pcg32_random_t* rng, int min, int max) {
    uint32_t range = (uint32_t)(max - min);
    return min + (int)(pcg32_random(rng) % range);
}

static double pcg32_random_double(pcg32_random_t* rng) {
    return (double)pcg32_random(rng) / (double)UINT32_MAX;
}

/* NumPy-compatible MT19937 implementation for exact reproducibility */
#define MT_N 624
#define MT_M 397
#define MT_MATRIX_A 0x9908b0dfUL
#define MT_UPPER_MASK 0x80000000UL
#define MT_LOWER_MASK 0x7fffffffUL

typedef struct {
    uint32_t mt[MT_N];
    int mti;
} mt19937_t;

static void mt19937_init(mt19937_t* rng, uint32_t seed) {
    rng->mt[0] = seed;
    for (rng->mti = 1; rng->mti < MT_N; rng->mti++) {
        rng->mt[rng->mti] = (1812433253UL * (rng->mt[rng->mti-1] ^ (rng->mt[rng->mti-1] >> 30)) + rng->mti);
    }
}

static uint32_t mt19937_random(mt19937_t* rng) {
    uint32_t y;
    static uint32_t mag01[2] = {0x0UL, MT_MATRIX_A};

    if (rng->mti >= MT_N) {
        int kk;
        for (kk = 0; kk < MT_N - MT_M; kk++) {
            y = (rng->mt[kk] & MT_UPPER_MASK) | (rng->mt[kk+1] & MT_LOWER_MASK);
            rng->mt[kk] = rng->mt[kk+MT_M] ^ (y >> 1) ^ mag01[y & 0x1UL];
        }
        for (; kk < MT_N - 1; kk++) {
            y = (rng->mt[kk] & MT_UPPER_MASK) | (rng->mt[kk+1] & MT_LOWER_MASK);
            rng->mt[kk] = rng->mt[kk+(MT_M-MT_N)] ^ (y >> 1) ^ mag01[y & 0x1UL];
        }
        y = (rng->mt[MT_N-1] & MT_UPPER_MASK) | (rng->mt[0] & MT_LOWER_MASK);
        rng->mt[MT_N-1] = rng->mt[MT_M-1] ^ (y >> 1) ^ mag01[y & 0x1UL];
        rng->mti = 0;
    }

    y = rng->mt[rng->mti++];
    y ^= (y >> 11);
    y ^= (y << 7) & 0x9d2c5680UL;
    y ^= (y << 15) & 0xefc60000UL;
    y ^= (y >> 18);

    return y;
}

static int mt19937_randint(mt19937_t* rng, int min, int max) {
    /* NumPy-compatible randint: [min, max) */
    uint32_t range = (uint32_t)(max - min);
    return min + (int)(mt19937_random(rng) % range);
}

static double mt19937_random_double(mt19937_t* rng) {
    /* Generate random double in [0, 1) matching NumPy */
    uint32_t a = mt19937_random(rng) >> 5;
    uint32_t b = mt19937_random(rng) >> 6;
    return (a * 67108864.0 + b) / 9007199254740992.0;
}

int run_simulation(uint32_t seed, int num_steps, const char* output_file) {
    mt19937_t rng;
    mt19937_init(&rng, seed);
    
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
        int request = mt19937_randint(&rng, 1, 11);
        
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
        if (buffer_used > 0 && mt19937_random_double(&rng) < 0.1) {
            int dealloc = buffer_used < 11 ? buffer_used : mt19937_randint(&rng, 1, 11);
            if (dealloc > buffer_used) dealloc = buffer_used;
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
