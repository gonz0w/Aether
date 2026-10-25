/* SPDX-License-Identifier: BSD-2-Clause */
/* Native descriptor witness. All scratch aliases close before the copy fixture.
 */
static int scratch_probe(void)
{
    if (!scratch_accept())
        return 0;
    int writer = open("/scratch/data", O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (writer != 3 || fcntl(writer, F_GETFD) != 0)
        return 0;
    int alias = fcntl(writer, F_DUPFD_CLOEXEC, 4);
    if (alias != 4 || fcntl(alias, F_GETFD) != FD_CLOEXEC ||
        write(writer, "A", 1) != 1 || close(writer) ||
        write(alias, "B", 1) != 1 || close(alias))
        return 0;
    int first = open("/scratch/data", O_RDONLY | O_CLOEXEC);
    int second = open("/scratch/data", O_RDONLY);
    if (first != 3 || second != 4 || fcntl(first, F_GETFD) != FD_CLOEXEC ||
        fcntl(second, F_GETFD) != 0)
        return 0;
    char b[2] = {0};
    if (read(first, b, 1) != 1 || b[0] != 'A' || read(first, b, 1) != 1 ||
        b[0] != 'B' || read(second, b, 2) != 2 || memcmp(b, "AB", 2) ||
        read(second, b, 1) != 0 || close(first) || close(second))
        return 0;
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return 0;
    for (unsigned i = 3; i < 16; ++i)
        if (!startup_fds[i].present)
            memset(&startup_fds[i], 0, sizeof startup_fds[i]);
    unsigned char done[32] = {0};
    put(done, 0, 96);
    int ok = exchange(done, 32);
    for (unsigned i = 0; i < 32; ++i)
        ok &= done[i] == 0;
    startup_mask_leave(previous);
    return ok;
}
