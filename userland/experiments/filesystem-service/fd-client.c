/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-client.h"

int aefd_client_init(struct aefd_client *client, struct aefd_io io,
                     unsigned char workspace[AEFD_READ_MAX],
                     uint64_t generation)
{
    if (!client || !workspace || !generation || !io.read || !io.write ||
        !io.wait || !io.close)
        return 0;
    *client = (struct aefd_client){.io = io,
                                   .workspace = workspace,
                                   .generation = generation,
                                   .sequence = 1,
                                   .live = 1};
    memset(workspace, 0, AEFD_READ_MAX);
    return 1;
}

void aefd_client_abort(struct aefd_client *client)
{
    if (!client)
        return;
    if (client->workspace) {
        memset(client->workspace, 0, AEFD_READ_MAX);
        client->workspace = NULL;
    }
    if (client->live) {
        /* Consume the local obligation before calling external cleanup. */
        client->live = 0;
        client->closed = client->io.close(client->io.context);
    }
}

static int transfer(struct aefd_client *client, unsigned char *bytes,
                    size_t length, int writing, unsigned *budget)
{
    size_t offset = 0;
    while (offset < length) {
        if (!*budget)
            return 0;
        --*budget;
        size_t count = length - offset;
        if (count > AEFD_FRAME)
            count = AEFD_FRAME;
        int64_t moved =
            writing
                ? client->io.write(client->io.context, bytes + offset, count)
                : client->io.read(client->io.context, bytes + offset, count);
        if (moved == -11) {
            if (client->io.wait(client->io.context, writing))
                return 0;
            continue;
        }
        if (moved <= 0 || (uint64_t)moved > count)
            return 0;
        offset += (size_t)moved;
    }
    return 1;
}

static int shape(uint64_t opcode, const uint64_t args[4], size_t name_length)
{
    if (args[3])
        return 0;
#ifdef AEFD_WRITE_WIRE
    if (opcode == 11)
        return 0; /* The typed entry must retain its mutation receipt. */
    if (opcode == 10)
        return args[0] <= 1 && args[1] == name_length && name_length >= 1 &&
               name_length <= 255 && args[2] <= 2;
#endif
    if (opcode == 1
#ifdef AEFD_CWD_WIRE
        || opcode == 8
#endif
    )
        return args[0] <= (opcode == 1 ? 1U : 0U) && args[1] == name_length &&
               name_length >= 1 && name_length <= 255 && !args[2];
    if (name_length)
        return 0;
#ifdef AEFD_DUP2_WIRE
    if (opcode == 7)
        return args[0] < 16 && args[1] < 16 && !args[2];
#endif
    if (opcode < 2 || opcode > 6)
        return !args[0] && !args[1] && !args[2];
    if (!aefd_file_selector(args[0]))
        return 0;
    switch (opcode) {
    case 2:
        return args[1] <= AEFD_READ_MAX && !args[2];
    case 3:
        return args[2] <= 2;
    case 4:
        return args[1] < 16 && args[2] <= 1;
    case 5:
        return !args[1] && !args[2];
    case 6:
        return args[1] <= 1 && !args[2];
    default:
        return 0;
    }
}

static int stage_name(unsigned char out[256], uint64_t opcode,
                      const unsigned char *name, size_t length)
{
#ifdef AEFD_WRITE_WIRE
    if (opcode == 10)
        return aefd_home_name(out, name, length);
#else
    (void)opcode;
#endif
    return aefd_name(out, name, length);
}

