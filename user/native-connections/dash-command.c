/* SPDX-License-Identifier: BSD-2-Clause */
#define CAT_ROLES
#define SHELL_STARTUP
#ifdef FORK_SHELL_FILES
#ifndef FORK_SHELL_ARGV
#define FORK_SHELL_ARGV
#endif
#define SCRATCH_CLIENT
#endif
#include "../native-command/transport.h"
#ifdef FORK_SHELL_FILES
#include "scratch-client.h"
#include "scratch-restore.h"
#endif
#ifdef FORK_NULL
#include "null-client.h"
#include "null-check.h"
#endif
#include <stdlib.h>
extern char **environ;
static _Thread_local volatile unsigned cookie = 71;
int main(int argc, char **argv)
{
#ifdef FORK_SHELL_ARGV
    if (cookie != 71 || argc < 1 || strcmp(argv[0], "/inputs/helper") ||
        !startup_begin())
        return 224;
#else
    if (argc != 1 || strcmp(argv[0], "/next") || cookie != 71 ||
        !getenv("PWD") || strcmp(getenv("PWD"), "/work") || !getenv("LC_ALL") ||
        strcmp(getenv("LC_ALL"), "C") || !getenv("PATH") ||
        strcmp(getenv("PATH"), "/") || !startup_begin())
        return 224;
#endif
#ifdef FORK_SHELL_FILES
    unsigned char table[64] = {0}, saved[32] = {0};
    unsigned char descriptions[32] = {0};
    if (!move(table, sizeof table, 0) || !move(saved, sizeof saved, 0) ||
        !scratch_accept() || !move(descriptions, sizeof descriptions, 0) ||
        !scratch_restore(table, descriptions))
        return 224;
#else
    unsigned char table[64] = {0}, expected[64] = {0}, saved[32] = {0};
    for (unsigned i = 0; i < 3; ++i) {
        expected[i * 4] = i;
        expected[i * 4 + 2] = 1;
    }
#ifdef FORK_NULL
    expected[0] = 3;
#endif
    if (!move(table, sizeof table, 0) || !move(saved, sizeof saved, 0) ||
        memcmp(table, expected, sizeof table))
        return 224;
    memset(startup_fds, 0, sizeof startup_fds);
    memset(startup_users, 0, sizeof startup_users);
    for (unsigned i = 0; i < 3; ++i) {
        unsigned binding = expected[i * 4];
        startup_fds[i] = (struct startup_fd){binding, 0, 1};
        startup_users[binding] = 1;
    }
#endif
#ifdef FORK_NULL
    live[0] = 0;
    if (!null_accept(1))
        return 224;
#endif
    uint64_t previous = 0, current = 0;
    if (memcmp(saved, "AEEMSK01", 8))
        return 224;
    for (unsigned i = 16; i < 32; ++i)
        if (saved[i])
            return 224;
    memcpy(&previous, saved + 8, 8);
    if (previous || memtrap(0x1000e, 0, 0, (uintptr_t)&current, 8) ||
        current != (UINT64_MAX & ~((UINT64_C(1) << 8) | (UINT64_C(1) << 18))))
        return 224;
    startup_mask_leave(previous);
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&current, 8) || current)
        return 224;
    errno = 0;
    if (fcntl(10, F_GETFD) != -1 || errno != EBADF || fcntl(0, F_GETFD) ||
        fcntl(1, F_GETFD) || fcntl(2, F_GETFD))
        return 224;
    unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    if (getpid() != (pid_t)(gen * 4 + 3) || getppid() != (pid_t)(
#ifdef FORK_REPEAT
                                                             5
#else
                                                             gen * 4 + 1
#endif
                                                             ))
        return 224;
#ifdef FORK_CONSOLE
    if (memtrap(0x26000, 0xf001, 0, 0, 0) != -13 ||
        write(1, "CHILD READY\n", 12) != 12)
        return 224;
#endif
#ifdef FORK_NULL
    char untouched = 'x';
    if (read(0, &untouched, 1) != 0 || untouched != 'x')
        return 224;
#endif
#ifdef FORK_SHELL_ARGV
#ifdef FORK_SHELL_CLOSED_LEAK
    if (fcntl(0, F_DUPFD, 3) != 3)
        return 224;
#endif
    extern int consumer_helper_main(int, char **);
#ifdef FORK_SHELL_ARGV_SKIP
    int result = 0;
#else
    int result = consumer_helper_main(argc, argv);
#endif
#ifdef FORK_SHELL_FILES
    for (unsigned i = 0; i < 16; ++i)
        if (startup_fds[i].present && close((int)i))
            return 224;
#elif defined(FORK_NULL)
    if (close(0))
        return 224;
    int null_failure = null_lifetime_check();
    if (null_failure)
        return null_failure;
    if (close(1) || close(2))
        return 224;
#else
    if (close(0) || close(1) || close(2))
        return 224;
#endif
#ifdef FORK_SHELL_CLOSED_LEAK
    if (close(3))
        return 224;
#endif
    return result;
#else
    char value = 0;
    if (read(0, &value, 1) != 1 || value != 'a' || close(0) || close(1) ||
        close(2))
        return 224;
    return 72;
#endif
}
