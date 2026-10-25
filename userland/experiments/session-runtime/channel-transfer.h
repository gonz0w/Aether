/* SPDX-License-Identifier: BSD-2-Clause */
/* Private ABI24 endpoint readiness; caller supplies state and memtrap. */
static int move(unsigned char *buffer, unsigned length, int writing)
{
    if (poisoned)
        return 0;
    unsigned offset = 0;
    unsigned long endpoint = writing ? output : input;
    while (offset < length) {
        unsigned request = length - offset;
        if (request > 16)
            request = 16;
        long result = memtrap(writing ? 0x24002 : 0x24001, endpoint,
                              (uintptr_t)(buffer + offset), request, 0);
        if (result == -11) {
            /* A zero hint is neither bytes nor EOF. Rescan the same offset.
             * EINTR does not deliver/dequeue a signal. Fail closed rather than
             * spin on the pending signal or replay an ambiguous transaction.
             * Ordinary FD transactions retain their existing outer mask.
             */
            if (memtrap(0x24004, endpoint, 0, 0, 0) == 0)
                continue;
            break;
        }
        if (result <= 0 || (unsigned long)result > request)
            break;
        offset += (unsigned)result;
        if (offset == length)
            return 1;
    }
    poisoned = 1;
    return 0;
}
