/* SPDX-License-Identifier: BSD-2-Clause */
/* Isolated public musl fork experiment; not an installed SDK implementation. */
#if defined(FORK_DASH_SIGNAL_NO_POST) || defined(FORK_DASH_SIGNAL_SCOPE)
#define FORK_DASH_SIGNAL
#endif
#ifdef FORK_DASH_SIGNAL
#define FORK_DASH_PIPE
#endif
#ifdef FORK_DASH_PIPE_CONSUMER
#define FORK_DASH_PIPE_EXEC
#endif
#ifdef FORK_DASH_PIPE_SERIAL_EXEC
#define FORK_DASH_PIPE_EXEC
#define FORK_DASH_PIPE_SERIAL
#endif
#ifdef FORK_DASH_PIPE_EXEC
#define FORK_DASH_PIPE
#define EXEC_MASK
#endif
#ifdef FORK_DASH_PIPE_SERIAL
#define FORK_DASH_PIPE_REPEAT
#endif
#ifdef FORK_DASH_PIPE_REPEAT
#define FORK_DASH_PIPE
#endif
#ifdef FORK_DASH_PIPE_HEADER
#define FORK_DASH_PIPE
#endif
#ifdef FORK_DASH_PIPE
#define FORK_PIPE_SIGNAL
#define FORK_WAIT3
#endif
#if defined(FORK_PIPE_SIGNAL_BLOCK) || defined(FORK_PIPE_SIGNAL_NO_POST) ||    \
    defined(FORK_PIPE_SIGNAL_NO_POLL)
#define FORK_PIPE_SIGNAL
#endif
#ifdef FORK_PIPE_SIGNAL
#define FORK_PIPE
#define STARTUP_PUBLIC_ACTION
#endif
#if defined(FORK_PIPE_BAD_REPLY) || defined(FORK_PIPE_REPLY_LOSS) ||           \
    defined(FORK_PIPE_FAULT) || defined(FORK_PIPE_STOP)
#define FORK_PIPE
#endif
#ifdef FORK_PIPE
#define FORK_WAIT
#define STARTUP_IDENTITY
#define STARTUP_CWD
#endif
#if defined(FORK_CONSOLE_OLD_CLEANUP) || defined(FORK_REDIRECT_STALE) ||       \
    defined(FORK_REDIRECT_EXEC_STALE)
#define FORK_CONSOLE
#endif
#ifdef FORK_FAILED_SKIP
#define FORK_SHELL_FAILED_EXEC
#endif
#ifdef FORK_SHELL_FAILED_EXEC
#define FORK_SHELL_ARGV
#endif
#ifdef FORK_SHELL_NULL_WAIT
#define FORK_SHELL_NULL
#endif
#ifdef FORK_SHELL_NULL_FAULT
#define FORK_SHELL_NULL
#endif
#ifdef FORK_SHELL_NULL_MASK
#define FORK_SHELL_NULL
#define EXEC_MASK_SKIP_FAILURE
#endif
#ifdef FORK_SHELL_NULL
#define FORK_SHELL_ARGV
#define FORK_NULL
#endif
#ifdef FORK_SHELL_FILES
#define FORK_SHELL_ARGV
#define SCRATCH_CLIENT
#endif
#ifdef FORK_SHELL_CLOSED
#define FORK_SHELL_ARGV
#endif
#ifdef FORK_SHELL_ARGV
#define FORK_SHELL_COMMAND
#endif
#ifdef FORK_CONSOLE
#define FORK_SHELL_COMMAND
#endif
#ifdef FORK_SHELL_COMMAND
#define FORK_SHELL
#endif
#ifdef FORK_SHELL_SKIP
#define FORK_SHELL
#endif
#ifdef FORK_SHELL
#define FORK_DISPATCH
#define FORK_WAIT3
#define STARTUP_PUBLIC_ACTION
#define STARTUP_IDENTITY
#define STARTUP_CWD
#endif
#ifdef FORK_PRELUDE
#define FORK_DISPATCH
#endif
#ifdef FORK_DISPATCH_LATE
#define FORK_DISPATCH
#endif
#ifdef FORK_DISPATCH
#define FORK_EXEC
#endif
#if defined(FORK_LIVE_DENY) || defined(FORK_LIVE_ORDER) ||                     \
    defined(FORK_LIVE_NO_POST)
