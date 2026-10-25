/* SPDX-License-Identifier: BSD-2-Clause */
/* Include after scratch-client.h; callers hold the existing fork mask guard. */
static int scratch_fork_valid(unsigned generation, const unsigned counts[5])
{
    if (!startup_ready || poisoned || generation < 1 || generation > 255 ||
        (scratch_root >> 24) != 0xfd || !((scratch_root >> 16) & 255) ||
        ((scratch_root >> 8) & 255) != generation || (scratch_root & 255) != 1)
        return 0;
    unsigned total = 0;
    for (unsigned j = 0; j < 5; ++j) {
        if (counts[j] > 16)
            return 0;
        total += counts[j];
    }
    if (total > 16)
        return 0;
    for (unsigned j = 3; j < 5; ++j) {
#ifndef SCRATCH_FORK_SKIP_COUNTS
        if (counts[j] != startup_users[j])
            return 0;
#endif
        if (!live[j]) {
            if (counts[j] || startup_users[j])
                return 0;
            continue;
        }
        unsigned sequence = (refs[j] >> 4) & 7;
        unsigned expected = 0xfc000000u | (scratch_root & 0x00ffff00u) |
                            (sequence << 4) | (j - 2);
        if (live[j] != 1 || !counts[j] || sequence < 1 || sequence > 6 ||
            refs[j] != expected || fds[j] != j ||
            (rights[j] != 1 && rights[j] != 2))
            return 0;
    }
    return 1;
}
static int scratch_fork_rebind(void)
{
    unsigned char frame[32] = {0};
    unsigned generation = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    if (!scratch_fork_valid((scratch_root >> 8) & 255, startup_users) ||
        generation < 1 || generation > 255 || !move(frame, 32, 0))
        return 0;
    unsigned root = get(frame, 8);
    unsigned expected_root =
        (scratch_root & 0xffff0000u) | (generation << 8) | 2;
    if (memcmp(frame, "AESFC001", 8) || root != expected_root ||
        get(frame, 12) != generation || get(frame, 24) || get(frame, 28))
        return 0;
    for (unsigned j = 3; j < 5; ++j) {
        unsigned expected =
            live[j] ? (refs[j] & 0xffff00ffu) | (generation << 8) | 8 : 0;
        if (get(frame, 16 + (j - 3) * 4) != expected)
            return 0;
    }
    /* No mutation until the entire grant has passed validation. */
    scratch_root = root;
    for (unsigned j = 3; j < 5; ++j) {
#ifndef SCRATCH_FORK_KEEP_PARENT
        refs[j] = get(frame, 16 + (j - 3) * 4);
#endif
        if (!live[j])
            fds[j] = rights[j] = 0;
    }
    return 1;
}
