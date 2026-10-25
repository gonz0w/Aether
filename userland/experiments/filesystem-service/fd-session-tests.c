/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-session-tests.h"
#include "fd-session.h"
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
struct observed {
    int ends[2];
    unsigned creates, closes, stream_closes;
    int fail_mode;
};
static unsigned char scratch[AEFD_READ_MAX], bytes[8];
static int64_t forbidden_read(void *ctx, unsigned char *out, size_t n)
{
    (void)ctx;
    (void)out;
    assert(n == SIZE_MAX);
    return -5;
}
static int64_t forbidden_write(void *ctx, const unsigned char *out, size_t n)
{
    (void)ctx;
    (void)out;
    assert(n == SIZE_MAX);
    return -5;
}
static int forbidden_wait(void *ctx, int writing)
{
    (void)ctx;
    assert(writing == INT32_MIN);
    return -5;
}
static struct aefd_close_result file_close(void *ctx)
{
    struct observed *o = ctx;
    ++o->closes;
    return (struct aefd_close_result){-5, -9};
}
static struct aefd_pipe_result create(void *ctx)
{
    struct observed *o = ctx;
    ++o->creates;
    assert(o->creates == 1 && pipe(o->ends) == 0);
    return (struct aefd_pipe_result){1, 0, 3, 4};
}
static struct aefd_stream_result
read_pipe(void *ctx, unsigned kind, unsigned sel, unsigned char *out, size_t n)
{
    struct observed *o = ctx;
    assert(kind == AEFD_BIND_PIPE && sel == 3);
    ssize_t got = read(o->ends[0], out, n);
    assert(got >= 0);
    return (struct aefd_stream_result){1, got};
}
static struct aefd_stream_result write_pipe(void *ctx, unsigned kind,
                                            unsigned sel,
                                            const unsigned char *in, size_t n)
{
    struct observed *o = ctx;
    assert(kind == AEFD_BIND_PIPE && sel == 4);
    ssize_t got = write(o->ends[1], in, n);
    assert(got >= 0);
    return (struct aefd_stream_result){1, got};
}
static struct aefd_stream_close_result close_pipe(void *ctx, unsigned kind,
                                                  unsigned sel)
{
    struct observed *o = ctx;
    ++o->stream_closes;
    assert(kind == AEFD_BIND_PIPE && (sel == 3 || sel == 4));
    unsigned at = sel - 3;
    if (o->fail_mode == 1 && sel == 3)
        return (struct aefd_stream_close_result){1, 0, -13};
    if (o->fail_mode == 3 && sel == 3)
        return (struct aefd_stream_close_result){0, 0, -5};
    assert(o->ends[at] >= 0 && close(o->ends[at]) == 0);
    o->ends[at] = -1;
    if (o->fail_mode == 2 && sel == 3)
        return (struct aefd_stream_close_result){1, 1, -5};
    if (o->fail_mode == 4 && sel == 3)
        return (struct aefd_stream_close_result){0, 0, -5};
    return (struct aefd_stream_close_result){1, 1, 0};
}
static void exercise(void)
{
    static int ran;
    if (ran)
        return;
    ran = 1;
    /* Run unchanged predecessor units without an extra real file request. */
    assert(aefd_replace_test_open(NULL, NULL, NULL, 0, 0) == -5);
    for (unsigned mode = 0; mode < 15; ++mode) {
        struct observed o = {.ends = {-1, -1}};
        struct aefd_io io = {&o, forbidden_read, forbidden_write,
                             forbidden_wait, file_close};
        struct aefd_adapters a = {
            {&o, read_pipe}, {&o, write_pipe}, {&o, close_pipe}, {&o, create}};
        struct aefd_session s = {0};
        struct aefd_bindings map = {0};
        struct aefd_client client = {0};
        unsigned char raw[AEFD_BINDINGS_BYTES] = {0},
                      output[AEFD_BINDINGS_BYTES];
        memcpy(raw, "AEFDT001", 8);
        aefd_put(raw, 1, 77);
        aefd_put(raw, 2, 16);
        memset(scratch, 0xa5, sizeof scratch);
        memset(output, 0xa5, sizeof output);
        if (mode == 1 || mode == 2) {
            if (mode == 1)
                raw[0] = 'X';
            else
                io.wait = NULL;
            struct aefd_session before = s;
            struct aefd_client old = client;
            assert(aefd_session_init(&s, &map, &client, raw, sizeof raw, 77, io,
                                     scratch, a) == -22);
            assert(!memcmp(&s, &before, sizeof s) &&
                   !memcmp(&client, &old, sizeof old));
            assert(!o.closes && !o.creates && !s.initialized &&
                   !map.generation);
            for (size_t i = 0; i < sizeof scratch; ++i)
                assert(scratch[i] == 0xa5);
            continue;
        }
        assert(aefd_session_init(&s, &map, &client, raw, sizeof raw, 77, io,
                                 scratch, a) == 0);
        assert(s.map == &map && s.client == &client && map.generation == 77);
        assert(aefd_session_init(&s, &map, &client, raw, sizeof raw, 77, io,
                                 scratch, a) == -16);
        if (mode == 3) { /* Empty retired context must still report unknown. */
            aefd_client_abort(&client);
            struct aefd_finish f = aefd_session_finish(&s);
            assert(f.unknown && f.first_error == -5 && !f.attempted &&
                   !f.remaining);
        } else {
            int pair[2] = {-1, -1};
            assert(aefd_session_pipe(&s, pair, 1) == 0 && pair[0] == 0 &&
                   pair[1] == 1);
            assert(aefd_session_flags(&s, 0) == 1 &&
                   aefd_session_flags(&s, 15) == -9);
            assert(aefd_session_set_flags(&s, 0, 2) == -22);
            assert(aefd_session_seek(&s, 0, 0, 0) == -29);
            assert(aefd_session_seek(&s, 0, 0, 3) == -22);
            assert(aefd_session_seek(&s, 15, 0, 0) == -9);
            if (mode == 4) {
                map.generation = 78;
                assert(aefd_session_flags(&s, 0) == -5 && !client.live);
            } else if (mode == 5 || mode == 6) {
                map.slots[4] = (struct aefd_binding){AEFD_BIND_FILE, 3, 1, 0};
                map.slots[5] = (struct aefd_binding){AEFD_BIND_FILE, 3, 1, 0};
                assert(aefd_session_snapshot(&s, output, sizeof output,
                                             mode == 6) == -5);
                for (size_t i = 0; i < sizeof output; ++i)
                    assert(output[i] == 0xa5);
                assert(!client.live);
            } else if (mode == 7) {
                assert(aefd_session_snapshot(&s, output, sizeof output - 1,
                                             0) == -22);
                assert(aefd_session_snapshot(&s, output, sizeof output, 2) ==
                       -22);
                for (size_t i = 0; i < sizeof output; ++i)
                    assert(output[i] == 0xa5);
            } else {
                struct aefd_bindings before = map, decoded;
                assert(aefd_session_snapshot(&s, output, sizeof output, 0) ==
                       0);
                assert(
                    aefd_bindings_decode(output, sizeof output, 77, &decoded));
                assert(!memcmp(&before, &decoded, sizeof map));
                assert(aefd_session_snapshot(&s, output, sizeof output, 1) ==
                       0);
                assert(
                    aefd_bindings_decode(output, sizeof output, 77, &decoded));
                assert(!decoded.slots[0].kind && !decoded.slots[1].kind);
                assert(!memcmp(&before, &map, sizeof map) && !o.stream_closes);
                assert(aefd_session_dup(&s, 0, 2, 0) == 2);
                assert(aefd_session_replace(&s, 1, 3) == 3);
                assert(aefd_session_flags(&s, 3) == 0);
                assert(aefd_session_close(&s, 0) == 0 && !o.stream_closes);
                assert(aefd_session_set_flags(&s, 2, 0) == 0);
                assert(aefd_session_flags(&s, 2) == 0);
                assert(aefd_session_write(&s, 3, (const unsigned char *)"ok",
                                          2) == 2);
                assert(aefd_session_read(&s, 2, bytes, 2) == 2 &&
                       !memcmp(bytes, "ok", 2));
                if (mode >= 8 && mode <= 11)
                    o.fail_mode = (int)mode - 7;
                if (mode == 12)
                    s.adapters.closer.close = NULL;
                if (mode == 13) {
                    /* Reinitializing the same live/retired client through
                     * another context is forbidden. */
                    struct aefd_session other = {0};
                    assert(aefd_session_init(&other, &map, &client, raw,
                                             sizeof raw, 77, io, scratch,
                                             a) == -16);
                }
                if (mode == 14) {
                    map.slots[4] =
                        (struct aefd_binding){AEFD_BIND_FILE, 3, 0, 0};
                    assert(aefd_session_replace(&s, 4, 3) == -38);
                    map.slots[4] = (struct aefd_binding){0};
                }
            }
            struct aefd_finish f = aefd_session_finish(&s);
            if (mode == 0 || mode == 13 || mode == 14) {
                assert(f.attempted == 3 && f.removed == 3 && !f.remaining &&
                       !f.unknown && !f.first_error);
                assert(o.stream_closes == 2);
            } else if (mode == 8) {
                assert(f.attempted == 3 && f.removed == 2 && f.remaining == 1 &&
                       !f.unknown && f.first_error == -13);
            } else if (mode == 9) {
                assert(f.attempted == 3 && f.removed == 3 && !f.remaining &&
                       !f.unknown && f.first_error == -5);
            } else if (mode == 10 || mode == 11) {
                assert(f.attempted == 2 && f.removed == 1 && f.remaining == 2 &&
                       f.unknown && f.first_error == -5);
                assert(o.stream_closes == 1);
            } else if (mode == 12) {
                assert(f.attempted == 3 && f.removed == 1 && f.remaining == 2 &&
                       !f.unknown && f.first_error == -38);
            } else if (mode == 4 || mode == 5 || mode == 6)
                assert(f.unknown && !f.attempted);
        }
        unsigned closed = o.stream_closes;
        struct aefd_finish saved = s.receipt;
        struct aefd_finish again = aefd_session_finish(&s);
        assert(again.attempted == saved.attempted &&
               again.removed == saved.removed &&
               again.remaining == saved.remaining &&
               again.first_error == saved.first_error &&
               again.unknown == saved.unknown &&
               again.transport.input == saved.transport.input &&
               again.transport.output == saved.transport.output &&
               o.stream_closes == closed);
        assert(again.transport.input == -5 && again.transport.output == -9 &&
               o.closes == 1);
        assert(aefd_session_read(&s, 0, bytes, 1) == -5);
        assert(aefd_session_init(&s, &map, &client, raw, sizeof raw, 77, io,
                                 scratch, a) == -16);
        for (unsigned end = 0; end < 2; ++end)
            if (o.ends[end] >= 0) {
                int fd = o.ends[end];
                assert(close(fd) == 0);
                errno = 0;
                assert(fcntl(fd, F_GETFD) == -1 && errno == EBADF);
            }
    }
}
/* Borrow the exact existing fixture map/client; never copy its live table. */
static struct aefd_session view(struct aefd_bindings *map,
                                struct aefd_client *client)
{
    return (struct aefd_session){
        .map = map, .client = client, .initialized = 1};
}
static int file_entry(const struct aefd_bindings *map, int fd)
{
    return map && fd >= 0 && fd < 16 && map->slots[fd].kind == AEFD_BIND_FILE;
}
int64_t aefd_session_test_open(struct aefd_bindings *map,
                               struct aefd_client *client,
                               const unsigned char *name, size_t n, int flag)
{
    exercise();
    struct aefd_session s = view(map, client);
    return aefd_session_open(&s, name, n, flag);
}
int64_t aefd_session_test_dup(struct aefd_bindings *map,
                              struct aefd_client *client, int fd, int minimum,
                              int flag)
{
    exercise();
    struct aefd_session s = view(map, client);
    return file_entry(map, fd) ? aefd_session_dup(&s, fd, minimum, flag)
                               : aefd_table_dup(map, client, fd, minimum, flag);
}
int64_t aefd_session_test_close(struct aefd_bindings *map,
                                struct aefd_client *client, int fd)
{
    exercise();
    struct aefd_session s = view(map, client);
    return file_entry(map, fd) ? aefd_session_close(&s, fd)
                               : aefd_table_close(map, client, fd);
}
int64_t aefd_session_test_flags(struct aefd_bindings *map,
                                struct aefd_client *client, int fd, int flag)
{
    exercise();
    struct aefd_session s = view(map, client);
    return file_entry(map, fd) ? aefd_session_set_flags(&s, fd, flag)
                               : aefd_table_set_cloexec(map, client, fd, flag);
}
int64_t aefd_session_test_seek(struct aefd_bindings *map,
                               struct aefd_client *client, int fd,
                               int64_t delta, int whence)
{
    exercise();
    struct aefd_session s = view(map, client);
    return file_entry(map, fd)
               ? aefd_session_seek(&s, fd, delta, whence)
               : aefd_table_seek(map, client, fd, delta, whence);
}
