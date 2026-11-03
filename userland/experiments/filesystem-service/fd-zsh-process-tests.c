/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-zsh-process.h"
#include <assert.h>
#include <stdio.h>
static struct aefd_startup_auxv parent = {0x40000102, 71, 72};
static struct aefd_startup_auxv child = {0x40000103, 81, 82};
static void put32(unsigned char *raw, unsigned at, uint32_t value)
{
    for (unsigned i = 0; i < 4; ++i)
        raw[at + i] = (unsigned char)(value >> (i * 8));
}
static void snapshot(unsigned char raw[336], int copied)
{
    memset(raw, 0, 336);
    memcpy(raw, "AEFDB009", 8);
    put32(raw, 8, 1);
    put32(raw, 12, 336);
    memcpy(raw + 16, "AEFSH001", 8);
    put32(raw, 24, 29);
    put32(raw, 28, 7);
    put32(raw, 32, copied ? 2 : 1);
    put32(raw, 36, 1);
    put32(raw, 40, copied ? 9 : 7);
    put32(raw, 44, 1);
    memcpy(raw + 48, "AEFDT009", 8);
    aefd_put(raw + 48, 1, copied ? 32 : 31);
    aefd_put(raw + 48, 2, 16);
    for (unsigned i = 0; i < 3; ++i) {
        raw[112 + i * 4] = 4;
        raw[113 + i * 4] = (unsigned char)i;
        put32(raw, 176 + i * 16, 0x7a000001 | i << 16);
        put32(raw, 180 + i * 16, i);
        put32(raw, 184 + i * 16, i ? 2 : 1);
        put32(raw, 188 + i * 16, 16);
    }
    raw[124] = raw[128] = 2;
    raw[125] = 3;
    raw[129] = 4;
    raw[132] = 3;
    raw[133] = 3;
    raw[152] = 5;
    raw[155] = 1;
    for (unsigned i = 3; i < 5; ++i) {
        put32(raw, 176 + i * 16, 0x79000100 | (i - 2));
        put32(raw, 180 + i * 16, i);
        put32(raw, 184 + i * 16, i == 3 ? 1 : 2);
        put32(raw, 188 + i * 16, 16);
    }
    put32(raw, 288, 1);
    put32(raw, 296, copied ? 0 : 0x76050001);
    put32(raw, 300, copied ? 0 : 0x7d000001);
    for (unsigned i = 0; i < 4; ++i)
        put32(raw, 304 + i * 4, 1000);
    put32(raw, 320, 1);
}
int main(void)
{
    unsigned char original[336], copied[336], frame[672], saved[672],
        arguments[272] = {0};
    snapshot(original, 0);
    snapshot(copied, 1);
    struct aefd_zsh_snapshot view = {0};
    assert(aefd_zsh_snapshot_decode(original, 336, parent, 9, 7, &view));
    assert(view.identity.slot == 1 && view.generation == 31);
    assert(aefd_zsh_snapshot_decode(copied, 336, child, 10, 9, &view));
    assert(view.identity.slot == 2 && view.generation == 32);
    assert(aefd_zsh_fork_encode(frame, 368, original, parent, 9, 7, 41));
    assert(!memcmp(frame + 32, original, 336));
    uint64_t sequence = 0;
    assert(
        aefd_zsh_fork_decode(frame, 368, parent, 9, 7, 31, &view, &sequence) &&
        sequence == 41);
    assert(
        aefd_zsh_child_match(frame, 368, parent, 9, copied, child, 10, &view));
    aefd_put(arguments, 0, 2);
    memcpy(arguments + 16, "/inputs/helper", 14);
    memcpy(arguments + 48, "status", 6);
    assert(aefd_zsh_exec_encode(frame, 672, copied, child, 10, 9, 42,
                                "/inputs/helper", arguments));
    assert(!memcmp(frame + 32, copied, 336) &&
           !memcmp(frame + 400, arguments, 272));
    assert(
        aefd_zsh_exec_decode(frame, 672, child, 10, 9, 32, &view, &sequence) &&
        sequence == 42);
    memcpy(saved, frame, sizeof(frame));
    for (size_t n = 0; n < sizeof(frame); ++n)
        assert(!aefd_zsh_exec_decode(frame, n, child, 10, 9, 32, &view,
                                     &sequence));
    for (unsigned at = 0; at < 32; ++at) {
        memcpy(frame, saved, sizeof(frame));
        frame[at] ^= 0x80;
        if (at >= 16 && at < 24)
            continue; /* Other nonzero sequence is valid data. */
        assert(!aefd_zsh_exec_decode(frame, 672, child, 10, 9, 32, &view,
                                     &sequence));
    }
    memcpy(frame, saved, sizeof(frame));
    frame[39] = '8';
    assert(
        !aefd_zsh_exec_decode(frame, 672, child, 10, 9, 32, &view, &sequence));
    memcpy(frame, saved, sizeof(frame));
    frame[400 + 271] = 1;
    assert(
        !aefd_zsh_exec_decode(frame, 672, child, 10, 9, 32, &view, &sequence));
    assert(
        !aefd_zsh_exec_decode(saved, 672, child, 10, 9, 33, &view, &sequence));
    assert(!aefd_zsh_exec_encode(frame, 672, original, parent, 9, 7, 44,
                                 "/inputs/helper", arguments));
    snapshot(copied, 1);
    copied[300] = 1;
    assert(!aefd_zsh_snapshot_decode(copied, 336, child, 10, 9, &view));
    snapshot(copied, 1);
    copied[155] = 0;
    assert(!aefd_zsh_snapshot_decode(copied, 336, child, 10, 9, &view));
    snapshot(copied, 1);
    copied[324] = 1;
    assert(!aefd_zsh_snapshot_decode(copied, 336, child, 10, 9, &view));
    snapshot(copied, 1);
    put32(copied, 32, 3);
    assert(!aefd_zsh_snapshot_decode(copied, 336, child, 10, 9, &view));
    unsigned char receipt[32];
    assert(aefd_zsh_receipt_encode(receipt, "AEZFR001", 41, 10));
    int64_t result = 0;
    assert(aefd_zsh_receipt_decode(receipt, "AEZFR001", 41, &result) &&
           result == 10);
    assert(!aefd_zsh_receipt_decode(receipt, "AEZER001", 41, &result));
    assert(!aefd_zsh_receipt_encode(receipt, "AEZER001", 41, 7));
    assert(!aefd_zsh_receipt_encode(receipt, "AEZFC001", 41, -13));
    assert(!aefd_zsh_receipt_encode(receipt, "AEZFR001", 41, 11));
    assert(!aefd_zsh_receipt_encode(receipt, "AEZFR001", UINT64_MAX, 10));
    receipt[31] = 1;
    assert(!aefd_zsh_receipt_decode(receipt, "AEZFR001", 41, &result));
    puts("ZSH_PROCESS_CODEC_PASS");
    return 0;
}
