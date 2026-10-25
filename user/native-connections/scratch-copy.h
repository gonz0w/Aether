/* SPDX-License-Identifier: BSD-2-Clause */
/* Live aliases retained through the existing masked copy protocol. */
static int scratch_copy_done(void)
{
    unsigned char done[32] = {0};
    put(done, 0, 96);
    if (!exchange(done, 32))
        return 0;
    for (unsigned i = 0; i < 32; ++i)
        if (done[i])
            return 0;
    return 1;
}
static int scratch_probe(void)
{
    return scratch_accept() &&
           open("/scratch/data", O_WRONLY | O_CREAT | O_TRUNC, 0600) == 3 &&
           fcntl(3, F_DUPFD_CLOEXEC, 4) == 4 && write(3, "A", 1) == 1 &&
           scratch_copy_done();
}
static int scratch_copy_finish(int child)
{
    if (fcntl(3, F_GETFD) != 0 || fcntl(4, F_GETFD) != FD_CLOEXEC)
        return 0;
    if (child && write(3, "B", 1) != 1)
        return 0;
    if (close(3))
        return 0;
    if (child && write(4, "C", 1) != 1)
        return 0;
    return !close(4) && scratch_copy_done();
}
