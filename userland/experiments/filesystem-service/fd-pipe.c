/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-pipe.h"
int64_t aefd_table_pipe(struct aefd_bindings *map, struct aefd_client *client,
                        const struct aefd_pipe_creator *source, int pair[2],
                        int cloexec)
{
    if (!pair || cloexec < 0 || cloexec > 1)
        return -22;
    if (!client || !client->live || !client->workspace)
        return -5;
    if (!map || !map->generation || map->generation != client->generation) {
        aefd_client_abort(client);
        return -5;
    }
    int slots[2] = {-1, -1};
    unsigned count = 0;
    for (int fd = 0; fd < 16 && count < 2; ++fd)
        if (map->slots[fd].kind == AEFD_BIND_EMPTY)
            slots[count++] = fd;
    if (count != 2)
        return -24;
    if (!source || !source->create)
        return -38;
    struct aefd_pipe_result result = source->create(source->context);
    if (result.complete != 1 || result.status > 0 ||
        result.status < -INT64_C(2147483647))
        goto invalid;
    if (result.status < 0) {
        if (result.read_selector || result.write_selector)
            goto invalid;
        return result.status;
    }
    if (!((result.read_selector == 3 && result.write_selector == 4) ||
          (result.read_selector == 5 && result.write_selector == 6)))
        goto invalid;
    for (unsigned fd = 0; fd < AEFD_BINDINGS_COUNT; ++fd)
        if (map->slots[fd].kind == AEFD_BIND_PIPE &&
            (map->slots[fd].selector == result.read_selector ||
             map->slots[fd].selector == result.write_selector))
            goto invalid;
    map->slots[slots[0]] = (struct aefd_binding){
        AEFD_BIND_PIPE, (unsigned char)result.read_selector,
        (unsigned char)cloexec, 0};
    map->slots[slots[1]] = (struct aefd_binding){
        AEFD_BIND_PIPE, (unsigned char)result.write_selector,
        (unsigned char)cloexec, 0};
    pair[0] = slots[0];
    pair[1] = slots[1];
    return 0;
invalid:
    /* Purported selectors may name an occupied resource; no unsafe rollback. */
    aefd_client_abort(client);
    return -5;
}
