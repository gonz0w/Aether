/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual ARC adapter/stat types, gated peers; no ARC engine has started. */
#include <sys/zfs_context.h>
#include <sys/arc_impl.h>
#include <sys/mman.h>

arc_stats_t arc_stats;

#define CHECK(c, n)                                                            \
    do {                                                                       \
        if (!(c))                                                              \
            return (n);                                                        \
    } while (0)

unsigned aether_arc_probe(void)
{
    uint64_t total = aether_zfs_granted_pages();
    physmem = total;
    uint64_t bytes = total * 4096;
    arc_sys_free = (total / 10) * 4096;
#ifdef ARC_BAD_HEADROOM
    arc_sys_free = bytes + 4096;
    arc_available_memory();
    return 415;
#endif
    CHECK(arc_all_memory() == bytes, 415);
    long before = aether_zfs_free_pages();
    CHECK(arc_free_memory() == (uint64_t)before * 4096 &&
              arc_available_memory() == before * 4096 - (int64_t)arc_sys_free,
          415);
    CHECK(before > (long)(total / 10), 416);
    void *mappings[128];
    size_t lengths[128];
    unsigned used = 0;
    uint64_t target = total / 10;
    while (aether_zfs_free_pages() > target) {
        CHECK(used < 128, 416);
        uint64_t pages = aether_zfs_free_pages() - target;
        if (pages > 64)
            pages = 64;
        size_t len = pages * 4096;
        void *p = mmap(NULL, len, PROT_READ | PROT_WRITE,
                       MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (p == MAP_FAILED) {
            len = 4096;
            p = mmap(NULL, len, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        }
        CHECK(p != MAP_FAILED, 416);
        mappings[used] = p;
        lengths[used++] = len;
    }
    CHECK(arc_available_memory() == 0 && arc_all_memory() == bytes, 415);
    void *last = mmap(NULL, 4096, PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    CHECK(last != MAP_FAILED && arc_available_memory() == -4096, 415);
    CHECK(!munmap(last, 4096) && arc_available_memory() == 0, 415);
    while (used) {
        --used;
        CHECK(!munmap(mappings[used], lengths[used]), 416);
    }
    CHECK(aether_zfs_free_pages() == (uint64_t)before &&
              arc_free_memory() == (uint64_t)before * 4096 &&
              arc_available_memory() > 0,
          415);
    return 0;
}
