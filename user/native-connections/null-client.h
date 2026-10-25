/* SPDX-License-Identifier: BSD-2-Clause */
/* Private opt-in null route. Authority arrives only through the bound channel.
 */
static unsigned null_factory;
static int null_accept(int active)
{
    unsigned char b[32] = {0};
    unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    if (!move(b, 32, 0) || memcmp(b, "AENUL001", 8) ||
        get(b, 8) != (0x76060000u | gen) || get(b, 16) != gen ||
        get(b, 20) != 1 || get(b, 24) != 3 || get(b, 28) ||
        get(b, 12) != (active ? 0x79000000u | (gen << 8) | 1 : 0))
        return 0;
    null_factory = get(b, 8);
    if (active) {
        refs[3] = get(b, 12);
        fds[3] = 3;
        rights[3] = 1;
        live[3] = 1;
    }
    return 1;
}
int open(const char *path, int flags, ...)
{
    if (!startup_ready || !null_factory)
        return startup_error(EACCES);
    if (!path)
        return startup_error(EFAULT);
    if (flags & ~O_CLOEXEC)
        return startup_error(ENOTSUP);
    if (strcmp(path, "/dev/null"))
        return startup_error(ENOENT);
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return startup_error(EIO);
    int result = -1, saved = EMFILE;
    unsigned fd = 0;
    while (fd < 16 && startup_fds[fd].present)
        ++fd;
    if (fd < 16 && !live[3] && !startup_users[3]) {
        unsigned char request[32] = {0};
        put(request, 0, 6);
        put(request, 4, null_factory);
        put(request, 8, 3);
        memcpy(request + 16, "/dev/null", 9);
        /* The owner must reject a wrong factory without consuming an instance.
         */
        put(request, 4, null_factory ^ 0x100);
        if (!exchange(request, 32) || (int)get(request, 0) != -EACCES)
            goto broken;
        for (unsigned i = 4; i < 32; ++i)
            if (request[i])
                goto broken;
        memset(request, 0, sizeof request);
        put(request, 0, 6);
        put(request, 4, null_factory);
        put(request, 8, 3);
        memcpy(request + 16, "/dev/null", 9);
        if (!exchange(request, 32))
            goto broken;
        int status = (int)get(request, 0);
        if (status == -ENFILE) {
            for (unsigned i = 4; i < 32; ++i)
                if (request[i])
                    goto broken;
            saved = ENFILE;
        } else {
            unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
            if (status || get(request, 4) != (0x79000000u | (gen << 8) | 1) ||
                get(request, 8) != 3)
                goto broken;
            for (unsigned i = 12; i < 32; ++i)
                if (request[i])
                    goto broken;
            refs[3] = get(request, 4);
            fds[3] = 3;
            rights[3] = 1;
            live[3] = 1;
            startup_users[3] = 1;
            startup_fds[fd] =
                (struct startup_fd){3, flags & O_CLOEXEC ? FD_CLOEXEC : 0, 1};
            result = (int)fd;
            saved = errno;
        }
    }
    startup_mask_leave(previous);
    errno = saved;
    return result;
broken:
    poisoned = 1;
    startup_mask_leave(previous);
    return startup_error(EIO);
}
int open64(const char *path, int flags, ...) { return open(path, flags); }