#define FORK_LIVE
#endif
#ifdef FORK_LIVE_DENY
#define FORK_DENY
#endif
#ifdef FORK_LIVE
#include <pthread.h>
#endif
#ifdef FORK_WAIT3_FAULT
#define FORK_WAIT_FAULT
#define FORK_WAIT3
#endif
#ifdef FORK_WAIT3_BROKEN
#define FORK_WAIT_BROKEN_ACK
#define FORK_WAIT3
#endif
#if defined(FORK_WAIT3) || defined(FORK_WAIT4_USAGE_BAD)
#define FORK_WAIT4
#endif
#ifdef FORK_WAIT4
#define FORK_WAIT
#include <sys/resource.h>
#endif
#if defined(FORK_WAIT_BROKEN_PARTIAL) || defined(FORK_WAIT_BROKEN_ACK) ||      \
    defined(FORK_WAIT_BROKEN_REPLAY) || defined(FORK_WAIT_BROKEN_FALSE)
#define FORK_WAIT_BROKEN
#endif
#ifdef FORK_WAIT_BROKEN_FALSE
#define FORK_WAIT_BROKEN_ACK
#endif
#ifdef FORK_WAIT_BROKEN
#define FORK_WAIT
#endif
#if defined(FORK_WAIT_NULL) || defined(FORK_WAIT_FAULT) ||                     \
    defined(FORK_WAIT_SIGNAL) || defined(FORK_WAIT_HIGH)
#define FORK_WAIT
#endif
#ifdef FORK_EXEC
#define FORK_WAIT
#define EXEC_MASK
#endif
#ifdef FORK_WAIT_SUSPEND_FRAME_VALID
#define FORK_WAIT_SUSPEND_FRAME
#endif
#ifdef FORK_WAIT_SUSPEND_STALE_POST
#define FORK_WAIT_SUSPEND_STALE
#endif
#ifdef FORK_WAIT_SUSPEND_REPEAT_POST
#define FORK_WAIT_SUSPEND_REPEAT
#endif
#if defined(FORK_WAIT_SUSPEND_SKIP) || defined(FORK_WAIT_SUSPEND_IGNORE) ||    \
    defined(FORK_WAIT_SUSPEND_BLOCK) || defined(FORK_WAIT_SUSPEND_REPEAT) ||   \
    defined(FORK_WAIT_SUSPEND_STALE) || defined(FORK_WAIT_SUSPEND_FRAME)
#define FORK_WAIT_SUSPEND
#endif
#ifdef FORK_WAIT_SUSPEND
#define FORK_WAIT
#define STARTUP_PUBLIC_ACTION
#endif
#ifdef FORK_WAIT
#include <sys/wait.h>
#endif
#ifdef FORK_WAIT_BROKEN_REPLAY
#define ALLOW_POISON_TRAFFIC // Deliberately bypass both wait and transport
                             // guards.
#endif
#if defined(FORK_PIPE) && defined(FORK_EXEC)
#error "pipe descriptors across exec are not qualified"
#endif
#define CAT_ROLES
#define SHELL_STARTUP
#include "../native-command/transport.h"
#ifdef FORK_SHELL_FILES
#include "scratch-client.h"
#include "scratch-fork.h"
#endif
#ifdef FORK_NULL
#include "null-client.h"
#endif
#if defined(FORK_EXEC) || defined(FORK_DASH_PIPE_EXEC)
#include "exec-stage.h"
#endif
int copy_rebind(unsigned long, unsigned long, unsigned long, unsigned long *,
                unsigned long *);
