/* SPDX-License-Identifier: BSD-2-Clause */
#include "transport.h"
#ifdef STARTUP_IDENTITY
#include <sys/syscall.h>
#endif
int dash_startup_probe(void);
static _Thread_local volatile unsigned startup_cookie = 23;
static void unsupported_handler(int signal) { (void)signal; }
#if defined(STARTUP_DUP_TEST) || defined(STARTUP_DUP_SELF) ||                  \
    defined(STARTUP_DUP_FLAGS) || defined(STARTUP_DUP_LEAK)
#define DUP_TEST
static int duplicate_checks(void)
{
    int saved = fcntl(2, F_DUPFD_CLOEXEC, 10);
    if (saved != 10 || dup2(saved, saved) != saved ||
        fcntl(saved, F_GETFD) != FD_CLOEXEC)
        return 70;
    if (dup2(-1, 2) != -1 || errno != EBADF || dup2(16, 2) != -1 ||
        errno != EBADF || dup2(9, 2) != -1 || errno != EBADF ||
        dup2(0, 16) != -1 || errno != EBADF || dup2(0, -1) != -1 ||
        errno != EBADF || fcntl(2, F_GETFD))
        return 71;
    /* Save/replace/restore stdout without losing its original remote binding.
     */
    if (dup2(1, 3) != 3 || dup2(0, 1) != 1 || write(1, "!", 1) != -1 ||
        errno != EACCES || dup2(3, 1) != 1 || fcntl(1, F_GETFD) || close(3))
        return 71;
    /* Replace the final stderr alias; the owner must observe exactly one close.
     */
    if (close(2) || dup2(0, saved) != saved || fcntl(saved, F_GETFD) ||
        close(saved))
        return 71;
    /* Exact replacement must work even when every descriptor slot is occupied.
     */
    for (int fd = 2; fd < 16; fd++)
        if (fcntl(0, F_DUPFD_CLOEXEC, fd) != fd)
            return 72;
    if (fcntl(0, F_DUPFD, 0) != -1 || errno != EMFILE || dup2(0, 15) != 15 ||
        fcntl(15, F_GETFD))
        return 72;
    for (int fd = 2; fd < 16; fd++)
        if (close(fd))
            return 72;
    return 0;
}
#endif
/* Actual linked musl helpers must observe the same mask as the public facade.
 */
void __block_all_sigs(void *);
void __block_app_sigs(void *);
void __restore_sigs(void *);
static int mask_checks(void)
{
    uint64_t original, observed = 0, requested = UINT64_C(1) << 9;
    const uint64_t allowed =
        UINT64_MAX & ~((UINT64_C(1) << 8) | (UINT64_C(1) << 18));
    sigset_t public_mask;
    if (memtrap(0x1000e, 999, 0, (uintptr_t)&original, 8) || original)
        return 73;
#ifndef STARTUP_MASK_SKIP_INTERNAL
    __block_all_sigs(&original);
#endif
    if (sigprocmask(SIG_BLOCK, 0, &public_mask))
        return 73;
    memcpy(&observed, &public_mask, 8);
    if (observed != allowed)
        return 73;
    __restore_sigs(&original);
    memset(&public_mask, 0, sizeof public_mask);
    memcpy(&public_mask, &requested, 8);
    if (sigprocmask(SIG_SETMASK, &public_mask, 0) ||
        memtrap(0x1000e, 999, 0, (uintptr_t)&observed, 8) ||
        observed != requested)
        return 73;
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&requested, 0, 8) ||
        sigprocmask(SIG_BLOCK, 0, &public_mask))
        return 73;
    memcpy(&observed, &public_mask, 8);
    if (observed != requested)
        return 73;
    __block_app_sigs(&observed);
    if (observed != requested ||
        memtrap(0x1000e, 999, 0, (uintptr_t)&observed, 8) ||
        observed != (UINT64_C(0xfffffffc7fffffff) & allowed))
        return 73;
    __restore_sigs(&requested);
    /* Invalid outputs and size/how must not commit the requested zero mask. */
    uint64_t zero = 0;
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&zero, 1, 8) != -EFAULT ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&zero, UINTPTR_MAX - 3, 8) !=
            -EFAULT ||
        memtrap(0x1000e, SIG_SETMASK, UINTPTR_MAX - 3, (uintptr_t)&observed,
                8) != -EFAULT ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&zero, (uintptr_t)&observed,
                16) != -EINVAL ||
        memtrap(0x1000e, 3, (uintptr_t)&zero, (uintptr_t)&observed, 8) !=
            -EINVAL)
        return 74;
    if (memtrap(0x1000e, 999, 0, (uintptr_t)&observed, 8) ||
        observed != requested)
        return 74;
    /* Input/output alias: old bytes must not replace the snapped new input. */
    observed = 0;
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&observed,
                (uintptr_t)&observed, 8) ||
        observed != requested || sigprocmask(SIG_BLOCK, 0, &public_mask))
        return 74;
    memcpy(&observed, &public_mask, 8);
    return observed ? 74 : 0;
}
#ifdef STARTUP_FRAME_TEST
#include <setjmp.h>
#ifdef STARTUP_FRAME_PREEMPT
#define FRAME_ITERATIONS 10000
#else
#define FRAME_ITERATIONS 3
#endif
extern void __restore_rt(void);
static jmp_buf frame_escape;
static volatile unsigned frame_calls;
static volatile uint64_t frame_mask;
static void frame_handler(int signal)
{
    uint64_t mask = 0;
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8))
        return;
    frame_mask = mask;
#ifndef STARTUP_FRAME_SKIP
    frame_calls++;
#endif
    __asm__ __volatile__("pxor %%xmm15, %%xmm15" : : : "xmm15");
#ifdef STARTUP_FRAME_PREEMPT
    memtrap(0x1fffe, 0, 0, 0, 0);
#endif
    if (signal == 12)
        longjmp(frame_escape, 1);
}
#if defined(STARTUP_FRAME_ADVERSARIAL) || defined(STARTUP_FRAME_MEMORY)
#ifdef STARTUP_FRAME_ADVERSARIAL
static unsigned char forged_frame[736] __attribute__((aligned(16)));
static unsigned char before_frame[720];
static volatile unsigned frame_rejections;
#endif
/* On rejection the kernel preserves R11 and returns on the supplied user RSP.
 * A valid frame instead resumes its saved continuation; it does not return
 * here.
 */
