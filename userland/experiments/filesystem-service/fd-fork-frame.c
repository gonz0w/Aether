/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-fork-frame.h"

static int64_t no_transport(void *context, uint64_t op, uint64_t a, uint64_t b,
                            uint64_t c, uint64_t d)
{
    (void)context;
    (void)op;
    (void)a;
    (void)b;
    (void)c;
    (void)d;
    return -5;
}
static int body(const unsigned char *raw, struct aefd_startup_auxv observed,
                long pid, long parent_pid,
                struct aether_fs_session_identity *identity)
{
    struct aefd_bindings map;
    if (!aether_fs_session_decode(raw + 16, 32, observed.memory, pid,
                                  parent_pid, identity) ||
        !observed.input || !observed.output ||
        observed.input == observed.output ||
        !aefd_bindings_decode(raw + 48, 128, aefd_word(raw + 48, 1), &map))
        return 0;
    struct aefd_native_source sources[7];
    for (unsigned i = 0; i < 7; ++i) {
        const unsigned char *s = raw + 176 + i * 16;
        sources[i] = (struct aefd_native_source){
            aether_fs_session_u32(s), aether_fs_session_u32(s + 4),
            aether_fs_session_u32(s + 8), aether_fs_session_u32(s + 12)};
    }
    unsigned history[2] = {aether_fs_session_u32(raw + 288),
                           aether_fs_session_u32(raw + 292)};
    /* Existing constructor validates only local metadata, with no I/O. This
     * temporary native value never borrows/transfers endpoints or enters a
     * guard. */
    struct aefd_native native = {0};
    if (!aefd_native_init(&native, no_transport, NULL, observed.input,
                          observed.output, sources, history,
                          UINT32_C(0x76050001)))
        return 0;
    unsigned seen = 0;
    for (unsigned i = 0; i < AEFD_BINDINGS_COUNT; ++i)
        if (map.slots[i].kind == AEFD_BIND_CONSOLE ||
            map.slots[i].kind == AEFD_BIND_PIPE)
            seen |= 1U << map.slots[i].selector;
    for (unsigned i = 0; i < 7; ++i)
        if (!!(seen & (1U << i)) != !!sources[i].reference)
            return 0;
    return 1;
}
int aefd_fork_header(const unsigned char *raw, size_t length)
{
    if ((!raw && length) || length > 16)
        return -1;
    if (length < 16)
        return 0;
    return !memcmp(raw, AEFD_FORK_MAGIC, 8) &&
                   aether_fs_session_u32(raw + 8) == 1 &&
                   aether_fs_session_u32(raw + 12) == AEFD_FORK_REQUEST_BYTES
               ? 1
               : -1;
}
int aefd_fork_decode(const unsigned char *raw, size_t length,
                     struct aefd_startup_auxv observed, long pid,
                     long parent_pid, struct aefd_fork_view *out)
{
    if (!raw || !out || length != AEFD_FORK_REQUEST_BYTES ||
        aefd_fork_header(raw, 16) != 1 || !aefd_word(raw + 296, 0))
        return 0;
    struct aether_fs_session_identity identity;
    if (!body(raw, observed, pid, parent_pid, &identity) || identity.slot != 1)
        return 0;
    *out = (struct aefd_fork_view){raw, identity, aefd_word(raw + 296, 0)};
    return 1;
}
int aefd_fork_encode(unsigned char *out, size_t size,
                     const unsigned char *snapshot, size_t length,
                     struct aefd_startup_auxv observed, long pid,
                     long parent_pid, uint64_t sequence)
{
    if (!out || size != AEFD_FORK_REQUEST_BYTES)
        return 0;
    if (!snapshot || length != AEFD_STARTUP_BYTES || !sequence ||
        memcmp(snapshot, AEFD_STARTUP_MAGIC, 8) ||
        aether_fs_session_u32(snapshot + 8) != 1 ||
        aether_fs_session_u32(snapshot + 12) != AEFD_STARTUP_BYTES ||
        aether_fs_session_u32(snapshot + 296) != UINT32_C(0x76050001) ||
        aether_fs_session_u32(snapshot + 300))
        goto invalid;
    struct aether_fs_session_identity identity;
    if (!body(snapshot, observed, pid, parent_pid, &identity) ||
        identity.slot != 1)
        goto invalid;
    memmove(out, snapshot, AEFD_FORK_REQUEST_BYTES);
    memcpy(out, AEFD_FORK_MAGIC, 8);
    aefd_put(out + 296, 0, sequence);
    return 1;
invalid:
    memset(out, 0, AEFD_FORK_REQUEST_BYTES);
    return 0;
}
int aefd_fork_child_match(const unsigned char *request, size_t request_length,
                          struct aefd_startup_auxv parent, long parent_pid,
                          const unsigned char *startup, size_t startup_length,
                          struct aefd_startup_auxv child, long child_pid,
                          struct aether_fs_session_identity *out)
{
    struct aefd_fork_view fork;
    struct aether_fs_session_identity identity;
    if (!startup || !out || startup_length != AEFD_STARTUP_BYTES ||
        !aefd_fork_decode(request, request_length, parent, parent_pid, 7,
                          &fork) ||
        memcmp(startup, AEFD_STARTUP_MAGIC, 8) ||
        aether_fs_session_u32(startup + 8) != 1 ||
        aether_fs_session_u32(startup + 12) != AEFD_STARTUP_BYTES ||
        aefd_word(startup + 296, 0) ||
        !body(startup, child, child_pid, parent_pid, &identity) ||
        identity.slot == 1 ||
        identity.shell_generation != fork.parent.shell_generation ||
        child.memory == parent.memory || child.input == parent.input ||
        child.input == parent.output || child.output == parent.input ||
        child.output == parent.output ||
        aefd_word(startup + 48, 1) == aefd_word(request + 48, 1) ||
        memcmp(startup + 112, request + 112, 64) ||
        memcmp(startup + 176, request + 176, 120))
        return 0;
    *out = identity;
    return 1;
}
int aefd_fork_next(uint64_t *counter, uint64_t *out)
{
    if (!counter || !out || counter == out || *counter == UINT64_MAX)
        return 0;
    *out = ++*counter;
    return 1;
}
int aefd_fork_parent_reply(const unsigned char *raw, size_t length,
                           uint64_t sequence, int64_t native_result,
                           int64_t *out)
{
    if (!raw || !out || length != AEFD_FORK_RECEIPT_BYTES || !sequence ||
        memcmp(raw, "AEFKR001", 8) || aefd_word(raw, 1) != sequence ||
        aefd_word(raw, 3))
        return 0;
    uint64_t bits = aefd_word(raw, 2);
    int64_t result =
        bits <= INT64_MAX ? (int64_t)bits : -1 - (int64_t)(UINT64_MAX - bits);
    if (result > 0) {
        if (result > 110 || !aether_fs_session_child_pid((long)result) ||
            result != native_result)
            return 0;
    } else if (result < -4095 || result == 0 || native_result != -11) {
        return 0;
    }
    *out = result;
    return 1;
}
int aefd_fork_ready_encode(unsigned char *out, size_t size, uint64_t sequence,
                           long child_pid)
{
    if (!out || size != AEFD_FORK_RECEIPT_BYTES)
        return 0;
    memset(out, 0, AEFD_FORK_RECEIPT_BYTES);
    if (!sequence || !aether_fs_session_child_pid(child_pid))
        return 0;
    memcpy(out, "AEFKC001", 8);
    aefd_put(out, 1, sequence);
    aefd_put(out, 2, (uint64_t)child_pid);
    return 1;
}
int aefd_fork_ready_decode(const unsigned char *raw, size_t length,
                           uint64_t sequence, long child_pid)
{
    return raw && length == AEFD_FORK_RECEIPT_BYTES && sequence &&
           aether_fs_session_child_pid(child_pid) &&
           !memcmp(raw, "AEFKC001", 8) && aefd_word(raw, 1) == sequence &&
           aefd_word(raw, 2) == (uint64_t)child_pid && !aefd_word(raw, 3);
}
