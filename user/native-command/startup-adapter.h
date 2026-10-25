/* SPDX-License-Identifier: BSD-2-Clause */
/* Opt-in, one-context startup facade. Included after the scoped transport. */
#include <fcntl.h>
#include <signal.h>
#include <stdarg.h>
#include <unistd.h>

struct startup_fd {
    unsigned binding;
    int flags, present;
};
static struct startup_fd startup_fds[16];
static unsigned startup_users[BINDINGS];
#ifndef STARTUP_PUBLIC_ACTION
static struct sigaction startup_actions[64];
#endif
static int startup_ready;

#ifdef STARTUP_GUARD_TEST
static int startup_guard_fail;
#endif
static long startup_mask_enter(uint64_t *previous)
{
    uint64_t all = UINT64_MAX;
#ifdef STARTUP_GUARD_SKIP
    all = 0; /* Negative control: leave the context exposed. */
#endif
#ifdef STARTUP_GUARD_TEST
    if (startup_guard_fail == 1)
        return -EFAULT;
#endif
    return memtrap(0x1000e, SIG_BLOCK, (uintptr_t)&all,
                   (uintptr_t)previous, 8);
}
#ifdef STARTUP_GUARD_LIVE
static int startup_live_before_restore(void);
#endif
static void startup_mask_leave(uint64_t previous)
{
#ifdef FORK_PIPE_SIGNAL
    int saved_errno = errno;
#endif
#ifdef STARTUP_GUARD_LIVE
#ifdef STARTUP_GUARD_LIVE_SKIP
    if (startup_live_before_restore())
        previous = UINT64_MAX; /* Negative fixture: prevent pending handler entry. */
#else
    (void)startup_live_before_restore();
#endif
#endif
    long status = memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&previous, 0, 8);
#ifdef STARTUP_GUARD_TEST
    if (startup_guard_fail == 2)
        status = -EFAULT;
#endif
    if (status) {
        /* This conformance facade cannot safely return with an unknown mask. */
        memtrap(0x100e7, 125, 0, 0, 0);
        __builtin_trap();
    }
#ifdef FORK_PIPE_SIGNAL
#ifndef FORK_PIPE_SIGNAL_NO_POLL
    if (memtrap(0x29002, 0, 0, 0, 0)) {
        memtrap(0x100e7, 125, 0, 0, 0);
        __builtin_trap();
    }
#endif
    errno = saved_errno;
#endif
}

