/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-session.h"
#include "fd-session-tests.h"
int aefd_redirect_reference_main(int, char **);
#define main aefd_redirect_reference_main
#include "fd-facade-host.c"
#undef main
struct streams {
    int pipe_ends[2], console[2];
    unsigned closes;
    int mode;
};
static struct aefd_stream_close_result stream_close(void *ctx, unsigned kind,
                                                    unsigned selector)
{
    struct streams *p = ctx;
    ++p->closes;
    assert(kind == AEFD_BIND_CONSOLE && selector == 1);
    if (p->mode == 1)
        return (struct aefd_stream_close_result){1, 0, -13};
    if (p->mode == 3)
        return (struct aefd_stream_close_result){0, 0, -5};
    assert(p->console[1] >= 0 && close(p->console[1]) == 0);
    p->console[1] = -1;
    if (p->mode == 2)
        return (struct aefd_stream_close_result){1, 1, -5};
    if (p->mode == 4)
        return (struct aefd_stream_close_result){0, 0, -5};
    return (struct aefd_stream_close_result){1, 1, 0};
}
static struct aefd_stream_result stream_write(void *ctx, unsigned kind,
                                              unsigned selector,
                                              const unsigned char *input,
                                              size_t count)
{
    struct streams *p = ctx;
    assert(kind == AEFD_BIND_PIPE && selector == 4);
    ssize_t n = write(p->pipe_ends[1], input, count);
    assert(n >= 0);
    return (struct aefd_stream_result){1, n};
}
static void same_map(const struct aefd_bindings *map,
                     const struct aefd_bindings *before)
{
    assert(!memcmp(map, before, sizeof *map));
}
int main(int argc, char **argv)
{
    assert(argc == 3);
    assert(aefd_session_test_open(NULL, NULL, NULL, 0, 0) == -5);
    const char *mode = argv[1];
    struct host_io host = {.chunk = !strcmp(mode, "bytewise") ? 1 : 7};
    struct aefd_io io = {&host, host_read, host_write, host_wait, host_close};
    assert(fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK) == 0);
    assert(fcntl(STDOUT_FILENO, F_SETFL, O_NONBLOCK) == 0);
    struct streams streams = {0};
    assert(pipe(streams.pipe_ends) == 0 && pipe(streams.console) == 0);
    struct aefd_adapters adapters = {.writer = {&streams, stream_write},
                                     .closer = {&streams, stream_close}};
    struct aefd_session session = {0};
    struct aefd_bindings map;
    struct aefd_client client = {0};
    unsigned char raw[AEFD_BINDINGS_BYTES] = {0};
    memcpy(raw, "AEFDT001", 8);
    aefd_put(raw, 1, 77);
    aefd_put(raw, 2, 16);
    int capacity = !strcmp(mode, "remote-full");
    if (!capacity) {
        for (unsigned fd = 0; fd < 3; ++fd) {
            raw[64 + fd * 4] = AEFD_BIND_CONSOLE;
            raw[65 + fd * 4] = (unsigned char)fd;
        }
        for (unsigned fd = 3; fd < 5; ++fd) {
            raw[64 + fd * 4] = AEFD_BIND_PIPE;
            raw[65 + fd * 4] = (unsigned char)fd;
            raw[66 + fd * 4] = 1;
        }
    }
    assert(aefd_session_init(&session, &map, &client, raw, sizeof raw, 77, io,
                             workspace, adapters) == 0);
    int source =
        (int)aefd_session_open(&session, (const unsigned char *)"file", 4, 1);
    assert(source == (capacity ? 0 : 5));
    int target =
        (int)(!strcmp(mode, "alias-file")
                  ? aefd_session_dup(&session, source, 6, 1)
                  : aefd_session_open(&session, (const unsigned char *)"file",
                                      4, 1));
    assert(target == (capacity ? 1 : 6));
    int64_t initial = aefd_session_read(&session, source, out, 1);
    if (!strcmp(mode, "source-body") || !strcmp(mode, "source-count")) {
        assert(initial == -5 && !client.live);
        struct aefd_bindings saved = map;
        struct aefd_redirect_result rejected =
            aefd_session_redirect(&session, source, target);
        assert(rejected.status == -5 && rejected.unknown &&
               !rejected.unresolved);
        same_map(&map, &saved);
        goto settle;
    }
    assert(initial == 1 && out[0] == 'a');
    if (capacity) {
        for (int fd = 2; fd < 13; ++fd)
            assert(aefd_session_open(&session, (const unsigned char *)"file", 4,
                                     0) == fd);
    }
    if (!strcmp(mode, "local-full"))
        for (unsigned fd = 0; fd < 16; ++fd)
            if (!map.slots[fd].kind)
                map.slots[fd] =
                    (struct aefd_binding){AEFD_BIND_CONSOLE, 0, 0, 0};
    int self = !strcmp(mode, "file-self");
    int stream_source = !strcmp(mode, "stream-file");
    int stream_target =
        !strcmp(mode, "file-stream") || !strcmp(mode, "target-denied") ||
        !strcmp(mode, "target-consumed") ||
        !strcmp(mode, "target-unknown-open") ||
        !strcmp(mode, "target-unknown-closed") ||
        !strcmp(mode, "missing-adapter") || !strcmp(mode, "cleanup-stale") ||
        !strcmp(mode, "cleanup-loss");
    if (self)
        target = source;
    if (stream_source)
        source = 4;
    if (stream_target)
        target = 1;
    if (!strcmp(mode, "file-empty"))
        target = 7;
    if (!strcmp(mode, "target-denied") || !strcmp(mode, "cleanup-stale") ||
        !strcmp(mode, "cleanup-loss"))
        streams.mode = 1;
    if (!strcmp(mode, "target-consumed"))
        streams.mode = 2;
    if (!strcmp(mode, "target-unknown-open"))
        streams.mode = 3;
    if (!strcmp(mode, "target-unknown-closed"))
        streams.mode = 4;
    if (!strcmp(mode, "missing-adapter"))
        session.adapters.closer.close = NULL;
    if (!strcmp(mode, "stale-target"))
        map.slots[target].selector = 15;
    if (!strcmp(mode, "stale-source"))
        map.slots[source].selector = 15;
    struct aefd_bindings before = map;
    struct aefd_redirect_result r =
        aefd_session_redirect(&session, source, target);
    int uncertain =
        !strcmp(mode, "source-close") || !strcmp(mode, "dup-loss") ||
        !strcmp(mode, "target-loss") || !strcmp(mode, "cleanup-loss") ||
        !strcmp(mode, "cleanup-stale") || !strcmp(mode, "collision") ||
        !strcmp(mode, "target-unknown-open") ||
        !strcmp(mode, "target-unknown-closed");
    if (uncertain) {
        assert(r.status == -5 && r.unknown && r.unresolved && !r.committed &&
               !client.live);
        same_map(&map, &before);
        assert(r.prepared_selector == (!strcmp(mode, "dup-loss")    ? -1
                                       : !strcmp(mode, "collision") ? 3
                                                                    : 5));
        if (!strcmp(mode, "cleanup-loss") || !strcmp(mode, "cleanup-stale"))
            assert(r.cleanup_attempted &&
                   r.cleanup_status ==
                       (!strcmp(mode, "cleanup-stale") ? -9 : -5) &&
                   r.target_status == -13);
        else
            assert(!r.cleanup_attempted);
        unsigned count = streams.closes;
        struct aefd_redirect_result again =
            aefd_session_redirect(&session, source, target);
        assert(again.status == -5 && streams.closes == count &&
               host.closes == 1);
    } else if (capacity || !strcmp(mode, "stale-source") ||
               !strcmp(mode, "stale-target") ||
               !strcmp(mode, "target-denied") ||
               !strcmp(mode, "target-consumed") ||
               !strcmp(mode, "missing-adapter")) {
        int64_t expected =
            capacity ? -24
            : !strcmp(mode, "stale-source") || !strcmp(mode, "stale-target")
                ? -9
            : !strcmp(mode, "target-denied")   ? -13
            : !strcmp(mode, "target-consumed") ? -5
                                               : -38;
        assert(r.status == expected && !r.unknown && !r.unresolved &&
               !r.committed && client.live);
        if (!strcmp(mode, "target-consumed")) {
            assert(r.target_removed &&
                   map.slots[target].kind == AEFD_BIND_EMPTY);
            before.slots[target] = (struct aefd_binding){0};
        }
        same_map(&map, &before);
        if (capacity || !strcmp(mode, "stale-source")) {
            assert(r.prepared_selector == -1 && !r.cleanup_attempted &&
                   !r.target_attempted);
        } else {
            assert(r.prepared_selector == 5 && r.cleanup_attempted &&
                   r.cleanup_status == 0 && r.target_attempted);
            assert(r.target_status == expected);
            assert(aefd_file_read(&client, r.prepared_selector, out, 1) == -9);
        }
        if (!strcmp(mode, "stale-target"))
            map.slots[6].selector = 4;
        if (!strcmp(mode, "stale-source"))
            map.slots[5].selector = 3;
        assert(aefd_session_read(&session, capacity ? 0 : 5, out, 2) == 2 &&
               !memcmp(out, "bc", 2));
        if (!strcmp(mode, "target-denied")) {
            streams.mode = 0;
            r = aefd_session_redirect(&session, 5, 1);
            assert(r.status == 1 && r.committed && !r.unresolved &&
                   streams.closes == 2);
            assert(aefd_session_read(&session, 1, out, 2) == 2 &&
                   !memcmp(out, "de", 2));
        }
    } else {
        assert(r.status == target && r.committed && !r.unresolved &&
               !r.unknown && client.live);
        assert(!r.cleanup_attempted);
        assert(map.slots[source].cloexec == 1);
        assert(map.slots[target].cloexec == (self ? 1 : 0));
        assert(r.prepared_selector == (self || stream_source ? -1 : 5));
        assert(r.target_attempted == (!self && strcmp(mode, "file-empty")));
        assert(r.target_removed == r.target_attempted);
        if (stream_source) {
            assert(map.slots[target].kind == AEFD_BIND_PIPE &&
                   map.slots[target].selector == 4);
            assert(aefd_session_write(&session, target,
                                      (const unsigned char *)"xy", 2) == 2);
            assert(read(streams.pipe_ends[0], out, 2) == 2 &&
                   !memcmp(out, "xy", 2));
        } else {
            assert(map.slots[target].kind == AEFD_BIND_FILE);
            assert(aefd_session_read(&session, target, out, 2) == 2 &&
                   !memcmp(out, "bc", 2));
            assert(aefd_session_read(&session, source, out, 2) == 2 &&
                   !memcmp(out, "de", 2));
        }
        if (stream_target)
            assert(read(streams.console[0], out, sizeof out) == 0);
        for (int fd = 0; fd < 16; ++fd)
            if (fd != target)
                assert(!memcmp(&map.slots[fd], &before.slots[fd],
                               sizeof map.slots[fd]));
    }
settle:
    if (client.live)
        for (int fd = 0; fd < 16; ++fd)
            if (map.slots[fd].kind == AEFD_BIND_FILE)
                assert(aefd_session_close(&session, fd) == 0);
    aefd_client_abort(&client);
    assert(host.closes == 1);
    for (unsigned end = 0; end < 2; ++end) {
        if (streams.pipe_ends[end] >= 0)
            assert(close(streams.pipe_ends[end]) == 0);
        if (streams.console[end] >= 0)
            assert(close(streams.console[end]) == 0);
    }
    return 0;
}
