/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-exec.h"
int aefd_fork_baseline_main(void);
#define main aefd_fork_baseline_main
#include "fd-fork-stage-tests.c"
#undef main
static unsigned char exec_sent[608], exec_reply[32];
static size_t exec_written, exec_read, exec_limit, exec_chunk;
static int exec_corrupt, exec_ready_error;
static int64_t exec_park;
static unsigned exec_ready_calls;
static int64_t exec_call(void *context, uint64_t op, uint64_t cap, uint64_t a,
                         uint64_t b, uint64_t c)
{
    if (op == 0x20004) {
        assert(f.fork.boot.phase == 2 && f.fork.boot.context.state == 1);
        assert(f.fork.boot.context.native.active && !cap && !a && !b && !c);
        ++exec_ready_calls;
        return exec_ready_error;
    }
    if (op == 0x23003) {
        assert(exec_written == 608 && !cap && !a && !b && !c);
        memcpy(exec_reply, "AEEXR001", 8);
        aefd_put(exec_reply, 1, f.fork.counter);
        aefd_put(exec_reply, 2, (uint64_t)-2LL);
        if (exec_corrupt >= 0)
            exec_reply[(unsigned)exec_corrupt] ^= 1;
        return exec_park;
    }
    if (op == 0x24001 || op == 0x24002) {
        assert(a && b && b <= 16 && !c);
        size_t n = (size_t)b;
        if (n > exec_chunk)
            n = exec_chunk;
        if (op == 0x24002) {
            assert(cap == 82 && exec_written + n <= sizeof exec_sent);
            memcpy(exec_sent + exec_written, (const void *)(uintptr_t)a, n);
            exec_written += n;
        } else {
            assert(cap == 81);
            if (n > exec_limit - exec_read)
                n = exec_limit - exec_read;
            memcpy((void *)(uintptr_t)a, exec_reply + exec_read, n);
            exec_read += n;
        }
        return (int64_t)n;
    }
    return call(context, op, cap, a, b, c);
}
static void exec_setup(void)
{
    setup();
    struct aefd_startup_auxv grants = child_setup();
    assert(aefd_fork_child(&f.fork, grants, rebind, &f) == 0);
    assert(f.fork.phase == AEFD_FORK_READY && f.new_closes == 0);
    f.fork.boot.context.native.call = exec_call;
    exec_written = exec_read = 0;
    exec_limit = 32;
    exec_chunk = 16;
    exec_corrupt = -1;
    exec_park = -11;
    exec_ready_error = 0;
    exec_ready_calls = 0;
    memset(exec_sent, 0, sizeof exec_sent);
    memset(exec_reply, 0, sizeof exec_reply);
}
static int64_t attempt(void)
{
    char *args[] = {"helper", "hello", NULL};
    char *env[] = {"PATH=/inputs", NULL};
    return aefd_exec(&f.fork, f.aux, "/inputs/helper", args, env);
}
int main(int argc, char **argv)
{
    unsigned checks = 0;
    for (size_t chunk = 1; chunk <= 16; ++chunk) {
        exec_setup();
        exec_chunk = chunk;
        unsigned char before[128], after[128];
        assert(aefd_context_snapshot(&f.fork.boot.context, before,
                                     sizeof before, 0) == 0);
        uint64_t mask = f.mask;
        assert(attempt() == -2 && exec_written == 608 && f.new_closes == 0 &&
               f.mask == mask);
        assert(!memcmp(exec_sent, AEFD_EXEC_MAGIC, 8) &&
               aether_fs_session_u32(exec_sent + 12) == 608);
        assert(aefd_word(exec_sent + 296, 0) == 2 &&
               !memcmp(exec_sent + 304, "/inputs/helper", 14));
        assert(aefd_word(exec_sent + 336, 0) == 2 &&
               aefd_word(exec_sent + 336, 1) == 1);
        assert(aefd_context_snapshot(&f.fork.boot.context, after, sizeof after,
                                     0) == 0);
        assert(!memcmp(before, after, sizeof before));
        ++checks;
    }
    for (size_t prefix = 0; prefix < 32; ++prefix) {
        exec_setup();
        exec_limit = prefix;
        assert(attempt() == -5 && f.fork.phase == AEFD_FORK_FAILED &&
               f.new_closes == 2);
        ++checks;
    }
    for (unsigned bad = 0; bad < 32; ++bad) {
        if (bad >= 16 && bad < 24)
            continue; /* errno corruption can be a valid private errno */
        exec_setup();
        exec_corrupt = (int)bad;
        assert(attempt() == -5 && f.fork.phase == AEFD_FORK_FAILED);
        ++checks;
    }
    for (unsigned lane = 0; lane < 3; ++lane) {
        exec_setup();
        exec_park = lane == 0 ? 0 : lane == 1 ? -2 : 10;
        assert(attempt() == -5 && f.fork.phase == AEFD_FORK_FAILED);
        ++checks;
    }
    exec_setup();
    f.fork.boot.phase = 0;
    assert(aefd_startup_ready(&f.fork.boot) == -22 && !exec_ready_calls);
    ++checks;
    exec_setup();
    assert(aefd_startup_ready(&f.fork.boot) == 0 && exec_ready_calls == 1);
    ++checks;
    exec_setup();
    exec_ready_error = -13;
    assert(aefd_startup_ready(&f.fork.boot) == -13 && f.new_closes == 2);
    ++checks;
    exec_setup();
    f.fork.counter = UINT64_MAX;
    assert(attempt() == -75 && !exec_written && f.new_closes == 0);
    ++checks;
    exec_setup();
    f.fork.boot.context.native.active = 1;
    assert(attempt() == -16 && !exec_written);
    ++checks;
    exec_setup();
    assert(attempt() == -2);
    if (argc == 2) {
        FILE *file = fopen(argv[1], "wb");
        assert(file);
        assert(fwrite(exec_sent, 1, sizeof exec_sent, file) ==
               sizeof exec_sent);
        assert(!fclose(file));
    } else
        assert(argc == 1);
    printf("%u exec/readiness checks pass\n", checks);
    return 0;
}