int aefd_client_exchange(struct aefd_client *client, uint64_t opcode,
                         const uint64_t args[4], const unsigned char *name,
                         size_t name_length, struct aefd_reply *out)
{
    if (!client)
        return 0;
    if (!client->live || client->sequence == UINT64_MAX) {
        aefd_client_abort(client);
        return -1;
    }
    int path_call = opcode == 1;
#ifdef AEFD_WRITE_WIRE
    path_call = path_call || opcode == 10;
#endif
#ifdef AEFD_CWD_WIRE
    path_call = path_call || opcode == 8;
#endif
    memset(client->workspace, 0, AEFD_READ_MAX);
    if (!args || !out || !shape(opcode, args, name_length) ||
        (!path_call && name) ||
        (path_call &&
         !stage_name(client->workspace, opcode, name, name_length)))
        return 0;
    unsigned char frame[AEFD_FRAME];
    if (!aefd_request(frame, client->generation, client->sequence, opcode,
                      args)) {
        aefd_client_abort(client);
        return -1;
    }
    unsigned budget = AEFD_IO_BUDGET;
    size_t outgoing = ((name_length + 63U) / 64U) * 64U;
    struct aefd_reply reply;
    if (!transfer(client, frame, sizeof frame, 1, &budget) ||
        !transfer(client, client->workspace, outgoing, 1, &budget))
        goto retired;
    memset(client->workspace, 0, AEFD_READ_MAX);
    if (!transfer(client, frame, sizeof frame, 0, &budget) ||
        !aefd_decode(frame, sizeof frame, client->generation, client->sequence,
                     opcode, opcode == 2 ? (size_t)args[1] : 0, &reply))
        goto retired;
#ifdef AEFD_DUP2_WIRE
    if (opcode == 7 && !reply.status && reply.result != args[1])
        goto retired;
#endif
    size_t incoming = ((reply.body + 63U) / 64U) * 64U;
    if (!transfer(client, client->workspace, incoming, 0, &budget) ||
        !aefd_body(client->workspace, client->workspace, incoming, reply.body))
        goto retired;
#ifdef AEFD_CWD_WIRE
    if (opcode == 9 && !reply.status) {
        size_t length = reply.body;
        if (client->workspace[0] != '/' || client->workspace[length - 1])
            goto retired;
        size_t start = 1;
        for (size_t i = 1; i < length; ++i) {
            if (i + 1 < length && !client->workspace[i])
                goto retired;
            if (i + 1 == length || client->workspace[i] == '/') {
                size_t n = i - start;
                if ((!n && length != 2) ||
                    (n == 1 && client->workspace[start] == '.') ||
                    (n == 2 && client->workspace[start] == '.' &&
                     client->workspace[start + 1] == '.'))
                    goto retired;
                start = i + 1;
            }
        }
    }
#endif
    ++client->sequence;
    *out = reply;
    return 1;
retired:
    aefd_client_abort(client);
    return -1;
}

#ifdef AEFD_WRITE_WIRE
int aefd_client_write(struct aefd_client *client, int fd,
                      const unsigned char *bytes, size_t count,
                      struct aefd_write_result *out)
{
    if (!out)
        return 0;
    struct aefd_write_result result = {.observation = AEFD_WRITE_NOT_SENT,
                                       .status = -22,
                                       .fd = fd,
                                       .requested = count};
    if (!client) {
        *out = result;
        return 0;
    }
    result.generation = client->generation;
    result.sequence = client->sequence;
    if (!client->live || client->sequence == UINT64_MAX) {
        aefd_client_abort(client);
        result.status = -5;
        result.file_closed = 1;
        result.file_cleanup = client->closed;
        *out = result;
        return -1;
    }
    memset(client->workspace, 0, AEFD_READ_MAX);
    if (!aefd_file_selector((uint64_t)fd) || !bytes || !count ||
        count > AEFD_READ_MAX) {
        *out = result;
        return 0;
    }
    memcpy(client->workspace, bytes, count);
    unsigned char frame[AEFD_FRAME];
    const uint64_t args[4] = {(uint64_t)fd, count, 0, 0};
    if (!aefd_request(frame, client->generation, client->sequence, 11, args)) {
        memset(client->workspace, 0, AEFD_READ_MAX);
        *out = result;
        return 0;
    }
    unsigned budget = AEFD_IO_BUDGET;
    result.observation = AEFD_WRITE_UNKNOWN;
    result.status = -5;
    if (!transfer(client, frame, 64, 1, &budget) ||
        !transfer(client, client->workspace, ((count + 63U) / 64U) * 64U, 1,
                  &budget))
        goto failed_write;
    memset(client->workspace, 0, AEFD_READ_MAX);
    if (!transfer(client, frame, 64, 0, &budget) ||
        !transfer(client, client->workspace, 64, 0, &budget) ||
        !aefd_write_decode(frame, client->workspace, 64, client->generation,
                           client->sequence, count, &result.remote))
        goto failed_write;
    result.observation = AEFD_WRITE_REMOTE;
    result.status = result.remote.status;
    ++client->sequence;
    memset(client->workspace, 0, AEFD_READ_MAX);
    if (result.remote.flags & 16U) {
        aefd_client_abort(client);
        result.file_closed = 1;
        result.file_cleanup = client->closed;
    }
    *out = result;
    return 1;
failed_write:
    aefd_client_abort(client);
    result.file_closed = 1;
    result.file_cleanup = client->closed;
    *out = result;
    return -1;
}
#endif
