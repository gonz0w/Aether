/* SPDX-License-Identifier: BSD-2-Clause */
/* Private session namespace; authenticated owner connection supplies authority.
 */
static unsigned scratch_root;
#ifdef SCRATCH_STALE_REFERENCE
static unsigned scratch_previous;
#endif
static int scratch_open_masked(const char *path, int flags)
{
    if (!startup_ready)
        return startup_error(EAGAIN);
    if (poisoned)
        return startup_error(EIO);
    if (!scratch_root)
        return startup_error(EACCES);
#ifdef SCRATCH_SKIP_REQUEST
    if (path && !strcmp(path, "/inputs/denied"))
        return startup_error(EACCES);
#endif
    int access = flags & ~O_CLOEXEC;
    unsigned mode;
    if (access == O_RDONLY)
        mode = 1;
    else if (access == (O_WRONLY | O_CREAT | O_TRUNC))
        mode = 14;
    else
        return startup_error(ENOTSUP);
    if (!path)
        return startup_error(EFAULT);
    size_t len = strnlen(path, 16);
    if (len == 16)
        return startup_error(ENAMETOOLONG);
    unsigned fd = 0;
    while (fd < 16 && startup_fds[fd].present)
        ++fd;
    if (fd == 16)
        return startup_error(EMFILE);
    if ((live[7] || startup_users[7]) && (live[8] || startup_users[8]))
        return startup_error(ENFILE);
    unsigned char b[32] = {0};
    put(b, 0, 86);
    put(b, 4, scratch_root);
    put(b, 12, mode);
    memcpy(b + 16, path, len);
    if (!exchange(b, 32)) {
        poisoned = 1;
        return startup_error(EIO);
    }
    int status = (int)get(b, 0);
    if (status < 0) {
        int valid = status == -ENOENT || status == -EBADF ||
                    status == -EACCES || status == -EINVAL ||
                    status == -ENFILE || status == -ENOSPC ||
                    status == -ENOTSUP;
        for (unsigned i = 4; i < 32; ++i)
            valid &= b[i] == 0;
        if (valid)
            return startup_error(-status);
    } else {
        unsigned binding = get(b, 8), reference = get(b, 4);
        unsigned sequence = (reference >> 8) & 255;
        unsigned expected = 0x78000000U | ((scratch_root & 255) << 16) |
                            (sequence << 8) | (binding - 6);
        int valid = status == 0 && binding >= 7 && binding <= 8 &&
                    sequence >= 1 && sequence <= 15 && reference == expected &&
                    get(b, 12) == (mode == 1 ? 1U : 2U);
        for (unsigned i = 16; i < 32; ++i)
            valid &= b[i] == 0;
        if (valid && !live[binding] && !startup_users[binding]) {
#ifdef SCRATCH_STALE_REFERENCE
            if (scratch_previous) {
                unsigned char stale[32] = {0};
                put(stale, 0, 1);
                put(stale, 4, scratch_previous);
                put(stale, 8, binding);
                put(stale, 12, 1);
                if (!exchange(stale, 32) || (int)get(stale, 0) != -EBADF) {
                    poisoned = 1;
                    return startup_error(EIO);
                }
                for (unsigned i = 4; i < 32; ++i)
                    if (stale[i]) {
                        poisoned = 1;
                        return startup_error(EIO);
                    }
            }
            scratch_previous = reference;
#endif
            refs[binding] = reference;
            fds[binding] = binding;
            rights[binding] = mode == 1 ? 1 : 2;
            live[binding] = 1;
            startup_users[binding] = 1;
            startup_fds[fd] = (struct startup_fd){
                binding, flags & O_CLOEXEC ? FD_CLOEXEC : 0, 1};
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
    int result = scratch_open_masked(path, flags);
    int saved = errno;
    startup_mask_leave(previous);
    errno = saved;
    return result;
}
int open64(const char *path, int flags, ...) { return open(path, flags); }
