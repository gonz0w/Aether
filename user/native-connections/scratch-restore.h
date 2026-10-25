/* SPDX-License-Identifier: BSD-2-Clause */
/* Include after scratch-client.h. Fresh-image local publication only. */
static int scratch_restore_masked(const unsigned char table[64],
                                  const unsigned char descriptions[32])
{
    unsigned counts[5] = {0};
    unsigned generation = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    if (!startup_ready || poisoned || (scratch_root >> 24) != 0xfd ||
        !((scratch_root >> 16) & 255) || generation < 1 || generation > 255 ||
        ((scratch_root >> 8) & 255) != generation ||
        ((scratch_root & 255) != 1 && (scratch_root & 255) != 2))
        return 0;
    for (unsigned i = 0; i < 16; ++i) {
        struct startup_fd initial = startup_fds[i];
        if (initial.binding != (i < 3 ? i : 0) || initial.flags ||
            initial.present != (i < 3 ? 1 : 0))
            return 0;
        const unsigned char *record = table + i * 4;
        if (!record[2]) {
            if (get(record, 0))
                return 0;
            continue;
        }
        if (record[2] != 1 || record[0] >= 5 || record[3])
            return 0;
#ifndef SCRATCH_RESTORE_KEEP_CLOEXEC
        if (record[1])
            return 0;
#endif
        ++counts[record[0]];
    }
    for (unsigned j = 0; j < 5; ++j) {
        if (j < 3) {
            if (live[j] != 1 || startup_users[j] != 1 || !refs[j] ||
                fds[j] != j || rights[j] != (j ? 2u : 1u))
                return 0;
            continue;
        }
        if (live[j] || startup_users[j] || refs[j] || fds[j] || rights[j])
            return 0;
        const unsigned char *record = descriptions + (j - 3) * 16;
        if (!counts[j]) {
            if (get(record, 0) || get(record, 4) || get(record, 8) ||
                get(record, 12))
                return 0;
            continue;
        }
        unsigned reference = get(record, 0), mode = get(record, 4);
        unsigned sequence = (reference >> 4) & 7;
        unsigned expected = 0xfc000000u | (scratch_root & 0x00ffff00u) |
                            (((scratch_root & 255) - 1) << 3) |
                            (sequence << 4) | (j - 2);
#ifndef SCRATCH_RESTORE_STALE
        if (reference != expected)
            return 0;
#else
        (void)expected;
#endif
        if (sequence < 1 || sequence > 6 || (mode != 1 && mode != 14) ||
            get(record, 8) != counts[j] || get(record, 12))
            return 0;
    }
    for (unsigned i = 0; i < 16; ++i)
        startup_fds[i] = (struct startup_fd){table[i * 4], table[i * 4 + 1],
                                             table[i * 4 + 2]};
    for (unsigned j = 0; j < 5; ++j) {
        startup_users[j] = counts[j];
        live[j] = counts[j] != 0;
        if (!counts[j]) {
            refs[j] = fds[j] = rights[j] = 0;
        } else if (j >= 3) {
            const unsigned char *record = descriptions + (j - 3) * 16;
            refs[j] = get(record, 0);
            fds[j] = j;
            rights[j] = get(record, 4) == 1 ? 1 : 2;
        }
    }
    return 1;
}
static int scratch_restore(const unsigned char table[64],
                           const unsigned char descriptions[32])
{
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return 0;
    int saved = errno;
    int result = scratch_restore_masked(table, descriptions);
    if (!result)
        poisoned = 1;
    startup_mask_leave(previous);
    errno = saved;
    return result;
}
