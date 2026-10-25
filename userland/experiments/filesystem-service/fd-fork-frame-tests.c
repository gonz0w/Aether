/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-fork-frame.h"
#include <assert.h>
#include <stdio.h>
static unsigned cases;
static void put32(unsigned char *raw, unsigned offset, uint32_t value)
{
    for (unsigned i = 0; i < 4; ++i)
        raw[offset + i] = (unsigned char)(value >> (i * 8));
}
static struct aefd_startup_auxv observed = {UINT64_C(0x40000102), 71, 72};
static void snapshot(unsigned char raw[304])
{
    memset(raw, 0, 304);
    memcpy(raw, AEFD_STARTUP_MAGIC, 8);
    put32(raw, 8, 1);
    put32(raw, 12, 304);
    memcpy(raw + 16, "AEFSH001", 8);
    put32(raw, 24, 29);
    put32(raw, 28, 7);
    put32(raw, 32, 1);
    put32(raw, 36, 1);
    put32(raw, 40, 7);
    put32(raw, 44, 1);
    memcpy(raw + 48, AEFD_MAP_MAGIC, 8);
    aefd_put(raw + 48, 1, 17);
    aefd_put(raw + 48, 2, 16);
    const unsigned char slots[24] = {1, 0, 1, 0, 1, 1, 0, 0, 1, 2, 0, 0,
                                     3, 3, 1, 0, 2, 3, 0, 0, 2, 4, 1, 0};
    memcpy(raw + 112, slots, sizeof slots);
    for (unsigned i = 0; i < 5; ++i) {
        unsigned offset = 176 + i * 16;
        put32(raw, offset, i < 3 ? 101 + i : UINT32_C(0x79000201) + i - 3);
        put32(raw, offset + 4, i);
        put32(raw, offset + 8, i == 0 || i == 3 ? 1 : 2);
        put32(raw, offset + 12, 16);
    }
    put32(raw, 288, 2);
    put32(raw, 292, 9);
    put32(raw, 296, UINT32_C(0x76050001));
}
static void rejected(const unsigned char *raw, size_t length,
                     struct aefd_startup_auxv aux, long pid, long parent)
{
    struct aefd_fork_view out = {
        .raw = raw, .parent = {4, 15, 3}, .sequence = 99};
    assert(!aefd_fork_decode(raw, length, aux, pid, parent, &out));
    assert(out.raw == raw && out.parent.slot == 4 && out.parent.epoch == 15 &&
           out.parent.shell_generation == 3 && out.sequence == 99);
    ++cases;
}
static void frames(void)
{
    unsigned char input[304], raw[304], bad[304];
    snapshot(input);
    assert(aefd_fork_encode(raw, sizeof raw, input, sizeof input, observed, 9,
                            7, UINT64_C(0x0102030405060708)));
    assert(!memcmp(raw, AEFD_FORK_MAGIC, 8));
    assert(!memcmp(raw + 8, input + 8, 288));
    const unsigned char sequence[8] = {8, 7, 6, 5, 4, 3, 2, 1};
    assert(!memcmp(raw + 296, sequence, 8));
    assert(raw[114] == 1 && raw[126] == 1 && raw[134] == 1);
    struct aefd_fork_view view;
    assert(aefd_fork_decode(raw, 304, observed, 9, 7, &view));
    assert(view.raw == raw && view.parent.slot == 1 &&
           view.sequence == UINT64_C(0x0102030405060708));
    ++cases;
    for (size_t length = 0; length < 304; ++length)
        rejected(raw, length, observed, 9, 7);
    rejected(raw, 305, observed, 9, 7);
    rejected(NULL, 304, observed, 9, 7);
    for (size_t length = 0; length < 16; ++length) {
        assert(aefd_fork_header(raw, length) == 0);
        ++cases;
    }
    assert(aefd_fork_header(raw, 16) == 1);
    assert(aefd_fork_header(raw, 17) == -1);
    assert(aefd_fork_header(NULL, 16) == -1);
    for (unsigned i = 0; i < 296; ++i) {
        // File generation and console references are opaque nonzero labels.
        if ((i >= 56 && i < 64) || (i >= 176 && i < 180) ||
            (i >= 192 && i < 196) || (i >= 208 && i < 212))
            continue;
        memcpy(bad, raw, 304);
        bad[i] ^= 128;
        rejected(bad, 304, observed, 9, 7);
    }
    for (unsigned i = 0; i < 16; ++i) {
        memcpy(bad, raw, 304);
        bad[i] ^= 128;
        assert(aefd_fork_header(bad, 16) == -1);
        ++cases;
    }
    memcpy(bad, raw, 304);
    memset(bad + 296, 0, 8);
    rejected(bad, 304, observed, 9, 7);
    rejected(raw, 304, observed, 10, 7);
    rejected(raw, 304, observed, 9, 14);
    rejected(raw, 304, (struct aefd_startup_auxv){0, 71, 72}, 9, 7);
    rejected(raw, 304, (struct aefd_startup_auxv){observed.memory, 71, 71}, 9,
             7);
    // Missing used source, orphan source, duplicate reference and pipe history.
    for (unsigned which = 0; which < 4; ++which) {
        memcpy(bad, raw, 304);
        if (which == 0)
            memset(bad + 176, 0, 16);
        else if (which == 1)
            memset(bad + 112, 0, 4);
        else if (which == 2)
            put32(bad, 192, 101);
        else
            put32(bad, 288, 1);
        rejected(bad, 304, observed, 9, 7);
    }
    // Valid opaque labels must not be interpreted as authority or rejected.
    memcpy(bad, raw, 304);
    aefd_put(bad + 48, 1, UINT64_MAX);
    put32(bad, 176, 999);
    assert(aefd_fork_decode(bad, 304, observed, 9, 7, &view));
    ++cases;
    memcpy(bad, input, 304);
    assert(aefd_fork_encode(bad, 304, bad, 304, observed, 9, 7, 1));
    assert(aefd_word(bad + 296, 0) == 1 && bad[126] == 1);
    ++cases;
    for (unsigned which = 0; which < 6; ++which) {
        snapshot(input);
        memset(bad, 0x77, 304);
        if (which == 1)
            input[0] = 0;
        if (which == 2)
            input[300] = 1;
        if (which == 3)
            input[296] = 0;
        if (which == 4)
            input[32] = 2;
        assert(!aefd_fork_encode(bad, 304, input, which == 5 ? 303 : 304,
                                 observed, 9, 7, which ? 1 : 0));
        for (unsigned i = 0; i < 304; ++i)
            assert(bad[i] == 0);
        ++cases;
    }
    memset(bad, 0x77, 304);
    assert(!aefd_fork_encode(bad, 303, input, 304, observed, 9, 7, 1));
    for (unsigned i = 0; i < 304; ++i)
        assert(bad[i] == 0x77);
    ++cases;
}
static void replies(void)
{
    unsigned char raw[32] = {0}, bad[32];
    memcpy(raw, "AEFKR001", 8);
    aefd_put(raw, 1, 42);
    int64_t out = 999;
    for (long pid = 1; pid <= 120; ++pid) {
        aefd_put(raw, 2, (uint64_t)pid);
        out = 999;
        int valid = aether_fs_session_child_pid(pid);
        assert(aefd_fork_parent_reply(raw, 32, 42, pid, &out) == valid);
        assert(out == (valid ? pid : 999));
        ++cases;
    }
    for (int64_t error = -1; error >= -4096; --error) {
        aefd_put(raw, 2, (uint64_t)error);
        out = 999;
        assert(aefd_fork_parent_reply(raw, 32, 42, -11, &out) ==
               (error >= -4095));
        assert(out == (error >= -4095 ? error : 999));
        ++cases;
    }
    aefd_put(raw, 2, 10);
    for (size_t length = 0; length < 32; ++length) {
        out = 999;
        assert(!aefd_fork_parent_reply(raw, length, 42, 10, &out));
        assert(out == 999);
        ++cases;
    }
    for (unsigned i = 0; i < 32; ++i) {
        if (i >= 16 && i < 24)
            continue;
        memcpy(bad, raw, 32);
        bad[i] ^= 128;
        out = 999;
        assert(!aefd_fork_parent_reply(bad, 32, 42, 10, &out));
        assert(out == 999);
        ++cases;
    }
    for (unsigned which = 0; which < 6; ++which) {
        memcpy(bad, raw, 32);
        if (which == 0)
            aefd_put(bad, 2, 0);
        if (which == 1)
            aefd_put(bad, 2, UINT64_C(0x8000000000000000));
        if (which == 2)
            aefd_put(bad, 2, UINT64_MAX);
        out = 999;
        assert(!aefd_fork_parent_reply(bad, which == 3 ? 33 : 32,
                                       which == 4 ? 0 : 42, which == 5 ? 11 : 0,
                                       &out));
        assert(out == 999);
        ++cases;
    }
    for (long pid = 1; pid <= 120; ++pid) {
        memset(raw, 0x77, 32);
        int valid = aether_fs_session_child_pid(pid);
        assert(aefd_fork_ready_encode(raw, 32, UINT64_MAX, pid) == valid);
        assert(aefd_fork_ready_decode(raw, 32, UINT64_MAX, pid) == valid);
        if (!valid)
            for (unsigned i = 0; i < 32; ++i)
                assert(raw[i] == 0);
        ++cases;
    }
    assert(aefd_fork_ready_encode(raw, 32, 42, 10));
    for (size_t length = 0; length <= 33; ++length) {
        assert(aefd_fork_ready_decode(raw, length, 42, 10) == (length == 32));
        ++cases;
    }
    for (unsigned i = 0; i < 32; ++i) {
        memcpy(bad, raw, 32);
        bad[i] ^= 128;
        assert(!aefd_fork_ready_decode(bad, 32, 42, 10));
        ++cases;
    }
    assert(!aefd_fork_ready_decode(raw, 32, 41, 10));
    assert(!aefd_fork_ready_decode(raw, 32, 42, 11));
    assert(!aefd_fork_ready_encode(raw, 32, 0, 10));
    ++cases;
}
static void child_frames(void)
{
    unsigned char parent[304], request[304], child[304], bad[304];
    struct aefd_startup_auxv copied = {UINT64_C(0x40000103), 81, 82};
    struct aether_fs_session_identity out;
    snapshot(parent);
    assert(aefd_fork_encode(request, 304, parent, 304, observed, 9, 7, 42));
    memcpy(child, parent, 304);
    put32(child, 32, 2);
    put32(child, 40, 9);
    aefd_put(child + 48, 1, 18);
    memset(child + 296, 0, 8);
    assert(aefd_fork_child_match(request, 304, observed, 9, child, 304, copied,
                                 10, &out));
    assert(out.slot == 2 && out.epoch == 1 && out.shell_generation == 1);
    ++cases;
    for (size_t length = 0; length <= 305; ++length) {
        out = (struct aether_fs_session_identity){4, 15, 3};
        int valid = length == 304;
        assert(aefd_fork_child_match(request, 304, observed, 9, child, length,
                                     copied, 10, &out) == valid);
        assert(out.slot == (valid ? 2U : 4U));
        ++cases;
    }
    for (unsigned i = 0; i < 304; ++i) {
        // New file generation is opaque and may differ in any bit.
        if (i >= 56 && i < 64)
            continue;
        memcpy(bad, child, 304);
        bad[i] ^= 128;
        out = (struct aether_fs_session_identity){4, 15, 3};
        assert(!aefd_fork_child_match(request, 304, observed, 9, bad, 304,
                                      copied, 10, &out));
        assert(out.slot == 4 && out.epoch == 15 && out.shell_generation == 3);
        ++cases;
    }
    // Structurally valid changes must still fail fork correspondence.
    for (unsigned which = 0; which < 3; ++which) {
        memcpy(bad, child, 304);
        if (which == 0)
            bad[126] ^= 1;
        if (which == 1)
            bad[125] = 4;
        if (which == 2) {
            bad[140] = AEFD_BIND_FILE;
            bad[141] = 4;
        }
        out = (struct aether_fs_session_identity){4, 15, 3};
        assert(!aefd_fork_child_match(request, 304, observed, 9, bad, 304,
                                      copied, 10, &out));
        assert(out.slot == 4 && out.epoch == 15 && out.shell_generation == 3);
        ++cases;
    }
    memcpy(bad, child, 304);
    aefd_put(bad + 48, 1, 17);
    assert(!aefd_fork_child_match(request, 304, observed, 9, bad, 304, copied,
                                  10, &out));
    ++cases;
    for (unsigned which = 0; which < 6; ++which) {
        struct aefd_startup_auxv wrong = copied;
        if (which == 0)
            wrong.memory = observed.memory;
        if (which == 1)
            wrong.input = observed.input;
        if (which == 2)
            wrong.input = observed.output;
        if (which == 3)
            wrong.output = observed.input;
        if (which == 4)
            wrong.output = observed.output;
        if (which == 5)
            wrong.input = wrong.output;
        assert(!aefd_fork_child_match(request, 304, observed, 9, child, 304,
                                      wrong, 10, &out));
        ++cases;
    }
    for (unsigned shell_generation = 1; shell_generation <= 3;
         ++shell_generation) {
        snapshot(parent);
        put32(parent, 36, shell_generation);
        put32(parent, 44, shell_generation);
        struct aefd_startup_auxv p = observed;
        p.memory = UINT64_C(0x40000002) | (uint64_t)shell_generation << 8;
        long pp = (long)(shell_generation * 7 + 2);
        assert(aefd_fork_encode(request, 304, parent, 304, p, pp, 7, 42));
        for (unsigned slot = 2; slot <= 4; ++slot) {
            for (unsigned epoch = 1; epoch <= 15; ++epoch) {
                memcpy(child, parent, 304);
                put32(child, 32, slot);
                put32(child, 36, epoch);
                put32(child, 40, (uint32_t)pp);
                aefd_put(child + 48, 1, 18);
                memset(child + 296, 0, 8);
                copied.memory =
                    UINT64_C(0x40000000) | (uint64_t)epoch << 8 | (slot + 1);
                assert(aefd_fork_child_match(
                    request, 304, p, pp, child, 304, copied,
                    (long)(epoch * 7 + slot + 1), &out));
                assert(out.slot == slot && out.epoch == epoch);
                ++cases;
            }
        }
    }
}
int main(void)
{
    frames();
    replies();
    child_frames();
    uint64_t counter = 0, next = 99;
    assert(aefd_fork_next(&counter, &next) && counter == 1 && next == 1);
    counter = UINT64_MAX - 1;
    assert(aefd_fork_next(&counter, &next) && counter == UINT64_MAX &&
           next == UINT64_MAX);
    next = 99;
    assert(!aefd_fork_next(&counter, &next) && counter == UINT64_MAX &&
           next == 99);
    assert(!aefd_fork_next(&counter, &counter) && counter == UINT64_MAX);
    assert(!aefd_fork_next(NULL, &next) && next == 99);
    ++cases;
    printf("%u fork-frame cases pass\n", cases);
    return 0;
}
