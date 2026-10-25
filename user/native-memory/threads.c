/* SPDX-License-Identifier: BSD-2-Clause */
/* Native thread conformance only. Child has no libc TCB and never calls libc.
 */
#include "adapter.h"
#include <sys/auxv.h>
#include <unistd.h>

static _Thread_local volatile unsigned parent_tls = 17;
static struct {
    unsigned long cap, memory, stack, fs, tid, identity;
    _Atomic unsigned progress, error, started;
    _Atomic unsigned hold;
    _Atomic unsigned release;
} shared;

static inline long thread_call(unsigned long op, unsigned long cap,
                               unsigned long entry, unsigned long stack,
                               unsigned long fs, unsigned long arg,
                               unsigned long tid)
{
    register unsigned long r10 __asm__("r10") = fs;
    register unsigned long r8 __asm__("r8") = arg;
    register unsigned long r9 __asm__("r9") = tid;
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+D"(cap), "+S"(entry), "+d"(stack),
                           "+r"(r10), "+r"(r8), "+r"(r9)
                         :
                         : "rcx", "r11", "memory", "cc");
    return (long)op;
}

#ifdef SIGNAL_MASK
static long mask(unsigned long how, const unsigned long *input,
                 unsigned long *output)
{
    return memtrap(0x28009, shared.cap, how, (unsigned long)input,
                   (unsigned long)output);
}
static int mask_checks(void)
{
    unsigned long old = 99, value = ~0UL;
    const unsigned long allowed = ~((1UL << 8) | (1UL << 18));
#define MC(x, n)                                                               \
    do {                                                                       \
        if (!(x))                                                              \
            return n;                                                          \
    } while (0)
    MC(mask(~0UL, 0, &old) == 0 && old == 0, 221);
    MC(mask(2, &value, &old) == 0 && old == 0, 222);
    MC(mask(0, 0, &old) == 0 && old == allowed, 223);
    MC(mask(1, &value, &old) == 0 && old == allowed, 224);
    value = 5;
    MC(mask(0, &value, &old) == 0 && old == 0, 225);
    value = 1;
    MC(mask(1, &value, &old) == 0 && old == 5, 226);
    value = 37;
    MC(mask(2, &value, &value) == 0 && value == 4, 227);
    MC(mask(0, 0, &old) == 0 && old == 37, 228);
    old = 0x1234;
    MC(memtrap(0x28009, shared.cap ^ 0x100, 2, ~0UL, (unsigned long)&old) ==
               -13 &&
           old == 0x1234,
       229);
    MC(memtrap(0x28009, shared.cap ^ 3, 2, 0, 0) == -13 &&
           memtrap(0x28009, 0, 0, 0, 0) == -13,
       230);
    MC(mask(3, &value, &old) == -22 && old == 0x1234, 231);
    MC(thread_call(0x28009, shared.cap, 0, 0, 0, 1, 0) == -22 &&
           thread_call(0x28009, shared.cap, 0, 0, 0, 0, 1) == -22,
       232);
    MC(mask(2, (const unsigned long *)~0UL, &old) == -14 && old == 0x1234, 233);
    MC(mask(2, &value, (unsigned long *)~0UL) == -14, 234);
    unsigned char *scratch = (unsigned char *)shared.stack;
    for (unsigned i = 0; i < 16; ++i)
        scratch[i] = 0;
    scratch[0] = 9;
    MC(mask(2, (const unsigned long *)scratch,
            (unsigned long *)(scratch + 1)) == 0 &&
           scratch[1] == 37,
       235);
    for (unsigned i = 2; i <= 8; ++i)
        MC(scratch[i] == 0, 235);
    for (unsigned i = 0; i < 8; ++i)
        scratch[4092 + i] = 0xa5;
    MC(memtrap(0x22002, shared.memory, shared.stack + 4096, 4096, 0) == 0, 236);
    MC(mask(2, &value, (unsigned long *)(scratch + 4092)) == -14, 237);
    for (unsigned i = 0; i < 4; ++i)
        MC(scratch[4092 + i] == 0xa5, 237);
    old = 0x1234;
    MC(mask(2, (const unsigned long *)(scratch + 4092), &old) == -14 &&
           old == 0x1234,
       238);
    MC(mask(0, 0, &old) == 0 && old == 9, 239);
    MC(memtrap(0x22002, shared.memory, shared.stack + 4096, 4096, 3) == 0, 240);
    MC(mask(0, 0, (unsigned long *)(scratch + 4092)) == 0 && scratch[4092] == 9,
       241);
    for (unsigned i = 1; i < 8; ++i)
        MC(scratch[4092 + i] == 0, 241);
    MC(mask(0, 0, (unsigned long *)mask_checks) == -14, 241);
    value = 1UL << shared.identity;
    MC(mask(2, &value, 0) == 0, 242);
#undef MC
    return 0;
}
#endif

