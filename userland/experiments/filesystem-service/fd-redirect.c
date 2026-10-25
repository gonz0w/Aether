/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-redirect.h"
struct aefd_redirect_result
aefd_redirect(struct aefd_bindings *map, struct aefd_client *client,
              const struct aefd_stream_closer *closer, int source, int target)
{
    struct aefd_redirect_result r = {.status = -5, .prepared_selector = -1};
    if (!client || !client->live || !client->workspace) {
        r.unknown = 1;
        return r;
    }
    struct aefd_binding value, previous;
    int from = aefd_bindings_lookup(map, client->generation, source, &value);
    int to = aefd_bindings_lookup(map, client->generation, target, &previous);
    if (from < 0 || to < 0) {
        aefd_client_abort(client);
        r.unknown = 1;
        return r;
    }
    if (!from || target < 0 || target >= 16) {
        r.status = -9;
        return r;
    }
    if (source == target) {
        r.status = target;
        r.committed = 1;
        return r;
    }
    if (value.kind == AEFD_BIND_FILE) {
        int64_t prepared = aefd_file_dup(client, value.selector, 3, 0);
        if (prepared < 0) {
            r.status = prepared;
            r.unknown = !client->live;
            r.unresolved = r.unknown;
            return r;
        }
        r.unresolved = 1;
        if (prepared < 3 || prepared >= 16)
            goto invalid;
        r.prepared_selector = (int)prepared;
        for (unsigned fd = 0; fd < AEFD_BINDINGS_COUNT; ++fd)
            if (map->slots[fd].kind == AEFD_BIND_FILE &&
                map->slots[fd].selector == prepared)
                goto invalid;
        value.selector = (unsigned char)prepared;
    }
    if (to) {
        r.target_attempted = 1;
        r.target_status = aefd_mixed_close(map, client, closer, target);
        r.target_removed = map->slots[target].kind == AEFD_BIND_EMPTY;
        if (r.target_status < 0) {
            r.status = r.target_status;
            if (!client->live) {
                r.unknown = 1;
                return r;
            }
            if (r.prepared_selector >= 0) {
                r.cleanup_attempted = 1;
                r.cleanup_status = aefd_file_close(client, r.prepared_selector);
                if (r.cleanup_status != 0) {
                    r.status = -5;
                    goto invalid;
                }
                r.unresolved = 0;
            }
            return r;
        }
    }
    value.cloexec = 0;
    map->slots[target] = value;
    r.unresolved = 0;
    r.committed = 1;
    r.status = target;
    return r;
invalid:
    /* A purported duplicate may be an existing FD; never close a collision. */
    aefd_client_abort(client);
    r.status = -5;
    r.unknown = 1;
    return r;
}
