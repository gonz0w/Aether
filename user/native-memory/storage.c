/* SPDX-License-Identifier: BSD-2-Clause */
/* Native TLS-range and separate TID-storage conformance. Only the parent uses
 * libc. */
#include "adapter.h"
#include <sys/auxv.h>
#include <unistd.h>
#ifdef LIBC_TLS
unsigned long libc_child_prepare(unsigned long, unsigned long, unsigned);
int libc_child_check(unsigned long, unsigned, int);
int libc_parent_check(void);
void libc_parent_prepare(void);
#endif
#ifdef LIBC_WAIT
int libc_wait_prepare(unsigned long, unsigned long);
int libc_wait_child(unsigned long);
long libc_wait_wake(unsigned long);
int libc_wait_check(void);
#endif

static _Thread_local volatile unsigned parent_tls = 17;
static struct {
    unsigned long cap, memory, stack, fs, tid, key, identity, tls;
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
#ifndef LIBC_WAIT
static long wake(unsigned long key)
{
    return invoke(0x28004, shared.cap, key, 0, 0, 0, 0).value;
}
#endif
static struct reply wait_word(unsigned long key, unsigned long value,
                              unsigned long ticks)
{
    return invoke(0x28003, shared.cap, key, value, ticks, 0, 0);
}

struct descriptor {
    unsigned version, size;
    unsigned long entry, base, bytes, rsp, fs, tid, argument;
    unsigned long tls_base, tls_bytes, parent_tid, reserved;
};
_Static_assert(sizeof(struct descriptor) == 96, "descriptor size");
static struct descriptor request;
static long create(const struct descriptor *d)
{
    return invoke(0x28006, shared.cap, (unsigned long)d, 0, 0, 0, 0).value;
}
static _Noreturn __attribute__((no_stack_protector)) void
child(unsigned long arg)
{
    volatile unsigned char local[256 * 1024 - 2048];
    if (invoke(0x28007, shared.cap, 0, 0, 0, 0, 0).value !=
        (long)(shared.identity + 2))
        shared.error = 6;
    if (invoke(0x10000 + 218, shared.tid, 0, 0, 0, 0, 0).value !=
        (long)(shared.identity + 2))
        shared.error = 7;
    if (invoke(0x10000 + 158, 0x1002, shared.tid, 0, 0, 0, 0).value != -22)
        shared.error = 8;
    if (invoke(0x10000 + 158, 0x1002, shared.fs + 8, 0, 0, 0, 0).value != 0 ||
        invoke(0x10000 + 158, 0x1002, shared.fs, 0, 0, 0, 0).value != 0)
        shared.error = 9;
    if (*(volatile unsigned long *)shared.tls != 0x1357 ||
        *(volatile unsigned long *)(shared.tls + 3 * 4096 - 8) != 0x2468)
        shared.error = 10;
#ifdef LIBC_TLS
    if (!libc_child_check(shared.fs, (unsigned)(shared.identity + 2), 1))
        shared.error = 11;
#endif
    if (arg != shared.identity)
        shared.error = 1;
#ifdef LIBC_WAIT
    if (libc_wait_child(shared.key) != 0)
#else
    if (wait_word(shared.key, 0, 100).value != 0)
#endif
        shared.error = 2;
#ifdef THREAD_FAULT
    if (shared.identity == 1) {
        volatile unsigned char guard =
            *(volatile unsigned char *)(shared.stack - 1);
        (void)guard;
    }
#endif
    for (unsigned i = 0; i < sizeof local; i += 4096)
        local[i] = (unsigned char)(i / 4096 + arg);
    local[sizeof local - 1] = 93;
    for (unsigned n = 0; n < 8; ++n) {
        unsigned long got, fs, op = 0x1fffe, sent = 0xaabb0000 + arg;
        __asm__ __volatile__(
            "movq %3,%%xmm0; int $0x81; movq %%xmm0,%0; movq %%fs:0,%1"
            : "=r"(got), "=r"(fs), "+a"(op)
            : "r"(sent)
            : "xmm0", "memory", "cc");
#ifdef LIBC_TLS
        if (!libc_child_check(shared.fs, (unsigned)(shared.identity + 2), 0))
            shared.error = 12;
        const unsigned long expected_fs = shared.fs;
#else
        const unsigned long expected_fs = arg;
#endif
        if (got != sent || fs != expected_fs)
            shared.error = 3;
    }
    for (unsigned i = 0; i < sizeof local; i += 4096)
        if (local[i] != (unsigned char)(i / 4096 + arg))
            shared.error = 4;
    if (local[sizeof local - 1] != 93)
        shared.error = 5;
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
    CHECK(argc == 2 && shared.error == 0, 260);
    shared.identity = argv[0][11] - '0';
    parent_tls = (unsigned)shared.identity;
    shared.cap = getauxval(0xa001);
    shared.memory = getauxval(0xa000);
    CHECK(shared.cap && shared.memory, 261);
    long raw = memtrap(0x22001, shared.memory, 71 * 4096, 0, 0);
    CHECK(raw > 0, 262);
    shared.stack = (unsigned long)raw + 8192;
    const unsigned long bytes = 256 * 1024, end = shared.stack + bytes;
    CHECK(memtrap(0x22002, shared.memory, shared.stack, bytes + 5 * 4096, 3) ==
              0,
          263);
    shared.fs = end + 4096 + 128;
    shared.tls = end;
    shared.tid = end + 3 * 4096;
    const unsigned long parent_tid = end + 4 * 4096;
    *(volatile unsigned *)parent_tid = 77;
    *(volatile unsigned long *)shared.tls = 0x1357;
    *(volatile unsigned long *)(shared.tls + 3 * 4096 - 8) = 0x2468;
    shared.key = shared.tid + 8;
    *(unsigned long *)shared.fs = shared.identity;
    *(volatile unsigned *)shared.tid = 99;
    request = (struct descriptor){1,
                                  96,
                                  (unsigned long)child,
                                  shared.stack,
                                  bytes,
                                  end - 264,
                                  shared.fs,
                                  shared.tid,
                                  shared.identity,
                                  shared.tls,
                                  3 * 4096,
                                  parent_tid,
                                  0};
    *(unsigned long *)request.rsp = 0x1234;
    *(unsigned long *)(end - 8) = 0x5678;
    CHECK(invoke(0x28006, shared.cap ^ 3, (unsigned long)&request, 0, 0, 0, 0)
                  .value == -13,
          264);
    CHECK(invoke(0x28006, shared.cap, (unsigned long)&request, 1, 0, 0, 0)
                  .value == -22,
          265);
    CHECK(create((void *)(parent_tid + 4096 - 32)) == -14, 266);
    struct descriptor bad = request;
    bad.version = 2;
    CHECK(create(&bad) == -22, 267);
    bad = request;
    bad.size = 63;
    CHECK(create(&bad) == -22, 268);
    bad = request;
    bad.bytes = 0;
    CHECK(create(&bad) == -22, 269);
    bad = request;
    bad.rsp = end;
    CHECK(create(&bad) == -22, 270);
    bad = request;
    bad.rsp = shared.stack + 8;
    CHECK(create(&bad) == -22, 271);
    bad = request;
    bad.bytes = ~4095ul;
    CHECK(create(&bad) == -22, 272);
    bad = request;
    bad.tid = 0xdead0000;
    CHECK(create(&bad) == -14, 273);
    CHECK(invoke(0x28007, shared.cap, 0, 0, 0, 0, 0).value ==
              (long)shared.identity,
          140);
    CHECK(invoke(0x28007, shared.cap ^ 3, 0, 0, 0, 0, 0).value == -13, 141);
    CHECK(invoke(0x28007, shared.cap, 0, 0, 0, 0, 1).value == -22, 142);
    bad = request;
    bad.reserved = 1;
    CHECK(create(&bad) == -22, 143);
    bad = request;
    bad.parent_tid = 0;
    CHECK(create(&bad) == -22, 144);
    bad = request;
    bad.parent_tid = 0xdead0000;
    CHECK(create(&bad) == -14, 145);
    bad = request;
    bad.tls_bytes = 0;
    CHECK(create(&bad) == -22, 146);
    bad = request;
    bad.tls_bytes = ~4095ul;
    CHECK(create(&bad) == -22, 147);
    bad = request;
    bad.tls_base += 1;
    CHECK(create(&bad) == -22, 148);
    bad = request;
    bad.fs = shared.tid;
    CHECK(create(&bad) == -22, 149);
    bad = request;
    bad.fs = 0xdead0000;
    CHECK(create(&bad) == -22, 161);
    bad = request;
    bad.parent_tid += 1;
    CHECK(create(&bad) == -22, 162);
    for (unsigned i = 0; i < 3; ++i) {
        CHECK(memtrap(0x22002, shared.memory, shared.tls + i * 4096, 4096, 1) ==
                  0,
              150);
        CHECK(create(&request) == -14, 151);
        CHECK(memtrap(0x22002, shared.memory, shared.tls + i * 4096, 4096, 3) ==
                  0,
              152);
    }
    CHECK(memtrap(0x22003, shared.memory, shared.tls, 4096, 0) == 0, 153);
    CHECK(create(&request) == -14, 154);
    CHECK(memtrap(0x22001, shared.memory, 4096, 3, 0) == (long)shared.tls, 155);
    *(volatile unsigned long *)shared.tls = 0x1357;
    CHECK(*(volatile unsigned *)parent_tid == 77, 156);
    CHECK(*(volatile unsigned *)shared.tid == 99 &&
              *(unsigned long *)request.rsp == 0x1234 &&
              invoke(0x28002, shared.cap, 0, 0, 0, 0, 0).value == -2,
          283);
#ifdef LIBC_TLS
    shared.fs = libc_child_prepare(shared.tls + 4096, 4096,
                                   (unsigned)(shared.identity + 2));
    CHECK(shared.fs != 0, 163);
    request.fs = shared.fs;
    libc_parent_prepare();
#ifdef LIBC_WAIT
    CHECK(libc_wait_prepare(shared.cap, shared.key), 165);
#endif
#endif
#ifdef THREAD_ALIAS
    request.parent_tid = request.rsp + 56;
    *(struct descriptor *)request.rsp = request;
    CHECK(create((void *)request.rsp) == (long)(shared.identity + 2), 284);
#else
    CHECK(create(&request) == (long)(shared.identity + 2), 284);
#endif
    CHECK(*(unsigned long *)request.rsp == 0 &&
              *(unsigned long *)(end - 8) == 0x5678,
          285);
    CHECK(*(volatile unsigned *)request.parent_tid == shared.identity + 2 &&
              *(volatile unsigned *)shared.tid == 99,
          157);
    CHECK(create(&request) == -28, 158);
    CHECK(memtrap(0x22003, shared.memory, parent_tid, 4096, 0) == 0, 159);
    unsigned yields = 0;
    while (!invoke(0x28002, shared.cap, 0, 0, 0, 0, 0).detail) {
        CHECK(yields < 32, 286);
        memtrap(0x1fffe, 0, 0, 0, 0);
        ++yields;
    }
    for (unsigned i = 0; i < 3; ++i) {
        CHECK(memtrap(0x22002, shared.memory, shared.tls + i * 4096, 4096, 3) ==
                  -13,
              194);
        CHECK(memtrap(0x22003, shared.memory, shared.tls + i * 4096, 4096, 0) ==
                  -13,
              160);
    }
#ifdef STOP_LIVE
    if (shared.identity == 1 && memtrap(0x20005, 0, 0, 0, 0) == 1) {
        CHECK(memtrap(0x20004, 0, 0, 0, 0) == 0, 287);
        wait_word(shared.key, 0, 100);
        return 288;
    }
#endif
    *(_Atomic unsigned *)shared.key = 1;
#ifdef LIBC_WAIT
    CHECK(libc_wait_wake(shared.key) == 1, 289);
#else
    CHECK(wake(shared.key) == 1, 289);
#endif
    struct reply joined = wait_word(shared.tid, 99, 100);
    CHECK(joined.value == 0 || joined.value == -11, 290);
    CHECK(shared.error == 0 && *(volatile unsigned *)shared.tid == 0 &&
              invoke(0x28002, shared.cap, 0, 0, 0, 0, 0).value == 38,
          291);
#ifdef LIBC_TLS
    CHECK(libc_parent_check(), 164);
#ifdef LIBC_WAIT
    CHECK(libc_wait_check(), 166);
#endif
#endif
    CHECK(memtrap(0x22003, shared.memory, (unsigned long)raw, 70 * 4096, 0) ==
              0,
          292);
    for (; yields < 64; ++yields) {
        memtrap(0x1fffe, 0, 0, 0, 0);
        CHECK(parent_tls == shared.identity, 293);
    }
    CHECK(write(1, "AETHER MUSL NATIVE PASS\n", 24) == 16, 294);
    CHECK(write(1, &"AETHER MUSL NATIVE PASS\n"[16], 8) == 8, 295);
    return 0;
}
