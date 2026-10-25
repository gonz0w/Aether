/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-table.h"
#include "fd-routing.h"
int aefd_prior_main(int, char **);
#define main aefd_prior_main
#include "fd-facade-host.c"
#undef main

static struct aefd_bindings initial_map(const char *mode)
{
    unsigned char raw[AEFD_BINDINGS_BYTES] = {0};
    memcpy(raw, "AEFDT001", 8);
    aefd_put(raw, 1, !strcmp(mode, "table-stale") ? 78 : 77);
    aefd_put(raw, 2, 16);
    if (strcmp(mode, "capacity")) {
        for (unsigned i = 0; i < 3; ++i) {
            raw[64 + i * 4] = AEFD_BIND_CONSOLE;
            raw[65 + i * 4] = (unsigned char)i;
        }
        for (unsigned i = 3; i < 5; ++i) {
            raw[64 + i * 4] = AEFD_BIND_PIPE;
            raw[65 + i * 4] = (unsigned char)i;
        }
    }
    if (!strcmp(mode, "full"))
        for (unsigned i = 0; i < 16; ++i) {
            raw[64 + i * 4] = AEFD_BIND_CONSOLE;
            raw[65 + i * 4] = 0;
        }
    if (!strcmp(mode, "dup-full"))
        for (unsigned i = 6; i < 16; ++i) {
            raw[64 + i * 4] = AEFD_BIND_CONSOLE;
            raw[65 + i * 4] = 0;
        }
    if (!strcmp(mode, "stale-source")) {
        raw[64 + 5 * 4] = AEFD_BIND_FILE;
        raw[65 + 5 * 4] = 3;
    }
    if (!strcmp(mode, "hole"))
        memset(raw + 64, 0, 4);
    struct aefd_bindings map;
    assert(aefd_bindings_decode(raw, sizeof raw,
                                !strcmp(mode, "table-stale") ? 78 : 77, &map));
    return map;
}
static int64_t open_file(struct aefd_bindings *map, struct aefd_client *client)
{
    return aefd_table_open(map, client, (const unsigned char *)"file", 4, 0);
}
static void same(const struct aefd_bindings *map,
                 const struct aefd_bindings *before)
{
    assert(!memcmp(map, before, sizeof *map));
}
static void normal(struct aefd_bindings *map, struct aefd_client *client)
{
    assert(open_file(map, client) == 5);
    assert(map->slots[5].kind == AEFD_BIND_FILE && map->slots[5].selector == 3);
    assert(map->slots[3].kind == AEFD_BIND_PIPE && map->slots[3].selector == 3);
    assert(aefd_routed_read(map, client, NULL, 5, out, 2) == 2);
    assert(!memcmp(out, "ab", 2));
    assert(aefd_table_seek(map, client, 5, 0, 1) == 2);
    assert(aefd_table_seek(map, client, 5, -4, 2) == 2);
    assert(aefd_table_dup(map, client, 5, 6, 0) == 6);
    assert(map->slots[6].selector == 4 && !map->slots[6].cloexec);
    assert(aefd_table_set_cloexec(map, client, 6, 1) == 0);
    assert(map->slots[6].cloexec == 1 && !map->slots[5].cloexec);
    assert(aefd_table_close(map, client, 5) == 0);
    assert(map->slots[5].kind == AEFD_BIND_EMPTY);
    assert(aefd_routed_read(map, client, NULL, 6, out, 2) == 2);
    assert(!memcmp(out, "cd", 2));
    assert(aefd_table_close(map, client, 6) == 0);
    assert(map->slots[6].kind == AEFD_BIND_EMPTY);
    assert(aefd_routed_read(map, client, NULL, 5, out, 2) == -9);
    assert(aefd_table_seek(map, client, 3, 0, 0) == -38);
    assert(aefd_table_seek(map, client, 3, 0, 3) == -22);
    assert(aefd_table_close(map, client, 3) == -38);
    assert(aefd_table_dup(map, client, 0, 0, 0) == -38);
    assert(aefd_table_set_cloexec(map, client, 1, 1) == -38);
}
int main(int argc, char **argv)
{
    assert(argc == 2);
    const char *mode = argv[1];
    assert(fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK) == 0);
    assert(fcntl(STDOUT_FILENO, F_SETFL, O_NONBLOCK) == 0);
    struct host_io host = {.chunk = !strcmp(mode, "bytewise") ? 1 : 7};
    struct aefd_io io = {&host, host_read, host_write, host_wait, host_close};
    struct aefd_client client;
    assert(aefd_client_init(&client, io, workspace, 77));
    struct aefd_bindings map = initial_map(mode), before = map;
    memset(out, 0xa5, sizeof out);
    if (!strcmp(mode, "happy") || !strcmp(mode, "bytewise")) {
        normal(&map, &client);
    } else if (!strcmp(mode, "full")) {
        assert(open_file(&map, &client) == -24);
        same(&map, &before);
        assert(client.sequence == 1 && client.live);
    } else if (!strcmp(mode, "dup-full")) {
        assert(open_file(&map, &client) == 5);
        before = map;
        assert(aefd_table_dup(&map, &client, 5, 0, 0) == -24);
        same(&map, &before);
        assert(client.sequence == 2 && client.live);
        assert(aefd_table_close(&map, &client, 5) == 0);
    } else if (!strcmp(mode, "table-stale")) {
        assert(open_file(&map, &client) == -5);
        same(&map, &before);
        assert(!client.live);
    } else if (!strcmp(mode, "stale-source")) {
        assert(aefd_table_close(&map, &client, 5) == -9);
        same(&map, &before);
        assert(aefd_table_set_cloexec(&map, &client, 5, 1) == -9);
        same(&map, &before);
        assert(aefd_table_dup(&map, &client, 5, 6, 1) == -9);
        same(&map, &before);
        assert(client.live);
    } else if (!strcmp(mode, "capacity")) {
        for (int fd = 0; fd < 13; ++fd) {
            assert(open_file(&map, &client) == fd);
            assert(map.slots[fd].selector == fd + 3);
        }
        before = map;
        assert(open_file(&map, &client) == -24);
        same(&map, &before);
        assert(map.slots[13].kind == AEFD_BIND_EMPTY);
        for (int fd = 0; fd < 13; ++fd)
            assert(aefd_table_close(&map, &client, fd) == 0);
    } else if (!strcmp(mode, "hole")) {
        assert(open_file(&map, &client) == 0);
        assert(map.slots[0].kind == AEFD_BIND_FILE &&
               map.slots[0].selector == 3);
        assert(aefd_routed_read(&map, &client, NULL, 0, NULL, 0) == 0);
        assert(aefd_table_close(&map, &client, 0) == 0);
        assert(map.slots[0].kind == AEFD_BIND_EMPTY);
    } else if (!strcmp(mode, "denied")) {
        assert(aefd_table_open(&map, &client, (const unsigned char *)"missing",
                               7, 0) == -2);
        same(&map, &before);
        assert(aefd_table_open(&map, &client, (const unsigned char *)"file", 4,
                               2) == -22);
        assert(aefd_table_dup(&map, &client, 0, 16, 0) == -22);
        assert(aefd_table_set_cloexec(&map, &client, 0, -1) == -22);
        same(&map, &before);
        assert(open_file(&map, &client) == 5);
        assert(aefd_routed_read(&map, &client, NULL, 5, out, 2) == -13);
        untouched(0);
        assert(client.live && map.slots[5].kind == AEFD_BIND_FILE);
        assert(aefd_routed_read(&map, &client, NULL, 5, out, 2) == 2);
        assert(!memcmp(out, "ab", 2));
        assert(aefd_table_close(&map, &client, 5) == 0);
    } else if (!strcmp(mode, "open-loss")) {
        assert(open_file(&map, &client) == -5);
        same(&map, &before);
        assert(!client.live);
    } else {
        assert(open_file(&map, &client) == 5);
        before = map;
        if (!strcmp(mode, "close-loss") || !strcmp(mode, "source-close")) {
            assert(aefd_table_close(&map, &client, 5) == -5);
        } else if (!strcmp(mode, "dup-loss") || !strcmp(mode, "collision")) {
            assert(aefd_table_dup(&map, &client, 5, 6, 1) == -5);
        } else if (!strcmp(mode, "flags-loss")) {
            assert(aefd_table_set_cloexec(&map, &client, 5, 1) == -5);
        } else {
            assert(aefd_routed_read(&map, &client, NULL, 5, out, 2) == -5);
            untouched(0);
        }
        same(&map, &before);
        assert(!client.live);
        assert(aefd_table_close(&map, &client, 5) == -5);
        same(&map, &before);
    }
    aefd_client_abort(&client);
    assert(!client.workspace && host.closes == 1);
    assert(!client.closed.input && !client.closed.output);
    aefd_client_abort(&client);
    assert(host.closes == 1);
    return 0;
}
