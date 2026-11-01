/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual shared C startup/context/libc bindings; only host I/O and mkdir/traps
 * are doubles. Target links the pinned SDK's unchanged read/write/close. */
#include "../mktemp-directory/target.h"
#include "../filesystem-service/fd-libc.h"
#include <errno.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
extern int amk_tty_duplex_probe(int, char **);
extern int aefd_test_open(const char *, int, ...);
extern int aefd_test_isatty(int);
extern int aefd_test_fcntl(int, int, ...);
static unsigned creates, traps;
char *amk_checked_mkdtemp(char *text)
{
    creates++;
    if (strcmp(text, "/home/t.XXXXXX"))
        return NULL;
    memcpy(text + 8, "ABCDEF", 6);
    return text;
}
long amk_tty_test_trap(unsigned long op, unsigned long cap, unsigned long a,
                       unsigned long b, unsigned long c)
{
    if ((op != 0x26000 && op != 0x26001) || cap != 0xf001 || a || b || c)
        return -EINVAL;
    traps++;
    return -EACCES;
}
static ssize_t checked_io(unsigned op, int fd, const void *pointer,
                          size_t count)
{
    int saved = errno;
    long result = __aether_io(op, (unsigned long)fd,
                              (unsigned long)(uintptr_t)pointer, count);
    if (result < 0) {
        errno = result >= -4095 ? (int)-result : EIO;
        return -1;
    }
    errno = saved;
    return result;
}
ssize_t amk_tty_test_read(int fd, void *pointer, size_t count)
{
    return checked_io(0, fd, pointer, count);
}
ssize_t amk_tty_test_write(int fd, const void *pointer, size_t count)
{
    return checked_io(1, fd, pointer, count);
}
int amk_tty_test_close(int fd) { return (int)checked_io(3, fd, NULL, 0); }
static int negatives(unsigned kind)
{
    struct aefd_context *c = &aefd_shell_external_startup()->context;
    if (aefd_shell_start() != -16)
        return 10; /* A second initializer cannot consume another greeting. */
    if (kind == 7) {
        if (creates || traps || c->state != 3 || c->client.live ||
            __aether_io(0, 0, 0, 0) != -EBADF ||
            __aether_io(1, 1, 0, 0) != -EBADF)
            return 21;
        for (int fd = 0; fd < 3; ++fd) {
            errno = 0;
            if (aefd_test_isatty(fd) || errno != EIO)
                return 22;
            errno = 0;
            if (aefd_test_fcntl(fd, F_GETFL) != -1 || errno != EIO)
                return 23;
        }
        return 0;
    }
    if (kind == 5 || kind == 6) {
        if (kind == 5)
            c->map.slots[0].kind = 255;
        else
            c->map.generation++;
        errno = 0;
        if (aefd_test_isatty(0) || errno != EIO || c->client.live)
            return 11;
        errno = 0;
        return aefd_test_fcntl(0, F_GETFL) == -1 && errno == EIO ? 0 : 12;
    }
    int state = c->state;
    c->state = 0; /* Explicit unadmitted-context double, restored before use. */
    errno = 0;
    int unadmitted = aefd_test_isatty(0) == 0 && errno == EIO;
    c->state = state;
    if (!unadmitted)
        return 13;
    struct aefd_bindings saved = c->map;
    for (unsigned i = 0; i < 3; ++i)
        c->map.slots[i].kind = AEFD_BIND_CONSOLE;
    errno = 0;
    if (aefd_test_isatty(0) || errno != ENOTTY ||
        aefd_test_fcntl(0, F_GETFL) != O_RDONLY)
        return 14;
    c->map.slots[15] = (struct aefd_binding){AEFD_BIND_FILE, 3, 0, 0};
    errno = 0;
    if (aefd_test_isatty(15) || errno != ENOTTY ||
        aefd_test_fcntl(15, F_GETFL) != O_RDONLY)
        return 15;
    /* These pipe source observations are explicit doubles; no data/close call
     * claims a native pipe was created. */
    c->map.slots[15] = (struct aefd_binding){AEFD_BIND_PIPE, 3, 0, 0};
    c->native.sources[3] = (struct aefd_native_source){0x79000101, 3, 1, 16};
    errno = 0;
    int pipe_ok = !aefd_test_isatty(15) && errno == ENOTTY &&
                  aefd_test_fcntl(15, F_GETFL) == O_RDONLY;
    c->native.sources[3] = (struct aefd_native_source){0};
    c->map = saved;
    if (!pipe_ok)
        return 16;
    for (unsigned i = 0; i < 3; ++i) {
        int access = i == 0 ? O_RDONLY : O_WRONLY;
        for (unsigned j = 0; j < 3; ++j) {
            int flags[] = {access | O_NONBLOCK, access | O_APPEND, O_RDWR};
            errno = 0;
            if (aefd_test_fcntl((int)i, F_SETFL, flags[j]) != -1 ||
                errno != EOPNOTSUPP || memcmp(&c->map, &saved, sizeof(saved)) ||
                aefd_test_fcntl((int)i, F_GETFL) != access)
                return 17;
        }
    }
    unsigned char raw[AEFD_BINDINGS_BYTES];
    struct aefd_bindings out;
    if (aefd_context_snapshot(c, raw, sizeof(raw), 0))
        return 18;
    for (unsigned i = 1; i <= 3; ++i) {
        raw[7] = (unsigned char)('0' + i);
        if (aefd_bindings_decode(raw, sizeof(raw), c->map.generation, &out))
            return 19;
    }
    raw[7] = '4';
    raw[64 + 3 * 4] = AEFD_BIND_CONSOLE;
    raw[65 + 3 * 4] = 0;
    if (aefd_bindings_decode(raw, sizeof(raw), c->map.generation, &out))
        return 20; /* One source cannot carry conflicting admitted types. */
    return 0;
}
static int acquire(int cloexec)
{
    return aefd_test_open("/dev/tty",
                          O_RDWR | O_NOCTTY | (cloexec ? O_CLOEXEC : 0));
}
static int duplex_cases(unsigned kind)
{
    struct aefd_context *c = &aefd_shell_external_startup()->context;
    if (!aefd_binding_valid((struct aefd_binding){5, 0, 0, 1}) ||
        aefd_binding_valid((struct aefd_binding){5, 0, 0, 0}) ||
        aefd_binding_valid((struct aefd_binding){5, 0, 0, 17}) ||
        aefd_binding_valid((struct aefd_binding){5, 1, 0, 1}) ||
        aefd_binding_valid((struct aefd_binding){4, 0, 0, 1}))
        return 30;
    if (kind == 25)
        return acquire(0) == 3 && !amk_tty_test_close(0) &&
                       !amk_tty_test_close(1)
                   ? 0
                   : 64;
    if (kind >= 21 && kind <= 23) {
        int fd = acquire(0);
        if (fd != 3 || amk_tty_test_close(0) || amk_tty_test_close(1))
            return 60;
        if (kind == 21)
            c->native.sources[1].rights = 1;
        if (kind == 22)
            c->native.sources[1].bound = 17;
        if (kind == 23)
            c->native.sources[1].reference ^= 1;
        return 0; /* The caller invokes the real finalizer directly. */
    }
    if (kind == 24) {
        if (c->state != 3 || c->client.live ||
            c->map.slots[3].kind != AEFD_BIND_DUPLEX_TERMINAL ||
            c->native.sources[0].reference != 0x7a000001 ||
            c->native.sources[2].reference != 0x7a020001 ||
            !c->session.receipt.unknown ||
            c->session.receipt.first_error != -5 ||
            c->session.receipt.attempted || c->session.receipt.removed ||
            c->session.receipt.remaining != 2)
            return 61;
        errno = 0;
        if (aefd_test_isatty(3) || errno != EIO)
            return 62;
        errno = 0;
        if (aefd_test_fcntl(3, F_GETFL) != -1 || errno != EIO)
            return 63;
        return 0;
    }
    if (kind >= 18 && kind <= 20) {
        int fd = acquire(0);
        if (fd != 3 || amk_tty_test_close(0) || amk_tty_test_close(1))
            return 58;
        if (kind == 18)
            c->native.sources[1].rights = 1;
        if (kind == 19)
            c->native.sources[1].bound = 17;
        if (kind == 20)
            c->native.sources[1].reference ^= 1;
        errno = 0;
        if (amk_tty_test_close(fd) != -1 || errno != EIO || c->client.live ||
            c->native.sources[0].reference != 0x7a000001 ||
            c->map.slots[fd].kind != AEFD_BIND_DUPLEX_TERMINAL)
            return 59;
        return 0;
    }
    if (kind == 10 || kind == 11) {
        int fd = acquire(0);
        if (fd != 3 || amk_tty_test_close(0) || amk_tty_test_close(1))
            return 31;
        struct aefd_binding saved = c->map.slots[fd];
        errno = 0;
        if (amk_tty_test_close(fd) != -1 || errno != EIO || c->client.live ||
            memcmp(&saved, &c->map.slots[fd], sizeof(saved)) ||
            (kind == 10 ? !c->native.sources[0].reference
                        : !!c->native.sources[0].reference) ||
            !c->native.sources[1].reference)
            return 32;
        errno = 0;
        if (aefd_test_isatty(fd) || errno != EIO)
            return 33;
        errno = 0;
        if (aefd_test_fcntl(fd, F_GETFL) != -1 || errno != EIO)
            return 34;
        errno = 0;
        if (acquire(0) != -1 || errno != EIO)
            return 35;
        return 0;
    }
    if (kind == 12 || kind == 13) {
        if (amk_tty_test_close((int)(kind - 12)))
            return 36;
        struct aefd_bindings saved = c->map;
        errno = 0;
        return acquire(0) == -1 && errno == ENXIO &&
                       !memcmp(&saved, &c->map, sizeof(saved))
                   ? 0
                   : 37;
    }
    if (kind == 14) {
        struct aefd_bindings saved = c->map;
        unsigned flags[] = {O_RDONLY, O_WRONLY, O_RDWR | O_NONBLOCK,
                            O_RDWR | O_APPEND, O_RDWR | O_CREAT};
        for (unsigned i = 0; i < sizeof(flags) / sizeof(flags[0]); ++i) {
            errno = 0;
            if (aefd_test_open("/dev/tty", (int)flags[i]) != -1 ||
                errno != EOPNOTSUPP || memcmp(&saved, &c->map, sizeof(saved)))
                return 38;
        }
        errno = 0;
        if (aefd_test_open(NULL, O_RDWR) != -1 || errno != EFAULT)
            return 39;
        for (unsigned i = 0; i < 2; ++i) {
            const char *path = i ? "/dev//tty" : "/dev/tty/";
            errno = 0;
            if (aefd_test_open(path, O_RDWR) != -1 || errno != EOPNOTSUPP)
                return 40;
        }
        c->native.sources[1].rights = 1;
        errno = 0;
        int denied = acquire(0) == -1 && errno == ENXIO;
        c->native.sources[1].rights = 2;
        if (!denied)
            return 41;
        c->native.sources[1].reference ^= 1;
        errno = 0;
        denied = acquire(0) == -1 && errno == ENXIO;
        c->native.sources[1].reference ^= 1;
        if (!denied)
            return 42;
        c->map.slots[0].kind = c->map.slots[1].kind = AEFD_BIND_CONSOLE;
        errno = 0;
        denied = acquire(0) == -1 && errno == ENXIO;
        c->map = saved;
        return denied ? 0 : 43;
    }
    int a = acquire(kind == 9);
    if (a != 3 || c->map.slots[a].reserved != 1 ||
        aefd_test_fcntl(a, F_GETFL) != O_RDWR || !aefd_test_isatty(a))
        return 44;
    if (kind == 15) {
        if (amk_tty_test_close(0) || amk_tty_test_close(1) ||
            amk_tty_test_close(2))
            return 45;
        for (unsigned i = 1; i < 16; ++i)
            if (acquire(0) < 0)
                return 46;
        unsigned ids = 0;
        for (unsigned fd = 0; fd < 16; ++fd)
            ids |= 1U << c->map.slots[fd].reserved;
        if (ids != 0x1fffe)
            return 47;
        struct aefd_bindings saved = c->map;
        errno = 0;
        if (acquire(0) != -1 || errno != EMFILE ||
            memcmp(&saved, &c->map, sizeof(saved)))
            return 48;
        errno = 0;
        if (aefd_test_fcntl(a, F_DUPFD, 0) != -1 || errno != EMFILE ||
            memcmp(&saved, &c->map, sizeof(saved)))
            return 49;
        int gap = -1;
        for (int fd = 0; fd < 16; ++fd)
            if (c->map.slots[fd].reserved == 8)
                gap = fd;
        if (gap < 0 || amk_tty_test_close(gap) || acquire(0) != gap ||
            c->map.slots[gap].reserved != 8)
            return 50;
        for (int fd = 0; fd < 16; ++fd)
            if (amk_tty_test_close(fd))
                return 51;
        return 0;
    }
    if (kind == 16) {
        int input = aefd_test_fcntl(0, F_DUPFD, 10), b = acquire(0);
        if (input != 10 || b != 4 || amk_tty_test_close(0) ||
            amk_tty_test_close(a) || amk_tty_test_close(1) ||
            amk_tty_test_close(input) || !c->native.sources[0].reference ||
            !c->native.sources[1].reference || amk_tty_test_close(b) ||
            amk_tty_test_close(2))
            return 52;
        return 0;
    }
    int alias = aefd_test_fcntl(a, F_DUPFD, 10), b = acquire(0);
    if (alias != 10 || b != 4 || c->map.slots[alias].reserved != 1 ||
        c->map.slots[b].reserved != 2 || aefd_test_fcntl(alias, F_GETFD) ||
        aefd_test_fcntl(a, F_GETFD) != (kind == 9 ? FD_CLOEXEC : 0))
        return 53;
    if (kind == 17) {
        if (amk_tty_test_close(a) || amk_tty_test_close(alias) ||
            amk_tty_test_close(b) || !c->native.sources[0].reference ||
            !c->native.sources[1].reference)
            return 54;
        a = acquire(0);
        if (a != 3 || c->map.slots[a].reserved != 1 || amk_tty_test_close(0) ||
            amk_tty_test_close(1) || amk_tty_test_close(a) ||
            amk_tty_test_close(2))
            return 55;
        return 0;
    }
    if (amk_tty_test_close(a) || amk_tty_test_close(0) ||
        amk_tty_test_close(1) || amk_tty_test_close(b) ||
        !c->native.sources[0].reference || !c->native.sources[1].reference ||
        aefd_test_fcntl(alias, F_GETFL) != O_RDWR ||
        amk_tty_test_close(alias) || c->native.sources[0].reference ||
        c->native.sources[1].reference)
        return 56;
    errno = 0;
    if (acquire(0) != -1 || errno != ENXIO || amk_tty_test_close(2))
        return 57;
    return 0;
}
int amk_test_tty_duplex_case(uint32_t kind)
{
    if (kind == 8) {
        creates = traps = 0;
        return 0;
    }
    if (kind >= 9)
        return duplex_cases(kind);
    if (kind >= 4)
        return negatives(kind);
    creates = traps = 0;
    char *argv[] = {"mktemp", "-d", "/home/t.XXXXXX", NULL};
    int status = amk_tty_duplex_probe(kind == 3 ? 2 : 3, argv);
    if (strcmp(argv[2], "/home/t.XXXXXX"))
        return 2;
    if (kind == 3)
        return status == 1 && !creates && !traps ? 0 : 3;
    if (creates != 1 || traps != 2)
        return 4;
    return status == (kind == 0 ? 0 : 1) ? 0 : 5;
}
