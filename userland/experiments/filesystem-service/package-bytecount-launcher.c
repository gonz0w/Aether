/* SPDX-License-Identifier: BSD-2-Clause */
#define _POSIX_C_SOURCE 200809L
#include "fd-libc.h"
#include "fd-exec.h"
#include <unistd.h>

_Noreturn void __real__exit(int);
int __wrap_main(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    if (aefd_shell_start() || aefd_shell_role() != 1 || aefd_shell_ready())
        __real__exit(143);
    pid_t child = fork();
    if (child == 0) {
        char *arguments[] = {"/pkg/bytecount", "--decimal", NULL};
        char *environment[] = {"LC_ALL=C", NULL};
        (void)execve(arguments[0], arguments, environment);
        __real__exit(126);
    }
    int status = -1;
    if (child < 10 || __aether_waitpid(child, &status, 0) != child || status != 0)
        __real__exit(1);
    __wrap__exit(0);
}