__attribute__((naked)) static long attempt_frame(void *payload)
{
    __asm__ __volatile__("mov %rsp, %r11\n"
                         "mov %rdi, %rsp\n"
                         "mov $0x1000f, %eax\n"
                         "int $0x81\n"
                         "mov %r11, %rsp\n"
                         "ret\n");
}
#endif
#ifdef STARTUP_FRAME_MEMORY
static volatile unsigned mapping_rejections;
static void mapping_handler(int signal)
{
    (void)signal;
    const unsigned char *payload =
        (const unsigned char *)__builtin_frame_address(0) + 16;
    unsigned long cap = getauxval(0xa000);
    uint64_t initial = 0, observed = 0;
    if (!cap || memtrap(0x1000e, 0, 0, (uintptr_t)&initial, 8) ||
        memtrap(0x22001, 0, 4096, 3, 0) != -EACCES)
        return;
    long address = memtrap(0x22001, cap, 4096, 3, 0);
    if (address < 0)
        return;
    unsigned char *page = (unsigned char *)address;
    memcpy(page, payload, 720);
    for (unsigned i = 0; i < 3; i++) {
#ifndef STARTUP_FRAME_MEMORY_WRITABLE
        if (i < 2 ? memtrap(0x22002, cap, address, 4096, i == 0 ? 1 : 0)
                  : memtrap(0x22003, cap, address, 4096, 0))
            return;
#endif
        if (attempt_frame(page) != -EINVAL ||
            memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) ||
            observed != initial)
            return;
        if (i < 2) {
            if (memtrap(0x22002, cap, address, 4096, 3) ||
                memcmp(page, payload, 720))
                return;
        } else {
            if (memtrap(0x22001, cap, 4096, 3, 0) != address)
                return;
            for (unsigned j = 0; j < 4096; j++)
                if (page[j])
                    return;
        }
        mapping_rejections++;
    }
    if (memtrap(0x22003, cap, address, 4096, 0))
        mapping_rejections = 0;
}
#endif
#ifdef STARTUP_FRAME_MEMORY_TARGETS
static unsigned char target_frame[720] __attribute__((aligned(16)));
static unsigned char target_before[720];
static volatile uintptr_t target_rsp __attribute__((used));
static volatile uintptr_t target_rip __attribute__((used));
static volatile unsigned target_rejections;
/* A valid alternate stack must resume without a C prologue or stack access. */
__attribute__((naked)) static void target_resume(void)
{
    __asm__ __volatile__("mov target_rsp(%rip), %rsp\n"
                         "jmp *target_rip(%rip)\n");
}
static void target_handler(int signal)
{
    (void)signal;
    const unsigned char *payload =
        (const unsigned char *)__builtin_frame_address(0) + 16;
    unsigned long cap = getauxval(0xa000);
    uint64_t initial = 0, observed = 0;
    memcpy((void *)&target_rsp, payload + 176, 8);
    memcpy((void *)&target_rip, payload + 152, 8);
    if (!cap || memtrap(0x1000e, 0, 0, (uintptr_t)&initial, 8))
        return;
    /* This grant cannot mutate the fixed code or live stack mappings. */
    for (unsigned i = 0; i < 2; i++) {
        uintptr_t fixed = (i ? target_rsp - 1 : target_rip) & ~(uintptr_t)4095;
        if (memtrap(0x22002, cap, fixed, 4096, 1) != -EACCES ||
            memtrap(0x22003, cap, fixed, 4096, 0) != -EACCES)
            return;
    }
    long address = memtrap(0x22001, cap, 4096, 3, 0);
    if (address < 0)
        return;
    for (unsigned i = 0; i < 6; i++) {
        memcpy(target_frame, payload, 720);
        uintptr_t stack = address + 4096, code = (uintptr_t)target_resume;
        if (i < 3) {
            memcpy(target_frame + 176, &stack, 8);
            memcpy(target_frame + 152, &code, 8);
#ifndef STARTUP_FRAME_MEMORY_TARGETS_STACK_VALID
            if (i < 2 ? memtrap(0x22002, cap, address, 4096, i == 0 ? 1 : 0)
                      : memtrap(0x22003, cap, address, 4096, 0))
                return;
#endif
        } else {
#ifndef STARTUP_FRAME_MEMORY_TARGETS_CODE_VALID
            memcpy(target_frame + 152, &address, 8);
#endif
            if (i == 4 && memtrap(0x22002, cap, address, 4096, 0))
                return;
            if (i == 5 && memtrap(0x22003, cap, address, 4096, 0))
                return;
        }
        memcpy(target_before, target_frame, 720);
        if (attempt_frame(target_frame) != -EINVAL ||
            memcmp(target_before, target_frame, 720) ||
            memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) ||
            observed != initial)
            return;
        if (i == 2 || i == 5) {
            if (memtrap(0x22001, cap, 4096, 3, 0) != address)
                return;
        } else if (memtrap(0x22002, cap, address, 4096, 3)) {
            return;
        }
        target_rejections++;
    }
    if (memtrap(0x22003, cap, address, 4096, 0))
        target_rejections = 0;
}
#endif
#ifdef STARTUP_FRAME_ADVERSARIAL
static void adversarial_handler(int signal)
{
    (void)signal;
    /* The saved RBP and return slot precede the aligned native payload. */
    const unsigned char *payload =
        (const unsigned char *)__builtin_frame_address(0) + 16;
    static const struct {
        unsigned offset;
        uint64_t value;
    } corruptions[] = {{0, 0},
                       {8, 1},
                       {160, 8},
                       {184, 16},
                       {168, 0x3202},
                       {168, 0x302},
                       {168, 0x20202},
                       {168, 2},
                       {152, (uintptr_t)forged_frame},
                       {176, UINT64_C(1) << 47},
                       {232, UINT64_C(0xffffffff80001f80)}};
    uint64_t initial = 0, observed = 0;
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&initial, 8))
        return;
    for (unsigned i = 0; i < sizeof corruptions / sizeof corruptions[0]; i++) {
        memcpy(forged_frame, payload, sizeof before_frame);
#ifndef STARTUP_FRAME_UNCORRUPTED
        memcpy(forged_frame + corruptions[i].offset, &corruptions[i].value, 8);
#endif
        memcpy(before_frame, forged_frame, sizeof before_frame);
        if (attempt_frame(forged_frame) != -EINVAL ||
            memcmp(before_frame, forged_frame, sizeof before_frame) ||
            memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) ||
            observed != initial)
            return;
        frame_rejections++;
    }
    /* Isolate alignment: valid payload bytes begin at the misaligned address.
     */
    memcpy(forged_frame + 1, payload, sizeof before_frame);
    memcpy(before_frame, forged_frame + 1, sizeof before_frame);
    if (attempt_frame(forged_frame + 1) == -EINVAL &&
        !memcmp(before_frame, forged_frame + 1, sizeof before_frame) &&
        !memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) && observed == initial)
        frame_rejections++;
}
#endif
#ifdef STARTUP_FRAME_STATE
extern int frame_register_checks(void);
static volatile unsigned nested_inner, nested_outer, nested_error;
static void nested_child(int signal)
{
    uint64_t mask = 0;
    if (signal != 12 || memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) ||
        mask != (4 | 8 | 512 | 16 | 2048))
        nested_error = 1;
#ifndef STARTUP_FRAME_STATE_NESTED
    nested_inner++;
#endif
}
static void nested_parent(int signal)
{
    unsigned char saved[720];
    const unsigned char *payload =
        (const unsigned char *)__builtin_frame_address(0) + 16;
    uint64_t mask = 0;
    if (signal != 10 || memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) ||
        mask != (4 | 8 | 512))
        nested_error = 1;
    memcpy(saved, payload, sizeof saved);
    if (memtrap(0x29000, (uintptr_t)nested_child, (uintptr_t)__restore_rt, 12,
                16) ||
        memcmp(saved, payload, sizeof saved) ||
        memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) || mask != (4 | 8 | 512))
        nested_error = 1;
    nested_outer++;
}
static int state_checks(void)
{
    uint64_t prior = 0, mask = 4, observed = 0;
    if (memtrap(0x1000e, 2, (uintptr_t)&mask, (uintptr_t)&prior, 8))
        return 79;
    for (unsigned i = 1; i <= 2; i++) {
        if (memtrap(0x29000, (uintptr_t)nested_parent, (uintptr_t)__restore_rt,
                    10, 8) ||
            nested_inner != i || nested_outer != i || nested_error ||
            memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) || observed != mask)
            return 79;
    }
    if (memtrap(0x1000e, 2, (uintptr_t)&prior, 0, 8))
        return 79;
    return frame_register_checks() ? 80 : 0;
}
#endif
static int frame_checks(void)
{
    uint64_t original = 0, mask = 4, observed = 0;
    if (memtrap(0x1000e, 2, (uintptr_t)&mask, (uintptr_t)&original, 8))
        return 75;
    for (unsigned i = 0; i < FRAME_ITERATIONS; i++) {
        unsigned char expected[16], actual[16];
        memset(expected, 0xa5, sizeof expected);
        __asm__ __volatile__("movdqu %0, %%xmm15" : : "m"(expected) : "xmm15");
#ifdef STARTUP_FRAME_PREEMPT
        memtrap(0x1fffe, 0, 0, 0, 0);
#endif
        long status = memtrap(0x29000, (uintptr_t)frame_handler,
                              (uintptr_t)__restore_rt, 10, 8);
        __asm__ __volatile__("movdqu %%xmm15, %0" : "=m"(actual));
        if (status)
            return 82;
        if (frame_calls != i + 1)
            return 75;
        if (frame_mask != (4 | 8 | 512))
            return 83;
        if (memcmp(expected, actual, sizeof actual))
            return 84;
        if (memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8))
            return 85;
        if (observed != mask)
            return 86;
    }
    if (!setjmp(frame_escape)) {
        memtrap(0x29000, (uintptr_t)frame_handler, (uintptr_t)__restore_rt, 12,
                0);
        return 76;
    }
    if (frame_calls != FRAME_ITERATIONS + 1 ||
        memtrap(0x1000e, 2, (uintptr_t)&mask, 0, 8) ||
        memtrap(0x29000, (uintptr_t)frame_handler, (uintptr_t)__restore_rt, 10,
                0) ||
        frame_calls != FRAME_ITERATIONS + 2)
        return 76;
    if (memtrap(0x29000, 0, (uintptr_t)__restore_rt, 10, 0) != -EINVAL ||
        memtrap(0x29000, (uintptr_t)frame_handler, (uintptr_t)&mask, 10, 0) !=
            -EINVAL ||
        memtrap(0x29000, (uintptr_t)frame_handler, (uintptr_t)__restore_rt, 9,
                0) != -EINVAL ||
        memtrap(0x1000f, 0, 0, 0, 0) != -EINVAL ||
        frame_calls != FRAME_ITERATIONS + 2 ||
        memtrap(0x1000e, 2, (uintptr_t)&original, 0, 8))
        return 77;
#ifdef STARTUP_FRAME_ADVERSARIAL
    if (memtrap(0x29000, (uintptr_t)adversarial_handler,
                (uintptr_t)__restore_rt, 10, 0) ||
        frame_rejections != 12)
        return 78;
