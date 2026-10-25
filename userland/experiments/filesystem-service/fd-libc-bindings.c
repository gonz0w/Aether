/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-libc.h"
#include <errno.h>
#include <stdarg.h>
#ifdef AEFD_CWD_WIRE
#include <stdlib.h>
#endif
#include <unistd.h>
#include <sys/wait.h>
#ifdef AEFD_LIBC_HOST_TEST
/* Rename only after system declarations, preserving the production bodies. */
#define open aefd_test_open
#define open64 aefd_test_open64
#define fcntl aefd_test_fcntl
#define dup aefd_test_dup
#define dup2 aefd_test_dup2
#define pipe aefd_test_pipe
#ifdef AEFD_CWD_WIRE
#define chdir aefd_test_chdir
#define getcwd aefd_test_getcwd
#define malloc aefd_test_malloc
void *aefd_test_malloc(size_t);
int chdir(const char *);
char *getcwd(char *, size_t);
#endif
#define lseek aefd_test_lseek
#define __aether_io aefd_test_io
int open(const char *, int, ...);
int open64(const char *, int, ...);
int fcntl(int, int, ...);
int dup(int);
int dup2(int, int);
int pipe(int[2]);
off_t lseek(int, off_t, int);
long __aether_io(unsigned long, unsigned long, unsigned long, unsigned long);
#endif
_Static_assert(sizeof(long) == 8 && sizeof(off_t) == 8,
               "selected64-bit libc ABI");
/* One concrete stable off-stack owner. Never reset/copy after admission. */
#ifdef AEFD_FORK_BINDINGS
#include "fd-fork-stage.h"
static struct aefd_fork fork_shell;
#define shell fork_shell.boot
struct aefd_fork *aefd_shell_fork_context(void) { return &fork_shell; }
#else
static struct aefd_startup shell;
#endif
static long checked(int64_t result, int saved)
{
    if (result < 0) {
        errno = result >= -4095 ? (int)-result : EIO;
        return -1;
    }
    errno = saved;
    return (long)result;
}
int64_t aefd_shell_start(void)
{
    int saved = errno;
#ifdef AEFD_FORK_BINDINGS
    if (!aefd_fork_tls_valid()) {
        errno = saved;
        return -EIO;
    }
#endif
    int64_t result = aefd_startup_native(&shell);
    errno = saved;
    return result;
}
int64_t aefd_shell_role(void)
{
    return shell.phase == 2 ? (int64_t)shell.identity.slot : -EIO;
}
int64_t aefd_shell_finish(struct aefd_finish *out)
{
    int saved = errno;
    int64_t result =
        shell.phase == 2 ? aefd_context_finish(&shell.context, out) : -EIO;
    errno = saved;
    return result;
}
int64_t aefd_shell_snapshot(unsigned char *out, size_t size, int omit)
{
    int saved = errno;
    int64_t result = aefd_context_snapshot(&shell.context, out, size, omit);
    errno = saved;
    return result;
}
struct aefd_redirect_result aefd_shell_redirect(int from, int to)
{
    int saved = errno;
    struct aefd_redirect_result result =
        aefd_context_redirect(&shell.context, from, to);
    errno = saved;
    return result;
}
long __aether_io(unsigned long op, unsigned long fd, unsigned long pointer,
                 unsigned long count)
{
    int saved = errno;
    int64_t result =
        aefd_libc_io(&shell.context, op, fd, (uintptr_t)pointer, count);
    errno = saved;
    return (long)(result < -4095 ? -EIO : result);
}
int open(const char *path, int flags, ...)
{
    int saved = errno;
    return (int)checked(aefd_libc_open(&shell.context, path, flags), saved);
}
int open64(const char *path, int flags, ...);
int open64(const char *path, int flags, ...) { return open(path, flags); }
int fcntl(int fd, int command, ...)
{
    int saved = errno, argument = 0;
    if (command == F_SETFD || command == F_DUPFD ||
        command == F_DUPFD_CLOEXEC) {
        va_list ap;
        va_start(ap, command);
        argument = va_arg(ap, int);
        va_end(ap);
    }
    return (int)checked(aefd_libc_fcntl(&shell.context, fd, command, argument),
                        saved);
}
int dup(int fd)
{
    int saved = errno;
    return (int)checked(aefd_libc_fcntl(&shell.context, fd, F_DUPFD, 0), saved);
}
int dup2(int from, int to)
{
#ifdef AEFD_DUP2_WIRE
    int saved = errno;
    int64_t result = aefd_context_replace(&shell.context, from, to);
    if (shell.phase == 2 && !shell.context.client.live)
        __wrap__exit(141);
    return (int)checked(result, saved);
#else
    (void)from;
    (void)to;
    errno = EOPNOTSUPP;
    return -1;
#endif
}
int pipe(int pair[2])
{
    int saved = errno;
    if (!pair) {
        errno = EFAULT;
        return -1;
    }
    return (int)checked(aefd_context_pipe(&shell.context, pair, 0), saved);
}
off_t lseek(int fd, off_t offset, int whence)
{
    int saved = errno;
    return (off_t)checked(aefd_context_seek(&shell.context, fd, offset, whence),
                          saved);
}

