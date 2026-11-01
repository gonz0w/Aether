/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_BINDINGS_H
#define AETHER_FD_BINDINGS_H
#include "fd-protocol.h"

#define AEFD_BINDINGS_COUNT 16U
#define AEFD_BINDINGS_BYTES 128U
#define AEFD_BIND_EMPTY 0U
#define AEFD_BIND_CONSOLE 1U
#define AEFD_BIND_PIPE 2U
#define AEFD_BIND_FILE 3
#define AEFD_BIND_TERMINAL 4U

struct aefd_binding {
    unsigned char kind, selector, cloexec, reserved;
};
struct aefd_bindings {
    uint64_t generation;
    struct aefd_binding slots[AEFD_BINDINGS_COUNT];
};
static inline int aefd_binding_valid(struct aefd_binding slot)
{
    if (slot.reserved || slot.cloexec > 1)
        return 0;
    switch (slot.kind) {
    case AEFD_BIND_EMPTY:
        return !slot.selector && !slot.cloexec;
    case AEFD_BIND_CONSOLE:
#ifdef AEFD_TERMINAL_BINDINGS
    case AEFD_BIND_TERMINAL:
#endif
        return slot.selector <= 2;
    case AEFD_BIND_PIPE:
        return slot.selector >= 3 && slot.selector <= 6;
    case AEFD_BIND_FILE:
        return aefd_file_selector(slot.selector);
    default:
        return 0;
    }
}
/* Fresh proposed startup snapshot only. Labels are not native authority.
 * Full publication after validation; caller must stop on decode failure. */
static inline int aefd_bindings_decode(const unsigned char *raw, size_t length,
                                       uint64_t generation,
                                       struct aefd_bindings *out)
{
    if (!raw || !out || length != AEFD_BINDINGS_BYTES || !generation ||
        memcmp(raw, AEFD_MAP_MAGIC, 8) || aefd_word(raw, 1) != generation ||
        aefd_word(raw, 2) != AEFD_BINDINGS_COUNT)
        return 0;
    for (unsigned i = 3; i < 8; ++i)
        if (aefd_word(raw, i))
            return 0;
    struct aefd_bindings value = {.generation = generation};
    for (unsigned i = 0; i < AEFD_BINDINGS_COUNT; ++i) {
        const unsigned char *record = raw + 64U + i * 4U;
        struct aefd_binding slot = {record[0], record[1], record[2], record[3]};
        if (!aefd_binding_valid(slot))
            return 0;
        if (slot.kind == AEFD_BIND_FILE)
            for (unsigned j = 0; j < i; ++j)
                if (value.slots[j].kind == AEFD_BIND_FILE &&
                    value.slots[j].selector == slot.selector)
                    return 0;
#ifdef AEFD_TERMINAL_BINDINGS
        /* A source has one admitted type, including all of its aliases. */
        if (slot.kind == AEFD_BIND_CONSOLE || slot.kind == AEFD_BIND_TERMINAL)
            for (unsigned j = 0; j < i; ++j)
                if ((value.slots[j].kind == AEFD_BIND_CONSOLE ||
                     value.slots[j].kind == AEFD_BIND_TERMINAL) &&
                    value.slots[j].selector == slot.selector &&
                    value.slots[j].kind != slot.kind)
                    return 0;
#endif
        value.slots[i] = slot;
    }
    *out = value;
    return 1;
}
/* Pure selection: 1 present, 0 absent/out-of-range FD, -1 invalid/stale map.
 * Successful decode and immutable serialized access are caller preconditions.
 * Preserve kind before dispatch; a selector alone cannot select file vs pipe.
 * Output is untouched unless returning1. */
static inline int aefd_bindings_lookup(const struct aefd_bindings *map,
                                       uint64_t generation, int fd,
                                       struct aefd_binding *out)
{
    if (!map || !out || !generation || map->generation != generation)
        return -1;
    if (fd < 0 || fd >= 16)
        return 0;
    struct aefd_binding slot = map->slots[fd];
    if (!aefd_binding_valid(slot))
        return -1;
    if (slot.kind == AEFD_BIND_EMPTY)
        return 0;
    *out = slot;
    return 1;
}
#endif
