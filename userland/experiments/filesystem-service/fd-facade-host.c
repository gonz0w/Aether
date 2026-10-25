/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only OS-pipe consumer; never a native Aether endpoint adapter. */
#include "fd-facade.h"
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <unistd.h>

struct host_io {
    size_t chunk;
    unsigned closes;
};
static int64_t host_error(void)
{
    return errno == EAGAIN || errno == EWOULDBLOCK ? -11 : -(int64_t)errno;
}
static int64_t host_read(void *context, unsigned char *out, size_t count)
{
    struct host_io *host = context;
    if (count > host->chunk)
        count = host->chunk;
    ssize_t moved = read(STDIN_FILENO, out, count);
    return moved < 0 ? host_error() : (int64_t)moved;
}
static int64_t host_write(void *context, const unsigned char *data,
                          size_t count)
{
    struct host_io *host = context;
    if (count > host->chunk)
        count = host->chunk;
    ssize_t moved = write(STDOUT_FILENO, data, count);
    return moved < 0 ? host_error() : (int64_t)moved;
}
static int host_wait(void *context, int writing)
{
    (void)context;
    struct pollfd fd = {.fd = writing ? STDOUT_FILENO : STDIN_FILENO,
                        .events = writing ? POLLOUT : POLLIN};
    int result = poll(&fd, 1, 1000);
    return result == 1 && (fd.revents & (writing ? POLLOUT : POLLIN)) ? 0 : -5;
}
static struct aefd_close_result host_close(void *context)
{
    struct host_io *host = context;
    assert(!host->closes++);
    int input = close(STDIN_FILENO);
    int64_t first = input < 0 ? -(int64_t)errno : 0;
    int output = close(STDOUT_FILENO);
    return (struct aefd_close_result){first, output < 0 ? -(int64_t)errno : 0};
}
static unsigned char workspace[AEFD_READ_MAX], out[AEFD_READ_MAX + 8];
static void untouched(size_t offset)
{
    for (size_t i = offset; i < sizeof out; ++i)
        assert(out[i] == 0xa5);
}
static void happy(struct aefd_client *client)
{
    assert(aefd_file_read(client, 3, out, 2) == -9);
    untouched(0);
    assert(aefd_file_open(client, (const unsigned char *)"missing", 7, 0) ==
           -2);
    assert(aefd_file_open(client, (const unsigned char *)"/", 1, 0) == -22);
    assert(aefd_file_open(client, (const unsigned char *)"file", 4, 1) == 3);
    assert(aefd_file_read(client, 3, out, 2) == 2);
    assert(!memcmp(out, "ab", 2));
    untouched(2);
    assert(aefd_file_dup(client, 3, 4, 0) == 4);
    assert(aefd_file_close(client, 3) == 0);
    assert(aefd_file_read(client, 4, out, 2) == 2);
    assert(!memcmp(out, "cd", 2));
    untouched(2);
    assert(aefd_file_seek(client, 4, -1, 2) == 5);
    assert(aefd_file_read(client, 4, out, 32) == 1 && out[0] == 'f');
    assert(out[1] == 'd');
    untouched(2);
    assert(aefd_file_read(client, 4, out, 32) == 0 && out[0] == 'f');
    assert(aefd_file_set_cloexec(client, 4, 1) == 0);
    assert(aefd_file_close(client, 4) == 0);
    assert(aefd_file_read(client, 4, out, 1) == -9);
    assert(aefd_file_read(client, 4, NULL, 0) == -9);
}
static void local_denials(struct aefd_client *client)
{
    assert(aefd_file_read(client, 0, out, 1) == -22);
    assert(aefd_file_read(client, 16, out, 1) == -22);
    assert(aefd_file_read(client, -1, out, 1) == -22);
    assert(aefd_file_read(client, 3, NULL, 1) == -22);
    assert(aefd_file_read(client, 3, out, AEFD_READ_MAX + 1) == -22);
    assert(aefd_file_seek(client, 3, 0, -1) == -22);
    assert(aefd_file_seek(client, 3, 0, 3) == -22);
    assert(aefd_file_dup(client, 3, 16, 0) == -22);
    assert(aefd_file_dup(client, 3, -1, 0) == -22);
    assert(aefd_file_dup(client, 3, 0, 2) == -22);
    assert(aefd_file_open(client, NULL, 1, 0) == -22);
    assert(aefd_file_open(client, (const unsigned char *)"file", 4, -1) == -22);
    assert(aefd_file_set_cloexec(client, 3, 2) == -22);
    assert(aefd_file_close(client, 0) == -22);
    assert(client->sequence == 1);
    untouched(0);
}
int main(int argc, char **argv)
{
    assert(argc == 2);
    assert(fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK) == 0);
    assert(fcntl(STDOUT_FILENO, F_SETFL, O_NONBLOCK) == 0);
    struct host_io host = {.chunk = !strcmp(argv[1], "bytewise") ? 1 : 7};
    struct aefd_io io = {&host, host_read, host_write, host_wait, host_close};
    struct aefd_client client;
    assert(aefd_client_init(&client, io, workspace, 77));
    memset(out, 0xa5, sizeof out);
    if (!strcmp(argv[1], "happy") || !strcmp(argv[1], "bytewise")) {
        happy(&client);
    } else if (!strcmp(argv[1], "local")) {
        local_denials(&client);
    } else if (!strcmp(argv[1], "header")) {
        assert(aefd_file_open(&client, (const unsigned char *)"file", 4, 0) ==
               -5);
        untouched(0);
        assert(!client.live);
    } else {
        assert(aefd_file_open(&client, (const unsigned char *)"file", 4, 0) ==
               3);
        if (!strcmp(argv[1], "full")) {
            assert(aefd_file_read(&client, 3, out, AEFD_READ_MAX) ==
                   AEFD_READ_MAX);
            for (size_t i = 0; i < AEFD_READ_MAX; ++i)
                assert(out[i] == (unsigned char)('a' + (unsigned)i));
            untouched(AEFD_READ_MAX);
            memset(out, 0xa5, sizeof out);
            assert(aefd_file_read(&client, 3, out, AEFD_READ_MAX) == 907);
            for (size_t i = 0; i < 907; ++i)
                assert(out[i] == (unsigned char)('a' + (unsigned)i));
            untouched(907);
            assert(aefd_file_close(&client, 3) == 0);
        } else if (!strcmp(argv[1], "denied")) {
            assert(aefd_file_read(&client, 3, out, 2) == -13);
            untouched(0);
            assert(client.live);
            assert(aefd_file_read(&client, 3, out, 2) == 2);
            assert(!memcmp(out, "ab", 2));
            untouched(2);
            assert(aefd_file_close(&client, 3) == 0);
        } else if (!strcmp(argv[1], "source-close")) {
            assert(aefd_file_close(&client, 3) == -5);
            assert(!client.live);
            untouched(0);
        } else {
            assert(aefd_file_read(&client, 3, out, 2) == -5);
            untouched(0);
            assert(!client.live);
            assert(aefd_file_read(&client, 3, out, 2) == -5);
        }
    }
    aefd_client_abort(&client);
    assert(!client.workspace && host.closes == 1);
    assert(!client.closed.input && !client.closed.output);
    aefd_client_abort(&client);
    assert(host.closes == 1);
    return 0;
}
