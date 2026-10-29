/* SPDX-License-Identifier: BSD-2-Clause */
/* Scripted C boundary controls. These ABI doubles are not the Rust service.
 * Compile target.c with fflush/ferror renamed to the declared fixture hooks.
 * Actual Toybox startup and actual Client/service composition are separate
 * gates.
 */
#include "target.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct amk_namespace {
    unsigned live, finished;
};
static struct amk_namespace context;
static struct amk_run_result *live_report;
static struct amk_mutation_result scripted;
static unsigned entries, effects, finishes, closes, flushes, inspections;
static int mutation_error, finish_error, flush_error, stream_error;
static int clock_error, clock_dirty, app_status, short_write, callback_error;
static int check_nested, check_repeat, check_mask, check_wrong_template;
static int native_mode, stderr_error;
#ifdef AMK_TARGET_NATIVE_TESTS
static int native_finish_error, native_finishes;
#endif
static struct amk_timespec clock_value;
static _Thread_local int64_t actual_fixture_tls_identity = 1;
static unsigned char leaf_seen[32];
static size_t leaf_length;
static char output[40];
static const char *case_name;
static struct amk_bootstrap bootstrap;
static struct amk_observations observations;
static char *arguments[] = {"mktemp", "-d", "/home/t.XXXXXX", NULL};
static char *environment[] = {"LC_ALL=C", NULL};

