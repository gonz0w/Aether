/* SPDX-License-Identifier: BSD-2-Clause */
/* One-shot startup rejection witness. All borrowed buffers are live for the
 * synchronous calls; no unvalidated binding may reach the byte channel.
 */
static void bootstrap_probe(void)
{
    if (bootstrap())
        _exit(96);
    if (live[0] || live[1])
        _exit(97);
    unsigned before = channel_calls;
    unsigned char byte = 0xa5;
    for (unsigned fd = 0; fd < 2; fd++) {
        errno = 0;
        if (read(fd, &byte, 1) != -1 || errno != EBADF || byte != 0xa5)
            _exit(98);
        errno = 0;
        if (write(fd, "X", 1) != -1 || errno != EBADF)
            _exit(99);
        errno = 0;
        if (close(fd) != -1 || errno != EBADF)
            _exit(101);
    }
    if (channel_calls != before)
        _exit(102);
    _exit(95);
}
