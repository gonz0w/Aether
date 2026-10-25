/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual entropy entry points share one authoritative kernel quota. No payload
 * is logged or assessed for statistical quality. Init/fini occur quiescently.
 */
unsigned long aether_bad_auxv(unsigned long key)
{
    unsigned long value = getauxval(key);
    return key == 0xa002 && value ? value + 256 : value;
}
static unsigned zfs_entropy_initialize(void)
{
    random_init();
    uint8_t data[515];
    memset(data, 0xa5, sizeof(data));
    CHECK(!random_get_bytes(NULL, 0) && !random_get_bytes(data + 1, 513) &&
              data[0] == 0xa5 && data[514] == 0xa5,
          394);
    return 0;
}
static unsigned zfs_entropy_worker(void)
{
    int saved_errno = errno;
    uint8_t data[18];
    memset(data, 0xa5, sizeof(data));
    CHECK(!random_get_bytes(data + 1, 8) &&
              !random_get_pseudo_bytes(data + 9, 8) && data[0] == 0xa5 &&
              data[17] == 0xa5 && errno == saved_errno,
          394);
    return 0;
}
static unsigned zfs_entropy_cleanup(void)
{
    unsigned long grant = getauxval(0xa002);
    uint8_t tail[4096], sentinel = 0xa5;
    /* Init consumes8 and513; each completed actual worker consumes16. */
    CHECK(limit == 2 || limit == 82, 395);
    size_t left = 4096 - 8 - 513 - limit * 16;
    CHECK(!random_get_bytes(tail, left) &&
              memtrap(0x2b000, grant, (uintptr_t)&sentinel, 1, 0) == -ENOSPC &&
              sentinel == 0xa5,
          395);
    random_fini();
    random_fini();
    CHECK(memtrap(0x2b000, grant, (uintptr_t)&sentinel, 1, 0) == -EBADF &&
              sentinel == 0xa5,
          396);
#ifdef ENTROPY_CLOSED
    random_get_bytes(&sentinel, 1);
    return 396;
#endif
    return 0;
}
