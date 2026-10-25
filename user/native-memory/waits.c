/* SPDX-License-Identifier: BSD-2-Clause */
/* Native wait conformance. Only the parent uses libc. */
#include "adapter.h"
#include <sys/auxv.h>
#include <unistd.h>

static _Thread_local volatile unsigned parent_tls = 17;
static struct {
    unsigned long cap, memory, stack, fs, tid, key, identity;
    _Atomic unsigned error;
} shared;
struct reply {
    long value;
    unsigned long detail;
};
static inline struct reply invoke(unsigned long op, unsigned long cap,
                                  unsigned long a, unsigned long b,
                                  unsigned long c, unsigned long arg,
                                  unsigned long tid)
{
    register unsigned long r10 __asm__("r10") = c;
    register unsigned long r8 __asm__("r8") = arg;
    register unsigned long r9 __asm__("r9") = tid;
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+D"(cap), "+S"(a), "+d"(b), "+r"(r10),
                           "+r"(r8), "+r"(r9)
                         :
                         : "rcx", "r11", "memory", "cc");
    return (struct reply){(long)op, b};
}
static long wake(unsigned long key)
{
    return invoke(0x28004, shared.cap, key, 0, 0, 0, 0).value;
}
static struct reply wait_word(unsigned long key, unsigned long value,
                              unsigned long ticks)
{
#ifdef INDEFINITE_WAIT
    if (ticks == 100)
        return invoke(0x28008, shared.cap, key, value, 0, 0, 0);
#endif
    return invoke(0x28003, shared.cap, key, value, ticks, 0, 0);
}

static _Noreturn __attribute__((no_stack_protector)) void
child(unsigned long arg)
{
    if (arg != shared.identity)
        shared.error = 221;
    if (wait_word(shared.key, 0, 100).value != 0)
        shared.error = 222;
    if (*(_Atomic unsigned *)shared.key != 1)
        shared.error = 223;
    for (unsigned i = 0; i < 8; ++i) {
        unsigned long got, fs, operation = 0x1fffe;
        unsigned long expected = 0xaabb0000 + shared.identity;
        __asm__ __volatile__(
            "movq %3,%%xmm0; int $0x81; movq %%xmm0,%0; movq %%fs:0,%1"
            : "=r"(got), "=r"(fs), "+a"(operation)
            : "r"(expected)
            : "xmm0", "memory", "cc");
        if (got != expected || fs != shared.identity)
            shared.error = 224;
    }
    invoke(0x28001, shared.cap, 37, 0, 0, 0, 0);
    __builtin_trap();
}
#define CHECK(x, n)                                                            \
    do {                                                                       \
        if (!(x))                                                              \
            return (n);                                                        \
    } while (0)
