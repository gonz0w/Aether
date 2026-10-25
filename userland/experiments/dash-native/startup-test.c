/* SPDX-License-Identifier: BSD-2-Clause */
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdarg.h>
#include <stdlib.h>
#include <unistd.h>

static int fault;
static int allocated = -1;
static pid_t test_getpid(void) { return fault == 1 ? -1 : getpid(); }
static int test_sigaction(int signal, const struct sigaction *action,
                          struct sigaction *old)
{
    if (fault == 2) {
        errno = ENOSYS;
        return -1;
    }
    if (fault == 3 && action)
        return 0;
    return sigaction(signal, action, old);
}
static int test_sigprocmask(int how, const sigset_t *set, sigset_t *old)
{
    if (fault == 4 && set)
        return 0;
    return sigprocmask(how, set, old);
}
static int test_fcntl(int fd, int cmd, ...)
{
    if (cmd == F_DUPFD_CLOEXEC) {
        va_list args;
        va_start(args, cmd);
        int minimum = va_arg(args, int);
        va_end(args);
        allocated = fcntl(fd, fault == 5 ? F_DUPFD : cmd, minimum);
        return allocated;
    }
    return fcntl(fd, cmd);
}
#define DASH_STARTUP_TEST
#define getpid test_getpid
#define sigprocmask test_sigprocmask
#define fcntl test_fcntl
/* Function-like macro preserves struct sigaction's tag. */
#define sigaction(...) test_sigaction(__VA_ARGS__)
#include "startup.c"
#undef getpid
#undef sigaction
#undef sigprocmask
#undef fcntl

int main(int argc, char **argv)
{
    if (argc != 2 || argv[1][0] < '0' || argv[1][0] > '5' || argv[1][1])
        return 64;
    fault = argv[1][0] - '0';
    struct sigaction before, after;
    sigset_t mask_before, mask_after;
    if (sigaction(SIGUSR1, NULL, &before) != 0 ||
        sigprocmask(SIG_BLOCK, NULL, &mask_before) != 0)
        return 80;
    int result = dash_startup_probe();
    if (sigaction(SIGUSR1, NULL, &after) != 0 ||
        sigprocmask(SIG_BLOCK, NULL, &mask_after) != 0 ||
        before.sa_handler != after.sa_handler ||
        sigismember(&mask_before, SIGUSR1) != sigismember(&mask_after, SIGUSR1))
        return 81;
    if (allocated >= 0) {
        errno = 0;
        if (fcntl(allocated, F_GETFD) != -1 || errno != EBADF)
            return 82;
    }
    return result;
}
