/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_SESSION_FS_IDENTITY_H
#define AETHER_SESSION_FS_IDENTITY_H

#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* Proposed AEFSH001 client greeting for AENFS003/ABI29 only. These labels
 * validate an already authenticated channel; they never grant authority. */
struct aether_fs_session_identity {
    unsigned slot;
    unsigned epoch;
    unsigned shell_generation;
};

static inline uint32_t aether_fs_session_u32(const unsigned char *bytes)
{
    return (uint32_t)bytes[0] | (uint32_t)bytes[1] << 8 |
           (uint32_t)bytes[2] << 16 | (uint32_t)bytes[3] << 24;
}

static inline int aether_fs_session_child_pid(long pid)
{
    if (pid <= 0 || pid > 110)
        return 0;
    unsigned value = (unsigned)pid - 1;
    unsigned slot = value % 7, epoch = value / 7;
    return slot >= 2 && slot <= 4 && epoch >= 1 && epoch <= 15;
}

/* Borrowed frame; copy output only after every native observation agrees.
 * Parent greeting carries boot owner6's generation0 PID7. Shell generations
 * do not advance that boot owner. Restarted owners require a separate contract.
 * Children carry their copied shell's PID. No identity is rewritten on failure.
 */
static inline int
aether_fs_session_decode(const unsigned char *frame, size_t length,
                         uint64_t memory, long pid, long parent_pid,
                         struct aether_fs_session_identity *identity)
{
    if (!frame || !identity || length != 32 || memcmp(frame, "AEFSH001", 8) ||
        aether_fs_session_u32(frame + 8) != 29 ||
        aether_fs_session_u32(frame + 12) != 7)
        return 0;
    unsigned slot = aether_fs_session_u32(frame + 16);
    unsigned epoch = aether_fs_session_u32(frame + 20);
    unsigned parent = aether_fs_session_u32(frame + 24);
    unsigned shell = aether_fs_session_u32(frame + 28);
    if (slot < 1 || slot > 4 || epoch < 1 || epoch > 15 || shell < 1 ||
        shell > 3 ||
        memory != (UINT64_C(0x40000000) | (uint64_t)epoch << 8 | (slot + 1U)) ||
        pid != (long)(epoch * 7 + slot + 1) || parent_pid != (long)parent)
        return 0;
    if (slot == 1) {
        if (epoch != shell || parent != 7)
            return 0;
    } else if (parent != shell * 7 + 2) {
        return 0;
    }
    *identity = (struct aether_fs_session_identity){slot, epoch, shell};
    return 1;
}

#endif
