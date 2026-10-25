/* SPDX-License-Identifier: BSD-2-Clause */
#include <assert.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
int aefd_root_read_probe(int, char **);
int aefd_probe_open(const char *, int, ...);
ssize_t aefd_probe_read(int, void *, size_t);
off_t aefd_probe_seek(int, off_t, int);
int aefd_probe_close(int);
ssize_t aefd_probe_write(int, const void *, size_t);
static unsigned mode, phase, closes;
int aefd_probe_open(const char *name, int flags, ...)
{
    assert(!phase++ && !strcmp(name, "/zstd") &&
           flags == (O_RDONLY | O_CLOEXEC));
    return mode == 1 ? -1 : 3;
}
ssize_t aefd_probe_read(int fd, void *out, size_t count)
{
    assert(fd == 3 && out &&
           ((phase == 1 && count == 16) || (phase == 3 && count == 16) ||
            (phase == 4 && count == 1)));
    unsigned step = phase++;
    memset(out, 0x55, count);
    if (step == 1)
        return mode == 2 ? -1 : mode == 3 ? 15 : 16;
    return (mode == 5 && step == 3) || (mode == 6 && step == 4) ? 1 : 0;
}
off_t aefd_probe_seek(int fd, off_t offset, int whence)
{
    assert(fd == 3 && phase++ == 2 && !offset && whence == SEEK_END);
    return mode == 4 ? -1 : 780248;
}
int aefd_probe_close(int fd)
{
    assert(fd == 3 && !closes++ && phase >= 2 && phase <= 5);
    return mode == 7 ? -1 : 0;
}
ssize_t aefd_probe_write(int fd, const void *bytes, size_t count)
{
    assert(fd == 1 && phase == 5 && closes == 1 && count == 13 &&
           !memcmp(bytes, "AF07-READ:ok\n", count));
    return mode == 8 ? 12 : 13;
}
int main(void)
{
    static const int expected[] = {7, 81, 82, 82, 83, 84, 84, 85, 86};
    assert(aefd_root_read_probe(1, NULL) == 80 && !phase && !closes);
    for (mode = 0; mode < sizeof expected / sizeof *expected; ++mode) {
        phase = closes = 0;
        assert(aefd_root_read_probe(2, NULL) == expected[mode]);
        assert(closes == (mode != 1));
    }
    puts("10 fixed root-read probe outcomes pass");
    return 0;
}
