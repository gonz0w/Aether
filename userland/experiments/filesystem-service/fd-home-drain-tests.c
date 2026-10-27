/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual startup/fork/codec/adapters; synthetic authenticated native transport.
 * No guest, scheduler, storage or authority-enforcement qualification. */
#include "fd-home-drain.h"
#include <sched.h>
#include <setjmp.h>
#include <stdlib.h>
int aefd_fork_baseline_main(void);
#define main aefd_fork_baseline_main
#include "fd-fork-stage-tests.c"
#undef main

int aefd_home_drain_test_pipe(int pair[2]);
pid_t aefd_home_drain_test_fork(void);
unsigned long aefd_home_drain_test_auxv(unsigned long);
_Noreturn void aefd_home_drain_test_trap(void);

static unsigned char request[608], response[128], parent_reference[304];
static size_t received, replied, response_length;
static unsigned opens, pipes, forks, native_ready, late_calls, exits, yields;
static unsigned serial, ready_serial, late_serial, checks, traps;
static unsigned test_mode, forbidden_yields, yield_serial;
static int64_t yield_result;
static int child_lane, late, rpc, run_active;
static jmp_buf completed;

#define CHECK(x, label)                                                        \
    do {                                                                       \
        if (!(x)) {                                                            \
            fprintf(stderr, "DRAIN_%s:%d\n", label, __LINE__);                 \
            exit(1);                                                           \
        }                                                                      \
    } while (0)

