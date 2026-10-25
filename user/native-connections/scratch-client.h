/* SPDX-License-Identifier: BSD-2-Clause */
/* Private five-binding descriptor adapter; no ambient path authority. */
#if defined(STARTUP_FILES) || defined(FORK_PIPE) || defined(FORK_NULL)
#error                                                                         \
    "scratch bindings cannot be combined with old file, pipe or null profiles"
#endif
#if BINDINGS != 5
#error "scratch descriptors require five bindings"
#endif
static unsigned scratch_root;
static int scratch_accept_masked(void)
{
    unsigned char b[32] = {0};
    unsigned generation = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    if (!startup_ready || poisoned || scratch_root || generation < 1 ||
        generation > 255)
        return 0;
    if (!move(b, 32, 0) || memcmp(b, "AESFD001", 8) ||
        (get(b, 8) >> 24) != 0xfd || !((get(b, 8) >> 16) & 255) ||
        ((get(b, 8) >> 8) & 255) != generation ||
        ((get(b, 8) & 255) != 1 && (get(b, 8) & 255) != 2) ||
        get(b, 12) != generation || get(b, 16) != 3 || get(b, 20) != 2 ||
        get(b, 24) || get(b, 28)) {
        poisoned = 1;
        return 0;
    }
    scratch_root = get(b, 8);
    return 1;
}
static int scratch_accept(void)
{
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return 0;
    int saved = errno;
    int result = scratch_accept_masked();
    startup_mask_leave(previous);
    errno = saved;
    return result;
}
static int scratch_open_masked(const char *path, int flags)
{
    if (!startup_ready)
        return startup_error(EAGAIN);
    if (poisoned)
        return startup_error(EIO);
    if (!scratch_root)
        return startup_error(EACCES);
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
    if ((live[3] || startup_users[3]) && (live[4] || startup_users[4]))
        return startup_error(ENFILE);
    unsigned char b[32] = {0};
    put(b, 0, 6);
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
        unsigned sequence = (reference >> 4) & 7;
        unsigned expected = 0xfc000000u | (scratch_root & 0x00ffff00u) |
                            (((scratch_root & 255) - 1) << 3) |
                            (sequence << 4) | (binding - 2);
        int valid = status == 0 && binding >= 3 && binding <= 4 &&
                    sequence >= 1 && sequence <= 6 && reference == expected;
        for (unsigned i = 12; i < 32; ++i)
            valid &= b[i] == 0;
        if (valid && !live[binding] && !startup_users[binding]) {
            refs[binding] = reference;
            fds[binding] = binding;
            rights[binding] = mode == 1 ? 1 : 2;
            live[binding] = 1;
            startup_users[binding] = 1;
            startup_fds[fd] = (struct startup_fd){
                binding, flags & O_CLOEXEC ? FD_CLOEXEC : 0, 1};
#ifdef SCRATCH_CLIENT_BAD_CLOEXEC
            startup_fds[fd].flags = 0;
#endif
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
