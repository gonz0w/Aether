/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-context.h"
#ifdef AEFD_CWD_WIRE
#include <errno.h>
#endif

int64_t aefd_context_init(struct aefd_context *c, aefd_native_call call,
                          void *owner, uint64_t input, uint64_t output,
                          const unsigned char *raw, size_t length,
                          uint64_t generation,
                          const struct aefd_native_source sources[7],
                          const unsigned generations[2], uint32_t factory)
{
    if (!c)
        return -22;
    if (c->state || c->native.initialized || c->session.initialized ||
        c->client.generation || c->client.live || c->client.workspace)
        return -16;
    struct aefd_bindings map;
    struct aefd_native native = {0};
    if (!aefd_bindings_decode(raw, length, generation, &map) ||
        !aefd_native_init(&native, call, owner, input, output, sources,
                          generations, factory))
        return -22;
#ifdef AEFD_TERMINAL_DUPLEX_BINDINGS
    /*004 attests this fixed owner-held relationship, never initial kind5. */
    for (unsigned i = 0; i < 3; ++i)
        if (map.slots[i].kind != AEFD_BIND_TERMINAL ||
            map.slots[i].selector != i ||
            sources[i].reference != (UINT32_C(0x7a000001) | i << 16))
            return -22;
    for (unsigned fd = 0; fd < 16; ++fd)
        if (map.slots[fd].kind != AEFD_BIND_EMPTY &&
            map.slots[fd].kind != AEFD_BIND_TERMINAL)
            return -22;
#endif
    unsigned seen = 0;
    for (unsigned fd = 0; fd < AEFD_BINDINGS_COUNT; ++fd) {
        struct aefd_binding slot = map.slots[fd];
        if (slot.kind == AEFD_BIND_CONSOLE || slot.kind == AEFD_BIND_PIPE
#ifdef AEFD_TERMINAL_BINDINGS
            || slot.kind == AEFD_BIND_TERMINAL
#endif
        ) {
            seen |= 1U << slot.selector;
        }
    }
    for (unsigned i = 0; i < 7; ++i)
        if (!!(seen & (1U << i)) != !!native.sources[i].reference)
            return -22;
    c->native = native;
    int64_t result =
        aefd_session_init(&c->session, &c->map, &c->client, raw, length,
                          generation, aefd_native_io(&c->native), c->workspace,
                          aefd_native_adapters(&c->native));
    if (result) {
        /* Unreachable with the validated exclusive fresh-storage contract;
         * fail terminally if caller violated it rather than reuse a channel. */
        struct aefd_io io = aefd_native_io(&c->native);
        (void)io.close(io.context);
        c->state = 2;
        return -5;
    }
    c->state = 1;
    return 0;
}
static int64_t begin(struct aefd_context *c)
{
    if (!c || c->state != 1)
        return -5;
    if (c->native.active || c->native.busy)
        return -16;
    int64_t result = aefd_native_enter(&c->native);
    if (result && result != -16)
        aefd_client_abort(&c->client);
    return result;
}
static int64_t end(struct aefd_context *c, int64_t result)
{
    aefd_native_leave(&c->native);
    return result;
}
#ifdef AEFD_TERMINAL_DUPLEX_BINDINGS
static int duplex_sources(const struct aefd_context *c)
{
    for (unsigned i = 0; i < 2; ++i) {
        const struct aefd_native_source *s = &c->native.sources[i];
        if (s->reference != (UINT32_C(0x7a000001) | i << 16) ||
            s->selector != i || s->rights != (i ? 2U : 1U) || s->bound != 16)
            return 0;
    }
    return 1;
}
int64_t aefd_context_open_duplex(struct aefd_context *c, int cloexec)
{
    if (cloexec < 0 || cloexec > 1)
        return -22;
    int64_t result = begin(c);
    if (result)
        return result;
    return end(c, duplex_sources(c)
                      ? aefd_session_open_duplex(&c->session, cloexec)
                      : -6);
}
#endif
int64_t aefd_context_open(struct aefd_context *c, const unsigned char *name,
                          size_t length, int flag)
{
    int64_t result = begin(c);
    if (result)
        return result;
    return end(c, aefd_session_open(&c->session, name, length, flag));
}
int64_t aefd_context_read(struct aefd_context *c, int fd, unsigned char *out,
                          size_t length)
{
    int64_t result = begin(c);
    if (result)
        return result;
    return end(c, aefd_session_read(&c->session, fd, out, length));
}
int64_t aefd_context_write(struct aefd_context *c, int fd,
                           const unsigned char *in, size_t length)
{
    int64_t result = begin(c);
    if (result)
        return result;
    return end(c, aefd_session_write(&c->session, fd, in, length));
}
int64_t aefd_context_dup(struct aefd_context *c, int fd, int minimum, int flag)
{
    int64_t result = begin(c);
    if (result)
        return result;
    return end(c, aefd_session_dup(&c->session, fd, minimum, flag));
}
int64_t aefd_context_replace(struct aefd_context *c, int from, int to)
{
    int64_t result = begin(c);
    if (result)
        return result;
    return end(c, aefd_session_replace(&c->session, from, to));
}
int64_t aefd_context_pipe(struct aefd_context *c, int pair[2], int flag)
{
    int64_t result = begin(c);
    if (result)
        return result;
    return end(c, aefd_session_pipe(&c->session, pair, flag));
}
int64_t aefd_context_close(struct aefd_context *c, int fd)
{
    int64_t result = begin(c);
    if (result)
        return result;
#ifdef AEFD_TERMINAL_DUPLEX_BINDINGS
    struct aefd_binding binding;
    result = aefd_session_binding(&c->session, fd, &binding);
    if (result)
        return end(c, result);
    if (binding.kind == AEFD_BIND_DUPLEX_TERMINAL && !duplex_sources(c)) {
        aefd_client_abort(&c->client);
        return end(c, -5);
    }
    /* Validate every component before the first possible physical close. */
    for (unsigned source = 0; source < 7; ++source)
        if (aefd_binding_depends(binding, source) &&
            (!c->native.sources[source].reference ||
             c->native.sources[source].selector != source)) {
            aefd_client_abort(&c->client);
            return end(c, -5);
        }
#endif
    return end(c, aefd_session_close(&c->session, fd));
}
int64_t aefd_context_describe(struct aefd_context *c, int fd,
                              struct aefd_binding *out, unsigned *rights)
{
    if (!out || !rights)
        return -22;
    int64_t result = begin(c);
    if (result)
        return result;
    struct aefd_binding binding;
    unsigned actual = 1; /* This profile's file table is read-only. */
    result = aefd_session_binding(&c->session, fd, &binding);
#ifdef AEFD_TERMINAL_DUPLEX_BINDINGS
    if (!result && binding.kind == AEFD_BIND_DUPLEX_TERMINAL) {
        if (!duplex_sources(c)) {
            aefd_client_abort(&c->client);
            result = -5;
        } else {
            actual = 3;
        }
    } else
#endif
        if (!result && binding.kind != AEFD_BIND_FILE) {
        const struct aefd_native_source *source =
            &c->native.sources[binding.selector];
        if (!source->reference || source->selector != binding.selector ||
            (source->rights != 1 && source->rights != 2)) {
            aefd_client_abort(&c->client);
            result = -5;
        } else {
            actual = source->rights;
        }
    }
    result = end(c, result);
    if (!result) {
        *out = binding;
        *rights = actual;
    }
    return result;
}
int64_t aefd_context_flags(struct aefd_context *c, int fd)
{
    int64_t result = begin(c);
    if (result)
        return result;
    return end(c, aefd_session_flags(&c->session, fd));
}
int64_t aefd_context_set_flags(struct aefd_context *c, int fd, int flag)
{
    int64_t result = begin(c);
    if (result)
        return result;
    return end(c, aefd_session_set_flags(&c->session, fd, flag));
}
int64_t aefd_context_seek(struct aefd_context *c, int fd, int64_t delta,
                          int whence)
{
    int64_t result = begin(c);
    if (result)
        return result;
    return end(c, aefd_session_seek(&c->session, fd, delta, whence));
}
int64_t aefd_context_snapshot(struct aefd_context *c, unsigned char *out,
                              size_t length, int omit)
{
    int64_t result = begin(c);
    if (result)
        return result;
    return end(c, aefd_session_snapshot(&c->session, out, length, omit));
}
struct aefd_redirect_result aefd_context_redirect(struct aefd_context *c,
                                                  int from, int to)
{
    int64_t error = begin(c);
    if (error)
        return (struct aefd_redirect_result){
            .status = error, .prepared_selector = -1, .unknown = error != -16};
    struct aefd_redirect_result result =
        aefd_session_redirect(&c->session, from, to);
    aefd_native_leave(&c->native);
    return result;
}
int64_t aefd_context_finish(struct aefd_context *c, struct aefd_finish *out)
{
    if (!c || !out || !c->state || c->session.initialized != 1)
        return -5;
    if (c->state == 3) {
        *out = c->session.receipt;
        return 0;
    }
    if (c->state != 1)
        return -16;
    if (c->native.active || c->native.busy)
        return -16;
    int64_t error = begin(c);
    if (error == -16)
        return error;
#ifdef AEFD_TERMINAL_DUPLEX_BINDINGS
    if (!error)
        for (unsigned fd = 0; fd < AEFD_BINDINGS_COUNT; ++fd)
            if (c->map.slots[fd].kind == AEFD_BIND_DUPLEX_TERMINAL) {
                /* Finalization must preflight before even an earlier
                 * directional entry can cause a physical source close. */
                if (!duplex_sources(c))
                    aefd_client_abort(&c->client);
                break;
            }
#endif
    c->state = 2;
    struct aefd_finish result = aefd_session_finish(&c->session);
    if (!error)
        aefd_native_leave(&c->native);
    c->state = 3;
    *out = result;
    return 0;
}

#ifdef AEFD_CWD_WIRE
int64_t aefd_context_chdir(struct aefd_context *c, const unsigned char *path,
                           size_t length)
{
    if (!path)
        return -14;
    if (!length)
        return -2;
    if (length > 255)
        return -ENAMETOOLONG;
    int64_t result = begin(c);
    if (result)
        return result;
    uint64_t args[4] = {0, length, 0, 0};
    struct aefd_reply reply;
    int moved = aefd_client_exchange(&c->client, 8, args, path, length, &reply);
    return end(c, moved == 1 ? reply.status : moved < 0 ? -5 : -22);
}
int64_t aefd_context_getcwd(struct aefd_context *c, unsigned char out[256])
{
    if (!out)
        return -14;
    memset(out, 0, 256);
    int64_t result = begin(c);
    if (result)
        return result;
    uint64_t args[4] = {0};
    struct aefd_reply reply;
    int moved = aefd_client_exchange(&c->client, 9, args, NULL, 0, &reply);
    result = moved == 1 ? reply.status : moved < 0 ? -5 : -22;
    if (!result) {
        memcpy(out, c->workspace, reply.body);
        result = (int64_t)reply.body;
    }
    return end(c, result);
}
#endif
