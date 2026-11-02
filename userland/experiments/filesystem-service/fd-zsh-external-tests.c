/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only actual entry/startup/FD-core control; no target execution. */
#define _POSIX_C_SOURCE 200809L
#include "fd-zsh-external.h"
#include "fd-libc.h"
#include <assert.h>
#include <errno.h>
#include <limits.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static struct aefd_startup *admitted;
static unsigned char frame[304], request[32], reply[32], output[16];
static unsigned mode, starts, ready_calls, main_calls, ignored, rpc_closes[2];
static unsigned source_closes[3], operations, bits;
static size_t input_at, sent, received, written;
static uint64_t revision = 1;
#ifdef AEFD_ZSH_STDIO_TEST
void aefd_test_stdio_unmask(struct aefd_startup *);
void aefd_test_zsh_stdio(struct aefd_startup *, int);
#endif
static void put(unsigned char *raw, unsigned at, uint32_t value)
{
    memcpy(raw + at, &value, 4);
}
static uint32_t word(const unsigned char *raw, unsigned at)
{
    uint32_t value;
    memcpy(&value, raw + at, 4);
    return value;
}
static int64_t call(void *owner, uint64_t op, uint64_t cap, uint64_t a,
                    uint64_t b, uint64_t c)
{
    assert(owner == &mode);
    ++operations;
    if (op == 0x1000e) {
        assert(c == 8);
        if (!cap) {
            assert(a && b && *(uint64_t *)(uintptr_t)a == UINT64_MAX);
            *(uint64_t *)(uintptr_t)b = 0;
        } else
            assert(cap == 2 && a && !b && !*(uint64_t *)(uintptr_t)a);
#ifdef AEFD_ZSH_STDIO_TEST
        if (cap == 2 && (mode == 9 || mode == 10))
            aefd_test_stdio_unmask(admitted);
#endif
        return 0;
    }
    assert(!c);
    if (op == 0x10027)
        return mode == 2 ? 10 : 9;
    if (op == 0x1006e)
        return mode == 2 ? 9 : 7;
    if (op == 0x20004) {
        assert(admitted == aefd_shell_external_startup() &&
               admitted->phase == 2 && admitted->context.native.active &&
               ignored == 1 && bits == 7 && revision == 2 && !main_calls);
        ++ready_calls;
        return mode == 4 ? -5 : 0;
    }
    if (op == 0x24003) {
        assert(cap == 71 || cap == 72);
        ++rpc_closes[cap == 72];
        return 0;
    }
    assert(a && b && b <= 16);
    if (admitted->phase == 1) {
        assert(op == 0x24001 && cap == 71 && input_at + b <= sizeof(frame));
        memcpy((void *)(uintptr_t)a, frame + input_at, (size_t)b);
        input_at += (size_t)b;
        return (int64_t)b;
    }
    assert(admitted->phase == 2);
    if (op == 0x24002) {
        assert(cap == 72 && sent + b <= 32);
        memcpy(request + sent, (void *)(uintptr_t)a, (size_t)b);
        sent += (size_t)b;
        if (sent == 32) {
            memset(reply, 0, sizeof(reply));
            uint32_t action = word(request, 0), count = word(request, 12);
            if (action == 0x10 || action == 0x11) {
                put(reply, 4, action);
                if (action == 0x11 && mode == 6)
                    put(reply, 0, (uint32_t)-95);
                else {
                    if (action == 0x11) {
                        assert(ignored == 1 && !ready_calls &&
                               word(request, 8) == 1 && request[24] == 7);
                        bits = 7;
                        ++revision;
                    }
                    put(reply, 8, 16);
                    memcpy(reply + 16, &revision, 8);
                    put(reply, 24, bits);
                    reply[28] = 1;
                }
            } else {
                unsigned selector = word(request, 8);
                assert(selector < 3 &&
                       word(request, 4) ==
                           (UINT32_C(0x7a000001) | selector << 16));
                if (action == 3)
                    ++source_closes[selector];
                else if (action == 1) {
                    assert(selector == 0 && count == 1);
                    put(reply, 0, 1);
                    reply[16] = 'Q';
                } else {
                    assert(action == 2 && selector == 1 && count <= 16);
                    written = mode == 1 ? 5 : count;
                    memcpy(output, request + 16, written);
                    put(reply, 0, (uint32_t)written);
                }
            }
        }
    } else {
        assert(op == 0x24001 && cap == 71 && sent == 32 && received + b <= 32);
        memcpy((void *)(uintptr_t)a, reply + received, (size_t)b);
        received += (size_t)b;
        if (received == 32)
            sent = received = 0;
    }
    return (int64_t)b;
}
int64_t aefd_startup_native(struct aefd_startup *boot)
{
    ++starts;
    assert(starts == 1 && boot == aefd_shell_external_startup());
    admitted = boot;
    return aefd_startup_start(
        boot, call, &mode,
        (struct aefd_startup_auxv){
            mode == 2 ? UINT64_C(0x40000103) : UINT64_C(0x40000102), 71, 72});
}
int sigaction(int number, const struct sigaction *action, struct sigaction *old)
{
    assert(number == SIGINT && action && !old && !ready_calls &&
           action->sa_handler == SIG_IGN && !action->sa_flags);
    if (mode == 5) {
        errno = EOPNOTSUPP;
        return -1;
    }
    ++ignored;
    return 0;
}
_Noreturn void __assert_fail(const char *expression, const char *file, int line,
                             const char *function)
{
    (void)dprintf(2, "ZSH_ENTRY_ASSERT %s:%d %s (%s)\n", file, line, expression,
                  function);
    abort();
}
_Noreturn void __wrap__Exit(int);
_Noreturn void __real__exit(int value)
{
    assert(starts == 1 && rpc_closes[0] == 1 && rpc_closes[1] == 1);
    assert(value == (mode == 0 || mode == 1 || mode == 8 || mode == 9 ? 19
                     : mode == 4 || mode == 10                        ? 141
                                                                      : 143));
    assert(main_calls == (mode == 0 || mode == 1 || mode == 7 || mode == 8 ||
                                  mode == 9 || mode == 10
                              ? 1U
                              : 0U));
    assert(ready_calls == (mode == 0 || mode == 1 || mode == 4 || mode == 7 ||
                                   mode == 8 || mode == 9 || mode == 10
                               ? 1U
                               : 0U));
    unsigned before = operations;
    assert(__aether_io(1, 1, 0, 0) == -EBADF && operations == before);
    if (mode != 3)
        for (unsigned i = 0; i < 3; ++i)
            assert(source_closes[i] == (mode == 4 || mode == 10 ? 0U : 1U));
    char marker[40];
    int length =
        snprintf(marker, sizeof(marker), "ZSH_EXTERNAL_ENTRY_PASS %u\n", mode);
    assert(length > 0 && (size_t)length < sizeof(marker));
    assert(write(1, marker, (size_t)length) == length);
    _Exit(0);
}
int __real_main(int argc, char **argv)
{
    ++main_calls;
    assert(starts == 1 && ready_calls == 1 && ignored == 1 && bits == 7 &&
           argc == 4 && !strcmp(argv[0], "zsh") && !strcmp(argv[1], "-f") &&
           !strcmp(argv[2], "-i") && !strcmp(argv[3], "+m") && !argv[4]);
    assert(admitted == aefd_shell_external_startup() &&
           admitted->context.client.workspace == admitted->context.workspace &&
           admitted->context.session.map == &admitted->context.map);
#ifdef AEFD_ZSH_STDIO_TEST
    if (mode == 9 || mode == 10) {
        aefd_test_zsh_stdio(admitted, mode == 10);
        return 19;
    }
#endif
    if (mode == 7)
        return __wrap_main(0, NULL);
    int opened = (int)aefd_libc_open(&admitted->context, "/dev/tty", O_RDWR);
    assert(opened == 3);
    assert(aefd_libc_fcntl(&admitted->context, opened, F_DUPFD, 10) == 10);
    assert(__aether_io(3, (unsigned long)opened, 0, 0) == 0);
    struct iovec parts[2] = {{"abc", 3}, {"0123456789ABCDEFGHIJ", 20}};
    errno = ERANGE;
    assert(aether_zsh_vector_write(10, parts, 2) == (mode == 1 ? 5 : 16));
    assert(errno == ERANGE && written == (mode == 1 ? 5U : 16U) &&
           !memcmp(output, "abc0123456789ABC", written));
    unsigned before = operations;
    assert(aether_zsh_vector_write(10, NULL, 1) == -1 && errno == EINVAL);
    parts[0] = (struct iovec){NULL, 1};
    assert(aether_zsh_vector_write(10, parts, 1) == -1 && errno == EFAULT);
    parts[0] = (struct iovec){"x", (size_t)SSIZE_MAX};
    parts[1] = (struct iovec){"x", 1};
    assert(aether_zsh_vector_write(10, parts, 2) == -1 && errno == EINVAL);
    assert(before == operations);
    unsigned char byte = 0xa5;
    errno = ERANGE;
    assert(__aether_io(0, 0, (unsigned long)(uintptr_t)&byte, 1) == 1 &&
           byte == 'Q' && errno == ERANGE);
    assert(__aether_io(32, 1, 0, 0) == 3);
    assert(__aether_io(33, 1, 10, 0) == -EOPNOTSUPP);
    if (mode == 8)
        __wrap__Exit(19);
    return 19;
}
int main(int argc, char **argv)
{
    assert(argc == 2);
    mode = (unsigned)strtoul(argv[1], NULL, 10);
    memcpy(frame, AEFD_STARTUP_MAGIC, 8);
    put(frame, 8, 1);
    put(frame, 12, 304);
    memcpy(frame + 16, "AEFSH001", 8);
    put(frame, 24, 29);
    put(frame, 28, 7);
    put(frame, 32, mode == 2 ? 2 : 1);
    put(frame, 36, 1);
    put(frame, 40, mode == 2 ? 9 : 7);
    put(frame, 44, 1);
    memcpy(frame + 48, AEFD_MAP_MAGIC, 8);
    aefd_put(frame + 48, 1, 31);
    aefd_put(frame + 48, 2, 16);
    for (unsigned i = 0; i < 3; ++i) {
        frame[112 + i * 4] = AEFD_BIND_TERMINAL;
        frame[113 + i * 4] = (unsigned char)i;
        put(frame, 176 + i * 16, UINT32_C(0x7a000001) | i << 16);
        put(frame, 180 + i * 16, i);
        put(frame, 184 + i * 16, i ? 2 : 1);
        put(frame, 188 + i * 16, 16);
    }
    put(frame, 296, mode == 2 ? 0 : UINT32_C(0x76050001));
    put(frame, 300, AEFD_MODE_CONTROL);
    if (mode == 3)
        frame[0] ^= 1;
    errno = ERANGE;
    assert(__aether_io(1, 1, 0, 0) == -EBADF && errno == ERANGE);
    (void)__wrap_main(0, NULL);
    assert(!"CURRENT_ENTRY_MUST_FINALIZE");
    return 1;
}
