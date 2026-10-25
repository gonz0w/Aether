/* SPDX-License-Identifier: BSD-2-Clause */
#include "transport.h"
#include "result.h"
#include <unistd.h>
#ifdef RUNNER_STARTUP
static char forwarded[6][32];
static unsigned forwarded_count;
#include "startup-probe.h"
#endif
static _Thread_local volatile unsigned cookie = 23;
int main(int argc, char **argv)
{
#ifdef RUNNER_STARTUP
    if (!startup_probe())
        return 110;
#endif
    if (cookie != 23 || argc != 1 || strcmp(argv[0], "client") ||
        !result_policy_probe() || !bootstrap())
        return 110;
    unsigned char b[384] = {0};
    put(b, 0, 4);
    put(b, 4, 1);
    put(b, 8, 2);
    put(b, 12, 1);
    put(b, 16, 2);
    memcpy(b + 32, "bytecount", 9);
    memcpy(b + 128, "bytecount", 9);
    memcpy(b + 160, "--decimal", 9);
    memcpy(b + 192, "LC_ALL=C", 8);
#ifdef RUNNER_STARTUP
    memset(b + 128, 0, 256);
    unsigned count = forwarded_count - FORWARD_FIRST;
    put(b, 8, count);
    memcpy(b + 32, forwarded[FORWARD_FIRST], 32);
    for (unsigned j = 0; j < count; j++)
        memcpy(b + 128 + j * 32, forwarded[FORWARD_FIRST + j], 32);
    memcpy(b + 128 + count * 32, "LC_ALL=C", 8);
#ifdef CORRUPT_FORWARDED
    b[224] = 'Y';
#endif
#endif
#ifdef SUCCESS_HELPER_ARGV
    memset(b + 32, 0, 32);
    memset(b + 128, 0, 256);
    put(b, 8, 4);
    put(b, 12, 2);
    memcpy(b + 32, "/inputs/helper", 14);
    memcpy(b + 128, "/inputs/helper", 14);
    memcpy(b + 160, "argv", 4);
    memcpy(b + 192, "a b", 3);
    memcpy(b + 224, "*", 1);
    memcpy(b + 256, "LC_ALL=C", 8);
    memcpy(b + 288, "WITNESS=value", 13);
#endif
    for (unsigned j = 0; j < 2; j++) {
        unsigned at = 64 + j * 32;
        put(b, at, refs[j + 2]);
        put(b, at + 4, j + 3);
        put(b, at + 8, j);
        put(b, at + 12, j ? 2 : 1);
    }
    unsigned receipt = 0x73000000u | (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    if (!exchange(b, sizeof b) || get(b, 0) || get(b, 4) != receipt)
        return 111;
    for (unsigned j = 8; j < 32; j++)
        if (b[j])
            return 111;
    memset(b, 0xa5, sizeof b);
    if (close(3))
        return 112;
    unsigned detail = 0, kind = 1;
#ifndef SUCCESS_SKIP_COLLECT
    int result = -11;
    for (unsigned t = 0; t < 100000 && result == -11; t++) {
        memset(b, 0, 32);
        put(b, 0, 5);
        put(b, 4, receipt);
#ifdef SUCCESS_STALE_COLLECT
        if ((receipt & 0xffffu) == 2)
            put(b, 4, receipt - 1);
#endif
        if (!exchange(b, 32))
            return 113;
        result = (int)get(b, 0);
    }
    if (result || get(b, 4) != receipt || (get(b, 12) != 1 && get(b, 12) != 2))
        return 114;
    for (unsigned j = 16; j < 32; j++)
        if (b[j])
            return 114;
    detail = get(b, 8);
    kind = get(b, 12);
    memset(b, 0, 32);
    put(b, 0, 5);
    put(b, 4, receipt);
    if (!exchange(b, 32) || (int)get(b, 0) != -10)
        return 115;
    for (unsigned j = 4; j < 32; j++)
        if (b[j])
            return 115;
    char probe;
    if (read(4, &probe, 1) != 0)
        return 116;
#endif
    int failed = 0;
    if (close(4))
        failed = 1;
#ifndef SUCCESS_SKIP_CLOSE
    if (close(1))
        failed = 1;
#endif
    if (close(2))
        failed = 1;
#ifdef SUCCESS_HELPER_ARGV
    if (cookie != 23) return 117;
#endif
#ifdef SUCCESS_FORCE_ZERO
    (void)kind;
    (void)detail;
    (void)failed;
    return 0;
#elif defined(SUCCESS_IGNORE_KIND)
    (void)kind;
    return (int)runner_result(1, detail, !failed);
#else
    return (int)runner_result(kind, detail, !failed);
#endif
}
