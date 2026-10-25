/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-table.h"

static int ready(const struct aefd_bindings *map, struct aefd_client *client)
{
    if (!client || !client->live || !client->workspace)
        return 0;
    if (!map || !map->generation || map->generation != client->generation) {
        aefd_client_abort(client);
        return 0;
    }
    return 1;
}
static int free_slot(const struct aefd_bindings *map, int minimum)
{
    for (int fd = minimum; fd < 16; ++fd)
        if (map->slots[fd].kind == AEFD_BIND_EMPTY)
            return fd;
    return -1;
}
static int64_t binding_slot(const struct aefd_bindings *map,
                            struct aefd_client *client, int fd,
                            struct aefd_binding *binding)
{
    int found = aefd_bindings_lookup(map, client->generation, fd, binding);
    if (found < 0) {
        aefd_client_abort(client);
        return -5;
    }
    if (!found)
        return -9;
    return 0;
}
static int64_t file_slot(const struct aefd_bindings *map,
                         struct aefd_client *client, int fd,
                         struct aefd_binding *binding)
{
    int64_t error = binding_slot(map, client, fd, binding);
    if (error)
        return error;
    return binding->kind == AEFD_BIND_FILE ? 0 : -38;
}
static int64_t install(struct aefd_bindings *map, struct aefd_client *client,
                       int logical, int64_t selector, int cloexec)
{
    if (selector < 0)
        return selector;
    if (!aefd_file_selector((uint64_t)selector))
        goto invalid;
    for (unsigned i = 0; i < AEFD_BINDINGS_COUNT; ++i)
        if (map->slots[i].kind == AEFD_BIND_FILE &&
            map->slots[i].selector == selector)
            goto invalid;
    map->slots[logical] = (struct aefd_binding){
        AEFD_BIND_FILE, (unsigned char)selector, (unsigned char)cloexec, 0};
    return logical;
invalid:
    /* A conflicting selector may already be owned; never close it as rollback.
     */
    aefd_client_abort(client);
    return -5;
}
int64_t aefd_table_open(struct aefd_bindings *map, struct aefd_client *client,
                        const unsigned char *name, size_t length, int cloexec)
{
    if (cloexec < 0 || cloexec > 1)
        return -22;
    if (!ready(map, client))
        return -5;
    int logical = free_slot(map, 0);
    if (logical < 0)
        return -24;
    int64_t selector = aefd_file_open(client, name, length, cloexec);
    return install(map, client, logical, selector, cloexec);
}
int64_t aefd_table_dup(struct aefd_bindings *map, struct aefd_client *client,
                       int fd, int minimum, int cloexec)
{
    if (minimum < 0 || minimum >= 16 || cloexec < 0 || cloexec > 1)
        return -22;
    if (!ready(map, client))
        return -5;
    struct aefd_binding binding;
    int64_t error = file_slot(map, client, fd, &binding);
    if (error)
        return error;
    int logical = free_slot(map, minimum);
    if (logical < 0)
        return -24;
    int64_t selector =
        aefd_file_dup(client, binding.selector, AEFD_FIRST_FILE, cloexec);
    return install(map, client, logical, selector, cloexec);
}
int64_t aefd_table_seek(struct aefd_bindings *map, struct aefd_client *client,
                        int fd, int64_t delta, int whence)
{
    if (whence < 0 || whence > 2)
        return -22;
    if (!ready(map, client))
        return -5;
    struct aefd_binding binding;
    int64_t error = file_slot(map, client, fd, &binding);
    if (error)
        return error;
    return aefd_file_seek(client, binding.selector, delta, whence);
}
int64_t aefd_table_close(struct aefd_bindings *map, struct aefd_client *client,
                         int fd)
{
    if (!ready(map, client))
        return -5;
    struct aefd_binding binding;
    int64_t error = file_slot(map, client, fd, &binding);
    if (error)
        return error;
    int64_t result = aefd_file_close(client, binding.selector);
    if (result == 0)
        map->slots[fd] = (struct aefd_binding){0};
    return result;
}
int64_t aefd_table_set_cloexec(struct aefd_bindings *map,
                               struct aefd_client *client, int fd, int cloexec)
{
    if (cloexec < 0 || cloexec > 1)
        return -22;
    if (!ready(map, client))
        return -5;
    struct aefd_binding binding;
    int64_t error = file_slot(map, client, fd, &binding);
    if (error)
        return error;
    int64_t result = aefd_file_set_cloexec(client, binding.selector, cloexec);
    if (result == 0)
        map->slots[fd].cloexec = (unsigned char)cloexec;
    return result;
}

int64_t aefd_mixed_dup(struct aefd_bindings *map, struct aefd_client *client,
                       int fd, int minimum, int cloexec)
{
    if (minimum < 0 || minimum >= 16 || cloexec < 0 || cloexec > 1)
        return -22;
    if (!ready(map, client))
        return -5;
    struct aefd_binding binding;
    int64_t error = binding_slot(map, client, fd, &binding);
    if (error)
        return error;
    if (binding.kind == AEFD_BIND_FILE)
        return aefd_table_dup(map, client, fd, minimum, cloexec);
    int target = free_slot(map, minimum);
    if (target < 0)
        return -24;
    binding.cloexec = (unsigned char)cloexec;
    map->slots[target] = binding;
    return target;
}
int64_t aefd_mixed_set_cloexec(struct aefd_bindings *map,
                               struct aefd_client *client, int fd, int cloexec)
{
    if (cloexec < 0 || cloexec > 1)
        return -22;
    if (!ready(map, client))
        return -5;
    struct aefd_binding binding;
    int64_t error = binding_slot(map, client, fd, &binding);
    if (error)
        return error;
    if (binding.kind == AEFD_BIND_FILE)
        return aefd_table_set_cloexec(map, client, fd, cloexec);
    map->slots[fd].cloexec = (unsigned char)cloexec;
    return 0;
}
int64_t aefd_mixed_close(struct aefd_bindings *map, struct aefd_client *client,
                         const struct aefd_stream_closer *streams, int fd)
{
    if (!ready(map, client))
        return -5;
    struct aefd_binding binding;
    int64_t error = binding_slot(map, client, fd, &binding);
    if (error)
        return error;
    if (binding.kind == AEFD_BIND_FILE)
        return aefd_table_close(map, client, fd);
    for (int other = 0; other < 16; ++other)
        if (other != fd && map->slots[other].kind == binding.kind &&
            map->slots[other].selector == binding.selector) {
            map->slots[fd] = (struct aefd_binding){0};
            return 0;
        }
    if (!streams || !streams->close)
        return -38;
    struct aefd_stream_close_result result =
        streams->close(streams->context, binding.kind, binding.selector);
    if (result.complete != 1 ||
        (result.consumed != 0 && result.consumed != 1) || result.status > 0 ||
        result.status < -INT64_C(2147483647) ||
        (!result.consumed && result.status == 0)) {
        aefd_client_abort(client);
        return -5;
    }
    if (result.consumed)
        map->slots[fd] = (struct aefd_binding){0};
    return result.status;
}
