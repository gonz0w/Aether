/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only actual pipe lifetime tests with injected completion observations.
 */
#include "fd-stream-tests.h"
#include "fd-routing.h"
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
struct observed {
    int input, output, physical_closed;
    unsigned source_calls, file_closes;
    struct aefd_stream_close_result reply;
    int close_actual;
};
static unsigned char scratch[AEFD_READ_MAX], bytes[8];
static int64_t forbidden_read(void *ctx, unsigned char *out, size_t count)
{
    (void)ctx;
    (void)out;
    assert(count == SIZE_MAX);
    return -5;
}
static int64_t forbidden_write(void *ctx, const unsigned char *out,
                               size_t count)
{
    (void)ctx;
    (void)out;
    assert(count == SIZE_MAX);
    return -5;
}
static int forbidden_wait(void *ctx, int writing)
{
    (void)ctx;
    assert(writing == INT32_MIN);
    return -5;
}
static struct aefd_close_result file_close(void *context)
{
    struct observed *seen = context;
    ++seen->file_closes;
    return (struct aefd_close_result){-5, -9};
}
static struct aefd_stream_close_result
stream_close(void *context, unsigned kind, unsigned selector)
{
    struct observed *seen = context;
    ++seen->source_calls;
    assert(kind == AEFD_BIND_PIPE && selector == 3);
    if (seen->close_actual) {
        assert(!seen->physical_closed);
        assert(close(seen->input) == 0);
        seen->physical_closed = 1;
    }
    return seen->reply;
}
static struct aefd_stream_result stream_read(void *context, unsigned kind,
                                             unsigned selector,
                                             unsigned char *out, size_t count)
{
    struct observed *seen = context;
    assert(kind == AEFD_BIND_PIPE && selector == 3);
    ssize_t result = read(seen->input, out, count);
    assert(result >= 0);
    return (struct aefd_stream_result){1, (int64_t)result};
}
static struct aefd_bindings map_for(unsigned mode)
{
    unsigned char raw[AEFD_BINDINGS_BYTES] = {0};
    memcpy(raw, "AEFDT001", 8);
    aefd_put(raw, 1, mode == 12 ? 78 : 77);
    aefd_put(raw, 2, 16);
    raw[64] = AEFD_BIND_CONSOLE;
    raw[64 + 3 * 4] = AEFD_BIND_PIPE;
    raw[65 + 3 * 4] = 3;
    raw[64 + 8 * 4] = AEFD_BIND_FILE;
    raw[65 + 8 * 4] = 3;
    if (mode == 11)
        for (unsigned fd = 0; fd < 16; ++fd) {
            raw[64 + fd * 4] = AEFD_BIND_PIPE;
            raw[65 + fd * 4] = 3;
        }
    struct aefd_bindings map;
    assert(aefd_bindings_decode(raw, sizeof raw, mode == 12 ? 78 : 77, &map));
    return map;
}
static void exercise(void)
{
    static int ran;
    if (ran)
        return;
    ran = 1;
    for (unsigned mode = 0; mode < 14; ++mode) {
        int pair[2];
        assert(pipe(pair) == 0);
        struct observed seen = {.input = pair[0],
                                .output = pair[1],
                                .reply = {1, 1, 0},
                                .close_actual = 1};
        struct aefd_io io = {&seen, forbidden_read, forbidden_write,
                             forbidden_wait, file_close};
        struct aefd_client client;
        assert(aefd_client_init(&client, io, scratch, 77));
        struct aefd_bindings map = map_for(mode), before = map;
        struct aefd_stream_closer closer = {&seen, stream_close};
        if (mode == 0) {
            assert(aefd_mixed_dup(&map, &client, 3, 4, 1) == 4);
            assert(map.slots[4].kind == AEFD_BIND_PIPE &&
                   map.slots[4].selector == 3);
            assert(map.slots[4].cloexec == 1 && map.slots[3].cloexec == 0);
            assert(aefd_mixed_set_cloexec(&map, &client, 4, 0) == 0);
            assert(map.slots[4].cloexec == 0);
            assert(aefd_mixed_close(&map, &client, NULL, 3) == 0);
            assert(map.slots[3].kind == AEFD_BIND_EMPTY && !seen.source_calls);
            assert(fcntl(seen.input, F_GETFD) >= 0);
            assert(write(seen.output, "ab", 2) == 2);
            struct aefd_stream_reader reader = {&seen, stream_read};
            memset(bytes, 0xa5, sizeof bytes);
            assert(aefd_routed_read(&map, &client, &reader, 4, bytes, 4) == 2);
            assert(!memcmp(bytes, "ab", 2) && bytes[2] == 0xa5);
            assert(aefd_mixed_close(&map, &client, &closer, 4) == 0);
            assert(map.slots[4].kind == AEFD_BIND_EMPTY &&
                   seen.source_calls == 1);
            assert(map.slots[8].kind == AEFD_BIND_FILE &&
                   map.slots[8].selector == 3);
            assert(aefd_mixed_close(&map, &client, &closer, 4) == -9);
            assert(aefd_mixed_dup(&map, &client, 0, 6, 1) == 6);
            assert(map.slots[6].kind == AEFD_BIND_CONSOLE &&
                   map.slots[6].cloexec == 1);
            assert(aefd_mixed_close(&map, &client, NULL, 6) == 0);
            assert(seen.source_calls == 1 && client.live);
        } else if (mode == 11) {
            assert(aefd_mixed_dup(&map, &client, 3, 0, 0) == -24);
            assert(!memcmp(&map, &before, sizeof map) && !seen.source_calls);
        } else if (mode == 12) {
            assert(aefd_mixed_dup(&map, &client, 3, 4, 0) == -5);
            assert(!client.live && !seen.source_calls);
            assert(!memcmp(&map, &before, sizeof map));
        } else if (mode == 13) {
            assert(aefd_mixed_dup(&map, &client, 3, 16, 0) == -22);
            assert(aefd_mixed_dup(&map, &client, 3, 4, 2) == -22);
            assert(aefd_mixed_set_cloexec(&map, &client, 3, -1) == -22);
            assert(aefd_mixed_close(&map, &client, &closer, 15) == -9);
            assert(!memcmp(&map, &before, sizeof map) && !seen.source_calls);
        } else {
            int64_t expected = -5;
            int live = 0, consumed = 0;
            seen.close_actual = 0;
            if (mode == 1) {
                seen.reply = (struct aefd_stream_close_result){1, 0, -13};
                expected = -13;
                live = 1;
            } else if (mode == 2) {
                seen.reply = (struct aefd_stream_close_result){1, 1, -5};
                seen.close_actual = 1;
                live = 1;
                consumed = 1;
            } else if (mode == 3 || mode == 4) {
                seen.reply = (struct aefd_stream_close_result){0, 0, -5};
                seen.close_actual = mode == 4;
            } else if (mode == 5) {
                seen.reply = (struct aefd_stream_close_result){1, 0, 0};
            } else if (mode == 6) {
                seen.reply.complete = 2;
            } else if (mode == 7) {
                seen.reply.consumed = 2;
            } else if (mode == 8) {
                seen.reply.status = 1;
            } else if (mode == 9) {
                seen.reply.status = -INT64_C(2147483648);
            } else if (mode == 10) {
                closer.close = NULL;
                expected = -38;
                live = 1;
            }
            assert(aefd_mixed_close(&map, &client, &closer, 3) == expected);
            assert(client.live == live);
            if (consumed)
                assert(map.slots[3].kind == AEFD_BIND_EMPTY);
            else
                assert(!memcmp(&map, &before, sizeof map));
            unsigned calls = seen.source_calls;
            if (!live) {
                assert(aefd_mixed_close(&map, &client, &closer, 3) == -5);
                assert(seen.source_calls == calls && seen.file_closes == 1);
            }
            if (mode == 1) {
                assert(fcntl(seen.input, F_GETFD) >= 0);
                seen.reply = (struct aefd_stream_close_result){1, 1, 0};
                seen.close_actual = 1;
                assert(aefd_mixed_close(&map, &client, &closer, 3) == 0);
                assert(seen.source_calls == 2 &&
                       map.slots[3].kind == AEFD_BIND_EMPTY);
            }
        }
        aefd_client_abort(&client);
        assert(seen.file_closes == 1);
        if (!seen.physical_closed)
            assert(close(seen.input) == 0);
        errno = 0;
        assert(fcntl(seen.input, F_GETFD) == -1 && errno == EBADF);
        assert(close(seen.output) == 0);
    }
}
static int file_entry(const struct aefd_bindings *map, int fd)
{
    return map && fd >= 0 && fd < 16 && map->slots[fd].kind == AEFD_BIND_FILE;
}
int64_t aefd_stream_test_open(struct aefd_bindings *map,
                              struct aefd_client *client,
                              const unsigned char *name, size_t length,
                              int flag)
{
    exercise();
    return aefd_table_open(map, client, name, length, flag);
}
int64_t aefd_stream_test_dup(struct aefd_bindings *map,
                             struct aefd_client *client, int fd, int minimum,
                             int flag)
{
    exercise();
    return file_entry(map, fd) ? aefd_mixed_dup(map, client, fd, minimum, flag)
                               : aefd_table_dup(map, client, fd, minimum, flag);
}
int64_t aefd_stream_test_close(struct aefd_bindings *map,
                               struct aefd_client *client, int fd)
{
    exercise();
    return file_entry(map, fd) ? aefd_mixed_close(map, client, NULL, fd)
                               : aefd_table_close(map, client, fd);
}
int64_t aefd_stream_test_flags(struct aefd_bindings *map,
                               struct aefd_client *client, int fd, int flag)
{
    exercise();
    return file_entry(map, fd) ? aefd_mixed_set_cloexec(map, client, fd, flag)
                               : aefd_table_set_cloexec(map, client, fd, flag);
}