static _Thread_local volatile unsigned cookie = 23;
static volatile unsigned private_value = 41;
static int mask_is(uint64_t expected)
{
    uint64_t actual = 0;
    return !memtrap(0x1000e, 0, 0, (uintptr_t)&actual, 8) && actual == expected;
}
static uint64_t held_mask(void)
{
    return UINT64_MAX & ~((UINT64_C(1) << 8) | (UINT64_C(1) << 18));
}
#ifdef FORK_LIVE
extern void __restore_rt(void);
static volatile unsigned callback_trace, callback_bad, signal_calls;
static int stage_complete;
static long original_pid;
static void prepare_one(void)
{
    if (!mask_is(16))
        callback_bad = 1;
    callback_trace = callback_trace * 10 + 1;
}
static void prepare_two(void)
{
    if (!mask_is(16))
        callback_bad = 1;
    callback_trace = callback_trace * 10 + 2;
}
static void after_fork(unsigned digit, int child)
{
    int saved = errno;
    if (!mask_is(16) || signal_calls != 1 || !stage_complete ||
        (getpid() != original_pid) != child ||
        gettid() != memtrap(0x10027, 0, 0, 0, 0) ||
        fcntl(10, F_GETFD) != FD_CLOEXEC)
        callback_bad = 1;
    callback_trace = callback_trace * 10 + digit;
    errno = saved;
}
static void parent_one(void) { after_fork(4, 0); }
static void parent_two(void) { after_fork(5, 0); }
static void child_one(void) { after_fork(6, 1); }
static void child_two(void) { after_fork(7, 1); }
static void fork_signal(int signo)
{
    int saved = errno;
    int child = getpid() != original_pid;
    unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    ++signal_calls;
    if (signo != 12 || !stage_complete || callback_trace != 21 ||
        gettid() != memtrap(0x10027, 0, 0, 0, 0) ||
        input != getauxval(0xa001) || output != getauxval(0xa002) ||
        fcntl(10, F_GETFD) != FD_CLOEXEC)
        callback_bad = 1;
    for (unsigned j = 0; j < 3; ++j)
        if (refs[j] != (child ? 0x77000000u : 0x76000000u) + (j << 16) + gen ||
            !live[j] || startup_users[j] != (j ? 1u : 2u))
            callback_bad = 1;
    callback_trace = callback_trace * 10 + 3;
    errno = saved;
}
static int callbacks_begin(void)
{
    original_pid = getpid();
#ifdef FORK_LIVE_ORDER
    if (pthread_atfork(prepare_two, parent_two, child_two) ||
        pthread_atfork(prepare_one, parent_one, child_one))
        return 0;
#else
    if (pthread_atfork(prepare_one, parent_one, child_one) ||
        pthread_atfork(prepare_two, parent_two, child_two))
        return 0;
#endif
    uint64_t action[4] = {(uintptr_t)fork_signal, 0x04000000,
                          (uintptr_t)__restore_rt, 4};
    return !memtrap(0x29001, 12, (uintptr_t)action, 0, 8);
}
#endif
static void failed_stage(void)
{
    /* Unknown staging outcome cannot safely return a retryable fork failure. */
    _exit(80);
}
static int record(unsigned op, int write)
{
    unsigned char b[32] = {0};
    put(b, 0, op);
    if (!(op == 67 && !write ? move(b, 32, 0) : move(b, 32, write)) ||
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
        if (!move(b, 32, 0))
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
static int prepare_valid(unsigned generation)
{
    unsigned counts[BINDINGS] = {0};
#ifdef FORK_DASH_PIPE_REPEAT
    unsigned pipe_generation = (refs[3] >> 8) & 0xff;
    if (pipe_generation < 1 || pipe_generation > 2)
        return 0;
#endif
    if (!startup_ready || poisoned || !input || !output || input == output)
        return 0;
    for (unsigned i = 0; i < 16; ++i) {
        struct startup_fd f = startup_fds[i];
        if (f.present != 0 && f.present != 1)
            return 0;
        /* Closed slots may retain local binding/flag metadata. They own no
         * reference; only live slots contribute to the inherited snapshot. */
        if (!f.present)
            continue;
        if (f.binding >= BINDINGS || (f.flags & ~FD_CLOEXEC))
            return 0;
        counts[f.binding]++;
    }
#ifdef FORK_SHELL_FILES
    if (!scratch_fork_valid(generation, counts))
        return 0;
#endif
    for (unsigned j = 0; j < BINDINGS; ++j) {
#ifdef FORK_SHELL_FILES
        if (j >= 3)
            continue;
#endif
#ifdef FORK_NULL
        if (j == 3) {
            if (live[j] || counts[j] || startup_users[j])
                return 0;
            continue;
        }
#endif
        if (live[j] != 1 || !counts[j] || counts[j] != startup_users[j] ||
            refs[j] !=
#ifdef FORK_PIPE
                (j >= 3 ?
#ifdef FORK_DASH_PIPE_REPEAT
                        0x78000000u + (pipe_generation << 8) + j - 2
#else
                        0x78000100u + j - 2
#endif
                        : 0x76000000u + (j << 16) + generation) ||
#else
                0x76000000u + (j << 16) + generation ||
#endif
            fds[j] != j || rights[j] != ((j == 0 || j == 3) ? 1u : 2u))
            return 0;
    }
    return 1;
}

long __aether_fork_stage(void)
{
    unsigned generation = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    if (!mask_is(held_mask()))
        failed_stage();
#ifdef FORK_LIVE
    if (callback_trace != 21 || callback_bad || signal_calls)
        _exit(81);
    if (memtrap(0x29002, 12, 0, 0, 0) || memtrap(0x29002, 12, 0, 0, 0) ||
        signal_calls)
        _exit(81);
#endif
#ifdef FORK_DENY
#ifdef FORK_LIVE
    stage_complete = 1;
#endif
    return -ENOTSUP;
#endif
    if (!prepare_valid(generation))
        return -ENOTSUP;
    unsigned char plan[96] = {0};
    put(plan, 0, 64);
#if defined(FORK_PIPE) && !defined(FORK_DASH_PIPE_HEADER)
    put(plan, 4, 2);
#else
    put(plan, 4, 1);
#endif
    put(plan, 8, generation);
    put(plan, 12, 16);
    for (unsigned i = 0; i < 16; ++i) {
#ifndef FORK_REDIRECT_STALE
        /* The wire requires canonical zero entries for absent descriptors. */
        if (!startup_fds[i].present)
            continue;
#endif
        plan[32 + i * 4] = startup_fds[i].binding;
        plan[33 + i * 4] = startup_fds[i].flags;
        plan[34 + i * 4] = startup_fds[i].present;
    }
    if (!move(plan, sizeof plan, 1))
        failed_stage();
    unsigned long op = 0x23003, memory = 0, reader = 0, writer = 0;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+D"(memory), "+S"(reader), "+d"(writer),
                           "+r"(r10), "+r"(r8), "+r"(r9)
                         :
                         : "rcx", "r11", "memory");
    if (!mask_is(held_mask()))
        failed_stage();
    if (!op) {
        if (!copy_rebind(memory, reader, writer, &input, &output))
            failed_stage();
#ifdef FORK_LIVE
        if (signal_calls)
            _exit(81);
#ifndef FORK_LIVE_NO_POST
        if (memtrap(0x29002, 12, 0, 0, 0) || signal_calls)
            _exit(81);
#endif
#endif
        unsigned char receipt[32] = {0};
        unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
        if (!move(receipt, 32, 0) || get(receipt, 0) != 65 ||
            get(receipt, 4) != gen ||
            get(receipt, 8) !=
#ifdef FORK_PIPE
                2)
#else
                1)
#endif
            failed_stage();
#ifndef FORK_PIPE
        for (unsigned i = 24; i < 32; ++i)
            if (receipt[i])
                failed_stage();
#endif
        for (unsigned j = 0; j <
#if defined(FORK_NULL) || defined(FORK_SHELL_FILES)
                             3
#else
                             BINDINGS
#endif
             ;
             ++j) {
            unsigned expected = 0x77000000u + (j << 16) + gen;
#ifdef FORK_PIPE
            if (j >= 3)
                expected = refs[j];
#endif
            if (get(receipt, 12 + j * 4) != expected)
                failed_stage();
        }
        for (unsigned j = 0; j <
#if defined(FORK_NULL) || defined(FORK_SHELL_FILES)
                             3
#else
                             BINDINGS
#endif
             ;
             ++j)
            refs[j] = get(receipt, 12 + j * 4);
#ifdef FORK_SHELL_FILES
        if (!scratch_fork_rebind()) {
            poisoned =
                1; /* No cleanup traffic through unvalidated file refs. */
            failed_stage();
        }
#endif
#ifdef FORK_BAD_FLAG
        startup_fds[10].flags = 0;
#endif
        if (!record(66, 1) || !record(67, 0))
            failed_stage();
#ifdef FORK_NULL
        if (!null_accept(0))
            failed_stage();
#endif
    } else {
        unsigned done = completion();
        if ((long)op == -EAGAIN && done == 68) {
#ifdef FORK_LIVE
            stage_complete = 1;
#endif
            return -EAGAIN;
        }
        if ((long)op <= 0 || done != 67)
            failed_stage();
    }
    if (!mask_is(held_mask()))
        failed_stage();
#ifdef FORK_LIVE
    stage_complete = 1;
#endif
    return (long)op;
}
#ifdef FORK_WAIT
static int wait_poisoned;
static int wait_reply(unsigned char *reply)
{
    if (!move(reply, 32, 0))
        return 0;
    for (unsigned i = 8; i < 32; ++i)
        if (reply[i])
            return 0;
    return 1;
}
static long wait_body(int *status)
{
    for (unsigned i = 0; i < 100000; ++i) {
        long n = memtrap(0x24001, input, (uintptr_t)status, 4, 0);
        if (n != -EAGAIN)
            return n;
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
    return -EIO;
}
static long wait_exchange(int pid, int *status, int options)
{
    unsigned char request[32] = {0}, reply[32] = {0};
    put(request, 0, 80);
    put(request, 4, (unsigned)pid);
    put(request, 8, (unsigned)options);
    if (!move(request, 32, 1) || !wait_reply(reply))
        goto broken;
    int result = (int32_t)get(reply, 0);
    unsigned token = get(reply, 4);
    if (result <= 0) {
        if (token || (result != 0 && result != -ECHILD && result != -EINVAL))
            goto broken;
        return result;
    }
    if (token != (unsigned)result || (pid != -1 && result != pid))
        goto broken;
    int discarded;
    long n = wait_body(status ? status : &discarded);
    if (n == -EFAULT) {
        if (wait_body(&discarded) != 4)
            goto broken;
        return -EFAULT; // Retained at owner: no acknowledgment after failed
                        // copy.
    }
    if (n != 4)
        goto broken;
    put(request, 0, 81);
    put(request, 4, token);
    put(request, 8, 0);
#ifdef FORK_WAIT_BROKEN_FALSE
    (void)move(request, 32, 1);
    (void)wait_reply(reply);
    return result; // Deliberate acceptance of an invalid acknowledgment.
#endif
    if (!move(request, 32, 1) || !wait_reply(reply) || get(reply, 0) ||
        get(reply, 4))
        goto broken;
    return result;
broken:
    wait_poisoned = 1;
    return -EIO;
}
long __aether_waitpid(int pid, int *status, int options)
{
#ifndef FORK_WAIT_BROKEN_REPLAY
    if (wait_poisoned)
        return -EIO;
#endif
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return -EIO;
    long result;
    do {
        result = wait_exchange(pid, status, options);
    } while (!result && !options);
    startup_mask_leave(previous);
    return result;
}
static pid_t checked_wait(pid_t pid, int *status, int options)
{
#ifdef FORK_WAIT3
    if (pid == -1)
        return wait3(status, options, 0);
#endif
#ifdef FORK_WAIT4
    return wait4(pid, status, options, 0);
#else
    return waitpid(pid, status, options);
#endif
}
#ifdef FORK_WAIT_SUSPEND
#include "suspend-check.h"
#endif
__attribute__((unused)) static int wait_checks(pid_t child)
{
    int status = 0x12345678;
#ifdef FORK_WAIT4
    struct rusage usage;
    memset(&usage, 0xa5, sizeof usage);
    errno = 0;
    if (wait4(child, &status, WNOHANG, &usage) != -1 || errno != ENOTSUP ||
        status != 0x12345678)
        return 0;
    errno = 0;
    if (wait3(&status, WNOHANG, &usage) != -1 || errno != ENOTSUP ||
        status != 0x12345678)
        return 0;
    for (unsigned i = 0; i < sizeof usage; ++i)
        if (((unsigned char *)&usage)[i] != 0xa5)
            return 0;
    errno = 0;
    if (wait4(child, &status, 0, (struct rusage *)(uintptr_t)1) != -1 ||
        errno != ENOTSUP || status != 0x12345678)
        return 0;
    errno = 0;
    if (wait3(&status, 0, (struct rusage *)(uintptr_t)1) != -1 ||
        errno != ENOTSUP || status != 0x12345678 || !mask_is(16))
        return 0;
#endif
#ifdef FORK_WAIT_SUSPEND
    struct sigaction action = {0}, old;
    sigset_t original, temporary;
    action.sa_handler = suspend_handler;
#ifdef FORK_WAIT_SUSPEND_IGNORE
    action.sa_handler = SIG_IGN;
#endif
    sigemptyset(&action.sa_mask);
    sigemptyset(&original);
    sigaddset(&original, SIGCHLD);
    sigaddset(&original, SIGTRAP);
    sigemptyset(&temporary);
    sigaddset(&temporary, SIGINT);
#ifdef FORK_WAIT_SUSPEND_BLOCK
    sigaddset(&temporary, SIGCHLD);
#endif
    if (sigaction(SIGCHLD, &action, &old))
        memtrap(0x100e7, 234, 0, 0, 0);
    if (sigprocmask(SIG_SETMASK, &original, 0))
        memtrap(0x100e7, 235, 0, 0, 0);
#endif
    if (checked_wait(child, &status, WNOHANG) != 0 || status != 0x12345678)
        return 0;
#ifdef FORK_WAIT_SUSPEND_FRAME
    if (!suspend_rejection_check(&temporary))
        memtrap(0x100e7, 238, 0, 0, 0);
#endif
#if defined(FORK_WAIT_SUSPEND) && !defined(FORK_WAIT_SUSPEND_SKIP)
    errno = 0;
    if (suspend_calls || sigsuspend(&temporary) != -1 || errno != EINTR ||
        suspend_calls != 1 || suspend_bad ||
        !mask_is(16 | (1u << (SIGCHLD - 1))))
        return 0;
    sigemptyset(&temporary);
    sigaddset(&temporary, SIGTRAP);
#ifndef FORK_WAIT_SUSPEND_REPEAT
    if (sigaction(SIGCHLD, &old, 0))
        return 0;
#endif
    if (sigprocmask(SIG_SETMASK, &temporary, 0))
        return 0;
#endif
    errno = 0;
    if (checked_wait(child + 1, &status, 0) != -1 || errno != ECHILD ||
        status != 0x12345678)
        return 0;
#ifdef FORK_WAIT_SUSPEND_REPEAT
#ifdef FORK_WAIT_SUSPEND_REPEAT_POST
    (void)memtrap(0x29002, SIGCHLD, 0, 0, 0);
#endif
    if (memtrap(0x29002, 0, 0, 0, 0) || suspend_calls != 1 || suspend_bad ||
        !mask_is(16) || sigaction(SIGCHLD, &old, 0))
        memtrap(0x100e7, 236, 0, 0, 0);
#endif
    errno = 0;
    if (checked_wait(child, &status, 2) != -1 || errno != EINVAL ||
        status != 0x12345678)
        return 0;
    errno = 0;
    if (checked_wait(child, (int *)(uintptr_t)1, 0) != -1 || errno != EFAULT)
        return 0;
#ifdef FORK_WAIT_BROKEN
    errno = 0;
    if (checked_wait(-1, &status, 0) != -1 || errno != EIO || !mask_is(16))
        return 0;
#ifdef FORK_WAIT_BROKEN_ACK
    if (status != (72 << 8))
#elif defined(FORK_WAIT_BROKEN_PARTIAL)
    if (status != 0x12344800)
#else
    if (status != 0x12345678)
#endif
        return 0;
    status = 0x12345678;
    errno = 0;
    return checked_wait(child, &status, 0) == -1 && errno == EIO &&
           status == 0x12345678 && mask_is(16);
#endif
#ifdef FORK_WAIT_NULL
    if (checked_wait(-1, 0, 0) != child || status != 0x12345678)
        return 0;
#else
    if (checked_wait(-1, &status, 0) != child)
        return 0;
#if defined(FORK_WAIT_FAULT) || defined(FORK_WAIT_SIGNAL)
    if (!WIFSIGNALED(status) || WCOREDUMP(status) ||
#ifdef FORK_WAIT_FAULT
        WTERMSIG(status) != SIGILL)
#else
        WTERMSIG(status) != SIGTERM)
#endif
        return 0;
#else
    if (!WIFEXITED(status) ||
#ifdef FORK_WAIT_HIGH
        WEXITSTATUS(status) != 134)
#else
        WEXITSTATUS(status) != 72)
