/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-fork-stage.h"
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>
struct fixture {
    struct aefd_fork fork;
    struct aefd_startup_auxv aux;
    unsigned char startup[304], child[304], sent[304], reply[32], ready[32];
    size_t offset, read_limit, written, write_limit, chunk;
    long pid, parent;
    uint64_t mask;
    unsigned calls, blocks, restores, old_closes, new_closes, rebinds;
    int mode, rebind_error, mask_error, restore_error, again, forever,
        wait_error, oversize;
    int reenter;
};
static struct fixture f;
static unsigned cases;
static void put32(unsigned char *raw, unsigned offset, uint32_t value)
{
    for (unsigned i = 0; i < 4; ++i)
        raw[offset + i] = (unsigned char)(value >> (i * 8));
}
static void startup_frame(unsigned char raw[304])
{
    memset(raw, 0, 304);
    memcpy(raw, AEFD_STARTUP_MAGIC, 8);
    put32(raw, 8, 1);
    put32(raw, 12, 304);
    memcpy(raw + 16, "AEFSH001", 8);
    put32(raw, 24, 29);
    put32(raw, 28, 7);
    put32(raw, 32, 1);
    put32(raw, 36, 1);
    put32(raw, 40, 7);
    put32(raw, 44, 1);
    memcpy(raw + 48, AEFD_MAP_MAGIC, 8);
    aefd_put(raw + 48, 1, 17);
    aefd_put(raw + 48, 2, 16);
    const unsigned char slots[24] = {1, 0, 1, 0, 1, 1, 0, 0, 1, 2, 0, 0,
                                     3, 3, 1, 0, 2, 3, 0, 0, 2, 4, 1, 0};
    memcpy(raw + 112, slots, sizeof slots);
    for (unsigned i = 0; i < 5; ++i) {
        unsigned offset = 176 + i * 16;
        put32(raw, offset, i < 3 ? 101 + i : UINT32_C(0x79000201) + i - 3);
        put32(raw, offset + 4, i);
        put32(raw, offset + 8, i == 0 || i == 3 ? 1 : 2);
        put32(raw, offset + 12, 16);
    }
    put32(raw, 288, 2);
    put32(raw, 292, 9);
    put32(raw, 296, UINT32_C(0x76050001));
}
static int rebind(void *context, struct aefd_startup_auxv parent,
                  struct aefd_startup_auxv child)
{
    struct fixture *x = context;
    ++x->rebinds;
    assert(x->mode == 2 && x->fork.phase == AEFD_FORK_CHILD);
    assert(x->fork.boot.phase == 4 && x->fork.boot.context.state == 4);
    unsigned before = x->calls;
    assert(aefd_context_flags(&x->fork.boot.context, 3) == -5);
    assert(x->calls == before);
    assert(parent.memory == x->aux.memory && parent.input == x->aux.input &&
           parent.output == x->aux.output);
    if (x->rebind_error)
        return 0;
    x->aux = child;
    return 1;
}
static int64_t call(void *context, uint64_t op, uint64_t cap, uint64_t a,
                    uint64_t b, uint64_t c)
{
    struct fixture *x = context;
    ++x->calls;
    if (x->reenter && (op == 0x24001 || op == 0x24002)) {
        unsigned before = x->calls;
        assert(aefd_fork_arm(&x->fork, x->aux) == -16);
        assert(aefd_fork_child(&x->fork, x->aux, rebind, x) == -16);
        assert(aefd_fork_parent(&x->fork, 10) == -16);
        assert(x->calls == before);
    }
    if (op == 0x1000e) {
        assert(a && c == 8);
        if (cap == 0) {
            assert(b && *(uint64_t *)(uintptr_t)a == UINT64_MAX);
            ++x->blocks;
            *(uint64_t *)(uintptr_t)b = x->mask;
            if (x->mode >= 2 && x->mask_error)
                return -14;
            x->mask = UINT64_MAX;
            return 0;
        }
        assert(cap == 2 && !b);
        if (x->mode >= 2 &&
            a == (uintptr_t)&x->fork.boot.context.native.saved_mask)
            assert(x->fork.boot.identity.slot != 1);
        ++x->restores;
        if (x->mode == 2 && x->restore_error)
            return -14;
        x->mask = *(uint64_t *)(uintptr_t)a;
        return 0;
    }
    if (op == 0x10027 || op == 0x1006e)
        return op == 0x10027 ? x->pid : x->parent;
    if (op == 0x24003) {
        assert(!a && !b && !c);
        if (x->mode >= 2) {
            assert(cap == (x->new_closes ? 82U : 81U));
            ++x->new_closes;
            assert(x->new_closes <= 2);
        } else {
            assert(cap == (x->old_closes ? 72U : 71U));
            ++x->old_closes;
            assert(x->old_closes <= 2);
        }
        return cap == 71 || cap == 81 ? -9 : -5;
    }
    if (op == 0x100e7) {
        assert(cap == 125 && x->mode == 2 && x->old_closes == 0 &&
               x->new_closes == 2);
        _exit(125);
    }
    if (op == 0x24004) {
        assert(cap == (x->mode >= 2 ? 81U : 71U) ||
               cap == (x->mode >= 2 ? 82U : 72U));
        return x->wait_error ? -4 : 0;
    }
    assert(!c && a && b && b <= 16);
    if (x->mode == 2 && cap == 101 && op == 0x24001) {
        memset((void *)(uintptr_t)a, 0x5a, (size_t)b);
        return (int64_t)b;
    }
    assert(op == 0x24001 || op == 0x24002);
    assert(cap == (op == 0x24001 ? (x->mode >= 2 ? 81U : 71U)
                                 : (x->mode >= 2 ? 82U : 72U)));
    if (x->forever || x->again) {
        x->again = 0;
        return -11;
    }
    if (x->oversize)
        return (int64_t)b + 1;
    size_t count = (size_t)b;
    if (count > x->chunk)
        count = x->chunk;
    if (op == 0x24001) {
        if (count > x->read_limit - x->offset)
            count = x->read_limit - x->offset;
        const unsigned char *raw = x->mode == 0   ? x->startup
                                   : x->mode == 2 ? x->child
                                                  : x->reply;
        memcpy((void *)(uintptr_t)a, raw + x->offset, count);
        x->offset += count;
    } else {
        if (count > x->write_limit - x->written)
            count = x->write_limit - x->written;
        unsigned char *raw = x->mode >= 2 ? x->ready : x->sent;
        memcpy(raw + x->written, (const void *)(uintptr_t)a, count);
        x->written += count;
    }
    return (int64_t)count;
}
static void setup(void)
{
    // Each fixture represents a fresh isolated synthetic native world.
    memset(&f, 0, sizeof f);
    startup_frame(f.startup);
    f.aux = (struct aefd_startup_auxv){UINT64_C(0x40000102), 71, 72};
    f.pid = 9;
    f.parent = 7;
    f.chunk = 16;
    f.read_limit = 304;
    f.write_limit = 304;
    f.mask = 0x1234;
    assert(aefd_startup_start(&f.fork.boot, call, &f, f.aux) == 0);
    assert(f.fork.boot.phase == 2);
    f.mode = 1;
    f.offset = f.written = 0;
    f.read_limit = 32;
    f.mask = UINT64_MAX; // Pinned _Fork's outer blocked mask.
}
static void arm(void)
{
    assert(aefd_fork_arm(&f.fork, f.aux) == 0);
    assert(f.fork.phase == AEFD_FORK_ARMED && f.written == 304);
    struct aefd_fork_view view;
    assert(aefd_fork_decode(f.sent, 304, f.aux, 9, 7, &view));
    assert(view.sequence == f.fork.sequence);
    assert(f.sent[126] == 1 && f.sent[134] == 1);
}
static struct aefd_startup_auxv child_after_arm(void)
{
    f.mode = 2;
    f.pid = 10;
    f.parent = 9;
    f.offset = f.written = 0;
    f.read_limit = 304;
    f.write_limit = 32;
    memcpy(f.child, f.startup, 304);
    put32(f.child, 32, 2);
    put32(f.child, 40, 9);
    aefd_put(f.child + 48, 1, 18);
    memset(f.child + 296, 0, 8);
    return (struct aefd_startup_auxv){UINT64_C(0x40000103), 81, 82};
}
static struct aefd_startup_auxv child_setup(void)
{
    arm();
    return child_after_arm();
}
static void parent_reply(int64_t result)
{
    memset(f.reply, 0, 32);
    memcpy(f.reply, "AEFKR001", 8);
    aefd_put(f.reply, 1, f.fork.sequence);
    aefd_put(f.reply, 2, (uint64_t)result);
}
static void parent_cases(void)
{
    for (unsigned which = 0; which < 3; ++which) {
        setup();
        struct aefd_startup before = f.fork.boot;
        f.reenter = 1;
        arm();
        unsigned calls = f.calls;
        assert(aefd_context_flags(&f.fork.boot.context, 3) == -16);
        assert(f.calls == calls);
        parent_reply(which == 0 ? 10 : which == 1 ? -12 : -11);
        assert(aefd_fork_parent(&f.fork, which ? -11 : 10) == (which == 0 ? 10
                                                               : which == 1
                                                                   ? -12
                                                                   : -11));
        assert(f.fork.phase == AEFD_FORK_IDLE && f.fork.counter == 1);
        assert(!memcmp(&before, &f.fork.boot, sizeof before));
        assert(f.old_closes == 0 && f.new_closes == 0 && f.mask == UINT64_MAX);
        ++cases;
    }
    setup();
    arm();
    parent_reply(-12);
    assert(aefd_fork_parent(&f.fork, -11) == -12);
    f.written = f.offset = 0;
    arm();
    assert(f.fork.counter == 2 && aefd_word(f.sent + 296, 0) == 2);
    ++cases;
    for (size_t length = 0; length < 304; ++length) {
        setup();
        f.write_limit = length;
        assert(aefd_fork_arm(&f.fork, f.aux) == -5);
        assert(f.fork.phase == AEFD_FORK_FAILED && f.fork.counter == 1);
        assert(f.old_closes == 2 && f.new_closes == 0);
        unsigned calls = f.calls;
        assert(aefd_fork_arm(&f.fork, f.aux) == -16);
        assert(f.calls == calls);
        ++cases;
    }
    for (size_t length = 0; length < 32; ++length) {
        setup();
        arm();
        parent_reply(10);
        f.read_limit = length;
        assert(aefd_fork_parent(&f.fork, 10) == -5);
        assert(f.fork.phase == AEFD_FORK_FAILED && f.old_closes == 2);
        ++cases;
    }
    for (unsigned which = 0; which < 6; ++which) {
        setup();
        arm();
        parent_reply(which == 0 ? 11 : which == 5 ? -12 : 10);
        if (which == 1)
            f.reply[8] ^= 1;
        if (which == 2)
            f.reply[24] = 1;
        assert(aefd_fork_parent(&f.fork, which == 3   ? 0
                                         : which == 4 ? -12
                                                      : 10) == -5);
        assert(f.fork.phase == AEFD_FORK_FAILED && f.old_closes == 2);
        ++cases;
    }
    for (unsigned which = 0; which < 4; ++which) {
        setup();
        if (which == 0)
            f.fork.boot.identity.slot = 2;
        if (which == 1)
            f.aux.input = 0;
        if (which == 2)
            f.fork.boot.context.native.retired = 1;
        if (which == 3)
            f.fork.boot.context.client.live = 0;
        unsigned before = f.calls;
        assert(aefd_fork_arm(&f.fork, f.aux) == -22 && f.calls == before);
        assert(f.old_closes == 0 && f.fork.counter == 0);
        ++cases;
    }
    setup();
    f.fork.counter = UINT64_MAX;
    unsigned calls = f.calls;
    assert(aefd_fork_arm(&f.fork, f.aux) == -75 && f.calls == calls);
    assert(f.fork.phase == AEFD_FORK_IDLE);
    ++cases;
}
static void child_success(void)
{
    setup();
    struct aefd_startup_auxv grants = child_setup();
    f.reenter = 1;
    assert(aefd_fork_child(&f.fork, grants, rebind, &f) == 0);
    assert(f.fork.phase == AEFD_FORK_READY && f.fork.boot.phase == 2);
    assert(f.fork.boot.identity.slot == 2 && f.rebinds == 1);
    assert(f.old_closes == 0 && f.new_closes == 0);
    assert(aefd_fork_ready_decode(f.ready, 32, f.fork.sequence, 10));
    struct aefd_context *c = &f.fork.boot.context;
    assert(c->session.map == &c->map && c->session.client == &c->client);
    assert(c->client.workspace == c->workspace &&
           c->client.io.context == &c->native);
    assert(c->session.adapters.reader.context == &c->native);
    assert(c->client.generation == 18 && c->native.factory == 0);
    assert(c->native.generations[0] == 2 && c->native.generations[1] == 9);
    assert(aefd_context_flags(c, 3) == 1);
    unsigned char data[17] = {0};
    f.reenter = 0;
    f.mode = 3;
    f.offset = f.written = 0;
    f.read_limit = f.write_limit = 32;
    memset(f.reply, 0, 32);
    put32(f.reply, 0, 16);
    memset(f.reply + 16, 0x5a, 16);
    assert(aefd_context_read(c, 0, data, 17) == 16);
    for (unsigned i = 0; i < 16; ++i)
        assert(data[i] == 0x5a);
    assert(data[16] == 0);
    unsigned calls = f.calls;
    assert(aefd_fork_child(&f.fork, grants, rebind, &f) == -16 &&
           f.calls == calls);
    assert(aefd_startup_start(&f.fork.boot, call, &f, grants) == -16 &&
           f.calls == calls);
    assert(aefd_fork_arm(&f.fork, grants) == -16 && f.calls == calls);
    ++cases;
}
static void child_failures(void)
{
    for (size_t length = 0; length < 304; ++length) {
        setup();
        struct aefd_startup_auxv grants = child_setup();
        f.read_limit = length;
        assert(aefd_fork_child(&f.fork, grants, rebind, &f) == -5);
        assert(f.fork.phase == AEFD_FORK_FAILED && f.fork.boot.phase == 4);
        assert(f.new_closes == 2 && f.old_closes == 0);
        assert(f.fork.boot.closed.input == -9 &&
               f.fork.boot.closed.output == -5);
        unsigned calls = f.calls;
        assert(aefd_fork_child(&f.fork, grants, rebind, &f) == -16 &&
               f.calls == calls);
        ++cases;
    }
    for (size_t length = 0; length < 32; ++length) {
        setup();
        struct aefd_startup_auxv grants = child_setup();
        f.write_limit = length;
        assert(aefd_fork_child(&f.fork, grants, rebind, &f) == -5);
        assert(f.new_closes == 2 && f.old_closes == 0 &&
               f.fork.boot.phase == 4);
        ++cases;
    }
    for (unsigned i = 0; i < 304; ++i) {
        if (i >= 56 && i < 64)
            continue;
        setup();
        struct aefd_startup_auxv grants = child_setup();
        f.child[i] ^= 128;
        assert(aefd_fork_child(&f.fork, grants, rebind, &f) == -5);
        assert(f.new_closes == 2 && f.old_closes == 0);
        if (i < 16)
            assert(f.offset == 16);
        ++cases;
    }
    for (unsigned which = 0; which < 12; ++which) {
        setup();
        struct aefd_startup_auxv grants = child_setup();
        if (which == 0)
            f.pid = 9;
        if (which == 1)
            f.parent = 7;
        if (which == 2)
            grants.memory = f.aux.memory;
        if (which == 3)
            grants.input = 71;
        if (which == 4)
            grants.output = 72;
        if (which == 5)
            grants.output = grants.input;
        if (which == 6)
            f.rebind_error = 1;
        if (which == 7)
            f.mask_error = 1;
        if (which == 8)
            f.fork.boot.scratch[296] ^= 1;
        if (which == 9)
            aefd_put(f.child + 48, 1, 17);
        if (which == 10)
            f.child[126] ^= 1;
        if (which == 11)
            f.child[125] = 4;
        assert(aefd_fork_child(&f.fork, grants, rebind, &f) == -5);
        assert(f.old_closes == 0 && f.fork.boot.phase == 4);
        assert(f.new_closes == (which == 7 || which >= 9 ? 2U : 0U));
        ++cases;
    }
    for (unsigned which = 0; which < 4; ++which) {
        setup();
        struct aefd_startup_auxv grants = child_setup();
        if (which == 0)
            f.again = 1;
        if (which == 1)
            f.forever = 1;
        if (which == 2)
            f.forever = f.wait_error = 1;
        if (which == 3)
            f.oversize = 1;
        int64_t result = aefd_fork_child(&f.fork, grants, rebind, &f);
        assert(result == (which == 0 ? 0 : -5));
        if (which)
            assert(f.new_closes == 2 && f.old_closes == 0);
        if (which == 1)
            assert(f.fork.budget == 0);
        ++cases;
    }
}
static void private_copy(void)
{
    setup();
    arm();
    struct aefd_fork before = f.fork;
    pid_t pid = fork();
    assert(pid >= 0);
    if (!pid) {
        f.mode = 2;
        f.pid = 10;
        f.parent = 9;
        f.offset = f.written = 0;
        f.read_limit = 304;
        f.write_limit = 32;
        memcpy(f.child, f.startup, 304);
        put32(f.child, 32, 2);
        put32(f.child, 40, 9);
        aefd_put(f.child + 48, 1, 18);
        memset(f.child + 296, 0, 8);
        struct aefd_startup_auxv grants = {UINT64_C(0x40000103), 81, 82};
        assert(aefd_fork_child(&f.fork, grants, rebind, &f) == 0);
        assert(f.old_closes == 0 &&
               f.fork.boot.context.client.generation == 18);
        _exit(0);
    }
    int status = 0;
    assert(waitpid(pid, &status, 0) == pid && WIFEXITED(status) &&
           WEXITSTATUS(status) == 0);
    assert(!memcmp(&before, &f.fork, sizeof before));
    parent_reply(10);
    assert(aefd_fork_parent(&f.fork, 10) == 10);
    ++cases;
}
#ifdef AEFD_FORK_HOST_TEST
static int native_lane;
void aefd_fork_test_tls_set(uint32_t);
unsigned long aefd_fork_test_auxv(unsigned long);
void aefd_fork_test_park(unsigned long *, unsigned long *, unsigned long *,
                         unsigned long *);
