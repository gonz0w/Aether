/* SPDX-License-Identifier: BSD-2-Clause */
#define _POSIX_C_SOURCE 200809L
#include "fd-zsh-process.h"
#include "fd-exec.h"
#include "fd-zsh-external.h"
#include "fd-libc.h"
#include <assert.h>
#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/wait.h>
/* A fresh fixture is a new isolated synthetic native world. No fixture grants
 * authority; actual provider bodies perform all snapshot/rebind validation. */
struct fixture {
    struct aefd_fork *f;
    struct aefd_startup_auxv aux;
    unsigned char startup[336], child[336], sent[672], reply[128];
    size_t offset, written, limit, write_limit;
    long pid, parent;
    uint64_t mask;
    unsigned calls, closes, rebinds, parks, ready, transactions;
    int mode, reenter, rebind_error, park_result;
#ifdef AEFD_ZSH_HOME_CWD_EXEC_BINDINGS
    unsigned cwd_response, file_requests, terminal_writes;
#endif
};
static struct fixture x;
static struct aefd_fork local;
static unsigned cases;
static int main_calls;
static int helper_check, helper_mode;
static char **expected_argv;
static void put32(unsigned char *raw, unsigned at, uint32_t value)
{
    for (unsigned i = 0; i < 4; ++i)
        raw[at + i] = (unsigned char)(value >> (i * 8));
}
static void snapshot(unsigned char raw[336], int child)
{
    memset(raw, 0, 336);
    memcpy(raw, "AEFDB009", 8);
    put32(raw, 8, 1);
    put32(raw, 12, 336);
    memcpy(raw + 16, "AEFSH001", 8);
    put32(raw, 24, 29);
    put32(raw, 28, 7);
    put32(raw, 32, child ? 2 : 1);
    put32(raw, 36, 1);
    put32(raw, 40, child ? 9 : 7);
    put32(raw, 44, 1);
    memcpy(raw + 48, "AEFDT009", 8);
    aefd_put(raw + 48, 1, child ? 32 : 31);
    aefd_put(raw + 48, 2, 16);
    for (unsigned i = 0; i < 3; ++i) {
        raw[112 + i * 4] = 4;
        raw[113 + i * 4] = (unsigned char)i;
        put32(raw, 176 + i * 16, 0x7a000001 | i << 16);
        put32(raw, 180 + i * 16, i);
        put32(raw, 184 + i * 16, i ? 2 : 1);
        put32(raw, 188 + i * 16, 16);
    }
    put32(raw, 296, child ? 0 : 0x76050001);
    put32(raw, 300, child ? 0 : 0x7d000001);
    for (unsigned i = 0; i < 4; ++i)
        put32(raw, 304 + i * 4, 1000);
    put32(raw, 320, 1);
}
#ifdef AEFD_ZSH_HOME_CWD_EXEC_BINDINGS
static void child_response(void)
{
    memset(x.reply, 0, sizeof x.reply);
    x.offset = 0;
    if (memcmp(x.sent, AEFD_MAGIC, 8)) {
        assert(aether_fs_session_u32(x.sent) == 2 &&
               aether_fs_session_u32(x.sent + 4) == 0x7a010001 &&
               aether_fs_session_u32(x.sent + 8) == 1 &&
               aether_fs_session_u32(x.sent + 12) == 5 &&
               !memcmp(x.sent + 16, "/home", 5));
        aefd_put(x.reply, 0, 5);
        x.limit = 32;
        ++x.terminal_writes;
        return;
    }
    assert(!memcmp(AEFD_MAGIC, "AEFP0007", 8) && aefd_word(x.sent, 2) == 32);
    memcpy(x.reply, AEFD_MAGIC, 8);
    aefd_put(x.reply, 2, 32);
    aefd_put(x.reply, 3, aefd_word(x.sent, 3));
    x.limit = 64;
    uint64_t operation = aefd_word(x.sent, 1);
    if (operation == 9) {
        for (unsigned i = 4; i < 8; ++i)
            assert(!aefd_word(x.sent, i));
        if (x.cwd_response == 2) {
            aefd_put(x.reply, 1, (uint64_t)-13);
        } else {
            size_t n = x.cwd_response ? 6 : 2;
            memcpy(x.reply + 64, x.cwd_response ? "/home" : "/", n);
            aefd_put(x.reply, 5, n);
            x.limit = 128;
            if (x.cwd_response == 3)
                x.reply[127] = 1;
            if (x.cwd_response == 4)
                memcpy(x.reply, "AEFP0006", 8);
            if (x.cwd_response == 5)
                aefd_put(x.reply, 2, 31);
            if (x.cwd_response == 6)
                aefd_put(x.reply, 5, 3);
            if (x.cwd_response == 7)
                x.limit = 70;
        }
    } else {
        assert(operation == 13 || operation == 1);
        /* These bytes are forwarded to the Owner, never locally authorized. */
        assert(
            !memcmp(x.sent + 64, operation == 13 ? "/" : AEFD_HOME_PROFILE_PATH,
                    operation == 13 ? 1 : sizeof(AEFD_HOME_PROFILE_PATH) - 1));
        aefd_put(x.reply, 1, (uint64_t)-13);
    }
    ++x.file_requests;
}
#endif
static int64_t call(void *unused, uint64_t op, uint64_t cap, uint64_t a,
                    uint64_t b, uint64_t c)
{
    (void)unused;
    ++x.calls;
    if (op == 0x1000e) {
        assert(c == 8 && a);
        if (!cap) {
            assert(b && *(uint64_t *)(uintptr_t)a == UINT64_MAX);
            *(uint64_t *)(uintptr_t)b = x.mask;
            x.mask = UINT64_MAX;
        } else {
            assert(cap == 2 && !b);
            x.mask = *(uint64_t *)(uintptr_t)a;
        }
        return 0;
    }
    if (op == 0x10027 || op == 0x1006e)
        return op == 0x10027 ? x.pid : x.parent;
    if (op == 0x24003) {
        assert(cap == x.aux.input || cap == x.aux.output);
        ++x.closes;
        assert(x.closes <= 2);
        return 0;
    }
    if (op == 0x24004)
        return 0;
    if (op == 0x23003) {
        assert(x.mode == 3 && x.written == 672);
        ++x.parks;
        return x.park_result;
    }
    if (op == 0x20004) {
        ++x.ready;
        x.mode = 5;
        x.written = x.offset = 0;
        return 0;
    }
    assert(op == 0x24001 || op == 0x24002);
    assert(cap == (op == 0x24001 ? x.aux.input : x.aux.output));
    assert(a && b && b <= 16 && !c && x.mask == UINT64_MAX);
    if (x.reenter) {
        unsigned before = x.calls;
        assert(aefd_fork_arm(x.f, x.aux) == -16);
        assert(__aether_waitpid(-1, NULL, 11) == -EBUSY);
        assert(x.calls == before);
    }
    size_t count = b > 7 ? 7 : (size_t)b; /* Actual short transport. */
    if (op == 0x24002) {
        if (count > x.write_limit - x.written)
            count = x.write_limit - x.written;
        memcpy(x.sent + x.written, (void *)(uintptr_t)a, count);
        x.written += count;
#ifdef AEFD_ZSH_HOME_CWD_EXEC_BINDINGS
        if (x.mode == 7 && x.written >= 8) {
            size_t goal = 32;
            if (!memcmp(x.sent, AEFD_MAGIC, 8)) {
                uint64_t operation = aefd_word(x.sent, 1);
                goal = operation == 9 ? 64 : 128;
            }
            if (x.written == goal)
                child_response();
        }
#endif
        if (x.mode == 5 && x.written == 32) {
            assert(aether_fs_session_u32(x.sent) == 3);
            memset(x.reply, 0, 32);
            x.offset = 0;
        }
    } else {
        const unsigned char *raw = x.mode == 0   ? x.startup
                                   : x.mode == 2 ? x.child
                                                 : x.reply;
        if (count > x.limit - x.offset)
            count = x.limit - x.offset;
        memcpy((void *)(uintptr_t)a, raw + x.offset, count);
        x.offset += count;
#ifdef AEFD_ZSH_HOME_CWD_EXEC_BINDINGS
        if (x.mode == 7 && x.offset == x.limit && x.cwd_response != 7) {
            x.written = x.offset = 0;
        }
#endif
        if (x.mode == 5 && x.offset == 32) {
            ++x.transactions;
            x.written = 0;
        }
    }
    return (int64_t)count;
}
static void setup(int global)
{
    memset(&x, 0, sizeof x);
    x.f = global ? aefd_shell_fork_context() : &local;
    memset(x.f, 0, sizeof *x.f);
    assert(!global || &x.f->boot == aefd_shell_external_startup());
    snapshot(x.startup, 0);
    snapshot(x.child, 1);
    x.aux = (struct aefd_startup_auxv){0x40000102, 71, 72};
    x.pid = 9;
    x.parent = 7;
    x.mask = 0x1234;
    x.limit = 336;
    x.write_limit = 672;
    assert(aefd_startup_start(&x.f->boot, call, NULL, x.aux) == 0);
    assert(x.mask == 0x1234 && !x.closes);
    x.mode = 1;
    x.offset = x.written = 0;
    x.limit = 32;
    x.park_result = -11;
}
static void arm(void)
{
    assert(aefd_fork_arm(x.f, x.aux) == 0);
    assert(x.written == 368 && x.f->phase == AEFD_FORK_ARMED);
    struct aefd_zsh_snapshot view;
    uint64_t sequence;
    assert(
        aefd_zsh_fork_decode(x.sent, 368, x.aux, 9, 7, 31, &view, &sequence));
    assert(sequence == x.f->sequence && !memcmp(x.sent + 32, x.startup, 336));
}
static int rebind(void *unused, struct aefd_startup_auxv parent,
                  struct aefd_startup_auxv child)
{
    (void)unused;
    ++x.rebinds;
    assert(parent.memory == 0x40000102 && x.f->boot.phase == 4);
    unsigned calls = x.calls;
    assert(aefd_context_flags(&x.f->boot.context, 0) == -5);
    assert(calls == x.calls);
    if (x.rebind_error)
        return 0;
    x.aux = child;
    return 1;
}
static int64_t become_child(void)
{
    arm();
    x.mode = 2;
    x.pid = 10;
    x.parent = 9;
    x.offset = x.written = 0;
    x.limit = 336;
    return aefd_fork_child(x.f, (struct aefd_startup_auxv){0x40000103, 81, 82},
                           rebind, NULL);
}
static void fork_cases(void)
{
    for (unsigned which = 0; which < 5; ++which) {
        setup(1);
        arm();
        assert(aefd_zsh_receipt_encode(x.reply, "AEZFR001", 1,
                                       which == 1 ? -12 : 10));
        if (which == 2)
            x.reply[8] ^= 1;
        if (which == 3)
            x.reply[24] = 1;
        if (which == 4)
            x.limit = 31;
        int64_t result = aefd_fork_parent(x.f, which == 1 ? -11 : 10);
        assert(result == (which >= 2 ? -5 : which == 1 ? -12 : 10));
        assert(x.closes == (which >= 2 ? 2U : 0U));
        ++cases;
    }
    for (unsigned which = 0; which < 5; ++which) {
        setup(0);
        if (which == 1)
            x.child[39] = '8';
        if (which == 2)
            x.child[304] ^= 1;
        if (which == 3)
            x.child[56] = 31; /* stale table generation */
        if (which == 4)
            x.rebind_error = 1;
        assert(become_child() == (which ? -5 : 0));
        assert(!x.closes || which);
        if (!which) {
            int64_t result;
            assert(aefd_zsh_receipt_decode(x.sent, "AEZFC001", 1, &result));
            assert(result == 10 && x.rebinds == 1);
            struct aefd_context *c = &x.f->boot.context;
            assert(c->session.map == &c->map &&
                   c->session.client == &c->client);
            assert(c->client.workspace == c->workspace &&
                   c->client.io.context == &c->native);
            assert(c->native.factory == 0 && c->mode_control == 0);
            assert(x.f->boot.credentials[3] == 1000 && c->map.generation == 32);
        }
        unsigned before = x.calls;
        assert(aefd_fork_child(x.f, x.aux, rebind, NULL) == -16 &&
               before == x.calls);
        ++cases;
    }
    setup(0);
    x.f->counter = UINT64_MAX - 1;
    unsigned before = x.calls;
    assert(aefd_fork_arm(x.f, x.aux) == -75 && before == x.calls && !x.closes);
    ++cases;
    setup(0);
    x.write_limit = 367;
    assert(aefd_fork_arm(x.f, x.aux) == -5 && x.closes == 2);
    ++cases;
}
static void pipe_alias_case(void)
{
    setup(0);
    x.mode = 6;
    memset(x.reply, 0, 32);
    put32(x.reply, 4, 1);
    put32(x.reply, 8, 0x79000101);
    put32(x.reply, 12, 0x79000102);
    put32(x.reply, 16, 3);
    put32(x.reply, 20, 4);
    put32(x.reply, 24, 256);
    put32(x.reply, 28, 16);
    int pair[2] = {-1, -1};
    assert(aefd_context_pipe(&x.f->boot.context, pair, 1) == 0);
    assert(pair[0] == 3 && pair[1] == 4 && x.sent[0] == 82);
    assert(aefd_context_open_duplex(&x.f->boot.context, 0) == 5);
    for (unsigned which = 0; which < 2; ++which) {
        unsigned char *raw = which ? x.child : x.startup;
        raw[124] = raw[128] = 2;
        raw[125] = 3;
        raw[129] = 4;
        raw[126] = raw[130] = 1;
        raw[132] = 5;
        raw[135] = 1;
        for (unsigned i = 3; i < 5; ++i) {
            put32(raw, 176 + i * 16, 0x79000100 | (i - 2));
            put32(raw, 180 + i * 16, i);
            put32(raw, 184 + i * 16, i == 3 ? 1 : 2);
            put32(raw, 188 + i * 16, 16);
        }
        put32(raw, 288, 1);
    }
    x.mode = 1;
    x.offset = x.written = 0;
    x.limit = 32;
    assert(become_child() == 0);
    struct aefd_context *c = &x.f->boot.context;
    assert(c->map.slots[3].cloexec == 1 && c->map.slots[4].cloexec == 1);
    assert(c->map.slots[5].reserved == 1 && c->native.generations[0] == 1);
    assert(c->native.sources[3].reference == 0x79000101 &&
           c->native.factory == 0);
    ++cases;
}
#ifdef AEFD_ZSH_HOME_CWD_EXEC_BINDINGS
static void child_cwd_cases(void)
{
    for (unsigned response = 0; response < 8; ++response) {
        setup(0);
        assert(become_child() == 0);
        struct aefd_context *c = &x.f->boot.context;
        assert(c->native.input == 81 && c->native.output == 82 &&
               c->native.factory == 0 && c->mode_control == 0 &&
               c->client.sequence == 1 && c->client.generation == 32 &&
               c->client.workspace == c->workspace &&
               c->client.io.context == &c->native);
        x.mode = 7;
        x.cwd_response = response;
        x.offset = x.written = 0;
        x.limit = 0;
        unsigned char path[6];
        memset(path, 0xa5, sizeof path);
        int64_t result = aefd_context_home_getcwd(c, path);
        assert(x.file_requests == 1 && x.mask == UINT64_MAX);
        if (response <= 1) {
            assert(result == (response ? 6 : 2) &&
                   !memcmp(path, response ? "/home" : "/", (size_t)result));
            assert(c->client.live && !x.closes);
            assert(aefd_context_write(c, 1, (const unsigned char *)"/home",
                                      5) == 5);
            assert(x.terminal_writes == 1);
            assert(aefd_context_home_chdir(c, (const unsigned char *)"/", 1) ==
                   -13);
            assert(aefd_context_open(
                       c, (const unsigned char *)AEFD_HOME_PROFILE_PATH,
                       sizeof(AEFD_HOME_PROFILE_PATH) - 1, 0) == -13);
            unsigned calls = x.calls;
            assert(aefd_fork_arm(x.f, x.aux) == -16 && x.calls == calls);
            assert(c->client.live && !x.closes && c->client.sequence == 4);
            aefd_client_abort(&c->client);
            assert(x.closes == 2);
        } else {
            for (unsigned i = 0; i < sizeof path; ++i)
                assert(path[i] == 0xa5);
            assert(result == (response == 2 ? -13 : -5));
            assert(c->client.live == (response == 2));
            assert(x.closes == (response == 2 ? 0U : 2U));
            if (response != 2) {
                unsigned calls = x.calls;
                assert(aefd_context_home_getcwd(c, path) == -5 &&
                       x.calls == calls);
            } else {
                aefd_client_abort(&c->client);
                assert(x.closes == 2);
            }
        }
        ++cases;
    }
}
#endif
static void exec_cases(void)
{
#ifdef AEFD_ZSH_HOME_CWD_EXEC_BINDINGS
    char arg0[] = "/home/probe";
    char *argv[] = {arg0, NULL}, *envp[] = {NULL};
#else
    char arg0[] = "/inputs/helper", arg1[] = "status", env0[] = "TERM=vt100";
    char *argv[] = {arg0, arg1, NULL}, *envp[] = {env0, NULL};
#endif
    for (unsigned which = 0; which < 5; ++which) {
        setup(0);
        assert(become_child() == 0);
        x.mode = 3;
        x.limit = 32;
        x.offset = x.written = 0;
        assert(aefd_zsh_receipt_encode(x.reply, "AEZER001", 2, -13));
        if (which == 1)
            x.reply[8] ^= 1;
        if (which == 2)
            x.limit = 31;
        if (which == 3)
            x.park_result = 0;
        if (which == 4)
            x.f->boot.context.map.slots[0].kind = 255;
        errno = 71;
        assert(aefd_exec(x.f, x.aux, arg0, argv, envp) == (which ? -5 : -13));
        if (which == 4) {
            assert(x.f->phase == AEFD_FORK_FAILED && x.closes == 2);
            assert(errno == 71 && !x.parks && !x.written && x.f->counter == 1);
            ++cases;
            continue;
        }
        assert(errno == 71 && x.parks == 1 && x.written == 672);
        struct aefd_zsh_snapshot view;
        uint64_t sequence;
        assert(aefd_zsh_exec_decode(x.sent, 672, x.aux, 10, 9, 32, &view,
                                    &sequence));
#ifdef AEFD_ZSH_HOME_CWD_EXEC_BINDINGS
        assert(sequence == 2 && aefd_word(x.sent + 400, 0) == 1 &&
               !aefd_word(x.sent + 400, 1) &&
               !strcmp((char *)x.sent + 416, "/home/probe"));
#else
        assert(sequence == 2 && aefd_word(x.sent + 400, 0) == 2);
        assert(aefd_word(x.sent + 400, 1) == 1 &&
               !strcmp((char *)x.sent + 448, "status"));
#endif
        assert(x.closes == (which ? 2U : 0U));
        ++cases;
    }
}
pid_t aefd_test_waitpid(pid_t, int *, int);
static void wait_cases(void)
{
    for (unsigned which = 0; which < 8; ++which) {
        setup(1);
        memset(x.reply, 0, 32);
        int result = which == 1   ? 0
                     : which == 2 ? -ECHILD
                     : which == 3 ? 11
                                  : 10;
        put32(x.reply, 0, (uint32_t)result);
        if (result > 0)
            put32(x.reply, 4, 7U << 8);
        if (which == 4)
            x.reply[8] = 1;
        if (which == 5)
            put32(x.reply, 4, 0x7f);
        if (which == 6)
            x.limit = 31;
        int status = 0x12345678;
        x.reenter = 1;
        errno = 71;
        pid_t observed = aefd_test_waitpid(-1, &status, 11);
        assert(observed == (which >= 2 && which <= 6 ? -1 : result));
        assert(errno == (which >= 3 && which <= 6 ? EIO
                         : which == 2             ? ECHILD
                                                  : 71));
        assert(status == (which == 0 || which == 7 ? 7 << 8 : 0x12345678));
        assert(x.closes == (which >= 3 && which <= 6 ? 2U : 0U));
        assert(x.sent[0] == 68 && aether_fs_session_u32(x.sent + 8) == 11);
        ++cases;
    }
    setup(1);
    unsigned before = x.calls;
    int status = 123;
    assert(__aether_waitpid(-1, &status, 4) == -EINVAL);
    assert(__aether_waitpid(11, &status, 11) == -EINVAL);
    assert(status == 123 && before == x.calls);
    ++cases;
}
int64_t aefd_startup_native(struct aefd_startup *boot)
{
    assert(boot == aefd_shell_external_startup());
    return aefd_startup_start(boot, call, NULL, x.aux);
}
int __real_main(int argc, char **argv)
{
    ++main_calls;
    assert(argc == 2 && argv == expected_argv && !argv[2]);
    assert(!strcmp(argv[0], "/inputs/helper") && !strcmp(argv[1], "status"));
    assert(aefd_shell_role() == 2 && aefd_zsh_tls_valid());
    assert(aefd_shell_start() == -16);
    return 7;
}
_Noreturn void __real__exit(int status)
{
    if (helper_mode) {
        assert(helper_check && status == 143 && !main_calls && !x.ready);
        assert(x.closes == (helper_mode == 2 ? 0U : 2U));
        printf("selected helper guard %d passed\n", helper_mode);
        fflush(NULL);
        _Exit(0);
    }
    assert(helper_check && status == 7 && main_calls == 1 && x.ready == 1);
    assert(x.transactions == 3 && x.closes == 2 && x.mask == 0x1234);
    assert(aefd_zsh_admit() == -16);
    printf("selected C runtime %u cases passed\n", cases + 1);
    fflush(NULL);
    _Exit(0);
}
int __wrap_main(int, char **);
static void helper_case(void)
{
    memset(&x, 0, sizeof x);
    x.f = aefd_shell_fork_context();
    memset(x.f, 0, sizeof *x.f);
    snapshot(x.startup, 1);
    x.aux = (struct aefd_startup_auxv){0x40000103, 81, 82};
    x.pid = 10;
    x.parent = 9;
    x.limit = 336;
    x.write_limit = 672;
    x.mask = 0x1234;
    if (helper_mode == 1)
        x.startup[7] = '8';
    if (helper_mode == 2) {
        snapshot(x.startup, 0);
        x.aux = (struct aefd_startup_auxv){0x40000102, 71, 72};
        x.pid = 9;
        x.parent = 7;
    }
    if (helper_mode == 3)
        x.limit = 335;
    assert(!aefd_zsh_tls_valid());
    char a[] = "/inputs/helper", b[] = "status";
    char *args[] = {a, b, NULL};
    expected_argv = args;
    helper_check = 1;
    (void)__wrap_main(2, args);
    abort();
}
_Noreturn void __assert_fail(const char *expression, const char *file, int line,
                             const char *function)
{
    printf("assertion %s at %s:%d (%s)\n", expression, file, line, function);
    fflush(NULL);
    _Exit(99);
}
int main(int argc, char **argv)
{
    if (argc == 2) {
        helper_mode = atoi(argv[1]);
        assert(helper_mode >= 1 && helper_mode <= 3);
        helper_case();
    }
    fork_cases();
    pipe_alias_case();
#ifdef AEFD_ZSH_HOME_CWD_EXEC_BINDINGS
    child_cwd_cases();
#endif
    exec_cases();
    wait_cases();
    helper_case();
    printf("selected C runtime %u cases passed\n", cases);
    return 0;
}
unsigned long getauxval(unsigned long type)
{
    assert(type >= 0xa000 && type <= 0xa002);
    return type == 0xa000   ? x.aux.memory
           : type == 0xa001 ? x.aux.input
                            : x.aux.output;
}