#endif
#ifdef STARTUP_FRAME_MEMORY
    if (memtrap(0x29000, (uintptr_t)mapping_handler, (uintptr_t)__restore_rt,
                10, 8) ||
        mapping_rejections != 3)
        return 81;
#endif
#ifdef STARTUP_FRAME_MEMORY_TARGETS
    if (memtrap(0x29000, (uintptr_t)target_handler, (uintptr_t)__restore_rt, 10,
                8) ||
        target_rejections != 6)
        return 87;
#endif
#ifdef STARTUP_FRAME_STATE
    return state_checks();
#else
    return 0;
#endif
}
#endif
#ifdef STARTUP_GUARD_LIVE
#ifdef STARTUP_GUARD_JUMP
#include <setjmp.h>
static sigjmp_buf startup_jump;
static char startup_jump_bytes[11];
#endif
extern void __restore_rt(void);
static unsigned startup_live_armed;
static volatile unsigned startup_live_count, startup_live_bad;
static int startup_live_before_restore(void)
{
    if (!startup_live_armed)
        return 0;
    startup_live_armed = 0;
#ifdef STARTUP_GUARD_POISON_REVIVE
    startup_fds[10].present = 1; /* Negative fixture: revive a consumed alias. */
#endif
    if (memtrap(0x29002, 10, 0, 0, 0) || startup_live_count)
        startup_live_bad = 1;
    return 1;
}
static void startup_live_handler(int signal)
{
    int saved = errno;
    uint64_t mask = 0;
    ++startup_live_count;
    if (signal != 10 || memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) ||
        mask != 512 || fcntl(1, F_GETFD))
        startup_live_bad = 1;
#ifdef STARTUP_GUARD_POISON
#ifdef STARTUP_GUARD_POISON_CLOSE
    if (startup_fds[10].present || startup_users[0] || live[0])
        startup_live_bad = 1;
#endif
    if (!poisoned || !poison_calls || channel_calls != poison_calls ||
        write(2, "D\n", 2) != -1 || errno != EIO ||
        close(2) != -1 || errno != EIO || channel_calls != poison_calls)
        startup_live_bad = 1;
#else
    int alias = fcntl(1, F_DUPFD_CLOEXEC, 10);
    if (alias != 11 || close(alias) || write(2, "D\n", 2) != 2)
        startup_live_bad = 1;
 #endif
    errno = saved;
#ifdef STARTUP_GUARD_ERROR
    errno = ERANGE; /* Caller wrapper must retain its own operation error. */
#endif
#ifdef STARTUP_GUARD_JUMP
    siglongjmp(startup_jump, 1);
#endif
}
#endif
#ifdef STARTUP_GUARD_TEST
static int guard_checks(void)
{
    uint64_t before = 4, observed = 0, outer;
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&before, 0, 8))
        return 88;
    int saved_errno = ERANGE;
    errno = saved_errno;
    if (startup_mask_enter(&outer) || fcntl(0, F_GETFD) ||
        dup2(0, 0) != 0 || errno != saved_errno ||
        memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) ||
        observed != (UINT64_MAX & ~((UINT64_C(1) << 8) | (UINT64_C(1) << 18))))
        return 88;
    startup_mask_leave(outer);
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) || observed != before)
        return 88;
    struct startup_fd snapshot[16];
    unsigned counts[3];
    memcpy(snapshot, startup_fds, sizeof snapshot);
    memcpy(counts, startup_users, sizeof counts);
    unsigned transfers = startup_guard_transfers;
    startup_guard_fail = 1;
    if (fcntl(0, F_DUPFD, 10) != -1 || errno != EFAULT ||
        dup2(0, 1) != -1 || errno != EFAULT ||
        startup_io(3, 0, 0, 0) != -EFAULT || startup_begin() ||
        memcmp(snapshot, startup_fds, sizeof snapshot) ||
        memcmp(counts, startup_users, sizeof counts) ||
        transfers != startup_guard_transfers)
        return 88;
    startup_guard_fail = 0;
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) || observed != before)
        return 88;
    before = 0;
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&before, 0, 8))
        return 88;
#ifdef STARTUP_GUARD_RESTORE_FAIL
    startup_guard_fail = 2;
    (void)fcntl(0, F_GETFD); /* Must exit 125, never resume here. */
    return 88;
#endif
    return 0;
}
#endif
#ifdef STARTUP_SELF_TEST
extern void __restore_rt(void);
static volatile unsigned self_count;
static volatile unsigned self_bad;
static void self_handler(int signal)
{
    uint64_t mask = 0;
    if (signal != 10 || memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) ||
        mask != (512 | 4))
        self_bad = 1;
    ++self_count;
}
#ifdef STARTUP_SELF_AUTO_RETRY
__attribute__((naked)) static long self_mask_at(uintptr_t stack,
                                              const uint64_t *set, uint64_t *old)
{
    __asm__ __volatile__("mov %rsp, %r11\n"
                         "mov %rdi, %rsp\n"
                         "mov $2, %edi\n"
                         "mov $8, %r10d\n"
                         "xor %r8d, %r8d\n"
                         "xor %r9d, %r9d\n"
                         "mov $0x1000e, %eax\n"
                         "int $0x81\n"
                         "mov %r11, %rsp\n"
                         "ret\n");
}
static int self_auto_retry_checks(void)
{
    uint64_t record[4] = {(uintptr_t)self_handler, 0x04000000,
                           (uintptr_t)__restore_rt, 4};
    uint64_t got[4], mask = 512, zero = 0, old;
    const uintptr_t stacks[] = {0, 0x08000080, 0x08010001, UINTPTR_MAX};
    if (memtrap(0x29001, 10, (uintptr_t)record, 0, 8))
        return 94;
    for (unsigned i = 0; i < sizeof stacks / sizeof stacks[0]; ++i) {
        old = 99;
        if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&mask, 0, 8) ||
            memtrap(0x29002, 10, 0, 0, 0) ||
            self_mask_at(stacks[i], &zero, &old) || old != 512 ||
            self_count != i || self_bad)
            return 94;
        old = 99;
        if (self_mask_at(stacks[i], 0, &old) || old || self_count != i ||
            memtrap(0x29001, 10, 0, (uintptr_t)got, 8) ||
            memcmp(got, record, sizeof record))
            return 94;
#ifdef STARTUP_SELF_AUTO_DISCARD
        record[0] = 1;
        if (memtrap(0x29001, 10, (uintptr_t)record, 0, 8))
            return 94;
        record[0] = (uintptr_t)self_handler;
        if (memtrap(0x29001, 10, (uintptr_t)record, 0, 8))
            return 94;
#endif
        if (memtrap(0x1000e, 0, 0, (uintptr_t)&old, 8) || old ||
            self_count != i + 1 || self_bad ||
            memtrap(0x1000e, 0, 0, (uintptr_t)&old, 8) || old ||
            self_count != i + 1)
            return 94;
    }
    self_count = 0;
    record[0] = 0;
    return memtrap(0x29001, 10, (uintptr_t)record, 0, 8) ? 94 : 0;
}
#endif
#ifdef STARTUP_SELF_RETRY
__attribute__((naked)) static long self_poll_at(uintptr_t stack)
{
    __asm__ __volatile__("mov %rsp, %r11\n"
                         "mov %rdi, %rsp\n"
                         "xor %edi, %edi\n"
                         "xor %esi, %esi\n"
                         "xor %edx, %edx\n"
                         "xor %r10d, %r10d\n"
                         "xor %r8d, %r8d\n"
                         "xor %r9d, %r9d\n"
                         "mov $0x29002, %eax\n"
                         "int $0x81\n"
                         "mov %r11, %rsp\n"
                         "ret\n");
}
static int self_retry_checks(void)
{
    uint64_t record[4] = {(uintptr_t)self_handler, 0x04000000,
                           (uintptr_t)__restore_rt, 4};
    uint64_t observed[4], mask = 512, zero = 0, got = 99;
    const uintptr_t stacks[] = {0, 0x08000080, 0x08010001, UINTPTR_MAX};
    if (memtrap(0x29001, 10, (uintptr_t)record, 0, 8) ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&mask, 0, 8) ||
        memtrap(0x29002, 10, 0, 0, 0) ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&zero, 0, 8))
        return 92;
    for (unsigned i = 0; i < sizeof stacks / sizeof stacks[0]; ++i) {
        if (self_poll_at(stacks[i]) != -EINVAL || self_count || self_bad ||
            memtrap(0x29001, 10, 0, (uintptr_t)observed, 8) ||
            memcmp(record, observed, sizeof record) ||
            memtrap(0x1000e, 0, 0, (uintptr_t)&got, 8) || got)
            return 92;
    }
