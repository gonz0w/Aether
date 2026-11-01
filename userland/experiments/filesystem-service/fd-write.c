/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-write.h"
int64_t aefd_routed_write(const struct aefd_bindings *map,
                          struct aefd_client *client,
                          const struct aefd_stream_writer *streams,
                          int logical_fd, const unsigned char *input,
                          size_t count)
{
    if ((count && !input) || count > AEFD_READ_MAX)
        return -22;
    if (!client || !client->live || !client->workspace)
        return -5;
    struct aefd_binding binding;
    int found =
        aefd_bindings_lookup(map, client->generation, logical_fd, &binding);
    if (found < 0) {
        aefd_client_abort(client);
        return -5;
    }
    if (!found)
        return -9;
    memset(client->workspace, 0, AEFD_READ_MAX);
    if (binding.kind == AEFD_BIND_FILE)
        return -30;
    if (!streams || !streams->write)
        return -38;
    if (count)
        memcpy(client->workspace, input, count);
#ifdef AEFD_TERMINAL_DUPLEX_BINDINGS
    if (binding.kind == AEFD_BIND_DUPLEX_TERMINAL) {
        binding.kind = AEFD_BIND_TERMINAL;
        binding.selector = 1;
    }
#endif
    struct aefd_stream_result reply =
        streams->write(streams->context, binding.kind, binding.selector,
                       client->workspace, count);
    if (reply.complete != 1 || reply.result < -INT64_C(2147483647) ||
        (reply.result >= 0 && (uint64_t)reply.result > count)) {
        aefd_client_abort(client);
        return -5;
    }
    memset(client->workspace, 0, AEFD_READ_MAX);
    return reply.result;
}
