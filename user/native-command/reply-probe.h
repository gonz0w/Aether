/* SPDX-License-Identifier: BSD-2-Clause */
/* Isolated adapter witness for NATIVE-COMMAND-IO's reply-failure plan.
 * Caller has validated both bindings. Stack buffers are live for synchronous
 * calls; no borrowed buffer survives the call. Exit 84 means every check
 * passed, but the surrounding normal-command workload must reject this outcome.
 */
static void reply_probe(void)
{
    unsigned char bytes[16];
    memset(bytes, 0xa5, sizeof bytes);
#ifdef DROP_CLOSE
    if (read(0, bytes, sizeof bytes) != 6 || memcmp(bytes, "abcdef", 6) ||
        write(1, "6\n", 2) != 2)
        _exit(85);
    errno = 0;
    if (close(0) != -1 || errno != EIO)
        _exit(86);
#else
    errno = 0;
    if (read(0, bytes, sizeof bytes) != -1 || errno != EIO)
        _exit(86);
    for (unsigned i = 0; i < sizeof bytes; i++)
        if (bytes[i] != 0xa5)
            _exit(87);
#endif
    if (!poisoned || reply_injections != 1)
        _exit(88);
    unsigned before = channel_calls;
    errno = 0;
    if (read(0, bytes, sizeof bytes) != -1
#ifdef DROP_CLOSE
        || errno != EBADF
#else
        || errno != EIO
#endif
    )
        _exit(89);
    errno = 0;
    if (write(1, "X", 1) != -1 || errno != EIO)
        _exit(90);
    errno = 0;
    if (close(1) != -1 || errno != EIO)
        _exit(91);
    errno = 0;
    if (close(1) != -1 || errno != EBADF)
        _exit(92);
    unsigned char frame[384] = {0};
    put(frame, 0, 4);
    if (exchange(frame, sizeof frame))
        _exit(93);
    memset(frame, 0, sizeof frame);
    put(frame, 0, 5);
    if (exchange(frame, 32) || channel_calls != before)
        _exit(94);
    _exit(84);
}