#ifdef STARTUP_SELF_DISCARD
    record[0] = 1;
    if (memtrap(0x29001, 10, (uintptr_t)record, 0, 8))
        return 92;
    record[0] = (uintptr_t)self_handler;
    if (memtrap(0x29001, 10, (uintptr_t)record, 0, 8))
        return 92;
#endif
    if (memtrap(0x29002, 0, 0, 0, 0) || self_count != 1 || self_bad ||
        memtrap(0x29002, 0, 0, 0, 0) || self_count != 1 ||
        memtrap(0x1000e, 0, 0, (uintptr_t)&got, 8) || got)
        return 92;
    self_count = 0;
    record[0] = 0;
    return memtrap(0x29001, 10, (uintptr_t)record, 0, 8) ? 92 : 0;
}
#endif
static int self_checks(void)
{
    uint64_t record[4] = {(uintptr_t)self_handler, 0x04000000,
                           (uintptr_t)__restore_rt, 4};
    uint64_t mask = 512, zero = 0, observed = 99;
    if (memtrap(0x29002, 0, 0, 0, 0) || self_count ||
        memtrap(0x29002, 9, 0, 0, 0) != -EINVAL ||
        memtrap(0x29002, 10, 1, 0, 0) != -EINVAL ||
        memtrap(0x29002, 10, 0, 0, 0) != -ENOTSUP ||
        memtrap(0x29001, 10, (uintptr_t)record, 0, 8) ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&mask, 0, 8) ||
        memtrap(0x29002, 10, 0, 0, 0) ||
        memtrap(0x29002, 10, 0, 0, 0) || self_count ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&zero, 1, 8) != -EFAULT || self_count ||
        memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) || observed != 512 ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&zero, 0, 8) ||
#ifdef STARTUP_SELF_AUTO
        self_count != 1)
#else
        self_count)
#endif
        return 91;
#ifndef STARTUP_SELF_SKIP
    if (memtrap(0x29002, 0, 0, 0, 0))
        return 91;
#endif
    if (self_count != 1 || self_bad || memtrap(0x29002, 0, 0, 0, 0) ||
        self_count != 1 || memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) || observed)
        return 91;
    record[0] = 1;
    if (memtrap(0x29001, 10, (uintptr_t)record, 0, 8) ||
        memtrap(0x29002, 10, 0, 0, 0) || self_count != 1)
        return 91;
    /* Leave a blocked post; reclaim must reset it before the next generation. */
    record[0] = (uintptr_t)self_handler;
    if (memtrap(0x29001, 10, (uintptr_t)record, 0, 8) ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&mask, 0, 8) ||
        memtrap(0x29002, 10, 0, 0, 0) ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&zero, 0, 8))
        return 91;
    return 0;
}
#endif

#ifdef STARTUP_ACTION_TEST
struct action_record { uint64_t entry, flags, restorer, mask; };
#ifndef STARTUP_ACTION_DISABLED
static unsigned char action_storage[8192] __attribute__((aligned(4096)));
#endif
static int action_checks(void)
{
    struct action_record old = {0};
    long status = memtrap(0x29001, 10, 0, (uintptr_t)&old, 8);
#ifdef STARTUP_ACTION_DISABLED
    return status == -ENOSYS ? 0 : 89;
#else
    struct action_record next = {1, 0x04000000, 23, 4}, got;
    if (status || old.entry || old.flags || old.restorer || old.mask)
        return 89;
    unsigned char *cross = action_storage + 4081;
    memcpy(cross, &next, sizeof next);
    if (memtrap(0x29001, 10, (uintptr_t)cross, (uintptr_t)cross, 8) ||
        memcmp(cross, &old, sizeof old) ||
        memtrap(0x29001, 10, 0, (uintptr_t)&got, 8) || memcmp(&got, &next, sizeof got))
        return 89;
    struct action_record rejected = {0, 1, 0, 0};
    got = next;
    if (memtrap(0x29001, 10, (uintptr_t)&rejected, (uintptr_t)&got, 8) != -ENOTSUP ||
        memcmp(&got, &next, sizeof got) ||
        memtrap(0x29001, 10, UINTPTR_MAX - 15, 0, 8) != -EFAULT ||
        memtrap(0x29001, 10, (uintptr_t)&old, UINTPTR_MAX - 15, 8) != -EFAULT ||
        memtrap(0x29001, 10, (uintptr_t)&old, (uintptr_t)unsupported_handler, 8) != -EFAULT)
        return 89;
    rejected = (struct action_record){(uintptr_t)action_storage, 0x04000000, (uintptr_t)unsupported_handler, 0};
    if (memtrap(0x29001, 10, (uintptr_t)&rejected, (uintptr_t)&got, 8) != -EINVAL ||
        memcmp(&got, &next, sizeof got) ||
        memtrap(0x29001, 10, 0, (uintptr_t)&got, 8) || memcmp(&got, &next, sizeof got))
        return 89;
    next = (struct action_record){(uintptr_t)unsupported_handler, 0x04000000, (uintptr_t)unsupported_handler, 4};
    if (memtrap(0x29001, 10, (uintptr_t)&next, (uintptr_t)&got, 8) ||
        memtrap(0x29001, 10, 0, (uintptr_t)&got, 8) || memcmp(&got, &next, sizeof got))
        return 89;
    /* Leave the action installed: next generation must observe initial DFL. */
    return 0;
#endif
}
#endif
#ifdef STARTUP_ACTION_MEMORY
static int action_mapping_checks(void)
{
    unsigned long cap = getauxval(0xa000);
    struct action_record baseline, observed, replacement = {1, 0x04000000, 23, 8};
    if (!cap || memtrap(0x29001, 10, 0, (uintptr_t)&baseline, 8))
        return 90;
    long address = memtrap(0x22001, cap, 8192, 3, 0);
    if (address < 0)
        return 90;
    unsigned char *cross = (unsigned char *)address + 4096 - 16;
    unsigned char before[32];
    memcpy(before, &replacement, 32);
    for (unsigned mode = 0; mode < 3; mode++) {
        memcpy(cross, before, 32);
#ifndef STARTUP_ACTION_MEMORY_WRITABLE
        if (mode < 2 ? memtrap(0x22002, cap, address + 4096, 4096, mode == 0 ? 1 : 0)
                     : memtrap(0x22003, cap, address + 4096, 4096, 0))
            return 90;
#endif
        if (memtrap(0x29001, 10, (uintptr_t)&replacement, (uintptr_t)cross, 8) != -EFAULT ||
            memcmp(cross, before, 16) ||
            memtrap(0x29001, 10, 0, (uintptr_t)&observed, 8) ||
            memcmp(&observed, &baseline, 32))
            return 90;
        observed = baseline;
        if (mode == 0) {
            /* Read-only input is readable and must install, then restore. */
            if (memtrap(0x29001, 10, (uintptr_t)cross, (uintptr_t)&observed, 8) ||
                memcmp(&observed, &baseline, 32) ||
                memtrap(0x29001, 10, (uintptr_t)&baseline, (uintptr_t)&observed, 8) ||
                memcmp(&observed, &replacement, 32))
                return 90;
        } else {
            if (memtrap(0x29001, 10, (uintptr_t)cross, (uintptr_t)&observed, 8) != -EFAULT ||
                memcmp(&observed, &baseline, 32))
                return 90;
            for (unsigned target = 0; target < 2; target++) {
                struct action_record bad = baseline;
                if (target == 0) bad.entry = (uint64_t)address + 4096;
                else bad.restorer = (uint64_t)address + 4096;
                if (memtrap(0x29001, 10, (uintptr_t)&bad, (uintptr_t)&observed, 8) != -EINVAL ||
                    memcmp(&observed, &baseline, 32))
                    return 90;
            }
        }
        if (memtrap(0x29001, 10, 0, (uintptr_t)&observed, 8) ||
            memcmp(&observed, &baseline, 32))
            return 90;
        if (mode < 2) {
            if (memtrap(0x22002, cap, address + 4096, 4096, 3) || memcmp(cross, before, 32))
                return 90;
        } else {
            if (memtrap(0x22001, cap, 4096, 3, 0) != address + 4096)
                return 90;
            for (unsigned i = 0; i < 4096; i++)
                if (*((unsigned char *)address + 4096 + i))
                    return 90;
            if (memcmp(cross, before, 16))
                return 90;
        }
    }
    return memtrap(0x22003, cap, address, 8192, 0) ? 90 : 0;
}
#endif
#ifdef STARTUP_PUBLIC_ACTION
#include <setjmp.h>
static sigjmp_buf public_jump;
static volatile unsigned public_count;
static volatile unsigned public_bad;
static volatile unsigned public_escape;
static void public_handler(int signal)
{
    uint64_t mask = 0;
    if (signal != SIGUSR1 || memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) ||
        mask != (512 | 4))
        public_bad = 1;
    ++public_count;
    if (public_escape)
        siglongjmp(public_jump, 1);
}
/* Four public arguments: deliberately dirty unused registers. Private ABI
 * still rejects them. Buffers remain owned by this active native domain. */
