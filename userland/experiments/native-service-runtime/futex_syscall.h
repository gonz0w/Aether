/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixture transport for the selected musl internal wait operations only. */
#define __SYSCALL_LL_E(x) (x)
#define __SYSCALL_LL_O(x) (x)
long aether_wait_syscall(long, long, long, long, long, long, long);
static inline long __syscall0(long n)
{
    return aether_wait_syscall(n, 0, 0, 0, 0, 0, 0);
}
static inline long __syscall1(long n, long a1)
{
    return aether_wait_syscall(n, a1, 0, 0, 0, 0, 0);
}
static inline long __syscall2(long n, long a1, long a2)
{
    return aether_wait_syscall(n, a1, a2, 0, 0, 0, 0);
}
static inline long __syscall3(long n, long a1, long a2, long a3)
{
    return aether_wait_syscall(n, a1, a2, a3, 0, 0, 0);
}
static inline long __syscall4(long n, long a1, long a2, long a3, long a4)
{
    return aether_wait_syscall(n, a1, a2, a3, a4, 0, 0);
}
static inline long __syscall5(long n, long a1, long a2, long a3, long a4,
                              long a5)
{
    return aether_wait_syscall(n, a1, a2, a3, a4, a5, 0);
}
static inline long __syscall6(long n, long a1, long a2, long a3, long a4,
                              long a5, long a6)
{
    return aether_wait_syscall(n, a1, a2, a3, a4, a5, a6);
}
