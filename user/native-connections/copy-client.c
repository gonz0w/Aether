/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-memory/adapter.h"
#include <sys/auxv.h>
#include <unistd.h>
#ifdef COPY_SIGNALS
#include <signal.h>
#include <setjmp.h>
#include <string.h>
#endif
#ifdef COPY_REBIND
#include <sys/mman.h>
#include <errno.h>
int copy_rebind(unsigned long, unsigned long, unsigned long, unsigned long *,
                unsigned long *);
#endif
static _Thread_local volatile unsigned cookie = 23;
#ifdef COPY_SIGNALS
extern void __restore_rt(void);
static volatile unsigned signal_count, signal_bad;
static uint64_t signal_previous;
static const uint64_t held_mask =
    UINT64_MAX & ~((UINT64_C(1) << 8) | (UINT64_C(1) << 18));
static void copy_signal(int signo)
{
    if (signo != 12)
        signal_bad = 1;
    ++signal_count;
}
static int signal_prepare(void)
{
    uint64_t empty[4] = {0}, observed[4];
    for (unsigned i = 0; i < 3; ++i) {
        unsigned signo = i == 0 ? 12 : i == 1 ? 14 : 64;
        if (memtrap(0x29001, signo, 0, (uintptr_t)observed, 8) ||
            memcmp(empty, observed, sizeof empty))
            return 0;
    }
    uint64_t record[4] = {(uintptr_t)copy_signal, 0x04000000,
                          (uintptr_t)__restore_rt, 4};
    uint64_t ignored[4] = {1, 0x04000000, 23, 16};
    if (memtrap(0x29001, 12, (uintptr_t)record, 0, 8) ||
        memtrap(0x29001, 14, (uintptr_t)ignored, 0, 8) ||
        memtrap(0x29001, 64, (uintptr_t)ignored, 0, 8) ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&held_mask,
                (uintptr_t)&signal_previous, 8) ||
        memtrap(0x29002, 12, 0, 0, 0) || memtrap(0x29002, 12, 0, 0, 0) ||
        signal_count)
        return 0;
    return 1;
}
static int signal_check(int child)
{
    uint64_t expected[4] = {(uintptr_t)copy_signal, 0x04000000,
                            (uintptr_t)__restore_rt, 4};
    uint64_t ignored[4] = {1, 0x04000000, 23, 16};
    uint64_t empty[4] = {0}, observed[4], mask = 0;
    if (memtrap(0x29001, 12, 0, (uintptr_t)observed, 8) ||
        memcmp(expected, observed, sizeof expected) ||
        memtrap(0x29001, 14, 0, (uintptr_t)observed, 8) ||
        memcmp(ignored, observed, sizeof ignored) ||
        memtrap(0x29001, 64, 0, (uintptr_t)observed, 8) ||
        memcmp(ignored, observed, sizeof ignored) ||
        memtrap(0x29001, 13, 0, (uintptr_t)observed, 8) ||
        memcmp(empty, observed, sizeof empty))
        return 247;
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) || mask != held_mask ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&signal_previous, 0, 8) ||
        signal_count != (child ? 0u : 1u) || signal_bad ||
        memtrap(0x29002, 0, 0, 0, 0) || signal_count != (child ? 0u : 1u))
        return 248;
    if (child &&
        (memtrap(0x29001, 14, (uintptr_t)empty, 0, 8) ||
         memtrap(0x29002, 12, 0, 0, 0) || signal_count != 1 || signal_bad))
        return 248;
    return 0;
}
#endif

