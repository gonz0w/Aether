/* SPDX-License-Identifier: BSD-2-Clause */
/* One selected ordinary-app callback; real startup/finalization stay in the
 * mktemp native entry. No libc terminal mode or direct console authority. */
#ifndef AMK_NATIVE_TTY_BYTE_PROBE
#error "select the native TTY byte probe explicitly"
#endif
#include "../mktemp-directory/target.h"
#include <errno.h>
#include <stdint.h>
#include <string.h>
#ifdef AMK_NATIVE_APP_HOST
extern long amk_tty_test_trap(unsigned long, unsigned long, unsigned long,
                              unsigned long, unsigned long);
#define memtrap amk_tty_test_trap
#else
#include "../../../user/native-memory/adapter.h"
#endif
extern long __aether_io(unsigned long, unsigned long, unsigned long,
                        unsigned long);
static const unsigned char payload[16] = {0x00, 0x41, 0x1b, 0x42, 0x0d, 0x43,
                                          0x0a, 0x44, 0x7f, 0x45, 0x01, 0x46,
                                          0x02, 0x47, 0x80, 0xff};
static int send_bytes(unsigned fd, const void *source, size_t count)
{
    const unsigned char *bytes = source;
    size_t at = 0;
    while (at < count) {
        long done = __aether_io(1, fd, (uintptr_t)(bytes + at), count - at);
        if (done <= 0 || (unsigned long)done > count - at)
            return 0;
        at += (size_t)done;
    }
    return 1;
}
int amk_tty_byte_probe(int argc, char **argv)
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
    if (__aether_io(0, 1, (uintptr_t)input, 1) != -EBADF ||
        __aether_io(1, 0, (uintptr_t)payload, 1) != -EBADF ||
        __aether_io(0, 0, 0, 0) != 0 || __aether_io(1, 1, 0, 0) != 0 ||
        __aether_io(1, 2, 0, 0) != 0 ||
        memtrap(0x26000, 0xf001, 0, 0, 0) != -EACCES ||
        memtrap(0x26001, 0xf001, 0, 0, 0) != -EACCES)
        return 1;
    if (!send_bytes(1, "TTY-BYTE READY\n", sizeof("TTY-BYTE READY\n") - 1))
        return 1;
    size_t at = 0;
    while (at < sizeof(input)) {
        long done =
            __aether_io(0, 0, (uintptr_t)(input + at), sizeof(input) - at);
        if (done <= 0 || (unsigned long)done > sizeof(input) - at)
            return 1;
        if (memcmp(input + at, payload + at, (size_t)done))
            return 1;
        at += (size_t)done;
    }
    if (__aether_io(3, 0, 0, 0) != 0 ||
        __aether_io(0, 0, (uintptr_t)input, 1) != -EBADF ||
        !send_bytes(1, "TTY-BYTE OUT\n", sizeof("TTY-BYTE OUT\n") - 1) ||
        !send_bytes(1, input, sizeof(input)) || !send_bytes(1, "\n", 1) ||
        !send_bytes(2, "TTY-BYTE ERR\n", sizeof("TTY-BYTE ERR\n") - 1) ||
        __aether_io(3, 2, 0, 0) != 0 ||
        __aether_io(1, 2, (uintptr_t)payload, 1) != -EBADF ||
        !send_bytes(1, "TTY-BYTE PASS\n", sizeof("TTY-BYTE PASS\n") - 1) ||
        __aether_io(3, 1, 0, 0) != 0 ||
        __aether_io(1, 1, (uintptr_t)payload, 1) != -EBADF)
        return 1;
    return 0;
}