static long public_raw(unsigned long number, unsigned long signal,
                       const void *set, void *old)
{
    register unsigned long r10 __asm__("r10") = 8;
    register unsigned long r8 __asm__("r8") = 123;
    register unsigned long r9 __asm__("r9") = 456;
    long result;
    __asm__ __volatile__("int $0x81" : "=a"(result)
        : "a"(number), "D"(signal), "S"(set), "d"(old),
          "r"(r10), "r"(r8), "r"(r9) : "rcx", "r11", "memory");
    return result;
}
static int public_action_checks(void)
{
    struct sigaction action = {0}, old = {0};
    uint64_t raw[4], before[4], mask = 0;
    if (sigaction(SIGUSR1, 0, &old) || old.sa_handler != SIG_DFL ||
        public_raw(0x29001, 10, 0, raw) != -EINVAL)
        return 101;
    action.sa_handler = SIG_IGN;
    if (sigaction(SIGUSR1, &action, &old) || old.sa_handler != SIG_DFL ||
        public_raw(0x1000d, 10, 0, raw) || raw[0] != 1 ||
        raw[1] != 0x04000000 || !raw[2] || raw[3])
        return 101;
    action.sa_handler = public_handler;
    if (sigemptyset(&action.sa_mask) || sigaddset(&action.sa_mask, 3) ||
        sigaction(SIGUSR1, &action, &old) || old.sa_handler != SIG_IGN ||
        memtrap(0x29001, 10, 0, (uintptr_t)before, 8) ||
        before[0] != (uintptr_t)public_handler || before[1] != 0x04000000 ||
        !before[2] || before[3] != 4)
        return 101;
    if (signal(SIGUSR1, public_handler) != SIG_ERR || errno != ENOTSUP ||
        public_raw(0x1000d, 10, (void *)1, raw) != -EFAULT ||
        public_raw(0x1000d, 10, before, (void *)public_handler) != -EFAULT ||
        public_raw(0x1000d, 10, 0, raw) || memcmp(raw, before, sizeof raw))
        return 101;
    raw[0] = (uintptr_t)raw; /* RW/NX handler must not replace the record. */
    if (public_raw(0x1000d, 10, raw, 0) != -EINVAL ||
        public_raw(0x1000d, 10, 0, raw) || memcmp(raw, before, sizeof raw) ||
        sigaction(SIGUSR1, 0, &old) || old.sa_handler != public_handler ||
        old.sa_flags != 0x04000000 || sigismember(&old.sa_mask, 3) != 1)
        return 101;
    if (memtrap(0x29002, 10, 0, 0, 0) || public_count != 1 || public_bad)
        return 101;
    public_escape = 1;
    if (!sigsetjmp(public_jump, 1)) {
        memtrap(0x29002, 10, 0, 0, 0);
        return 101;
    }
    if (public_count != 2 || public_bad ||
        memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) || mask)
        return 101;
    mask = 512;
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&mask, 0, 8) ||
        memtrap(0x29002, 10, 0, 0, 0))
        return 101;
#ifndef STARTUP_PUBLIC_IGNORE_SKIP
    if (signal(SIGUSR1, SIG_IGN) != public_handler)
        return 101;
#endif
    if (sigaction(SIGUSR1, 0, &old) || old.sa_handler != SIG_IGN ||
        old.sa_flags != (0x04000000 | SA_RESTART) ||
        memtrap(0x29001, 10, 0, (uintptr_t)raw, 8) || raw[0] != 1 ||
        raw[1] != (0x04000000 | SA_RESTART) || raw[3] ||
        memtrap(0x29001, 10, (uintptr_t)raw, 0, 8) != -ENOTSUP ||
        signal(SIGKILL, SIG_IGN) != SIG_ERR || errno != EINVAL ||
        signal(SIGUSR1, public_handler) != SIG_ERR || errno != ENOTSUP)
        return 101;
    mask = 0;
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&mask, 0, 8) ||
        memtrap(0x29002, 0, 0, 0, 0) ||
        memtrap(0x29002, 10, 0, 0, 0) || public_count != 2 ||
        signal(SIGUSR1, SIG_DFL) != SIG_IGN ||
        sigaction(SIGUSR1, 0, &old) || old.sa_handler != SIG_DFL ||
        old.sa_flags != (0x04000000 | SA_RESTART))
        return 101;
    /* Private replacement still requires its original flags subset. */
    raw[0] = 0;
    raw[1] = 0x04000000;
    raw[3] = 0;
    if (memtrap(0x29001, 10, (uintptr_t)raw, (uintptr_t)before, 8) ||
        before[0] != 0 || before[1] != (0x04000000 | SA_RESTART) ||
        sigaction(SIGUSR1, 0, &old) || old.sa_handler != SIG_DFL)
        return 101;
    return 0;
}
#endif
#ifdef STARTUP_CWD
#ifdef STARTUP_CWD_POISON
static int directory_poison_checks(void)
{
    char buffer[8], original[8];
    struct stat value, original_stat;
    memset(buffer, '!', sizeof buffer); memcpy(original, buffer, sizeof buffer);
    memset(&value, 0x5a, sizeof value); original_stat = value;
    uint64_t before = 0, after = 0;
    if (memtrap(0x1000e, 999, 0, (uintptr_t)&before, 8)) return 107;
#ifdef STARTUP_CWD_POISON_STAT
    if (stat(".", &value) != -1 || errno != EIO) return 107;
#else
    if (getcwd(buffer, sizeof buffer) || errno != EIO) return 107;
#endif
    if (!poisoned || memcmp(buffer, original, sizeof buffer) ||
        memcmp(&value, &original_stat, sizeof value) ||
        memtrap(0x1000e, 999, 0, (uintptr_t)&after, 8) || after != before)
        return 107;
    if (getcwd(buffer, sizeof buffer) || errno != EIO ||
        stat(".", &value) != -1 || errno != EIO ||
        read(0, buffer, 1) != -1 || errno != EIO ||
        write(1, "!", 1) != -1 || errno != EIO ||
        memcmp(buffer, original, sizeof buffer) ||
        memcmp(&value, &original_stat, sizeof value)) return 107;
    return 1; /* Verified transport failure; no successful shell claim. */
}
#endif