static _Noreturn
    __attribute__((no_stack_protector)) void child(unsigned long arg)
{
#ifdef SIGNAL_MASK
    unsigned long child_mask = 0, expected_mask = 1UL << shared.identity;
    if (mask(0, 0, &child_mask) != 0 || child_mask != expected_mask)
        shared.error = 220;
    expected_mask |= 1UL << 60;
    if (mask(2, &expected_mask, 0) != 0)
        shared.error = 243;
#endif
    if (arg != (unsigned long)&shared)
        shared.error = 201;
    if (thread_call(0x28002, shared.cap, 0, 0, 0, 0, 0) != -13)
        shared.error = 202;
    if (memtrap(0x22002, shared.memory, shared.stack, 4096, 3) != -13)
        shared.error = 210;
    for (; shared.progress < 8 || shared.hold || !shared.release;) {
        unsigned long got, fs, op = 0x1fffe;
        unsigned long expected = 0xaabb0000 + shared.identity;
        __asm__ __volatile__(
            "movq %3,%%xmm0; int $0x81; movq %%xmm0,%0; movq %%fs:0,%1"
            : "=r"(got), "=r"(fs), "+a"(op)
            : "r"(expected)
            : "xmm0", "memory", "cc");
        if (got != expected || fs != shared.identity)
            shared.error = 203;
#ifdef SIGNAL_MASK
        if (mask(0, 0, &child_mask) != 0 || child_mask != expected_mask)
            shared.error = 244;
#endif
        shared.started = 1;
        if (shared.release)
            ++shared.progress;
#ifdef THREAD_FAULT
        if (shared.identity == 1)
            __asm__ __volatile__("ud2");
#endif
    }
    thread_call(0x28001, shared.cap, 37, 0, 0, 0, 0);
    __builtin_trap();
}

#define CHECK(x, n)                                                            \
    do {                                                                       \
        if (!(x))                                                              \
            return (n);                                                        \
    } while (0)
