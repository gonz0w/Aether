/* SPDX-License-Identifier: BSD-2-Clause */
/* Private single-context exec staging shared by the libc witnesses. */
long __aether_execve_stage(const char *path, char *const argv[],
                           char *const envp[])
{
    if (strcmp(path, "/next") && strcmp(path, "/denied")
#if defined(FORK_SHELL_ARGV) || defined(FORK_DASH_PIPE_CONSUMER)
        && strcmp(path, "/inputs/helper")
#ifdef FORK_SHELL_FAILED_EXEC
        && strcmp(path, "/inputs/missing") &&
        strcmp(path, "/inputs/not-executable")
#endif
#endif
    )
        return -ENOENT;
#ifdef FORK_NULL
    if (!strcmp(path, "/inputs/helper")) {
        unsigned char before_fds[sizeof startup_fds];
        unsigned char before_users[sizeof startup_users];
        unsigned char before_refs[sizeof refs], before_live[sizeof live];
        uint64_t before_mask = 0, after_mask = 0;
        memcpy(before_fds, startup_fds, sizeof before_fds);
        memcpy(before_users, startup_users, sizeof before_users);
        memcpy(before_refs, refs, sizeof before_refs);
        memcpy(before_live, live, sizeof before_live);
        if (memtrap(0x1000e, 0, 0, (uintptr_t)&before_mask, 8))
            memtrap(0x100e7, 229, 0, 0, 0);
        /* Only the helper path injects this call; /denied cannot recurse. */
        errno = 0;
        if (execve("/denied", argv, envp) != -1 || errno != EACCES)
            memtrap(0x100e7, 230, 0, 0, 0);
        if (memtrap(0x1000e, 0, 0, (uintptr_t)&after_mask, 8) ||
            after_mask != before_mask)
            memtrap(0x100e7, 229, 0, 0, 0);
        if (memcmp(before_fds, startup_fds, sizeof before_fds) ||
            memcmp(before_users, startup_users, sizeof before_users) ||
            memcmp(before_refs, refs, sizeof before_refs) ||
            memcmp(before_live, live, sizeof before_live) ||
            fcntl(10, F_GETFD) != FD_CLOEXEC)
            memtrap(0x100e7, 228, 0, 0, 0);
        char untouched = 'x';
        if (read(0, &untouched, 1) != 0 || untouched != 'x')
            memtrap(0x100e7, 231, 0, 0, 0);
#ifdef FORK_SHELL_NULL_FAULT
        __asm__ volatile("ud2");
#endif
    }
#endif
#ifdef FORK_SHELL_FAILED_EXEC
#ifdef FORK_FAILED_SKIP
    if (!strcmp(path, "/inputs/not-executable"))
        return -EACCES;
#endif
    unsigned char original_fds[sizeof startup_fds],
        original_users[sizeof startup_users];
    unsigned char original_refs[sizeof refs], original_live[sizeof live];
    memcpy(original_fds, startup_fds, sizeof original_fds);
    memcpy(original_users, startup_users, sizeof original_users);
    memcpy(original_refs, refs, sizeof original_refs);
    memcpy(original_live, live, sizeof original_live);
#endif
    uint64_t mask = 0;
#ifndef EXEC_MASK
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&mask, 8) ||
        mask != (UINT64_MAX & ~((UINT64_C(1) << 8) | (UINT64_C(1) << 18))))
        return -ENOTSUP;
#endif
    unsigned char arguments[272] = {0}, name[32] = {0}, table[64] = {0};
    char *const *lists[2] = {argv, envp};
    for (unsigned list = 0; list < 2; ++list) {
        if (!lists[list])
            return -EINVAL;
        unsigned count = 0;
        while (count < 4 && lists[list][count]) {
            size_t len = strnlen(lists[list][count], 32);
            if (len == 32)
                return -E2BIG;
            memcpy(arguments + 16 + list * 128 + count * 32, lists[list][count],
                   len);
            count++;
        }
        if (count == 4 && lists[list][count])
            return -E2BIG;
        put(arguments, list * 8, count);
    }
#ifdef EXEC_MASK
    if (startup_mask_enter(&mask))
        return -EIO;
    unsigned char saved[32] = {0};
    memcpy(saved, "AEEMSK01", 8);
    memcpy(saved + 8, &mask, 8);
#endif
    memcpy(name, path, strlen(path));
    for (unsigned i = 0; i < 16; ++i) {
#ifndef FORK_REDIRECT_EXEC_STALE
        /* Closed local entries may retain metadata; the wire may not. */
        if (!startup_fds[i].present)
            continue;
#endif
        table[i * 4] = startup_fds[i].binding;
        table[i * 4 + 1] = startup_fds[i].flags;
        table[i * 4 + 2] = startup_fds[i].present;
    }
    if (!move(name, sizeof name, 1) || !move(arguments, sizeof arguments, 1) ||
#ifdef EXEC_MASK
        !move(saved, sizeof saved, 1) ||
#endif
        !move(table, sizeof table, 1) || memtrap(0x23003, 0, 0, 0, 0) != -11)
        memtrap(0x100e7, 220, 0, 0, 0);
    unsigned char reply[32] = {0}, expected[32] = {0};
#ifdef FORK_SHELL_FAILED_EXEC
    if (!move(reply, sizeof reply, 0))
        memtrap(0x100e7, 239, 0, 0, 0);
    int error = (int)get(reply, 0);
    if (error != -ENOENT && error != -EACCES)
        memtrap(0x100e7, 239, 0, 0, 0);
    put(expected, 0, (unsigned)error);
    if (memcmp(reply, expected, sizeof reply))
        memtrap(0x100e7, 239, 0, 0, 0);
#else
    put(expected, 0, (unsigned)-EACCES);
    if (!move(reply, sizeof reply, 0) || memcmp(reply, expected, sizeof reply))
        memtrap(0x100e7, 220, 0, 0, 0);
#endif
#ifdef EXEC_MASK
#ifndef EXEC_MASK_SKIP_FAILURE
    startup_mask_leave(mask);
#endif
#endif
#ifdef FORK_SHELL_FAILED_EXEC
    uint64_t restored_mask = 0;
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&restored_mask, 8) ||
        restored_mask != mask ||
        memcmp(original_fds, startup_fds, sizeof original_fds) ||
        memcmp(original_users, startup_users, sizeof original_users) ||
        memcmp(original_refs, refs, sizeof original_refs) ||
        memcmp(original_live, live, sizeof original_live))
        memtrap(0x100e7, 239, 0, 0, 0);
    return error;
#endif
#ifdef EXEC_PUBLIC_FALSE_RETURN
    return 0;
#else
    return -EACCES;
#endif
}