#ifndef STARTUP_CWD_PWD
static int directory_checks(void)
{
    unsigned char raw[32] = {0};
    unsigned generation = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    /* Raw requests bypass the facade; the owner must enforce the binding. */
    const unsigned refs_to_reject[] = {0, 0x12345678, 0x76030000 + generation - 1};
    for (unsigned j = 0; j < 3; j++) {
        memset(raw, 0, sizeof raw);
        put(raw, 0, 4); put(raw, 4, refs_to_reject[j]); put(raw, 8, 3);
        if (!exchange(raw, 32) || (int)get(raw, 0) != (j == 2 ? -EBADF : -EACCES))
            return 106;
        for (unsigned k = 4; k < 32; k++)
            if (raw[k]) return 106;
    }
    for (unsigned j = 0; j < 4; j++) {
        memset(raw, 0, sizeof raw);
        put(raw, 0, j == 2 ? 99 : 4);
        put(raw, 4, startup_directory);
        put(raw, 8, j == 0 ? 0 : j == 1 ? 4 : 3);
        if (j == 3) raw[31] = 1;
        if (!exchange(raw, 32) || (int)get(raw, 0) != (j == 2 ? -ENOSYS : -EINVAL))
            return 106;
        for (unsigned k = 4; k < 32; k++)
            if (raw[k]) return 106;
    }
    char buffer[10];
    memset(buffer, '!', sizeof buffer);
    for (unsigned size = 0; size < 6; size++) {
        if (getcwd(buffer + 1, size) || errno != ERANGE)
            return 106;
        for (unsigned j = 0; j < sizeof buffer; j++)
            if (buffer[j] != '!') return 106;
    }
    errno = 77;
    if (getcwd(buffer + 1, 6) != buffer + 1 || strcmp(buffer + 1, "/work") ||
        buffer[0] != '!' || buffer[7] != '!' || errno != 77 ||
        getcwd(buffer, sizeof buffer) != buffer || strcmp(buffer, "/work"))
        return 106;
    if (getcwd(0, 1) || errno != ERANGE)
        return 106;
#ifdef STARTUP_CWD_ENOMEM
    uint64_t allocation_mask = 0, restored_mask = 0;
    if (memtrap(0x1000e, 999, 0, (uintptr_t)&allocation_mask, 8)) return 106;
    errno = 77;
    if (getcwd(0, 0) || errno != ENOMEM || poisoned || !startup_ready ||
        memtrap(0x1000e, 999, 0, (uintptr_t)&restored_mask, 8) ||
        restored_mask != allocation_mask) return 106;
#endif
    char *allocated = getcwd(0, 0);
    if (!allocated || strcmp(allocated, "/work")) return 106;
    free(allocated);
    struct stat a, b;
    if (stat(".", &a) || stat("/work", &b) || a.st_dev != 100 + generation ||
        a.st_ino != 1 || a.st_dev != b.st_dev || a.st_ino != b.st_ino ||
        a.st_mode != (S_IFDIR | 0500)) return 106;
    const char *paths[] = {"", "missing", "..", "/", "a/b", "0123456789012345"};
    const int errors[] = {ENOENT, ENOENT, EACCES, EACCES, EINVAL, ENAMETOOLONG};
    for (unsigned j = 0; j < 6; j++) {
        memset(&a, 0x5a, sizeof a); b = a;
        if (stat(paths[j], &a) != -1 || errno != errors[j] || memcmp(&a, &b, sizeof a))
            return 106;
    }
    return 0;
}
#endif
#endif
#ifdef STARTUP_DASH_SIGNALS
/* Existing symbols from pinned dash headers; no replacement dash state. */
extern char optlist[], sigmode[];
extern int shlvl;
extern volatile sig_atomic_t gotsigchld;
extern void setsignal(int), ignoresig(int), onsig(int);
#ifdef STARTUP_DASH_INIT
extern void init(void), flushall(void);
extern const char *lookupvar(const char *);
extern char **environ;
static int dash_init_checks(void)
{
    static char *empty_environment[] = {
#if defined(STARTUP_CWD_MATCH) || defined(STARTUP_CWD_PWD)
        "PWD=/work",
#elif defined(STARTUP_CWD_RELATIVE)
        "PWD=work",
#elif defined(STARTUP_CWD_ABSENT)
        "PWD=/missing",
#endif
        0};
#if defined(STARTUP_CWD) && !defined(STARTUP_CWD_PWD)
    if (directory_checks()) return 106;
#endif
    struct sigaction action = {0};
#ifdef STARTUP_PARENT
    long parent = getppid();
#ifdef STARTUP_PARENT_SELF
    parent = getpid(); /* Negative fixture: substitute the worker identity. */
#endif
    if (parent != 4 || parent == getpid() || getppid() != parent ||
        public_raw(0x1006e, 999, (void *)1, (void *)1) != parent)
        return 104;
#endif
    environ = empty_environment;
#ifndef STARTUP_DASH_INIT_SKIP
    init();
#endif
    flushall();
    const char *ppid = lookupvar("PPID");
    const char *pwd = lookupvar("PWD");
    const char *ifs = lookupvar("IFS");
    const char *optind = lookupvar("OPTIND");
#ifdef STARTUP_PARENT
    const char *expected_parent = "4";
#else
    const char *expected_parent = "-38";
#endif
#ifdef STARTUP_IDENTITY
    unsigned generation = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    unsigned base = 1000 + generation;
#ifdef STARTUP_IDENTITY_ZERO
    unsigned effective = 0;
#else
    unsigned effective = base + 10;
#endif
    const unsigned raw_getters[] = {SYS_getuid, SYS_geteuid, SYS_getgid, SYS_getegid};
    for (unsigned j = 0; j < 4; j++)
        if (memtrap(0x10000 + raw_getters[j], 0, 0, 0, 0) != -ENOSYS)
            return 105;
    const char *ps1 = lookupvar("PS1");
    if (getuid() != base || geteuid() != effective || getgid() != base + 20 ||
        getegid() != base + 30 || !ps1 || strcmp(ps1, effective ? "$ " : "# ") ||
        memtrap(0x20002, 4, 0, 0, 0) != -EACCES ||
        write(0, "!", 1) != -1 || errno != EACCES)
        return 105;
#endif
    if (!ppid || strcmp(ppid, expected_parent) || !pwd ||
#ifdef STARTUP_CWD
        strcmp(pwd, "/work") ||
#else
        *pwd ||
#endif
        !ifs || strcmp(ifs, " \t\n") || !optind || strcmp(optind, "1") ||
#ifndef STARTUP_IDENTITY
        geteuid() != (uid_t)-ENOSYS ||
#endif
        sigaction(SIGCHLD, 0, &action) || action.sa_handler != onsig)
        return 103;
    return 0;
}
#endif
static int dash_signal_checks(void)
{
    struct sigaction action = {0};
    uint64_t record[4];
    shlvl = 0;
    optlist[3] = 1; /* iflag */
    optlist[4] = 0; /* mflag */
#ifndef STARTUP_DASH_SIGNAL_SKIP
    setsignal(SIGCHLD);
#endif
    setsignal(SIGINT);
    setsignal(SIGQUIT);
    setsignal(SIGTERM);
    const int signals[] = {SIGCHLD, SIGINT, SIGQUIT, SIGTERM};
    for (unsigned i = 0; i < sizeof signals / sizeof signals[0]; ++i) {
        int sig = signals[i];
        uintptr_t expected = i < 2 ? (uintptr_t)onsig : (uintptr_t)SIG_IGN;
        if (sigaction(sig, 0, &action) || (uintptr_t)action.sa_handler != expected ||
            action.sa_flags != 0x04000000 ||
            memtrap(0x29001, sig, 0, (uintptr_t)record, 8) ||
            record[0] != expected || record[1] != 0x04000000 || !record[2] ||
            sigismember(&action.sa_mask, SIGUSR1) != 1)
            return 102;
    }
    if (gotsigchld || memtrap(0x29002, SIGCHLD, 0, 0, 0) || !gotsigchld)
        return 102;
    ignoresig(SIGHUP);
    if (sigaction(SIGHUP, 0, &action) || action.sa_handler != SIG_IGN ||
        action.sa_flags != (0x04000000 | SA_RESTART))
        return 102;
    action = (struct sigaction){0};
    for (unsigned i = 0; i < sizeof signals / sizeof signals[0]; ++i)
        if (sigaction(signals[i], &action, 0))
            return 102;
    return sigaction(SIGHUP, &action, 0) ? 102 : 0;
}
#endif
#ifdef STARTUP_IDENTITY
static int identity_unpublished(void)
{
    uid_t (*getters[])(void) = {getuid, geteuid, getgid, getegid};
    for (unsigned j = 0; j < 4; j++) {
        errno = 77;
        if (getters[j]() != (uid_t)-1 || errno != EAGAIN || startup_ids[j])
            return 0;
    }
    return 1;
}
#endif
#ifdef STARTUP_FILES_BOUNDARIES
/* Test requests use the same masked connection as the facade. */
static int file_denial(unsigned op, unsigned token, unsigned selector,
                       unsigned count, const char *name, int error)
{
    unsigned char b[32] = {0};
    put(b, 0, op); put(b, 4, token); put(b, 8, selector); put(b, 12, count);
    if (name) memcpy(b + 16, name, strlen(name));
    uint64_t previous;
    if (startup_mask_enter(&previous)) return 0;
    int complete = exchange(b, 32);
    startup_mask_leave(previous);
    if (!complete || (int)get(b, 0) != -error) return 0;
    for (unsigned j = 4; j < 32; j++) if (b[j]) return 0;
    return 1;
}
static int file_description_checks(void)
{
    static const char script[] = "printf 'hello\\n'\n";
    char bytes[16] = {0};
    int a = open("hello.sh", O_RDONLY), b = open("hello.sh", O_RDONLY);
    if (a != 3 || b != 4 || open("hello.sh", O_RDONLY) != -1 || errno != EMFILE)
        return 114;
    unsigned binding = startup_fds[a].binding, stale = refs[binding];
    int alias = fcntl(a, F_DUPFD_CLOEXEC, 10);
    if (alias != 10 || fcntl(alias, F_GETFD) != FD_CLOEXEC ||
        fcntl(a, F_GETFD) != 0 || read(a, bytes, 4) != 4 || memcmp(bytes, script, 4) ||
        read(alias, bytes, 4) != 4 || memcmp(bytes, script + 4, 4) ||
        read(b, bytes, 4) != 4 || memcmp(bytes, script, 4)) return 114;
    unsigned calls = channel_calls;
    if (write(a, "x", 1) != -1 || errno != EACCES || channel_calls != calls)
        return 114;
    int filled[10];
    for (unsigned j = 0; j < 10; j++) {
        filled[j] = fcntl(1, F_DUPFD, 0);
        if (filled[j] < 0) return 114;
    }
    if (open("hello.sh", O_RDONLY) != -1 || errno != EMFILE || channel_calls != calls)
        return 114;
    for (unsigned j = 0; j < 10; j++) if (close(filled[j])) return 114;
    if (close(a) || channel_calls != calls ||
        read(alias, bytes, sizeof bytes) != 9 || memcmp(bytes, script + 8, 9) ||
        read(alias, bytes, 1) != 0 || close(alias) || close(b)) return 114;
    int c = open("hello.sh", O_RDONLY);
    if (c != 3 || refs[startup_fds[c].binding] == stale ||
        !file_denial(7, stale, binding, 1, 0, EBADF) ||
        !file_denial(7, refs[startup_fds[c].binding], 4, 1, 0, EBADF) ||
        !file_denial(6, startup_directory, 4, 1, "hello.sh", EACCES) ||
        !file_denial(6, startup_root, 4, 3, "hello.sh", EACCES) ||
        open("missing", O_RDONLY) != -1 || errno != ENOENT ||
        read(c, bytes, 4) != 4 || memcmp(bytes, script, 4) || close(c)) return 114;
    for (unsigned j = 0; j < 3; j++) {
        c = open("hello.sh", O_RDONLY);
        if (c != 3 || read(c, bytes, 1) != 1 || bytes[0] != 'p' || close(c))
            return 114;
    }
    if (open("hello.sh", O_RDONLY) != -1 || errno != EMFILE || poisoned)
        return 114;
    return 0;
}
#endif
#ifdef STARTUP_FILES_POISON
static int file_reply_failure_checks(void)
{
    uint64_t before = 0, after = 0;
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&before, 8)) return 115;
    unsigned char bytes[16];
    memset(bytes, 0x5a, sizeof bytes);
    int fd = open("hello.sh", O_RDONLY);
    int ok;