#endif
        return 0;
#endif
#endif
    errno = 0;
    return checked_wait(child, &status, 0) == -1 && errno == ECHILD &&
           mask_is(16);
}
#endif
static __attribute__((unused)) int read_byte(int fd, char expected)
{
    char b = 0;
    return read(fd, &b, 1) == 1 && b == expected;
}
#ifdef FORK_PIPE
#include "pipe-client.h"
#elif defined(FORK_SHELL)
#include "shell-client.h"
#else
#ifdef FORK_WAIT_SUSPEND_STALE
static int replacement_check(void)
{
    if (memtrap(0x20005, 0, 0, 0, 0) != 2)
        return 1;
    input = getauxval(0xa001);
    output = getauxval(0xa002);
    struct sigaction action = {0}, old;
    sigset_t mask;
    action.sa_handler = suspend_handler;
    sigemptyset(&action.sa_mask);
    sigemptyset(&mask);
    sigaddset(&mask, SIGCHLD);
    if (sigaction(SIGCHLD, &action, &old) ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&mask, 0, 8) || suspend_calls)
        return 0;
    unsigned char record[32] = {0};
    put(record, 0, 86);
    put(record, 4, 2);
    if (!move(record, sizeof record, 1) || !move(record, sizeof record, 0) ||
        get(record, 0) != 87 || get(record, 4) != 2)
        return 0;
    for (unsigned i = 8; i < sizeof record; ++i)
        if (record[i])
            return 0;
