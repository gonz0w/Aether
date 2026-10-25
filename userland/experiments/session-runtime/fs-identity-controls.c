/* SPDX-License-Identifier: BSD-2-Clause */
#include "fs-identity.h"
#include <assert.h>
#include <limits.h>

static void put32(unsigned char *frame, unsigned offset, unsigned value)
{
    for (unsigned i = 0; i < 4; ++i)
        frame[offset + i] = (unsigned char)(value >> (8 * i));
}

static void greeting(unsigned char frame[32], unsigned slot, unsigned epoch,
                     unsigned parent, unsigned shell)
{
    memcpy(frame, "AEFSH001", 8);
    put32(frame, 8, 29);
    put32(frame, 12, 7);
    put32(frame, 16, slot);
    put32(frame, 20, epoch);
    put32(frame, 24, parent);
    put32(frame, 28, shell);
}

static void reject(const unsigned char *frame, size_t length, uint64_t memory,
                   long pid, long parent)
{
    struct aether_fs_session_identity result = {91, 92, 93};
    assert(
        !aether_fs_session_decode(frame, length, memory, pid, parent, &result));
    assert(result.slot == 91 && result.epoch == 92 &&
           result.shell_generation == 93);
}

int main(void)
{
    /* Literal native seven-domain PID rows, independent of decoder arithmetic.
     */
    static const long child_pids[15][3] = {
        {10, 11, 12}, {17, 18, 19},    {24, 25, 26},   {31, 32, 33},
        {38, 39, 40}, {45, 46, 47},    {52, 53, 54},   {59, 60, 61},
        {66, 67, 68}, {73, 74, 75},    {80, 81, 82},   {87, 88, 89},
        {94, 95, 96}, {101, 102, 103}, {108, 109, 110}};
    static const long shell_pids[3] = {9, 16, 23};
    static const unsigned wrong_owner_pids[] = {0,  1,  6,  8,       9,
                                                14, 21, 28, UINT_MAX};
    unsigned char frame[32];
    struct aether_fs_session_identity result;
    for (unsigned shell = 1; shell <= 3; ++shell) {
        greeting(frame, 1, shell, 7, shell);
        uint64_t parent_memory = UINT64_C(0x40000002) + (uint64_t)shell * 256;
        assert(aether_fs_session_decode(frame, 32, parent_memory,
                                        shell_pids[shell - 1], 7, &result));
        assert(result.slot == 1 && result.epoch == shell &&
               result.shell_generation == shell);
        for (unsigned i = 0;
             i < sizeof wrong_owner_pids / sizeof *wrong_owner_pids; ++i) {
            /* Neither a forged frame nor a forged native observation may
             * turn a different owner generation into this boot owner. */
            unsigned wrong = wrong_owner_pids[i];
            reject(frame, 32, parent_memory, shell_pids[shell - 1], wrong);
            greeting(frame, 1, shell, wrong, shell);
            reject(frame, 32, parent_memory, shell_pids[shell - 1], 7);
            reject(frame, 32, parent_memory, shell_pids[shell - 1], wrong);
            greeting(frame, 1, shell, 7, shell);
        }
        put32(frame, 20, shell == 3 ? 1 : shell + 1);
        reject(frame, 32, parent_memory, shell_pids[shell - 1], 7);
        for (unsigned epoch = 1; epoch <= 15; ++epoch) {
            for (unsigned slot = 2; slot <= 4; ++slot) {
                long pid = child_pids[epoch - 1][slot - 2];
                uint64_t memory =
                    UINT64_C(0x40000000) + (uint64_t)epoch * 256 + slot + 1;
                greeting(frame, slot, epoch, (unsigned)shell_pids[shell - 1],
                         shell);
                assert(aether_fs_session_decode(
                    frame, 32, memory, pid, shell_pids[shell - 1], &result));
                assert(result.slot == slot && result.epoch == epoch &&
                       result.shell_generation == shell);
                reject(frame, 32, memory ^ UINT64_C(0x100000000), pid,
                       shell_pids[shell - 1]);
                reject(frame, 32, memory + 256, pid, shell_pids[shell - 1]);
                reject(frame, 32, memory + 1, pid, shell_pids[shell - 1]);
                reject(frame, 32, memory, pid - 1, shell_pids[shell - 1]);
                reject(frame, 32, memory, pid, shell_pids[shell - 1] + 1);
            }
        }
    }
    greeting(frame, 2, 1, 9, 1);
    uint64_t memory = UINT64_C(0x40000103);
    for (size_t length = 0; length < 32; ++length)
        reject(frame, length, memory, 10, 9);
    reject(frame, 33, memory, 10, 9);
    reject(NULL, 32, memory, 10, 9);
    assert(!aether_fs_session_decode(frame, 32, memory, 10, 9, NULL));
    /* Every framing/identity bit is material. No partial output on any failure.
     */
    for (unsigned offset = 0; offset < 32; ++offset) {
        for (unsigned bit = 0; bit < 8; ++bit) {
            frame[offset] ^= (unsigned char)(1U << bit);
            reject(frame, 32, memory, 10, 9);
            frame[offset] ^= (unsigned char)(1U << bit);
        }
    }
    static const unsigned invalid_slots[] = {0, 5, 6, 7, UINT_MAX};
    for (unsigned i = 0; i < sizeof invalid_slots / sizeof *invalid_slots;
         ++i) {
        greeting(frame, invalid_slots[i], 1, 9, 1);
        reject(frame, 32, UINT64_C(0x40000100) | (invalid_slots[i] + 1U),
               8 + (long)invalid_slots[i], 9);
    }
    greeting(frame, 1, 1, 9, 1);
    reject(frame, 32, UINT64_C(0x40000102), 9, 9);
    greeting(frame, 2, 0, 9, 1);
    reject(frame, 32, UINT64_C(0x40000003), 3, 9);
    greeting(frame, 2, 16, 9, 1);
    reject(frame, 32, UINT64_C(0x40001003), 115, 9);
    greeting(frame, 2, 1, 2, 0);
    reject(frame, 32, memory, 10, 2);
    greeting(frame, 2, 1, 30, 4);
    reject(frame, 32, memory, 10, 30);
    greeting(frame, 2, 1, 9, 1);
    put32(frame, 24, 7);
    reject(frame, 32, memory, 10, 7);
    put32(frame, 24, 9);
    reject(frame, 32, memory, 9, 7); /* Legacy ABI24 child PID/parent. */
    for (long pid = -1; pid <= 120; ++pid) {
        int expected = 0;
        for (unsigned epoch = 0; epoch < 15; ++epoch)
            for (unsigned slot = 0; slot < 3; ++slot)
                if (pid == child_pids[epoch][slot])
                    expected = 1;
        assert(aether_fs_session_child_pid(pid) == expected);
    }
    assert(!aether_fs_session_child_pid(LONG_MAX));
    assert(!aether_fs_session_child_pid(LONG_MIN));
    return 0;
}
