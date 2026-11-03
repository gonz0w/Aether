/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-libc.h"
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
_Static_assert(sizeof(AEFD_MAGIC) == 9 && AEFD_MAGIC[7] == '5',
               "HOME_WRITE_MAGIC");
static struct aefd_context context;
static struct {
    unsigned char request[128], reply[128];
    size_t sent, read, length;
    uint64_t mask;
    unsigned calls, requests, closes, payload_writes, payload_closes;
    int mode, reenter;
} fixture;
static unsigned cases;
int aether145_payload_main(int, char **);

static void answer(void)
{
    const unsigned char *request = fixture.request;
    uint64_t opcode = aefd_word(request, 1);
    memset(fixture.reply, 0, sizeof fixture.reply);
    memcpy(fixture.reply, AEFD_MAGIC, 8);
    aefd_put(fixture.reply, 2, aefd_word(request, 2));
    aefd_put(fixture.reply, 3, aefd_word(request, 3));
    fixture.length = 64;
    if (opcode == 1) {
        aefd_put(fixture.reply, 4, 3);
    } else if (opcode == 12) {
        assert(aefd_word(request, 4) <= 1 && aefd_word(request, 5) == 11);
        assert(!memcmp(request + 64, "/home/probe", 11));
        for (unsigned i = 75; i < 128; ++i)
            assert(!request[i]);
        if (fixture.mode == 6)
            aefd_put(fixture.reply, 1, (uint64_t)-13);
        else
            aefd_put(fixture.reply, 4, 3);
    } else if (opcode == 11) {
        assert(aefd_word(request, 4) == 3 && aefd_word(request, 5) == 16);
        assert(!memcmp(request + 64, "AETHER-ZSH-HOME\n", 16));
        for (unsigned i = 80; i < 128; ++i)
            assert(!request[i]);
        aefd_put(fixture.reply, 4, fixture.mode == 1 ? 15 : 16);
        aefd_put(fixture.reply, 5, 64);
        aefd_put(fixture.reply + 64, 0, 14);
        aefd_put(fixture.reply + 64, 2, 99);
        aefd_put(fixture.reply + 64, 3, 16);
        fixture.length = 128;
        if (fixture.mode == 2) {
            aefd_put(fixture.reply, 1, (uint64_t)-5);
            aefd_put(fixture.reply, 4, 0);
            aefd_put(fixture.reply + 64, 0,
                     26); /* reported committed, offset and close receipts */
            aefd_put(fixture.reply + 64, 6, 12);
            aefd_put(fixture.reply + 64, 7, (uint64_t)-5);
        }
        if (fixture.mode == 3)
            aefd_put(fixture.reply, 2, 999);
    } else {
        assert(opcode == 5 && aefd_word(request, 4) == 3);
        if (fixture.mode == 5)
            aefd_put(fixture.reply, 3, 999);
        if (fixture.mode == 7)
            aefd_put(fixture.reply, 1, (uint64_t)-13);
    }
    ++fixture.requests;
    fixture.read = 0;
}
static int64_t native_call(void *unused, uint64_t op, uint64_t cap, uint64_t a,
                           uint64_t b, uint64_t c)
{
    (void)unused;
    ++fixture.calls;
    if (op == 0x1000e) {
        assert(c == 8);
        if (!cap) {
            assert(a && b && *(uint64_t *)(uintptr_t)a == UINT64_MAX);
            *(uint64_t *)(uintptr_t)b = fixture.mask;
            fixture.mask = UINT64_MAX;
        } else {
            assert(cap == 2 && !b);
            fixture.mask = *(uint64_t *)(uintptr_t)a;
        }
        return 0;
    }
    if (op == 0x24003) {
        assert(cap == 71 || cap == 72);
        ++fixture.closes;
        assert(fixture.closes <= 2);
        return 0;
    }
    assert((op == 0x24001 || op == 0x24002) && a && b && b <= 16 && !c);
    assert(cap == (op == 0x24001 ? 71 : 72) && fixture.mask == UINT64_MAX);
    if (fixture.reenter) {
        unsigned before = fixture.calls;
        assert(aefd_context_write(&context, context.home_write_fd,
                                  (const unsigned char *)"AETHER-ZSH-HOME\n",
                                  16) == (context.state == 2 ? -5 : -16));
        assert(fixture.calls == before);
    }
    size_t n = b < 7 ? (size_t)b : 7;
    if (op == 0x24002) {
        assert(fixture.sent + n <= sizeof fixture.request);
        memcpy(fixture.request + fixture.sent, (void *)(uintptr_t)a, n);
        fixture.sent += n;
        if (fixture.sent >= 64) {
            uint64_t opcode = aefd_word(fixture.request, 1);
            if (fixture.sent ==
                (opcode == 1 || opcode == 12 || opcode == 11 ? 128 : 64))
                answer();
        }
    } else {
        if (fixture.mode == 4 && aefd_word(fixture.request, 1) == 11 &&
            fixture.read >= 35)
            return 0;
        assert(fixture.read < fixture.length);
        if (n > fixture.length - fixture.read)
            n = fixture.length - fixture.read;
        memcpy((void *)(uintptr_t)a, fixture.reply + fixture.read, n);
        fixture.read += n;
        if (fixture.read == fixture.length)
            fixture.sent = 0;
    }
    return (int64_t)n;
}
static void setup(int mode)
{
    /* Each fixture is fresh, isolated local storage, never a native admission.
     */
    memset(&context, 0, sizeof context);
    memset(&fixture, 0, sizeof fixture);
    fixture.mask = 0x1234;
    fixture.mode = mode;
    unsigned char raw[AEFD_BINDINGS_BYTES] = {0};
    memcpy(raw, AEFD_MAP_MAGIC, 8);
    aefd_put(raw, 1, 31);
    aefd_put(raw, 2, 16);
    struct aefd_native_source sources[7] = {{0}};
    unsigned generations[2] = {0};
    assert(aefd_context_init(&context, native_call, NULL, 71, 72, raw,
                             sizeof raw, 31, sources, generations, 0) == 0);
    assert(context.home_write_fd == -1);
    ++cases;
}
int aether145_open(const char *path, int flags, ...)
{
    int64_t value = aefd_libc_open(&context, path, flags);
    return value < 0 ? -1 : (int)value;
}
ssize_t aether145_write(int fd, const void *bytes, size_t count)
{
    ++fixture.payload_writes;
    int64_t value = aefd_context_write(&context, fd, bytes, count);
    return value < 0 ? -1 : (ssize_t)value;
}
int aether145_close(int fd)
{
    ++fixture.payload_closes;
    return aefd_context_close(&context, fd) < 0 ? -1 : 0;
}
_Noreturn void __assert_fail(const char *expression, const char *file, int line,
                             const char *function)
{
    printf("assertion %s at %s:%d (%s)\n", expression, file, line, function);
    fflush(NULL);
    _Exit(99);
}
int main(void)
{
    static char helper[] = "/inputs/helper", command[] = "home-write",
                wrong[] = "status";
    char *args[] = {helper, command, NULL}, *bad[] = {helper, wrong, NULL};
#ifndef AEFD_ZSH_HELPER_ENTRY
    (void)args;
    (void)bad;
    setup(0);
    assert(aefd_libc_open(&context, "/home/probe", O_WRONLY) == -EOPNOTSUPP);
    assert(fixture.requests == 0 && fixture.calls == 0);
    aefd_client_abort(&context.client);
    puts("HOME_PARENT_DENIAL_PASS");
#else
    setup(0);
    assert(aether145_payload_main(2, bad) == 64 && fixture.requests == 0);
    aefd_client_abort(&context.client);
    for (int mode =
#ifdef HOME_CLOSE_REFUSAL_ONLY
             7
#else
             0
#endif
         ;
         mode <= 7; ++mode) {
        setup(mode);
        fixture.reenter = 1;
        int result = aether145_payload_main(2, args);
        assert(fixture.mask == 0x1234);
        if (!mode) {
            assert(result == 0 && fixture.requests == 3);
            assert(context.home_write.observation == AEFD_WRITE_REMOTE &&
                   context.home_write.remote.flags == 14);
            assert(context.home_write.requested == 16 &&
                   context.home_write.generation == 31 &&
                   context.home_write.sequence == 2);
            assert(context.home_close_attempted &&
                   context.home_close_status == 0 &&
                   context.home_close_sequence == 3);
            assert(context.home_write_fd ==
                   -1); /* A closed logical number may be reused readonly. */
            static const unsigned char entry[] = "/home/.terminfo/v/vt100";
            int readonly =
                (int)aefd_context_open(&context, entry, sizeof entry - 1, 0);
            assert(readonly >= 0 &&
                   aefd_libc_fcntl(&context, readonly, F_GETFL, 0) == O_RDONLY);
            assert(aefd_context_write(&context, readonly,
                                      (const unsigned char *)"x", 1) == -30);
            struct aefd_write_result retained = context.home_write;
            struct aefd_finish finish;
            assert(!aefd_context_finish(&context, &finish) && !finish.unknown);
            assert(!memcmp(&retained, &context.home_write, sizeof retained));
        } else if (mode == 6) {
            assert(result == 65 && fixture.requests == 1 &&
                   !fixture.payload_writes && !fixture.payload_closes);
        } else {
            assert(result == 66 && fixture.payload_writes == 1 &&
                   fixture.payload_closes == 1);
            if (mode == 2)
                assert(context.home_write.observation == AEFD_WRITE_REMOTE &&
                       (context.home_write.remote.flags & 7) == 2);
            else if (mode != 5 && mode != 7)
                assert(context.home_write.observation == AEFD_WRITE_UNKNOWN);
            else
                assert(context.home_write.observation == AEFD_WRITE_REMOTE &&
                       context.home_close_status < 0);
            unsigned before = fixture.requests;
            assert(aefd_context_write(
                       &context, context.home_write_fd,
                       (const unsigned char *)"AETHER-ZSH-HOME\n", 16) < 0);
            assert(fixture.requests == before);
            struct aefd_finish finish;
            assert(!aefd_context_finish(&context, &finish));
            assert(fixture.requests ==
                   before); /* Failed close is never replayed by finish. */
        }
        aefd_client_abort(&context.client);
        assert(fixture.closes == 2);
    }
    setup(0);
    assert(aefd_libc_open(&context, "/home/probe", O_RDONLY) == -EOPNOTSUPP);
    assert(aefd_libc_open(&context, "/home/probe", O_WRONLY | O_CREAT) ==
           -EOPNOTSUPP);
    assert(aefd_libc_open(&context, "/home/probe", O_WRONLY | O_TRUNC) ==
           -EOPNOTSUPP);
    assert(fixture.requests == 0);
    int fd = (int)aefd_libc_open(&context, "/home/probe", O_WRONLY);
    assert(fd >= 0 && aefd_libc_fcntl(&context, fd, F_GETFL, 0) == O_WRONLY);
    unsigned before = fixture.requests;
    assert(aefd_context_write(&context, fd, (const unsigned char *)"wrong",
                              5) == -22);
    assert(context.home_write.observation == AEFD_WRITE_NOT_SENT &&
           fixture.requests == before);
    assert(aefd_context_write(&context, fd,
                              (const unsigned char *)"AETHER-ZSH-HOME\n",
                              16) == -16);
    aefd_client_abort(&context.client);
    printf("HOME_PROVIDER_PASS cases=%u\n", cases);
#endif
    return 0;
}
