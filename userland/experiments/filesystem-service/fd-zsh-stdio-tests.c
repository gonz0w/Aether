/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only actual scoped musl units + existing descriptor context. Auxv,
 * signal/kernel calls, stream source, fdopen allocation and mode parsing are
 * explicit doubles. No host FILE ABI or native FILE/path authority is claimed.
 */
#define _POSIX_C_SOURCE 200809L
#include "fd-zsh-external.h"
#include "fd-libc.h"
#include "stdio_impl.h"
#include <assert.h>
#include <errno.h>
#include <limits.h>
#include <string.h>

FILE *aefd_test_fopen(const char *, const char *);
size_t aefd_test_stdio_read(FILE *, unsigned char *, size_t);
off_t aefd_test_stdio_seek(FILE *, off_t, int);
FILE *aefd_test_fdopen(int, const char *);
int aefd_test_fmodeflags(const char *);
void aefd_test_stdio_unmask(struct aefd_startup *);
void aefd_test_zsh_stdio(struct aefd_startup *, int);
static struct aefd_startup *boot;
static struct aefd_stream_reader original;
static unsigned calls, fdopens, fail_fdopen, armed, delivered;
static int64_t outcome;
static int complete = 1;
static size_t requested;
static unsigned char *published;
static FILE file;
static struct aefd_stream_result read_source(void *context, unsigned kind,
                                             unsigned selector,
                                             unsigned char *out, size_t n)
{
    assert(context == boot && kind == AEFD_BIND_TERMINAL && !selector &&
           boot->context.native.active && !boot->context.native.busy &&
           out == boot->context.workspace);
    ++calls;
    requested = n;
    unsigned char untouched = 0xa5;
    int saved = errno;
    assert(aether_zsh_read(0, &untouched, 1) == -1 && errno == EBUSY &&
           untouched == 0xa5);
    errno = saved;
    if (outcome > 0) {
        assert((uint64_t)outcome <= n && outcome <= 16);
        memcpy(out, "ABCDEFGHIJKLMNOP", (size_t)outcome);
    }
    return (struct aefd_stream_result){complete, outcome};
}
void aefd_test_stdio_unmask(struct aefd_startup *value)
{
    if (!armed)
        return;
    armed = 0;
    assert(value == boot && !boot->context.native.active &&
           !boot->context.native.busy && published &&
           !memcmp(published, "ABC", 3));
    ++delivered;
    /* A handler's transaction must survive the outer leave unchanged. */
    assert(aether_zsh_raw_fcntl(0, F_DUPFD, 10) == 10);
    assert(aether_zsh_raw_fcntl(10, F_GETFD, 0) == 0);
}
int aefd_test_fmodeflags(const char *mode)
{
    return (*mode == 'r' ? (strchr(mode, '+') ? O_RDWR : O_RDONLY)
                         : O_WRONLY | O_CREAT | O_TRUNC) |
           (strchr(mode, 'e') ? O_CLOEXEC : 0);
}
FILE *aefd_test_fdopen(int fd, const char *mode)
{
    ++fdopens;
    assert(strchr(mode, '+') && fd == 3);
    if (fail_fdopen) {
        errno = ENOMEM;
        return NULL;
    }
    memset(&file, 0, sizeof(file));
    file.fd = fd;
    return &file;
}
void aefd_test_zsh_stdio(struct aefd_startup *value, int unknown)
{
    boot = value;
    original = boot->context.session.adapters.reader;
    boot->context.session.adapters.reader =
        (struct aefd_stream_reader){boot, read_source};
    unsigned char a[8], b[8];
    memset(a, 0xa5, sizeof(a));
    memset(b, 0xa5, sizeof(b));
    struct iovec parts[2] = {{a, sizeof(a)}, {b, sizeof(b)}};
    outcome = 3;
    published = a;
    armed = 1;
    errno = ERANGE;
    assert(aether_zsh_vector_read(0, parts, 2) == 3 && errno == ERANGE &&
           calls == 1 && requested == 8 && delivered == 1 &&
           !memcmp(a, "ABC", 3) && a[3] == 0xa5 && b[0] == 0xa5);
    assert(aether_zsh_raw_fcntl(10, F_GETFD, 0) == 0);
    assert(aether_zsh_raw_close(10) == 0);
    unsigned before = calls;
    parts[1] = (struct iovec){NULL, 1};
    assert(aether_zsh_vector_read(0, parts, 2) == -1 && errno == EFAULT);
    parts[1] = (struct iovec){(void *)(UINTPTR_MAX - 1), 8};
    assert(aether_zsh_vector_read(0, parts, 2) == -1 && errno == EFAULT);
    parts[1] = (struct iovec){boot->context.workspace, 1};
    assert(aether_zsh_vector_read(0, parts, 2) == -1 && errno == EFAULT);
    parts[0] = (struct iovec){a, (size_t)SSIZE_MAX};
    parts[1] = (struct iovec){b, 1};
    assert(aether_zsh_vector_read(0, parts, 2) == -1 && errno == EINVAL);
    assert(aether_zsh_vector_read(0, NULL, 1) == -1 && errno == EFAULT);
    assert(aether_zsh_vector_read(0, parts, -1) == -1 && errno == EINVAL);
    assert(aether_zsh_vector_read(0, parts, 3) == -1 && errno == EINVAL);
    assert(calls == before);
    errno = ERANGE;
    assert(aether_zsh_vector_read(0, NULL, 0) == 0 && errno == ERANGE);
    parts[0] = (struct iovec){NULL, 0};
    parts[1] = (struct iovec){NULL, 0};
    assert(aether_zsh_vector_read(0, parts, 2) == 0 && calls == before);
    static unsigned char large[5000];
    parts[0] = (struct iovec){large, sizeof(large)};
    parts[1] = (struct iovec){b, sizeof(b)};
    assert(aether_zsh_vector_read(0, parts, 2) == 3 &&
           requested == AEFD_READ_MAX && calls == before + 1);
    parts[0] = (struct iovec){NULL, 0};
    parts[1] = (struct iovec){b, sizeof(b)};
    assert(aether_zsh_vector_read(0, parts, 2) == 3 && !memcmp(b, "ABC", 3));

    /* Actual upstream FILE read algorithm: short prefix, buffer fill branch,
     * known EOF/error, and no implicit close on zero-byte EOF. */
    unsigned char buffer[8];
    memset(buffer, 0xa5, sizeof(buffer));
    file = (FILE){.fd = 0, .buf = buffer, .buf_size = sizeof(buffer)};
    assert(aefd_test_stdio_read(&file, a, 4) == 3 && !file.flags &&
           !file.rpos && buffer[0] == 0xa5);
    assert(aefd_test_stdio_read(&file, a, 1) == 1 && a[0] == 'A' &&
           file.rpos == buffer + 1 && file.rend == buffer + 3);
    outcome = 0;
    file.flags = 0;
    assert(!aefd_test_stdio_read(&file, a, 4) && file.flags == F_EOF &&
           boot->context.client.live);
    outcome = -EIO;
    file.flags = 0;
    memset(a, 0xa5, sizeof(a));
    assert(!aefd_test_stdio_read(&file, a, 4) && file.flags == F_ERR &&
           errno == EIO && a[0] == 0xa5 && boot->context.client.live);
    errno = ERANGE;
    assert(aether_zsh_raw_fcntl(15, F_GETFD, 0) == -EBADF && errno == ERANGE);
    assert(aether_zsh_raw_close(15) == -EBADF && errno == ERANGE);
    assert(aefd_test_stdio_seek(&file, 0, SEEK_CUR) == -1 && errno == ESPIPE);
    assert(aether_zsh_seek(0, 0, 9) == -1 && errno == EINVAL);
    assert(!aefd_test_fopen("/home/.terminfo/v/vt100", "r") &&
           errno == EOPNOTSUPP && !fdopens);
    assert(!aefd_test_fopen("/dev/tty", "w") && errno == EOPNOTSUPP);
    assert(!aefd_test_fopen("/dev/tty", "x") && errno == EINVAL);
    errno = ERANGE;
    assert(aefd_test_fopen("/dev/tty", "r+e") == &file && errno == ERANGE &&
           file.fd == 3 && fdopens == 1 &&
           aether_zsh_raw_fcntl(3, F_GETFD, 0) == FD_CLOEXEC);
    assert(aether_zsh_raw_close(3) == 0);
    fail_fdopen = 1;
    assert(!aefd_test_fopen("/dev/tty", "r+") && errno == ENOMEM &&
           fdopens == 2 && boot->context.map.slots[3].kind == AEFD_BIND_EMPTY);
    boot->context.session.adapters.reader = original;
    if (unknown) {
        boot->context.session.adapters.reader =
            (struct aefd_stream_reader){boot, read_source};
        complete = 0;
        outcome = 3;
        memset(a, 0xa5, sizeof(a));
        before = calls;
        assert(aether_zsh_read(0, a, sizeof(a)) == -1 && errno == EIO &&
               a[0] == 0xa5 && calls == before + 1 &&
               !boot->context.client.live);
        assert(aether_zsh_read(0, a, sizeof(a)) == -1 && errno == EBADF &&
               calls == before + 1);
    }
}
