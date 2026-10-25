/* SPDX-License-Identifier: BSD-2-Clause */
/* Native fixture probes; these do not install descriptors in the libc table. */
static int null_probe(unsigned op, unsigned reference, unsigned count,
                      int status, unsigned object)
{
    unsigned char request[32] = {0}, expected[32] = {0};
    put(request, 0, op);
    put(request, 4, reference);
    put(request, 8, 3);
    put(request, 12, count);
    if (op == 6)
        memcpy(request + 16, "/dev/null", 9);
    put(expected, 0, (unsigned)status);
    if (object) {
        put(expected, 4, object);
        put(expected, 8, 3);
    }
    return exchange(request, sizeof request) &&
           !memcmp(request, expected, sizeof request);
}
static int null_lifetime_check(void)
{
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return 227;
    unsigned generation = null_factory & 255;
    unsigned old = 0x79000000u | (generation << 8) | 1;
    int failure = 0;
    if (live[3] || startup_users[3] || refs[3] != old) {
        failure = 227;
        goto done;
    }
    for (unsigned sequence = 2; sequence <= 16; ++sequence) {
        unsigned current = 0x79000000u | (generation << 8) | sequence;
        if (!null_probe(1, old, 1, -EBADF, 0) ||
            !null_probe(3, old, 0, -EBADF, 0)) {
            failure = 225;
            goto done;
        }
        if (!null_probe(6, null_factory ^ 1, 0, -EACCES, 0) ||
            !null_probe(6, null_factory, 0, 0, current)) {
            failure = 227;
            goto done;
        }
        if (!null_probe(1, old, 1, -EBADF, 0) ||
            !null_probe(3, old, 0, -EBADF, 0) ||
            !null_probe(1, current ^ 0x100, 1, -EBADF, 0)) {
            failure = 225;
            goto done;
        }
        if (!null_probe(6, null_factory, 0, -ENFILE, 0)) {
            failure = 226;
            goto done;
        }
        if (!null_probe(2, current, 0, -EACCES, 0) ||
            !null_probe(1, current, 16, 0, 0) ||
            !null_probe(3, current, 0, 0, 0)) {
            failure = 227;
            goto done;
        }
        old = current;
    }
    if (!null_probe(6, null_factory, 0, -ENFILE, 0))
        failure = 226;
    else if (!null_probe(1, old, 0, -EBADF, 0) ||
             !null_probe(3, old, 0, -EBADF, 0))
        failure = 225;
done:
    startup_mask_leave(previous);
    return failure;
}