_Noreturn void __real__exit(int);
_Noreturn void __wrap__exit(int status)
{
    struct aefd_finish result;
    if (aefd_shell_finish(&result) || result.unknown || result.remaining ||
        result.first_error || result.transport.input || result.transport.output)
        __real__exit(141);
    __real__exit(status);
}
static int wait_exchange(unsigned char bytes[32])
{
    struct aefd_io io = aefd_native_io(&shell.context.native);
    unsigned budget = AEFD_IO_BUDGET;
    for (int writing = 1; writing >= 0; --writing) {
        size_t offset = 0;
        while (offset < 32 && budget) {
            --budget;
            int64_t n = writing
                            ? io.write(io.context, bytes + offset, 32 - offset)
                            : io.read(io.context, bytes + offset, 32 - offset);
            if (n > 0 && (uint64_t)n <= 32 - offset)
                offset += (size_t)n;
            else if (n != -11 || io.wait(io.context, writing))
                return 0;
        }
        if (offset != 32)
            return 0;
    }
    return 1;
}
long __aether_waitpid(int pid, int *status, int options)
{
    int saved = errno;
    long result = -EINVAL;
    if (shell.phase != 2 || shell.context.state != 1 ||
        shell.identity.slot != 1 || (pid != -1 && pid <= 0) ||
        (options != 0 && options != WNOHANG))
        return result;
    if (shell.context.native.active || shell.context.native.busy)
        return -EBUSY;
    result = (long)aefd_native_enter(&shell.context.native);
    if (result) {
        if (result != -16)
            aefd_client_abort(&shell.context.client);
        errno = saved;
        return result;
    }
    unsigned char frame[32] = {0};
    frame[0] = 68;
    for (unsigned i = 0; i < 4; ++i) {
        frame[4 + i] = (unsigned char)((uint32_t)pid >> (i * 8));
        frame[8 + i] = (unsigned char)((unsigned)options >> (i * 8));
    }
    result = -EIO;
    if (wait_exchange(frame)) {
        uint32_t raw = aether_fs_session_u32(frame);
        int64_t value = raw <= INT32_MAX ? (int64_t)raw
                                         : (int64_t)raw - INT64_C(4294967296);
        int valid = (value > 0 && aether_fs_session_child_pid((long)value) &&
                     (pid == -1 || value == pid)) ||
                    (value == 0 && options == WNOHANG) || value == -ECHILD;
        if (value <= 0 && aether_fs_session_u32(frame + 4))
            valid = 0;
        for (unsigned i = 8; i < 32; ++i)
            valid = valid && !frame[i];
        if (valid) {
            result = (long)value;
            if (value > 0 && status) {
                uint32_t packed = aether_fs_session_u32(frame + 4);
                *status =
                    packed <= INT32_MAX
                        ? (int)packed
                        : INT32_MIN + (int)(packed - UINT32_C(0x80000000));
            }
        }
    }
    if (result == -EIO)
        aefd_client_abort(&shell.context.client);
    aefd_native_leave(&shell.context.native);
    errno = saved;
    return result;
}

#ifdef AEFD_CWD_WIRE
int chdir(const char *path)
{
    int saved = errno;
    if (!path) {
        errno = EFAULT;
        return -1;
    }
    size_t length = 0;
    while (length < 256 && path[length])
        ++length;
    int64_t result =
        aefd_context_chdir(&shell.context, (const unsigned char *)path, length);
    if (shell.phase == 2 && !shell.context.client.live)
        __wrap__exit(141);
    return (int)checked(result, saved);
}
char *getcwd(char *buffer, size_t size)
{
    int saved = errno;
    if (buffer && !size) {
        errno = EINVAL;
        return NULL;
    }
    unsigned char path[256];
    int64_t result = aefd_context_getcwd(&shell.context, path);
    if (shell.phase == 2 && !shell.context.client.live)
        __wrap__exit(141);
    if (result < 0) {
        (void)checked(result, saved);
        return NULL;
    }
    size_t length = (size_t)result;
    if (size && length > size) {
        errno = ERANGE;
        return NULL;
    }
    char *out = buffer;
    if (!out) {
        out = malloc(size ? size : length);
        if (!out) {
            errno = ENOMEM;
            return NULL;
        }
    }
    memcpy(out, path, length);
    errno = saved;
    return out;
}
#endif
