/* SPDX-License-Identifier: BSD-2-Clause */
/* Bounded private pipe adapter and opt-in native consumers. */
static unsigned pipe_factory;
static int pipe_grant(void)
{
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return 0;
    unsigned char b[32];
    int ok = move(b, sizeof b, 0) && !memcmp(b, "AEPIPE01", 8) &&
             get(b, 8) == 1 && get(b, 12) == 0x76050001u && get(b, 16) == 256 &&
             get(b, 20) == 16 && get(b, 24) == 1 && !get(b, 28);
    if (ok)
        pipe_factory = get(b, 12);
    else
        poisoned = 1;
    startup_mask_leave(previous);
    return ok;
}
static int native_pipe_pair(int *pair)
{
    if (!pair)
        return startup_error(EFAULT);
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return startup_error(EIO);
    int error = 0, slots[2] = {-1, -1};
    unsigned found = 0;
    for (unsigned i = 0; i < 16 && found < 2; ++i)
        if (!startup_fds[i].present)
            slots[found++] = (int)i;
    if (!startup_ready || poisoned || !pipe_factory)
        error = EIO;
    else if (found != 2)
        error = EMFILE;
    else if (live[3] || live[4] || startup_users[3] || startup_users[4])
        error = ENFILE;
    else {
        unsigned char b[32] = {0};
        put(b, 0, 82);
        put(b, 4, pipe_factory);
        put(b, 8, 1);
        if (!exchange(b, sizeof b))
            error = EIO;
        else if ((int32_t)get(b, 0) < 0) {
            int32_t result = (int32_t)get(b, 0);
            /* Validate before negation: INT32_MIN is not a representable errno.
             */
            if (result != -EACCES && result != -EINVAL && result != -ENFILE)
                error = EIO;
            else {
                error = -result;
                for (unsigned i = 4; i < 32; ++i)
                    if (b[i])
                        error = EIO;
            }
        } else if (get(b, 0) || get(b, 4) < 1 || get(b, 4) > 3 ||
                   get(b, 8) != (0x78000001u | (get(b, 4) << 8)) ||
                   get(b, 12) != (0x78000002u | (get(b, 4) << 8)) ||
                   get(b, 16) != 3 || get(b, 20) != 4 || get(b, 24) != 256 ||
                   get(b, 28) != 16)
            error = EIO;
        else {
            for (unsigned i = 0; i < 2; ++i) {
                unsigned binding = 3 + i;
                refs[binding] = get(b, 8 + i * 4);
                fds[binding] = binding;
                rights[binding] = i ? 2 : 1;
                live[binding] = 1;
                startup_users[binding] = 1;
                startup_fds[slots[i]] = (struct startup_fd){binding, 0, 1};
            }
            pair[0] = slots[0];
            pair[1] = slots[1];
        }
    }
    if (error == EIO)
        poisoned = 1;
    startup_mask_leave(previous);
    return error ? startup_error(error) : 0;
}
#ifdef FORK_DASH_PIPE
#include "pipe-shell-client.h"
#else
static int pipe_control(unsigned op, unsigned reference, unsigned binding,
                        int expected)
{
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return 0;
    unsigned char b[32] = {0};
    put(b, 0, op);
    put(b, 4, reference);
    put(b, 8, binding);
    int ok = exchange(b, sizeof b) && (int32_t)get(b, 0) == expected;
    for (unsigned i = 4; i < 32; ++i)
        if (b[i])
            ok = 0;
    startup_mask_leave(previous);
    return ok;
}
#ifdef FORK_PIPE_SIGNAL
static volatile sig_atomic_t pipe_signals, pipe_signal_bad;
static void pipe_signal_handler(int signal)
{
    uint64_t mask = 0;
    if (signal != SIGPIPE || memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) ||
        mask != (16 | (UINT64_C(1) << (SIGPIPE - 1))))
        pipe_signal_bad = 1;
    ++pipe_signals;
    errno = ERANGE;
}
static int pipe_broken_write(void)
{
    unsigned char byte = 0x5a;
    return write(4, &byte, 1) == -1 && errno == EPIPE && !pipe_signal_bad;
}
static _Noreturn void pipe_signal_probe(void)
{
    struct sigaction action = {0};
    sigset_t blocked;
    uint64_t seed = 16;
    if (close(11) || memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&seed, 0, 8) ||
        sigemptyset(&action.sa_mask) || sigemptyset(&blocked) ||
        sigaddset(&blocked, SIGPIPE))
        _exit(94);
    action.sa_handler = pipe_signal_handler;
    if (sigaction(SIGPIPE, &action, 0) || write(4, 0, 0) != 0 ||
        write(3, "x", 1) != -1 || errno != EBADF || pipe_signals)
        _exit(94);
    action.sa_handler = SIG_IGN;
    if (sigaction(SIGPIPE, &action, 0) || !pipe_broken_write() || pipe_signals)
        _exit(94);
    action.sa_handler = pipe_signal_handler;
    if (sigaction(SIGPIPE, &action, 0) || !pipe_broken_write() ||
        pipe_signals != 1 || !mask_is(seed))
        _exit(94);
    if (sigprocmask(SIG_BLOCK, &blocked, 0) || !pipe_broken_write() ||
        !pipe_broken_write() || pipe_signals != 1 ||
        !mask_is(seed | (1u << (SIGPIPE - 1))))
        _exit(94);
    errno = EDOM;
    if (sigprocmask(SIG_UNBLOCK, &blocked, 0) || pipe_signals != 2 ||
        errno != EDOM || !mask_is(seed) || memtrap(0x29002, 0, 0, 0, 0) ||
        pipe_signals != 2)
        _exit(94);
    if (sigprocmask(SIG_BLOCK, &blocked, 0) || !pipe_broken_write() ||
        pipe_signals != 2)
        _exit(94);
    action.sa_handler = SIG_IGN;
    if (sigaction(SIGPIPE, &action, 0) ||
        sigprocmask(SIG_UNBLOCK, &blocked, 0) || pipe_signals != 2 ||
        pipe_signal_bad || !mask_is(seed))
        _exit(94);
    action.sa_handler = SIG_DFL;
    if (sigaction(SIGPIPE, &action, 0))
        _exit(94);