#ifdef FORK_WAIT_SUSPEND_STALE_POST
    if (memtrap(0x29002, SIGCHLD, 0, 0, 0))
        return 0;
#endif
    sigemptyset(&mask);
    sigaddset(&mask, SIGINT);
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&mask, 0, 8) ||
        memtrap(0x29002, 0, 0, 0, 0) || suspend_calls || suspend_bad)
        return 0;
    sigemptyset(&mask);
    if (sigaction(SIGCHLD, &old, 0) ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&mask, 0, 8))
        return 0;
    put(record, 0, 88);
    return move(record, sizeof record, 1);
}
#endif
int main(void)
{
#ifdef FORK_WAIT_SUSPEND_STALE
    if (!replacement_check())
        memtrap(0x100e7, 237, 0, 0, 0);
#endif
    if (!startup_begin() || fcntl(0, F_DUPFD_CLOEXEC, 10) != 10)
        return 80;
#ifdef FORK_LIVE
    if (!callbacks_begin())
        return 81;
#endif
#ifdef FORK_PRELUDE
    int before_status = 0x12345678;
    errno = 0;
    if (waitpid(-1, &before_status, WNOHANG) != -1 || errno != ECHILD ||
        before_status != 0x12345678)
        return 86;
    char untouched_before = 'X';
    refs[0] ^= 0x1000000u;
    errno = 0;
    long rejected_before = read(0, &untouched_before, 1);
    refs[0] ^= 0x1000000u;
    if (rejected_before != -1 || errno != EACCES || untouched_before != 'X' ||
        !read_byte(0, 'a'))
        return 86;
#endif
    long parent = getpid();
    uint64_t seed = 16;
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&seed, 0, 8))
        return 80;
    errno = ERANGE;
    pid_t child = fork();
    int saved = errno;
