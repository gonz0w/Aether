/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-libc.h"
#include <errno.h>
_Static_assert(O_RDONLY == 0 && FD_CLOEXEC == 1, "selected libc FD constants");
int64_t aefd_libc_isatty(struct aefd_context *c, int fd)
{
    struct aefd_binding binding;
    unsigned rights;
    int64_t status = aefd_context_describe(c, fd, &binding, &rights);
    if (status)
        return status;
    return binding.kind == AEFD_BIND_TERMINAL
#ifdef AEFD_TERMINAL_DUPLEX_BINDINGS
                   || binding.kind == AEFD_BIND_DUPLEX_TERMINAL
#endif
               ? 1
               : -ENOTTY;
}
int64_t aefd_libc_open(struct aefd_context *c, const char *path, int flags)
{
    if (!path)
        return -EFAULT;
#ifdef AEFD_TERMINAL_DUPLEX_BINDINGS
    if (!strcmp(path, "/dev/tty")) {
        if ((flags & ~(O_RDWR | O_NOCTTY | O_CLOEXEC)) ||
            (flags & O_ACCMODE) != O_RDWR)
            return -EOPNOTSUPP;
        return aefd_context_open_duplex(c, !!(flags & O_CLOEXEC));
    }
#endif
    if (flags & ~O_CLOEXEC)
        return -EOPNOTSUPP;
    size_t length = 0;
    while (length < 256 && path[length]) {
#ifndef AEFD_PATH_WIRE
        if (path[length] == '/')
            return -EOPNOTSUPP;
#endif
        ++length;
    }
    if (length == 256)
        return -ENAMETOOLONG;
    return aefd_context_open(c, (const unsigned char *)path, length,
                             !!(flags & O_CLOEXEC));
}
int64_t aefd_libc_fcntl(struct aefd_context *c, int fd, int command,
                        int argument)
{
    switch (command) {
#ifdef AEFD_TERMINAL_BINDINGS
    case F_GETFL:
    case F_SETFL: {
        struct aefd_binding binding;
        unsigned rights;
        int64_t status = aefd_context_describe(c, fd, &binding, &rights);
        if (status)
            return status;
        int access = rights == 1 ? O_RDONLY : O_WRONLY;
#ifdef AEFD_TERMINAL_DUPLEX_BINDINGS
        if (rights == 3)
            access = O_RDWR;
#endif
        if (command == F_GETFL)
            return access;
        /* No mutable status flags are implemented. In particular NONBLOCK
         * would lie while the owner retains EAGAIN as Pending. */
        return argument == 0 || argument == access ? 0 : -EOPNOTSUPP;
    }
#endif
    case F_GETFD:
        return aefd_context_flags(c, fd);
    case F_SETFD:
        if (argument & ~FD_CLOEXEC)
            return -EINVAL;
        return aefd_context_set_flags(c, fd, argument);
    case F_DUPFD:
    case F_DUPFD_CLOEXEC:
        return aefd_context_dup(c, fd, argument, command == F_DUPFD_CLOEXEC);
    default:
        return -EOPNOTSUPP;
    }
}
int64_t aefd_libc_io(struct aefd_context *c, uint64_t op, uint64_t fd,
                     uintptr_t pointer, uint64_t count)
{
    if (op != 0 && op != 1 && op != 3)
        return -ENOSYS;
    if (fd >= 16)
        return -EBADF;
    if (op == 3)
        return aefd_context_close(c, (int)fd);
    if (count && !pointer)
        return -EFAULT;
    size_t bounded = count > AEFD_READ_MAX ? AEFD_READ_MAX : (size_t)count;
    return op == 0 ? aefd_context_read(c, (int)fd, (unsigned char *)pointer,
                                       bounded)
                   : aefd_context_write(
                         c, (int)fd, (const unsigned char *)pointer, bounded);
}
