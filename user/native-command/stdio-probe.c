/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual internal musl callback witness; not public stdio or Toybox. */
#include <sys/types.h>
#include <unistd.h>
#include "stdio_impl.h"
#include "transport.h"
static unsigned inject_zero, zero_calls;
static long observed_io(unsigned long op, unsigned long fd, unsigned long p,
                        unsigned long n)
{
    if (inject_zero) {
        zero_calls++;
        return 0;
    }
#ifdef STDIO_PROGRESS
    if (op == 1 && n > 11)
        n = 11;
#endif
    return file_io(op, fd, p, n);
}
#define file_io observed_io
#include "vector-write.h"
#undef file_io
ssize_t fixture_writev(int fd, const struct iovec *parts, int count)
{
    long result = vector_write(fd, parts, count);
    if (result < 0) {
        errno = (int)-result;
        return -1;
    }
    return result;
}
size_t candidate_stdio_write(FILE *, const unsigned char *, size_t);
static _Thread_local volatile unsigned cookie = 23;
static FILE stream(unsigned char *buffer, size_t prefix)
{
    return (FILE){.buf = buffer,
                  .buf_size = 64,
                  .wbase = buffer,
                  .wpos = buffer + prefix,
                  .wend = buffer + 64,
                  .fd = 1};
}
int main(int argc, char **argv)
{
    if (cookie != 23 || argc != 1 || strcmp(argv[0], "cat") || argv[1] ||
        !bootstrap())
        return 118;
    unsigned char buffer[64] = {0}, data[32] = {0};
    unsigned before = channel_calls;
    FILE f = stream(buffer, 3);
    inject_zero = 1;
    errno = 0;
    if (candidate_stdio_write(&f, data, 5) != 0 || errno != EIO ||
        !(f.flags & F_ERR) || f.wpos || f.wbase || f.wend || zero_calls != 1 ||
        channel_calls != before)
        return 118;
    inject_zero = 0;
#if !defined(STDIO_ERROR) && !defined(STDIO_PROGRESS)
    /* Real zero-byte request validates the live native output binding. */
    f = stream(buffer, 0);
    if (candidate_stdio_write(&f, data, 0) != 0 || (f.flags & F_ERR) ||
        f.wpos != buffer || f.wbase != buffer || f.wend != buffer + 64)
        return 118;
#endif
    int failed = 0;
    for (;;) {
        size_t used = 0;
#ifdef STDIO_PROGRESS
        size_t goal = 22;
#elif defined(STDIO_ERROR)
        size_t goal = 11;
#else
        size_t goal = sizeof data;
#endif
        while (used < goal) {
            ssize_t got = read(0, data + used, goal - used);
            if (got < 0)
                return 118;
            if (!got)
                break;
            used += (size_t)got;
        }
        if (!used)
            break;
#if defined(STDIO_ERROR) || defined(STDIO_PROGRESS)
        size_t prefix = used < 3 ? used : 3;
#else
        size_t prefix = used < 17 ? used : 17;
#endif
        memcpy(buffer, data, prefix);
        f = stream(buffer, prefix);
        errno = 0;
        size_t done = candidate_stdio_write(&f, data + prefix, used - prefix);
        if (f.flags & F_ERR) {
#ifdef STDIO_PROGRESS
            size_t confirmed = 8;
#else
            size_t confirmed = 0;
#endif
#ifdef STDIO_EXPECT_EINTR
            int expected_error = EINTR;
#else
            int expected_error = EIO;
#endif
            if (done != confirmed || f.wpos || f.wbase || f.wend ||
                errno != expected_error)
                return 118;
            failed = 1;
            break;
        }
        if (done != used - prefix || f.wpos != buffer || f.wbase != buffer ||
            f.wend != buffer + 64)
            return 118;
    }
    if (poisoned) {
        before = channel_calls;
        f = stream(buffer, 0);
        f.fd = 2;
        if (candidate_stdio_write(&f, data, 1) != 0 || !(f.flags & F_ERR) ||
            channel_calls != before)
            return 118;
    }
    for (int fd = 0; fd < 3; fd++)
        if (close(fd))
            failed = 1;
    if (poisoned && channel_calls != before)
        return 118;
    return failed ? 1 : 0;
}
