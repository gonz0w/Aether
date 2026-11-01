/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-routing.h"

static int64_t retired(struct aefd_client *client)
{
    aefd_client_abort(client);
    return -5;
}
int64_t aefd_routed_read(const struct aefd_bindings *map,
                         struct aefd_client *client,
                         const struct aefd_stream_reader *streams,
                         int logical_fd, unsigned char *out, size_t count)
{
    if ((count && !out) || count > AEFD_READ_MAX)
        return -22;
    if (!client || !client->live || !client->workspace)
        return -5;
    struct aefd_binding binding;
    int found =
        aefd_bindings_lookup(map, client->generation, logical_fd, &binding);
    if (found < 0)
        return retired(client);
    if (!found)
        return -9;
    if (binding.kind == AEFD_BIND_FILE) {
        int64_t result = aefd_file_read(client, binding.selector, out, count);
        if (client->workspace)
            memset(client->workspace, 0, AEFD_READ_MAX);
        return result;
    }
    memset(client->workspace, 0, AEFD_READ_MAX);
    if (!streams || !streams->read)
        return -38;
#ifdef AEFD_TERMINAL_DUPLEX_BINDINGS
    if (binding.kind == AEFD_BIND_DUPLEX_TERMINAL) {
        binding.kind = AEFD_BIND_TERMINAL;
        binding.selector = 0;
    }
#endif
    struct aefd_stream_result reply =
        streams->read(streams->context, binding.kind, binding.selector,
                      client->workspace, count);
    if (reply.complete != 1 || reply.result < -INT64_C(2147483647) ||
        (reply.result >= 0 && (uint64_t)reply.result > count))
        return retired(client);
    if (reply.result > 0)
        memcpy(out, client->workspace, (size_t)reply.result);
    memset(client->workspace, 0, AEFD_READ_MAX);
    return reply.result;
}
