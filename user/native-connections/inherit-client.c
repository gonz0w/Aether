/* SPDX-License-Identifier: BSD-2-Clause */
#if defined(INHERIT_UNCERTAIN_WRITE) || defined(INHERIT_UNCERTAIN_CLOSE)
#define INHERIT_UNCERTAIN
#endif
#if defined(INHERIT_MASK_PREPARE) || defined(INHERIT_MASK_SKIP_REJECT)
#define INHERIT_PREPARE_FAULT 5
#endif
#ifdef INHERIT_MASK_ROLLBACK
#define INHERIT_ROLLBACK
#endif
#if defined(INHERIT_MASK_PREPARE) || defined(INHERIT_MASK_ROLLBACK) ||         \
    defined(INHERIT_MASK_SKIP_ENTER) || defined(INHERIT_MASK_SKIP_PARENT) ||   \
    defined(INHERIT_MASK_SKIP_CHILD) || defined(INHERIT_MASK_SKIP_REJECT)
#define INHERIT_MASK_SEED
#endif
#if defined(INHERIT_SIGNAL_ROLLBACK) || defined(INHERIT_SIGNAL_EARLY) ||       \
    defined(INHERIT_SIGNAL_REF) || defined(INHERIT_SIGNAL_NO_POST) ||          \
    defined(INHERIT_SIGNAL_OUTCOME)
#define INHERIT_SIGNAL
#endif
#ifdef INHERIT_SIGNAL_ROLLBACK
#define INHERIT_ROLLBACK
#endif
#if defined(INHERIT_SIGNAL_REJECT_PREPARE) ||                                  \
    defined(INHERIT_SIGNAL_REJECT_PREPARE_SKIP) ||                             \
    defined(INHERIT_SIGNAL_REJECT_PREPARE_FD)
#define INHERIT_PREPARE_FAULT 5
#define INHERIT_SIGNAL_ABORT
#endif
#ifdef INHERIT_SIGNAL_REJECT_PREPARE_SKIP
#define INHERIT_SIGNAL_ABORT_SKIP
#endif
#ifdef INHERIT_SIGNAL_REJECT_PREPARE_FD
#define INHERIT_SIGNAL_ABORT_FD
#endif
#if defined(INHERIT_SIGNAL_ABORT_SKIP) || defined(INHERIT_SIGNAL_ABORT_FD)
#define INHERIT_SIGNAL_ABORT
#endif
#ifdef INHERIT_SIGNAL_ABORT
#define INHERIT_SIGNAL
#endif
#ifdef INHERIT_SIGNAL_ACK_MISSING
#define INHERIT_SIGNAL
#define INHERIT_ACK_MISSING
#endif
#ifdef INHERIT_SIGNAL_ACK_PARTIAL
#define INHERIT_SIGNAL
#define INHERIT_ACK_PARTIAL
#endif
#ifdef INHERIT_SIGNAL_FINAL_PAD
#define INHERIT_SIGNAL
#define INHERIT_FINAL_PAD
#endif
#ifdef SCRATCH_EXEC_DENY
#define SCRATCH_EXEC_LAST
#endif
#ifdef SCRATCH_EXEC_LAST
#define SCRATCH_EXEC
#endif
#ifdef SCRATCH_EXEC
#define SCRATCH_COPY
#endif
#if defined(SCRATCH_CLIENT_BAD_CLOEXEC) || defined(SCRATCH_COPY)
#define SCRATCH_CLIENT
#endif
#define CAT_ROLES
#define SHELL_STARTUP
#include "../native-command/transport.h"
#ifdef SCRATCH_CLIENT
#include "scratch-client.h"
#ifdef SCRATCH_COPY
#include "scratch-copy.h"
#ifdef SCRATCH_EXEC
#include "scratch-restore.h"
#include "scratch-exec.h"
#endif
#else
#include "scratch-probe.h"
#endif
#endif
int copy_rebind(unsigned long, unsigned long, unsigned long, unsigned long *,
                unsigned long *);
