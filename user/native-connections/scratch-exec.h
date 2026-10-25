/* SPDX-License-Identifier: BSD-2-Clause */
/* Private image-replacement witness, not public execve. */
static int scratch_exec_request(void)
{
#ifdef SCRATCH_EXEC_LAST
    char first = 0;
    if (open("/scratch/data", O_RDONLY | O_CLOEXEC) != 5 ||
        fcntl(5, F_GETFD) != FD_CLOEXEC || read(5, &first, 1) != 1 ||
        first != 'A')
        return 0;
#endif
    if (fcntl(10, F_SETFD, FD_CLOEXEC))
        return 0;
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return 0;
    unsigned char request[96] = {0};
    put(request, 0, 97);
    for (unsigned i = 0; i < 16; ++i) {
        if (!startup_fds[i].present)
            continue;
        request[32 + i * 4] = startup_fds[i].binding;
        request[33 + i * 4] = startup_fds[i].flags;
        request[34 + i * 4] = 1;
    }
#ifdef SCRATCH_EXEC_DENY
    unsigned old_refs[5], old_users[5];
    memcpy(old_refs, refs, sizeof old_refs);
    memcpy(old_users, startup_users, sizeof old_users);
    if (!move(request, sizeof request, 1) ||
        memtrap(0x23003, 0, 0, 0, 0) != -11)
        goto failed;
    unsigned char denied[32] = {0}, expected[32] = {0};
    put(expected, 0, (unsigned)-EACCES);
    if (!move(denied, 32, 0) || memcmp(denied, expected, 32) ||
        memcmp(old_refs, refs, sizeof old_refs) ||
        memcmp(old_users, startup_users, sizeof old_users))
        goto failed;
    for (unsigned i = 0; i < 16; ++i) {
        if (startup_fds[i].binding != request[32 + i * 4] ||
            startup_fds[i].flags != request[33 + i * 4] ||
            startup_fds[i].present != request[34 + i * 4])
            goto failed;
    }
    char retained = 'x';
    if (read(5, &retained, 1) != 0 || retained != 'x' || write(3, "", 0) != 0)
        goto failed;
#endif
    if (!move(request, sizeof request, 1))
        goto failed;
    memtrap(0x23003, 0, 0, 0, 0);
    /* Successful replacement never returns to the old image. */
failed:
    poisoned = 1;
    startup_mask_leave(previous);
    return 0;
}
static int scratch_exec_replacement(void)
{
    unsigned char table[64] = {0}, descriptions[32] = {0};
    uint64_t empty = 0;
    if (!startup_begin() || !scratch_accept() || !move(table, 64, 0) ||
        !move(descriptions, 32, 0) || !scratch_restore(table, descriptions))
        return 254;
    unsigned generation = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    for (unsigned j = 0; j < 3; ++j)
        refs[j] = 0x77000000u + (j << 16) + generation;
#ifdef SCRATCH_EXEC_LAST
    char untouched = 'x';
    errno = 0;
    if (read(5, &untouched, 1) != -1 || errno != EBADF || untouched != 'x')
        return 254;
#endif
    errno = 0;
    if (fcntl(4, F_GETFD) != -1 || errno != EBADF)
        return 254;
    errno = 0;
    if (fcntl(10, F_GETFD) != -1 || errno != EBADF || fcntl(3, F_GETFD) != 0 ||
        memtrap(0x1000e, SIG_SETMASK, (uintptr_t)&empty, 0, 8) ||
        fcntl(0, F_DUPFD, 10) != 10 || write(3, "B", 1) != 1 ||
        write(3, "C", 1) != 1 || close(3) || !scratch_copy_done())
        return 254;
    char value;
    if (read(0, &value, 1) != 1 || value != 'b' || read(0, &value, 1) != 1 ||
        value != 'd' || close(0) || read(10, &value, 1) != 1 || value != 'e' ||
        close(10) || close(1) || close(2))
        return 254;
    return 72;
}
