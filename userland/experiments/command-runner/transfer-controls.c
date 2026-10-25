/* SPDX-License-Identifier: BSD-2-Clause */
/* Host scripted peer; adapter is linked as a separate translation unit. */
#include "native-io.h"
#include "../native-channel/channel.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/auxv.h>
extern long __aether_io(unsigned long, unsigned long, unsigned long,
                        unsigned long);
static unsigned char bootstrap[32], reply[32], sent[384];
static unsigned boot_used, received, written, calls, yields, turn;
static const char *mode;
static int active, forbidden;

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
void channel_yield(void) { ++yields; }
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
    ++turn;
    if (!strncmp(mode, "tx-", 3) && writing) {
        if (!strcmp(mode, "tx-eagain"))
            return -EAGAIN;
        if (!strcmp(mode, "tx-error"))
            return -EPIPE;
        if (!strcmp(mode, "tx-zero"))
            return 0;
        if (!strcmp(mode, "tx-overlong"))
            return (long)count + 1;
    }
    if (!writing && (!strncmp(mode, "rx-", 3) || !strcmp(mode, "close-lost"))) {
        if (!strcmp(mode, "rx-eagain"))
            return -EAGAIN;
        if (!strcmp(mode, "rx-error"))
            return -EPIPE;
        if (!strcmp(mode, "rx-overlong"))
            return (long)count + 1;
        if (!strcmp(mode, "rx-zero") || !strcmp(mode, "close-lost"))
            return 0;
        if (!strcmp(mode, "rx-partial") && received >= 5)
            return 0;
    }
    if (!strcmp(mode, "short-eagain") && turn % 3 == 1)
        return -EAGAIN;
    if (!strcmp(mode, "short-eagain") || !strcmp(mode, "short"))
        count = 1;
    if (writing) {
        need(count <= sizeof sent - written, "request-overrun");
        memcpy(sent + written, (void *)address, count);
        written += (unsigned)count;
    } else {
        need(count <= sizeof reply - received, "reply-overrun");
        memcpy((void *)address, reply + received, count);
        received += (unsigned)count;
    }
    return (long)count;
}
static void no_replay(unsigned fd, int closed)
{
    unsigned before = calls;
    forbidden = 1;
    unsigned char bytes[16], q[384] = {4}, r[32];
    memset(bytes, 0xa5, sizeof bytes);
    need(__aether_io(0, fd, (unsigned long)bytes, sizeof bytes) ==
             (closed ? -EBADF : -EIO),
         "poisoned-file");
    need(!native_exchange(q, sizeof q, r), "poisoned-launch");
    q[0] = 5;
    need(!native_exchange(q, 32, r), "poisoned-collection");
    need(__aether_io(3, fd, 0, 0) == (closed ? -EBADF : -EIO),
         "poisoned-close");
    need(__aether_io(3, fd, 0, 0) == -EBADF, "close-once");
    need(calls == before, "no-replay-traffic");
}
int main(int argc, char **argv)
{
    need(argc == 2, "case-argument");
    mode = argv[1];
    put(bootstrap + 4, 0x71000001);
    put(bootstrap + 8, 3);
    put(bootstrap + 12, 1);
    put(bootstrap + 16, 0x71010001);
    put(bootstrap + 20, 4);
    put(bootstrap + 24, 3);
    need(native_bootstrap(0), "bootstrap");
    active = 1;
    calls = 0;
    unsigned char data[16];
    memset(data, 0xa5, sizeof data);
    if (!strncmp(mode, "size-", 5)) {
        unsigned size = (unsigned)strtoul(mode + 5, NULL, 10);
        unsigned char q[384] = {4}, r[32];
        need(size != 32 && size != 384 && size <= sizeof q, "case-size");
        need(!native_exchange(q, size, r), "invalid-size");
        need(!calls, "invalid-size-traffic");
        no_replay(3, 0);
    } else {
        int closing = !strncmp(mode, "close-", 6);
        int writing = !strncmp(mode, "write-", 6);
        int poison = 1;
        long expected = -EIO;
        put(reply, 2);
        reply[16] = 'O';
        reply[17] = 'K';
        if (!strcmp(mode, "short") || !strcmp(mode, "short-eagain")) {
            expected = 2;
            poison = 0;
        } else if (!strncmp(mode, "error-", 6)) {
            expected = -(long)strtoul(mode + 6, NULL, 10);
            memset(reply, 0, sizeof reply);
            put(reply, (unsigned)expected);
            poison = 0;
        } else if (!strncmp(mode, "metadata-", 9)) {
            unsigned offset = (unsigned)strtoul(mode + 9, NULL, 10);
            need(offset >= 4 && offset < 16, "metadata-offset");
            reply[offset] = 1;
        } else if (!strncmp(mode, "padding-", 8)) {
            unsigned offset = (unsigned)strtoul(mode + 8, NULL, 10);
            need(offset >= 18 && offset < 32, "padding-offset");
            reply[offset] = 1;
        } else if (!strcmp(mode, "result-overlong")) {
            put(reply, 17);
        } else if (!strcmp(mode, "result-negative-range")) {
            memset(reply, 0, sizeof reply);
            put(reply, (unsigned)-4096);
        } else if (closing || writing) {
            memset(reply, 0, sizeof reply);
            if (!strcmp(mode, "close-negative"))
                put(reply, (unsigned)-EIO);
            else if (!strcmp(mode, "close-positive"))
                put(reply, 1);
            else if (!strcmp(mode, "close-padding") ||
                     !strcmp(mode, "write-padding"))
                reply[16] = 1;
            else if (!strcmp(mode, "write-valid")) {
                put(reply, 2);
                expected = 2;
                poison = 0;
            } else if (!strcmp(mode, "close-valid")) {
                expected = 0;
                poison = 0;
            } else
                need(!strcmp(mode, "close-lost"), "known-close-write");
        } else {
            need(!strncmp(mode, "tx-", 3) || !strncmp(mode, "rx-", 3),
                 "known-case");
        }
        unsigned fd = writing ? 4 : 3;
        errno = EDOM;
        long result = __aether_io(closing   ? 3
                                  : writing ? 1
                                            : 0,
                                  fd, (unsigned long)data, sizeof data);
        need(result == expected, "reply-result");
        need(errno == EDOM, "errno-preserved");
        for (unsigned i = 0; i < sizeof data; ++i)
            need(data[i] == (!closing && !writing && expected > 0 && i < 2
                                 ? (unsigned char)"OK"[i]
                                 : 0xa5),
                 "destination-sentinel");
        if (strncmp(mode, "tx-", 3)) {
            unsigned char want[32] = {0};
            put(want, closing ? 3 : writing ? 2 : 1);
            put(want + 4, writing ? 0x71010001 : 0x71000001);
            put(want + 8, fd);
            put(want + 12, closing ? 0 : 16);
            if (writing)
                memset(want + 16, 0xa5, 16);
            need(written == 32 && !memcmp(want, sent, 32), "exact-request");
        } else {
            need(!written, "refused-request");
        }
        if (!strcmp(mode, "tx-eagain"))
            need(calls == 100000 && yields == 100000, "tx-budget");
        if (!strcmp(mode, "rx-eagain"))
            need(calls == 100005 && yields == 100000, "rx-budget");
        if (!strcmp(mode, "short-eagain"))
            need(yields && received == 32, "short-progress");
        if (poison)
            no_replay(fd, closing);
        else if (closing) {
            unsigned before = calls;
            need(__aether_io(3, fd, 0, 0) == -EBADF && calls == before,
                 "valid-close-once");
        } else {
            /* A valid negative reply must not poison the connection. */
            written = received = 0;
            memset(reply, 0, sizeof reply);
            need(__aether_io(0, fd, (unsigned long)data, 0) == 0,
                 "usable-after-reply");
        }
    }
    puts("PASS: transfer boundary");
    return 0;
}
