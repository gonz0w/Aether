/* SPDX-License-Identifier: BSD-2-Clause */
/* Native vector witness, not Toybox or musl's stdio callback. */
#include "transport.h"
#include "vector-write.h"
#include <unistd.h>
static _Thread_local volatile unsigned cookie = 23;
int main(int argc, char **argv)
{
    if (cookie != 23 || argc != 1 || strcmp(argv[0], "cat") || argv[1] ||
        !bootstrap())
        return 117;
    unsigned before = channel_calls;
    unsigned char b[11] = {0};
    struct iovec bad[2] = {{b, 1}, {0, (size_t)SSIZE_MAX}};
    /* Null validation must precede aggregate overflow and copying. */
    if (vector_write(1, bad, 2) != -EFAULT ||
        vector_write(0, bad, 2) != -EBADF || vector_write(1, 0, 1) != -EINVAL ||
        vector_write(1, bad, -1) != -EINVAL ||
        vector_write(1, bad, 3) != -EINVAL)
        return 117;
    bad[1].iov_base = b;
    if (vector_write(1, bad, 2) != -EINVAL || channel_calls != before)
        return 117;
    int failed = 0;
    ssize_t n;
    while ((n = read(0, b, sizeof b)) > 0) {
        for (size_t at = 0; at < (size_t)n;) {
            size_t remaining = (size_t)n - at;
            size_t first = remaining < 3 ? remaining : 3;
            struct iovec parts[2] = {{b + at, first},
                                     {b + at + first, remaining - first}};
            long done = vector_write(1, parts, 2);
            if (done <= 0) {
                if (done != -EIO && done != -EINTR)
                    return 117;
                failed = 1;
                goto finish;
            }
            at += (size_t)done;
        }
    }
    if (n < 0)
        failed = 1;
finish:
    if (poisoned) {
        before = channel_calls;
        struct iovec diag = {(void *)"D", 1};
        if (vector_write(2, &diag, 1) != -EIO || channel_calls != before)
            return 117;
    }
    for (int fd = 0; fd < 3; fd++)
        if (close(fd))
            failed = 1;
    if (poisoned && channel_calls != before)
        return 117;
    before = channel_calls;
    if (vector_write(1, 0, 0) != -EBADF || channel_calls != before)
        return 117;
    return failed ? 1 : 0;
}
