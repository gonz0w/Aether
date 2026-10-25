/* SPDX-License-Identifier: BSD-2-Clause */
/* Test-only exit after actual command output; owner releases abandoned aliases.
 */
#include <unistd.h>
int __real_close(int fd);
int __wrap_close(int fd);
int __wrap_close(int fd)
{
    if (fd == STDIN_FILENO) {
#ifdef MAPPED_CHILD_FAULT
        __builtin_trap();
#else
        _exit(MAPPED_CHILD_STATUS);
#endif
    }
    return __real_close(fd);
}
