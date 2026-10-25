/* SPDX-License-Identifier: BSD-2-Clause */
/* Private measurement of the unchanged pinned CDDL libspl malloc fallback.
 * The primary calls this while allocator peers are gated; callbacks borrow
 * live blocks. All owned pointers die at free or confirmed domain reclaim.
 */
#include <errno.h>
#include <stdint.h>
#include <sys/mman.h>
#include <umem.h>

static void *held;
static size_t held_size;
static unsigned constructors, destructors, callback_error;
static unsigned callback_cookie;
#ifdef ALLOC_PORT
static long (*failure_query)(void);
static long failure_peak;
static unsigned failed_constructors;
static int fail_construct(void *block, void *private, int flags)
{
    if (!block || private != &callback_cookie || flags != UMEM_DEFAULT)
        callback_error = 1;
    /* The callback retains no external resource and owns its failure cleanup.
     * Its raw block is subsequently freed by the allocation wrapper. */
    failure_peak = failure_query();
    ++failed_constructors;
    return ENOMEM;
}
#endif

static int construct(void *block, void *private, int flags)
{
    if (private != &callback_cookie || flags != UMEM_DEFAULT)
        callback_error = 1;
    memset(block, 0xc7, 512);
    ++constructors;
    return 0;
}

static void destruct(void *block, void *private)
{
    if (private != &callback_cookie)
        callback_error = 1;
    for (size_t i = 0; i < 512; ++i)
        if (((unsigned char *)block)[i] != 0xc7)
            callback_error = 1;
    ++destructors;
}

#define CHECK(c, n)                                                            \
    do {                                                                       \
        if (!(c))                                                              \
            return (n);                                                        \
    } while (0)

/* Free-page observations are not physical memory, allocator statistics or a
 * reservation. No other allocator caller runs between these snapshots.
 */
