/* SPDX-License-Identifier: BSD-2-Clause */
/* Link-only test injection: bytecount has produced output but not closed
 * aliases. */
#include <unistd.h>
int __real_close(int fd);
int __wrap_close(int fd);
int __wrap_close(int fd)
{
    if (fd == STDIN_FILENO) {
#ifdef TERMINAL_FAULT
        __builtin_trap();
#else
        _exit(134);
#endif
    }
    return __real_close(fd);
}
