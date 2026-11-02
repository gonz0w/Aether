/* SPDX-License-Identifier: BSD-2-Clause */
/* Selected ordinary app using the real libc descriptor entry points. */
#ifndef AMK_NATIVE_TTY_MODE_PROBE
#error "select the native TTY mode probe explicitly"
#endif
#include "../mktemp-directory/target.h"
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>
#ifdef AMK_NATIVE_APP_HOST
/* Only the host kernel/libc I/O boundary is substituted. The target uses the
 * unmodified pinned musl read/write/close and actual descriptor bindings. */
int aefd_test_open(const char *, int, ...);
int aefd_test_tcgetattr(int, struct termios *);
int aefd_test_tcsetattr(int, int, const struct termios *);
int aefd_test_isatty(int);
int aefd_test_fcntl(int, int, ...);
ssize_t amk_tty_test_read(int, void *, size_t);
ssize_t amk_tty_test_write(int, const void *, size_t);
int amk_tty_test_close(int);
#define open aefd_test_open
#define tcgetattr aefd_test_tcgetattr
#define tcsetattr aefd_test_tcsetattr
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
static int same_mode(const struct termios *a, const struct termios *b)
{
    return a->c_iflag == b->c_iflag && a->c_oflag == b->c_oflag &&
           a->c_cflag == b->c_cflag && a->c_lflag == b->c_lflag &&
           a->c_line == b->c_line && !memcmp(a->c_cc, b->c_cc, NCCS) &&
           a->__c_ispeed == b->__c_ispeed && a->__c_ospeed == b->__c_ospeed;
}
int amk_tty_mode_probe(int argc, char **argv)
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
    if (memtrap(0x26000, 0xf001, 0, 0, 0) != -EACCES ||
        memtrap(0x26001, 0xf001, 0, 0, 0) != -EACCES ||
        memtrap(0x26004, 0xf001, 0, 0, 0) != -EACCES)
        return 1;
    int opened = open("/dev/tty", O_RDWR | O_NOCTTY);
    if (opened != 3)
        return 1;
    int tty = fcntl(opened, F_DUPFD, 10);
    if (tty != 10 || close(opened) || fcntl(tty, F_SETFD, FD_CLOEXEC) ||
        fcntl(tty, F_GETFD) != FD_CLOEXEC || !isatty(tty) ||
        fcntl(tty, F_GETFL) != O_RDWR || close(0) || close(1))
        return 1;
    struct termios saved, current, changed;
    if (tcgetattr(tty, &saved) || saved.c_iflag)
        return 1;
    changed = saved;
    changed.c_iflag |= ICRNL;
    if (!send_bytes(tty, "TTY-MODE DRAIN\n", sizeof("TTY-MODE DRAIN\n") - 1) ||
        tcsetattr(tty, TCSADRAIN, &changed) || tcgetattr(tty, &current) ||
        !same_mode(&current, &changed) ||
        !send_bytes(tty, "TTY-MODE READY1\n", sizeof("TTY-MODE READY1\n") - 1))
        return 1;
    for (unsigned phase = 0; phase < 2; ++phase) {
        size_t at = 0;
        while (at < sizeof(input)) {
            ssize_t done = read(tty, input + at, sizeof(input) - at);
            if (done <= 0 || (size_t)done > sizeof(input) - at)
                return 1;
            for (size_t i = at; i < at + (size_t)done; ++i) {
                unsigned char expected = payload[i];
                if (!phase && expected == 0x0d)
                    expected = 0x0a;
                if (input[i] != expected)
                    return 1;
            }
            at += (size_t)done;
        }
        const char *marker = phase ? "TTY-MODE OUT2\n" : "TTY-MODE OUT1\n";
        if (!send_bytes(tty, marker, sizeof("TTY-MODE OUT1\n") - 1) ||
            !send_bytes(tty, input, sizeof(input)) || !send_bytes(tty, "\n", 1))
            return 1;
        if (!phase &&
            (tcsetattr(tty, TCSADRAIN, &saved) || tcgetattr(tty, &current) ||
             !same_mode(&current, &saved) ||
             !send_bytes(tty, "TTY-MODE READY2\n",
                         sizeof("TTY-MODE READY2\n") - 1)))
            return 1;
    }
    if (!send_bytes(2, "TTY-MODE ERR\n", sizeof("TTY-MODE ERR\n") - 1) ||
        close(2) ||
        !send_bytes(tty, "TTY-MODE PASS\n", sizeof("TTY-MODE PASS\n") - 1) ||
        close(tty))
        return 1;
    return 0;
}
