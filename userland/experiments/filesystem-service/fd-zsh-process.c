/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-zsh-process.h"
static int64_t no_transport(void *owner, uint64_t op, uint64_t a, uint64_t b,
                            uint64_t c, uint64_t d)
{
    (void)owner;
    (void)op;
    (void)a;
    (void)b;
    (void)c;
    (void)d;
    return -5;
}
static int sequence_ok(uint64_t sequence)
{
    return sequence && sequence != UINT64_MAX;
}
int aefd_zsh_snapshot_decode(const unsigned char *raw, size_t size,
                             struct aefd_startup_auxv observed, long pid,
                             long parent, struct aefd_zsh_snapshot *out)
{
    struct aether_fs_session_identity identity;
    struct aefd_bindings map;
    if (!raw || !out || size != 336 || memcmp(raw, "AEFDB009", 8) ||
        aether_fs_session_u32(raw + 8) != 1 ||
        aether_fs_session_u32(raw + 12) != 336 || !observed.input ||
        !observed.output || observed.input == observed.output ||
        !aether_fs_session_decode(raw + 16, 32, observed.memory, pid, parent,
                                  &identity) ||
        (identity.slot != 1 && identity.slot != 2) ||
        !aefd_bindings_decode(raw + 48, 128, aefd_word(raw + 48, 1), &map) ||
        aether_fs_session_u32(raw + 296) !=
            (identity.slot == 1 ? UINT32_C(0x76050001) : 0) ||
        aether_fs_session_u32(raw + 300) !=
            (identity.slot == 1 ? AEFD_MODE_CONTROL : 0) ||
        aether_fs_session_u32(raw + 320) != 1 ||
        aether_fs_session_u32(raw + 324) || aefd_word(raw + 328, 0))
        return 0;
    for (unsigned i = 0; i < 4; ++i)
        if (aether_fs_session_u32(raw + 304 + i * 4) != 1000)
            return 0;
    unsigned seen = 0;
    for (unsigned fd = 0; fd < 16; ++fd) {
        struct aefd_binding slot = map.slots[fd];
        if (slot.kind == AEFD_BIND_CONSOLE)
            return 0;
        if (slot.kind == AEFD_BIND_DUPLEX_TERMINAL)
            seen |= 3U;
        else if (slot.kind == AEFD_BIND_TERMINAL || slot.kind == AEFD_BIND_PIPE)
            seen |= 1U << slot.selector;
    }
    struct aefd_native_source sources[7];
    for (unsigned i = 0; i < 7; ++i) {
        const unsigned char *s = raw + 176 + i * 16;
        sources[i] = (struct aefd_native_source){
            aether_fs_session_u32(s), aether_fs_session_u32(s + 4),
            aether_fs_session_u32(s + 8), aether_fs_session_u32(s + 12)};
        if (!!sources[i].reference != !!(seen & (1U << i)) ||
            (i < 3 && sources[i].reference &&
             sources[i].reference != (UINT32_C(0x7a000001) | i << 16)))
            return 0;
    }
    unsigned history[2] = {aether_fs_session_u32(raw + 288),
                           aether_fs_session_u32(raw + 292)};
    struct aefd_native native = {0};
    if (!aefd_native_init(&native, no_transport, NULL, observed.input,
                          observed.output, sources, history,
                          aether_fs_session_u32(raw + 296)))
        return 0;
    *out = (struct aefd_zsh_snapshot){raw, identity, map.generation};
    return 1;
}
static int header(const unsigned char *raw, size_t size, const char magic[8],
                  size_t expected, uint64_t *sequence)
{
    if (!raw || size != expected || memcmp(raw, magic, 8) ||
        aether_fs_session_u32(raw + 8) != 1 ||
        aether_fs_session_u32(raw + 12) != expected ||
        !sequence_ok(aefd_word(raw, 2)) || aefd_word(raw, 3))
        return 0;
    *sequence = aefd_word(raw, 2);
    return 1;
}
static void prefix(unsigned char *out, const char magic[8], size_t size,
                   uint64_t sequence)
{
    memset(out, 0, 32);
    memcpy(out, magic, 8);
    aefd_put(out, 1, 1 | (uint64_t)size << 32);
    aefd_put(out, 2, sequence);
}
int aefd_zsh_fork_encode(unsigned char *out, size_t size,
                         const unsigned char snapshot[336],
                         struct aefd_startup_auxv observed, long pid,
                         long parent, uint64_t sequence)
{
    struct aefd_zsh_snapshot view;
    if (!out || size != 368 || !sequence_ok(sequence) ||
        !aefd_zsh_snapshot_decode(snapshot, 336, observed, pid, parent,
                                  &view) ||
        view.identity.slot != 1)
        return 0;
    memmove(out + 32, snapshot, 336);
    prefix(out, "AEZFK001", size, sequence);
    return 1;
}
int aefd_zsh_fork_decode(const unsigned char *raw, size_t size,
                         struct aefd_startup_auxv observed, long pid,
                         long parent, uint64_t generation,
                         struct aefd_zsh_snapshot *out, uint64_t *sequence)
{
    struct aefd_zsh_snapshot view;
    uint64_t value;
    if (!out || !sequence || !header(raw, size, "AEZFK001", 368, &value) ||
        !aefd_zsh_snapshot_decode(raw + 32, 336, observed, pid, parent,
                                  &view) ||
        view.identity.slot != 1 || view.generation != generation)
        return 0;
    *out = view;
    *sequence = value;
    return 1;
}
int aefd_zsh_child_match(const unsigned char *request, size_t size,
                         struct aefd_startup_auxv parent, long parent_pid,
                         const unsigned char startup[336],
                         struct aefd_startup_auxv child, long child_pid,
                         struct aefd_zsh_snapshot *out)
{
    struct aefd_zsh_snapshot before, after;
    uint64_t sequence;
    if (!out || !request || size != 368 ||
        !aefd_zsh_fork_decode(request, size, parent, parent_pid, 7,
                              aefd_word(request + 80, 1), &before, &sequence) ||
        !aefd_zsh_snapshot_decode(startup, 336, child, child_pid, parent_pid,
                                  &after) ||
        after.identity.slot != 2 || before.generation == after.generation ||
        parent.memory == child.memory || child.input == parent.input ||
        child.input == parent.output || child.output == parent.input ||
        child.output == parent.output ||
        memcmp(before.raw + 112, startup + 112, 184) ||
        memcmp(before.raw + 304, startup + 304, 32))
        return 0;
    *out = after;
    return 1;
}
static int arguments_ok(const unsigned char raw[272])
{
    if (!raw || aefd_word(raw, 0) < 1 || aefd_word(raw, 0) > 4 ||
        aefd_word(raw, 1) > 4)
        return 0;
    for (unsigned i = 0; i < 8; ++i) {
        const unsigned char *s = raw + 16 + i * 32;
        unsigned count = (unsigned)aefd_word(raw, i < 4 ? 0 : 1);
        int used = (i % 4) < count;
        size_t end = 0;
        while (end < 32 && used && s[end])
            ++end;
        if (end == 32)
            return 0;
        for (size_t j = end; j < 32; ++j)
            if (s[j])
                return 0;
    }
    return 1;
}
int aefd_zsh_exec_encode(unsigned char *out, size_t size,
                         const unsigned char snapshot[336],
                         struct aefd_startup_auxv observed, long pid,
                         long parent, uint64_t sequence, const char *path,
                         const unsigned char arguments[272])
{
    struct aefd_zsh_snapshot view;
    if (!out || size != 672 || !path || !sequence_ok(sequence) ||
        !arguments_ok(arguments) ||
        !aefd_zsh_snapshot_decode(snapshot, 336, observed, pid, parent,
                                  &view) ||
        view.identity.slot != 2)
        return 0;
    size_t length = 0;
    while (length < 32 && path[length])
        ++length;
    if (!length || length == 32)
        return 0;
    memmove(out + 32, snapshot, 336);
    prefix(out, "AEZEX001", size, sequence);
    memset(out + 368, 0, 32);
    memcpy(out + 368, path, length);
    memmove(out + 400, arguments, 272);
    return 1;
}
int aefd_zsh_exec_decode(const unsigned char *raw, size_t size,
                         struct aefd_startup_auxv observed, long pid,
                         long parent, uint64_t generation,
                         struct aefd_zsh_snapshot *out, uint64_t *sequence)
{
    struct aefd_zsh_snapshot view;
    uint64_t value;
    if (!out || !sequence || !header(raw, size, "AEZEX001", 672, &value) ||
        !aefd_zsh_snapshot_decode(raw + 32, 336, observed, pid, parent,
                                  &view) ||
        view.identity.slot != 2 || view.generation != generation ||
        !arguments_ok(raw + 400))
        return 0;
    size_t end = 0;
    while (end < 32 && raw[368 + end])
        ++end;
    if (!end || end == 32)
        return 0;
    for (size_t j = end; j < 32; ++j)
        if (raw[368 + j])
            return 0;
    *out = view;
    *sequence = value;
    return 1;
}
static int receipt_kind(const char magic[8])
{
    return magic &&
           (!memcmp(magic, "AEZFR001", 8) || !memcmp(magic, "AEZFC001", 8) ||
            !memcmp(magic, "AEZER001", 8));
}
static int receipt_result(const char magic[8], int64_t result)
{
    int child_pid = result >= 10 && result <= 108 && (result - 3) % 7 == 0;
    int error = result >= -4095 && result <= -1;
    return !memcmp(magic, "AEZFR001", 8)   ? child_pid || error
           : !memcmp(magic, "AEZFC001", 8) ? child_pid
                                           : error;
}
int aefd_zsh_receipt_encode(unsigned char out[32], const char magic[8],
                            uint64_t sequence, int64_t result)
{
    if (!out || !receipt_kind(magic) || !sequence_ok(sequence) ||
        !receipt_result(magic, result))
        return 0;
    memset(out, 0, 32);
    memcpy(out, magic, 8);
    aefd_put(out, 1, sequence);
    aefd_put(out, 2, (uint64_t)result);
    return 1;
}
int aefd_zsh_receipt_decode(const unsigned char raw[32], const char magic[8],
                            uint64_t sequence, int64_t *out)
{
    if (!raw || !out || !receipt_kind(magic) || !sequence_ok(sequence) ||
        memcmp(raw, magic, 8) || aefd_word(raw, 1) != sequence ||
        aefd_word(raw, 3))
        return 0;
    uint64_t result = aefd_word(raw, 2);
    int64_t value = result <= INT64_MAX ? (int64_t)result
                                        : -1 - (int64_t)(UINT64_MAX - result);
    if (!receipt_result(magic, value))
        return 0;
    *out = value;
    return 1;
}
