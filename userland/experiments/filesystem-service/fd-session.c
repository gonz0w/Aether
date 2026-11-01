/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-session.h"
static int ready(struct aefd_session *s)
{
    if (!s || s->initialized != 1 || s->finished || !s->map || !s->client ||
        !s->client->live || !s->client->workspace)
        return 0;
    if (!s->map->generation || s->map->generation != s->client->generation) {
        aefd_client_abort(s->client);
        return 0;
    }
    return 1;
}
int64_t aefd_session_init(struct aefd_session *s, struct aefd_bindings *map,
                          struct aefd_client *client, const unsigned char *raw,
                          size_t length, uint64_t generation, struct aefd_io io,
                          unsigned char workspace[AEFD_READ_MAX],
                          struct aefd_adapters adapters)
{
    if (!s || !map || !client)
        return -22;
    if (s->initialized || client->generation || client->live ||
        client->workspace)
        return -16;
    struct aefd_bindings value;
    if (!aefd_bindings_decode(raw, length, generation, &value) ||
        !aefd_client_init(client, io, workspace, generation))
        return -22;
    *map = value;
    *s = (struct aefd_session){
        .map = map, .client = client, .adapters = adapters, .initialized = 1};
    return 0;
}
int64_t aefd_session_open(struct aefd_session *s, const unsigned char *name,
                          size_t count, int flag)
{
    return ready(s) ? aefd_table_open(s->map, s->client, name, count, flag)
                    : -5;
}
int64_t aefd_session_read(struct aefd_session *s, int fd, unsigned char *out,
                          size_t n)
{
    return ready(s) ? aefd_routed_read(s->map, s->client, &s->adapters.reader,
                                       fd, out, n)
                    : -5;
}
int64_t aefd_session_write(struct aefd_session *s, int fd,
                           const unsigned char *in, size_t n)
{
    return ready(s) ? aefd_routed_write(s->map, s->client, &s->adapters.writer,
                                        fd, in, n)
                    : -5;
}
int64_t aefd_session_dup(struct aefd_session *s, int fd, int minimum, int flag)
{
    return ready(s) ? aefd_mixed_dup(s->map, s->client, fd, minimum, flag) : -5;
}
int64_t aefd_session_replace(struct aefd_session *s, int from, int to)
{
#ifdef AEFD_DUP2_WIRE
    return ready(s)
               ? aefd_dup2(s->map, s->client, &s->adapters.closer, from, to)
               : -5;
#else
    return ready(s) ? aefd_stream_replace(s->map, s->client,
                                          &s->adapters.closer, from, to)
                    : -5;
#endif
}
int64_t aefd_session_pipe(struct aefd_session *s, int pair[2], int flag)
{
    return ready(s) ? aefd_table_pipe(s->map, s->client, &s->adapters.creator,
                                      pair, flag)
                    : -5;
}
int64_t aefd_session_close(struct aefd_session *s, int fd)
{
    return ready(s)
               ? aefd_mixed_close(s->map, s->client, &s->adapters.closer, fd)
               : -5;
}
int64_t aefd_session_binding(struct aefd_session *s, int fd,
                             struct aefd_binding *out)
{
    if (!out)
        return -22;
    if (!ready(s))
        return -5;
    struct aefd_binding value;
    int found = aefd_bindings_lookup(s->map, s->client->generation, fd, &value);
    if (found < 0) {
        aefd_client_abort(s->client);
        return -5;
    }
    if (!found)
        return -9;
    *out = value;
    return 0;
}
int64_t aefd_session_flags(struct aefd_session *s, int fd)
{
    if (!ready(s))
        return -5;
    struct aefd_binding value;
    int found = aefd_bindings_lookup(s->map, s->client->generation, fd, &value);
    if (found < 0) {
        aefd_client_abort(s->client);
        return -5;
    }
    return found ? value.cloexec : -9;
}
int64_t aefd_session_set_flags(struct aefd_session *s, int fd, int flag)
{
    return ready(s) ? aefd_mixed_set_cloexec(s->map, s->client, fd, flag) : -5;
}
int64_t aefd_session_seek(struct aefd_session *s, int fd, int64_t delta,
                          int whence)
{
    if (!ready(s))
        return -5;
    if (whence < 0 || whence > 2)
        return -22;
    struct aefd_binding value;
    int found = aefd_bindings_lookup(s->map, s->client->generation, fd, &value);
    if (found < 0) {
        aefd_client_abort(s->client);
        return -5;
    }
    if (!found)
        return -9;
    return value.kind == AEFD_BIND_FILE
               ? aefd_table_seek(s->map, s->client, fd, delta, whence)
               : -29;
}
int64_t aefd_session_snapshot(struct aefd_session *s, unsigned char *out,
                              size_t length, int omit_cloexec)
{
    if (!out || length != AEFD_BINDINGS_BYTES || omit_cloexec < 0 ||
        omit_cloexec > 1)
        return -22;
    if (!ready(s))
        return -5;
    unsigned char raw[AEFD_BINDINGS_BYTES] = {0};
    memcpy(raw, AEFD_MAP_MAGIC, 8);
    aefd_put(raw, 1, s->map->generation);
    aefd_put(raw, 2, AEFD_BINDINGS_COUNT);
    for (unsigned fd = 0; fd < AEFD_BINDINGS_COUNT; ++fd)
        memcpy(raw + 64 + fd * 4, &s->map->slots[fd], 4);
    struct aefd_bindings checked;
    if (!aefd_bindings_decode(raw, sizeof raw, s->client->generation,
                              &checked)) {
        aefd_client_abort(s->client);
        return -5;
    }
    if (omit_cloexec)
        for (unsigned fd = 0; fd < AEFD_BINDINGS_COUNT; ++fd)
            if (checked.slots[fd].cloexec)
                memset(raw + 64 + fd * 4, 0, 4);
    memcpy(out, raw, sizeof raw);
    return 0;
}
struct aefd_finish aefd_session_finish(struct aefd_session *s)
{
    if (!s || s->initialized != 1 || !s->map || !s->client)
        return (struct aefd_finish){.first_error = -5, .unknown = 1};
    if (s->finished)
        return s->receipt;
    struct aefd_finish result = {0};
    if (!ready(s)) {
        result.unknown = 1;
        result.first_error = -5;
    }
    for (int fd = 0; fd < 16; ++fd) {
        if (result.unknown)
            break;
        if (!s->map->slots[fd].kind)
            continue;
        if (!ready(s)) {
            result.unknown = 1;
            break;
        }
        ++result.attempted;
        int64_t status = aefd_session_close(s, fd);
        if (!s->map->slots[fd].kind)
            ++result.removed;
        if (status < 0 && !result.first_error)
            result.first_error = status;
        if (!s->client->live) {
            result.unknown = 1;
            break;
        }
    }
    for (unsigned fd = 0; fd < AEFD_BINDINGS_COUNT; ++fd)
        if (s->map->slots[fd].kind)
            ++result.remaining;
    aefd_client_abort(s->client);
    result.transport = s->client->closed;
    s->receipt = result;
    s->finished = 1;
    return result;
}

struct aefd_redirect_result aefd_session_redirect(struct aefd_session *s,
                                                  int from, int to)
{
    if (!ready(s))
        return (struct aefd_redirect_result){
            .status = -5, .prepared_selector = -1, .unknown = 1};
    return aefd_redirect(s->map, s->client, &s->adapters.closer, from, to);
}