static void reply_for_request(void)
{
    memset(response, 0, sizeof response);
    if (rpc == 1) {
        CHECK(received == 128 && aefd_word(request, 1) == 10 &&
                  aefd_word(request, 2) == 17 && aefd_word(request, 4) == 0 &&
                  aefd_word(request, 5) == 5 && aefd_word(request, 6) == 1 &&
                  !aefd_word(request, 7) && !memcmp(request + 64, "probe", 5),
              "HOME_OPEN_WRITE_NO_CREATE_NO_CLOEXEC");
        for (unsigned i = 69; i < 128; ++i)
            CHECK(!request[i], "HOME_NAME_PADDING");
        memcpy(response, AEFD_MAGIC, 8);
        aefd_put(response, 2, 17);
        aefd_put(response, 3, aefd_word(request, 3));
        response_length = 64;
        ++opens;
    } else {
        CHECK(rpc == 2 && received == 32 &&
                  aether_fs_session_u32(request) == 82 &&
                  aether_fs_session_u32(request + 4) == UINT32_C(0x76050001) &&
                  aether_fs_session_u32(request + 8) == 1,
              "ORDINARY_PIPE_FACTORY");
        put32(response, 4, 1);
        put32(response, 8, UINT32_C(0x79000101));
        put32(response, 12, UINT32_C(0x79000102));
        put32(response, 16, 3);
        put32(response, 20, 4);
        put32(response, 24, 256);
        put32(response, 28, 16);
        response_length = 32;
        ++pipes;
    }
}
static int64_t drain_call(void *context, uint64_t op, uint64_t cap, uint64_t a,
                          uint64_t b, uint64_t tail)
{
    ++serial;
    CHECK(op != 0x10018, "UNSUPPORTED_LIBC_YIELD_OPCODE");
    CHECK(!exits, "NO_NATIVE_CLEANUP_OR_WAIT_AFTER_EXIT_RETURN");
    CHECK(!run_active || !yields || op == 0x1fffe,
          "NO_EXTRA_OPERATION_AFTER_NATIVE_YIELD");
    if (op == 0x1fffe) {
        CHECK(context == &f && !cap && !a && !b && !tail &&
                  f.fork.boot.identity.slot == 2 && native_ready == 1 &&
                  late_calls == 2 && received == 32 && opens == 1 &&
                  pipes == 1 && forks == 1 && ready_serial < late_serial &&
                  late_serial < serial && !f.new_closes && !f.old_closes &&
                  !f.fork.boot.context.native.active &&
                  !f.fork.boot.context.native.busy &&
                  !f.fork.boot.context.native.retired &&
                  !f.fork.boot.context.native.closed && f.mask == UINT64_MAX,
              "TWO_WRITES_THEN_YIELD_NO_CLEANUP");
        CHECK(!yields || serial == yield_serial + 1,
              "REPEATED_NATIVE_YIELD_NO_EXTRA_OPERATION");
        yield_serial = serial;
        ++yields;
        if (yield_result) {
            CHECK(yields == 1, "NATIVE_YIELD_ERROR_NO_RETRY");
            return yield_result;
        }
        if (yields == 3)
            longjmp(completed,
                    2); /* Bounded host escape, not guest completion. */
        return 0;
    }
    if (op == 0x100e7) {
        CHECK(!cap && !a && !b && !tail && forks == 1 && !native_ready &&
                  !late_calls && f.fork.boot.identity.slot == 1,
              "PARENT_REAL_NORMAL_EXIT_NO_CLEANUP");
        ++exits;
        if (test_mode != 6)
            longjmp(completed, 1);
        return 0;
    }
    if (op == 0x20004) {
        CHECK(!cap && !a && !b && !tail && f.fork.phase == AEFD_FORK_READY &&
                  f.fork.boot.identity.slot == 2 && f.rebinds == 1 &&
                  f.written == 32 &&
                  aefd_fork_ready_decode(f.ready, 32, f.fork.sequence, 10),
              "WIRE_READY32_BEFORE_NATIVE_READY");
        CHECK(f.fork.boot.context.native.active && !late_calls,
              "NATIVE_READY_ORDER");
        ready_serial = serial;
        ++native_ready;
        late = 1;
        received = 0;
        memset(request, 0, sizeof request);
        return test_mode == 1 ? -13 : 0;
    }
    if (!late && f.fork.phase == AEFD_FORK_READY && op == 0x24002)
        CHECK(0, "BYTES_REQUIRE_NATIVE_READY");
    if (late && op == 0x24002) {
        CHECK(cap == 82 && a && b == 16 && !tail && native_ready == 1 &&
                  late_calls < 2 && received + 16 <= 32,
              "AUTHENTICATED_EXACT_WRITE16");
        CHECK(f.fork.boot.context.native.active && ready_serial < serial,
              "READY_PRECEDES_BYTES");
        if (!late_calls)
            late_serial = serial;
        ++late_calls;
        size_t n = test_mode == 5 && late_calls == 2   ? 0
                   : test_mode == 2                    ? 15
                   : test_mode == 3 && late_calls == 2 ? 15
                                                       : 16;
        memcpy(request + received, (const void *)(uintptr_t)a, n);
        received += n;
        return (int64_t)n;
    }
    if (rpc && (op == 0x24001 || op == 0x24002)) {
        CHECK(cap == (op == 0x24001 ? 71U : 72U) && a && b && b <= 16 && !tail,
              "HOME_PIPE_ENDPOINT");
        if (op == 0x24002) {
            CHECK(received + b <= sizeof request, "RPC_BOUND");
            memcpy(request + received, (const void *)(uintptr_t)a, (size_t)b);
            received += (size_t)b;
            if (received == (rpc == 1 ? 128U : 32U))
                reply_for_request();
        } else {
            CHECK(replied + b <= response_length, "RPC_REPLY_BOUND");
            memcpy((void *)(uintptr_t)a, response + replied, (size_t)b);
            replied += (size_t)b;
            if (replied == response_length) {
                rpc = 0;
                received = replied = response_length = 0;
                memset(request, 0, sizeof request);
            }
        }
        return (int64_t)b;
    }
    return call(context, op, cap, a, b, tail);
}
int aefd_home_drain_test_pipe(int pair[2])
{
    CHECK(opens == 1 && !pipes && !forks, "OPEN_BEFORE_PIPE");
    rpc = 2;
    return (int)aefd_context_pipe(&f.fork.boot.context, pair, 0);
}
unsigned long aefd_home_drain_test_auxv(unsigned long key)
{
    return key == 0xa000   ? f.aux.memory
           : key == 0xa001 ? f.aux.input
           : key == 0xa002 ? f.aux.output
                           : 0;
}
pid_t aefd_home_drain_test_fork(void)
{
    CHECK(opens == 1 && pipes == 1 && !forks, "PIPE_BEFORE_FORK");
    CHECK(!aefd_fork_arm(&f.fork, f.aux) && f.written == 304,
          "REAL_PARENT_ARM304");
    memcpy(parent_reference, f.sent, sizeof parent_reference);
    ++forks;
    if (!child_lane) {
        f.offset = 0;
        parent_reply(10);
        CHECK(aefd_fork_parent(&f.fork, 10) == 10, "REAL_PARENT_DISPOSITION");
        return 10;
    }
    struct aefd_startup_auxv grants = child_after_arm();
    /* Actual owner publication preserves all current real records and changes
     * only child identity, file generation and removed factory authority. */
    memcpy(f.child + 48, f.sent + 48, 128);
    aefd_put(f.child + 48, 1, 18);
    memcpy(f.child + 176, f.sent + 176, 120);
    memset(f.child + 296, 0, 8);
    f.read_limit = test_mode == 4 ? 303 : 304;
    f.fork.call = drain_call;
    CHECK(aefd_fork_child(&f.fork, grants, rebind, &f) ==
              (test_mode == 4 ? -5 : 0),
          "ACTUAL_REBIND_STARTUP304");
    if (test_mode == 4)
        return -1;
    return 0;
}
/* Deliberately finite forbidden libc path; never a successful yield double. */
int sched_yield(void)
{
    ++forbidden_yields;
    return -1;
}
_Noreturn void aefd_home_drain_test_trap(void)
{
    CHECK(test_mode == 6 && exits == 1 && !f.old_closes && !f.new_closes &&
              !native_ready && !late_calls && !yields,
          "PARENT_EXIT_RETURN_FAIL_STOP_NO_FINISH_WAIT_CLOSE");
    ++traps;
    longjmp(completed, 3);
}
static void drain_setup(void)
{
    memset(&f, 0, sizeof f);
    startup_frame(f.startup);
    memset(f.startup + 124, 0, 52); /* Console descriptors only. */
    memset(f.startup + 224, 0, 72); /* No existing pipes/history. */
    f.aux = (struct aefd_startup_auxv){UINT64_C(0x40000102), 71, 72};
    f.pid = 9;
    f.parent = 7;
    f.chunk = 16;
    f.read_limit = f.write_limit = 304;
    f.mask = 0x1234;
    received = replied = response_length = 0;
    opens = pipes = forks = native_ready = late_calls = exits = yields = 0;
    serial = ready_serial = late_serial = traps = 0;
    forbidden_yields = yield_serial = 0;
    yield_result = 0;
    late = rpc = 0;
    test_mode = 0;
    CHECK(!aefd_startup_start(&f.fork.boot, drain_call, &f, f.aux),
          "REAL_PARENT_STARTUP");
    f.mode = 1;
    f.offset = f.written = 0;
    f.read_limit = 32;
    f.mask = UINT64_MAX;
    rpc = 1;
}
static int run_lane(unsigned which, int child)
{
    child_lane = child;
    int done = setjmp(completed);
    if (!done) {
        run_active = 1;
        int result = aefd_home_drain_run(&f.fork, which);
        run_active = 0;
        return result;
    }
    run_active = 0;
    CHECK(done == (test_mode == 6 ? 3 : child ? 2 : 1), "LANE_TERMINAL");
    return 0;
}
static void run_cases(void)
{
    for (unsigned which = 1; which <= 8; ++which) {
        drain_setup();
        CHECK(!run_lane(which, 0) && exits == 1 && !late_calls && !yields &&
                  !f.old_closes && !f.new_closes,
              "PARENT_EXITS_WITH_SHARED_FILE_AND_PIPE");
        ++checks;
        drain_setup();
        int result = run_lane(which, 1);
        CHECK(yields == 3 && !forbidden_yields,
              "NATIVE_YIELD_REQUIRED_FORBIDDEN_LIBC_DENIED");
        CHECK(!result && opens == 1 && pipes == 1 && forks == 1 &&
                  received == 32,
              "CHILD_RUN");
        if (which == AEFD_DRAIN_FORK_PREFIX)
            CHECK(!memcmp(request, parent_reference, 32),
                  "CANONICAL_PARENT_PREFIX_ONLY");
        else if (which == AEFD_DRAIN_EXEC_PREFIX)
            CHECK(!memcmp(request, AEFD_EXEC_MAGIC, 8) &&
                      aether_fs_session_u32(request + 12) == 608,
                  "EXEC_PREFIX");
        else if (which == AEFD_DRAIN_STREAM)
            CHECK(aether_fs_session_u32(request) == 2 &&
                      aether_fs_session_u32(request + 4) ==
                          UINT32_C(0x79000102) &&
                      aether_fs_session_u32(request + 8) == 4 &&
                      aether_fs_session_u32(request + 12) == 16 &&
                      !memcmp(request + 16, "AF09-HOME-WRITE\n", 16),
                  "REAL_PIPE_STREAM_REQUEST");
        else
            CHECK(!memcmp(request, AEFD_MAGIC, 8) &&
                      aefd_word(request, 1) == 11 &&
                      aefd_word(request, 2) == 18 && aefd_word(request, 3) == 1,
                  "FILE_PREFIX_ACTUAL_CHILD_GENERATION_SEQUENCE");
        ++checks;
    }
    const int64_t rejected_yields[3] = {-38, -1, 1};
    for (unsigned which = 1; which <= 8; ++which) {
        for (unsigned failure = 0; failure < 3; ++failure) {
            drain_setup();
            yield_result = rejected_yields[failure];
            CHECK(run_lane(which, 1) == 119 && yields == 1 &&
                      !forbidden_yields && serial == yield_serial &&
                      !f.old_closes && !f.new_closes && !exits &&
                      !f.fork.boot.context.native.active,
                  "NATIVE_YIELD_NONZERO119_NO_LATER_EFFECT");
            ++checks;
        }
    }
    for (unsigned mode = 1; mode <= 5; ++mode) {
        drain_setup();
        test_mode = mode;
        CHECK(run_lane(1, 1) != 0 && !yields, "DENIED_INCOMPLETE_NO_YIELD");
        CHECK(mode == 1   ? !late_calls
              : mode == 2 ? late_calls == 1 && received == 15
              : mode == 3 ? late_calls == 2 && received == 31
              : mode == 4 ? !native_ready && !late_calls && f.new_closes == 2
                          : late_calls == 2 && received == 16,
              "READY_SHORT15_SHORT31_STARTUP303_ONLY16_REJECTION");
        ++checks;
    }
    drain_setup();
    test_mode = 6;
    CHECK(!run_lane(1, 0) && exits == 1 && traps == 1 && !yields &&
              !f.old_closes,
          "UNEXPECTED_EXIT_RETURN_FAILS");
    ++checks;
    for (unsigned which = 0; which <= 9; which += 9) {
        drain_setup();
        CHECK(run_lane(which, 0) == 110 && !opens && !pipes && !forks,
              "CLOSED_CASE_SET");
        ++checks;
    }
}

