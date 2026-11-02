/* SPDX-License-Identifier: BSD-2-Clause */
/* Execute selected real musl fopen/read/seek algorithms against the same actual
 * C context and fake Owner. fdopen allocation alone is a host seam. */
#define _POSIX_C_SOURCE 200809L
#include "fd-zsh-external.h"
#include "stdio_impl.h"
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
FILE *aefd_test_fopen(const char *, const char *);
size_t aefd_test_stdio_read(FILE *, unsigned char *, size_t);
off_t aefd_test_stdio_seek(FILE *, off_t, int);
FILE *aefd_test_fdopen(int, const char *);
int aefd_test_fmodeflags(const char *);
void aefd_test_filesystem_direct(void);
void aefd_test_filesystem_stdio(void);
static FILE stream;
static unsigned char buffer[8];
FILE *aefd_test_fdopen(int fd, const char *mode)
{
    assert(fd == 3 && !strcmp(mode, "r"));
    memset(&stream, 0, sizeof(stream));
    stream.fd = fd;
    stream.buf = buffer;
    stream.buf_size = sizeof(buffer);
    return &stream;
}
int aefd_test_fmodeflags(const char *mode)
{
    assert(!strcmp(mode, "r"));
    return O_RDONLY;
}
void aefd_test_filesystem_stdio(void)
{
    aefd_test_filesystem_direct();
    errno = ERANGE;
    FILE *f = aefd_test_fopen("/home/.terminfo/./v/vt100", "r");
    assert(f == &stream && errno == ERANGE);
    unsigned char out[8] = {0};
    assert(aefd_test_stdio_read(f, out, 5) == 4 && !memcmp(out, "TERM", 4) &&
           !(f->flags & F_EOF) && errno == ERANGE);
    /* A real zero-byte EOF sets FILE EOF without closing its description. */
    assert(aefd_test_stdio_read(f, out, 5) == 0 && (f->flags & F_EOF) &&
           errno == ERANGE);
    assert(aefd_test_stdio_seek(f, 0, SEEK_SET) == 0 && errno == ERANGE);
    assert(aether_zsh_raw_close(f->fd) == 0 && errno == ERANGE);
}