static _Thread_local volatile unsigned cookie = 23;
static uint64_t preparation_previous;
static int preparation_active, preparation_child;
static int mask_is(uint64_t expected)
{
    uint64_t actual = 0;
    return !memtrap(0x1000e, 0, 0, (uintptr_t)&actual, 8) && actual == expected;
}
static uint64_t held_mask(void)
{
    return UINT64_MAX & ~((UINT64_C(1) << 8) | (UINT64_C(1) << 18));
}
static int preparation_restore(void)
{
    if (preparation_active) {
        if (!mask_is(held_mask()))
            return 0;
        int skip = 0;
#if defined(INHERIT_MASK_SKIP_PARENT) || defined(INHERIT_MASK_SKIP_REJECT)
        skip = !preparation_child;
#endif
#ifdef INHERIT_MASK_SKIP_CHILD
        skip = preparation_child;
#endif
        if (!skip) {
            startup_mask_leave(preparation_previous);
            preparation_active = 0;
        }
    }
    return mask_is(preparation_previous);
}

#ifdef INHERIT_SIGNAL
extern void __restore_rt(void);
static volatile unsigned signal_calls, signal_bad;
static int signal_published;
#ifdef INHERIT_SIGNAL_ABORT
static int signal_aborted;
static volatile unsigned signal_abort_calls, signal_descriptor_calls;
#endif
static void inherited_handler(int signo)
{
    int saved_errno = errno;
    unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    ++signal_calls;
#ifdef INHERIT_SIGNAL_ABORT
    if (signal_aborted) {
        ++signal_abort_calls;
        if (signo != 12 || signal_published)
            signal_bad = 1;
#ifdef INHERIT_SIGNAL_ABORT_FD
        ++signal_descriptor_calls;
        (void)fcntl(10, F_GETFD); /* Deliberately touch unpublished state. */
#endif
        errno = saved_errno;
        return;
    }
#endif
    if (signo != 12 || !signal_published || !startup_ready || poisoned ||
        input != getauxval(0xa001) || output != getauxval(0xa002) ||
        gettid() != memtrap(0x10027, 0, 0, 0, 0) ||
        fcntl(10, F_GETFD) != (preparation_child ? 0 : FD_CLOEXEC)) {
        signal_bad = 1;
        errno = saved_errno;
        return;
    }
    for (unsigned j = 0; j < 3; ++j) {
        unsigned expected =
            (preparation_child ? 0x77000000u : 0x76000000u) + (j << 16) + gen;
        if (refs[j] != expected || fds[j] != j || rights[j] != (j ? 2u : 1u) ||
            !live[j] || startup_users[j] != (j ? 1u : 2u)) {
            signal_bad = 1;
            errno = saved_errno;
            return;
        }
    }
#ifdef INHERIT_SIGNAL_ABORT
    ++signal_descriptor_calls;
#endif
    if (fcntl(10, F_DUPFD_CLOEXEC, 11) != 11 || close(11) ||
        startup_users[0] != 2)
        signal_bad = 1;
    errno = saved_errno;
}
static int signal_prepare(void)
{
    uint64_t record[4] = {(uintptr_t)inherited_handler, 0x04000000,
                          (uintptr_t)__restore_rt, 4};
    return !memtrap(0x29001, 12, (uintptr_t)record, 0, 8) &&
           !memtrap(0x29002, 12, 0, 0, 0) && !memtrap(0x29002, 12, 0, 0, 0) &&
           signal_calls == 0;
}
static int signal_release(int completed)
{
    signal_published = completed;
#ifdef INHERIT_SIGNAL_REF
    if (preparation_child)
        refs[0] ^= 1;
#endif
    int saved_errno = errno = ERANGE;
    return preparation_restore() && signal_calls == 1 && !signal_bad &&
           errno == saved_errno;
}
#endif

static int completion_read(unsigned char *b)
{
#ifdef INHERIT_FINAL_PAD
    unsigned used = 0;
    for (unsigned i = 0; i < 256; ++i) {
        long n =
            (long)memtrap(0x24001, input, (uintptr_t)(b + used), 32 - used, 0);
        if (n == -11) {
            if (used)
                return 1; /* Deliberately accept a zero-padded incomplete frame.
                           */
            memtrap(0x1fffe, 0, 0, 0, 0);
            continue;
        }
        if (n <= 0 || (unsigned long)n > 32 - used)
            return 0;
        used += (unsigned)n;
        if (used == 32)
            return 1;
    }
    return 0;
#else
    return move(b, 32, 0);
#endif
}
static int record(unsigned op, int write)
{
    unsigned char b[32] = {0};
    put(b, 0, op);
    if (!(op == 67 && !write ? completion_read(b) : move(b, 32, write)) ||
        get(b, 0) != op)
        return 0;
    for (unsigned i = 4; i < 32; ++i)
        if (b[i])
            return 0;
    return 1;
}
/* One diagnostic probe is permitted while the parent still awaits publication.
 */
