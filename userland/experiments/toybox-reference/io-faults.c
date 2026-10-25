// SPDX-License-Identifier: BSD-2-Clause
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

ssize_t __real_read(int fd, void *buf, size_t count);
ssize_t __real_write(int fd, const void *buf, size_t count);
int __real_close(int fd);

static int selected(const char *name)
{
    const char *mode = getenv("TOYBOX_IO_FAULT");
    return mode && !strcmp(mode, name);
}

static void witness(void)
{
    static const char text[] = "IO_FAULT_INJECTED\n";
    if (__real_write(2, text, sizeof(text) - 1) != sizeof(text) - 1)
        _exit(90);
}

ssize_t __wrap_read(int fd, void *buf, size_t count)
{
    static int seen;
    if (fd == 0 && selected("read-short") && count > 3) {
        count = 3;
        if (!seen++)
            witness();
    }
    if (fd == 0 && selected("read-eintr") && !seen++) {
        witness();
        errno = EINTR;
        return -1;
    }
    return __real_read(fd, buf, count);
}

ssize_t __wrap_write(int fd, const void *buf, size_t count)
{
    static int seen;
    if (fd == 1 && selected("write-short") && count > 2) {
        count = 2;
        if (!seen++)
            witness();
    }
    if (fd == 1 && selected("write-eintr") && !seen++) {
        witness();
        errno = EINTR;
        return -1;
    }
    if (fd == 1 && selected("write-prefix-error")) {
        if (seen++) {
            witness();
            errno = EIO;
            return -1;
        }
        if (count > 2)
            count = 2;
    }
    return __real_write(fd, buf, count);
}

int __wrap_close(int fd)
{
    int result = __real_close(fd);
    if (fd > 2 && selected("close-error") && result == 0) {
        witness();
        errno = EIO;
        return -1;
    }
    return result;
}