#ifdef STARTUP_FILES_POISON_READ
    ok = fd == 3 && read(fd, bytes, 4) == -1 && errno == EIO;
#elif defined(STARTUP_FILES_POISON_CLOSE)
    ok = fd == 3 && close(fd) == -1 && errno == EIO && !startup_fds[3].present;
#else
    ok = fd == -1 && errno == EIO && !startup_fds[3].present && !live[3] && !live[4];
#endif
    for (unsigned j = 0; j < sizeof bytes; j++) ok &= bytes[j] == 0x5a;
    unsigned calls = channel_calls;
    ok &= poisoned && open("hello.sh", O_RDONLY) == -1 && errno == EIO;
    for (unsigned j = 0; j < 16; j++) {
        if (startup_fds[j].present && (close((int)j) != -1 || errno != EIO)) ok = 0;
        if (startup_fds[j].present) ok = 0;
    }
    ok &= channel_calls == calls;
    ok &= !memtrap(0x1000e, 0, 0, (uintptr_t)&after, 8) && after == before;
    return ok ? 1 : 115;
}
#endif
#ifdef STARTUP_DASH_MAIN
extern int __real_main(int, char **);
extern _Noreturn void __real__exit(int);
_Noreturn void __wrap__exit(int status)
{
#ifndef STARTUP_DASH_MAIN_SKIP_CLOSE
    for (int fd = 0; fd < 16; fd++)
        if (startup_fds[fd].present && close(fd)) status = 112;
#endif
#ifdef STARTUP_ENV
    if (status == 7 && startup_file_duplicates !=
#ifdef STARTUP_ENV_LOAD
        1
#else
        0
#endif
    ) status = 112;
#elif defined(STARTUP_FILES)
    if (status == 0 && startup_file_duplicates != 1)
        status = 112;
#endif
    __real__exit(status);
}
#endif
int main(void)
{
    if (startup_cookie != 23)
        return 60;
    startup_cookie++;
    if (fcntl(0, F_GETFD) != -1 || errno != EBADF)
        return 61;
#ifdef STARTUP_IDENTITY
    if (!identity_unpublished())
        return 105;
#endif
#ifdef STARTUP_CWD
    char before[8] = "guard";
    if (getcwd(before, sizeof before) || errno != EAGAIN || strcmp(before, "guard"))
        return 106;
#endif
#ifdef STARTUP_FILES
    if (startup_root || open("hello.sh", O_RDONLY) != -1 || errno != EAGAIN)
        return 113;
#endif
    if (!startup_begin()) {
#ifdef STARTUP_FILES
        if (startup_root || open("hello.sh", O_RDONLY) != -1 || errno != EAGAIN)
            return 113;
#endif
#ifdef STARTUP_QUEUED_BODY
        if (!startup_queued_witness) return 108;
#endif
        for (int fd = 0; fd < 16; fd++)
            if (fcntl(fd, F_GETFD) != -1 || errno != EBADF)
                return 61;
#ifdef STARTUP_IDENTITY
#ifdef STARTUP_CWD
        if (startup_directory || getcwd(before, sizeof before) || errno != EAGAIN ||
            strcmp(before, "guard")) return 106;
#endif
#ifdef STARTUP_IDENTITY_ERRNO_SKIP
        startup_identity_errno_fault = 1;
#endif
        if (!identity_unpublished())
            return 105;
#endif
        if (
#ifndef STARTUP_PUBLIC_ACTION
            sigaction(SIGUSR1, 0, 0) != -1 || errno != EAGAIN ||
#endif
            sigprocmask(SIG_BLOCK, 0, 0) != -1 || errno != EAGAIN)
            return 61;
        return 110;
    }
#ifdef STARTUP_FILES_POISON
    __wrap__exit(file_reply_failure_checks());
#endif
#ifdef STARTUP_FILES_BOUNDARIES
    __wrap__exit(file_description_checks());
#endif
#ifdef STARTUP_DASH_MAIN
    static char *main_environment[] = {"PWD=/work", "LC_ALL=C",
#ifdef STARTUP_SYNTAX
        "WITNESS=value", "PATH=/nonexistent",
#endif
#if defined(STARTUP_ENV) && !defined(STARTUP_ENV_ABSENT)
#ifdef STARTUP_ENV_EMPTY
        "ENV=",
#else
        "ENV=hello.sh",
#endif
#endif
        0};
    environ = main_environment;
#ifdef STARTUP_DASH_MAIN_SKIP
    __wrap__exit(0);
#else
    static char *main_arguments[] = {"sh", "-c", "printf 'dash-main\\n'; exit 7", 0};
#ifdef STARTUP_SYNTAX
    static char *syntax_arguments[] = {"sh", "-c", "if then\n", 0};
    (void)main_arguments;
    __wrap__exit(__real_main(3, syntax_arguments));
#elif defined(STARTUP_PRIVILEGED)
    static char *privileged_arguments[] = {"sh", "-p", "-c", "exit 7", 0};
    (void)main_arguments;
    __wrap__exit(__real_main(4, privileged_arguments));
#elif defined(STARTUP_ENV)
#ifdef STARTUP_ENV_NONINTERACTIVE
    __wrap__exit(__real_main(3, main_arguments));
#else
    static char *env_arguments[] = {"sh", "-i", "+m", "-c", "printf 'dash-main\\n'; exit 7", 0};
    (void)main_arguments;
    __wrap__exit(__real_main(5, env_arguments));
#endif
#elif defined(STARTUP_FILES)
    static char *file_arguments[] = {"sh", "hello.sh", 0};
    (void)main_arguments;
    __wrap__exit(__real_main(2, file_arguments));
#else
    __wrap__exit(__real_main(3, main_arguments));
#endif
#endif
#endif
#ifdef STARTUP_CWD_POISON
    return directory_poison_checks();
#endif
#ifdef STARTUP_GUARD_TEST
    if (guard_checks())
        return 88;
#endif
#ifdef STARTUP_SELF_AUTO_RETRY
    if (self_auto_retry_checks())
        return 94;
#endif
#ifdef STARTUP_SELF_RETRY
    if (self_retry_checks())
        return 92;
#endif
#ifdef STARTUP_SELF_TEST
    if (self_checks())
        return 91;
#endif
#ifdef STARTUP_ACTION_TEST
    if (action_checks())
        return 89;
#endif
#ifdef STARTUP_ACTION_MEMORY
    if (action_mapping_checks())
        return 90;
#endif
#ifdef STARTUP_PUBLIC_ACTION
    if (public_action_checks())
        return 101;
#endif
#ifndef STARTUP_PUBLIC_ACTION
    if (memtrap(0x1000d, 10, 0, 0, 8) != -ENOSYS)
        return 101;
#endif
#ifdef STARTUP_DASH_INIT
    int init_status = dash_init_checks();
    if (init_status)
        return init_status;
#endif
#ifdef STARTUP_DASH_SIGNALS
    if (dash_signal_checks())
        return 102;
#endif
    int result = dash_startup_probe();
    if (result)
        return result;
    /* Consumer restoration, generation reset and actual kernel identity. */
    if (getpid() != memtrap(0x20005, 0, 0, 0, 0) * 4 +
#ifdef STARTUP_PARENT_SWAP
        2 ||
#else
        1 ||
#endif
        memtrap(0x10027, 1, 2, 3, 4) != getpid())
        return 62;
    struct sigaction action, observed;
    sigset_t original, all, observed_mask;
    if (sigaction(SIGUSR1, 0, &action) || action.sa_handler != SIG_DFL ||
        sigprocmask(999, 0, &original))
        return 63;
    uint64_t bits;
    memcpy(&bits, &original, sizeof bits);
    if (bits)
        return 63;
    memset(&all, 255, sizeof all);
    if (sigprocmask(SIG_SETMASK, &all, 0) ||
        sigprocmask(SIG_BLOCK, 0, &observed_mask))
        return 63;
    memcpy(&bits, &observed_mask, sizeof bits);
    if (bits != (UINT64_MAX & ~((UINT64_C(1) << 8) | (UINT64_C(1) << 18))))
        return 63;
    if (sigprocmask(999, &original, 0) != -1 || errno != EINVAL ||
        sigprocmask(SIG_BLOCK, 0, &observed_mask) ||
        memcmp(&observed_mask, &bits, 8) != 0 ||
        sigprocmask(SIG_SETMASK, &original, 0))
        return 63;
    action.sa_handler = unsupported_handler;
#ifdef STARTUP_PUBLIC_ACTION
    action.sa_flags = SA_RESTART;
#endif
    if (sigaction(SIGUSR1, &action, 0) != -1 || errno != ENOTSUP ||
        sigaction(SIGUSR1, 0, &observed) || observed.sa_handler != SIG_DFL)
        return 64;
    action.sa_handler = SIG_IGN;
    if (sigaction(SIGKILL, &action, 0) != -1 || errno != EINVAL)
        return 64;
#ifdef DUP_TEST
    int duplicate_result = duplicate_checks();
    if (duplicate_result)
        return duplicate_result;
#endif
#ifdef STARTUP_FRAME_TEST
    int frame_result = frame_checks();
    if (frame_result)
        return frame_result;
#endif
    int mask_result = mask_checks();
    if (mask_result)
        return mask_result;
    int alias = fcntl(0, F_DUPFD_CLOEXEC, 10);
    if (alias != 10 || fcntl(0, F_GETFD) != 0 ||
        fcntl(alias, F_SETFD, 2) != -1 || errno != EINVAL ||
        fcntl(alias, F_GETFD) != FD_CLOEXEC || fcntl(alias, F_SETFD, 0) ||
        fcntl(alias, F_GETFD) != 0)
        return 65;
    int plain = fcntl(alias, F_DUPFD, 3);
    if (plain != 3 || fcntl(plain, F_GETFD) || close(plain))
        return 65;
    for (int expected = 11; expected < 16; expected++)
        if (fcntl(alias, F_DUPFD_CLOEXEC, 10) != expected)
            return 66;
    if (fcntl(alias, F_DUPFD, 10) != -1 || errno != EMFILE ||
        fcntl(alias, F_DUPFD, 16) != -1 || errno != EINVAL ||
        fcntl(-1, F_DUPFD, 3) != -1 || errno != EBADF)
        return 66;
    for (int fd = 11; fd < 16; fd++)
        if (close(fd))
            return 67;
    if (close(0) || fcntl(0, F_GETFD) != -1 || errno != EBADF)
        return 67;
    char bytes[11];
    if (write(alias, "!", 1) != -1 || errno != EACCES)
        return 68;
    ssize_t size;
#ifdef STARTUP_GUARD_LIVE
    uint64_t live_record[4] = {(uintptr_t)startup_live_handler, 0x04000000,
                                (uintptr_t)__restore_rt, 0};
    if (memtrap(0x29001, 10, (uintptr_t)live_record, 0, 8))
        return 95;
    startup_live_armed = 1;
#ifdef STARTUP_GUARD_POISON
#ifdef STARTUP_GUARD_POISON_SKIP
    startup_live_armed = 0;
#endif
#ifdef STARTUP_GUARD_JUMP
    char *poison_buffer = startup_jump_bytes;

#else
    char *poison_buffer = bytes;

#endif
#ifdef STARTUP_GUARD_POISON_CLOSE
    const int poison_failure = 100;
#elif defined(STARTUP_GUARD_JUMP)
    const int poison_failure = 99;
#else
    const int poison_failure = 98;
#endif
    memset(poison_buffer, 0x5a, sizeof bytes);
#ifdef STARTUP_GUARD_JUMP
    if (!sigsetjmp(startup_jump,
#ifdef STARTUP_GUARD_JUMP_NO_MASK
                   0
#else
                   1
#endif
                   )) {
#ifdef STARTUP_GUARD_POISON_CLOSE
        (void)close(alias);
#else
        (void)read(alias, poison_buffer, sizeof bytes);
#endif
        return poison_failure;
    }
#else
#ifdef STARTUP_GUARD_POISON_CLOSE
    if (close(alias) != -1 || errno != EIO)
#else
    if (read(alias, poison_buffer, sizeof bytes) != -1 || errno != EIO)
#endif
        return poison_failure;
#endif
    if (startup_live_count != 1 || startup_live_bad || !poisoned ||
        channel_calls != poison_calls)
        return poison_failure;
    for (size_t i = 0; i < sizeof bytes; ++i)
        if ((unsigned char)poison_buffer[i] != 0x5a)
            return poison_failure;
    uint64_t poison_mask = 99;
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&poison_mask, 8) || poison_mask ||
        close(alias) != -1 || errno !=
