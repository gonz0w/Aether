/* SPDX-License-Identifier: BSD-2-Clause */
/* Selected ordinary app using the real libc descriptor entry points. */
#ifndef AMK_NATIVE_TTY_DESCRIPTOR_PROBE
#error "select the native TTY descriptor probe explicitly"
#endif
#include "../mktemp-directory/target.h"
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#ifdef AMK_NATIVE_APP_HOST
/* Only the host kernel/libc I/O boundary is substituted. The target uses the
 * unmodified pinned musl read/write/close and actual descriptor bindings. */
int aefd_test_isatty(int);
int aefd_test_fcntl(int, int, ...);
ssize_t amk_tty_test_read(int, void *, size_t);
ssize_t amk_tty_test_write(int, const void *, size_t);
int amk_tty_test_close(int);
#define isatty aefd_test_isatty
#define fcntl aefd_test_fcntl
#define read amk_tty_test_read
#define write amk_tty_test_write
#define close amk_tty_test_close
extern long amk_tty_test_trap(unsigned long, unsigned long, unsigned long,
                              unsigned long, unsigned long);
#define memtrap amk_tty_test_trap
#else
#include "../../../user/native-memory/adapter.h"
#endif
static const unsigned char payload[16] = {0x00, 0x41, 0x1b, 0x42, 0x0d, 0x43,
                                          0x0a, 0x44, 0x7f, 0x45, 0x01, 0x46,
                                          0x02, 0x47, 0x80, 0xff};
static int send_bytes(int fd, const void *source, size_t count)
{
    const unsigned char *bytes = source;
    size_t at = 0;
    while (at < count) {
        ssize_t done = write(fd, bytes + at, count - at);
        if (done <= 0 || (size_t)done > count - at)
            return 0;
        at += (size_t)done;
    }
    return 1;
}
static int terminal(int fd, int access)
{
    errno = EALREADY;
    if (isatty(fd) != 1 || errno != EALREADY || fcntl(fd, F_GETFL) != access ||
        errno != EALREADY || fcntl(fd, F_SETFL, access) || errno != EALREADY ||
        fcntl(fd, F_SETFL, 0) || errno != EALREADY)
        return 0;
    errno = 0;
    if (fcntl(fd, F_SETFL, access | O_NONBLOCK) != -1 || errno != EOPNOTSUPP ||
        fcntl(fd, F_GETFL) != access)
        return 0;
    return 1;
}
static int closed(int fd)
{
    errno = 0;
    if (isatty(fd) || errno != EBADF)
        return 0;
    errno = 0;
    return fcntl(fd, F_GETFL) == -1 && errno == EBADF;
}
int amk_tty_descriptor_probe(int argc, char **argv)
{
    char path[32];
    unsigned char input[16];
    if (argc != 3 || !argv || !argv[0] || !argv[1] || !argv[2] || argv[3] ||
        strcmp(argv[0], "mktemp") || strcmp(argv[1], "-d") ||
        strcmp(argv[2], "/home/t.XXXXXX"))
        return 1;
    memcpy(path, argv[2], sizeof("/home/t.XXXXXX"));
    if (!amk_checked_mkdtemp(path))
        return 1;
    if (!terminal(0, O_RDONLY) || !terminal(1, O_WRONLY) ||
        !terminal(2, O_WRONLY) || !closed(15) || !closed(-1))
        return 1;
    int in = fcntl(0, F_DUPFD_CLOEXEC, 10);
    int out = fcntl(1, F_DUPFD, 11);
    if (in != 10 || out != 11 || !terminal(in, O_RDONLY) ||
        !terminal(out, O_WRONLY) || fcntl(in, F_GETFD) != FD_CLOEXEC ||
        fcntl(0, F_GETFD) || fcntl(out, F_GETFD) || fcntl(in, F_SETFD, 0) ||
        fcntl(in, F_GETFD))
        return 1;
    errno = 0;
    if (read(out, input, 1) != -1 || errno != EBADF)
        return 1;
    errno = 0;
    if (write(in, payload, 1) != -1 || errno != EBADF ||
        read(in, input, 0) != 0 || write(out, payload, 0) != 0 ||
        memtrap(0x26000, 0xf001, 0, 0, 0) != -EACCES ||
        memtrap(0x26001, 0xf001, 0, 0, 0) != -EACCES || close(0) || close(1) ||
        !closed(0) || !closed(1) || !terminal(in, O_RDONLY) ||
        !terminal(out, O_WRONLY) ||
        !send_bytes(out, "TTY-BYTE READY\n", sizeof("TTY-BYTE READY\n") - 1))
        return 1;
    size_t at = 0;
    while (at < sizeof(input)) {
        ssize_t done = read(in, input + at, sizeof(input) - at);
        if (done <= 0 || (size_t)done > sizeof(input) - at ||
            memcmp(input + at, payload + at, (size_t)done))
            return 1;
        at += (size_t)done;
    }
    if (close(in) || !closed(in) ||
        !send_bytes(out, "TTY-BYTE OUT\n", sizeof("TTY-BYTE OUT\n") - 1) ||
        !send_bytes(out, input, sizeof(input)) || !send_bytes(out, "\n", 1) ||
        !send_bytes(2, "TTY-BYTE ERR\n", sizeof("TTY-BYTE ERR\n") - 1) ||
        close(2) || !closed(2) ||
        !send_bytes(out, "TTY-BYTE PASS\n", sizeof("TTY-BYTE PASS\n") - 1) ||
        close(out) || !closed(out))
        return 1;
    return 0;
}
