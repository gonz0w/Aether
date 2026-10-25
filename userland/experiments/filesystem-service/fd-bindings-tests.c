/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-bindings.h"
#include <assert.h>
#include <stdio.h>
static unsigned char snapshot[AEFD_BINDINGS_BYTES];
static unsigned cases;
static void seed(void)
{
    memset(snapshot, 0, sizeof snapshot);
    memcpy(snapshot, "AEFDT001", 8);
    aefd_put(snapshot, 1, 77);
    aefd_put(snapshot, 2, 16);
    for (unsigned i = 0; i < 3; ++i) {
        snapshot[64 + i * 4] = AEFD_BIND_CONSOLE;
        snapshot[65 + i * 4] = (unsigned char)i;
    }
    snapshot[64 + 3 * 4] = AEFD_BIND_PIPE;
    snapshot[65 + 3 * 4] = 3;
    snapshot[64 + 4 * 4] = AEFD_BIND_PIPE;
    snapshot[65 + 4 * 4] = 4;
    snapshot[64 + 5 * 4] = AEFD_BIND_FILE;
    snapshot[65 + 5 * 4] = 3;
    snapshot[66 + 5 * 4] = 1;
    snapshot[64 + 6 * 4] = AEFD_BIND_CONSOLE;
    snapshot[65 + 6 * 4] = 1;
}
static void denied(size_t length, uint64_t generation)
{
    struct aefd_bindings map, prior;
    memset(&map, 0xa5, sizeof map);
    memcpy(&prior, &map, sizeof map);
    assert(!aefd_bindings_decode(snapshot, length, generation, &map));
    assert(!memcmp(&map, &prior, sizeof map));
    ++cases;
}
int main(void)
{
    seed();
    struct aefd_bindings map;
    assert(aefd_bindings_decode(snapshot, sizeof snapshot, 77, &map));
    struct aefd_binding pipe, file, console;
    assert(aefd_bindings_lookup(&map, 77, 3, &pipe) == 1);
    assert(aefd_bindings_lookup(&map, 77, 5, &file) == 1);
    assert(pipe.kind == AEFD_BIND_PIPE && file.kind == AEFD_BIND_FILE);
    assert(pipe.selector == file.selector && pipe.selector == 3);
    assert(file.cloexec == 1 && pipe.cloexec == 0);
    assert(aefd_bindings_lookup(&map, 77, 6, &console) == 1);
    assert(console.kind == AEFD_BIND_CONSOLE && console.selector == 1);
    ++cases;
    struct aefd_binding output = {0xa5, 0xa5, 0xa5, 0xa5};
    assert(aefd_bindings_lookup(&map, 78, 5, &output) == -1);
    assert(aefd_bindings_lookup(&map, 0, 5, &output) == -1);
    assert(aefd_bindings_lookup(NULL, 77, 5, &output) == -1);
    assert(aefd_bindings_lookup(&map, 77, 5, NULL) == -1);
    assert(aefd_bindings_lookup(&map, 77, -1, &output) == 0);
    assert(aefd_bindings_lookup(&map, 77, 16, &output) == 0);
    assert(aefd_bindings_lookup(&map, 77, 15, &output) == 0);
    assert(output.kind == 0xa5 && output.selector == 0xa5 &&
           output.cloexec == 0xa5 && output.reserved == 0xa5);
    ++cases;
    map.slots[5].reserved = 1;
    assert(aefd_bindings_lookup(&map, 77, 5, &output) == -1);
    ++cases;
    for (size_t length = 0; length < sizeof snapshot; ++length)
        denied(length, 77);
    denied(129, 77);
    denied(sizeof snapshot, 0);
    denied(sizeof snapshot, 78);
    for (unsigned word = 3; word < 8; ++word) {
        seed();
        aefd_put(snapshot, word, 1);
        denied(sizeof snapshot, 77);
    }
    seed();
    snapshot[0] ^= 1;
    denied(sizeof snapshot, 77);
    seed();
    aefd_put(snapshot, 2, 15);
    denied(sizeof snapshot, 77);
    seed();
    snapshot[64 + 7 * 4] = AEFD_BIND_FILE;
    snapshot[65 + 7 * 4] = 3;
    denied(sizeof snapshot, 77);
    for (unsigned kind = 0; kind < 256; ++kind)
        for (unsigned selector = 0; selector < 256; ++selector) {
            seed();
            snapshot[64 + 7 * 4] = (unsigned char)kind;
            snapshot[65 + 7 * 4] = (unsigned char)selector;
            int expected = (kind == 0 && selector == 0) ||
                           (kind == 1 && selector <= 2) ||
                           (kind == 2 && selector >= 3 && selector <= 6) ||
                           (kind == 3 && selector >= 4 && selector <= 15);
            assert(aefd_bindings_decode(snapshot, sizeof snapshot, 77, &map) ==
                   expected);
            ++cases;
        }
    seed();
    snapshot[66 + 7 * 4] = 1;
    denied(sizeof snapshot, 77);
    for (unsigned flag = 2; flag < 256; ++flag) {
        seed();
        snapshot[66 + 5 * 4] = (unsigned char)flag;
        denied(sizeof snapshot, 77);
    }
    for (unsigned record = 0; record < 16; ++record) {
        seed();
        snapshot[67 + record * 4] = 1;
        denied(sizeof snapshot, 77);
    }
    /* Old installed-table32/64 bytes and old greeting cannot be interpreted. */
    seed();
    memcpy(snapshot, "AEFSH001", 8);
    denied(sizeof snapshot, 77);
    seed();
    memset(snapshot, 0, sizeof snapshot);
    denied(sizeof snapshot, 77);
    printf("%u tagged binding cases pass\n", cases);
    return 0;
}
