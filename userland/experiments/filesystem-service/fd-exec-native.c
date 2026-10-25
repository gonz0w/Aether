/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-exec.h"
#include <sys/auxv.h>
#include <unistd.h>
#include <errno.h>
_Noreturn void __real__exit(int);
int64_t aefd_shell_ready(void)
{
    return aefd_startup_ready(&aefd_shell_fork_context()->boot);
}
int execve(const char *path, char *const argv[], char *const envp[])
{
    struct aefd_fork *f = aefd_shell_fork_context();
    struct aefd_startup_auxv observed = {getauxval(0xa000), getauxval(0xa001),
                                         getauxval(0xa002)};
    int64_t result = aefd_exec(f, observed, path, argv, envp);
    if (f->phase == AEFD_FORK_FAILED)
        __real__exit(126);
    errno = result < 0 && result >= -4095 ? (int)-result : EIO;
    return -1;
}
