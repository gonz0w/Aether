/* SPDX-License-Identifier: BSD-2-Clause */
/* Raw native children: only the parent has a musl TCB or calls libc. */
#include "adapter.h"
#include <sys/auxv.h>
#include <unistd.h>

static unsigned long cap, memory, identity;
static unsigned yields;
static _Atomic unsigned *group_gate;
static _Thread_local volatile unsigned parent_tls = 7;
struct child_data {
    unsigned long base, id, tag;
    _Atomic unsigned *wait_gate;
    _Atomic unsigned gate, error;
    unsigned tid;
};
static struct child_data children[2];
struct descriptor {
    unsigned version, size;
    unsigned long entry, base, bytes, rsp, fs, tid, argument;
    unsigned long tls_base, tls_bytes, parent_tid, reserved;
};
struct observation {
    long status;
    unsigned long waiting;
};
static struct observation observe(unsigned long id)
{
    unsigned long op = 0x2800b, d = 0;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0;
    register unsigned long r9 __asm__("r9") = 0;
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+d"(d)
                         : "D"(cap), "S"(id), "r"(r10), "r"(r8), "r"(r9)
                         : "rcx", "r11", "memory", "cc");
    return (struct observation){(long)op, d};
}
static long requeue(unsigned long grant, unsigned long source,
                    unsigned long destination, unsigned long wakes,
                    unsigned long moves, unsigned long reserved)
{
    unsigned long op = 0x2800d;
    register unsigned long r10 __asm__("r10") = moves;
    register unsigned long r8 __asm__("r8") = destination;
    register unsigned long r9 __asm__("r9") = reserved;
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+D"(grant), "+S"(source), "+d"(wakes),
                           "+r"(r10), "+r"(r8), "+r"(r9)
                         :
                         : "rcx", "r11", "memory", "cc");
    return (long)op;
}
static void step(void)
{
    ++yields;
    memtrap(0x1fffe, 0, 0, 0, 0);
}
static _Noreturn __attribute__((no_stack_protector)) void
child(unsigned long arg)
{
    struct child_data *c = (void *)arg;
    if (memtrap(0x28007, cap, 0, 0, 0) != (long)c->id ||
        observe(c->id).status != -13 ||
        memtrap(0x2800a, cap, c->id, 0, 0) != -13)
        c->error = 1;
    while (!*c->wait_gate)
        if (memtrap(0x28008, cap, (unsigned long)c->wait_gate, 0, 0) != 0 &&
            !*c->wait_gate)
            c->error = 2;
#ifdef THREAD_FAULT
    if (identity == 1 && c == &children[1])
        __asm__ __volatile__("ud2");
#endif
    for (unsigned i = 0; i < 4; ++i) {
        unsigned long got, fs, op = 0x1fffe;
        __asm__ __volatile__(
            "movq %3,%%xmm0; int $0x81; movq %%xmm0,%0; movq %%fs:0,%1"
            : "=r"(got), "=r"(fs), "+a"(op)
            : "r"(c->tag)
            : "xmm0", "memory", "cc");
        if (got != c->tag || fs != c->tag)
            c->error = 3;
    }
    memtrap(0x28001, cap, 17 + (c == &children[1]), 0, 0);
    __builtin_trap();
}
#define CHECK(x, n)                                                            \
    do {                                                                       \
        if (!(x))                                                              \
            return n;                                                          \
    } while (0)
