// SPDX-License-Identifier: BSD-2-Clause
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

ssize_t __wrap_read(int fd, void *buf, size_t count);
ssize_t __wrap_write(int fd, const void *buf, size_t count);
int __wrap_close(int fd);
static int closes;
static int markers;
ssize_t __real_read(int fd, void *buf, size_t count)
{
    (void)fd;
    memset(buf, 'x', count);
    return (ssize_t)count;
}
ssize_t __real_write(int fd, const void *buf, size_t count)
{
    if (fd == 2) {
        assert(count == 18);
        assert(!memcmp(buf, "IO_FAULT_INJECTED\n", count));
        markers++;
    }
    return (ssize_t)count;
}
int __real_close(int fd)
{
    assert(fd == 3);
    closes++;
    return 0;
}
int main(int argc, char **argv)
{
    char data[8] = {0};
    assert(argc == 2);
    assert(!setenv("TOYBOX_IO_FAULT", argv[1], 1));
    if (!strcmp(argv[1], "read-short")) {
        assert(__wrap_read(0, data, sizeof(data)) == 3);
        assert(__wrap_read(0, data, sizeof(data)) == 3);
    } else if (!strcmp(argv[1], "write-short")) {
        assert(__wrap_write(1, data, sizeof(data)) == 2);
        assert(__wrap_write(1, data, sizeof(data)) == 2);
    } else if (!strcmp(argv[1], "read-eintr")) {
        assert(__wrap_read(0, data, sizeof(data)) == -1 && errno == EINTR);
        assert(__wrap_read(0, data, sizeof(data)) == sizeof(data));
    } else if (!strcmp(argv[1], "write-eintr")) {
        assert(__wrap_write(1, data, sizeof(data)) == -1 && errno == EINTR);
        assert(__wrap_write(1, data, sizeof(data)) == sizeof(data));
    } else if (!strcmp(argv[1], "write-prefix-error")) {
        assert(__wrap_write(1, data, sizeof(data)) == 2);
        assert(__wrap_write(1, data, sizeof(data)) == -1 && errno == EIO);
    } else {
        assert(!strcmp(argv[1], "close-error"));
        assert(__wrap_close(3) == -1 && errno == EIO);
        assert(closes == 1);
    }
    assert(markers == 1);
    return 0;
}