#ifdef STARTUP_GUARD_POISON_CLOSE
        EBADF
#else
        EIO
#endif
        || close(1) != -1 || errno != EIO ||
        close(2) != -1 || errno != EBADF || channel_calls != poison_calls || !poisoned)
        return poison_failure;
    return 1;
#endif
#ifdef STARTUP_GUARD_ERROR
    errno = 0;
#ifdef STARTUP_GUARD_ERROR_IO
    if (write(alias, "!", 1) != -1 || errno != EACCES)
#else
    if (fcntl(-1, F_GETFD) != -1 || errno != EBADF)
#endif
        return 97;
    uint64_t error_mask = 99;
    if (startup_live_count != 1 || startup_live_bad ||
        memtrap(0x1000e, 0, 0, (uintptr_t)&error_mask, 8) || error_mask ||
        fcntl(alias, F_GETFD) != 0)
        return 97;
#endif
#ifdef STARTUP_GUARD_JUMP
    if (!sigsetjmp(startup_jump,
#ifdef STARTUP_GUARD_JUMP_NO_MASK
                   0
#else
                   1
#endif
                   )) {
        (void)read(alias, startup_jump_bytes, sizeof startup_jump_bytes);
        return 96; /* Handler must leave nonlocally before read returns. */
    }
    uint64_t jump_mask = 99;
    if (startup_live_count != 1 || startup_live_bad ||
        memtrap(0x1000e, 0, 0, (uintptr_t)&jump_mask, 8) || jump_mask)
        return 96;
    for (size_t at = 0; at < sizeof startup_jump_bytes;) {
        ssize_t done = write(1, startup_jump_bytes + at, sizeof startup_jump_bytes - at);
        if (done <= 0)
            return 96;
        at += (size_t)done;
    }
#endif
#endif
    while ((size = read(alias, bytes, sizeof bytes)) > 0) {
        for (ssize_t at = 0; at < size;) {
            ssize_t done = write(1, bytes + at, (size_t)(size - at));
            if (done <= 0)
                return 68;
            at += done;
        }
    }
    if (size || close(alias) || close(1)
#ifndef DUP_TEST
        || close(2)
#endif
    )
        return 69;
#ifdef STARTUP_GUARD_TEST
    uint64_t final_mask = 1;
    if (!startup_guard_transfers || startup_guard_exposed ||
        memtrap(0x1000e, 0, 0, (uintptr_t)&final_mask, 8) || final_mask)
        return 88;
#endif
#ifdef STARTUP_SIGNAL_TERM
    const unsigned signal =
#ifdef STARTUP_SIGNAL_INT
        2;
#else
        15;
#endif
    uint64_t blocked = 1ull << (signal - 1), clear = 0;
    if (memtrap(0x29002, 18, 0, 0, 0) != -ENOTSUP ||
        memtrap(0x29002, 9, 0, 0, 0) != -EINVAL ||
        memtrap(0x29002, 17, 0, 0, 0) ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&blocked, 0, 8) ||
        memtrap(0x29002, signal, 0, 0, 0) ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&clear, 0, 8))
        return 93;
#ifdef STARTUP_SIGNAL_EXIT
    return 128 + signal;
#else
    memtrap(0x29002, 0, 0, 0, 0);
    return 93;
#endif
#endif
#ifdef STARTUP_GUARD_LIVE
    if (startup_live_armed || startup_live_count != 1 || startup_live_bad)
        return 95;
#endif
    return 0;
}
