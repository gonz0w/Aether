/* SPDX-License-Identifier: BSD-2-Clause */
/* Native test-only link wrapper: corrupt a received second binding, then prove
 * rejection through real musl calls and zero subsequent adapter channel traps.
 */
#include "native-io.h"
#include <errno.h>
#include <unistd.h>

long __real_channel_raw(unsigned long, unsigned long, unsigned long,
                        unsigned long);
long __wrap_channel_raw(unsigned long, unsigned long, unsigned long,
                        unsigned long);
static unsigned calls, received;
static unsigned char *record;
long __wrap_channel_raw(unsigned long op, unsigned long grant,
                        unsigned long address, unsigned long size)
{
    ++calls;
    long result = __real_channel_raw(op, grant, address, size);
    if (op == 0x24001 && received < 32 && result > 0 &&
        (unsigned long)result <= size) {
        if (!received)
            record = (unsigned char *)address;
        received += (unsigned)result;
        if (received == 32)
            record[BOOTSTRAP_FIELD] ^= 0x80;
    }
    return result;
}
int main(void)
{
    if (native_bootstrap(1))
        return 96;
    if (native_ref(0) || native_ref(1))
        return 97;
    unsigned before = calls;
    unsigned char sentinel = 0xa5;
    for (unsigned fd = 0; fd < 2; ++fd) {
        errno = 0;
        if (read((int)fd, &sentinel, 1) != -1 || errno != EBADF ||
            sentinel != 0xa5)
            return 98;
        errno = 0;
        if (write((int)fd, "X", 1) != -1 || errno != EBADF)
            return 99;
        errno = 0;
        if (close((int)fd) != -1 || errno != EBADF)
            return 101;
    }
    if (native_bootstrap(1))
        return 103;
    unsigned char request[384] = {4}, reply[32];
    if (native_exchange(request, sizeof request, reply))
        return 104;
    if (calls != before || received != 32)
        return 102;
    return 95;
}