static int startup_error(int error)
{
    errno = error;
    return -1;
}
static int startup_begin_masked(void)
{
    if (startup_ready || !bootstrap())
        return 0;
#ifdef PIPELINE_STREAMS
    pipeline_install();
#else
    for (unsigned j = 0; j < 3; j++) {
        startup_fds[j] = (struct startup_fd){j, 0, 1};
        startup_users[j] = 1;
    }
#endif
    startup_ready = 1;
    return 1;
}
static int startup_begin(void)
{
    int saved = errno;
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return 0;
    int result = startup_begin_masked();
    startup_mask_leave(previous);
    errno = saved;
    return result;
}
#ifdef STARTUP_FILES
static unsigned startup_open_sequence;
static unsigned startup_file_duplicates;
static int startup_open_masked(const char *path, int flags)
{
    if (!startup_ready)
        return startup_error(EAGAIN);
    if (poisoned)
        return startup_error(EIO);
    if (!startup_root)
        return startup_error(EACCES);
    if (flags & ~O_CLOEXEC)
        return startup_error(ENOTSUP);
    if (!path)
        return startup_error(EFAULT);
    unsigned length = (unsigned)strnlen(path, 16);
    if (length == 16)
        return startup_error(ENAMETOOLONG);
    if (!length || strchr(path, '/') || !strcmp(path, ".") || !strcmp(path, ".."))
        return startup_error(EINVAL);
    unsigned fd = 0;
    while (fd < 16 && startup_fds[fd].present)
        fd++;
    if (fd == 16)
        return startup_error(EMFILE);
    unsigned char b[32] = {0};
    put(b, 0, 6);
    put(b, 4, startup_root);
    put(b, 8, 4);
    put(b, 12, 1);
    memcpy(b + 16, path, length);
    if (!exchange(b, 32))
        return startup_error(EIO);
    int result = (int)get(b, 0);
    if (result < 0) {
        int bad = result != -EACCES && result != -EINVAL && result != -ENOENT && result != -EMFILE;
        for (unsigned i = 4; i < 32; i++)
            bad |= b[i];
        if (!bad)
            return startup_error(-result);
    } else {
        unsigned binding = get(b, 8), sequence = startup_open_sequence + 1;
        unsigned gen = startup_root - 0x76040000u;
        int bad = result || binding < 3 || binding >= BINDINGS || sequence > 6;
        for (unsigned i = 12; i < 32; i++)
            bad |= b[i];
        if (!bad && !live[binding] && !startup_users[binding] &&
            get(b, 4) == (0x77000000u | (gen << 16) | (sequence << 8) | (binding - 2))) {
            refs[binding] = get(b, 4);
            fds[binding] = binding;
            rights[binding] = 1;
            live[binding] = 1;
            startup_users[binding] = 1;
            startup_open_sequence = sequence;
            startup_fds[fd] = (struct startup_fd){binding, flags & O_CLOEXEC ? FD_CLOEXEC : 0, 1};
            return (int)fd;
        }
    }
    poisoned = 1;
    return startup_error(EIO);
}
int open(const char *path, int flags, ...)
{
    uint64_t previous;
    long status = startup_mask_enter(&previous);
    if (status)
        return startup_error((int)-status);
    int result = startup_open_masked(path, flags);
    int saved = errno;
    startup_mask_leave(previous);
    errno = saved;
    return result;
}
int open64(const char *path, int flags, ...)
{
    return open(path, flags);
}
#endif
#ifdef STARTUP_IDENTITY
#ifdef STARTUP_IDENTITY_ERRNO_SKIP
static unsigned startup_identity_errno_fault;
#endif
static unsigned startup_identity(unsigned index)
{
    if (!startup_ready) {
#ifdef STARTUP_IDENTITY_ERRNO_SKIP
        if (!startup_identity_errno_fault || index != STARTUP_IDENTITY_ERRNO_SKIP)
#endif
            errno = EAGAIN;
        return UINT_MAX;
    }
    return startup_ids[index];
}
uid_t getuid(void) { return startup_identity(0); }
uid_t geteuid(void) { return startup_identity(1); }
gid_t getgid(void) { return startup_identity(2); }
gid_t getegid(void) { return startup_identity(3); }
#endif
#ifdef STARTUP_CWD
#include <stdlib.h>
#include <sys/stat.h>
/* Query bytes are stack-owned until the synchronous guarded exchange returns. */
static int startup_directory_query(unsigned op, const char *path,
                                   unsigned char reply[32])
{
    if (!startup_ready)
        return startup_error(EAGAIN);
    if (poisoned)
        return startup_error(EIO);
    if (!startup_directory)
        return startup_error(EACCES);
    unsigned char request[32] = {0};
    unsigned length = path ? (unsigned)strnlen(path, 16) : 0;
    if (length == 16)
        return startup_error(ENAMETOOLONG);
    put(request, 0, op);
    put(request, 4, startup_directory);
    put(request, 8, 3);
    put(request, 12, length);
    if (length)
        memcpy(request + 16, path, length);
    if (!exchange(request, 32))
        return startup_error(EIO);
    int result = (int)get(request, 0);
    int malformed = 0;
    for (unsigned j = 4; j < 16; j++)
        malformed |= request[j];
    if (result < 0) {
        for (unsigned j = 16; j < 32; j++)
            malformed |= request[j];
        if (!malformed && (result == -EACCES || result == -EBADF ||
            result == -EINVAL || result == -ENOENT || result == -ENAMETOOLONG ||
            result == -ENOSYS))
            return startup_error(-result);
        malformed = 1;
    } else if (op == 4) {
        if (result < 2 || result > 16 || request[16] != '/' ||
            request[16 + result - 1] ||
            memchr(request + 16, 0, (unsigned)result - 1))
            malformed = 1;
        else
            for (unsigned j = 16 + (unsigned)result; j < 32; j++)
                malformed |= request[j];
    } else if (result || !get(request, 16) || !get(request, 20) ||
               get(request, 24) != (S_IFDIR | 0500) || get(request, 28)) {
        malformed = 1;
    }
    if (malformed) {
#ifndef STARTUP_CWD_NO_POISON
        poisoned = 1;
#endif
        return startup_error(EIO);
    }
    memcpy(reply, request, 32);
    return result;
}
char *getcwd(char *buffer, size_t size)
{
    int saved = errno;
    uint64_t previous;
    if (startup_mask_enter(&previous)) {
        errno = EIO;
        return 0;
    }
    unsigned char reply[32];
    int count = startup_directory_query(4, 0, reply);
    char *result = 0;
    if (count >= 0) {
        if ((buffer || size) && size < (unsigned)count)
            errno = ERANGE;
        else {
#ifdef STARTUP_CWD_ENOMEM
            static unsigned allocation_attempts;
            if (!buffer && allocation_attempts++ == 0)
                result = 0; /* One injected local allocation failure. */
            else
#endif
                result = buffer ? buffer : malloc(size ? size : (unsigned)count);
            if (!result) {
#ifndef STARTUP_CWD_ENOMEM_NO_ERRNO
                errno = ENOMEM;
#endif
            } else {
                memcpy(result, reply + 16, (unsigned)count);
                errno = saved;
            }
        }
    }
    int error = errno;
    startup_mask_leave(previous);
    errno = error;
    return result;
}
int stat(const char *restrict path, struct stat *restrict output_stat)
{
    int saved = errno;
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return startup_error(EIO);
    unsigned char reply[32];
    int result = startup_directory_query(5, path, reply);
    if (result == 0) {
        /* Only these three fields are supported by this directory witness. */
        struct stat next = {0};
        next.st_dev = get(reply, 16);
        next.st_ino = get(reply, 20);
#ifdef STARTUP_CWD_PWD_COLLAPSE_DEV
        next.st_dev = 100 + (unsigned)memtrap(0x20005, 0, 0, 0, 0);
#endif
#ifdef STARTUP_CWD_PWD_COLLAPSE_INO
        next.st_ino = 1;
#endif
        next.st_mode = get(reply, 24);
        *output_stat = next;
        errno = saved;
    }
    int error = errno;
    startup_mask_leave(previous);
    errno = error;
    return result;
}
#endif
pid_t getpid(void)
{
#ifdef STARTUP_BAD_PID
    return 0;
#else
    long value = memtrap(0x10027, 0, 0, 0, 0);
    return value < 0 ? startup_error((int)-value) : (pid_t)value;
#endif
}
#ifndef STARTUP_PUBLIC_ACTION
int sigaction(int sig, const struct sigaction *restrict action,
              struct sigaction *restrict old)
{
    if (!startup_ready)
        return startup_error(EAGAIN);
    if (sig < 1 || sig > 64 || (sig >= 32 && sig <= 34) ||
        (action && (sig == SIGKILL || sig == SIGSTOP)))
        return startup_error(EINVAL);
    struct sigaction next = {0};
    if (action) {
        next = *action;
        if ((next.sa_handler != SIG_DFL && next.sa_handler != SIG_IGN) ||
            next.sa_flags)
            return startup_error(ENOTSUP);
        uint64_t bits;
        memcpy(&bits, &next.sa_mask, sizeof bits);
        bits &= ~((UINT64_C(1) << 8) | (UINT64_C(1) << 18));
        memset(&next.sa_mask, 0, sizeof next.sa_mask);
        memcpy(&next.sa_mask, &bits, sizeof bits);
    }
    if (old)
        *old = startup_actions[sig - 1];
#ifndef STARTUP_NO_ACTION
    if (action)
        startup_actions[sig - 1] = next;
#endif
    return 0;
}
#endif
int sigprocmask(int how, const sigset_t *restrict set, sigset_t *restrict old)
{
#ifdef FORK_PIPE_SIGNAL
    int saved_errno = errno;
#endif
    if (!startup_ready)
        return startup_error(EAGAIN);
    uint64_t bits = 0, previous = 0;
    if (set)
        memcpy(&bits, set, sizeof bits);
#ifdef STARTUP_NO_MASK
    set = 0;
#endif
    long status = memtrap(0x1000e, (unsigned)how, set ? (uintptr_t)&bits : 0,
                          old ? (uintptr_t)&previous : 0, 8);
    if (status)
        return startup_error((int)-status);
    if (old) {
        memset(old, 0, sizeof *old);
        memcpy(old, &previous, sizeof previous);
    }
#ifdef FORK_PIPE_SIGNAL
#ifndef FORK_PIPE_SIGNAL_NO_POLL
    if (set && memtrap(0x29002, 0, 0, 0, 0)) {
        memtrap(0x100e7, 125, 0, 0, 0);
        __builtin_trap();
    }
#endif
    errno = saved_errno;
#endif
    return 0;
}

