/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-facade.h"

static int64_t invoke(struct aefd_client *client, uint64_t opcode,
                      const uint64_t args[4], const unsigned char *name,
                      size_t length)
{
    struct aefd_reply reply;
    int completed =
        aefd_client_exchange(client, opcode, args, name, length, &reply);
    if (completed != 1)
        return completed == 0 ? -22 : -5;
    if (reply.status)
        return reply.status;
    return (int64_t)reply.result;
}

int64_t aefd_file_open(struct aefd_client *client, const unsigned char *name,
                       size_t length, int cloexec)
{
    const uint64_t args[4] = {(uint64_t)cloexec, length, 0, 0};
    return invoke(client, 1, args, name, length);
}

int64_t aefd_file_read(struct aefd_client *client, int fd, unsigned char *out,
                       size_t count)
{
    if ((count && !out) || count > AEFD_READ_MAX)
        return -22;
    const uint64_t args[4] = {(uint64_t)fd, count, 0, 0};
    int64_t result = invoke(client, 2, args, NULL, 0);
    /* Never expose partially received bytes or overwrite bytes beyond count. */
    if (result > 0)
        memcpy(out, client->workspace, (size_t)result);
    return result;
}

int64_t aefd_file_seek(struct aefd_client *client, int fd, int64_t delta,
                       int whence)
{
    const uint64_t args[4] = {(uint64_t)fd, (uint64_t)delta, (uint64_t)whence,
                              0};
    return invoke(client, 3, args, NULL, 0);
}

int64_t aefd_file_dup(struct aefd_client *client, int fd, int minimum,
                      int cloexec)
{
    const uint64_t args[4] = {(uint64_t)fd, (uint64_t)minimum,
                              (uint64_t)cloexec, 0};
    return invoke(client, 4, args, NULL, 0);
}

int64_t aefd_file_close(struct aefd_client *client, int fd)
{
    const uint64_t args[4] = {(uint64_t)fd, 0, 0, 0};
    return invoke(client, 5, args, NULL, 0);
}

int64_t aefd_file_set_cloexec(struct aefd_client *client, int fd, int cloexec)
{
    const uint64_t args[4] = {(uint64_t)fd, (uint64_t)cloexec, 0, 0};
    return invoke(client, 6, args, NULL, 0);
}

#ifdef AEFD_DUP2_WIRE
int64_t aefd_file_replace(struct aefd_client *client, int source, int target)
{
    const uint64_t args[4] = {(uint64_t)source, (uint64_t)target, 0, 0};
    return invoke(client, 7, args, NULL, 0);
}
#endif

#ifdef AEFD_WRITE_WIRE
int64_t aefd_file_open_home(struct aefd_client *client,
                            const unsigned char *name, size_t length,
                            int access, int cloexec)
{
    const uint64_t args[4] = {(uint64_t)cloexec, length, (uint64_t)access, 0};
    return invoke(client, 10, args, name, length);
}
int64_t aefd_file_write(struct aefd_client *client, int fd,
                        const unsigned char *bytes, size_t count,
                        struct aefd_write_result *out)
{
    if (!out)
        return -22;
    int result = aefd_client_write(client, fd, bytes, count, out);
    if (result != 1 || out->status)
        return out->status;
    return (int64_t)out->remote.count;
}
#endif
