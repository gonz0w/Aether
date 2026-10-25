/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-home-probe-adapter.h"
static int64_t begin(struct aefd_context *c)
{
    if (!c || c->state != 1)
        return -5;
    if (c->native.active || c->native.busy)
        return -16;
    int64_t result = aefd_native_enter(&c->native);
    if (result) {
        if (result != -16)
            aefd_client_abort(&c->client);
        return result;
    }
    if (c->session.initialized != 1 || c->session.finished ||
        c->session.map != &c->map || c->session.client != &c->client ||
        !c->client.live || c->client.workspace != c->workspace ||
        !c->map.generation || c->map.generation != c->client.generation) {
        aefd_client_abort(&c->client);
        aefd_native_leave(&c->native);
        return -5;
    }
    return 0;
}
static int64_t end(struct aefd_context *c, int64_t result)
{
    aefd_native_leave(&c->native);
    return result;
}
int64_t aefd_home_probe_open(struct aefd_context *c, const unsigned char *name,
                             size_t length, int access, int cloexec)
{
    if (cloexec < 0 || cloexec > 1 || access < 0 || access > 2)
        return -22;
    int64_t result = begin(c);
    if (result)
        return result;
    int logical = 0;
    while (logical < 16 && c->map.slots[logical].kind != AEFD_BIND_EMPTY)
        ++logical;
    if (logical == 16)
        return end(c, -24);
    int64_t selector =
        aefd_file_open_home(&c->client, name, length, access, cloexec);
    if (selector < 0)
        return end(c, selector);
    int valid = aefd_file_selector((uint64_t)selector);
    for (unsigned i = 0; i < 16; ++i)
        if (c->map.slots[i].kind == AEFD_BIND_FILE &&
            c->map.slots[i].selector == selector)
            valid = 0;
    if (!valid) {
        /* It may alias an existing owned selector; never close as rollback. */
        aefd_client_abort(&c->client);
        return end(c, -5);
    }
    c->map.slots[logical] = (struct aefd_binding){
        AEFD_BIND_FILE, (unsigned char)selector, (unsigned char)cloexec, 0};
    return end(c, logical);
}
int64_t aefd_home_probe_write(struct aefd_context *c, int logical,
                              const unsigned char *bytes, size_t length,
                              struct aefd_write_result *out)
{
    if (!out)
        return -22;
    *out = (struct aefd_write_result){.observation = AEFD_WRITE_NOT_SENT,
                                      .status = -22,
                                      .fd = logical,
                                      .requested = length};
    if (c) {
        out->generation = c->client.generation;
        out->sequence = c->client.sequence;
    }
    int64_t result = begin(c);
    if (result) {
        out->status = result;
        if (c && c->client.generation && !c->client.live) {
            out->file_closed = 1;
            out->file_cleanup = c->client.closed;
        }
        return result;
    }
    struct aefd_binding binding;
    int found =
        aefd_bindings_lookup(&c->map, c->client.generation, logical, &binding);
    if (found < 0) {
        aefd_client_abort(&c->client);
        out->status = -5;
        out->file_closed = 1;
        out->file_cleanup = c->client.closed;
    } else if (!found || binding.kind != AEFD_BIND_FILE) {
        out->status = -9;
    } else {
        result =
            aefd_file_write(&c->client, binding.selector, bytes, length, out);
        return end(c, result);
    }
    return end(c, out->status);
}
