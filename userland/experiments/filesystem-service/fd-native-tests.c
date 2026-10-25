/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-native.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>

struct fixture {
    struct aefd_native n;
    unsigned char request[32], reply[32];
    size_t sent, received, step, read_limit, write_limit;
    unsigned calls, commands, waits, closes, blocks, restores;
    int again, wait_error, oversized, budget, enter_error, restore_error;
    int real, fd[2];
};
static unsigned cases;
static uint32_t get(const unsigned char *b, unsigned i)
{
    return (uint32_t)b[i] | (uint32_t)b[i + 1] << 8 | (uint32_t)b[i + 2] << 16 |
           (uint32_t)b[i + 3] << 24;
}
static void put(unsigned char *b, unsigned i, uint32_t value)
{
    for (unsigned j = 0; j < 4; ++j)
        b[i + j] = (unsigned char)(value >> (8 * j));
}
static void execute(struct fixture *f)
{
    ++f->commands;
    if (!f->real)
        return;
    unsigned op = get(f->request, 0), sel = get(f->request, 8);
    unsigned count = get(f->request, 12);
    assert(count <= 16);
    assert(get(f->request, 4) == (sel == 0 ? 101U : 102U));
    memset(f->reply, 0, 32);
    if (op == 1) {
        assert(sel == 0);
        ssize_t result = read(f->fd[0], f->reply + 16, count);
        assert(result >= 0);
        put(f->reply, 0, (uint32_t)result);
    } else if (op == 2) {
        assert(sel == 1);
        ssize_t result = write(f->fd[1], f->request + 16, count);
        assert(result >= 0);
        put(f->reply, 0, (uint32_t)result);
    } else {
        assert(op == 3 && sel <= 1);
        assert(close(f->fd[sel]) == 0);
        f->fd[sel] = -1;
    }
}
static int64_t call(void *context, uint64_t op, uint64_t cap, uint64_t a,
                    uint64_t b, uint64_t c)
{
    struct fixture *f = context;
    ++f->calls;
    if (op == 0x1000e) {
        assert(c == 8 && a);
        if (cap == 0) {
            ++f->blocks;
            assert(b && *(uint64_t *)(uintptr_t)a == UINT64_MAX);
            *(uint64_t *)(uintptr_t)b = UINT64_C(0x12345);
            return f->enter_error ? -14 : 0;
        }
        assert(cap == 2 && !b);
        assert(*(uint64_t *)(uintptr_t)a == UINT64_C(0x12345));
        ++f->restores;
        return f->restore_error ? -14 : 0;
    }
    if (op == 0x100e7) {
        assert(cap == 125 && f->closes == 2);
        _exit(125);
    }
    if (op == 0x24003) {
        assert(!a && !b && !c && (cap == 71 || cap == 72));
        ++f->closes;
        assert(f->n.retired && f->n.closed);
        return cap == 71 ? -9 : -5;
    }
    assert(f->n.active && f->n.busy && !c);
    assert(aefd_native_enter(&f->n) == -16);
    if (op == 0x24004) {
        assert((cap == 71 || cap == 72) && !a && !b);
        ++f->waits;
        return f->wait_error ? -4 : 0;
    }
    assert((op == 0x24001 && cap == 71) || (op == 0x24002 && cap == 72));
    assert(a && b && b <= 16);
    if (f->oversized)
        return (int64_t)b + 1;
    if (f->budget || f->again) {
        f->again = 0;
        return -11;
    }
    size_t *offset = op == 0x24002 ? &f->sent : &f->received;
    size_t limit = op == 0x24002 ? f->write_limit : f->read_limit;
    if (*offset == limit)
        return 0;
    size_t count = (size_t)b;
    if (count > f->step)
        count = f->step;
    if (count > limit - *offset)
        count = limit - *offset;
    assert(*offset + count <= 32);
    if (op == 0x24002) {
        memcpy(f->request + *offset, (const void *)(uintptr_t)a, count);
        *offset += count;
        if (*offset == 32)
            execute(f);
    } else {
        assert(f->sent == 32);
        memcpy((void *)(uintptr_t)a, f->reply + *offset, count);
        *offset += count;
    }
    return (int64_t)count;
}
static void init(struct fixture *f)
{
    memset(f, 0, sizeof(*f));
    f->step = 16;
    f->read_limit = f->write_limit = 32;
    struct aefd_native_source sources[7] = {{101, 0, 1, 16}, {102, 1, 2, 16}};
    unsigned generations[2] = {0, 0};
    assert(aefd_native_init(&f->n, call, f, 71, 72, sources, generations,
                            0x76050001));
    assert(aefd_native_enter(&f->n) == 0);
}
static void next(struct fixture *f)
{
    f->sent = f->received = 0;
    memset(f->request, 0, 32);
    memset(f->reply, 0, 32);
}
static void finish(struct fixture *f)
{
    aefd_native_leave(&f->n);
    assert(f->blocks == 1 && f->restores == 1 && !f->n.active);
    struct aefd_io io = aefd_native_io(&f->n);
    struct aefd_close_result first = io.close(io.context),
                             second = io.close(io.context);
    assert(first.input == -9 && first.output == -5);
    assert(second.input == first.input && second.output == first.output &&
           f->closes == 2);
    assert(aefd_native_enter(&f->n) == -5);
    ++cases;
}
static struct aefd_stream_result reading(struct fixture *f, unsigned char *out)
{
    struct aefd_adapters adapters = aefd_native_adapters(&f->n);
    return adapters.reader.read(adapters.reader.context, AEFD_BIND_CONSOLE, 0,
                                out, 4096);
}
static void pipe_reply(struct fixture *f, unsigned object, unsigned generation)
{
    put(f->reply, 4, generation);
    put(f->reply, 8, 0x79000001U | object << 16 | generation << 8);
    put(f->reply, 12, 0x79000002U | object << 16 | generation << 8);
    put(f->reply, 16, 3 + object * 2);
    put(f->reply, 20, 4 + object * 2);
    put(f->reply, 24, 256);
    put(f->reply, 28, 16);
}
static void startup_tests(void)
{
    for (unsigned field = 0; field < 10; ++field) {
        struct aefd_native n = {0};
        struct aefd_native_source sources[7] = {{101, 0, 1, 16}};
        unsigned generations[2] = {0, 0};
        uint64_t input = 71, output = 72;
        uint32_t factory = 0x76050001;
        switch (field) {
        case 0:
            input = 0;
            break;
        case 1:
            output = input;
            break;
        case 2:
            sources[0].selector = 1;
            break;
        case 3:
            sources[0].rights = 2;
            break;
        case 4:
            sources[0].bound = 17;
            break;
        case 5:
            sources[1].bound = 16;
            break;
        case 6:
            generations[1] = 10;
            break;
        case 7:
            factory = 1;
            break;
        case 8:
            sources[1] = (struct aefd_native_source){101, 1, 2, 16};
            break;
        default:
            sources[3] = (struct aefd_native_source){0x79000101, 3, 1, 16};
            break;
        }
        assert(!aefd_native_init(&n, call, NULL, input, output, sources,
                                 generations, factory));
        assert(!n.initialized && !n.call);
        ++cases;
    }
    struct fixture f;
    init(&f);
    assert(!aefd_native_init(&f.n, call, &f, 71, 72, f.n.sources,
                             f.n.generations, f.n.factory));
    finish(&f);
}
static void transport_tests(void)
{
    for (unsigned step = 1; step <= 16; ++step) {
        struct fixture f;
        init(&f);
        f.step = step;
        f.again = 1;
        unsigned char out[32];
        memset(out, 0xcc, sizeof(out));
        put(f.reply, 0, 3);
        memcpy(f.reply + 16, "abc", 3);
        struct aefd_stream_result r = reading(&f, out);
        assert(r.complete && r.result == 3 && !memcmp(out, "abc", 3) &&
               out[3] == 0xcc);
        assert(get(f.request, 0) == 1 && get(f.request, 4) == 101 &&
               get(f.request, 8) == 0 && get(f.request, 12) == 16);
        for (unsigned j = 16; j < 32; ++j)
            assert(!f.request[j]);
        assert(f.waits == 1 && f.commands == 1);
        finish(&f);
    }
    for (unsigned direction = 0; direction < 2; ++direction)
        for (unsigned prefix = 0; prefix < 32; ++prefix) {
            struct fixture f;
            init(&f);
            if (direction)
                f.read_limit = prefix;
            else
                f.write_limit = prefix;
            unsigned char out[16];
            memset(out, 0xcc, 16);
            assert(!reading(&f, out).complete && f.n.retired);
            for (unsigned i = 0; i < 16; ++i)
                assert(out[i] == 0xcc);
            assert(f.commands == direction);
            unsigned calls = f.calls;
            assert(!reading(&f, out).complete && f.calls == calls);
            finish(&f);
        }
    for (unsigned bad = 4; bad < 32; ++bad) {
        struct fixture f;
        init(&f);
        f.reply[bad] = 1;
        unsigned char out[16] = {0};
        assert(!reading(&f, out).complete && f.n.retired && !out[0]);
        finish(&f);
    }
    const int results[] = {-4096, -4095, -32, -11, -1, 0, 16, 17};
    for (unsigned i = 0; i < sizeof(results) / sizeof(results[0]); ++i) {
        struct fixture f;
        init(&f);
        put(f.reply, 0, (uint32_t)results[i]);
        unsigned char out[16] = {0};
        struct aefd_stream_result r = reading(&f, out);
        int valid = results[i] >= -4095 && results[i] <= 16;
        assert(r.complete == valid);
        if (valid)
            assert(r.result == results[i] && !f.n.retired);
        finish(&f);
    }
    for (unsigned fault = 0; fault < 3; ++fault) {
        struct fixture f;
        init(&f);
        f.oversized = fault == 0;
        f.again = f.wait_error = fault == 1;
        f.budget = fault == 2;
        unsigned char out[16] = {0};
        assert(!reading(&f, out).complete && f.n.retired && !f.commands);
        if (fault == 2)
            assert(f.waits == AEFD_IO_BUDGET);
        finish(&f);
    }
    struct fixture f;
    init(&f);
    struct aefd_io io = aefd_native_io(&f.n);
    unsigned char bytes[40] = {0};
    assert(io.write(io.context, bytes, sizeof(bytes)) == 16 && f.sent == 16);
    unsigned calls = f.calls;
    assert(io.write(io.context, NULL, 0) == 0 && f.calls == calls);
    aefd_native_leave(&f.n);
    assert(io.write(io.context, bytes, 1) == -5 && f.calls == calls + 1);
    assert(aefd_native_enter(&f.n) == 0);
    f.blocks = 1;
    f.restores = 0;
    finish(&f);
}
static void lifecycle_tests(void)
{
    for (unsigned object = 0; object < 2; ++object)
        for (unsigned gen = 1; gen <= 9; ++gen) {
            struct fixture f;
            init(&f);
            f.n.generations[object] = gen - 1;
            struct aefd_adapters a = aefd_native_adapters(&f.n);
            pipe_reply(&f, object, gen);
            struct aefd_pipe_result p = a.creator.create(a.creator.context);
            unsigned rsel = 3 + object * 2;
            assert(p.complete && !p.status && p.read_selector == rsel &&
                   p.write_selector == rsel + 1);
            assert(get(f.request, 0) == 82 && get(f.request, 4) == 0x76050001 &&
                   get(f.request, 8) == 1);
            assert(f.n.generations[object] == gen &&
                   f.n.sources[rsel].reference);
            for (unsigned i = 12; i < 32; ++i)
                assert(!f.request[i]);
            next(&f);
            struct aefd_stream_close_result c =
                a.closer.close(a.closer.context, AEFD_BIND_PIPE, rsel);
            assert(c.complete && c.consumed && !c.status &&
                   !f.n.sources[rsel].reference);
            assert(f.n.generations[object] == gen);
            next(&f);
            c = a.closer.close(a.closer.context, AEFD_BIND_PIPE, rsel + 1);
            assert(c.complete && c.consumed &&
                   !f.n.sources[rsel + 1].reference);
            next(&f);
            pipe_reply(&f, object, gen);
            assert(!a.creator.create(a.creator.context).complete &&
                   f.n.retired);
            assert(f.n.generations[object] == gen &&
                   !f.n.sources[rsel].reference);
            finish(&f);
        }
    for (unsigned field = 0; field < 32; ++field) {
        struct fixture f;
        init(&f);
        pipe_reply(&f, 0, 1);
        f.reply[field] ^= 0x40;
        struct aefd_adapters a = aefd_native_adapters(&f.n);
        assert(!a.creator.create(a.creator.context).complete && f.n.retired);
        assert(!f.n.sources[3].reference && !f.n.generations[0]);
        finish(&f);
    }
    for (unsigned fault = 0; fault < 5; ++fault) {
        struct fixture f;
        init(&f);
        struct aefd_adapters a = aefd_native_adapters(&f.n);
        if (fault < 2) {
            f.n.factory = 0;
            struct aefd_pipe_result p = a.creator.create(a.creator.context);
            assert(p.complete && p.status == -38 && !f.commands);
            f.n.factory = 0x76050001;
            put(f.reply, 0, (uint32_t)-23);
            if (fault)
                f.reply[31] = 1;
            p = a.creator.create(a.creator.context);
            assert(p.complete == !fault);
            if (!fault)
                assert(p.status == -23 && !f.n.retired);
        } else if (fault == 2) {
            pipe_reply(&f, 0, 1);
            f.n.sources[3] = (struct aefd_native_source){0x79000101, 3, 1, 16};
            assert(!a.creator.create(a.creator.context).complete &&
                   f.n.sources[3].reference);
        } else {
            if (fault == 3)
                put(f.reply, 0, (uint32_t)-5);
            else
                f.read_limit = 31;
            struct aefd_stream_close_result c =
                a.closer.close(a.closer.context, AEFD_BIND_CONSOLE, 1);
            assert(!c.complete && !c.consumed && f.n.retired &&
                   f.n.sources[1].reference == 102);
        }
        finish(&f);
    }
    struct fixture f;
    init(&f);
    struct aefd_adapters a = aefd_native_adapters(&f.n);
    unsigned char out[16] = {0};
    assert(
        !a.reader.read(a.reader.context, AEFD_BIND_FILE, 0, out, 1).complete);
    assert(
        a.reader.read(a.reader.context, AEFD_BIND_CONSOLE, 1, out, 1).result ==
        -9);
    assert(
        a.writer.write(a.writer.context, AEFD_BIND_CONSOLE, 0, out, 1).result ==
        -9);
    assert(!f.commands);
    finish(&f);
}
static void session_test(int lost)
{
    struct fixture f;
    init(&f);
    assert(pipe(f.fd) == 0);
    f.real = 1;
    struct aefd_bindings map = {0};
    struct aefd_client client = {0};
    struct aefd_session session = {0};
    unsigned char raw[128] = {0}, workspace[4096], bytes[32] = {0};
    memcpy(raw, "AEFDT001", 8);
    aefd_put(raw, 1, 31);
    aefd_put(raw, 2, 16);
    raw[64] = raw[68] = AEFD_BIND_CONSOLE;
    raw[69] = 1;
    assert(!aefd_session_init(&session, &map, &client, raw, 128, 31,
                              aefd_native_io(&f.n), workspace,
                              aefd_native_adapters(&f.n)));
    if (lost) {
        f.read_limit = 0;
        assert(aefd_session_write(&session, 1, (const unsigned char *)"effect",
                                  6) == -5);
        assert(f.n.retired && !client.live && f.commands == 1 && f.closes == 2);
        assert(read(f.fd[0], bytes, 6) == 6 && !memcmp(bytes, "effect", 6));
        unsigned calls = f.calls;
        assert(aefd_session_write(&session, 1, bytes, 6) == -5 &&
               f.calls == calls);
        assert(close(f.fd[0]) == 0 && close(f.fd[1]) == 0);
    } else {
        assert(aefd_session_write(&session, 1, (const unsigned char *)"hello",
                                  5) == 5);
        next(&f);
        assert(aefd_session_read(&session, 0, bytes, 32) == 5 &&
               !memcmp(bytes, "hello", 5));
        next(&f);
        assert(aefd_session_dup(&session, 1, 3, 0) == 3);
        assert(aefd_session_close(&session, 1) == 0 && f.commands == 2 &&
               f.fd[1] >= 0);
        assert(aefd_session_close(&session, 3) == 0 && f.fd[1] == -1);
        next(&f);
        assert(aefd_session_read(&session, 0, bytes, 1) == 0);
        next(&f);
        struct aefd_finish r = aefd_session_finish(&session);
        assert(!r.unknown && !r.remaining && f.fd[0] == -1 && f.closes == 2);
    }
    finish(&f);
}
static void session_pipe_test(int exhausted)
{
    struct fixture f;
    init(&f);
    struct aefd_bindings map = {0};
    struct aefd_client client = {0};
    struct aefd_session session = {0};
    unsigned char raw[128] = {0}, snapshot[128] = {0}, workspace[4096];
    memcpy(raw, "AEFDT001", 8);
    aefd_put(raw, 1, 31);
    aefd_put(raw, 2, 16);
    raw[64] = raw[68] = AEFD_BIND_CONSOLE;
    raw[69] = 1;
    assert(!aefd_session_init(&session, &map, &client, raw, 128, 31,
                              aefd_native_io(&f.n), workspace,
                              aefd_native_adapters(&f.n)));
    if (exhausted)
        put(f.reply, 0, (uint32_t)-23);
    else
        pipe_reply(&f, 0, 1);
    int pair[2] = {-99, -98};
    int64_t result = aefd_session_pipe(&session, pair, 1);
    assert(result == (exhausted ? -23 : 0));
    if (exhausted) {
        assert(pair[0] == -99 && pair[1] == -98 && !f.n.generations[0]);
    } else {
        assert(pair[0] == 2 && pair[1] == 3 && f.n.generations[0] == 1);
        assert(aefd_session_dup(&session, pair[0], 5, 0) == 5);
        assert(!aefd_session_snapshot(&session, snapshot, 128, 1));
        assert(!snapshot[72] && !snapshot[76]);
        assert(snapshot[84] == AEFD_BIND_PIPE && snapshot[85] == 3);
        assert(map.slots[2].kind == AEFD_BIND_PIPE && f.commands == 1);
    }
    for (int fd = 0; fd < 16; ++fd)
        if (map.slots[fd].kind) {
            next(&f);
            assert(!aefd_session_close(&session, fd));
        }
    assert(f.commands == (exhausted ? 3U : 5U));
    assert(f.n.generations[0] == (exhausted ? 0U : 1U));
    struct aefd_finish receipt = aefd_session_finish(&session);
    assert(!receipt.unknown && !receipt.remaining && f.closes == 2);
    finish(&f);
}
static void mask_tests(void)
{
    struct fixture f;
    init(&f);
    aefd_native_leave(&f.n);
    f.enter_error = 1;
    assert(aefd_native_enter(&f.n) == -14 && !f.commands && f.n.retired &&
           !f.n.active);
    struct aefd_io io = aefd_native_io(&f.n);
    (void)io.close(io.context);
    assert(f.closes == 2);
    ++cases;
    pid_t pid = fork();
    assert(pid >= 0);
    if (!pid) {
        init(&f);
        f.restore_error = 1;
        aefd_native_leave(&f.n);
        _exit(99);
    }
    int status = 0;
    assert(waitpid(pid, &status, 0) == pid && WIFEXITED(status) &&
           WEXITSTATUS(status) == 125);
    ++cases;
}
int main(void)
{
    startup_tests();
    transport_tests();
    lifecycle_tests();
    session_test(0);
    session_test(1);
    session_pipe_test(0);
    session_pipe_test(1);
    mask_tests();
    printf("%u native-call adapter host scenarios pass\n", cases);
    return 0;
}
