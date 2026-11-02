/* SPDX-License-Identifier: BSD-2-Clause */
#define _POSIX_C_SOURCE 200809L
#include "fd-zsh-external.h"
#include "fd-libc.h"
#include <errno.h>
#include <limits.h>
#include <signal.h>
#include <string.h>
#if !defined(AEFD_TERMINAL_CANONICAL_BINDINGS) ||                              \
    !defined(AEFD_EXTERNAL_STARTUP)
#error "current Zsh entry requires canonical external startup"
#endif
#if defined(AEFD_FORK_BINDINGS) || defined(AEFD_EXEC_BINDINGS) ||              \
    defined(AEFD_EXEC_WIRE) || defined(AEFD_DUP2_WIRE) ||                      \
    defined(AEFD_WRITE_WIRE) || defined(AEFD_CWD_WIRE)
#error "current Zsh entry excludes historical process/provider selections"
#endif
extern int __real_main(int, char **);
_Noreturn void __real__exit(int);
_Noreturn void __wrap__Exit(int);
_Noreturn void __wrap__Exit(int status) { __wrap__exit(status); }
/* Internal borrows point into this object. Never move/reset/reinitialize it. */
static struct aefd_startup startup;
static _Thread_local unsigned entry_fresh = 1;
struct aefd_startup *aefd_shell_external_startup(void) { return &startup; }
static int live(void)
{
    return !entry_fresh && startup.phase == 2 && startup.context.state == 1 &&
           startup.context.session.initialized && startup.context.client.live &&
           !startup.context.native.retired;
}
long __aether_io(unsigned long operation, unsigned long fd,
                 unsigned long pointer, unsigned long count)
{
    if (!live() || fd >= 16)
        return -EBADF;
    int saved = errno;
    int64_t result;
    if (operation == 32)
        result = pointer || count
                     ? -EINVAL
                     : aefd_context_dup(&startup.context, (int)fd, 0, 0);
    else if (operation == 33)
        result = -EOPNOTSUPP;
    else
        result = aefd_libc_io(&startup.context, operation, fd,
                              (uintptr_t)pointer, count);
    errno = saved;
    return (long)(result < -4095 ? -EIO : result);
}
static long libc_result(int64_t result, int saved)
{
    if (result < 0) {
        errno = result >= -4095 ? (int)-result : EIO;
        return -1;
    }
    errno = saved;
    return (long)result;
}
int aether_zsh_open(const char *path, int flags, mode_t mode)
{
    (void)mode; /* Existing readonly opens do not use a creation mode. */
    int saved = errno;
    /* On this x86_64 target O_LARGEFILE is the musl syscall shim's no-op bit,
     * not a request for additional descriptor rights. All other flags remain
     * subject to the existing readonly/terminal admission checks. */
    int64_t result =
        live() ? aefd_libc_open(&startup.context, path, flags & ~O_LARGEFILE)
               : -EBADF;
    return (int)libc_result(result, saved);
}
long aether_zsh_raw_fcntl(int fd, int command, int argument)
{
    int saved = errno;
    int64_t result =
        live() ? aefd_libc_fcntl(&startup.context, fd, command, argument)
               : -EBADF;
    errno = saved;
    return result < -4095 ? -EIO : (long)result;
}
long aether_zsh_raw_close(int fd)
{
    return __aether_io(3, (unsigned long)fd, 0, 0);
}
off_t aether_zsh_seek(int fd, off_t offset, int whence)
{
    int saved = errno;
    int64_t result =
        live() ? aefd_context_seek(&startup.context, fd, offset, whence)
               : -EBADF;
    return (off_t)libc_result(result, saved);
}
static int outside_context(const void *pointer, size_t length)
{
    uintptr_t start = (uintptr_t)pointer;
    if (!length)
        return 1;
    if (!start || length > UINTPTR_MAX - start)
        return 0;
    uintptr_t context = (uintptr_t)&startup.context;
    return start + length <= context ||
           start >= context + sizeof(startup.context);
}
long aether_zsh_vector_read(int fd, const struct iovec *parts, int count)
{
    int saved = errno;
    int64_t result = -EINVAL;
    if (count < 0 || count > 2)
        goto done;
    if (count && !outside_context(parts, (size_t)count * sizeof(*parts))) {
        result = -EFAULT;
        goto done;
    }
    size_t total = 0;
    for (int i = 0; i < count; ++i) {
        if (parts[i].iov_len > (size_t)SSIZE_MAX - total)
            goto done;
        total += parts[i].iov_len;
    }
    for (int i = 0; i < count; ++i)
        if (!outside_context(parts[i].iov_base, parts[i].iov_len)) {
            result = -EFAULT;
            goto done;
        }
    if (!live() || fd < 0 || fd >= 16) {
        result = -EBADF;
        goto done;
    }
    result = 0;
    for (int i = 0; i < count; ++i)
        if (parts[i].iov_len) {
            /* A short first prefix is a valid readv result. One existing
             * context read publishes its confirmed bytes and settles state
             * before unmask/handler reentry; never retry a second component
             * after a partial, EOF, error or uncertain completion. */
            size_t n = parts[i].iov_len < AEFD_READ_MAX ? parts[i].iov_len
                                                        : AEFD_READ_MAX;
            result =
                __aether_io(0, (unsigned long)fd,
                            (unsigned long)(uintptr_t)parts[i].iov_base, n);
            break;
        }
done:
    return libc_result(result, saved);
}
long aether_zsh_read(int fd, void *out, size_t count)
{
    const struct iovec part = {out, count};
    return aether_zsh_vector_read(fd, &part, 1);
}
long aether_zsh_vector_write(int fd, const struct iovec *parts, int count)
{
    int saved = errno;
    long result = -EINVAL;
    if (count < 0 || count > 2 || (count && !parts))
        goto done;
    size_t total = 0;
    for (int i = 0; i < count; ++i) {
        if (parts[i].iov_len && !parts[i].iov_base) {
            result = -EFAULT;
            goto done;
        }
        if (parts[i].iov_len > (size_t)SSIZE_MAX - total)
            goto done;
        total += parts[i].iov_len;
    }
    unsigned char bytes[16] = {0};
    size_t limit = total < sizeof(bytes) ? total : sizeof(bytes), used = 0;
    for (int i = 0; i < count && used < limit; ++i) {
        size_t n =
            parts[i].iov_len < limit - used ? parts[i].iov_len : limit - used;
        if (n)
            memcpy(bytes + used, parts[i].iov_base, n);
        used += n;
    }
    result = __aether_io(1, (unsigned long)fd, (unsigned long)(uintptr_t)bytes,
                         limit);
    if (!result && limit)
        result = -EIO;
done:
    if (result < 0) {
        errno = result >= -4095 ? (int)-result : EIO;
        return -1;
    }
    errno = saved;
    return result;
}
static int bootstrap(void)
{
    struct sigaction action = {0};
    action.sa_handler = SIG_IGN;
    struct termios saved;
    if (sigaction(SIGINT, &action, NULL) || tcgetattr(0, &saved))
        return -1;
    saved.c_iflag = ICRNL;
    saved.c_oflag = OPOST | ONLCR;
    saved.c_lflag = ISIG | ICANON | ECHO | ECHOE | ECHOK;
    memset(saved.c_cc, 0, NCCS);
    saved.c_cc[VINTR] = 3;
    saved.c_cc[VERASE] = 127;
    saved.c_cc[VKILL] = 21;
    saved.c_cc[VEOF] = 4;
    saved.c_cc[VMIN] = 1;
    return tcsetattr(0, TCSADRAIN, &saved);
}
static int64_t ready(void)
{
    if (!live() || startup.context.native.active || startup.context.native.busy)
        return -EINVAL;
    int64_t result = aefd_native_enter(&startup.context.native);
    if (result)
        return result;
    result = startup.context.native.call(startup.context.native.context,
                                         0x20004, 0, 0, 0, 0);
    if (result)
        aefd_client_abort(&startup.context.client);
    aefd_native_leave(&startup.context.native);
    return result;
}
static _Noreturn void failed(void)
{
    if (startup.phase == 2)
        __wrap__exit(143);
    __real__exit(143);
}
int __wrap_main(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    if (entry_fresh != 1)
        failed();
    entry_fresh = 0;
    if (aefd_startup_native(&startup) || !live() ||
        startup.identity.slot != 1 ||
        startup.identity.epoch != startup.identity.shell_generation ||
        bootstrap() || ready())
        failed();
    char *arguments[] = {"zsh", "-f", "-i", "+m", NULL};
    __wrap__exit(__real_main(4, arguments));
}
