/* SPDX-License-Identifier: BSD-2-Clause */
/* Public musl stdio witness; no private FILE mutation or Toybox applet. */
#include "transport.h"
#include "vector-write.h"
#include <stdio.h>
#include <unistd.h>
ssize_t fixture_writev(int fd, const struct iovec *parts, int count)
{
    long result = vector_write(fd, parts, count);
    if (result < 0) {
        errno = (int)-result;
        return -1;
    }
    return result;
}
static _Thread_local volatile unsigned cookie = 23;
int main(int argc, char **argv)
{
#ifdef PUBLIC_DIAG
    const char *name = "client";
#else
    const char *name = "cat";
#endif
    if (cookie != 23 || argc < 1 || strcmp(argv[0], name) || argv[argc] ||
        !bootstrap())
        return 119;
    char output_buffer[32];
    if (setvbuf(stdout, output_buffer, _IOFBF, sizeof output_buffer))
        return 119;
    int status = 0;
#ifdef PUBLIC_USAGE
    if (argc != 2)
        return 119;
    status = 64;
    int result =
        fprintf(stderr, "%s", "cat: this profile accepts stdin only\n");
#ifdef PUBLIC_DIAG_ERROR
    if (result >= 0 || !ferror(stderr) || errno != EIO)
        return 119;
#else
    if (result != 37 || ferror(stderr))
        return 119;
#endif
#else
    if (argc != 1)
        return 119;
    unsigned char data[32];
    for (;;) {
        size_t used = 0;
#ifdef PUBLIC_ERROR
        size_t goal = 11;
#else
        size_t goal = sizeof data;
#endif
        while (used < goal) {
            ssize_t got = read(0, data + used, goal - used);
            if (got < 0)
                return 119;
            if (!got)
                break;
            used += (size_t)got;
        }
        if (!used)
            break;
        unsigned before = channel_calls;
#ifdef PUBLIC_ERROR
        if (fwrite(data, 1, used, stdout) != used || channel_calls != before)
            return 119;
#else
        size_t prefix = used < 17 ? used : 17;
        if (fwrite(data, 1, prefix, stdout) != prefix ||
            channel_calls != before ||
            fwrite(data + prefix, 1, used - prefix, stdout) != used - prefix)
            return 119;
        if (used == 32 && channel_calls == before)
            return 119;
#endif
        errno = 0;
        if (fflush(stdout) == EOF) {
#ifdef PUBLIC_EINTR
            int expected_error = EINTR;
#else
            int expected_error = EIO;
#endif
            if (!ferror(stdout) || errno != expected_error)
                return 119;
            status = 1;
            break;
        }
        if (ferror(stdout))
            return 119;
    }
#ifdef PUBLIC_DIAG
#ifndef PUBLIC_SKIP_DIAG
    if (fprintf(stderr, "%s", "D\n") != 2 || ferror(stderr))
        return 119;
#endif
#endif
#endif
    if (poisoned) {
        unsigned before = channel_calls;
        if (fprintf(stderr, "%s", "D") >= 0 || !ferror(stderr) ||
            errno != EIO || channel_calls != before)
            return 119;
    }
    unsigned before = channel_calls;
    if (fflush(NULL) == EOF && !status)
        status = 1;
    if (poisoned && channel_calls != before)
        return 119;
    for (int fd = 0; fd < 3; fd++)
        if (close(fd) && !status)
            status = 1;
    if (poisoned && channel_calls != before)
        return 119;
    return status;
}
