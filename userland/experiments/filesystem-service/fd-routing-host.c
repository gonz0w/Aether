/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only wrapper reuses exact predecessor consumer and live Rust server. */
#include "fd-routing.h"
static int64_t mapped_file_read(struct aefd_client *, int, unsigned char *,
                                size_t);
int aefd_prior_main(int, char **);
#define aefd_file_read mapped_file_read
#define main aefd_prior_main
#include "fd-facade-host.c"
#undef main
#undef aefd_file_read

static struct aefd_bindings routing_map(uint64_t generation)
{
    unsigned char raw[AEFD_BINDINGS_BYTES] = {0};
    memcpy(raw, "AEFDT001", 8);
    aefd_put(raw, 1, generation);
    aefd_put(raw, 2, 16);
    raw[64] = AEFD_BIND_CONSOLE;
    raw[64 + 3 * 4] = AEFD_BIND_PIPE;
    raw[65 + 3 * 4] = 3;
    raw[64 + 8 * 4] = AEFD_BIND_FILE;
    raw[65 + 8 * 4] = 3;
    raw[64 + 9 * 4] = AEFD_BIND_FILE;
    raw[65 + 9 * 4] = 4;
    struct aefd_bindings map;
    assert(aefd_bindings_decode(raw, sizeof raw, generation, &map));
    return map;
}
static int64_t mapped_file_read(struct aefd_client *client, int fd,
                                unsigned char *bytes, size_t count)
{
    /* Preserve preceding invalid source-field tests; valid reads now route
     * logical8/9 to source3/4. These test maps are not live startup admission.
     */
    if (fd != 3 && fd != 4)
        return aefd_file_read(client, fd, bytes, count);
    struct aefd_bindings map = routing_map(client->generation);
    return aefd_routed_read(&map, client, NULL, fd == 3 ? 8 : 9, bytes, count);
}
struct stream_test {
    unsigned calls, closes;
    unsigned expected_kind, expected_selector;
    struct aefd_stream_result reply;
};
static struct aefd_stream_result fake_stream(void *context, unsigned kind,
                                             unsigned selector,
                                             unsigned char *bytes, size_t count)
{
    struct stream_test *test = context;
    ++test->calls;
    assert(kind == test->expected_kind && selector == test->expected_selector);
    memset(bytes, 0x66, count);
    if (count >= 2)
        memcpy(bytes, "xy", 2);
    return test->reply;
}
static int64_t forbidden_read(void *context, unsigned char *bytes, size_t count)
{
    (void)context;
    (void)bytes;
    (void)count;
    assert(count == SIZE_MAX);
    return -5;
}
static int64_t forbidden_write(void *context, const unsigned char *bytes,
                               size_t count)
{
    (void)context;
    (void)bytes;
    assert(count == SIZE_MAX);
    return -5;
}
static int forbidden_wait(void *context, int writing)
{
    (void)context;
    (void)writing;
    assert(writing == INT32_MIN);
    return -5;
}
static struct aefd_close_result fake_close(void *context)
{
    struct stream_test *test = context;
    ++test->closes;
    return (struct aefd_close_result){-5, -9};
}
static unsigned char private_bytes[AEFD_READ_MAX], guarded[12];
static void guards(size_t start)
{
    for (size_t i = start; i < sizeof guarded; ++i)
        assert(guarded[i] == 0xa5);
}
static void stream_tests(void)
{
    for (unsigned mode = 0; mode < 13; ++mode) {
        struct stream_test test = {.expected_kind = AEFD_BIND_PIPE,
                                   .expected_selector = 3,
                                   .reply = {1, 2}};
        struct aefd_io io = {&test, forbidden_read, forbidden_write,
                             forbidden_wait, fake_close};
        struct aefd_client client;
        assert(aefd_client_init(&client, io, private_bytes, 77));
        struct aefd_bindings map = routing_map(77);
        struct aefd_stream_reader reader = {&test, fake_stream};
        memset(guarded, 0xa5, sizeof guarded);
        int fd = 3;
        size_t count = 4;
        int64_t expected = 2;
        int live = 1;
        unsigned calls = 1;
        if (mode == 1) {
            test.reply.result = -13;
            expected = -13;
        } else if (mode == 2) {
            test.reply.result = 0;
            expected = 0;
        } else if (mode == 3) {
            test.reply.complete = 0;
            expected = -5;
            live = 0;
        } else if (mode == 4) {
            test.reply.result = 5;
            expected = -5;
            live = 0;
        } else if (mode == 5) {
            test.reply.result = -INT64_C(2147483648);
            expected = -5;
            live = 0;
        } else if (mode == 6) {
            map = routing_map(78);
            expected = -5;
            live = 0;
            calls = 0;
        } else if (mode == 7) {
            fd = 7;
            expected = -9;
            calls = 0;
        } else if (mode == 8) {
            reader.read = NULL;
            expected = -38;
            calls = 0;
        } else if (mode == 9) {
            count = 0;
            test.reply.result = 0;
            expected = 0;
        } else if (mode == 10) {
            fd = 0;
            test.expected_kind = AEFD_BIND_CONSOLE;
            test.expected_selector = 0;
        } else if (mode == 11) {
            count = AEFD_READ_MAX + 1;
            expected = -22;
            calls = 0;
        } else if (mode == 12) {
            test.reply.result = -5;
            expected = -5;
        }
        assert(aefd_routed_read(&map, &client, &reader, fd, guarded, count) ==
               expected);
        assert(client.live == live && test.calls == calls);
        if (expected == 2) {
            assert(!memcmp(guarded, "xy", 2));
            guards(2);
        } else {
            guards(0);
        }
        for (size_t i = 0; i < sizeof private_bytes; ++i)
            assert(!private_bytes[i]);
        if (!live) {
            assert(!client.workspace && test.closes == 1);
            assert(client.closed.input == -5 && client.closed.output == -9);
            assert(aefd_routed_read(&map, &client, &reader, fd, guarded, 4) ==
                   -5);
            assert(test.calls == calls);
        }
        aefd_client_abort(&client);
        assert(test.closes == 1);
    }
}
int main(int argc, char **argv)
{
    stream_tests();
    return aefd_prior_main(argc, argv);
}
