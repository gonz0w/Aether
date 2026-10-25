/* SPDX-License-Identifier: BSD-2-Clause */
/* Bounded real dash driver; private fork/exec/wait adapters stay in the caller.
 */
#include <stdlib.h>
extern char **environ;
extern int __real_main(int, char **);
_Noreturn void __real__exit(int);
#ifdef FORK_CONSOLE
static pid_t shell_parent_pid;
#endif
_Noreturn void __wrap__exit(int status)
{
    /* Only these completed application paths own a usable transport. */
    int cleanup = status == 72 || status == 73;
#ifdef FORK_SHELL_ARGV
    cleanup = startup_ready && !poisoned;
#endif
#if defined(FORK_CONSOLE) && !defined(FORK_CONSOLE_OLD_CLEANUP)
    if (shell_parent_pid && getpid() == shell_parent_pid)
        cleanup = startup_ready && !poisoned;
#endif
    if (cleanup)
        for (int fd = 0; fd < 16; ++fd)
            if (startup_fds[fd].present && close(fd))
                __real__exit(226);
    __real__exit(status);
}
#ifdef FORK_SHELL_NULL_WAIT
#include "suspend-check.h"
#endif
int main(void)
{
    if (cookie != 23 || private_value != 41 || !startup_begin() ||
        fcntl(0, F_DUPFD_CLOEXEC, 10) != 10)
        return 224;
#ifdef FORK_SHELL_FILES
    if (!scratch_accept())
        return 224;
#endif
#ifdef FORK_SHELL_NULL_WAIT
    if (!suspend_check())
        memtrap(0x100e7, 233, 0, 0, 0);
#endif
#ifdef FORK_SHELL_SKIP
    __real__exit(72);
#endif
#ifdef FORK_SHELL_ARGV
    char *environment[] = {"PWD=/work", "WITNESS=value", "LC_ALL=C",
                           "PATH=/nonexistent", NULL};
#else
    char *environment[] = {"PWD=/work", "LC_ALL=C", "PATH=/", NULL};
#endif
#ifdef FORK_CONSOLE
    shell_parent_pid = getpid();
    if (memtrap(0x26000, 0xf001, 0, 0, 0) != -13 ||
        write(1, "SHELL READY\n", 12) != 12)
        return 224;
    char *arguments[] = {"sh", "-i", "+m", NULL};
#else
    char *arguments[] = {"sh", "-c",
#ifdef FORK_SHELL_FILES
                         AETHER_FILE_SCRIPT,
#elif defined(FORK_SHELL_FAILED_EXEC)
                         AETHER_FAILED_SCRIPT,
#elif defined(FORK_SHELL_NULL_WAIT)
                         AETHER_WAIT_SCRIPT,
#elif defined(FORK_SHELL_NULL)
                         "(exec /inputs/helper status) </dev/null; s=$?; [ "
#ifdef FORK_SHELL_NULL_FAULT
                         "\"$s\" -eq 132 ] || exit 20; printf \"null ok\\n\"",
#else
                         "\"$s\" -eq 7 ] || exit 20; printf \"null ok\\n\"",
#endif
#elif defined(FORK_SHELL_CLOSED)
                         "/inputs/helper closed\ns=$?\n[ \"$s\" -eq 0 ] || "
                         "exit 22\nprintf \"closed ok\\n\"\n",
#elif defined(FORK_SHELL_ARGV)
                         "WITNESS=value /inputs/helper argv \"a b\" \"*\"\n",
#elif defined(FORK_SHELL_COMMAND)
                         "/next; exit $?",
#else
                         "(exec /next); exit $?",
#endif
                         NULL};
#endif
    environ = environment;
    __wrap__exit(__real_main(3, arguments));
}
