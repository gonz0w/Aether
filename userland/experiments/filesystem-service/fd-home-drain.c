/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-home-drain.h"
#include <sched.h>
#include <unistd.h>
#ifdef AEFD_HOME_DRAIN_HOST_TEST
unsigned long aefd_home_drain_test_auxv(unsigned long);
_Noreturn void aefd_home_drain_test_trap(void);
#define getauxval aefd_home_drain_test_auxv
#else
#include <sys/auxv.h>
#if !defined(AEFD_HOME_DRAIN_CASE) || AEFD_HOME_DRAIN_CASE < 1 ||              \
    AEFD_HOME_DRAIN_CASE > 8
#error "home drain requires one exact matched case1..8"
#endif
#endif

static const unsigned char payload[] = "AF09-HOME-WRITE\n";
static struct aefd_home_drain retained;

static void put32(unsigned char *raw, unsigned at, uint32_t value)
{
    for (unsigned i = 0; i < 4; ++i)
        raw[at + i] = (unsigned char)(value >> (i * 8));
}
static int selected(unsigned which)
{
    return which >= AEFD_DRAIN_FILE_PREFIX &&
           which <= AEFD_DRAIN_PENDING_FRAGMENT;
}
static int snapshot(struct aefd_fork *f, unsigned char raw[608],
                    struct aefd_startup_auxv observed)
{
    struct aefd_startup *b = &f->boot;
    struct aefd_context *c = &b->context;
    if (b->phase != 2 || c->state != 1 || !c->client.live || c->native.active ||
        c->native.busy || c->native.retired ||
        observed.input != c->native.input ||
        observed.output != c->native.output || !c->native.call)
        return 0;
    int64_t pid = c->native.call(c->native.context, 0x10027, 0, 0, 0, 0);
    int64_t parent = c->native.call(c->native.context, 0x1006e, 0, 0, 0, 0);
    memcpy(raw, AEFD_STARTUP_MAGIC, 8);
    put32(raw, 8, 1);
    put32(raw, 12, 304);
    memcpy(raw + 16, "AEFSH001", 8);
    put32(raw, 24, 29);
    put32(raw, 28, 7);
    put32(raw, 32, b->identity.slot);
    put32(raw, 36, b->identity.epoch);
    if (parent < 0 || (uint64_t)parent > UINT32_MAX)
        return 0;
    put32(raw, 40, (uint32_t)parent);
    put32(raw, 44, b->identity.shell_generation);
    struct aether_fs_session_identity identity;
    if (!aether_fs_session_decode(raw + 16, 32, observed.memory, (long)pid,
                                  (long)parent, &identity) ||
        memcmp(&identity, &b->identity, sizeof identity) ||
        aefd_context_snapshot(c, raw + 48, 128, 0))
        return 0;
    for (unsigned i = 0; i < 7; ++i) {
        struct aefd_native_source s = c->native.sources[i];
        put32(raw, 176 + i * 16, s.reference);
        put32(raw, 180 + i * 16, s.selector);
        put32(raw, 184 + i * 16, s.rights);
        put32(raw, 188 + i * 16, s.bound);
    }
    put32(raw, 288, c->native.generations[0]);
    put32(raw, 292, c->native.generations[1]);
    put32(raw, 296, c->native.factory);
    return 1;
}
int aefd_home_drain_reference(struct aefd_fork *f, struct aefd_home_drain *out,
                              unsigned which, int file, const int pair[2],
                              struct aefd_startup_auxv observed)
{
    if (!out)
        return 0;
    memset(out, 0, sizeof *out);
    if (!f || !pair || !selected(which) ||
        (which == AEFD_DRAIN_FORK_PREFIX ? f->boot.identity.slot != 1
                                         : f->boot.identity.slot != 2) ||
        !snapshot(f, out->bytes, observed))
        return 0;
    struct aefd_context *c = &f->boot.context;
    struct aefd_binding binding, read_end, write_end;
    if (aefd_bindings_lookup(&c->map, c->client.generation, file, &binding) !=
            1 ||
        binding.kind != AEFD_BIND_FILE || binding.cloexec ||
        aefd_bindings_lookup(&c->map, c->client.generation, pair[0],
                             &read_end) != 1 ||
        aefd_bindings_lookup(&c->map, c->client.generation, pair[1],
                             &write_end) != 1 ||
        read_end.kind != AEFD_BIND_PIPE || write_end.kind != AEFD_BIND_PIPE ||
        read_end.cloexec || write_end.cloexec ||
        (read_end.selector != 3 && read_end.selector != 5) ||
        write_end.selector != read_end.selector + 1 ||
        !c->native.sources[read_end.selector].reference ||
        c->native.sources[read_end.selector].rights != 1 ||
        !c->native.sources[write_end.selector].reference ||
        c->native.sources[write_end.selector].rights != 2)
        return 0;
    if (which == AEFD_DRAIN_FORK_PREFIX) {
        if (f->counter == UINT64_MAX ||
            !aefd_fork_encode(
                out->bytes, 304, out->bytes, 304, observed,
                (long)c->native.call(c->native.context, 0x10027, 0, 0, 0, 0),
                (long)c->native.call(c->native.context, 0x1006e, 0, 0, 0, 0),
                f->counter + 1))
            return 0;
        out->length = 304;
    } else if (which == AEFD_DRAIN_EXEC_PREFIX) {
        if (f->counter == UINT64_MAX)
            return 0;
        memcpy(out->bytes, AEFD_EXEC_MAGIC, 8);
        put32(out->bytes, 12, 608);
        aefd_put(out->bytes + 296, 0, f->counter + 1);
        memcpy(out->bytes + 304, "/inputs/helper", 14);
        aefd_put(out->bytes + 336, 0, 2);
        aefd_put(out->bytes + 336, 1, 1);
        memcpy(out->bytes + 352, "helper", 6);
        memcpy(out->bytes + 384, "hello", 5);
        memcpy(out->bytes + 480, "PATH=/inputs", 12);
        out->length = 608;
    } else if (which == AEFD_DRAIN_STREAM) {
        memset(out->bytes, 0, sizeof out->bytes);
        put32(out->bytes, 0, 2);
        put32(out->bytes, 4, c->native.sources[write_end.selector].reference);
        put32(out->bytes, 8, write_end.selector);
        put32(out->bytes, 12, 16);
        memcpy(out->bytes + 16, payload, (sizeof payload - 1));
        out->length = 32;
    } else {
        memset(out->bytes, 0, sizeof out->bytes);
        const uint64_t args[4] = {binding.selector, (sizeof payload - 1), 0, 0};
        if (!aefd_request(out->bytes, c->client.generation, c->client.sequence,
                          11, args))
            return 0;
        memcpy(out->bytes + 64, payload, (sizeof payload - 1));
        out->length = 128;
    }
    return 1;
}
int aefd_home_drain_run(struct aefd_fork *f, unsigned which)
{
    if (!f || !selected(which) || f->boot.phase != 2 ||
        f->boot.identity.slot != 1 || f->phase != AEFD_FORK_IDLE)
        return 110;
    int64_t file = aefd_home_probe_open(
        &f->boot.context, (const unsigned char *)"probe", 5, 1, 0);
    if (file < 0 || file >= 16)
        return 111;
    int pair[2];
    if (pipe(pair))
        return 112;
    struct aefd_startup_auxv observed = {getauxval(0xa000), getauxval(0xa001),
                                         getauxval(0xa002)};
    /* Capture before copy. Only this parent's validated reference is retained
     * for the fork-prefix case; the child cannot construct a nested request. */
    if (!aefd_home_drain_reference(f, &retained, AEFD_DRAIN_FORK_PREFIX,
                                   (int)file, pair, observed))
        return 113;
    pid_t pid = fork();
    if (pid < 0)
        return 114;
    if (pid) {
        (void)f->boot.context.native.call(f->boot.context.native.context,
                                          0x100e7, 0, 0, 0, 0);
        __builtin_trap();
    }
    observed = (struct aefd_startup_auxv){getauxval(0xa000), getauxval(0xa001),
                                          getauxval(0xa002)};
    if (f->phase != AEFD_FORK_READY || f->boot.identity.slot != 2 ||
        (which != AEFD_DRAIN_FORK_PREFIX &&
         !aefd_home_drain_reference(f, &retained, which, (int)file, pair,
                                    observed)) ||
        aefd_startup_ready(&f->boot))
        return 116;
    struct aefd_native *n = &f->boot.context.native;
    if (aefd_native_enter(n))
        return 117;
    struct aefd_io io = aefd_native_io(n);
    int valid = io.write(io.context, retained.bytes, 16) == 16 &&
                io.write(io.context, retained.bytes + 16, 16) == 16;
    aefd_native_leave(n);
    if (!valid)
        return 118;
    for (;;)
        if (sched_yield())
            return 119;
}
#ifndef AEFD_HOME_DRAIN_HOST_TEST
int main(int argc, char **argv);
int main(int argc, char **argv)
{
    (void)argv;
    if (argc == 3)
        (void)aefd_home_drain_run(aefd_shell_fork_context(),
                                  AEFD_HOME_DRAIN_CASE);
    /* Setup/transfer failures must not return through libc descriptor finish.
     */
    __builtin_trap();
}
#endif
