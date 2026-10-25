/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-client.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

struct script {
    unsigned char input[8192];
    unsigned char output[8192];
    size_t length, received, sent, stop_in, stop_out, chunk;
    unsigned reads, writes, waits, closes;
    int again, blocked, last_direction, fail_wait, always_again;
    int oversized, zero_write, read_error;
};
static unsigned char requests[704], replies[832], workspace[AEFD_READ_MAX];
static unsigned scenarios;

static void zeroes(const unsigned char *data, size_t length)
{
    for (size_t i = 0; i < length; ++i)
        assert(!data[i]);
}
static int64_t scripted_read(void *context, unsigned char *out, size_t length)
{
    struct script *script = context;
    assert(length && length <= AEFD_FRAME);
    ++script->reads;
    if (script->oversized)
        return (int64_t)length + 1;
    if (script->always_again || (script->again && !script->blocked)) {
        script->blocked = 1;
        script->last_direction = 0;
        return -11;
    }
    script->blocked = 0;
    if (script->received == script->stop_in)
        return script->read_error ? -5 : 0;
    assert(script->received < script->length);
    size_t count = script->length - script->received;
    if (count > length)
        count = length;
    if (count > script->chunk)
        count = script->chunk;
    if (count > script->stop_in - script->received)
        count = script->stop_in - script->received;
    memcpy(out, script->input + script->received, count);
    script->received += count;
    return (int64_t)count;
}
static int64_t scripted_write(void *context, const unsigned char *data,
                              size_t length)
{
    struct script *script = context;
    assert(length && length <= AEFD_FRAME);
    ++script->writes;
    if (script->oversized == 1)
        return (int64_t)length + 1;
    if (script->always_again == 1 || (script->again && !script->blocked)) {
        script->blocked = 1;
        script->last_direction = 1;
        return -11;
    }
    script->blocked = 0;
    if (script->sent == script->stop_out)
        return script->zero_write ? 0 : -5;
    size_t count = length < script->chunk ? length : script->chunk;
    if (count > script->stop_out - script->sent)
        count = script->stop_out - script->sent;
    assert(script->sent + count <= sizeof script->output);
    memcpy(script->output + script->sent, data, count);
    script->sent += count;
    return (int64_t)count;
}
static int scripted_wait(void *context, int writing)
{
    struct script *script = context;
    assert(script->blocked && writing == script->last_direction);
    ++script->waits;
    return script->fail_wait && (script->fail_wait == 1 || !writing) ? -5 : 0;
}
static struct aefd_close_result scripted_close(void *context)
{
    struct script *script = context;
    ++script->closes;
    return (struct aefd_close_result){-5, -9};
}
static struct aefd_client connect(struct script *script)
{
    struct aefd_client client;
    struct aefd_io io = {script, scripted_read, scripted_write, scripted_wait,
                         scripted_close};
    assert(aefd_client_init(&client, io, workspace, aefd_word(requests, 2)));
    zeroes(workspace, sizeof workspace);
    return client;
}
static struct script initial(void)
{
    struct script script = {.length = sizeof replies,
                            .stop_in = SIZE_MAX,
                            .stop_out = SIZE_MAX,
                            .chunk = 64};
    memcpy(script.input, replies, sizeof replies);
    return script;
}
static void retired(struct aefd_client *client, struct script *script)
{
    assert(!client->live && !client->workspace && script->closes == 1);
    assert(client->closed.input == -5 && client->closed.output == -9);
    zeroes(workspace, sizeof workspace);
    unsigned reads = script->reads, writes = script->writes;
    uint64_t args[4] = {3, 1, 0, 0};
    struct aefd_reply out = {123, 456, 789};
    assert(aefd_client_exchange(client, 2, args, NULL, 0, &out) == -1);
    aefd_client_abort(client);
    assert(script->closes == 1 && script->reads == reads &&
           script->writes == writes);
    assert(out.status == 123 && out.result == 456 && out.body == 789);
}
static void conversation(struct script *script, int expect_failure)
{
    ++scenarios;
    struct aefd_client client = connect(script);
    size_t offset = 0;
    const uint64_t results[10] = {3, 2, 4, 0, 2, 5, 1, 0, 0, 0};
    for (unsigned i = 0; i < 10; ++i) {
        const unsigned char *request = requests + offset;
        uint64_t opcode = aefd_word(request, 1), args[4];
        for (unsigned j = 0; j < 4; ++j)
            args[j] = aefd_word(request, j + 4U);
        size_t length = opcode == 1 ? (size_t)args[1] : 0;
        struct aefd_reply reply = {123, 456, 789};
        int result =
            aefd_client_exchange(&client, opcode, args,
                                 length ? request + 64 : NULL, length, &reply);
        offset += 64 + ((length + 63U) / 64U) * 64U;
        if (result == -1) {
            assert(expect_failure);
            assert(reply.status == 123 && reply.result == 456 &&
                   reply.body == 789);
            assert(script->sent <= sizeof requests);
            assert(!memcmp(script->output, requests, script->sent));
            retired(&client, script);
            return;
        }
        assert(result == 1 && client.sequence == (uint64_t)i + 2);
        assert(reply.status == (i == 9 ? -38 : 0) &&
               reply.result == results[i]);
        size_t count = 0;
        const char *data = "";
        if (i == 1) {
            count = 2;
            data = "ab";
        } else if (i == 4) {
            count = 2;
            data = "cd";
        } else if (i == 6) {
            count = 1;
            data = "f";
        }
        assert(reply.body == count && !memcmp(workspace, data, count));
        zeroes(workspace + count, sizeof workspace - count);
    }
    assert(!expect_failure && script->sent == sizeof requests &&
           script->received == sizeof replies);
    assert(!memcmp(script->output, requests, sizeof requests));
    aefd_client_abort(&client);
    retired(&client, script);
}
static void local_denials(void)
{
    struct script script = initial();
    struct aefd_client client = connect(&script);
    struct aefd_reply reply = {123, 456, 789};
    const uint64_t bad[][5] = {
        {1, 2, 1, 0, 0},  {1, 0, 0, 0, 0},  {1, 0, 256, 0, 0},
        {2, 2, 1, 0, 0},  {2, 16, 1, 0, 0}, {2, 3, 4097, 0, 0},
        {2, 3, 1, 1, 0},  {3, 3, 0, 3, 0},  {4, 3, 16, 0, 0},
        {4, 3, 0, 2, 0},  {5, 3, 1, 0, 0},  {6, 3, 2, 0, 0},
        {99, 1, 0, 0, 0}, {2, 3, 1, 0, 1}};
    for (size_t i = 0; i < sizeof bad / sizeof bad[0]; ++i) {
        memset(workspace, 0xa5, sizeof workspace);
        uint64_t op = bad[i][0];
        size_t length = op == 1 ? (size_t)bad[i][2] : 0;
        assert(aefd_client_exchange(&client, op, bad[i] + 1,
                                    length ? (const unsigned char *)"x" : NULL,
                                    length, &reply) == 0);
        zeroes(workspace, sizeof workspace);
    }
    uint64_t open_args[4] = {0, 1, 0, 0};
    assert(aefd_client_exchange(&client, 1, open_args,
                                (const unsigned char *)"/", 1, &reply) == 0);
    assert(aefd_client_exchange(&client, 1, open_args, NULL, 1, &reply) == 0);
    assert(aefd_client_exchange(&client, 1, NULL, NULL, 0, &reply) == 0);
    assert(aefd_client_exchange(&client, 1, open_args, NULL, 1, NULL) == 0);
    assert(!script.reads && !script.writes && !script.waits && !script.closes);
    assert(client.sequence == 1 && reply.status == 123 && reply.result == 456 &&
           reply.body == 789);
    aefd_client_abort(&client);
    retired(&client, &script);
    ++scenarios;
}
static void full_and_exhausted(void)
{
    struct script script = initial();
    struct aefd_client client = connect(&script);
    /* Full read at last usable sequence, followed by permanent exhaustion. */
    client.sequence = UINT64_MAX - 1;
    memset(script.input, 0, sizeof script.input);
    memcpy(script.input, "AEFD0001", 8);
    aefd_put(script.input, 2, client.generation);
    aefd_put(script.input, 3, client.sequence);
    aefd_put(script.input, 4, AEFD_READ_MAX);
    aefd_put(script.input, 5, AEFD_READ_MAX);
    script.length = 64 + AEFD_READ_MAX;
    for (size_t i = 0; i < AEFD_READ_MAX; ++i)
        script.input[64 + i] = (unsigned char)i;
    script.chunk = 1;
    script.again = 1;
    uint64_t args[4] = {3, AEFD_READ_MAX, 0, 0};
    struct aefd_reply reply;
    assert(aefd_client_exchange(&client, 2, args, NULL, 0, &reply) == 1);
    assert(reply.status == 0 && reply.result == AEFD_READ_MAX &&
           client.sequence == UINT64_MAX);
    for (size_t i = 0; i < AEFD_READ_MAX; ++i)
        assert(workspace[i] == (unsigned char)i);
    unsigned reads = script.reads, writes = script.writes;
    assert(aefd_client_exchange(&client, 2, args, NULL, 0, &reply) == -1);
    assert(script.reads == reads && script.writes == writes);
    retired(&client, &script);
    ++scenarios;
}
static void semantic_continuation(void)
{
    struct script script = initial();
    struct aefd_client client = connect(&script);
    memset(script.input, 0, sizeof script.input);
    for (unsigned i = 0; i < 2; ++i) {
        unsigned char *header = script.input + i * 64U;
        memcpy(header, "AEFD0001", 8);
        aefd_put(header, 2, client.generation);
        aefd_put(header, 3, i + 1U);
    }
    aefd_put(script.input, 1, (uint64_t)-INT64_C(9));
    script.length = 128;
    uint64_t args[4] = {3, 1, 0, 0};
    struct aefd_reply reply;
    assert(aefd_client_exchange(&client, 2, args, NULL, 0, &reply) == 1);
    assert(reply.status == -9 && !reply.result && !reply.body && client.live);
    zeroes(workspace, sizeof workspace);
    assert(aefd_client_exchange(&client, 2, args, NULL, 0, &reply) == 1);
    assert(!reply.status && !reply.result && !reply.body &&
           client.sequence == 3);
    zeroes(workspace, sizeof workspace);
    aefd_client_abort(&client);
    retired(&client, &script);
    ++scenarios;
}
static void maximum_component(void)
{
    for (size_t chunk = 1; chunk <= 64; chunk += 63) {
        struct script script = initial();
        script.chunk = chunk;
        struct aefd_client client = connect(&script);
        unsigned char name[255];
        memset(name, 'x', sizeof name);
        uint64_t args[4] = {1, sizeof name, 0, 0};
        struct aefd_reply reply;
        assert(aefd_client_exchange(&client, 1, args, name, sizeof name,
                                    &reply) == 1);
        assert(!reply.status && reply.result == 3 && !reply.body);
        assert(script.sent == 320 && script.received == 64);
        assert(aefd_word(script.output, 4) == 1 &&
               aefd_word(script.output, 5) == 255);
        assert(!memcmp(script.output + 64, name, sizeof name));
        assert(script.output[319] == 0);
        zeroes(workspace, sizeof workspace);
        aefd_client_abort(&client);
        retired(&client, &script);
        ++scenarios;
    }
}
static void initialization_denials(void)
{
    struct script script = initial();
    struct aefd_client client = {0};
    struct aefd_io io = {&script, scripted_read, scripted_write, scripted_wait,
                         scripted_close};
    struct aefd_io missing = io;
    memset(workspace, 0xa5, sizeof workspace);
    missing.read = NULL;
    assert(!aefd_client_init(&client, missing, workspace, 1));
    missing = io;
    missing.write = NULL;
    assert(!aefd_client_init(&client, missing, workspace, 1));
    missing = io;
    missing.wait = NULL;
    assert(!aefd_client_init(&client, missing, workspace, 1));
    missing = io;
    missing.close = NULL;
    assert(!aefd_client_init(&client, missing, workspace, 1));
    assert(!aefd_client_init(NULL, io, workspace, 1));
    assert(!aefd_client_init(&client, io, NULL, 1));
    assert(!aefd_client_init(&client, io, workspace, 0));
    assert(!client.live && !client.workspace && !script.closes);
    for (size_t i = 0; i < sizeof workspace; ++i)
        assert(workspace[i] == 0xa5);
    aefd_client_abort(&client);
    assert(!script.closes);
    ++scenarios;
}
static void load(const char *path, unsigned char *out, size_t length)
{
    FILE *file = fopen(path, "rb");
    assert(file && fread(out, 1, length, file) == length);
    assert(fgetc(file) == EOF && !ferror(file));
    assert(!fclose(file));
}
int main(int argc, char **argv)
{
    assert(argc == 3);
    load(argv[1], requests, sizeof requests);
    load(argv[2], replies, sizeof replies);
    for (size_t chunk = 1; chunk <= 64; ++chunk) {
        struct script script = initial();
        script.chunk = chunk;
        script.again = (int)(chunk % 2);
        conversation(&script, 0);
    }
    for (size_t prefix = 0; prefix < sizeof replies; ++prefix) {
        struct script script = initial();
        script.stop_in = prefix;
        script.chunk = 7;
        conversation(&script, 1);
    }
    for (size_t prefix = 0; prefix < sizeof requests; ++prefix) {
        struct script script = initial();
        script.stop_out = prefix;
        script.chunk = 7;
        conversation(&script, 1);
    }
    const size_t corrupt[] = {0,  8,  16, 24,  32,  40,  48,  56,
                              64, 80, 88, 104, 112, 120, 130, 191};
    for (size_t i = 0; i < sizeof corrupt / sizeof corrupt[0]; ++i) {
        struct script script = initial();
        script.input[corrupt[i]] ^= 0x40;
        conversation(&script, 1);
    }
    for (unsigned mode = 0; mode < 9; ++mode) {
        struct script script = initial();
        script.again = 1;
        if (mode == 0)
            script.fail_wait = 1;
        if (mode == 1)
            script.always_again = 1;
        if (mode == 2)
            script.oversized = 1;
        if (mode == 3) {
            script.stop_out = 0;
            script.zero_write = 1;
        }
        if (mode == 4) {
            script.stop_in = 65;
            script.read_error = 1;
        }
        if (mode == 5) {
            script.stop_in = 64;
            script.fail_wait = 2;
        }
        if (mode == 6) {
            script.stop_in = 0;
            script.read_error = 1;
        }
        if (mode == 7)
            script.oversized = 2;
        if (mode == 8)
            script.always_again = 2;
        conversation(&script, 1);
        if (script.always_again)
            assert(script.reads + script.writes == AEFD_IO_BUDGET);
    }
    local_denials();
    full_and_exhausted();
    semantic_continuation();
    maximum_component();
    initialization_denials();
    printf("%u C client schedules pass\n", scenarios);
    return 0;
}
