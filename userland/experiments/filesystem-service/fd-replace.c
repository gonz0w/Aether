/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-replace.h"
int64_t aefd_stream_replace(struct aefd_bindings *map,
                            struct aefd_client *client,
                            const struct aefd_stream_closer *closer, int source,
                            int target)
{
    if (!client || !client->live || !client->workspace)
        return -5;
    struct aefd_binding value, previous;
    int from = aefd_bindings_lookup(map, client->generation, source, &value);
    int to = aefd_bindings_lookup(map, client->generation, target, &previous);
    if (from < 0 || to < 0) {
        aefd_client_abort(client);
        return -5;
    }
    if (!from || target < 0 || target >= 16)
        return -9;
    if (value.kind == AEFD_BIND_FILE || (to && previous.kind == AEFD_BIND_FILE))
        return -38;
    if (source == target)
        return target;
    if (to) {
        int64_t result = aefd_mixed_close(map, client, closer, target);
        if (result < 0)
            return result;
    }
    value.cloexec = 0;
    map->slots[target] = value;
    return target;
}

#ifdef AEFD_DUP2_WIRE
static int64_t invalid(struct aefd_client *client)
{
    aefd_client_abort(client);
    return -5;
}
int64_t aefd_dup2(struct aefd_bindings *map, struct aefd_client *client,
                  const struct aefd_stream_closer *closer, int source,
                  int target)
{
    if (!client || !client->live || !client->workspace)
        return -5;
    if (!map || !map->generation || map->generation != client->generation)
        return invalid(client);
    for (unsigned i = 0; i < AEFD_BINDINGS_COUNT; ++i) {
        if (!aefd_binding_valid(map->slots[i]))
            return invalid(client);
        if (map->slots[i].kind == AEFD_BIND_FILE)
            for (unsigned j = 0; j < i; ++j)
                if (map->slots[j].kind == AEFD_BIND_FILE &&
                    map->slots[j].selector == map->slots[i].selector)
                    return invalid(client);
    }
    if (source < 0 || source >= 16 || target < 0 || target >= 16 ||
        map->slots[source].kind == AEFD_BIND_EMPTY)
        return -9;
    if (source == target)
        return target;
    struct aefd_binding value = map->slots[source];
    struct aefd_binding previous = map->slots[target];
    value.cloexec = 0;
    int prepared = -1;
    if (value.kind == AEFD_BIND_FILE) {
        if (previous.kind == AEFD_BIND_FILE) {
            int64_t result =
                aefd_file_replace(client, value.selector, previous.selector);
            if (result < 0)
                return result;
            value.selector = previous.selector;
            map->slots[target] = value;
            return target;
        }
        int64_t result = aefd_file_dup(client, value.selector, 0, 0);
        if (result < 0)
            return result;
        for (unsigned i = 0; i < AEFD_BINDINGS_COUNT; ++i)
            if (map->slots[i].kind == AEFD_BIND_FILE &&
                map->slots[i].selector == result)
                return invalid(client);
        prepared = (int)result;
        value.selector = (unsigned char)result;
    }
    if (previous.kind != AEFD_BIND_EMPTY) {
        int64_t result = aefd_mixed_close(map, client, closer, target);
        if (!client->live)
            return -5;
        if (result < 0 && map->slots[target].kind != AEFD_BIND_EMPTY) {
            /* Confirmed no victim consumption. Only the known prepared alias
             * may be closed; unknown cleanup cannot publish or resume. */
            if (prepared >= 0 && aefd_file_close(client, prepared) != 0)
                return invalid(client);
            return result;
        }
        /* A known consumed close error does not prevent dup2 replacement. */
    }
    map->slots[target] = value;
    return target;
}
#endif
