/* SPDX-License-Identifier: BSD-2-Clause */
/* Native stack-range conformance. Only the parent uses libc. */
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
    return invoke(0x28003, shared.cap, key, value, ticks, 0, 0);
}

struct descriptor {
    unsigned version, size;
    unsigned long entry, base, bytes, rsp, fs, tid, argument;
};
_Static_assert(sizeof(struct descriptor) == 64, "descriptor size");
static struct descriptor request;
static long create(const struct descriptor *d)
{
    return invoke(0x28005, shared.cap, (unsigned long)d, 0, 0, 0, 0).value;
}
static _Noreturn __attribute__((no_stack_protector)) void
child(unsigned long arg)
{
    volatile unsigned char local[256 * 1024 - 2048];
    if (arg != shared.identity)
        shared.error = 1;
    if (wait_word(shared.key, 0, 100).value != 0)
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
        if (got != sent || fs != arg)
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
    long raw = memtrap(0x22001, shared.memory, 69 * 4096, 0, 0);
    CHECK(raw > 0, 262);
    shared.stack = (unsigned long)raw + 8192;
    const unsigned long bytes = 256 * 1024, end = shared.stack + bytes;
    CHECK(memtrap(0x22002, shared.memory, shared.stack, bytes + 3 * 4096, 3) ==
              0,
          263);
    shared.fs = end + 4096 + 128;
    shared.tid = end + 8192;
    shared.key = shared.tid + 8;
    *(unsigned long *)shared.fs = shared.identity;
    *(volatile unsigned *)shared.tid = 99;
    request = (struct descriptor){
        1,         64,        (unsigned long)child, shared.stack,   bytes,
        end - 264, shared.fs, shared.tid,           shared.identity};
    *(unsigned long *)request.rsp = 0x1234;
    *(unsigned long *)(end - 8) = 0x5678;
    CHECK(invoke(0x28005, shared.cap ^ 3, (unsigned long)&request, 0, 0, 0, 0)
                  .value == -13,
          264);
    CHECK(invoke(0x28005, shared.cap, (unsigned long)&request, 1, 0, 0, 0)
                  .value == -22,
          265);
    CHECK(create((void *)(shared.tid + 4096 - 32)) == -14, 266);
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
    CHECK(memtrap(0x22002, shared.memory, shared.stack, 4096, 1) == 0, 274);
    CHECK(create(&request) == -14, 275);
    CHECK(memtrap(0x22002, shared.memory, shared.stack, 4096, 3) == 0, 276);
    CHECK(memtrap(0x22002, shared.memory, end - 4096, 4096, 0) == 0, 277);
    CHECK(create(&request) == -14, 278);
    CHECK(memtrap(0x22002, shared.memory, end - 4096, 4096, 3) == 0, 279);
    CHECK(memtrap(0x22003, shared.memory, shared.stack + 32 * 4096, 4096, 0) ==
              0,
          280);
    CHECK(create(&request) == -14, 281);
    CHECK(memtrap(0x22001, shared.memory, 4096, 3, 0) ==
              (long)(shared.stack + 32 * 4096),
          282);
    CHECK(*(volatile unsigned *)shared.tid == 99 &&
              *(unsigned long *)request.rsp == 0x1234 &&
              invoke(0x28002, shared.cap, 0, 0, 0, 0, 0).value == -2,
          283);
#ifdef THREAD_ALIAS
    *(struct descriptor *)request.rsp = request;
    CHECK(create((void *)request.rsp) == 1, 284);
#else
    CHECK(create(&request) == 1, 284);
#endif
    CHECK(*(unsigned long *)request.rsp == 0 &&
              *(unsigned long *)(end - 8) == 0x5678,
          285);
    unsigned yields = 0;
    while (!invoke(0x28002, shared.cap, 0, 0, 0, 0, 0).detail) {
        CHECK(yields < 32, 286);
        memtrap(0x1fffe, 0, 0, 0, 0);
        ++yields;
    }
    for (unsigned i = 0; i < 64; ++i)
        CHECK(memtrap(0x22002, shared.memory, shared.stack + i * 4096, 4096,
                      3) == -13,
              194);
#ifdef STOP_LIVE
    if (shared.identity == 1 && memtrap(0x20005, 0, 0, 0, 0) == 1) {
        CHECK(memtrap(0x20004, 0, 0, 0, 0) == 0, 287);
        wait_word(shared.key, 0, 100);
        return 288;
    }
#endif
    *(_Atomic unsigned *)shared.key = 1;
    CHECK(wake(shared.key) == 1, 289);
    struct reply joined = wait_word(shared.tid, 1, 100);
    CHECK(joined.value == 0 || joined.value == -11, 290);
    CHECK(shared.error == 0 && *(volatile unsigned *)shared.tid == 0 &&
              invoke(0x28002, shared.cap, 0, 0, 0, 0, 0).value == 38,
          291);
    CHECK(memtrap(0x22003, shared.memory, (unsigned long)raw, 69 * 4096, 0) ==
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
