/* SPDX-License-Identifier: BSD-2-Clause */
#include <signal.h>
static volatile sig_atomic_t suspend_calls, suspend_bad;
static void suspend_handler(int signal)
{
    uint64_t mask = 0;
    if (signal != SIGCHLD || memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) ||
        mask != (2u | (1u << (SIGCHLD - 1))))
        suspend_bad = 1;
    suspend_calls++;
}
#ifdef FORK_WAIT_SUSPEND_FRAME
/* No C stack access occurs between switching RSP and restoring it from R11.
 * Both rejection and ordinary sigreturn preserve the interrupted R11 value. */
__attribute__((naked)) static long suspend_on_stack(const sigset_t *mask,
                                                    uintptr_t stack)
{
    __asm__ __volatile__("mov %rsp, %r11\n"
#ifndef FORK_WAIT_SUSPEND_FRAME_VALID
                         "mov %rsi, %rsp\n"
#endif
                         "mov $8, %esi\n"
                         "mov $0x10082, %eax\n"
                         "int $0x81\n"
                         "mov %r11, %rsp\n"
                         "ret\n");
}
static int suspend_rejection_check(const sigset_t *temporary)
{
    volatile unsigned char *canary = (void *)(uintptr_t)0x08000000;
    const uintptr_t positions[] = {0x08000080, 0x08000350, 0x08000358};
    for (unsigned i = 0; i < 1024; ++i)
        canary[i] = (unsigned char)(i ^ 0xa5);
    for (unsigned attempt = 0; attempt < 3; ++attempt) {
        uint64_t mask = 0;
        if (suspend_on_stack(temporary, positions[attempt]) != -EINVAL ||
            suspend_calls || suspend_bad ||
            memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) ||
            mask != (16u | (1u << (SIGCHLD - 1))))
            return 0;
        for (unsigned i = 0; i < 1024; ++i)
            if (canary[i] != (unsigned char)(i ^ 0xa5))
                return 0;
    }
    return 1;
}
#endif
__attribute__((unused)) static int suspend_check(void)
{
    struct sigaction action = {0}, old;
    sigset_t original, temporary;
    sigemptyset(&action.sa_mask);
    action.sa_handler = suspend_handler;
    if (sigaction(SIGCHLD, &action, &old))
        return 0;
    sigemptyset(&original);
    sigaddset(&original, SIGCHLD);
    sigaddset(&original, SIGUSR1);
    sigemptyset(&temporary);
    sigaddset(&temporary, SIGINT);
    if (sigprocmask(SIG_SETMASK, &original, 0) ||
        memtrap(0x10082, 0, 7, 0, 0) != -EINVAL ||
        memtrap(0x10082, 0, 8, 0, 0) != -EFAULT ||
        memtrap(0x29002, SIGCHLD, 0, 0, 0) || suspend_calls)
        return 0;
    errno = 0;
    if (sigsuspend(&temporary) != -1 || errno != EINTR || suspend_calls != 1 ||
        suspend_bad)
        return 0;
    uint64_t restored = 0;
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&restored, 8) ||
        restored != ((1u << (SIGCHLD - 1)) | (1u << (SIGUSR1 - 1))))
        return 0;
    sigemptyset(&temporary);
    return !sigaction(SIGCHLD, &old, 0) &&
           !sigprocmask(SIG_SETMASK, &temporary, 0);
}