static unsigned completion(void)
{
    for (unsigned i = 0; i < 2; ++i) {
        unsigned char b[32] = {0};
        if (!completion_read(b))
            return 0;
        for (unsigned j = 4; j < 32; ++j)
            if (b[j])
                return 0;
        unsigned op = get(b, 0);
        if (op == 67 || op == 68)
            return op;
        if (op != 69 || i || !record(70, 1))
            return 0;
    }
    return 0;
}
static int ready(void)
{
#if defined(INHERIT_ACK_PARTIAL) || defined(INHERIT_ACK_MISSING)
#ifdef INHERIT_ACK_PARTIAL
    unsigned char b[32] = {0};
    put(b, 0, 66);
    if (!move(b, 16, 1))
        return 0;
#endif
    /* Deliberately stalled publication fixture; owner must stop this context.
     */
    for (;;)
        memtrap(0x1fffe, 0, 0, 0, 0);
#else
    return record(66, 1);
#endif
}
static int read_byte(int fd, char expected)
{
    char b = 0;
    return read(fd, &b, 1) == 1 && b == expected;
}
#ifdef INHERIT_UNCERTAIN
static int uncertain_client(int child)
{
#ifdef INHERIT_UNCERTAIN_CLOSE
    if (fcntl(10, F_GETFD) != (child ? 0 : FD_CLOEXEC) || close(0))
        return 255;
    const int fds[] = {10, 1, 2};
    for (unsigned i = 0; i < 3; ++i) {
        errno = 0;
        int status = close(fds[i]);
        if ((child ? status != -1 || errno != EIO : status != 0) ||
            !record(70, 1))
            return 255;
        errno = 0;
        if (close(fds[i]) != -1 || errno != EBADF)
            return 255;
    }
    return child ? 77 : 76;
#else
    for (unsigned i = 0; i < 2; ++i) {
        char b = 'z';
        errno = 0;
#ifdef INHERIT_UNCERTAIN_WRITE
        if (write(1, &b, 1) != -1 || errno != EIO || b != 'z' ||
#else
        if (read(i ? 10 : 0, &b, 1) != -1 || errno != EIO || b != 'z' ||
#endif
            !record(70, 1))
            return 254;
    }
    if (fcntl(10, F_GETFD) != (child ? 0 : FD_CLOEXEC) || close(0))
        return 254;
    const int fds[] = {10, 1, 2};
    for (unsigned i = 0; i < 3; ++i) {
        errno = 0;
        if (close(fds[i]) != -1 || errno != EIO)
            return 254;
        errno = 0;
        if (close(fds[i]) != -1 || errno != EBADF)
            return 254;
    }
    return child ? 75 : 74;
#endif
}
#endif
static int prepare_valid(unsigned generation)
{
    unsigned counts[BINDINGS] = {0};
    if (!startup_ready || poisoned || !input || !output || input == output)
        return 0;
    for (unsigned i = 0; i < 16; ++i) {
        struct startup_fd f = startup_fds[i];
        if (f.present != 0 && f.present != 1)
            return 0;
        if (!f.present) {
            if (f.binding || f.flags)
                return 0;
            continue;
        }
        if (f.binding >= BINDINGS || (f.flags & ~FD_CLOEXEC))
            return 0;
        counts[f.binding]++;
    }
    for (unsigned j = 0; j < BINDINGS; ++j) {
#ifdef SCRATCH_CLIENT
        if (j >= 3) {
#ifdef SCRATCH_COPY
            if (j == 3) {
                if (live[j] != 1 || counts[j] != 2 || startup_users[j] != 2 ||
                    refs[j] != (0xfc000011u | (generation << 16) |
                                (generation << 8)) ||
                    fds[j] != 3 || rights[j] != 2)
                    return 0;
                continue;
            }
#endif
            if (live[j] || counts[j] || startup_users[j])
                return 0;
            continue;
        }
#endif
        if (live[j] != 1 || !counts[j] || counts[j] != startup_users[j] ||
            refs[j] != 0x76000000u + (j << 16) + generation || fds[j] != j ||
            rights[j] != (j ? 2u : 1u))
            return 0;
    }
    return 1;
}
#ifdef INHERIT_PREPARE_SKIP
#define INHERIT_PREPARE_FAULT 5
#endif
static int inherit_run(void)
{
    if (!mask_is(held_mask()))
        return 79;
    unsigned generation = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
#ifdef INHERIT_PREPARE_FAULT
    switch (INHERIT_PREPARE_FAULT) {
    case 1:
        startup_fds[10].present = 2;
        break;
    case 2:
        startup_fds[10].flags = 2;
        break;
    case 3:
        startup_fds[10].binding = BINDINGS;
        break;
    case 4:
        startup_fds[9].binding = 1;
        break;
    case 5:
        startup_users[0]++;
        break;
    case 6:
        live[0] = 0;
        break;
    case 7:
        rights[1] = 3;
        break;
    case 8:
        refs[0] ^= 1;
        break;
    case 9:
        poisoned = 1;
        break;
    }
#endif
    int valid = prepare_valid(generation);
#ifndef INHERIT_PREPARE_SKIP
    if (!valid)
        return 78;
#else
    (void)valid; /* Deliberate omission of the preparation gate. */
#endif
    unsigned char plan[96] = {0};
    put(plan, 0, 64);
    put(plan, 4, 1);
    put(plan, 8, generation);
    put(plan, 12, 16);
    for (unsigned i = 0; i < 16; ++i) {
        plan[32 + i * 4] = startup_fds[i].binding;
        plan[33 + i * 4] = startup_fds[i].flags;
        plan[34 + i * 4] = startup_fds[i].present;
    }
    if (!mask_is(held_mask()) || !move(plan, sizeof plan, 1) ||
        !mask_is(held_mask()))
        return 250;
    unsigned long op = 0x23003, memory = 0, reader = 0, writer = 0;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+D"(memory), "+S"(reader), "+d"(writer),
                           "+r"(r10), "+r"(r8), "+r"(r9)
                         :
                         : "rcx", "r11", "memory");
#ifdef INHERIT_ROLLBACK
    if ((long)op != -11)
        return 253;
#else
    if ((long)op < 0)
        return 250;
#endif
    if (!mask_is(held_mask()))
        return 79;
    if (!op) {
        preparation_child = 1;
        if (!copy_rebind(memory, reader, writer, &input, &output))
            return 251;
        if (!mask_is(held_mask()))
            return 79;
#if defined(INHERIT_SIGNAL) && !defined(INHERIT_SIGNAL_NO_POST)
        if (memtrap(0x29002, 12, 0, 0, 0) || signal_calls)
            return 79;
#endif
        unsigned char receipt[32] = {0};
#ifndef INHERIT_SKIP_RECEIPT
        unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
#endif
        if (!move(receipt, 32, 0))
            return 251;
#ifndef INHERIT_SKIP_RECEIPT
        if (get(receipt, 0) != 65 || get(receipt, 4) != gen ||
            get(receipt, 8) != 1)
            return 251;
#ifdef SCRATCH_COPY
        if (get(receipt, 24) != (0xfc000019u | (gen << 16) | (gen << 8)) ||
            get(receipt, 28) != (0xfd000002u | (gen << 16) | (gen << 8)))
            return 251;
        refs[3] = get(receipt, 24);
        scratch_root = get(receipt, 28);
#else
        for (unsigned i = 24; i < 32; ++i)
            if (receipt[i])
                return 251;
#endif
        for (unsigned j = 0; j < 3; ++j)
            if (get(receipt, 12 + j * 4) != 0x77000000u + (j << 16) + gen)
                return 251;
#endif
        for (unsigned j = 0; j < 3; ++j)
            refs[j] = get(receipt, 12 + j * 4);
        if (fcntl(10, F_GETFD) != FD_CLOEXEC || fcntl(10, F_SETFD, 0) ||
            !ready() ||
#ifndef INHERIT_SKIP_CHILD_GATE
            !record(67, 0) ||
#endif
#ifdef INHERIT_SIGNAL
            !signal_release(1) ||
#else
            !preparation_restore() ||
#endif
#ifdef INHERIT_UNCERTAIN
            0)
            return 251;
        return uncertain_client(1);
#else
#ifdef SCRATCH_COPY
#ifdef SCRATCH_EXEC
            !scratch_exec_request() ||
#else
            !scratch_copy_finish(1) ||
#endif
#endif
            !read_byte(0, 'b') || !read_byte(0, 'd') || close(0) ||
            !read_byte(10, 'e') || close(10) || close(1) || close(2))
            return 251;
        return 72;
#endif
    }