/* Capture existing aefd_exec/native stream writes, then refuse/complete through
 * their unchanged real response paths. Compare the whole initialized reference,
 * not a handwritten approximation of the prefix. */
static unsigned char encoded[608];
static int encode_mode;
static int64_t encode_call(void *context, uint64_t op, uint64_t cap, uint64_t a,
                           uint64_t b, uint64_t tail)
{
    if (op == 0x23003) {
        CHECK(received == 608 && !cap && !a && !b && !tail,
              "REAL_EXEC_COMPLETE_REFERENCE");
        memset(response, 0, 32);
        memcpy(response, "AEEXR001", 8);
        aefd_put(response, 1, f.fork.counter);
        aefd_put(response, 2, (uint64_t)-2LL);
        return -11;
    }
    if (op == 0x24002 || op == 0x24001) {
        CHECK(cap == (op == 0x24002 ? 82U : 81U) && a && b <= 16 && !tail,
              "REFERENCE_ENDPOINT");
        if (op == 0x24002) {
            CHECK(received + b <= sizeof encoded, "REFERENCE_CAPACITY");
            memcpy(encoded + received, (const void *)(uintptr_t)a, (size_t)b);
            received += (size_t)b;
            if (encode_mode == 0 && received == 128) {
                memset(response, 0, sizeof response);
                memcpy(response, AEFD_MAGIC, 8);
                aefd_put(response, 2, 18);
                aefd_put(response, 3, 1);
                aefd_put(response, 4, 16);
                aefd_put(response, 5, 64);
                aefd_put(response + 64, 0, 14);
                aefd_put(response + 64, 2, 790);
                aefd_put(response + 64, 3, 16);
            }
            if (encode_mode == 1 && received == 32) {
                memset(response, 0, 32);
                put32(response, 0, 16);
            }
        } else {
            CHECK(replied + b <= (encode_mode == 0 ? 128U : 32U),
                  "REFERENCE_REPLY_CAPACITY");
            memcpy((void *)(uintptr_t)a, response + replied, (size_t)b);
            replied += (size_t)b;
        }
        return (int64_t)b;
    }
    return call(context, op, cap, a, b, tail);
}
static void reference_cases(void)
{
    for (unsigned which = 1; which <= 4; ++which) {
        drain_setup();
        CHECK(!run_lane(1, 1), "REFERENCE_SETUP_CHILD");
        f.fork.boot.context.native.call = encode_call;
        const int pair[2] = {4, 5};
        struct aefd_home_drain reference;
        if (which == 3)
            continue;
        unsigned actual = which;
        CHECK(aefd_home_drain_reference(&f.fork, &reference, actual, 3, pair,
                                        f.aux),
              "BUILD_FULL_REFERENCE");
        received = replied = 0;
        if (which == 1) {
            const uint64_t args[4] = {0, 16, 0, 0};
            unsigned char header[64];
            CHECK(aefd_request(header, 18, 1, 11, args) &&
                      reference.length == 128 &&
                      !memcmp(reference.bytes, header, 64) &&
                      !memcmp(reference.bytes + 64, "AF09-HOME-WRITE\n", 16),
                  "FILE_COMPLETE_CODEC_AND_BODY");
            for (unsigned i = 80; i < 608; ++i)
                CHECK(!reference.bytes[i], "FILE_INITIALIZED_CONTINUATION");
            encode_mode = 0;
            struct aefd_write_result written;
            CHECK(aefd_home_probe_write(
                      &f.fork.boot.context, 3,
                      (const unsigned char *)"AF09-HOME-WRITE\n", 16,
                      &written) == 16 &&
                      received == 128 && !memcmp(reference.bytes, encoded, 128),
                  "REAL_FILE_WRITER_MATCH_ALL128");
        } else if (which == 4) {
            encode_mode = 1;
            CHECK(aefd_context_write(&f.fork.boot.context, pair[1],
                                     (const unsigned char *)"AF09-HOME-WRITE\n",
                                     16) == 16 &&
                      received == 32 && reference.length == 32 &&
                      !memcmp(reference.bytes, encoded, 32),
                  "REAL_STREAM_ADAPTER_MATCH");
        } else {
            encode_mode = 2;
            char *args[] = {"helper", "hello", NULL};
            char *env[] = {"PATH=/inputs", NULL};
            CHECK(aefd_exec(&f.fork, f.aux, "/inputs/helper", args, env) ==
                          -2 &&
                      received == 608 && reference.length == 608 &&
                      !memcmp(reference.bytes, encoded, 608),
                  "REAL_EXEC_ENCODER_MATCH_ALL608");
        }
        ++checks;
    }
    /* Validate preserved parent304 through the existing decoder and explicitly
     * deny treating its continuation as an authorized child nested request. */
    drain_setup();
    CHECK(!run_lane(3, 1), "FORK_REFERENCE_CHILD");
    struct aefd_fork_view view;
    struct aefd_startup_auxv parent = {UINT64_C(0x40000102), 71, 72};
    CHECK(aefd_fork_decode(parent_reference, 304, parent, 9, 7, &view) &&
              !aefd_fork_decode(parent_reference, 304, f.aux, 10, 9, &view),
          "PARENT_CODEC_VALID_CHILD_AUTHORITY_DENIED");
    ++checks;
    for (unsigned bad = 0; bad < 6; ++bad) {
        drain_setup();
        CHECK(!run_lane(1, 1), "REJECTION_SETUP");
        struct aefd_home_drain reference;
        struct aefd_startup_auxv observed = f.aux;
        int pair[2] = {4, 5};
        if (bad == 0)
            ++observed.memory;
        if (bad == 1)
            ++observed.output;
        if (bad == 2)
            ++f.fork.boot.context.map.generation;
        if (bad == 3)
            ++f.fork.boot.identity.epoch;
        if (bad == 4)
            pair[1] = 4;
        CHECK(!aefd_home_drain_reference(
                  &f.fork, &reference, bad == 5 ? 3U : 1U, 3, pair, observed) &&
                  !reference.length,
              "STALE_IDENTITY_ENDPOINT_PIPE_NESTED_DENIAL");
        ++checks;
    }
}
int main(void)
{
    run_cases();
    reference_cases();
    printf("%u drain host scenarios pass; native enforcement unqualified\n",
           checks);
    return 0;
}
