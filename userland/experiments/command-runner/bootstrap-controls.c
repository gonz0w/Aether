/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only scripted peer. The adapter is separately compiled, not
 * reimplemented. */
#include "native-io.h"
#include "../native-channel/channel.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/auxv.h>

extern long __aether_io(unsigned long, unsigned long, unsigned long,
                        unsigned long);
static unsigned char stream[64], sent[64];
static unsigned cursor, length = 64, written, calls, aux_calls;
static unsigned generation = 1, child;
static unsigned long in = 101, out = 202;

static void require(int ok, const char *name)
{
    if (!ok) {
        fprintf(stderr, "ORACLE: %s\n", name);
        exit(90);
    }
}

/* Independent little-endian fixture writer; do not use adapter serialization.
 */
static void put(unsigned offset, unsigned value)
{
    for (unsigned i = 0; i < 4; ++i)
        stream[offset + i] = (unsigned char)(value >> (i * 8));
}

unsigned long getauxval(unsigned long key)
{
    ++aux_calls;
    return key == 0xa001 ? in : key == 0xa002 ? out : 0;
}

void channel_yield(void) { require(0, "unexpected-yield"); }

long channel_raw(unsigned long op, unsigned long grant, unsigned long address,
                 unsigned long size)
{
    ++calls;
    if (op == 0x20005) {
        require(!grant && !address && !size, "generation-arguments");
        return generation;
    }
    require(op == 0x24001 || op == 0x24002, "channel-operation");
    require(grant == (op == 0x24001 ? in : out), "channel-grant");
    require(size && size <= (op == 0x24001 ? 5u : 7u), "transfer-bound");
    if (op == 0x24001) {
        if (cursor == length)
            return 0;
        if (size > length - cursor)
            size = length - cursor;
        memcpy((void *)address, stream + cursor, size);
        cursor += (unsigned)size;
    } else {
        /* Refuse an attempted launch; its very first call violates startup. */
        if (!written && *(const unsigned char *)address == 4)
            return 0;
        require(size <= sizeof sent - written, "send-bound");
        memcpy(sent + written, (void *)address, size);
        written += (unsigned)size;
    }
    return (long)size;
}

int main(int argc, char **argv)
{
    require(argc == 2, "case-argument");
    const char *mode = argv[1];
    child = strstr(mode, "child") != NULL;
    if (strstr(mode, "gen2"))
        generation = 2;
    unsigned prefix = child ? 0x72000000u : 0x71000000u;
    for (unsigned i = 0; i < 2; ++i) {
        put(4 + 12 * i, prefix | (i << 16) | generation);
        put(8 + 12 * i, child ? i : 3 + i);
        put(12 + 12 * i, i ? (child ? 2 : 3) : 1);
    }
    int valid = !strncmp(mode, "valid-", 6);
    if (!strncmp(mode, "bad-word-", 9)) {
        unsigned word = (unsigned)strtoul(mode + 9, NULL, 10);
        require(word < 8, "word-index");
        stream[word * 4] ^= 0x80;
    } else if (!strcmp(mode, "bad-generation")) {
        generation = 3;
    } else if (!strcmp(mode, "missing-input")) {
        in = 0;
    } else if (!strcmp(mode, "missing-output")) {
        out = 0;
    } else if (!strcmp(mode, "missing-both")) {
        in = out = 0;
    } else if (!strcmp(mode, "equal-channels")) {
        out = in;
    } else if (!strncmp(mode, "prefix-", 7)) {
        length = (unsigned)strtoul(mode + 7, NULL, 10);
        require(length < 32, "prefix-bound");
    } else {
        require(valid, "known-case");
    }
    require(native_bootstrap((int)child) == valid, "bootstrap-result");
    unsigned saved = calls, saved_aux = aux_calls;
    if (valid) {
        require(native_ref(0) == (prefix | generation) &&
                    native_ref(1) == (prefix | 0x10000u | generation),
                "published-pair");
        require(!native_bootstrap((int)child), "successful-reentry");
        require(calls == saved && aux_calls == saved_aux, "reentry-traffic");
        unsigned fd = child ? 0 : 3;
        unsigned char sentinel = 0xa5;
        errno = EDOM;
        require(__aether_io(1, fd, (unsigned long)&sentinel, 1) == -EACCES,
                "read-only-rights");
        require(calls == saved, "denial-traffic");
        require(__aether_io(0, fd, (unsigned long)&sentinel, 1) == 0,
                "live-read-after-reentry");
        require(sentinel == 0xa5 && errno == EDOM, "sentinel-errno");
        unsigned char expected[32] = {1};
        unsigned ref = prefix | generation;
        for (unsigned i = 0; i < 4; ++i) {
            expected[4 + i] = (unsigned char)(ref >> (8 * i));
            expected[8 + i] = (unsigned char)(fd >> (8 * i));
        }
        expected[12] = 1;
        require(written == 32 && !memcmp(sent, expected, 32),
                "exact-read-frame");
        require(cursor == 64, "exact-read-reply");
    } else {
        require(!native_ref(0) && !native_ref(1), "no-published-references");
        unsigned char sentinel = 0xa5;
        for (unsigned fd = 0; fd < 5; ++fd) {
            for (unsigned op = 0; op < 4; ++op) {
                if (op == 2)
                    continue;
                require(__aether_io(op, fd, (unsigned long)&sentinel, 1) ==
                            -EBADF,
                        "no-live-binding");
            }
        }
        require(sentinel == 0xa5 && calls == saved,
                "no-failed-startup-effects");
        require(!native_bootstrap((int)child), "failed-startup-retry-result");
        require(calls == saved && aux_calls == saved_aux,
                "failed-startup-retry-traffic");
        unsigned char request[384] = {4}, reply[32];
        require(!native_exchange(request, sizeof request, reply),
                "failed-startup-exchange");
        require(calls == saved && !written, "failed-startup-exchange-traffic");
    }
    puts("PASS: bootstrap boundary");
    return 0;
}