int copy_rebind(unsigned long, unsigned long, unsigned long, unsigned long *,
                unsigned long *);
_Noreturn void __real__exit(int);
struct aefd_fork *aefd_shell_fork_context(void) { return &f.fork; }
unsigned long aefd_fork_test_auxv(unsigned long key)
{
    errno = ERANGE;
    return key == 0xa000   ? f.aux.memory
           : key == 0xa001 ? f.aux.input
           : key == 0xa002 ? f.aux.output
                           : 0;
}
int copy_rebind(unsigned long memory, unsigned long input, unsigned long output,
                unsigned long *old_input, unsigned long *old_output)
{
    assert(*old_input == f.aux.input && *old_output == f.aux.output);
    struct aefd_startup_auxv child = {memory, input, output};
    if (!rebind(&f, f.aux, child))
        return 0;
    if (native_lane == 6)
        aefd_fork_test_tls_set(0);
    *old_input = input;
    *old_output = output;
    return 1;
}
void aefd_fork_test_park(unsigned long *op, unsigned long *memory,
                         unsigned long *input, unsigned long *output)
{
    assert(*op == 0x23003 && f.fork.phase == AEFD_FORK_ARMED);
    if (native_lane == 1 || native_lane == 3 || native_lane == 4 ||
        native_lane == 6) {
        struct aefd_startup_auxv grants = child_after_arm();
        *op = 0;
        *memory = grants.memory;
        *input = grants.input;
        *output = grants.output;
        if (native_lane == 3)
            f.read_limit = 16;
        if (native_lane == 4)
            f.restore_error = 1;
    } else {
        *op = native_lane == 5 ? (unsigned long)-11L : 10;
        parent_reply(native_lane == 5 ? -12 : 10);
        if (native_lane == 2)
            f.read_limit = 16;
    }
}
_Noreturn void __real__exit(int status) { _exit(status); }
static void native_entry(void)
{
    assert(aefd_fork_tls_valid());
    for (int lane = 0; lane < 2; ++lane) {
        setup();
        native_lane = lane ? 6 : 0;
        pid_t pid = fork();
        assert(pid >= 0);
        if (!pid) {
            if (!lane) {
                aefd_fork_test_tls_set(0);
                assert(!aefd_fork_tls_valid());
            }
            (void)__aether_fork_stage();
            _exit(99);
        }
        int status = 0;
        assert(waitpid(pid, &status, 0) == pid && WIFEXITED(status));
        assert(WEXITSTATUS(status) == (lane ? 114 : 116));
        assert(aefd_fork_tls_valid());
        assert(f.fork.phase == AEFD_FORK_IDLE && f.old_closes == 0);
        ++cases;
    }
    const int paths[3] = {0, 1, 5};
    for (unsigned path = 0; path < 3; ++path) {
        native_lane = paths[path];
        setup();
        errno = EALREADY;
        assert(__aether_fork_stage() == (native_lane == 1   ? 0
                                         : native_lane == 5 ? -12
                                                            : 10));
        assert(errno == EALREADY);
        assert(f.fork.phase ==
               (native_lane == 1 ? AEFD_FORK_READY : AEFD_FORK_IDLE));
        if (native_lane == 1)
            assert(aefd_fork_ready_decode(f.ready, 32, 1, 10));
        ++cases;
    }
    setup();
    f.fork.counter = UINT64_MAX;
    errno = EALREADY;
    assert(__aether_fork_stage() == -75 && errno == EALREADY);
    ++cases;
    for (native_lane = 2; native_lane <= 4; ++native_lane) {
        setup();
        pid_t pid = fork();
        assert(pid >= 0);
        if (!pid) {
            (void)__aether_fork_stage();
            _exit(99);
        }
        int status = 0;
        assert(waitpid(pid, &status, 0) == pid && WIFEXITED(status));
        assert(WEXITSTATUS(status) == (native_lane == 2   ? 116
                                       : native_lane == 3 ? 114
                                                          : 125));
        assert(f.fork.phase == AEFD_FORK_IDLE && f.old_closes == 0);
        ++cases;
    }
}
#endif
int main(void)
{
    parent_cases();
    child_success();
    child_failures();
    private_copy();
#ifdef AEFD_FORK_HOST_TEST
    native_entry();
#endif
    printf("%u armed fork/child cases pass\n", cases);
    return 0;
}
