/* SPDX-License-Identifier: BSD-2-Clause */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned long input = 0x1234, output = 0x5678;
static int poisoned;
static unsigned char frame[48], delivered[48];
static unsigned position, transfers, waits, stalls, calls;
static int fixture_writing, failure, after_hint, bad;
static long transfer_failure, wait_failure;

static long memtrap(unsigned long op, unsigned long cap, unsigned long pointer,
                    unsigned long count, unsigned long reserved)
{
    calls++;
    if (cap != (fixture_writing ? output : input) || reserved)
        bad = 1;
    if (op == 0x24004) {
        waits++;
        if (pointer || count || !after_hint)
            bad = 1;
        after_hint = 0;
        return wait_failure;
    }
    transfers++;
    if (op != (fixture_writing ? 0x24002ul : 0x24001ul) ||
        pointer != (uintptr_t)(frame + position) || !count || count > 16 ||
        count > sizeof(frame) - position || after_hint)
        bad = 1;
    /* Make progress first, then force arbitrarily many readiness rescans. */
    if (position >= 3 && stalls) {
        stalls--;
        after_hint = 1;
        return -11;
    }
    if (position >= 3 && failure)
        return transfer_failure;
    unsigned n = count > 3 ? 3 : (unsigned)count;
    if (fixture_writing)
        memcpy(delivered + position, (void *)pointer, n);
    else
        memcpy((void *)pointer, delivered + position, n);
    position += n;
    return n;
}

#include "channel-transfer.h"

static int check(int direction, unsigned blocked, long wait_result,
                 int fail_transfer, long transfer_result)
{
    fixture_writing = direction;
    stalls = blocked;
    wait_failure = wait_result;
    failure = fail_transfer;
    transfer_failure = transfer_result;
    poisoned = 0;
    position = transfers = waits = calls = 0;
    after_hint = bad = 0;
    for (unsigned i = 0; i < sizeof(frame); i++) {
        frame[i] = direction ? (unsigned char)(i + 1) : 0;
        delivered[i] = direction ? 0 : (unsigned char)(i + 1);
    }
    int expected = !wait_result && !fail_transfer;
    if (move(frame, sizeof(frame), direction) != expected || bad ||
        poisoned != !expected)
        return 1;
    if (expected) {
        if (position != sizeof(frame) || waits != blocked ||
            memcmp(frame, delivered, sizeof(frame)))
            return 2;
    } else {
        unsigned before = calls;
        if (position != 3 || move(frame, sizeof(frame), direction) ||
            calls != before || waits != (blocked ? 1u : 0u))
            return 3;
    }
    return 0;
}

int main(void)
{
    unsigned cases = 0;
    for (int direction = 0; direction < 2; direction++) {
        const unsigned blocked[] = {0, 1, 100001};
        for (unsigned i = 0; i < sizeof(blocked) / sizeof(blocked[0]); i++) {
            if (check(direction, blocked[i], 0, 0, 0))
                return 10;
            cases++;
        }
        const long wait_errors[] = {-38, -13, -22, -4, 1};
        for (unsigned i = 0; i < sizeof(wait_errors) / sizeof(wait_errors[0]);
             i++) {
            if (check(direction, 1, wait_errors[i], 0, 0))
                return 20;
            cases++;
        }
        const long transfer_errors[] = {0, -13, -4, -38, 17, 46};
        for (unsigned i = 0;
             i < sizeof(transfer_errors) / sizeof(transfer_errors[0]); i++) {
            if (check(direction, 0, 0, 1, transfer_errors[i]))
                return 30;
            cases++;
        }
    }
    printf("PASS channel-transfer cases=%u\n", cases);
    return 0;
}
