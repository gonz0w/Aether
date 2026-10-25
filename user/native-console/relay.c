/* SPDX-License-Identifier: BSD-2-Clause */
/* Transport composition witness, not a POSIX adapter or production service. */
#include "../native-memory/adapter.h"
#include <sys/auxv.h>
static _Thread_local volatile unsigned int witness = 17;

static long io(unsigned long op, unsigned long cap, char *bytes,
               unsigned long count)
{
    for (unsigned long tries = 0; tries < 1000000; ++tries) {
        long n = memtrap(op, cap, (unsigned long)bytes, count, 0);
        if (n != -11)
            return n;
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
    return -110;
}
static int transfer(unsigned long op, unsigned long cap, char *bytes,
                    unsigned long count)
{
    while (count) {
        long n = io(op, cap, bytes, count);
        if (n <= 0 || (unsigned long)n > count)
            return 1;
        bytes += n;
        count -= n;
    }
    return 0;
}
int main(int argc, char **argv)
{
    char bytes[8];
    if (witness != 17 || argc != 2)
        return 70;
    unsigned long reader = getauxval(0xa001), writer = getauxval(0xa002);
    if (argv[1][0] != 'c') {
        for (unsigned long op = 0x26000; op <= 0x26003; ++op)
            if (memtrap(op, 0xf001, (unsigned long)bytes, 1, 0) != -13)
                return 71;
        if (argv[1][0] == 'n')
            return reader == 0 && writer == 0 ? 0 : 72;
        if (transfer(0x24001, reader, bytes, 8))
            return 73;
        const char expected[8] = {'a', 0, 27, '\r', 'Z', '9', '\n', '!'};
        for (unsigned long i = 0; i < 8; ++i)
            if (bytes[i] != expected[i])
                return 74;
        return transfer(0x24002, writer, bytes, 8) ? 75 : 0;
    }
    unsigned long tries;
    for (tries = 0; tries < 1000000; ++tries) {
        long n = memtrap(0x26000, 0xf001, 0, 0, 0);
        if (n == 0)
            break;
        if (n != -13)
            return 76;
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
    if (tries == 1000000)
        return 77;
    if (transfer(0x26001, 0xf001, "CONSOLE READY\n", 14) ||
        transfer(0x26000, 0xf001, bytes, 8) ||
        transfer(0x24002, writer, bytes, 8))
        return 78;
    if (memtrap(0x24003, writer, 0, 0, 0) != 0)
        return 79;
    if (transfer(0x24001, reader, bytes, 8))
        return 80;
    if (transfer(0x26001, 0xf001, "CONSOLE ECHO:", 13) ||
        transfer(0x26001, 0xf001, bytes, 8) ||
        transfer(0x26001, 0xf001, "\n0123456789abcdefghijklmnopqrstuv\n", 34))
        return 81;
#ifdef CONNECTIONS_CONSOLE
    /* Leave the grant open: slot reuse must be denied by generation binding. */
    return 0;
#else
    return memtrap(0x26002, 0xf001, 0, 0, 0) == 0 ? 0 : 82;
#endif
}