#ifdef FORK_LIVE
    if (callback_bad || signal_calls != 1 ||
        callback_trace != (child == 0 ? 21367u : 21345u))
        return 81;
#endif
    if (!mask_is(seed) || cookie != 23 || private_value != 41 ||
        gettid() != memtrap(0x10027, 0, 0, 0, 0) ||
        fcntl(10, F_GETFD) != FD_CLOEXEC || input != getauxval(0xa001) ||
        output != getauxval(0xa002))
        return 80;
#ifdef FORK_DENY
    return child == -1 && saved == ENOTSUP && getpid() == parent ? 78 : 80;
#endif
    if (child < 0) {
        if (child != -1 || saved != EAGAIN || getpid() != parent ||
            !read_byte(0, 'a') || !read_byte(10, 'b'))
            return 80;
    } else if (!child) {
        if (getpid() == parent || getppid() != parent || saved != ERANGE)
            return 80;
#ifdef FORK_EXEC
        char *args[] = {"exec-stream", "hello", 0};
        char *env[] = {"AETHER_EXEC=1", 0};
        if (fcntl(1, F_SETFD, FD_CLOEXEC))
            return 84;
        execve("/next", args, env);
        return 84; // Successful image replacement cannot return here.
#endif
        cookie = 24;
        private_value = 42;
        if (fcntl(10, F_SETFD, 0) || !read_byte(0, 'b') || !read_byte(0, 'd') ||
            close(0) || !read_byte(10, 'e') || close(10) || close(1) ||
            close(2))
            return 80;
#ifdef FORK_WAIT_FAULT
        __asm__ __volatile__("ud2");
        return 83;
#elif defined(FORK_WAIT_SIGNAL)
        (void)memtrap(0x29002, SIGTERM, 0, 0, 0);
        return 83; // A returning post is not terminal delivery.
#elif defined(FORK_WAIT_HIGH)
        return 134;
#else
        return 72;
#endif
    } else {
        unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
#ifdef FORK_DISPATCH
        if (child != (pid_t)(gen * 4 + 3) || getpid() != parent ||
            saved != ERANGE)
            return 85;
        char untouched = 'X';
        refs[0] ^= 0x1000000u;
        errno = 0;
        long denied = read(0, &untouched, 1);
        refs[0] ^= 0x1000000u;
        if (denied != -1 || errno != EACCES || untouched != 'X')
            return 85;
#ifdef FORK_DISPATCH_LATE
        if (!read_byte(0, 'a'))
            return 85;
#endif
        int status = 0x12345678;
        if (waitpid(child, &status, WNOHANG) != 0 || status != 0x12345678 ||
            waitpid(child, &status, 0) != child || !WIFEXITED(status) ||
            WEXITSTATUS(status) != 72 || !mask_is(16))
            return 85;
        errno = 0;
        if (waitpid(child, &status, 0) != -1 || errno != ECHILD)
            return 85;
#if !defined(FORK_DISPATCH_LATE) && !defined(FORK_PRELUDE)
        if (!read_byte(0, 'b'))
            return 85;
#endif
        if (!read_byte(10, 'c'))
            return 85;
#else
        if (child != (pid_t)(gen * 4 + 3) || getpid() != parent ||
            saved != ERANGE || !read_byte(0, 'a') || !read_byte(10, 'c'))
            return 80;
#endif
    }
    if (cookie != 23 || private_value != 41 ||
        fcntl(10, F_GETFD) != FD_CLOEXEC || close(0) || close(10) || close(1) ||
        close(2))
        return 80;
#if defined(FORK_WAIT) && !defined(FORK_DISPATCH)
    if (child <= 0 || !wait_checks(child))
        return 82;
#endif
    return child < 0 ? 73 : 71;
}

#endif