#ifdef INHERIT_SKIP_PARENT_GATE
    unsigned outcome = 68;
    (void)completion; /* Deliberately expose application I/O before owner
                         completion. */
#else
    unsigned outcome = completion();
#endif
#ifdef INHERIT_SIGNAL_OUTCOME
    outcome = 0; /* Deliberately corrupt the decoded completion. */
#endif
#ifdef INHERIT_SIGNAL
    if (!signal_release(outcome == 67 || outcome == 68))
#else
    if (!preparation_restore())
#endif
        return 79;
    if (outcome == 68) {
        if (!read_byte(0, 'a') || !read_byte(10, 'b') ||
            fcntl(10, F_GETFD) != FD_CLOEXEC || close(0) || close(10) ||
            close(1) || close(2))
            return 252;
        return 73;
    }
#ifdef INHERIT_UNCERTAIN
    if (outcome != 67)
        return 252;
    return uncertain_client(0);
#else
    if (outcome != 67 ||
#ifdef SCRATCH_COPY
        !scratch_copy_finish(0) ||
#endif
        !read_byte(0, 'a') || !read_byte(10, 'c') ||
        fcntl(10, F_GETFD) != FD_CLOEXEC || close(0) || close(10) || close(1) ||
        close(2))
        return 252;
    return 71;