static int byte_io(unsigned long cap, unsigned char *b, int write)
{
    for (unsigned i = 0; i < 100000; ++i) {
        long n = memtrap(write ? 0x24002 : 0x24001, cap, (uintptr_t)b, 1, 0);
        if (n == 1)
            return 1;
        if (n != -11)
            return 0;
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
    return 0;
}
static int copy_run(void)
{
    unsigned long old_memory = getauxval(0xa000);
    unsigned long input = getauxval(0xa001), output = getauxval(0xa002);
    long parent_pid = memtrap(0x10027, 0, 0, 0, 0);
    long allocated = memtrap(0x22001, old_memory, 16384, 3, 0);
    if (allocated < 0 || parent_pid <= 0 || cookie != 23)
        return 210;
    if (gettid() != parent_pid)
        return 230;
    volatile unsigned char *p = (void *)(uintptr_t)allocated;
    p[0] = 0x41;
    p[4096] = 0x42;
    p[8192] = 0x43;
    if (memtrap(0x100da, allocated + 12288, 0, 0, 0) != parent_pid)
        return 230;
    if (memtrap(0x22003, old_memory, allocated + 4096, 4096, 0) ||
        memtrap(0x22002, old_memory, allocated + 8192, 4096, 0))
        return 211;
    if (memtrap(0x23006, 0, 0, 0, 0) != -13)
        return 212;
#ifdef COPY_SIGNALS
    if (!signal_prepare())
        return 246;
#endif
    volatile unsigned stack_cookie = 41;
    unsigned long op = 0x23003, memory = 0, reader = 0, writer = 0;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    const uint64_t fx_seed = 0x0123456789abcdefULL;
    uint64_t fx_after;
    /* All result registers are explicit. The memory clobber covers the kernel
       boundary; child stores use its copied stack at the same virtual address.
     */
    __asm__ __volatile__(
        "movq %[seed], %%xmm15; int $0x81; movq %%xmm15, %[saved]"
        : "+a"(op), "+D"(memory), "+S"(reader), "+d"(writer), "+r"(r10),
          "+r"(r8), "+r"(r9), [saved] "=m"(fx_after)
        : [seed] "m"(fx_seed)
        : "rcx", "r11", "xmm15", "memory");
    if (cookie != 23 || stack_cookie != 41 || fx_after != fx_seed)
        return 214;
#ifdef COPY_SIGNALS
    if ((long)op == -95)
        return 246;
#endif
    unsigned char reply;
    if (op == 0) {
#ifdef COPY_SIGNALS
        int status = signal_check(1);
        if (status)
            return status;
#endif
        if (p[0] != 0x41)
            return 214;
        if (memory == old_memory ||
            memtrap(0x22000, old_memory, 0, 0, 0) != -13 ||
            memtrap(0x24001, input, 0, 0, 0) != -13 ||
            memtrap(0x24002, output, 0, 0, 0) != -13 ||
            memtrap(0x22000, memory, 0, 0, 0) < 0 ||
            memtrap(0x10027, 0, 0, 0, 0) != parent_pid + 2 ||
            memtrap(0x1006e, 0, 0, 0, 0) != parent_pid)
            return 216;
        cookie = 73;
        stack_cookie = 83;
        p[0] = 0x61;
        if (memtrap(0x22002, memory, allocated + 8192, 4096, 3))
            return 218;
        if (p[8192] != 0x43 ||
            memtrap(0x22003, memory, allocated + 4096, 4096, 0) != -12)
            return 219;
        p[8192] = 0x63;
        long hole = memtrap(0x22001, memory, 4096, 3, 0);
        if (hole != allocated + 4096)
            return 220;
        for (unsigned i = 0; i < 4096; ++i)
            if (((volatile unsigned char *)(uintptr_t)hole)[i])
                return 221;
        /* Copied bytes retain the parent cache, but not its kernel
         * registration. */
        if (gettid() != parent_pid ||
            memtrap(0x22003, memory, allocated + 12288, 4096, 0) ||
            memtrap(0x100da, (uintptr_t)&stack_cookie, 0, 0, 0) !=
                parent_pid + 2 ||
            gettid() != parent_pid)
            return 231;
#ifdef COPY_REBIND
        /* Failed validation leaves all known cached state untouched. */
        if (copy_rebind(old_memory, reader, writer, &input, &output) ||
            copy_rebind(memory, writer, reader, &input, &output) ||
            getauxval(0xa000) != old_memory || gettid() != parent_pid ||
            input != getauxval(0xa001) || output != getauxval(0xa002) ||
            !copy_rebind(memory, reader, writer, &input, &output))
            return 239;
        if (getauxval(0xa000) != memory || getauxval(0xa001) != reader ||
            getauxval(0xa002) != writer)
            return 240;
        if (gettid() != parent_pid + 2)
            return 241;
        if (input != reader || output != writer)
            return 242;
        unsigned char *mapped = mmap(0, 4096, PROT_READ | PROT_WRITE,
                                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (mapped == MAP_FAILED)
            return 243;
        mapped[0] = 0x67;
        if (mprotect(mapped, 4096, PROT_NONE) ||
            mprotect(mapped, 4096, PROT_READ | PROT_WRITE) ||
            mapped[0] != 0x67 || munmap(mapped, 4096))
            return 243;
        reader = input;
        writer = output;
#endif
        reply = 0x72;
        if (!byte_io(writer, &reply, 1) || !byte_io(reader, &reply, 0) ||
            reply != 0x62)
            return 223;
        if (cookie != 73 || stack_cookie != 83 || p[0] != 0x61 ||
            p[8192] != 0x63)
            return 228;
        if (memtrap(0x22003, memory, hole, 4096, 0) ||
            memtrap(0x22003, memory, allocated, 4096, 0) ||
            memtrap(0x22003, memory, allocated + 8192, 4096, 0))
            return 222;
        return 72;
    }
#ifdef COPY_ROLLBACK
    if ((long)op != -11)
        return 224;
#else
    if ((long)op != parent_pid + 2 || !byte_io(input, &reply, 0) ||
        reply != 0x61)
        return 225;
#endif
#ifdef COPY_SIGNALS
    int status = signal_check(0);
    if (status)
        return status;
#endif
    if (cookie != 23 || stack_cookie != 41 || p[0] != 0x41 ||
        memtrap(0x10027, 0, 0, 0, 0) != parent_pid)
        return 215;
    if (memtrap(0x22002, old_memory, allocated + 8192, 4096, 3) ||
        p[8192] != 0x43)
        return 226;
    /* Failed replacement must leave the original parent page pinned. */
    if (memtrap(0x22003, old_memory, allocated + 12288, 4096, 0) != -13 ||
        memtrap(0x100da, 0, 0, 0, 0) != -14 ||
        memtrap(0x22003, old_memory, allocated + 12288, 4096, 0) != -13 ||
        memtrap(0x100da, (uintptr_t)&stack_cookie, 0, 0, 0) != parent_pid ||
        memtrap(0x22003, old_memory, allocated + 12288, 4096, 0))
        return 232;
#ifdef COPY_REBIND
    if (getauxval(0xa000) != old_memory || getauxval(0xa001) != input ||
        getauxval(0xa002) != output || gettid() != parent_pid)
        return 244;
#endif
    cookie = 63;
    stack_cookie = 51;
    p[0] = 0x51;
    p[8192] = 0x53;
    reply = 0x71;
    if (!byte_io(output, &reply, 1))
        return 227;
#ifndef COPY_ROLLBACK
    if (!byte_io(input, &reply, 0) || reply != 0x63)
        return 229;
#endif
    if (memtrap(0x22003, old_memory, allocated, 4096, 0) ||
        memtrap(0x22003, old_memory, allocated + 8192, 4096, 0))
        return 226;
    return 71;
}

#ifdef COPY_SIGNAL_HANDLER
static volatile int signal_result = 249;
#ifdef COPY_HANDLER_ESCAPE
static sigjmp_buf handler_escape;
#endif
#ifdef COPY_HANDLER_INVALID
static volatile unsigned frame_rejections;
__attribute__((naked)) static long attempt_return(void *payload)
{
    __asm__ __volatile__("mov %rsp, %r11\n"
                         "mov %rdi, %rsp\n"
                         "mov $0x1000f, %eax\n"
                         "int $0x81\n"
                         "mov %r11, %rsp\n"
                         "ret\n");
}
#endif
__attribute__((naked)) static int invoke_copy_handler(void)
{
    __asm__ __volatile__("push %r12\n"
                         "movabs $0x123456789abcdef, %r12\n"
                         "movabs $0x76543210abcdef01, %rax\n"
                         "movq %rax, %xmm14\n"
                         "mov $10, %edi\n"
                         "xor %esi, %esi\n"
                         "xor %edx, %edx\n"
                         "xor %r10d, %r10d\n"
                         "xor %r8d, %r8d\n"
                         "xor %r9d, %r9d\n"
                         "mov $0x29002, %eax\n"
                         "int $0x81\n"
                         "test %rax, %rax\n"
                         "jnz 1f\n"
                         "movabs $0x123456789abcdef, %rax\n"
                         "cmp %rax, %r12\n"
                         "jne 1f\n"
                         "movq %xmm14, %rdx\n"
                         "movabs $0x76543210abcdef01, %rax\n"
                         "cmp %rax, %rdx\n"
                         "jne 1f\n"
                         "xor %eax, %eax\n"
                         "pop %r12\n"
                         "ret\n"
                         "1: mov $1, %eax\n"
                         "pop %r12\n"
                         "ret\n");
}
static void copying_handler(int signo)
{
    if (signo == 10)
        signal_result = copy_run();
#if defined(COPY_HANDLER_INVALID) || defined(COPY_HANDLER_REGISTER) ||         \
    defined(COPY_HANDLER_FP)
    unsigned char *payload = (unsigned char *)__builtin_frame_address(0) + 16;
    if (signal_result == 72) {
#ifdef COPY_HANDLER_INVALID
        uint64_t before = 0, after = 0;
        if (memtrap(0x1000e, 0, 0, (uintptr_t)&before, 8)) {
            signal_result = 250;
            return;
        }
#ifndef COPY_HANDLER_SKIP_INVALID
        payload[8] = 1;
#endif
        if (attempt_return(payload) != -22 ||
            memtrap(0x1000e, 0, 0, (uintptr_t)&after, 8) || after != before) {
            signal_result = 250;
            return;
        }
        payload[8] = 0;
        frame_rejections = 1;
#endif
#ifdef COPY_HANDLER_REGISTER
        memset(payload + 40, 0, 8); /* Payload.cpu.r12 */
#endif
#ifdef COPY_HANDLER_FP
        memset(payload + 592, 0, 8); /* Payload.fp.XMM14 low half */
#endif
    }
#endif
    __asm__ __volatile__("pxor %%xmm14, %%xmm14" : : : "xmm14");
#ifdef COPY_HANDLER_ESCAPE
    siglongjmp(handler_escape, 1);
#endif
}
#endif
int main(void)
{
#ifdef COPY_SIGNAL_HANDLER
    uint64_t seed = 16, observed = 0;
    uint64_t record[4] = {(uintptr_t)copying_handler, 0x04000000,
                          (uintptr_t)__restore_rt, 4};
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&seed, 0, 8) ||
        memtrap(0x29001, 10, (uintptr_t)record, 0, 8))
        return 249;
#ifdef COPY_HANDLER_ESCAPE
#ifdef COPY_HANDLER_ESCAPE_MASK
    int escaped = sigsetjmp(handler_escape, 0);
#else
    int escaped = sigsetjmp(handler_escape, 1);
#endif
    if (!escaped && invoke_copy_handler())
        return 250;
#else
    if (invoke_copy_handler())
        return 250;
#endif
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) || observed != seed)
        return 249;
#ifdef COPY_HANDLER_INVALID
    if (frame_rejections != (signal_result == 72 ? 1u : 0u))
        return 250;
#endif
#ifdef COPY_HANDLER_ESCAPE
    if (!escaped || memtrap(0x29002, 12, 0, 0, 0) || signal_count != 2 ||
        signal_bad)
        return 250;
#endif
    return signal_result;
#else
    return copy_run();
#endif
}
