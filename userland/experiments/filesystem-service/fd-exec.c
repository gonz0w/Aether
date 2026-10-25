/* SPDX-License-Identifier: BSD-2-Clause */
#define _POSIX_C_SOURCE 200809L
#include "fd-exec.h"
static void put32(unsigned char *raw, unsigned at, uint32_t value)
{
    for (unsigned i = 0; i < 4; ++i)
        raw[at + i] = (unsigned char)(value >> (i * 8));
}
static int move(struct aefd_io io, unsigned char *raw, size_t length,
                int writing, unsigned *budget)
{
    size_t at = 0;
    while (at < length && *budget) {
        --*budget;
        size_t n = length - at;
        if (n > 16)
            n = 16;
        int64_t result = writing ? io.write(io.context, raw + at, n)
                                 : io.read(io.context, raw + at, n);
        if (result > 0 && (uint64_t)result <= n)
            at += (size_t)result;
        else if (result != -11 || io.wait(io.context, writing))
            return 0;
    }
    return at == length;
}
static int64_t failed(struct aefd_fork *f)
{
    f->phase = AEFD_FORK_FAILED;
    aefd_client_abort(&f->boot.context.client);
    aefd_native_leave(&f->boot.context.native);
    return -5;
}
static int arguments(unsigned char raw[272], char *const argv[],
                     char *const envp[])
{
    if (!argv || !envp)
        return 0;
    for (unsigned which = 0; which < 2; ++which) {
        char *const *values = which ? envp : argv;
        unsigned n = 0;
        while (n < 4 && values[n]) {
            size_t len = strnlen(values[n], 32);
            if (len == 32)
                return 0;
            memcpy(raw + 16 + (which * 4 + n) * 32, values[n], len);
            ++n;
        }
        if (values[n] || (!which && !n))
            return 0;
        aefd_put(raw, which, n);
    }
    return 1;
}
int64_t aefd_startup_ready(struct aefd_startup *b)
{
    if (!b || b->phase != 2 || b->context.state != 1 ||
        !b->context.client.live || b->context.native.active ||
        b->context.native.busy)
        return -22;
    int64_t result = aefd_native_enter(&b->context.native);
    if (result)
        return result;
    result =
        b->context.native.call(b->context.native.context, 0x20004, 0, 0, 0, 0);
    if (result)
        aefd_client_abort(&b->context.client);
    aefd_native_leave(&b->context.native);
    return result;
}
int64_t aefd_exec(struct aefd_fork *f, struct aefd_startup_auxv observed,
                  const char *path, char *const argv[], char *const envp[])
{
    if (!f || !path)
        return -22;
    struct aefd_startup *b = &f->boot;
    if (b->phase != 2 || b->identity.slot < 2 || b->identity.slot > 4 ||
        b->context.state != 1 || b->context.client.live != 1 ||
        b->context.native.retired ||
        observed.input != b->context.native.input ||
        observed.output != b->context.native.output)
        return -13;
    if (b->context.native.active || b->context.native.busy)
        return -16;
    if ((f->phase != AEFD_FORK_READY && f->phase != AEFD_FORK_IDLE) ||
        f->counter == UINT64_MAX)
        return -75;
    unsigned char raw[608] = {0};
    size_t len = strnlen(path, 32);
    if (!len || len == 32)
        return -22;
    memcpy(raw + 304, path, len);
    if (!arguments(raw + 336, argv, envp))
        return -7;
    int64_t result = aefd_native_enter(&b->context.native);
    if (result)
        return failed(f);
    int64_t pid =
        b->context.native.call(b->context.native.context, 0x10027, 0, 0, 0, 0);
    int64_t parent =
        b->context.native.call(b->context.native.context, 0x1006e, 0, 0, 0, 0);
    memcpy(raw, AEFD_STARTUP_MAGIC, 8);
    put32(raw, 8, 1);
    put32(raw, 12, 304);
    memcpy(raw + 16, "AEFSH001", 8);
    put32(raw, 24, 29);
    put32(raw, 28, 7);
    put32(raw, 32, b->identity.slot);
    put32(raw, 36, b->identity.epoch);
    put32(raw, 40, (uint32_t)parent);
    put32(raw, 44, b->identity.shell_generation);
    result = aefd_session_snapshot(&b->context.session, raw + 48, 128, 0);
    for (unsigned i = 0; i < 7; ++i) {
        struct aefd_native_source s = b->context.native.sources[i];
        put32(raw, 176 + i * 16, s.reference);
        put32(raw, 180 + i * 16, s.selector);
        put32(raw, 184 + i * 16, s.rights);
        put32(raw, 188 + i * 16, s.bound);
    }
    put32(raw, 288, b->context.native.generations[0]);
    put32(raw, 292, b->context.native.generations[1]);
    struct aether_fs_session_identity identity;
    if (result ||
        !aether_fs_session_decode(raw + 16, 32, observed.memory, (long)pid,
                                  (long)parent, &identity) ||
        memcmp(&identity, &b->identity, sizeof identity)) {
        aefd_native_leave(&b->context.native);
        return -22;
    }
    memcpy(raw, AEFD_EXEC_MAGIC, 8);
    put32(raw, 12, 608);
    uint64_t sequence = ++f->counter;
    aefd_put(raw + 296, 0, sequence);
    unsigned budget = AEFD_IO_BUDGET;
    struct aefd_io io = aefd_native_io(&b->context.native);
    if (!move(io, raw, sizeof raw, 1, &budget))
        return failed(f);
    /* Only the owner may commit/publish a new image. Successful exec cannot
     * resume this continuation; a known refusal resumes with exact raw-11. */
    result =
        b->context.native.call(b->context.native.context, 0x23003, 0, 0, 0, 0);
    if (result != -11 || !move(io, raw, 32, 0, &budget) ||
        memcmp(raw, "AEEXR001", 8) || aefd_word(raw, 1) != sequence ||
        aefd_word(raw, 3))
        return failed(f);
    int64_t error = (int64_t)aefd_word(raw, 2);
    if (error >= 0 || error < -4095)
        return failed(f);
    memset(raw, 0, sizeof raw);
    aefd_native_leave(&b->context.native);
    return error;
}
