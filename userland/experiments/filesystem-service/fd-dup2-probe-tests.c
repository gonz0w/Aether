/* SPDX-License-Identifier: BSD-2-Clause */
#include <assert.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
int aefd_root_read_probe(int, char **);
int aefd_probe_open(const char *, int, ...);
int aefd_probe_dup2(int, int);
int aefd_probe_fcntl(int, int, ...);
ssize_t aefd_probe_read(int, void *, size_t);
off_t aefd_probe_seek(int, off_t, int);
int aefd_probe_close(int);
ssize_t aefd_probe_write(int, const void *, size_t);
static unsigned mode, opened, flags, dups, io_phase, closed;
static int alias10, alias0;
int aefd_probe_open(const char *name, int flag, ...)
{
    assert(!opened++ && !strcmp(name, "/zstd") &&
           flag == (O_RDONLY | O_CLOEXEC));
    return mode == 1 ? -1 : 3;
}
int aefd_probe_dup2(int from, int to)
{
    ++dups;
    if (dups == 1) {
        assert(from == 3 && to == 3);
        return mode == 10 ? -1 : to;
    }
    if (dups == 2) {
        assert(from == 3 && to == 10);
        if (mode == 12)
            return -1;
        alias10 = 1;
    } else if (dups == 3) {
        assert(from == 10 && to == 3);
        if (mode == 13)
            return -1;
    } else {
        assert(dups == 4 && from == 3 && to == 0);
        if (mode == 15)
            return -1;
        alias0 = 1;
    }
    return to;
}
int aefd_probe_fcntl(int fd, int command, ...)
{
    assert(fd == 3 && command == F_GETFD);
    ++flags;
    if (flags == 1)
        return mode == 9 ? 0 : FD_CLOEXEC;
    if (flags == 2)
        return mode == 11 ? 0 : FD_CLOEXEC;
    assert(flags == 3);
    return mode == 14 ? FD_CLOEXEC : 0;
}
ssize_t aefd_probe_read(int fd, void *out, size_t count)
{
    assert(out && ((io_phase == 0 && fd == 0 && count == 16) ||
                   (io_phase == 2 && fd == 10 && count == 16) ||
                   (io_phase == 3 && fd == 3 && count == 1)));
    memset(out, 0x55, count);
    unsigned step = io_phase++;
    if (!step)
        return mode == 2 ? -1 : mode == 3 ? 15 : 16;
    return (mode == 5 && step == 2) || (mode == 6 && step == 3) ? 1 : 0;
}
off_t aefd_probe_seek(int fd, off_t offset, int whence)
{
    assert(fd == 3 && io_phase++ == 1 && !offset && whence == SEEK_END);
    return mode == 4 ? -1 : 780248;
}
int aefd_probe_close(int fd)
{
    unsigned bit = fd == 10 ? 1U : fd == 0 ? 2U : 4U;
    assert(fd == 10 || fd == 0 || fd == 3);
    assert(!(closed & bit));
    if (fd == 10)
        assert(alias10);
    if (fd == 0)
        assert(alias0);
    closed |= bit;
    return (mode == 7 && fd == 3) || (mode == 16 && fd == 10) ||
                   (mode == 17 && fd == 0)
               ? -1
               : 0;
}
ssize_t aefd_probe_write(int fd, const void *bytes, size_t count)
{
    assert(fd == 1 && io_phase == 4 && closed == 7 && count == 13 &&
           !memcmp(bytes, "AF07-READ:ok\n", count));
    return mode == 8 ? 12 : 13;
}
int main(void)
{
    static const int expected[] = {7,  81, 82, 82, 83, 84, 84, 85, 86,
                                   87, 87, 87, 88, 89, 87, 90, 85, 85};
    assert(aefd_root_read_probe(1, NULL) == 80 && !opened);
    for (mode = 0; mode < sizeof expected / sizeof *expected; ++mode) {
        opened = flags = dups = io_phase = closed = 0;
        alias10 = alias0 = 0;
        assert(aefd_root_read_probe(2, NULL) == expected[mode]);
        assert(
            closed ==
            (mode == 1 ? 0U : 4U | (alias10 ? 1U : 0U) | (alias0 ? 2U : 0U)));
    }
    puts("19 fixed dup2/read probe outcomes pass");
    return 0;
}
