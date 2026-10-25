/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual dash consumer of the bounded pipe/fork/wait producer. */
#include <stdlib.h>
extern char **environ;
extern int __real_main(int, char **);
_Noreturn void __real__exit(int);
#ifdef FORK_DASH_SIGNAL
/* Private self-only facade; PID lookup conveys no cross-process authority. */
int kill(pid_t pid, int sig)
{
    if (!startup_ready)
        return startup_error(EAGAIN);
    if (sig < 0 || sig > 64)
        return startup_error(EINVAL);
    if (pid <= 0)
        return startup_error(ENOTSUP);
#ifndef FORK_DASH_SIGNAL_SCOPE
    if (pid != getpid())
        return startup_error(EPERM);
#endif
    if (sig == 0)
        return 0;
    if (sig != SIGUSR1)
        return startup_error(ENOTSUP);
#ifdef FORK_DASH_SIGNAL_NO_POST
    return 0;
#else
    long result = memtrap(0x29002, SIGUSR1, 0, 0, 0);
    return result < 0 ? startup_error((int)-result) : (int)result;
#endif
}
#endif
int pipe(int pair[2]) { return native_pipe_pair(pair); }
int execve(const char *path, char *const argv[], char *const envp[])
{
#ifdef FORK_DASH_PIPE_EXEC
    if (strcmp(path,
#ifdef FORK_DASH_PIPE_CONSUMER
               "/inputs/helper"
#else
               "/next"
#endif
               ))
        return startup_error(ENOENT);
    if (fcntl(1, F_DUPFD_CLOEXEC, 11) != 11)
        __real__exit(227);
    long denied = __aether_execve_stage("/denied", argv, envp);
    if (denied != -EACCES || fcntl(10, F_GETFD) != FD_CLOEXEC ||
        fcntl(11, F_GETFD) != FD_CLOEXEC || fcntl(1, F_GETFD) != 0)
        __real__exit(227);
    long result = __aether_execve_stage(path, argv, envp);
    return startup_error(result < 0 ? (int)-result : EIO);
#else
    (void)path;
    (void)argv;
    (void)envp;
    return startup_error(ENOTSUP);
#endif
}
_Noreturn void __wrap__exit(int status)
{
#ifdef FORK_DASH_PIPE_REPEAT
    /* Unknown copy readiness must not issue descriptor traffic. */
    if (status == 80)
        __real__exit(status);
#endif
    if (startup_ready && !poisoned)
        for (int fd = 0; fd < 16; ++fd)
            if (startup_fds[fd].present && close(fd))
                __real__exit(226);
    __real__exit(status);
}
int main(void)
{
    if (cookie != 23 || private_value != 41 || !startup_begin() ||
        !pipe_grant() || fcntl(0, F_DUPFD_CLOEXEC, 10) != 10)
        return 224;
#if defined(FORK_DASH_SIGNAL) || defined(FORK_DASH_PIPE_CONSUMER)
    char *environment[] = {"PWD=/work", "WITNESS=value", "LC_ALL=C",
                           "PATH=/nonexistent", NULL};
#else
    char *environment[] = {"PWD=/work", "LC_ALL=C", "PATH=/", NULL};
#endif
    char *arguments[] = {
        "sh", "-c",
        "value=$(echo pipe); result=$?; echo \"$value\"; exit \"$result\"",
        NULL};
#ifdef FORK_DASH_PIPE_EXEC
    arguments[2] =
        "value=$(/next); result=$?; echo \"$value\"; exit \"$result\"";
#endif
#ifdef FORK_DASH_PIPE_REPEAT
    arguments[2] =
        memtrap(0x20005, 0, 0, 0, 0) == 1
            ? "a=$(echo pipe); b=$(echo pipe); echo \"$a\"; echo \"$b\""
            : "echo clean";
#endif
#ifdef FORK_DASH_PIPE_SERIAL
    arguments[1] = "-i";
    arguments[2] = "+m";
    if (memtrap(0x26000, 0xf001, 0, 0, 0) != -13 ||
        write(1, "SHELL READY\n", 12) != 12)
        return 224;
#endif
#ifdef FORK_DASH_SIGNAL
    pid_t self = getpid();
    if (kill(self + 4, SIGUSR1) != -1 || errno != EPERM ||
        kill(0, SIGUSR1) != -1 || errno != ENOTSUP || kill(-1, SIGUSR1) != -1 ||
        errno != ENOTSUP || kill(self, 65) != -1 || errno != EINVAL ||
        kill(self, SIGUSR2) != -1 || errno != ENOTSUP || kill(self, 0))
        __real__exit(228);
    arguments[2] = "[ \"$(kill -l 10)\" = USR1 ] || exit 26\n"
                   "trap 'printf \"signal ok\\n\"' USR1\n"
                   "kill -USR1 $$\n";
#endif
#ifdef FORK_DASH_PIPE_CONSUMER
    arguments[2] = AETHER_SUBSTITUTION_SCRIPT;
#endif
    environ = environment;
    __wrap__exit(__real_main(3, arguments));
}
