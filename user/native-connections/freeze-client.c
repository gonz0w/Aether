/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-memory/adapter.h"
static _Thread_local volatile unsigned cookie = 23;
int main(void)
{
#ifdef FREEZE_DUMMY
    return cookie == 23 ? 29 : 200;
#else
    volatile unsigned stack_cookie = 41;
#ifdef FREEZE_DISABLED
    if (memtrap(0x23003, 0, 0, 0, 0) != -38 ||
        memtrap(0x23004, 0, 0, 0, 0) != -38 ||
        memtrap(0x23005, 0, 0, 0, 0) != -38)
        return 201;
#else
    if (memtrap(0x23004, 0, 0, 0, 0) != -13 ||
        memtrap(0x23005, 0, 0, 0, 0) != -13 ||
        memtrap(0x23003, 1, 0, 0, 0) != -22)
        return 202;
#ifdef FREEZE_UNSUPPORTED
    if (memtrap(0x23003, 0, 0, 0, 0) != -95)
        return 203;
#else
    for (unsigned i = 0; i < 2; ++i) {
        cookie = 23 + i;
        stack_cookie = 41 + i;
        if (memtrap(0x23003, 0, 0, 0, 0) != -11)
            return 204;
        if (cookie != 23 + i || stack_cookie != 41 + i)
            return 205;
    }
#endif
#endif
    return cookie >= 23 && stack_cookie >= 41 ? 29 : 206;
#endif
}