#define CHECK(c)                                                               \
    do {                                                                       \
        if (!(c)) {                                                            \
            fprintf(stderr, "AMK_C_ASSERT %s:%d:%s\n", case_name, __LINE__,    \
                    #c);                                                       \
            exit(1);                                                           \
        }                                                                      \
    } while (0)

int amk_fixture_fflush(FILE *stream);
int amk_fixture_ferror(FILE *stream);
int amk_fixture_fflush(FILE *stream)
{
    CHECK(stream == NULL);
    flushes++;
    return flush_error;
}
int amk_fixture_ferror(FILE *stream)
{
    CHECK(stream == stdout || (native_mode && stream == stderr));
    inspections++;
    return stream == stderr ? stderr_error : stream_error;
}
static int32_t monotonic(void *state, struct amk_timespec *out)
{
    (void)state;
    CHECK(out->seconds == 0 && out->nanoseconds == 0);
    if (!clock_dirty)
        *out = clock_value;
    return clock_error;
}
static int64_t identity(void *state)
{
    (void)state;
    return actual_fixture_tls_identity;
}
static int64_t transfer(void *state, uint32_t writing, unsigned char *bytes,
                        size_t length)
{
    (void)state;
    (void)writing;
    (void)bytes;
    (void)length;
    return -5;
}
static int64_t readiness(void *state, uint32_t writing)
{
    (void)state;
    (void)writing;
    return -5;
}
static void close_endpoints(void *state, int64_t results[2])
{
    (void)state;
    closes++;
    results[0] = 0;
    results[1] = 0;
}
int32_t amk_mkdir(struct amk_namespace *borrowed, const unsigned char *leaf,
                  size_t length, uint32_t mode, struct amk_mutation_result *out)
{
    CHECK(borrowed == &context && context.live && !context.finished);
    CHECK(mode == 0700 && length < sizeof(leaf_seen));
    effects++;
    memcpy(leaf_seen, leaf, length);
    leaf_length = length;
    *out = scripted;
    live_report->mutation = *out;
    return mutation_error;
}
int32_t amk_finish(struct amk_namespace *borrowed,
                   struct amk_finish_result *out)
{
    CHECK(borrowed == &context && context.live);
    finishes++;
    if (!context.finished) {
        context.finished = 1;
        int64_t results[2] = {0, 0};
        close_endpoints(NULL, results);
        live_report->finalization = (struct amk_finish_result){
            .phase = AMK_FINISHED,
            .disconnect_attempted = 1,
            .error_kind = finish_error ? AMK_ERROR_TRANSPORT : AMK_ERROR_NONE,
            .errno_value = finish_error ? 5u : 0u,
            .error_value = finish_error,
            .cleanup_present = 1,
            .cleanup_uncertain = finish_error ? 1u : 0u,
            .reader_close = results[0],
            .writer_close = results[1]};
    }
    *out = live_report->finalization;
    return finish_error;
}
int32_t amk_with_namespace(const struct amk_bootstrap *boot, amk_entry_fn entry,
                           void *application, struct amk_run_result *out)
{
    CHECK(!context.live && boot == &bootstrap);
    memset(out, 0, sizeof(*out));
    out->mutation.progress = AMK_ABSENT;
    out->phase = AMK_RUN_ENTRY;
    out->admission.phase = AMK_ADMITTED;
    out->admission.endpoints_accepted = 1;
    context = (struct amk_namespace){.live = 1};
    live_report = out;
    entries++;
    int32_t status = entry(&context, application);
    /* C target entry must finish before return; this wrapper fallback cannot
     * establish its preterminal finalization order. */
    CHECK(context.finished);
    struct amk_finish_result cached = out->finalization;
    unsigned already_finished = context.finished;
    struct amk_finish_result receipt;
    (void)amk_finish(&context, &receipt);
    if (already_finished)
        CHECK(!memcmp(&receipt, &cached, sizeof(receipt)));
    out->command_status = (uint32_t)status;
    out->final_status = status ? (uint32_t)status : (finish_error ? 1u : 0u);
    out->phase = AMK_RUN_FINISHED;
    context.live = 0;
    return 0;
}
int32_t amk_with_native_namespace(const struct amk_bootstrap *boot,
                                  amk_verify_fn verify, amk_entry_fn entry,
                                  void *application, struct amk_run_result *out)
{
    CHECK(verify != NULL);
    /* ABI double only. Native Client/EOF verification is a separate Rust
     * actual-body gate; legacy cases never select this constructor. */
    return amk_with_namespace(boot, entry, application, out);
}
static int applet(int argc, char **argv)
{
    CHECK(argc == 3 && !strcmp(argv[0], "mktemp"));
    if (check_nested) {
        struct amk_run_result nested;
        CHECK(amk_target_run(&bootstrap, argc, argv, environment, &observations,
                             applet, &nested) < 0);
        CHECK(entries == 1);
    }
    if (check_mask) {
        CHECK(amk_target_umask(0) == 0077);
        CHECK(amk_target_umask(0077) == 0);
    }
    char path[32];
    memcpy(path, argv[2], strlen(argv[2]) + 1);
    if (check_wrong_template)
        path[6] = 'u';
    char *created = amk_checked_mkdtemp(path);
    if (!created)
        return 1;
    CHECK(created == path);
    /* Independent delivered byte oracle; an injected short write becomes
     * status. Real libc output failures in Toybox require the separate applet
     * witness.
     */
    if (short_write)
        return 1;
    CHECK(snprintf(output, sizeof(output), "%s\n", path) > 0);
    char second[] = "/home/t.XXXXXX";
    CHECK(amk_checked_mkdtemp(second) == NULL && errno == EINVAL);
    CHECK(!strcmp(second, "/home/t.XXXXXX"));
    int status = callback_error ? 1 : app_status;
    if (check_repeat) {
        CHECK(amk_target_terminal_status(status) == status);
        CHECK(amk_target_terminal_status(status) == status);
        errno = 0;
        CHECK(amk_checked_mkdtemp(path) == NULL && errno == EBADF);
    }
    return status;
}
static void reset(const char *name)
{
    case_name = name;
    context = (struct amk_namespace){0};
    scripted = (struct amk_mutation_result){
        .outcome = AMK_COMPLETED_SUCCESS, .progress = AMK_COMPLETED, .txg = 9};
    entries = effects = finishes = closes = flushes = inspections = 0;
    mutation_error = finish_error = flush_error = stream_error = 0;
    clock_error = clock_dirty = app_status = short_write = callback_error = 0;
    check_nested = check_repeat = check_mask = check_wrong_template = 0;
    actual_fixture_tls_identity = 1;
    clock_value = (struct amk_timespec){0, 0};
    leaf_length = 0;
    memset(leaf_seen, 0, sizeof(leaf_seen));
    memset(output, 0, sizeof(output));
    arguments[0] = "mktemp";
    arguments[1] = "-d";
    arguments[2] = "/home/t.XXXXXX";
    environment[0] = "LC_ALL=C";
    environment[1] = NULL;
    bootstrap = (struct amk_bootstrap){
        .io = {NULL, transfer, readiness, close_endpoints},
        .epoch = 1,
        .parent_prefix = (const unsigned char *)"/home/",
        .parent_prefix_length = 6};
    observations = (struct amk_observations){
        .state = NULL, .monotonic = monotonic, .thread_identity = identity};
}
static struct amk_run_result run(void)
{
    struct amk_run_result out;
    CHECK(amk_target_run(&bootstrap, 3, arguments, environment, &observations,
                         applet, &out) == 0);
    CHECK(closes == 1);
    return out;
}
static void pass(void) { printf("AMK_C_PASS %s\n", case_name); }
static void exact_path_one_effect(void)
{
    reset("exact_path_one_effect");
    check_mask = 1;
    struct amk_run_result out = run();
    CHECK(!strcmp(output, "/home/t.BAACAA\n"));
    CHECK(leaf_length == 8 && !memcmp(leaf_seen, "t.BAACAA", 8));
    CHECK(effects == 1 && out.mutation.outcome == AMK_COMPLETED_SUCCESS);
    CHECK(out.mutation.progress == AMK_COMPLETED && out.mutation.txg == 9);
    CHECK(out.command_status == 0 && out.final_status == 0);
    CHECK(flushes == 1 && inspections == 1);
    pass();
}
static void admission_denied(void)
{
    const char *bad[] = {
        "/evil/t.XXXXXX",  "/home/a/bXXXXXX",
        "/home/..",        "/home/t.XXXXX",
        "/home/t.XXXXXXX", "/home/abcdefghijklmnopqrstu.XXXXXX"};
    for (size_t i = 0; i < sizeof(bad) / sizeof(bad[0]); i++) {
        reset("admission_denied");
        arguments[2] = (char *)bad[i];
        struct amk_run_result out;
        CHECK(amk_target_run(&bootstrap, 3, arguments, environment,
                             &observations, applet, &out) < 0);
        CHECK(entries == 0 && effects == 0 && closes == 0);
        CHECK(out.mutation.outcome == AMK_NOT_SENT);
    }
    for (unsigned i = 0; i < 4; i++) {
        reset("admission_denied");
        if (i == 0)
            arguments[0] = "toybox";
        if (i == 1)
            arguments[1] = "--directory";
        if (i == 2)
            environment[0] = "TMPDIR=/home";
        if (i == 3)
            environment[1] = "HOME=/home";
        struct amk_run_result out;
        CHECK(amk_target_run(&bootstrap, 3, arguments, environment,
                             &observations, applet, &out) < 0);
        CHECK(entries == 0 && effects == 0 && closes == 0);
    }
    pass();
}
static void clock_tls_mask_denied(void)
{
    for (unsigned i = 0; i < 7; i++) {
        reset("clock_tls_mask_denied");
        if (i == 0)
            clock_error = -1;
        if (i == 1)
            clock_value.seconds = -1;
        if (i == 2)
            clock_value.nanoseconds = -1;
        if (i == 3)
            clock_value.nanoseconds = 1000000000;
        if (i == 4)
            actual_fixture_tls_identity = 0;
        if (i == 5)
            actual_fixture_tls_identity = -1;
        if (i == 6)
            check_wrong_template = 1;
        struct amk_run_result out = run();
        CHECK(effects == 0 && out.final_status != 0);
    }
    pass();
}
static int wrong_mask_applet(int argc, char **argv)
{
    (void)argc;
    CHECK(amk_target_umask(0) == 0077);
    char path[32];
    strcpy(path, argv[2]);
    CHECK(amk_checked_mkdtemp(path) == NULL && errno == EINVAL);
    return 1;
}
static void mask_denied(void)
{
    reset("mask_denied");
    struct amk_run_result out;
    CHECK(amk_target_run(&bootstrap, 3, arguments, environment, &observations,
                         wrong_mask_applet, &out) == 0);
    CHECK(effects == 0 && out.final_status != 0 && closes == 1);
    pass();
}
static void collision_once(void)
{
    reset("collision_once");
    mutation_error = -17;
    scripted = (struct amk_mutation_result){
        AMK_REPORTED, AMK_UNASSIGNED, AMK_ERROR_REMOTE, 17, -17, 0, 0};
    struct amk_run_result out = run();
    CHECK(effects == 1 && errno == EEXIST && !*output);
    CHECK(out.mutation.error_value == -17 && out.mutation.errno_value == 17);
    CHECK(out.mutation.outcome == AMK_REPORTED);
    pass();
}
static void typed_progress_preserved(void)
{
    const struct amk_mutation_result cases[] = {
        {AMK_NOT_SENT, AMK_ABSENT, AMK_ERROR_CLOSED, 9, 0, 0, 0},
        {AMK_REPORTED, AMK_UNASSIGNED, AMK_ERROR_REMOTE, 5, -5, 0, 0},
        {AMK_REPORTED, AMK_COMMITTED, AMK_ERROR_REMOTE, 5, -5, 0, 0},
        {AMK_REPORTED, AMK_COMPLETED, AMK_ERROR_REMOTE, 5, -5, 7, 0},
        {AMK_REPORTED, AMK_PROGRESS_UNKNOWN, AMK_ERROR_REMOTE, 5, -5, 0, 0},
        {AMK_UNKNOWN, AMK_PROGRESS_UNKNOWN, AMK_ERROR_TRANSPORT, 5, -5, 0, 0}};
    for (size_t i = 0; i < sizeof(cases) / sizeof(cases[0]); i++) {
        reset("typed_progress_preserved");
        scripted = cases[i];
        mutation_error = -5;
        struct amk_run_result out = run();
        CHECK(!memcmp(&out.mutation, &cases[i], sizeof(cases[i])));
        CHECK(effects == 1 && out.final_status != 0 && !*output);
    }
    pass();
}
static void completed_output_failure(void)
{
    for (unsigned i = 0; i < 6; i++) {
        reset("completed_output_failure");
        if (i == 0)
            short_write = 1;
        if (i == 1)
            callback_error = 1;
        if (i == 2)
            flush_error = EOF;
        if (i == 3)
            stream_error = 1;
        if (i == 4)
            finish_error = -5;
        if (i == 5) {
            finish_error = -5;
            app_status = 37;
        }
        struct amk_run_result out = run();
        CHECK(effects == 1 && out.mutation.progress == AMK_COMPLETED);
        CHECK(out.mutation.txg == 9 && out.final_status != 0);
        if (i == 4)
            CHECK(out.command_status == 0);
        if (i == 5)
            CHECK(out.command_status == 37 && out.final_status == 37);
    }
    pass();
}
static void cleanup_reentry_cleared_tls(void)
{
    reset("cleanup_reentry_cleared_tls");
    check_nested = check_repeat = 1;
    struct amk_run_result out = run();
    CHECK(effects == 1 && closes == 1 && out.final_status == 0);
    /* Repeated finish calls are valid. This scripted ABI fixture checks one
     * close and a retained receipt, not real Rust endpoint semantics.
     * AMK_REPEAT_FINISH is a positive idempotence control.
     */
    CHECK(finishes >= 1);
    CHECK(out.finalization.phase == AMK_FINISHED);
    CHECK(out.finalization.cleanup_present == 1);
    CHECK(out.finalization.cleanup_uncertain == 0);
    CHECK(out.finalization.reader_close == 0);
    CHECK(out.finalization.writer_close == 0);
    char path[] = "/home/t.XXXXXX";
    CHECK(amk_checked_mkdtemp(path) == NULL && errno == EBADF);
    CHECK(amk_target_terminal_status(29) == 29);
    CHECK(closes == 1 && effects == 1);
    pass();
}
#ifdef AMK_TARGET_NATIVE_TESTS
static int64_t native_verify(void *state)
{
    (void)state;
    return 0;
}
static int32_t native_finish(void *state)
{
    (void)state;
    CHECK(context.finished && closes == 1);
    native_finishes++;
    return native_finish_error;
}
static void native_terminal(uint32_t status)
{
    CHECK(native_finishes == 1 && inspections == 2 && closes == 1);
    CHECK(status == 1);
    char path[] = "/home/t.XXXXXX";
    CHECK(amk_checked_mkdtemp(path) == NULL && errno == EBADF);
    puts("AMK_C_PASS native_terminal_stderr_and_order");
    exit(0);
}
static int native_applet(int argc, char **argv)
{
    CHECK(argc == 3 && argv != NULL);
#ifdef AMK_TARGET_NATIVE_TERMINAL
    amk_target_terminal_exit(0);
#endif
    return 0;
}
static void native_finalization_cases(void)
{
    const struct amk_native_hooks hooks = {native_verify, native_finish,
                                           native_terminal, NULL};
    for (unsigned failure = 0; failure < 4; ++failure) {
        reset("native_finalization_cases");
        native_mode = 1;
        native_finishes = 0;
        stderr_error = failure == 0;
        native_finish_error = failure == 1 ? -5 : 0;
        finish_error = failure == 2 ? -5 : 0;
        flush_error = failure == 3 ? EOF : 0;
        struct amk_run_result out;
        CHECK(amk_target_run_native(&bootstrap, 3, arguments, environment,
                                    &hooks, native_applet, &out) == 0);
        CHECK(out.command_status == 0 && out.final_status == 1);
        CHECK(native_finishes == 1 && closes == 1 && inspections == 2);
        char path[] = "/home/t.XXXXXX";
        CHECK(amk_checked_mkdtemp(path) == NULL && errno == EBADF);
    }
    pass();
}
#endif
int main(void)
{
    exact_path_one_effect();
    admission_denied();
    clock_tls_mask_denied();
    mask_denied();
    collision_once();
    typed_progress_preserved();
    completed_output_failure();
    cleanup_reentry_cleared_tls();
#ifdef AMK_TARGET_NATIVE_TESTS
    native_finalization_cases();
#endif
    return 0;
}