unsigned aether_umem_begin(unsigned workers, long (*available)(void),
                           unsigned long observations[3])
{
    CHECK(!held && (workers == 82 || workers == 2), 397);
    long before = available();
    CHECK(before > 0 && before < 8192, 397);
    held_size = workers == 82 ? 4 * 1024 * 1024 : 16 * 1024;
    held = umem_zalloc(held_size, UMEM_DEFAULT);
    CHECK(held, 397);
    for (size_t i = 0; i < held_size; ++i)
        CHECK(((unsigned char *)held)[i] == 0, 397);
    memset(held, 0x5a, held_size);
    long holding = available();
    CHECK(holding >= 0 && before - holding >= (long)(held_size / 4096) &&
              before - holding <= (long)(held_size / 4096) + 16,
          397);

    /* DEFAULT must fail without changing live contents or granted backing. */
    errno = 0;
    /* Volatile result publication keeps optimized Clang from deleting a
     * malloc used solely in a failure assertion. Inspect the native object.
     */
    void *volatile denied = umem_alloc(64 * 1024 * 1024, UMEM_DEFAULT);
    CHECK(!denied && errno == ENOMEM && available() == holding, 398);
    errno = 0;
    denied = umem_zalloc(64 * 1024 * 1024, UMEM_DEFAULT);
    CHECK(!denied && errno == ENOMEM && available() == holding, 398);
    denied = umem_alloc_aligned(64 * 1024 * 1024, 4096, UMEM_DEFAULT);
    CHECK(!denied && available() == holding, 398);
    for (size_t i = 0; i < held_size; ++i)
        CHECK(((unsigned char *)held)[i] == 0x5a, 398);

    void *aligned = umem_alloc_aligned(4096, 4096, UMEM_DEFAULT);
    CHECK(aligned && !((uintptr_t)aligned % 4096), 397);
    memset(aligned, 0x3c, 4096);
    umem_cache_t *cache =
        umem_cache_create("native-measurement", 512, 64, construct, destruct,
                          NULL, &callback_cookie, NULL, UMC_NODEBUG);
    CHECK(cache, 397);
    void *blocks[8];
    for (unsigned i = 0; i < 8; ++i) {
        blocks[i] = umem_cache_alloc(cache, UMEM_DEFAULT);
        CHECK(blocks[i] && !((uintptr_t)blocks[i] % 64), 397);
    }
    CHECK(constructors == 8 && !destructors && !callback_error, 397);
    long peak = available();
    CHECK(peak >= 0 && peak <= holding, 397);
    for (unsigned i = 0; i < 8; ++i)
        umem_cache_free(cache, blocks[i]);
    CHECK(destructors == 8 && !callback_error, 397);
    umem_cache_destroy(cache);
    for (size_t i = 0; i < 4096; ++i)
        CHECK(((unsigned char *)aligned)[i] == 0x3c, 397);
    umem_free_aligned(aligned, 4096);
    long remaining = available();
    CHECK(remaining >= peak && remaining <= before &&
              before - remaining <= (long)(held_size / 4096) + 16,
          397);
#ifdef ALLOC_PORT
    failure_query = available;
    void *plain = umem_alloc(512, UMEM_NOFAIL);
    void *zero = umem_zalloc(512, UMEM_NOFAIL);
    void *aligned_success = umem_alloc_aligned(512, 64, UMEM_NOFAIL);
    CHECK(plain && zero && aligned_success &&
              !((uintptr_t)aligned_success % 64),
          410);
    for (unsigned i = 0; i < 512; ++i)
        CHECK(((unsigned char *)zero)[i] == 0, 410);
    umem_free(plain, 512);
    umem_free(zero, 512);
    umem_free_aligned(aligned_success, 512);
    long before_invalid = available();
    errno = 0;
    void *volatile invalid = umem_alloc_aligned(512, 3, UMEM_DEFAULT);
    CHECK(!invalid && errno == EINVAL && available() == before_invalid, 410);
    for (unsigned pass = 0; pass < 2; ++pass) {
        size_t bytes = workers == 82 ? 2 * 1024 * 1024 : 4096;
        umem_cache_t *bad = umem_cache_create(
            "native-error", bytes, pass ? 4096 : 0, fail_construct, destruct,
            NULL, &callback_cookie, NULL, UMC_NODEBUG);
        long before_reject = available();
        for (unsigned i = 0; i < 8; ++i) {
            errno = 0;
            void *volatile rejected = umem_cache_alloc(bad, UMEM_DEFAULT);
            CHECK(!rejected && errno == ENOMEM && !callback_error &&
                      destructors == 8 && failure_peak <= before_reject &&
                      (workers == 2 || failure_peak < before_reject),
                  410);
            if (failure_peak < peak)
                peak = failure_peak;
            CHECK(available() >= before_reject - 2, 411);
        }
#if ALLOC_FAILURE == 4
        if (pass)
            umem_cache_alloc(bad, UMEM_NOFAIL);
#endif
        umem_cache_destroy(bad);
    }
    CHECK(failed_constructors == 16, 410);
    remaining = available();
#if ALLOC_FAILURE == 1
    invalid = umem_alloc(64 * 1024 * 1024, UMEM_NOFAIL);
#elif ALLOC_FAILURE == 2
    invalid = umem_zalloc(64 * 1024 * 1024, UMEM_NOFAIL);
#elif ALLOC_FAILURE == 3
    invalid = umem_alloc_aligned(64 * 1024 * 1024, 4096, UMEM_NOFAIL);
#elif ALLOC_FAILURE == 5
    /* Free backing is not a contiguous virtual reservation. Fill large
     * available spans first, then isolated holes; at most8192 maps. */
    for (unsigned i = 0; available() > 0; ++i) {
        CHECK(i < 8192, 412);
        size_t pages = available() < 64 ? (size_t)available() : 64;
        void *mapped =
            mmap(NULL, pages * 4096, 3, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (mapped == MAP_FAILED)
            mapped = mmap(NULL, 4096, 3, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        CHECK(mapped != MAP_FAILED, 412);
    }
    /* Drain already-cached descriptor slots too. Creation must terminate at
     * the first real backing denial, not return an invalid cache. */
    for (unsigned i = 0; i < 4096; ++i) {
        umem_cache_t *volatile exhausted = umem_cache_create(
            "native-exhaustion", 512, 0, NULL, NULL, NULL, NULL, NULL, 0);
        CHECK(exhausted, 412);
    }
#elif ALLOC_FAILURE == 6
    invalid = umem_alloc_aligned(512, 3, UMEM_NOFAIL);
#endif
#if ALLOC_FAILURE > 0
    return 413; /* Reaching this is a semantic failure, never a valid fatal. */
#endif
#endif
    observations[0] = (unsigned long)before;
    observations[1] = (unsigned long)peak;
    observations[2] = (unsigned long)remaining;
    errno = 71;
    return 0;
}

unsigned aether_umem_end(long (*available)(void))
{
    CHECK(held, 399);
    for (size_t i = 0; i < held_size; ++i)
        CHECK(((unsigned char *)held)[i] == 0x5a, 399);
    long before = available();
#ifndef HEAP_LEAK
    umem_free(held, held_size);
    held = NULL;
#endif
    long after = available();
    CHECK(after >= before, 399);
    /* Large mallocng mappings must return independently of thread retirement.
     * Small frees may stay cached; the original overall16-page limit remains.
     */
    CHECK(held_size < 1024 * 1024 || after - before >= (long)(held_size / 4096),
          399);
    errno = 71;
    return 0;
}
