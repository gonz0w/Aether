// SPDX-License-Identifier: BSD-2-Clause
#include <sys/types.h>
#include "stdio_impl.h"
#include "vector.h"
#include <assert.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <sys/uio.h>
#include <unistd.h>

// Fixture-only assertion exit avoids testing the emulator's abort path.
_Noreturn void __assert_fail(const char *expr, const char *file, int line,
                             const char *function)
{
    (void)file;
    (void)line;
    (void)function;
    const char marker[] = "Assertion failed: ";
    (void)write(2, marker, sizeof(marker) - 1);
    (void)write(2, expr, strlen(expr));
    (void)write(2, "\n", 1);
    _Exit(99);
}

size_t candidate_stdio_write(FILE *, const unsigned char *, size_t);
size_t control_stdio_write(FILE *, const unsigned char *, size_t);
static struct tv_state state;
static unsigned char expected[64], actual[64];
static size_t committed, acknowledged, total, cap;
static unsigned calls, kind, fail_at, triggered;

static struct tv_reply backend(void *ctx, unsigned sink,
                               const unsigned char *data, size_t size)
{
    (void)ctx;
    assert(sink == 0 && committed + size <= total);
    assert(!memcmp(data, expected + committed, size));
    unsigned fault = kind && calls++ == fail_at;
    if (fault) {
        triggered = 1;
        if (kind == 1)
            return (struct tv_reply){1, 0, -EIO};
        if (kind == 2)
            return (struct tv_reply){1, 0, 0};
        memcpy(actual + committed, data, size);
        committed += size;
        return (struct tv_reply){kind == 3 ? 0 : 1, size + 1, 0};
    }
    if (!kind)
        calls++;
    size_t n = size < cap ? size : cap;
    memcpy(actual + committed, data, n);
    committed += n;
    acknowledged += n;
    return (struct tv_reply){1, n, 0};
}
ssize_t fixture_writev(int fd, const struct iovec *iov, int count)
{
    assert(count >= 0 && count <= 2);
    struct tv_part parts[2] = {{0}};
    for (int i = 0; i < count; i++)
        parts[i] = (struct tv_part){iov[i].iov_base, iov[i].iov_len};
    struct tv_reply r = tv_write(&state, fd == 1 ? 0 : 1, parts,
                                 (unsigned)count, backend, NULL);
    if (!r.known || r.error) {
        errno = r.known ? -r.error : EIO;
        return -1;
    }
    return (ssize_t)r.count;
}
int main(void)
{
    unsigned char prefix[32], incoming[32], storage[64];
    for (unsigned i = 0; i < 32; i++) {
        prefix[i] = (unsigned char)i;
        incoming[i] = (unsigned char)(255 - i);
    }
    int pipefd[2];
    assert(!pipe(pipefd));
    FILE baseline = {.wbase = prefix,
                     .wpos = prefix + 5,
                     .buf = storage,
                     .buf_size = sizeof(storage),
                     .fd = pipefd[1]};
    assert(control_stdio_write(&baseline, incoming, 7) == 7);
    assert(!close(pipefd[1]));
    unsigned char received[16];
    assert(read(pipefd[0], received, sizeof(received)) == 12);
    assert(!memcmp(received, prefix, 5) && !memcmp(received + 5, incoming, 7));
    assert(!close(pipefd[0]));
    unsigned scenarios = 0;
    for (unsigned p = 0; p <= 17; p++)
        for (unsigned q = 0; q <= 17; q++)
            for (unsigned limit = 0; limit < 3; limit++)
                for (kind = 0; kind < 5; kind++)
                    for (fail_at = 0; fail_at < 2; fail_at++) {
                        state = (struct tv_state){0};
                        committed = acknowledged = calls = triggered = 0;
                        total = p + q;
                        cap = limit == 0 ? 1 : limit == 1 ? 7 : 16;
                        memcpy(expected, prefix, p);
                        memcpy(expected + p, incoming, q);
                        memset(actual, 0, sizeof(actual));
                        FILE f = {.wbase = prefix,
                                  .wpos = prefix + p,
                                  .buf = storage,
                                  .buf_size = sizeof(storage),
                                  .fd = 1};
                        size_t result = candidate_stdio_write(&f, incoming, q);
                        unsigned failed =
                            triggered && (kind != 2 || total != 0);
                        size_t confirmed_new =
                            acknowledged > p ? acknowledged - p : 0;
                        assert(result == (failed ? confirmed_new : q));
                        assert(!!(f.flags & F_ERR) == failed);
                        assert(!memcmp(actual, expected, committed));
                        if (failed)
                            assert(!f.wpos && !f.wbase && !f.wend);
                        else {
                            assert(committed == total);
                            assert(f.wpos == storage && f.wbase == storage);
                            assert(f.wend == storage + sizeof(storage));
                        }
                        assert(state.poisoned == (triggered && kind >= 3));
                        if (state.poisoned) {
                            unsigned before = calls;
                            struct iovec diagnostic = {incoming, 1};
                            assert(fixture_writev(2, &diagnostic, 1) == -1);
                            assert(errno == EIO && calls == before);
                        }
                        scenarios++;
                    }
    printf("PASS: %u musl-loop cases and pipe control\n", scenarios);
    return 0;
}
