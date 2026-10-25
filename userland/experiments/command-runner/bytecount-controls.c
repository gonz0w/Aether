/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only deterministic libc-call injection, not native transport evidence.
 */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
extern int bytecount_main(int, char **);
static const char *mode;
static unsigned reads, writes, closes[2], remaining;
static char output[32];
static size_t used;
ssize_t controlled_read(int fd, void *p, size_t n)
{
    if (fd != 0)
        abort();
    reads++;
    if (!strcmp(mode, "read-error")) {
        errno = EIO;
        return -1;
    }
    if (!strcmp(mode, "read-eagain")) {
        errno = EAGAIN;
        return -1;
    }
    if (!strcmp(mode, "read-eintr") && reads == 1) {
        errno = EINTR;
        return -1;
    }
    if (!strcmp(mode, "read-overlong"))
        return (ssize_t)n + 1;
    if (!remaining)
        return 0;
    size_t k = remaining < 3 ? remaining : 3;
    if (k > n)
        k = n;
    memset(p, 0xa5, k);
    remaining -= (unsigned)k;
    return (ssize_t)k;
}
ssize_t controlled_write(int fd, const void *p, size_t n)
{
    if (fd == 2)
        return (ssize_t)n;
    if (fd != 1)
        abort();
    writes++;
    if (!strcmp(mode, "write-error")) {
        errno = ENOSPC;
        return -1;
    }
    if (!strcmp(mode, "write-zero"))
        return 0;
    if (!strcmp(mode, "write-overlong"))
        return (ssize_t)n + 1;
    if (!strcmp(mode, "write-eintr") && writes == 1) {
        errno = EINTR;
        return -1;
    }
    /* Force one-byte writes so decimal output cannot rely on atomic completion.
     */
    if (!n || used == sizeof output)
        abort();
    output[used++] = *(const char *)p;
    return 1;
}
int controlled_close(int fd)
{
    if (fd < 0 || fd > 1)
        abort();
    closes[fd]++;
    if (!strcmp(mode, "close-error") || !strcmp(mode, "close-eintr")) {
        errno = !strcmp(mode, "close-eintr") ? EINTR : EIO;
        return -1;
    }
    return 0;
}
int main(int argc, char **argv)
{
    if (argc != 2)
        return 2;
    mode = argv[1];
    remaining = 137;
    char *args[] = {"custom-argv-zero", "--decimal", 0};
    int result = bytecount_main(2, args);
    int success = !strcmp(mode, "short-io") || !strcmp(mode, "read-eintr") ||
                  !strcmp(mode, "write-eintr");
    if (result != (success ? 0 : 1) || closes[0] != 1 || closes[1] != 1)
        return 3;
    if (success && (used != 4 || memcmp(output, "137\n", 4)))
        return 4;
    if (!strncmp(mode, "read-", 5) && !success && writes)
        return 5;
    if (!strcmp(mode, "write-zero") && writes != 1)
        return 6;
    if (!strcmp(mode, "read-eagain") && reads != 1)
        return 7;
    return 0;
}