int main(int argc, char **argv)
{
    CHECK(argc == 2 && parent_tls == 7, 180);
    identity = argv[0][11] - '0';
    cap = getauxval(0xa001);
    memory = getauxval(0xa000);
    CHECK(cap && memory, 181);
    long quota = memtrap(0x22000, memory, 0, 0, 0);
    unsigned long old[2] = {0, 0};
    for (unsigned batch = 0; batch < 2; ++batch) {
        struct descriptor requests[2];
        if (batch) {
            long pages = memtrap(0x22001, memory, 8192, 3, 0);
            CHECK(pages > 0, 204);
            group_gate = (void *)pages;
        }
        for (unsigned i = 0; i < 2; ++i) {
            struct child_data *c = &children[i];
            long base = memtrap(0x22001, memory, 3 * 4096, 3, 0);
            CHECK(base > 0, 182);
            c->base = base;
            c->id = identity + 2 + (batch * 2 + i) * 8;
            c->tag = 0xabc000 + c->id;
            c->gate = c->error = 0;
            c->wait_gate = batch ? group_gate : &c->gate;
            c->tid = 99;
            *(unsigned long *)(base + 8192) = c->tag;
            *(unsigned *)(base + 8208) = 99;
            requests[i] = (struct descriptor){1,
                                              96,
                                              (unsigned long)child,
                                              base,
                                              8192,
                                              base + 8184,
                                              base + 8192,
                                              base + 8208,
                                              (unsigned long)c,
                                              base + 8192,
                                              4096,
                                              (unsigned long)&c->tid,
                                              0};
            if (i == 1) {
                struct descriptor overlap = requests[i];
                overlap.base = children[0].base;
                overlap.rsp = overlap.base + 8184;
                CHECK(memtrap(0x28006, cap, (unsigned long)&overlap, 0, 0) ==
                          -22,
                      190);
            }
            CHECK(memtrap(0x28006, cap, (unsigned long)&requests[i], 0, 0) ==
                          (long)c->id &&
                      c->tid == c->id,
                  183);
        }
        CHECK(memtrap(0x28006, cap, (unsigned long)&requests[0], 0, 0) == -28,
              184);
        CHECK(memtrap(0x22002, memory, children[1].base, 3 * 4096, 3) == -13 &&
                  memtrap(0x22003, memory, children[1].base, 3 * 4096, 0) ==
                      -13,
              191);
        for (unsigned spin = 0; spin < 8 && (!observe(children[0].id).waiting ||
                                             !observe(children[1].id).waiting);
             ++spin)
            step();
        CHECK(observe(children[0].id).waiting &&
                  observe(children[1].id).waiting,
              185);
        CHECK(memtrap(0x2800b, cap ^ 0x100, children[1].id, 0, 0) == -13 &&
                  observe(0).status == -22 &&
                  observe(children[1].id + 1).status == -9 &&
                  memtrap(0x2800b, cap, children[1].id, 1, 0) == -22,
              186);
#ifdef STOP_LIVE
        if (identity == 1 && memtrap(0x20005, 0, 0, 0, 0) == 1) {
            memtrap(0x20004, 0, 0, 0, 0);
            for (;;)
                memtrap(0x1fffe, 0, 0, 0, 0);
        }
#endif
#ifdef THREAD_PARENT_EXIT
        break;
#endif
        if (batch) {
            unsigned long key = (unsigned long)group_gate;
            CHECK(memtrap(0x2800c, cap ^ 0x100, key, 1, 0) == -13 &&
                      memtrap(0x2800c, cap, key + 1, 1, 0) == -22 &&
                      memtrap(0x2800c, cap, 0, 1, 0) == -22 &&
                      memtrap(0x2800c, cap, (unsigned long)child & ~3UL, 1,
                              0) == -14 &&
                      memtrap(0x2800c, cap, key, 0x80000000UL, 0) == -22 &&
                      memtrap(0x2800c, cap, key, 1, 1) == -22 &&
                      memtrap(0x2800c, cap, 0x70000000, 0, 0) == -14 &&
                      memtrap(0x2800c, cap, key, 0, 0) == 0 &&
                      observe(children[0].id).waiting &&
                      observe(children[1].id).waiting,
                  202);
            long target = (long)group_gate + 4096;
            CHECK(target > 0, 204);
            CHECK(requeue(cap ^ 0x100, key, target, 1, 1, 0) == -13 &&
                      requeue(cap, key, key, 0, 1, 0) == -22 &&
                      requeue(cap, key, target + 1, 1, 1, 0) == -22 &&
                      requeue(cap, key, target, 0x80000000UL, 1, 0) == -22 &&
                      requeue(cap, key, target, 1, 0x80000000UL, 0) == -22 &&
                      requeue(cap, key, target, 1, 1, 1) == -22 &&
                      requeue(cap, key, 0x70000000, 1, 1, 0) == -14 &&
                      requeue(cap, key, (unsigned long)child & ~3UL, 1, 1, 0) ==
                          -14 &&
                      requeue(cap, key, target, 0, 0, 0) == 0 &&
                      observe(children[0].id).waiting &&
                      observe(children[1].id).waiting,
                  204);
            CHECK(memtrap(0x22002, memory, key, 4096, 3) == -13, 205);
            CHECK(requeue(cap, key, target, 0, 2, 0) == 2 &&
                      memtrap(0x22002, memory, target, 4096, 3) == -13 &&
                      memtrap(0x22003, memory, target, 4096, 0) == -13,
                  205);
            CHECK(memtrap(0x22002, memory, key, 4096, 0) == 0 &&
                      memtrap(0x22002, memory, key, 4096, 3) == 0 &&
                      memtrap(0x2800c, cap, key, 1, 0) == 0 &&
                      observe(children[0].id).waiting &&
                      observe(children[1].id).waiting,
                  206);
#ifdef STOP_REQUEUED
            if (identity == 1 && memtrap(0x20005, 0, 0, 0, 0) == 1) {
                memtrap(0x20004, 0, 0, 0, 0);
                for (;;)
                    memtrap(0x1fffe, 0, 0, 0, 0);
            }
#endif
            CHECK(requeue(cap, target, key, 0, 1, 0) == 1 &&
                      memtrap(0x22003, memory, target, 4096, 0) == -13 &&
                      requeue(cap, target, key, 0, 1, 0) == 1 &&
                      memtrap(0x22003, memory, target, 4096, 0) == 0,
                  207);
            *group_gate = 1;
            CHECK(memtrap(0x2800c, cap, key, 1, 0) == 1 &&
                      observe(children[0].id).waiting +
                              observe(children[1].id).waiting ==
                          1,
                  201);
            CHECK(memtrap(0x2800c, cap, key, 1, 0) == 1 &&
                      memtrap(0x2800c, cap, key, 0x7fffffff, 0) == 0,
                  203);
        }
        for (unsigned i = 0; i < 2; ++i) {
            struct child_data *c = &children[i];
            if (!batch) {
                CHECK(memtrap(0x2800a, cap, c->id, 0, 0) == -16, 187);
                c->gate = 1;
                CHECK(memtrap(0x28004, cap, (unsigned long)&c->gate, 0, 0) == 1,
                      188);
            }
            for (unsigned spin = 0; spin < 8 && observe(c->id).status == 0;
                 ++spin)
                step();
            CHECK(observe(c->id).status == 18 + (long)i && !c->error &&
                      *(unsigned *)(c->base + 8208) == 0,
                  189);
            if (i == 0 && !batch)
                CHECK(observe(children[1].id).status == 0 &&
                          observe(children[1].id).waiting,
                      192);
            if (batch)
                CHECK(memtrap(0x2800a, cap, old[i], 0, 0) == -9, 193);
            CHECK(memtrap(0x2800a, cap, c->id, 0, 0) == 0, 194);
            old[i] = c->id;
            CHECK(memtrap(0x22003, memory, c->base, 3 * 4096, 0) == 0, 195);
        }
        if (batch)
            CHECK(memtrap(0x22003, memory, (unsigned long)group_gate, 4096,
                          0) == 0,
                  207);
        CHECK(observe(old[0]).status == -2 &&
                  memtrap(0x22000, memory, 0, 0, 0) == quota,
              196);
    }
#ifndef THREAD_PARENT_EXIT
    CHECK(memtrap(0x28006, cap, 0, 0, 0) == -28, 197);
#endif
    CHECK(yields <= 64, 198);
    while (yields < 64)
        step();
    CHECK(write(1, "AETHER MUSL NATIVE PASS\n", 24) == 16, 199);
    CHECK(write(1, &"AETHER MUSL NATIVE PASS\n"[16], 8) == 8, 200);
    return 0;
}
