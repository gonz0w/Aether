/* SPDX-License-Identifier: BSD-2-Clause */
/* Keep the caller alive after closing only its sending endpoint. A reply means
 * the broker acted on an incomplete frame. Buffers are synchronous stack
 * borrows.
 */
static void eof_probe(void)
{
    unsigned char frame[384];
    request(frame);
    if (LAUNCH_PREFIX && !move(frame, LAUNCH_PREFIX, 1))
        _exit(106);
    if (memtrap(0x24003, output, 0, 0, 0) != 0)
        _exit(107);
    for (unsigned t = 0; t < 100000; t++) {
        long n = memtrap(0x24001, input, (uintptr_t)frame, 1, 0);
        if (n > 0) {
            /* Drain the reply before exiting so broker completion cannot race
             * endpoint teardown in this deliberate broken-broker control. */
            if (!move(frame + 1, 31, 0))
                _exit(109);
            _exit(104);
        }
        if (n != -EAGAIN)
            _exit(108);
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
    _exit(105);
}