int main(int argc, char **argv)
{
    CHECK(argc == 2 && shared.error == 0, 230);
    shared.identity = argv[0][11] - '0';
    shared.cap = getauxval(0xa001);
    shared.memory = getauxval(0xa000);
    CHECK(shared.cap && shared.memory, 231);
    parent_tls = (unsigned)shared.identity;
    long area = memtrap(0x22001, shared.memory, 5 * 4096, 3, 0);
    CHECK(area > 0, 232);
    shared.stack = (unsigned long)area;
    shared.fs = shared.stack + 2 * 4096 + 128;
    shared.tid = shared.stack + 3 * 4096;
    shared.key = shared.stack + 4 * 4096;
    *(unsigned long *)shared.fs = shared.identity;
    CHECK(*(_Atomic unsigned *)shared.key == 0, 233);
    CHECK(invoke(0x28003, shared.cap ^ 3, shared.key, 0, 1, 0, 0).value == -13,
          234);
    CHECK(invoke(0x28004, shared.cap ^ 0x100, shared.key, 0, 0, 0, 0).value ==
              -13,
          235);
    CHECK(wait_word(shared.key + 1, 0, 1).value == -22, 236);
    CHECK(wait_word(0xdead0000, 0, 1).value == -14, 237);
    CHECK(wait_word(shared.key, 0, 0).value == -22, 238);
    CHECK(wait_word(shared.key, 0, 101).value == -22, 239);
    CHECK(wait_word(shared.key, ~0ul, 1).value == -22, 240);
    CHECK(invoke(0x28004, shared.cap, shared.key, 1, 0, 0, 0).value == -22,
          241);
    CHECK(wake(shared.key) == 0,
          216); /* Other domain's equal VA is not our wait. */
    CHECK(wait_word(shared.key, 1, 1).value == -11, 215);
    *(_Atomic unsigned *)shared.key = 1;
    CHECK(wake(shared.key) == 0, 216);
    CHECK(wait_word(shared.key, 0, 1).value == -11, 215);
    *(_Atomic unsigned *)shared.key = 0;
    CHECK(invoke(0x28003, shared.cap - 0x100, shared.key, 0, 1, 0, 0).value ==
              -13,
          235);
#ifdef INDEFINITE_WAIT
    CHECK(invoke(0x28008, shared.cap, shared.key, 1, 0, 0, 0).value == -11,
          170);
    CHECK(invoke(0x28008, shared.cap ^ 3, shared.key, 0, 0, 0, 0).value == -13,
          171);
    CHECK(invoke(0x28008, shared.cap - 0x100, shared.key, 0, 0, 0, 0).value ==
              -13,
          172);
    CHECK(invoke(0x28008, shared.cap, shared.key, 0, 1, 0, 0).value == -22,
          173);
    CHECK(invoke(0x28008, shared.cap, shared.key + 1, 0, 0, 0, 0).value == -22,
          174);
    CHECK(invoke(0x28008, shared.cap, 0xdead0000, 0, 0, 0, 0).value == -14,
          175);
    CHECK(invoke(0x28008, shared.cap, shared.key, ~0ul, 0, 0, 0).value == -22,
          176);
#endif
    unsigned long operation = 0x28003, cap = shared.cap, key = shared.key,
                  elapsed = 0, got;
    unsigned long sent = 0xeeff0000 + shared.identity;
    register unsigned long deadline __asm__("r10") = 30;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    __asm__ __volatile__("movq %8,%%xmm0; int $0x81; movq %%xmm0,%0"
                         : "=r"(got), "+a"(operation), "+D"(cap), "+S"(key),
                           "+d"(elapsed), "+r"(deadline), "+r"(r8), "+r"(r9)
                         : "r"(sent)
                         : "rcx", "r11", "xmm0", "memory", "cc");
    CHECK(got == sent, 257);
    struct reply timed = {(long)operation, elapsed};
    CHECK(timed.value == -110 && timed.detail >= 30, 242);
    CHECK(wake(shared.key) == 0, 243);
    CHECK(invoke(0x28000, shared.cap, (unsigned long)child, shared.stack,
                 shared.fs, shared.identity, shared.tid)
                  .value == 1,
          244);
    unsigned yields = 0;
    while (!invoke(0x28002, shared.cap, 0, 0, 0, 0, 0).detail) {
        CHECK(yields < 32, 245);
        memtrap(0x1fffe, 0, 0, 0, 0);
        ++yields;
    }
#ifdef INDEFINITE_WAIT
    for (unsigned n = 0; n < 2; ++n) {
        struct reply pause =
            invoke(0x28003, shared.cap, shared.key + 4, 0, 100, 0, 0);
        CHECK(pause.value == -110 && pause.detail >= 100, 177);
        CHECK(invoke(0x28002, shared.cap, 0, 0, 0, 0, 0).detail == 1 &&
                  shared.error == 0,
              178);
    }
#endif
    CHECK(wake(shared.key + 4) == 0, 246);
    CHECK(memtrap(0x22002, shared.memory, shared.key, 4096, 3) == -13, 218);
    CHECK(memtrap(0x22003, shared.memory, shared.key, 4096, 0) == -13, 247);
#ifdef STOP_LIVE
    if (shared.identity == 1 && memtrap(0x20005, 0, 0, 0, 0) == 1) {
        CHECK(memtrap(0x20004, 0, 0, 0, 0) == 0, 248);
        wait_word(shared.key, 0, 100);
        return 249; /* Stop must discard this continuation. */
    }
#endif
#ifndef THREAD_PARENT_EXIT
    *(_Atomic unsigned *)shared.key = 1;
    CHECK(wake(shared.key) == 1, 217);
    struct reply joined = wait_word(shared.tid, 1, 100);
    CHECK(joined.value == 0 || joined.value == -11, 250);
    CHECK(*(volatile unsigned *)shared.tid == 0 && shared.error == 0 &&
              invoke(0x28002, shared.cap, 0, 0, 0, 0, 0).value == 38,
          251);
    CHECK(memtrap(0x22003, shared.memory, shared.stack, 5 * 4096, 0) == 0, 252);
#endif
    for (; yields < 64; ++yields) {
        unsigned long got, operation = 0x1fffe;
        unsigned long expected = 0x11220000 + shared.identity;
        __asm__ __volatile__("movq %2,%%xmm0; int $0x81; movq %%xmm0,%0"
                             : "=r"(got), "+a"(operation)
                             : "r"(expected)
                             : "xmm0", "memory", "cc");
        CHECK(got == expected && parent_tls == shared.identity, 253);
    }
#ifdef THREAD_PARENT_EXIT
    CHECK(invoke(0x28002, shared.cap, 0, 0, 0, 0, 0).detail == 1, 254);
#endif
    CHECK(write(1, "AETHER MUSL NATIVE PASS\n", 24) == 16, 255);
    CHECK(write(1, &"AETHER MUSL NATIVE PASS\n"[16], 8) == 8, 256);
    return 0;
}