static int startup_fcntl_masked(int fd, int command, int argument)
{
    if (!startup_ready || fd < 0 || fd >= 16 || !startup_fds[fd].present)
        return startup_error(EBADF);
    if (command == F_GETFD)
        return startup_fds[fd].flags;
    if (command != F_SETFD && command != F_DUPFD && command != F_DUPFD_CLOEXEC)
        return startup_error(ENOTSUP);
    if (command == F_SETFD) {
        if (argument & ~FD_CLOEXEC)
            return startup_error(EINVAL);
        startup_fds[fd].flags = argument;
        return 0;
    }
    if (argument < 0 || argument >= 16)
        return startup_error(EINVAL);
    for (int target = argument; target < 16; target++) {
        if (!startup_fds[target].present) {
            struct startup_fd value = startup_fds[fd];
            value.flags = command == F_DUPFD_CLOEXEC ? FD_CLOEXEC : 0;
#ifdef STARTUP_NO_CLOEXEC
            value.flags = 0;
#endif
            /* Single-context admission plus the outer signal mask. */
            startup_users[value.binding]++;
#ifdef STARTUP_FILES
            if (value.binding >= 3 && target >= 10 && command == F_DUPFD_CLOEXEC)
                startup_file_duplicates++;
#endif
            startup_fds[target] = value;
            return target;
        }
    }
    return startup_error(EMFILE);
}
int fcntl(int fd, int command, ...)
{
    int argument = 0;
    if (command == F_SETFD || command == F_DUPFD || command == F_DUPFD_CLOEXEC) {
        va_list ap;
        va_start(ap, command);
        argument = va_arg(ap, int);
        va_end(ap);
    }
    uint64_t previous;
    long status = startup_mask_enter(&previous);
    if (status)
        return startup_error((int)-status);
    int result = startup_fcntl_masked(fd, command, argument);
    int saved = errno;
    startup_mask_leave(previous);
#ifndef STARTUP_GUARD_ERRNO_SKIP
    errno = saved;
#else
    (void)saved; /* Negative fixture: expose handler errno to the caller. */
#endif
    return result;
}
static long startup_io_masked(unsigned long op, unsigned long fd, unsigned long p,
                       unsigned long count)
{
    if (op != 0 && op != 1 && op != 3)
        return -ENOSYS;
    if (!startup_ready || fd >= 16 || !startup_fds[fd].present)
        return -EBADF;
    unsigned binding = startup_fds[fd].binding;
    if (op == 3) {
        startup_fds[fd].present = 0;
        if (--startup_users[binding]) {
#ifdef SCRATCH_EARLY_CLOSE
            if (binding >= 7) {
                unsigned char frame[32] = {0};
                put(frame, 0, 3);
                put(frame, 4, refs[binding]);
                put(frame, 8, binding);
                if (!exchange(frame, 32) || get(frame, 0)) return -EIO;
            }
#endif
            return 0;
        }
    }
    return file_io(op, fds[binding], p, count);
}

