/* SPDX-License-Identifier: BSD-2-Clause */
/* Synthetic event schedules around the actual ledger. No OpenZFS pipeline,
 * provider, native runtime, DMA, pool or durability is exercised here. */
#include "pool-witness.h"
#include <errno.h>
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>

static struct aether_pool_witness witness;
static int leaf, file, foreign;
static _Atomic unsigned ready, go;
static struct aether_pool_token shared_token;
static _Atomic unsigned bind_winners, bind_denials;
typedef struct {
    uint64_t tx_txg;
} dmu_tx_t;
#define ASSERT(expression)                                                     \
    do {                                                                       \
        if (!(expression))                                                     \
            abort();                                                           \
    } while (0)
/* Pinned original getter/CDDL notices; the transaction itself is synthetic. */
#include "pool-target-body.inc"

#define REQUIRE(expression)                                                    \
    do {                                                                       \
        if (!(expression)) {                                                   \
            fprintf(stderr, "pool witness rejection: %s\n", #expression);      \
            return 1;                                                          \
        }                                                                      \
    } while (0)

static void init(void) { aether_pool_witness_init(&witness, &leaf, &file, 7); }
static struct aether_pool_token begin(enum aether_pool_io_kind kind)
{
    return aether_pool_io_begin(&witness, kind,
                                kind == AETHER_POOL_WRITE ? 7 : 0,
                                kind == AETHER_POOL_WRITE ? 512 : 0);
}
static void finish(struct aether_pool_token token,
                   enum aether_pool_io_kind kind)
{
    aether_pool_provider_done(&witness, token, &file, 0, 0);
    aether_pool_leaf_done(&witness, token, &leaf, kind,
                          kind == AETHER_POOL_WRITE ? 7 : 0, 0);
}
static void healthy(void)
{
    finish(begin(AETHER_POOL_WRITE), AETHER_POOL_WRITE);
    finish(begin(AETHER_POOL_FLUSH), AETHER_POOL_FLUSH);
}
static void *worker(void *argument)
{
    (void)argument;
    struct aether_pool_token first = begin(AETHER_POOL_WRITE);
    atomic_fetch_add(&ready, 1);
    while (!atomic_load(&go))
        sched_yield();
    finish(first, AETHER_POOL_WRITE);
    finish(begin(AETHER_POOL_FLUSH), AETHER_POOL_FLUSH);
    for (unsigned i = 1; i < 128; ++i) {
        /* Keep both operations open; complete in the other order. */
        struct aether_pool_token write = begin(AETHER_POOL_WRITE);
        struct aether_pool_token flush = begin(AETHER_POOL_FLUSH);
        finish(flush, AETHER_POOL_FLUSH);
        finish(write, AETHER_POOL_WRITE);
    }
    return NULL;
}
static void *duplicate_provider(void *argument)
{
    (void)argument;
    atomic_fetch_add(&ready, 1);
    while (!atomic_load(&go))
        sched_yield();
    aether_pool_provider_done(&witness, shared_token, &file, 0, 0);
    return NULL;
}

static void *contested_binding(void *argument)
{
    uint64_t target = *(uint64_t *)argument;
    atomic_fetch_add(&ready, 1);
    while (!atomic_load(&go))
        sched_yield();
    int result = aether_pool_witness_bind_txg(&witness, target);
    if (result == 0)
        atomic_fetch_add(&bind_winners, 1);
    else if (result == EALREADY)
        atomic_fetch_add(&bind_denials, 1);
    else
        abort();
    return NULL;
}

static int deferred_target(int mode)
{
    aether_pool_witness_init(&witness, &leaf, &file, mode == 25 ? 7 : 0);
    dmu_tx_t assigned = {.tx_txg = 7};
    uint64_t target = dmu_tx_get_txg(&assigned);
    REQUIRE(target == assigned.tx_txg);
    if (mode == 23) {
        pthread_t threads[32];
        for (unsigned i = 0; i < 32; ++i)
            REQUIRE(pthread_create(&threads[i], NULL, worker, NULL) == 0);
        while (atomic_load(&ready) != 32)
            sched_yield();
        /* All initial writes are open; binding may overlap their completion. */
        atomic_store(&go, 1);
        REQUIRE(aether_pool_witness_bind_txg(&witness, target) == 0);
        for (unsigned i = 0; i < 32; ++i)
            REQUIRE(pthread_join(threads[i], NULL) == 0);
        REQUIRE(atomic_load(&witness.writes) == 4096);
        REQUIRE(atomic_load(&witness.flushes) == 4096);
        REQUIRE(aether_pool_witness_check(&witness, target) == 0);
        return 0;
    }
    healthy();
    if (mode == 26 || mode == 27) {
        struct aether_pool_token tokens[AETHER_POOL_WITNESS_SLOTS];
        unsigned count = mode == 26 ? 1 : AETHER_POOL_WITNESS_SLOTS;
        for (unsigned i = 0; i < count; ++i) {
            tokens[i] = begin(AETHER_POOL_WRITE);
            REQUIRE(tokens[i].generation != 0);
        }
        if (mode == 27)
            REQUIRE(begin(AETHER_POOL_WRITE).generation == 0);
        REQUIRE(aether_pool_witness_bind_txg(&witness, target) == 0);
        unsigned expected = mode == 27 ? AETHER_POOL_CAPACITY : 0;
        REQUIRE(aether_pool_witness_check(&witness, target) ==
                (expected | AETHER_POOL_INCOMPLETE));
        for (unsigned i = 0; i < count; ++i)
            finish(tokens[i], AETHER_POOL_WRITE);
        REQUIRE(aether_pool_witness_check(&witness, target) == expected);
        return 0;
    }
    if (mode == 18) {
        REQUIRE(aether_pool_witness_check(&witness, UINT64_MAX) ==
                AETHER_POOL_TXG_PENDING);
        return 0;
    }
    if (mode == 24) {
        pthread_t threads[16];
        uint64_t targets[16];
        for (unsigned i = 0; i < 16; ++i) {
            targets[i] = 7 + i % 2;
            REQUIRE(pthread_create(&threads[i], NULL, contested_binding,
                                   &targets[i]) == 0);
        }
        while (atomic_load(&ready) != 16)
            sched_yield();
        atomic_store(&go, 1);
        for (unsigned i = 0; i < 16; ++i)
            REQUIRE(pthread_join(threads[i], NULL) == 0);
        REQUIRE(atomic_load(&bind_winners) == 1 &&
                atomic_load(&bind_denials) == 15);
        REQUIRE(atomic_load(&witness.target_txg) == 7 ||
                atomic_load(&witness.target_txg) == 8);
        REQUIRE(aether_pool_witness_check(&witness, UINT64_MAX) ==
                AETHER_POOL_BAD_EVENT);
        return 0;
    }
    unsigned expected = 0;
    if (mode == 19) {
        struct aether_pool_token token = begin(AETHER_POOL_WRITE);
        aether_pool_provider_done(&witness, token, &file, EIO, 0);
        aether_pool_leaf_done(&witness, token, &leaf, AETHER_POOL_WRITE, 7, 0);
        expected = AETHER_POOL_PROVIDER_ERROR;
    }
    uint64_t generation = atomic_load(&witness.operations[0].state);
    uint64_t writes = atomic_load(&witness.writes);
    uint64_t flushes = atomic_load(&witness.flushes);
    if (mode == 20) {
        REQUIRE(aether_pool_witness_bind_txg(&witness, 0) == EINVAL);
        REQUIRE(atomic_load(&witness.target_txg) == 0);
        expected = AETHER_POOL_BAD_EVENT;
    }
    if (mode == 25) {
        REQUIRE(aether_pool_witness_bind_txg(&witness, target) == EALREADY);
        expected = AETHER_POOL_BAD_EVENT;
    } else {
        REQUIRE(aether_pool_witness_bind_txg(&witness, target) == 0);
    }
    if (mode == 21 || mode == 22) {
        REQUIRE(aether_pool_witness_bind_txg(&witness, mode == 21 ? 7 : 8) ==
                EALREADY);
        expected = AETHER_POOL_BAD_EVENT;
    }
    REQUIRE(atomic_load(&witness.target_txg) == target);
    REQUIRE(atomic_load(&witness.operations[0].state) == generation);
    REQUIRE(atomic_load(&witness.writes) == writes &&
            atomic_load(&witness.flushes) == flushes);
    REQUIRE(witness.leaf == &leaf && witness.file == &file);
    REQUIRE(aether_pool_witness_check(&witness, target - 1) ==
            (expected | AETHER_POOL_TXG_PENDING));
    REQUIRE(aether_pool_witness_check(&witness, target) == expected);
    if (mode == 19)
        REQUIRE(atomic_load(&witness.provider_error) == EIO);
    healthy();
    REQUIRE(aether_pool_witness_check(&witness, target) == expected);
    return 0;
}

int main(int argc, char **argv)
{
    REQUIRE(argc == 2);
    int mode = atoi(argv[1]);
    REQUIRE(mode >= 0 && mode <= 27);
    if (mode >= 17)
        return deferred_target(mode);
    init();
    if (mode == 0) {
        healthy();
        REQUIRE(aether_pool_witness_check(&witness, 7) == 0);
        REQUIRE(sizeof(witness) <= 8192);
        return 0;
    }
    if (mode == 1) {
        pthread_t threads[32];
        for (unsigned i = 0; i < 32; ++i)
            REQUIRE(pthread_create(&threads[i], NULL, worker, NULL) == 0);
        while (atomic_load(&ready) != 32)
            sched_yield();
        REQUIRE(aether_pool_witness_check(&witness, 0) &
                AETHER_POOL_INCOMPLETE);
        atomic_store(&go, 1);
        for (unsigned i = 0; i < 32; ++i)
            REQUIRE(pthread_join(threads[i], NULL) == 0);
        REQUIRE(atomic_load(&witness.writes) == 4096);
        REQUIRE(atomic_load(&witness.flushes) == 4096);
        REQUIRE(aether_pool_witness_check(&witness, 7) == 0);
        return 0;
    }
    healthy();
    struct aether_pool_token token = begin(AETHER_POOL_WRITE);
    unsigned expected = 0;
    if (mode == 2) {
        aether_pool_provider_done(&witness, token, &file, 0, 0);
        aether_pool_provider_done(&witness, token, &file, 0, 0);
        aether_pool_leaf_done(&witness, token, &leaf, AETHER_POOL_WRITE, 7, 0);
        aether_pool_leaf_done(&witness, token, &leaf, AETHER_POOL_WRITE, 7, 0);
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode == 3) {
        finish(token, AETHER_POOL_WRITE);
        struct aether_pool_token next = begin(AETHER_POOL_WRITE);
        REQUIRE(token.slot == next.slot && token.generation != next.generation);
        aether_pool_provider_done(&witness, token, &file, 0, 0);
        aether_pool_leaf_done(&witness, token, &leaf, AETHER_POOL_WRITE, 7, 0);
        finish(next, AETHER_POOL_WRITE);
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode == 4) {
        aether_pool_provider_done(&witness, token, &foreign, 0, 0);
        aether_pool_leaf_done(&witness, token, &leaf, AETHER_POOL_WRITE, 7, 0);
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode == 5) {
        finish(token, AETHER_POOL_WRITE);
        for (unsigned i = 0; i < 3; ++i) {
            init();
            healthy();
            token = begin(AETHER_POOL_WRITE);
            aether_pool_provider_done(&witness, token, &file, 0, 0);
            aether_pool_leaf_done(&witness, token, i == 0 ? &foreign : &leaf,
                                  i == 1 ? AETHER_POOL_FLUSH
                                         : AETHER_POOL_WRITE,
                                  i == 2 ? 8 : 7, 0);
            REQUIRE(aether_pool_witness_check(&witness, 7) ==
                    AETHER_POOL_BAD_EVENT);
        }
        return 0;
    } else if (mode == 6) {
        aether_pool_provider_done(&witness, token, &file, 0, 256);
        aether_pool_leaf_done(&witness, token, &leaf, AETHER_POOL_WRITE, 7, 0);
        expected = AETHER_POOL_PARTIAL_WRITE;
    } else if (mode == 7) {
        finish(token, AETHER_POOL_WRITE);
        int errors[] = {ENOTSUP, EACCES, EBADF, EIO};
        for (unsigned i = 0; i < 4; ++i) {
            struct aether_pool_token flush = begin(AETHER_POOL_FLUSH);
            aether_pool_provider_done(&witness, flush, &file, errors[i], 0);
            /* A successful leaf/parent cannot erase the provider error. */
            aether_pool_leaf_done(&witness, flush, &leaf, AETHER_POOL_FLUSH, 0,
                                  0);
        }
        REQUIRE(atomic_load(&witness.provider_error) == ENOTSUP);
        REQUIRE(atomic_load(&witness.leaf_error) == 0);
        expected = AETHER_POOL_PROVIDER_ERROR;
    } else if (mode == 8) {
        aether_pool_leaf_done(&witness, token, &leaf, AETHER_POOL_WRITE, 7, 0);
        REQUIRE(aether_pool_witness_check(&witness, 7) ==
                (AETHER_POOL_BAD_EVENT | AETHER_POOL_INCOMPLETE));
        finish(token, AETHER_POOL_WRITE);
        expected = AETHER_POOL_BAD_EVENT;
    } else if (mode == 9) {
        aether_pool_provider_done(&witness, token, &file, 0, 0);
        REQUIRE(aether_pool_witness_check(&witness, 7) ==
                AETHER_POOL_INCOMPLETE);
        aether_pool_leaf_done(&witness, token, &leaf, AETHER_POOL_WRITE, 7,
                              EIO);
        REQUIRE(atomic_load(&witness.leaf_error) == EIO);
        expected = AETHER_POOL_LEAF_ERROR;
    } else if (mode == 10) {
        struct aether_pool_token tokens[AETHER_POOL_WITNESS_SLOTS];
        tokens[0] = token;
        for (unsigned i = 1; i < AETHER_POOL_WITNESS_SLOTS; ++i)
            tokens[i] = begin(AETHER_POOL_WRITE);
        REQUIRE(begin(AETHER_POOL_WRITE).generation == 0);
        for (unsigned i = 0; i < AETHER_POOL_WITNESS_SLOTS; ++i)
            finish(tokens[i], AETHER_POOL_WRITE);
        expected = AETHER_POOL_CAPACITY;
    } else if (mode == 11) {
        finish(token, AETHER_POOL_WRITE);
        atomic_store(&witness.operations[token.slot].state, UINT64_MAX & ~3ULL);
        finish(begin(AETHER_POOL_WRITE), AETHER_POOL_WRITE);
        expected = AETHER_POOL_OVERFLOW;
    } else if (mode == 12) {
        atomic_store(&witness.writes, UINT64_MAX);
        finish(token, AETHER_POOL_WRITE);
        expected = AETHER_POOL_OVERFLOW | AETHER_POOL_NO_WRITE;
    } else if (mode == 13) {
        finish(token, AETHER_POOL_WRITE);
        REQUIRE(aether_pool_witness_check(&witness, 6) ==
                AETHER_POOL_TXG_PENDING);
    } else if (mode == 14) {
        finish(token, AETHER_POOL_WRITE);
        /* Prior operations drained. Each init below is a fresh test lifetime.
         */
        init();
        finish(begin(AETHER_POOL_WRITE), AETHER_POOL_WRITE);
        REQUIRE(aether_pool_witness_check(&witness, 7) == AETHER_POOL_NO_FLUSH);
        init();
        finish(begin(AETHER_POOL_FLUSH), AETHER_POOL_FLUSH);
        REQUIRE(aether_pool_witness_check(&witness, 7) == AETHER_POOL_NO_WRITE);
        return 0;
    } else if (mode == 15) {
        finish(token, AETHER_POOL_WRITE);
        for (unsigned i = 0; i < 8; ++i) {
            init();
            healthy();
            if (i < 3) {
                enum aether_pool_io_kind kind = i == 0   ? 99
                                                : i == 1 ? AETHER_POOL_WRITE
                                                         : AETHER_POOL_FLUSH;
                REQUIRE(aether_pool_io_begin(&witness, kind, 7, i == 2 ? 1 : 0)
                            .generation == 0);
            } else {
                token = begin(AETHER_POOL_WRITE);
                if (i == 7) {
                    aether_pool_provider_done(&witness, token, &file, 0, 513);
                    aether_pool_leaf_done(&witness, token, &leaf,
                                          AETHER_POOL_WRITE, 7, 0);
                } else {
                    struct aether_pool_token bad = token;
                    if (i == 3)
                        bad.slot = AETHER_POOL_WITNESS_SLOTS;
                    else if (i == 4)
                        bad.generation = 0;
                    else if (i == 5)
                        bad.generation = UINT64_MAX;
                    else
                        ++bad.slot;
                    aether_pool_provider_done(&witness, bad, &file, 0, 0);
                    finish(token, AETHER_POOL_WRITE);
                }
            }
            REQUIRE(aether_pool_witness_check(&witness, 7) ==
                    (AETHER_POOL_BAD_EVENT |
                     (i == 7 ? AETHER_POOL_PARTIAL_WRITE : 0)));
        }
        return 0;
    } else if (mode == 16) {
        shared_token = token;
        pthread_t threads[2];
        for (unsigned i = 0; i < 2; ++i)
            REQUIRE(pthread_create(&threads[i], NULL, duplicate_provider,
                                   NULL) == 0);
        while (atomic_load(&ready) != 2)
            sched_yield();
        atomic_store(&go, 1);
        for (unsigned i = 0; i < 2; ++i)
            REQUIRE(pthread_join(threads[i], NULL) == 0);
        aether_pool_leaf_done(&witness, token, &leaf, AETHER_POOL_WRITE, 7, 0);
        expected = AETHER_POOL_BAD_EVENT;
    }
    /* Later healthy traffic cannot clear any recorded error. */
    if (mode != 12)
        healthy();
    REQUIRE(aether_pool_witness_check(&witness, 7) == expected);
    return 0;
}
