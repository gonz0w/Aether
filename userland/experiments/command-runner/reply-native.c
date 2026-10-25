/* SPDX-License-Identifier: BSD-2-Clause */
/* Native fault injection after a full real reply has been received. */
#include "native-io.h"
#include <errno.h>
#include <string.h>
#include <unistd.h>
long __real_channel_raw(unsigned long, unsigned long, unsigned long,
                        unsigned long);
long __wrap_channel_raw(unsigned long, unsigned long, unsigned long,
                        unsigned long);
static unsigned calls, used, replies, injections;
static int active, forbidden;
static unsigned char *record;
long __wrap_channel_raw(unsigned long op, unsigned long grant,
                        unsigned long address, unsigned long size)
{
    ++calls;
    if (forbidden)
        _exit(94);
    long result = __real_channel_raw(op, grant, address, size);
    if (active && op == 0x24001 && result > 0 &&
        (unsigned long)result <= size) {
        if (!used)
            record = (unsigned char *)address;
        used += (unsigned)result;
        if (used == 32) {
            used = 0;
            ++replies;
#ifdef DROP_CLOSE
            unsigned target = 3; /* read, write, close */
#else
            unsigned target = 1;
#endif
            if (replies == target) {
                ++injections;
#ifdef BAD_REPLY
                record[4] = 1;
#else
                return 0; /* Last fragment consumed remotely, not acknowledged.
                           */
#endif
            }
        }
    }
    return result;
}
int main(void)
{
    if (!native_bootstrap(1))
        return 83;
    active = 1;
    unsigned char bytes[16];
    memset(bytes, 0xa5, sizeof bytes);
#ifdef DROP_CLOSE
    if (read(0, bytes, sizeof bytes) != 6 || memcmp(bytes, "abcdef", 6) ||
        write(1, "6\n", 2) != 2)
        return 85;
    errno = 0;
    if (close(0) != -1 || errno != EIO)
        return 86;
#else
    errno = 0;
    if (read(0, bytes, sizeof bytes) != -1 || errno != EIO)
        return 86;
    for (unsigned i = 0; i < sizeof bytes; ++i)
        if (bytes[i] != 0xa5)
            return 87;
#endif
    if (injections != 1 || used)
        return 88;
    unsigned before = calls;
    forbidden = 1;
    errno = 0;
    if (read(0, bytes, sizeof bytes) != -1 ||
#ifdef DROP_CLOSE
        errno != EBADF
#else
        errno != EIO
#endif
    )
        return 89;
    errno = 0;
    if (write(1, "X", 1) != -1 || errno != EIO)
        return 90;
    errno = 0;
    if (close(1) != -1 || errno != EIO)
        return 91;
    errno = 0;
    if (close(1) != -1 || errno != EBADF)
        return 92;
    unsigned char request[384] = {4}, reply[32];
    if (native_exchange(request, sizeof request, reply))
        return 93;
    request[0] = 5;
    if (native_exchange(request, 32, reply) || calls != before)
        return 94;
    return 84;
}
