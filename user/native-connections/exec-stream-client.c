/* SPDX-License-Identifier: BSD-2-Clause */
#define CAT_ROLES
#define SHELL_STARTUP
#include "../native-command/transport.h"
#ifdef EXEC_PUBLIC
#include <stdlib.h>
#endif
static _Thread_local volatile unsigned cookie = 71;
#if defined(EXEC_PUBLIC) && !defined(EXEC_REPLACEMENT)
#include "exec-stage.h"
#endif
#if defined(EXEC_SHARED) || defined(EXEC_PUBLIC)
int main(int argc, char **argv)
#else
int main(void)
#endif
{
    if (!startup_begin() || cookie != 71)
        return 215;
#ifdef EXEC_SHARED
    if (argc == 1 && !strcmp(argv[0], "worker")) {
#ifdef EXEC_PEER_FIRST
        unsigned char barrier[32] = {0}, expected_barrier[32] = {91};
        if (!move(barrier, sizeof barrier, 0) ||
            memcmp(barrier, expected_barrier, sizeof barrier))
            return 219;
#ifdef EXEC_PEER_FAULT
        __asm__ __volatile__("ud2");
        return 219;
#else
        if (close(0) || close(1) || close(2))
            return 219;
        return 64;
#endif
#else
        char value = 0;
        if (read(0, &value, 1) != 1 || value != 'd' || write(1, "z", 1) != 1 ||
            close(0) || close(1) || close(2))
            return 219;
        return 63;
#endif
    }
#endif
#if !defined(EXEC_PUBLIC) || defined(EXEC_REPLACEMENT)
    unsigned char table[64] = {0};
#endif
#ifdef EXEC_REPLACEMENT
#ifdef EXEC_PUBLIC
    if (argc != 2 || strcmp(argv[0], "exec-stream") ||
        strcmp(argv[1], "hello") || !getenv("AETHER_EXEC") ||
        strcmp(getenv("AETHER_EXEC"), "1"))
        return 220;
#endif
#ifdef EXEC_TABLE_PAD
    /* Deliberately promote a partial record into application readiness. */
    if (!move(table, 16, 0))
#else
    if (!move(table, sizeof table, 0))
#endif
        return 215;
    unsigned char expected[64] = {0};
    expected[2] = 1;
    expected[8] = 2;
    expected[10] = 1;
#ifndef EXEC_TABLE_SKIP
    if (memcmp(table, expected, sizeof table))
        return 216;
#else
    (void)expected; /* Deliberate reserved-byte validation bypass. */
#endif
    memset(startup_fds, 0, sizeof startup_fds);
    memset(startup_users, 0, sizeof startup_users);
    for (unsigned i = 0; i < 16; ++i) {
        startup_fds[i] = (struct startup_fd){table[i * 4], table[i * 4 + 1],
                                             table[i * 4 + 2]};
        if (startup_fds[i].present)
            startup_users[startup_fds[i].binding]++;
    }
    live[1] = 0;
#ifdef EXEC_MASK
    unsigned char saved[32] = {0};
    uint64_t previous = 0, current = 0;
    if (!move(saved, sizeof saved, 0) || memcmp(saved, "AEEMSK01", 8))
        return 222;
    for (unsigned i = 16; i < 32; ++i)
        if (saved[i])
            return 222;
    memcpy(&previous, saved + 8, 8);
    if (previous & ((UINT64_C(1) << 8) | (UINT64_C(1) << 18)) ||
        memtrap(0x1000e, 0, 0, (uintptr_t)&current, 8) ||
        current != (UINT64_MAX & ~((UINT64_C(1) << 8) | (UINT64_C(1) << 18))))
        return 222;
#ifndef EXEC_MASK_SKIP_SUCCESS
    startup_mask_leave(previous);
#endif
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&current, 8) || current != previous)
        return 222;
#endif
    errno = 0;
    if (fcntl(10, F_GETFD) != -1 || errno != EBADF)
        return 216;
    errno = 0;
    if (fcntl(1, F_GETFD) != -1 || errno != EBADF || fcntl(0, F_GETFD) != 0 ||
        fcntl(2, F_GETFD) != 0)
        return 216;
#ifdef EXEC_FORK
    unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    uint64_t mask = 0;
    if (getpid() != (pid_t)(gen * 4 + 3) || getppid() != (pid_t)(gen * 4 + 1) ||
        memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) || mask != 16)
        return 223;
#endif
#ifdef EXEC_PENDING
    /* The backend opens stdin only after observing an empty parent read. */
    int released = 0;
    for (unsigned attempt = 0; attempt < 100000; ++attempt) {
        if (write(2, "!", 1) == 1) {
            released = 1;
            break;
        }
        if (errno != EAGAIN)
            return 225;
    }
    if (!released)
        return 225;
#endif
    char value = 0;
    if (read(0, &value, 1) != 1 ||
        value !=
#ifdef EXEC_DISPATCH
            'a'
#elif defined(EXEC_FORK)
            'b'
#else
            'c'
#endif
        || close(0) || close(2))
        return 217;
#ifdef EXEC_FORK
    return 72;
#else
    return 62;
#endif
#else
    char value = 0;
    if (read(0, &value, 1) != 1 || value != 'a' ||
        fcntl(0, F_DUPFD_CLOEXEC, 10) != 10 || fcntl(1, F_SETFD, FD_CLOEXEC))
        return 215;
#ifdef EXEC_PUBLIC
    (void)argc;
    (void)argv;
    char *next_args[] = {"exec-stream", "hello", 0};
    char *next_env[] = {"AETHER_EXEC=1", 0};
#ifdef EXEC_MASK
    uint64_t caller_mask = 16;
#ifdef EXEC_MASK_ZERO
    caller_mask = 0;
#endif
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&caller_mask, 0, 8))
        return 221;
#else
    errno = 0;
    if (execve("/next", next_args, next_env) != -1 || errno != ENOTSUP)
        return 220;
    uint64_t all = UINT64_MAX;
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&all, 0, 8))
        return 220;
#endif
    errno = 0;
    if (execve("/absent", next_args, next_env) != -1 || errno != ENOENT)
        return 220;
    errno = 0;
    if (execve("/denied", next_args, next_env) != -1 || errno != EACCES ||
        fcntl(10, F_GETFD) != FD_CLOEXEC || fcntl(1, F_GETFD) != FD_CLOEXEC)
        return 220;
#ifdef EXEC_MASK
    uint64_t observed = 0;
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) ||
        observed != caller_mask)
        return 221;
#endif
    if (read(10, &value, 1) != 1 || value != 'b' || cookie != 71)
        return 220;
    execve("/next", next_args, next_env);
    return 218;
#else
    for (unsigned i = 0; i < 16; ++i) {
        table[i * 4] = startup_fds[i].binding;
        table[i * 4 + 1] = startup_fds[i].flags;
        table[i * 4 + 2] = startup_fds[i].present;
    }
    if (!move(table, sizeof table, 1) || memtrap(0x23003, 0, 0, 0, 0) != -11 ||
        fcntl(10, F_GETFD) != FD_CLOEXEC || fcntl(1, F_GETFD) != FD_CLOEXEC ||
        read(10, &value, 1) != 1 || value != 'b' || cookie != 71)
        return 215;
    memtrap(0x23003, 0, 0, 0, 0);
    return 218;
#endif
#endif
}
