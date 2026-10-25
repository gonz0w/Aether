/* SPDX-License-Identifier: BSD-2-Clause */
#include "native-io.h"
#include "../native-channel/channel.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/auxv.h>

static unsigned char bootstrap[32], reply[32];
static unsigned boot_used, received, written, calls, forbidden, active;

static void need(int ok, const char *name)
{
    if (!ok) {
        fprintf(stderr, "ORACLE: %s\n", name);
        exit(90);
    }
}

static void put(unsigned char *p, unsigned value)
{
    for (unsigned i = 0; i < 4; ++i)
        p[i] = (unsigned char)(value >> (i * 8));
}

unsigned long getauxval(unsigned long key)
{
    return key == 0xa001 ? 101 : key == 0xa002 ? 202 : 0;
}

void channel_yield(void) {}

long channel_raw(unsigned long op, unsigned long grant, unsigned long address,
                 unsigned long count)
{
    ++calls;
    need(!forbidden, "no-replay-traffic");
    if (op == 0x20005)
        return 1;
    need(op == 0x24001 || op == 0x24002, "operation");
    int writing = op == 0x24002;
    need(grant == (writing ? 202u : 101u), "grant");
    need(count && count <= (writing ? 7u : 5u), "transfer-limit");
    if (!active) {
        need(!writing && count <= 32 - boot_used, "bootstrap-read");
        memcpy((void *)address, bootstrap + boot_used, count);
        boot_used += (unsigned)count;
        return (long)count;
    }
    if (writing) {
        need(count <= 384 - written, "request-overrun");
        written += (unsigned)count;
        return (long)count;
    }
    need(count <= 32 - received, "reply-overrun");
    memcpy((void *)address, reply + received, count);
    received += (unsigned)count;
    return (long)count;
}

int main(void)
{
    put(bootstrap + 4, 0x71000001);
    put(bootstrap + 8, 3);
    put(bootstrap + 12, 1);
    put(bootstrap + 16, 0x71010001);
    put(bootstrap + 20, 4);
    put(bootstrap + 24, 3);
    need(native_bootstrap(0), "bootstrap");
    active = 1;
    calls = 0;
    for (unsigned round = 0; round < 256; ++round) {
        unsigned char request[32] = {0}, out[32];
        put(reply, 2);
        reply[16] = 'O';
        reply[17] = 'K';
        received = written = 0;
        need(native_exchange(request, 32, out), "exchange");
        need(native_word(out) == 2 && out[16] == 'O' && out[17] == 'K',
             "reply-bytes");
    }
    need(calls == 3072, "channel-count");
    unsigned before = calls;
    unsigned char bad[32], out[32];
    need(!native_exchange(bad, 16, out), "invalid-size");
    need(calls == before, "invalid-size-traffic");
    forbidden = 1;
    need(!native_exchange(bad, 32, out), "poisoned-exchange");
    need(calls == before, "no-replay-traffic");
    puts("PASS: transport stress");
    return 0;
}