int main(int argc, char **argv)
{
    CHECK(argc == 2, 180);
    CHECK(shared.progress == 0 && shared.error == 0, 181);
    shared.identity = argv[0][11] - '0';
    shared.cap = getauxval(0xa001);
    shared.memory = getauxval(0xa000);
    CHECK(shared.cap && shared.memory, 182);
    parent_tls = (unsigned)shared.identity;
    long area = memtrap(0x22001, shared.memory, 4 * 4096, 3, 0);
    CHECK(area > 0, 183);
    shared.stack = (unsigned long)area;
    shared.fs = shared.stack + 2 * 4096 + 128;
    shared.tid = shared.stack + 3 * 4096;
#ifdef SIGNAL_MASK
    int mask_status = mask_checks();
    CHECK(mask_status == 0, mask_status);
#endif
    *(unsigned long *)shared.fs = shared.identity;
    *(volatile unsigned *)shared.tid = 99;
    *(unsigned long *)(shared.stack + 4096 - 8) = 0x1234;
    CHECK(thread_call(0x28002, shared.cap, 0, 0, 0, 0, 0) == -2, 184);
    CHECK(thread_call(0x28001, shared.cap, 0, 0, 0, 0, 0) == -13, 185);
    CHECK(thread_call(0x28000, shared.cap ^ 3, (unsigned long)child,
                      shared.stack, shared.fs, (unsigned long)&shared,
                      shared.tid) == -13,
          186);
    CHECK(thread_call(0x28000, 0, (unsigned long)child, shared.stack, shared.fs,
                      0, shared.tid) == -13,
          211);
    CHECK(thread_call(0x28000, shared.cap ^ 0x100, (unsigned long)child,
                      shared.stack, shared.fs, 0, shared.tid) == -13,
          212);
    CHECK(thread_call(0x28000, shared.cap, (unsigned long)child,
                      shared.stack + 4 * 4096, shared.fs, 0, shared.tid) == -14,
          213);
    CHECK(thread_call(0x28000, shared.cap, (unsigned long)&shared, shared.stack,
                      shared.fs, 0, shared.tid) == -14,
          187);
    CHECK(thread_call(0x28000, shared.cap, (unsigned long)child,
                      shared.stack + 1, shared.fs, 0, shared.tid) == -22,
          188);
    CHECK(thread_call(0x28000, shared.cap, (unsigned long)child, shared.stack,
                      0xdead0000, 0, shared.tid) == -14,
          189);
    CHECK(thread_call(0x28000, shared.cap, (unsigned long)child, shared.stack,
                      shared.fs, 0, 0xdead0000) == -14,
          190);
    CHECK(*(volatile unsigned *)shared.tid == 99 &&
              *(unsigned long *)(shared.stack + 4096 - 8) == 0x1234 &&
              thread_call(0x28002, shared.cap, 0, 0, 0, 0, 0) == -2,
          191);
#ifdef STOP_LIVE
    shared.hold = shared.identity == 1 && memtrap(0x20005, 0, 0, 0, 0) == 1;
#endif
#ifdef THREAD_PARENT_EXIT
    shared.hold = 1;
#endif
    CHECK(thread_call(0x28000, shared.cap, (unsigned long)child, shared.stack,
                      shared.fs, (unsigned long)&shared, shared.tid) == 1,
          192);
    CHECK(thread_call(0x28000, shared.cap, 0, 0, 0, 0, 0) == -28, 193);
    /* Child cannot complete until the parent starts yielding below. Timer
       preemption is allowed, so hold it until all live-pin checks complete. */
    CHECK(memtrap(0x22002, shared.memory, shared.stack, 4096, 3) == -13, 194);
    CHECK(memtrap(0x22003, shared.memory, shared.stack + 4096, 4096, 0) == -13,
          195);
    CHECK(memtrap(0x22003, shared.memory, shared.stack + 2 * 4096, 4096, 0) ==
              -13,
          196);
    CHECK(memtrap(0x22003, shared.memory, shared.tid, 4096, 0) == -13, 197);
#ifdef STOP_LIVE
    if (shared.hold) {
        while (!shared.started)
            memtrap(0x1fffe, 0, 0, 0, 0);
        CHECK(memtrap(0x20004, 0, 0, 0, 0) == 0, 198);
        for (;;)
            memtrap(0x1fffe, 0, 0, 0, 0);
    }
#endif
#ifdef SIGNAL_MASK
    unsigned long own_mask = 0, empty_mask = 0;
    CHECK(mask(2, &empty_mask, &own_mask) == 0 &&
              own_mask == (1UL << shared.identity),
          245);
#endif
    shared.release = 1;
    for (unsigned i = 0; i < 64; ++i) {
        unsigned long got, op = 0x1fffe;
        unsigned long expected = 0x11220000 + shared.identity;
        __asm__ __volatile__("movq %2,%%xmm0; int $0x81; movq %%xmm0,%0"
                             : "=r"(got), "+a"(op)
                             : "r"(expected)
                             : "xmm0", "memory", "cc");
        CHECK(got == expected && parent_tls == shared.identity, 199);
#ifdef SIGNAL_MASK
        CHECK(mask(0, 0, &own_mask) == 0 && own_mask == 0, 246);
#endif
    }
#ifdef SIGNAL_MASK
    CHECK(shared.error != 220, 220);
#endif
#ifndef THREAD_PARENT_EXIT
    CHECK(shared.progress == 8 && shared.error == 0, 200);
    CHECK(thread_call(0x28002, shared.cap, 0, 0, 0, 0, 0) == 38 &&
              *(volatile unsigned *)shared.tid == 0,
          204);
    CHECK(thread_call(0x28002, shared.cap, 0, 0, 0, 0, 0) == 38, 205);
    CHECK(thread_call(0x28000, shared.cap, 0, 0, 0, 0, 0) == -28, 206);
    CHECK(memtrap(0x22003, shared.memory, shared.stack, 4 * 4096, 0) == 0, 207);
#else
    CHECK(shared.progress > 0 && shared.error == 0 &&
              thread_call(0x28002, shared.cap, 0, 0, 0, 0, 0) == 0 &&
              *(volatile unsigned *)shared.tid == 1,
          214);
#endif
    CHECK(write(1, "AETHER MUSL NATIVE PASS\n", 24) == 16, 208);
    CHECK(write(1, &"AETHER MUSL NATIVE PASS\n"[16], 8) == 8, 209);
    return 0;
}
