/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-memory/adapter.h"

static _Thread_local volatile unsigned int witness = 17;

int main(void)
{
    char byte = 'X';
    witness = 1;
    if (witness != 1)
        return 72;
    for (unsigned long op = 0x26000; op <= 0x26002; ++op) {
        if (memtrap(op, 0xf001, (unsigned long)&byte, 1, 0) != -13)
            return 71;
    }
    return 0;
}