#endif
}

#ifdef SCRATCH_EXEC
int main(int argc, char **argv)
#else
int main(void)
#endif
{
#ifdef SCRATCH_EXEC
    if (argc == 1 && !strcmp(argv[0], "scratch-next"))
        return scratch_exec_replacement();
#endif
    if (cookie != 23 || !startup_begin() || fcntl(0, F_DUPFD_CLOEXEC, 10) != 10)
        return 250;
#ifdef SCRATCH_CLIENT
    if (!scratch_probe())
        return 252;
#endif
#ifdef INHERIT_SIGNAL
    uint64_t signal_seed = 16;
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&signal_seed, 0, 8))
        return 79;
#endif
#ifdef INHERIT_MASK_SEED
    uint64_t seed =
        (UINT64_C(1) << (SIGUSR1 - 1)) | (UINT64_C(1) << (SIGUSR2 - 1));
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&seed, 0, 8) || !mask_is(seed))
        return 79;
#endif
#ifdef INHERIT_MASK_SKIP_ENTER
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&preparation_previous, 8))
        return 79;
#else
    if (startup_mask_enter(&preparation_previous))
        return 79;
#endif
    preparation_active = 1;
#ifdef INHERIT_SIGNAL
    if (!signal_prepare())
        return 79;
#ifdef INHERIT_SIGNAL_EARLY
    startup_mask_leave(preparation_previous);
    return signal_bad ? 79 : 250;
#endif
#endif
    int result = inherit_run();
#ifdef INHERIT_SIGNAL_ABORT
#ifndef INHERIT_SIGNAL_ABORT_SKIP
    signal_aborted = !signal_published &&
                     (result == 78 || (preparation_child && result == 251));
#endif
    int abort_errno = errno = ERANGE;
#endif
    if (!preparation_restore())
        return 79;
#ifdef INHERIT_SIGNAL_ABORT
    if (errno != abort_errno ||
        signal_abort_calls != (signal_aborted ? 1u : 0u) ||
        signal_descriptor_calls != (signal_aborted ? 0u : 1u))
        return 79;
#endif
#ifdef INHERIT_SIGNAL
    if (signal_calls != 1 || signal_bad)
        return 79;
#endif
    return result;
}
