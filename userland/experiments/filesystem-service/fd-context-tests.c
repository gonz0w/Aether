/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-context.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>

struct step {
    unsigned char request[320], reply[128];
    size_t request_size, reply_size, received, sent;
    int effect;
};
struct fixture {
    struct aefd_context c;
    struct step steps[8];
    unsigned count, current, blocks, restores, closes, calls;
    uint64_t sequence;
    int mask_error, restore_error, fd[2];
};
static unsigned cases;
static void put(unsigned char *bytes, unsigned i, uint32_t value)
{
    for (unsigned j = 0; j < 4; ++j)
        bytes[i + j] = (unsigned char)(value >> (8 * j));
}
static int64_t call(void *context, uint64_t op, uint64_t cap, uint64_t a,
                    uint64_t b, uint64_t tail)
{
    struct fixture *f = context;
    ++f->calls;
    if (op == 0x1000e) {
        assert(tail == 8 && a);
        if (!cap) {
            assert(b && *(uint64_t *)(uintptr_t)a == UINT64_MAX);
            ++f->blocks;
            *(uint64_t *)(uintptr_t)b = 0x4321;
            return f->mask_error ? -14 : 0;
        }
        assert(cap == 2 && !b && *(uint64_t *)(uintptr_t)a == 0x4321);
        ++f->restores;
        return f->restore_error ? -14 : 0;
    }
    if (op == 0x24003) {
        assert(!a && !b && !tail && (cap == 71 || cap == 72));
        assert(f->c.native.retired);
        ++f->closes;
        return cap == 71 ? -9 : -5;
    }
    if (op == 0x100e7) {
        assert(cap == 125 && f->closes == 2);
        _exit(125);
    }
    assert(f->c.native.active && f->c.native.busy);
    assert(f->blocks == f->restores + 1 && !tail && a && b && b <= 16);
    if (f->current == f->count) {
        assert(op == 0x24001 && cap == 71);
        return 0;
    }
    assert(f->current < f->count);
    struct step *s = &f->steps[f->current];
    if (op == 0x24002) {
        assert(cap == 72 && s->received + b <= s->request_size && !s->sent);
        assert(
            !memcmp((void *)(uintptr_t)a, s->request + s->received, (size_t)b));
        s->received += (size_t)b;
        if (s->received == s->request_size && s->effect) {
            if (s->effect == 1)
                assert(write(f->fd[1], "hello", 5) == 5);
            else {
                assert(s->effect == 2 && close(f->fd[1]) == 0);
                f->fd[1] = -1;
            }
        }
        return (int64_t)b;
    }
    assert(op == 0x24001 && cap == 71 && s->received == s->request_size);
    size_t count = (size_t)b;
    if (count > s->reply_size - s->sent)
        count = s->reply_size - s->sent;
    memcpy((void *)(uintptr_t)a, s->reply + s->sent, count);
    s->sent += count;
    if (count && s->sent == s->reply_size)
        ++f->current;
    return (int64_t)count;
}
static void raw_init(unsigned char raw[128])
{
    memset(raw, 0, 128);
    memcpy(raw, "AEFDT001", 8);
    aefd_put(raw, 1, 31);
    aefd_put(raw, 2, 16);
}
static void admit(struct fixture *f, unsigned char raw[128],
                  struct aefd_native_source sources[7], unsigned history[2])
{
    assert(!aefd_context_init(&f->c, call, f, 71, 72, raw, 128, 31, sources,
                              history, 0x76050001));
    assert(f->c.client.workspace == f->c.workspace);
    assert(f->c.session.map == &f->c.map &&
           f->c.session.client == &f->c.client);
    assert(f->c.client.io.context == &f->c.native && !f->calls);
}
static void init(struct fixture *f, int kind)
{
    memset(f, 0, sizeof(*f));
    unsigned char raw[128];
    struct aefd_native_source sources[7] = {0};
    unsigned history[2] = {0};
    raw_init(raw);
    if (kind == 1) {
        raw[68] = AEFD_BIND_CONSOLE;
        raw[69] = 1;
        sources[1] = (struct aefd_native_source){102, 1, 2, 16};
    } else if (kind >= 2) {
        raw[80] = AEFD_BIND_FILE;
        raw[81] = 3;
        raw[82] = 1;
    }
    if (kind == 3) {
        raw[68] = AEFD_BIND_CONSOLE;
        raw[69] = 1;
        raw[70] = 1;
        sources[1] = (struct aefd_native_source){102, 1, 2, 16};
    } else if (kind == 4) {
        raw[68] = AEFD_BIND_FILE;
        raw[69] = 5;
        raw[70] = 1;
    }
    admit(f, raw, sources, history);
}
static struct step *new_step(struct fixture *f)
{
    assert(f->count < 8);
    return &f->steps[f->count++];
}
static struct step *rpc(struct fixture *f, unsigned opcode, uint64_t a,
                        uint64_t b, uint64_t c, int64_t status, uint64_t result)
{
    struct step *s = new_step(f);
    uint64_t args[4] = {a, b, c, 0};
    assert(aefd_request(s->request, 31, ++f->sequence, opcode, args));
    s->request_size = 64;
    s->reply_size = 64;
    memcpy(s->reply, "AEFD0001", 8);
    aefd_put(s->reply, 1, (uint64_t)status);
    aefd_put(s->reply, 2, 31);
    aefd_put(s->reply, 3, f->sequence);
    aefd_put(s->reply, 4, result);
    return s;
}
static struct step *control(struct fixture *f, unsigned op, uint32_t ref,
                            unsigned selector, unsigned count, int result)
{
    struct step *s = new_step(f);
    s->request_size = s->reply_size = 32;
    put(s->request, 0, op);
    put(s->request, 4, ref);
    put(s->request, 8, selector);
    put(s->request, 12, count);
    put(s->reply, 0, (uint32_t)result);
    return s;
}
static void done(struct fixture *f)
{
    assert(!f->c.native.active && f->blocks == f->restores);
    ++cases;
}
static void startup_tests(void)
{
    for (unsigned selector = 0; selector < 7; ++selector)
        for (unsigned mode = 0; mode < 4; ++mode) {
            struct fixture f = {0};
            unsigned char raw[128];
            struct aefd_native_source sources[7] = {0};
            unsigned history[2] = {0};
            raw_init(raw);
            unsigned kind = selector < 3 ? AEFD_BIND_CONSOLE : AEFD_BIND_PIPE;
            raw[64] = (unsigned char)kind;
            raw[65] = (unsigned char)selector;
            unsigned rights =
                selector == 0 || selector == 3 || selector == 5 ? 1U : 2U;
            uint32_t ref = selector < 3
                               ? 100 + selector
                               : 0x79000100U | ((selector - 3) / 2) << 16 |
                                     ((selector - 3) % 2 + 1);
            if (selector >= 3)
                history[(selector - 3) / 2] = 1;
            sources[selector] =
                (struct aefd_native_source){ref, selector, rights, 16};
            if (mode == 1)
                memset(&sources[selector], 0, sizeof(sources[selector]));
            if (mode == 2)
                memset(raw + 64, 0, 4);
            if (mode == 3) {
                raw[68] = AEFD_BIND_FILE;
                raw[69] = 3;
                raw[72] = (unsigned char)kind;
                raw[73] = (unsigned char)selector;
            }
            int64_t result = aefd_context_init(&f.c, call, &f, 71, 72, raw, 128,
                                               31, sources, history, 0);
            if (mode == 1 || mode == 2) {
                assert(result == -22 && !f.c.state && !f.c.native.initialized &&
                       !f.calls);
                assert(!f.c.client.workspace && !f.c.map.generation);
            } else {
                assert(result == 0 && f.c.state == 1 && !f.calls);
                assert(aefd_context_init(&f.c, call, &f, 71, 72, raw, 128, 31,
                                         sources, history, 0) == -16);
                assert(!f.calls);
            }
            done(&f);
        }
    for (unsigned mode = 0; mode < 8; ++mode) {
        struct fixture f = {0};
        unsigned char raw[128];
        raw_init(raw);
        struct aefd_native_source sources[7] = {0};
        unsigned history[2] = {0};
        uint64_t input = 71, gen = 31;
        size_t length = 128;
        switch (mode) {
        case 0:
            raw[0] ^= 1;
            break;
        case 1:
            gen = 32;
            break;
        case 2:
            length = 64;
            break;
        case 3:
            input = 72;
            break;
        case 4:
            history[1] = 10;
            break;
        case 5:
            raw[64] = AEFD_BIND_PIPE;
            raw[65] = 2;
            break;
        case 6:
            raw[64] = raw[68] = AEFD_BIND_FILE;
            raw[65] = raw[69] = 3;
            break;
        default:
            raw[127] = 1;
            break;
        }
        assert(aefd_context_init(&f.c, call, &f, input, 72, raw, length, gen,
                                 sources, history, 0) == -22);
        assert(!f.calls && !f.c.state && !f.c.client.workspace);
        raw_init(raw);
        history[1] = 0;
        assert(!aefd_context_init(&f.c, call, &f, 71, 72, raw, 128, 31, sources,
                                  history, 0));
        done(&f);
    }
}
static void file_operations(void)
{
    struct fixture f;
    init(&f, 0);
    struct step *s = rpc(&f, 1, 1, 4, 0, 0, 3);
    s->request_size = 128;
    memcpy(s->request + 64, "item", 4);
    assert(aefd_context_open(&f.c, (const unsigned char *)"item", 4, 1) == 0);
    s = rpc(&f, 2, 3, 3, 0, 0, 3);
    aefd_put(s->reply, 5, 3);
    memcpy(s->reply + 64, "abc", 3);
    s->reply_size = 128;
    unsigned char bytes[16] = {0};
    assert(aefd_context_read(&f.c, 0, bytes, 3) == 3 &&
           !memcmp(bytes, "abc", 3));
    (void)rpc(&f, 3, 3, (uint64_t)-1, 1, 0, 2);
    assert(aefd_context_seek(&f.c, 0, -1, 1) == 2);
    (void)rpc(&f, 6, 3, 0, 0, 0, 0);
    assert(!aefd_context_set_flags(&f.c, 0, 0));
    (void)rpc(&f, 4, 3, 3, 1, 0, 4);
    assert(aefd_context_dup(&f.c, 0, 5, 1) == 5);
    unsigned before = f.blocks;
    assert(aefd_context_flags(&f.c, 5) == 1 && f.blocks == before + 1);
    assert(aefd_context_write(&f.c, 0, bytes, 3) == -30);
    (void)rpc(&f, 5, 3, 0, 0, 0, 0);
    assert(!aefd_context_close(&f.c, 0));
    (void)rpc(&f, 5, 4, 0, 0, 0, 0);
    struct aefd_finish receipt;
    assert(!aefd_context_finish(&f.c, &receipt));
    assert(!receipt.unknown && !receipt.remaining && receipt.removed == 1);
    assert(receipt.transport.input == -9 && receipt.transport.output == -5 &&
           f.closes == 2);
    unsigned calls = f.calls;
    assert(!aefd_context_finish(&f.c, &receipt) && f.calls == calls);
    assert(aefd_context_flags(&f.c, 5) == -5 && f.calls == calls);
    assert(f.current == f.count);
    done(&f);
}
static void local_operations(void)
{
    struct fixture f;
    init(&f, 1);
    assert(!aefd_context_set_flags(&f.c, 1, 1));
    assert(aefd_context_dup(&f.c, 1, 3, 1) == 3);
    assert(aefd_context_replace(&f.c, 3, 1) == 1);
    assert(aefd_context_flags(&f.c, 1) == 0 &&
           aefd_context_flags(&f.c, 3) == 1);
    unsigned char raw[128];
    memset(raw, 0xcc, 128);
    assert(!aefd_context_snapshot(&f.c, raw, 128, 1));
    assert(raw[68] == AEFD_BIND_CONSOLE && !raw[76] && f.c.map.slots[3].kind);
    memset(raw, 0xcc, 128);
    assert(aefd_context_snapshot(&f.c, raw, 127, 0) == -22 && raw[0] == 0xcc);
    assert(aefd_context_seek(&f.c, 1, 0, 0) == -29);
    assert(aefd_context_open(&f.c, (const unsigned char *)"a/b", 3, 0) == -22);
    assert(f.blocks == 9 && f.restores == 9 && !f.current && !f.count);
    (void)control(&f, 3, 102, 1, 0, 0);
    struct aefd_finish receipt;
    assert(!aefd_context_finish(&f.c, &receipt));
    assert(receipt.attempted == 2 && receipt.removed == 2 &&
           !receipt.remaining && !receipt.unknown);
    assert(f.current == 1 && f.closes == 2 && f.blocks == 10);
    done(&f);
}
static void redirect_test(int rollback)
{
    struct fixture f;
    init(&f, rollback ? 4 : 3);
    if (!rollback)
        assert(pipe(f.fd) == 0);
    (void)rpc(&f, 4, 3, 3, 0, 0, 4);
    if (rollback) {
        (void)rpc(&f, 5, 5, 0, 0, -9, 0);
        (void)rpc(&f, 5, 4, 0, 0, 0, 0);
    } else {
        struct step *s = control(&f, 3, 102, 1, 0, 0);
        s->effect = 2;
    }
    struct aefd_redirect_result result = aefd_context_redirect(&f.c, 4, 1);
    assert(f.blocks == 1 && f.restores == 1 && f.current == f.count);
    assert(result.status == (rollback ? -9 : 1) &&
           result.committed == !rollback && !result.unknown);
    assert(result.prepared_selector == 4 &&
           result.cleanup_attempted == rollback && !result.unresolved);
    assert(f.c.map.slots[4].selector == 3 && f.c.map.slots[4].cloexec == 1);
    assert(f.c.map.slots[1].kind == AEFD_BIND_FILE);
    assert(f.c.map.slots[1].selector == (rollback ? 5 : 4));
    assert(f.c.map.slots[1].cloexec == (rollback ? 1 : 0));
    if (!rollback) {
        unsigned char byte;
        assert(read(f.fd[0], &byte, 1) == 0 && close(f.fd[0]) == 0);
    }
    (void)rpc(&f, 5, rollback ? 5U : 4U, 0, 0, 0, 0);
    (void)rpc(&f, 5, 3, 0, 0, 0, 0);
    struct aefd_finish receipt;
    assert(!aefd_context_finish(&f.c, &receipt) && !receipt.unknown &&
           !receipt.remaining);
    assert(f.current == f.count && f.blocks == 2 && f.restores == 2);
    done(&f);
}
static void pipe_test(void)
{
    struct fixture f;
    init(&f, 0);
    struct step *s = control(&f, 82, 0x76050001, 1, 0, 0);
    put(s->reply, 4, 1);
    put(s->reply, 8, 0x79000101);
    put(s->reply, 12, 0x79000102);
    put(s->reply, 16, 3);
    put(s->reply, 20, 4);
    put(s->reply, 24, 256);
    put(s->reply, 28, 16);
    int pair[2] = {-99, -98};
    assert(!aefd_context_pipe(&f.c, pair, 1) && pair[0] == 0 && pair[1] == 1);
    assert(f.c.native.generations[0] == 1 && f.c.map.slots[0].cloexec);
    (void)control(&f, 3, 0x79000101, 3, 0, 0);
    (void)control(&f, 3, 0x79000102, 4, 0, 0);
    struct aefd_finish receipt;
    assert(!aefd_context_finish(&f.c, &receipt) && !receipt.remaining &&
           !receipt.unknown);
    assert(f.blocks == 2 && f.current == f.count);
    done(&f);
}
static void loss_tests(void)
{
    for (unsigned prefix = 0; prefix < 128; ++prefix) {
        struct fixture f;
        init(&f, 2);
        struct step *s = rpc(&f, 2, 3, 3, 0, 0, 3);
        aefd_put(s->reply, 5, 3);
        memcpy(s->reply + 64, "abc", 3);
        s->reply_size = prefix;
        unsigned char out[8];
        memset(out, 0xcc, sizeof(out));
        assert(aefd_context_read(&f.c, 4, out, 3) == -5);
        assert(out[0] == 0xcc && f.c.map.slots[4].selector == 3 &&
               !f.c.client.live);
        for (unsigned i = 0; i < 4096; ++i)
            assert(!f.c.workspace[i]);
        unsigned calls = f.calls;
        assert(aefd_context_read(&f.c, 4, out, 3) == -5 && f.calls == calls);
        struct aefd_finish receipt;
        assert(!aefd_context_finish(&f.c, &receipt));
        assert(receipt.unknown && receipt.remaining == 1 &&
               !receipt.attempted && f.closes == 2);
        assert(f.calls == calls);
        done(&f);
    }
    struct fixture f;
    init(&f, 1);
    assert(pipe(f.fd) == 0);
    struct step *s = control(&f, 2, 102, 1, 5, 5);
    memcpy(s->request + 16, "hello", 5);
    s->reply_size = 0;
    s->effect = 1;
    assert(aefd_context_write(&f.c, 1, (const unsigned char *)"hello", 5) ==
           -5);
    unsigned char out[5];
    assert(read(f.fd[0], out, 5) == 5 && !memcmp(out, "hello", 5));
    unsigned calls = f.calls;
    assert(aefd_context_write(&f.c, 1, out, 5) == -5 && f.calls == calls);
    struct aefd_finish receipt;
    assert(!aefd_context_finish(&f.c, &receipt) && receipt.unknown &&
           receipt.remaining == 1);
    assert(f.calls == calls && close(f.fd[0]) == 0 && close(f.fd[1]) == 0);
    done(&f);
}
static void guard_tests(void)
{
    struct fixture f;
    init(&f, 1);
    assert(!aefd_native_enter(&f.c.native));
    unsigned calls = f.calls;
    unsigned char bytes[128];
    memset(bytes, 0xcc, 128);
    int pair[2] = {-99, -98};
    struct aefd_finish receipt, saved;
    memset(&receipt, 0xcc, sizeof(receipt));
    saved = receipt;
    assert(aefd_context_flags(&f.c, 1) == -16);
    assert(aefd_context_set_flags(&f.c, 1, 1) == -16);
    assert(aefd_context_dup(&f.c, 1, 3, 0) == -16);
    assert(aefd_context_replace(&f.c, 1, 3) == -16);
    assert(aefd_context_close(&f.c, 1) == -16);
    assert(aefd_context_read(&f.c, 1, bytes, 1) == -16);
    assert(aefd_context_write(&f.c, 1, bytes, 1) == -16);
    assert(aefd_context_seek(&f.c, 1, 0, 0) == -16);
    assert(aefd_context_open(&f.c, bytes, 1, 0) == -16);
    assert(aefd_context_pipe(&f.c, pair, 0) == -16 && pair[0] == -99);
    assert(aefd_context_snapshot(&f.c, bytes, 128, 0) == -16 &&
           bytes[0] == 0xcc);
    struct aefd_redirect_result r = aefd_context_redirect(&f.c, 1, 3);
    assert(r.status == -16 && !r.unknown && r.prepared_selector == -1);
    assert(aefd_context_finish(&f.c, &receipt) == -16 &&
           !memcmp(&receipt, &saved, sizeof(receipt)));
    assert(f.calls == calls && f.c.client.live && !f.closes);
    f.c.native.retired = 1;
    assert(aefd_context_flags(&f.c, 1) == -16 && f.calls == calls && !f.closes);
    f.c.native.retired = 0;
    aefd_native_leave(&f.c.native);
    done(&f);
    init(&f, 2);
    f.c.map.generation = 32; /* Explicit corrupted-state rejection fixture. */
    assert(aefd_context_read(&f.c, 4, bytes, 1) == -5);
    assert(f.blocks == 1 && f.restores == 1 && f.closes == 2 && !f.current);
    calls = f.calls;
    assert(!aefd_context_finish(&f.c, &receipt) && receipt.unknown &&
           receipt.remaining == 1);
    assert(f.calls == calls);
    done(&f);
    init(&f, 1);
    f.mask_error = 1;
    assert(aefd_context_flags(&f.c, 1) == -14 && !f.c.client.live &&
           f.closes == 2);
    assert(f.c.map.slots[1].kind && !f.current && !f.restores);
    calls = f.calls;
    assert(!aefd_context_finish(&f.c, &receipt));
    assert(receipt.unknown && receipt.remaining == 1 && f.calls == calls);
    ++cases;
    memset(&f, 0, sizeof(f));
    memset(&receipt, 0xcc, sizeof(receipt));
    saved = receipt;
    assert(aefd_context_finish(&f.c, &receipt) == -5 &&
           !memcmp(&receipt, &saved, sizeof(receipt)));
    assert(aefd_context_flags(NULL, 0) == -5);
    ++cases;
    pid_t pid = fork();
    assert(pid >= 0);
    if (!pid) {
        init(&f, 1);
        f.restore_error = 1;
        (void)aefd_context_flags(&f.c, 1);
        _exit(99);
    }
    int status;
    assert(waitpid(pid, &status, 0) == pid && WIFEXITED(status) &&
           WEXITSTATUS(status) == 125);
    ++cases;
}
int main(void)
{
    startup_tests();
    file_operations();
    local_operations();
    redirect_test(0);
    redirect_test(1);
    pipe_test();
    loss_tests();
    guard_tests();
    printf("%u placed descriptor context host scenarios pass\n", cases);
    return 0;
}
