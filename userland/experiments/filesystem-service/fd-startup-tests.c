/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-startup.h"
#include <assert.h>
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

struct fixture {
    struct aefd_startup boot;
    struct aefd_startup_auxv auxv;
    unsigned char frame[304], request[32];
    size_t offset, limit, chunk, sent, replied;
    int64_t pid, parent;
    unsigned calls, reads, waits, blocks, restores, closes;
    int again, wait_error, budget, oversize, mask_error, restore_error;
    int reentered, real, fd[2];
};
static unsigned cases;
static void put(unsigned char *b, unsigned i, uint32_t value)
{
    for (unsigned j = 0; j < 4; ++j)
        b[i + j] = (unsigned char)(value >> (8 * j));
}
static int64_t call(void *context, uint64_t op, uint64_t cap, uint64_t a,
                    uint64_t b, uint64_t c)
{
    struct fixture *f = context;
    ++f->calls;
    if (!f->reentered) {
        f->reentered = 1;
        unsigned before = f->calls;
        assert(aefd_startup_start(&f->boot, call, f, f->auxv) == -16);
        assert(f->calls == before);
    }
    if (op == 0x1000e) {
        assert(a && c == 8);
        if (!cap) {
            assert(b && *(uint64_t *)(uintptr_t)a == UINT64_MAX);
            *(uint64_t *)(uintptr_t)b = 0x1234;
            ++f->blocks;
            return f->mask_error ? -14 : 0;
        }
        assert(cap == 2 && !b && *(uint64_t *)(uintptr_t)a == 0x1234);
        ++f->restores;
        return f->restore_error ? -14 : 0;
    }
    if (op == 0x10027 || op == 0x1006e) {
        assert(!cap && !a && !b && !c && f->blocks == f->restores + 1);
        return op == 0x10027 ? f->pid : f->parent;
    }
    if (op == 0x24003) {
        assert(!a && !b && !c && cap == (f->closes ? 72U : 71U));
        ++f->closes;
        assert(f->closes <= 2);
        return cap == 71 ? -9 : -5;
    }
    if (op == 0x100e7) {
        assert(cap == 125 && f->closes == 2);
        _exit(125);
    }
    if (op == 0x24004) {
        assert(cap == 71 && !a && !b && !c);
        ++f->waits;
        return f->wait_error ? -4 : 0;
    }
    assert(!c && a && b && b <= 16 && f->blocks == f->restores + 1);
    if (f->boot.phase == 1) {
        assert(op == 0x24001 && cap == 71 && !f->boot.context.state);
        assert(!f->boot.identity.slot);
        ++f->reads;
        if (f->oversize)
            return (int64_t)b + 1;
        if (f->budget || f->again) {
            f->again = 0;
            return -11;
        }
        size_t count = (size_t)b;
        if (count > f->chunk)
            count = f->chunk;
        if (count > f->limit - f->offset)
            count = f->limit - f->offset;
        if (f->real) {
            ssize_t result = read(f->fd[0], (void *)(uintptr_t)a, count);
            assert(result >= 0);
            f->offset += (size_t)result;
            return result;
        }
        memcpy((void *)(uintptr_t)a, f->frame + f->offset, count);
        f->offset += count;
        return (int64_t)count;
    }
    assert(f->boot.phase == 2);
    if (op == 0x24002) {
        assert(cap == 72 && f->sent + b <= 32);
        memcpy(f->request + f->sent, (void *)(uintptr_t)a, (size_t)b);
        f->sent += (size_t)b;
        return (int64_t)b;
    }
    assert(op == 0x24001 && cap == 71 && f->sent == 32 && f->replied + b <= 32);
    unsigned char expected[32] = {0};
    put(expected, 0, 3);
    put(expected, 4, 102);
    put(expected, 8, 1);
    assert(!memcmp(f->request, expected, 32));
    memset((void *)(uintptr_t)a, 0, (size_t)b);
    f->replied += (size_t)b;
    return (int64_t)b;
}
static void init(struct fixture *f, unsigned slot, unsigned epoch,
                 unsigned shell)
{
    memset(f, 0, sizeof(*f));
    f->auxv = (struct aefd_startup_auxv){
        UINT64_C(0x40000000) | (uint64_t)epoch << 8 | (slot + 1U), 71, 72};
    f->pid = (int64_t)(epoch * 7 + slot + 1);
    f->parent = slot == 1 ? 7 : (int64_t)(shell * 7 + 2);
    f->limit = 304;
    f->chunk = 16;
    unsigned char *p = f->frame;
    memcpy(p, "AEFDB001", 8);
    put(p, 8, 1);
    put(p, 12, 304);
    memcpy(p + 16, "AEFSH001", 8);
    put(p, 24, 29);
    put(p, 28, 7);
    put(p, 32, slot);
    put(p, 36, epoch);
    put(p, 40, (uint32_t)f->parent);
    put(p, 44, shell);
    memcpy(p + 48, "AEFDT001", 8);
    aefd_put(p + 48, 1, 31);
    aefd_put(p + 48, 2, 16);
    p[116] = AEFD_BIND_CONSOLE;
    p[117] = 1;
    put(p, 192, 102);
    put(p, 196, 1);
    put(p, 200, 2);
    put(p, 204, 16);
    put(p, 296, slot == 1 ? 0x76050001 : 0);
}
static int64_t start(struct fixture *f)
{
    return aefd_startup_start(&f->boot, call, f, f->auxv);
}
static void zero_scratch(struct fixture *f)
{
    for (unsigned i = 0; i < 304; ++i)
        assert(!f->boot.scratch[i]);
}
static void success(struct fixture *f)
{
    assert(!start(f) && f->boot.phase == 2 && !f->boot.status);
    assert(f->offset == 304 && f->boot.identity.slot &&
           f->boot.context.state == 1);
    assert(f->blocks == 1 && f->restores == 1 && !f->closes &&
           !f->boot.close_attempted);
    assert(f->boot.context.session.map == &f->boot.context.map);
    zero_scratch(f);
    unsigned calls = f->calls;
    assert(start(f) == -16 && f->calls == calls);
    assert(aefd_context_flags(&f->boot.context, 1) == 0);
    struct aefd_finish receipt;
    assert(!aefd_context_finish(&f->boot.context, &receipt) &&
           !receipt.unknown && !receipt.remaining);
    assert(f->closes == 2 && f->sent == 32 && f->replied == 32 &&
           f->blocks == 3 && f->restores == 3);
    assert(receipt.transport.input == -9 && receipt.transport.output == -5);
    ++cases;
}
static void failure(struct fixture *f, int64_t expected, int close_expected)
{
    assert(start(f) == expected && f->boot.phase == 3 &&
           f->boot.status == expected);
    assert(!f->boot.identity.slot && !f->boot.context.state &&
           !f->boot.context.client.workspace);
    assert(f->boot.close_attempted == close_expected &&
           f->closes == (close_expected ? 2U : 0U));
    if (close_expected)
        assert(f->boot.closed.input == -9 && f->boot.closed.output == -5);
    zero_scratch(f);
    unsigned calls = f->calls;
    assert(start(f) == -16 && f->calls == calls && !f->sent);
    ++cases;
}
int main(void)
{
    struct fixture f;
    for (unsigned shell = 1; shell <= 3; ++shell) {
        init(&f, 1, shell, shell);
        success(&f);
        for (unsigned slot = 2; slot <= 4; ++slot)
            for (unsigned epoch = 1; epoch <= 15; ++epoch) {
                init(&f, slot, epoch, shell);
                success(&f);
            }
    }
    for (unsigned object = 0; object < 2; ++object)
        for (unsigned history = 0; history <= 9; ++history) {
            init(&f, 1, 1, 1);
            put(f.frame, 288 + object * 4, history);
            success(&f);
            assert(f.boot.context.native.generations[object] == history);
        }
    for (unsigned prefix = 0; prefix < 304; ++prefix) {
        init(&f, 1, 1, 1);
        f.limit = prefix;
        failure(&f, -5, 1);
        assert(f.offset == prefix && f.blocks == f.restores);
    }
    for (unsigned chunk = 1; chunk <= 16; ++chunk) {
        init(&f, 1, 1, 1);
        f.chunk = chunk;
        f.again = 1;
        success(&f);
        assert(f.waits == 1);
    }
    for (unsigned byte = 0; byte < 304; ++byte) {
        if ((byte >= 56 && byte < 64) || (byte >= 192 && byte < 196))
            continue;
        init(&f, 1, 1, 1);
        f.frame[byte] ^= 0x80;
        failure(&f, -22, 1);
    }
    for (unsigned byte = 0; byte < 12; ++byte) {
        init(&f, 1, 1, 1);
        f.frame[byte < 8 ? 56 + byte : 192 + byte - 8] ^= 0x80;
        assert(!start(&f) && f.boot.phase == 2);
        aefd_client_abort(&f.boot.context.client);
        struct aefd_finish r;
        assert(!aefd_context_finish(&f.boot.context, &r) && r.unknown &&
               r.remaining == 1);
        assert(f.closes == 2);
        ++cases;
    }
    for (unsigned fault = 0; fault < 13; ++fault) {
        init(&f, 1, 1, 1);
        int64_t expected = -22;
        int closes = 1;
        switch (fault) {
        case 0:
            f.pid = -38;
            expected = -5;
            break;
        case 1:
            f.parent = -38;
            expected = -5;
            break;
        case 2:
            ++f.pid;
            break;
        case 3:
            ++f.parent;
            break;
        case 4:
            f.auxv.memory ^= 1;
            break;
        case 5:
            f.auxv.memory = 0;
            break;
        case 6:
            f.auxv.input = 0;
            closes = 0;
            break;
        case 7:
            f.auxv.output = 0;
            closes = 0;
            break;
        case 8:
            f.auxv.output = f.auxv.input;
            closes = 0;
            break;
        case 9:
            f.parent = 14;
            put(f.frame, 40, 14);
            break;
        case 10:
            init(&f, 2, 1, 1);
            put(f.frame, 296, 0x76050001);
            break;
        case 11:
            put(f.frame, 296, 0);
            break;
        default:
            memset(f.frame + 56, 0, 8);
            break;
        }
        failure(&f, expected, closes);
        if (fault < 2 || fault == 5 || (fault >= 6 && fault <= 8))
            assert(!f.reads);
    }
    for (unsigned mismatch = 0; mismatch < 2; ++mismatch) {
        init(&f, 1, 1, 1);
        if (!mismatch)
            memcpy(f.frame, "AEFSH001", 8);
        else
            put(f.frame, 8, 2);
        f.limit = 16;
        failure(&f, -22, 1);
        assert(f.offset == 16 && !f.waits);
    }
    for (unsigned fault = 0; fault < 4; ++fault) {
        init(&f, 1, 1, 1);
        if (fault == 0)
            f.again = f.wait_error = 1;
        if (fault == 1)
            f.budget = 1;
        if (fault == 2)
            f.oversize = 1;
        if (fault == 3)
            f.mask_error = 1;
        failure(&f, fault == 3 ? -14 : -5, 1);
        if (fault == 1)
            assert(f.waits == AEFD_IO_BUDGET);
        if (fault == 3)
            assert(!f.reads && !f.restores);
    }
    init(&f, 1, 1, 1);
    assert(pipe(f.fd) == 0 && write(f.fd[1], f.frame, 304) == 304 &&
           write(f.fd[1], "TAIL", 4) == 4);
    assert(close(f.fd[1]) == 0);
    f.real = 1;
    success(&f);
    unsigned char tail[4];
    assert(read(f.fd[0], tail, 4) == 4 && !memcmp(tail, "TAIL", 4) &&
           read(f.fd[0], tail, 1) == 0);
    assert(close(f.fd[0]) == 0);
    pid_t pid = fork();
    assert(pid >= 0);
    if (!pid) {
        init(&f, 1, 1, 1);
        f.restore_error = 1;
        (void)start(&f);
        _exit(99);
    }
    int status;
    assert(waitpid(pid, &status, 0) == pid && WIFEXITED(status) &&
           WEXITSTATUS(status) == 125);
    ++cases;
    printf("%u single-consumer startup host scenarios pass\n", cases);
    return 0;
}