#if defined(FORK_PIPE_SIGNAL_BLOCK) || defined(FORK_PIPE_SIGNAL_NO_POLL)
    if (sigprocmask(SIG_BLOCK, &blocked, 0) || !pipe_broken_write() ||
        pipe_signals != 2)
        _exit(94);
    sigprocmask(SIG_UNBLOCK, &blocked, 0);
#else
    pipe_broken_write();
#endif
    _exit(94); /* Default SIGPIPE must not return here. */
}
#endif
int main(void)
{
    if (!startup_begin() || !pipe_grant() || cookie != 23 ||
        private_value != 41 || fcntl(0, F_DUPFD_CLOEXEC, 10) != 10)
        return 90;
    int pair[2] = {-1, -1};
    if (native_pipe_pair(0) != -1 || errno != EFAULT)
        return 90;
    /* Fill all remaining slots with local aliases: EMFILE must send no create.
     */
    int aliases[12];
    for (unsigned i = 0; i < 12; ++i) {
        aliases[i] = fcntl(0, F_DUPFD, 0);
        if (aliases[i] < 0)
            return 90;
    }
    if (native_pipe_pair(pair) != -1 || errno != EMFILE || pair[0] != -1 ||
        pair[1] != -1)
        return 90;
    if (close(aliases[0]) || native_pipe_pair(pair) != -1 || errno != EMFILE ||
        pair[0] != -1 || pair[1] != -1)
        return 90;
    for (unsigned i = 1; i < 12; ++i)
        if (close(aliases[i]))
            return 90;
#if defined(FORK_PIPE_BAD_REPLY) || defined(FORK_PIPE_REPLY_LOSS)
    uint64_t failure_mask = 16;
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&failure_mask, 0, 8))
        _exit(93);
    /* The second call must fail locally: an unknown create is never retried. */
    for (unsigned attempt = 0; attempt < 2; ++attempt)
        if (native_pipe_pair(pair) != -1 || errno != EIO || !poisoned ||
            pair[0] != -1 || pair[1] != -1 || live[3] || live[4] ||
            startup_users[3] || startup_users[4] || startup_fds[3].present ||
            startup_fds[4].present || !mask_is(failure_mask))
            _exit(93);
    _exit(92);
#endif
    if (native_pipe_pair(pair) || pair[0] != 3 || pair[1] != 4 ||
        fcntl(3, F_GETFD) || fcntl(4, F_GETFD) || dup2(3, 11) != 11 || close(3))
        return 90;
#ifdef FORK_PIPE_SIGNAL
    pipe_signal_probe();
#endif
    unsigned char buffer[16];
    if (read(3, buffer, 1) != -1 || errno != EBADF)
        return 90;
    uint64_t seed = 16;
    if (memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&seed, 0, 8))
        return 90;
    pid_t child = fork();
    if (child < 0 || !mask_is(seed) || cookie != 23 || private_value != 41)
        return 90;
    if (!child) {
        cookie = 47;
        private_value = 75;
        if (!pipe_control(82, pipe_factory, 1, -EACCES) ||
            !pipe_control(1, refs[4], 4, -EACCES) || close(11))
            return 91;
        for (unsigned i = 0; i < 20; ++i) {
#ifdef FORK_PIPE_FAULT
            if (i == 16) {
                unsigned char partial[32] = {0};
                put(partial, 0, 2);
                put(partial, 4, refs[4]);
                put(partial, 8, 4);
                put(partial, 12, 16);
                if (!move(partial, 17, 1))
                    return 91;
                __asm__ __volatile__("ud2");
                __builtin_unreachable();
            }
#endif
            for (unsigned j = 0; j < sizeof buffer; ++j)
                buffer[j] = (unsigned char)(i * 16 + j);
            if (write(4, buffer, sizeof buffer) != sizeof buffer)
                return 91;
        }
        /* Intentionally no close: the owner must release the terminal writer.
         */
        _exit(0);
    }
    if (close(4) || !pipe_control(83, 0, 0, 0))
        return 90;
    unsigned total = 0;
    for (;;) {
        ssize_t n = read(11, buffer, sizeof buffer);
        if (n < 0)
            return 90;
        if (!n)
            break;
        for (unsigned j = 0; j < (unsigned)n; ++j)
            if (buffer[j] != (unsigned char)(total + j))
                return 90;
        total += (unsigned)n;
        if (total > 320)
            return 90;
    }
    int status = -1;
    unsigned expected_bytes = 320;
    int expected_status = 0;
#ifdef FORK_PIPE_FAULT
    expected_bytes = 256;
    expected_status = SIGILL;
#endif
#ifdef FORK_PIPE_STOP
    expected_bytes = 256;
    expected_status = SIGTERM;
#endif
    if (total != expected_bytes || waitpid(child, &status, 0) != child ||
        status != expected_status || cookie != 23 || private_value != 41 ||
        !mask_is(seed) || close(11) || close(0) || close(1) || close(2) ||
        close(10))
        return 90;
    return 0;
}

#endif