static long startup_io(unsigned long op, unsigned long fd, unsigned long p,
                       unsigned long count)
{
    uint64_t previous;
    long status = startup_mask_enter(&previous);
    if (status)
        return status;
    long result = startup_io_masked(op, fd, p, count);
#if defined(FORK_PIPE_SIGNAL) && !defined(FORK_PIPE_SIGNAL_NO_POST)
    if (op == 1 && count && result == -EPIPE && fd < 16 &&
        startup_fds[fd].present && startup_fds[fd].binding == 4 &&
        memtrap(0x29002, SIGPIPE, 0, 0, 0)) {
        memtrap(0x100e7, 125, 0, 0, 0);
        __builtin_trap();
    }
#endif
    startup_mask_leave(previous);
    return result;
}

/* Called under the outer mask, including the nested close transaction. */
static int startup_dup2_masked(int source, int target)
{
    if (!startup_ready || source < 0 || source >= 16 ||
        !startup_fds[source].present || target < 0 || target >= 16)
        return startup_error(EBADF);
    if (source == target) {
#ifdef STARTUP_DUP_SELF
        startup_fds[target].flags = 0;
#endif
        return target;
    }
    struct startup_fd value = startup_fds[source];
    value.flags = 0;
#ifdef STARTUP_DUP_FLAGS
    value.flags = FD_CLOEXEC;
#endif
    if (startup_fds[target].present) {
#ifndef STARTUP_DUP_LEAK
        long status = startup_io(3, (unsigned)target, 0, 0);
        /* A complete EIO close consumed the binding. Unknown replies poison. */
        if (status && (status != -EIO || poisoned))
            return startup_error((int)-status);
#endif
    }
    startup_users[value.binding]++;
    startup_fds[target] = value;
    return target;
}

int dup2(int source, int target)
{
    uint64_t previous;
    long status = startup_mask_enter(&previous);
    if (status)
        return startup_error((int)-status);
    int result = startup_dup2_masked(source, target);
    int saved = errno;
    startup_mask_leave(previous);
    errno = saved;
    return result;
}
