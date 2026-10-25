/* SPDX-License-Identifier: BSD-2-Clause */
/* Native transport witness, not the production console service. */
#include "../native-memory/adapter.h"
static _Thread_local volatile unsigned int witness = 17;
#define CALL(op, p, n) memtrap(op, 0xf001, (unsigned long)(p), n, 0)

static int send(const char *bytes, unsigned long count)
{
    for (unsigned long tries = 0; count && tries < 1000000; ++tries) {
        long n = CALL(0x26001, bytes, count);
        if (n == -11) {
            memtrap(0x1fffe, 0, 0, 0, 0);
            continue;
        }
        if (n <= 0 || n > 16 || (unsigned long)n > count)
            return 74;
        bytes += n;
        count -= n;
    }
    return count ? 75 : 0;
}
int main(void)
{
    char bytes[8];
    if (witness != 17)
        return 72;
    long generation = memtrap(0x20005, 0, 0, 0, 0);
    if (generation != 2) {
        for (unsigned long op = 0x26000; op <= 0x26003; ++op)
            if (CALL(op, bytes, 1) != -13)
                return 71;
        return 0;
    }
    unsigned long tries;
    for (tries = 0; tries < 1000000; ++tries) {
        long n = CALL(0x26000, 0, 0);
        if (n == 0)
            break;
        if (n != -13)
            return 76;
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
    if (tries == 1000000 || CALL(0x26003, 0, 0) != -13)
        return 77;
    if (send("CONSOLE READY\n", 14))
        return 78;
    unsigned long used = 0;
    for (tries = 0; used < sizeof bytes && tries < 1000000; ++tries) {
        long n = CALL(0x26000, bytes + used, sizeof bytes - used);
        if (n == -11) {
            memtrap(0x1fffe, 0, 0, 0, 0);
            continue;
        }
        if (n <= 0 || (unsigned long)n > sizeof bytes - used)
            return 79;
        used += n;
    }
    const char expected[8] = {'a', 0, 27, '\r', 'Z', '9', '\n', '!'};
    if (used != sizeof bytes)
        return 80;
    for (unsigned long i = 0; i < sizeof bytes; ++i)
        if (bytes[i] != expected[i])
            return 73;
    if (send("CONSOLE ECHO:", 13) || send(bytes, sizeof bytes) ||
        send("\n0123456789abcdefghijklmnopqrstuv\n", 34))
        return 81;
#ifdef HANDOFF_FAULT
    __asm__ __volatile__("ud2");
#else
    if (CALL(0x26002, 0, 0) != 0)
        return 82;
    for (unsigned long op = 0x26000; op <= 0x26003; ++op)
        if (CALL(op, bytes, 1) != -9)
            return 83;
#endif
    return 0;
}
