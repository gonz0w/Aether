/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only fault provider; positive data comes from the real opened file. */
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

ssize_t aether_hash_test_read(int fd, void *buffer, size_t count)
{
    static unsigned calls;
    const char *mode = getenv("AETHER_HASH_READ_FAULT");
    ++calls;
    if (mode && (!strcmp(mode, "initial-eio") ||
                 (!strcmp(mode, "partial-eio") && calls > 1))) {
        errno = EIO;
        return -1;
    }
    if (mode && !strcmp(mode, "partial-eio") && count > 3)
        count = 3;
    return read(fd, buffer, count);
}
