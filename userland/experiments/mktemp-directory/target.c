/* SPDX-License-Identifier: BSD-2-Clause */
#include "target.h"
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

struct execution {
    const struct amk_bootstrap *bootstrap;
    const struct amk_observations *observations;
    amk_applet_fn applet;
    struct amk_run_result *out;
    struct amk_namespace *borrowed;
    int argc;
    char **argv;
    char original[32];
    size_t length;
    mode_t mask;
    unsigned attempted, finished;
};
static _Thread_local struct execution *active;
static _Thread_local unsigned running;

static size_t payload_length(const char *text)
{
    if (!text)
        return 32;
    size_t length = 0;
    while (length < 32 && text[length])
        length++;
    return length;
}
static int valid_prefix(const struct amk_bootstrap *bootstrap)
{
    size_t length = bootstrap->parent_prefix_length;
    const unsigned char *prefix = bootstrap->parent_prefix;
    return prefix && length > 0 && length < 31 && prefix[0] == '/' &&
           prefix[length - 1] == '/' && !memchr(prefix, 0, length);
}
static int valid_template(const struct amk_bootstrap *bootstrap,
                          const char *text, size_t length)
{
    size_t prefix = bootstrap->parent_prefix_length;
#ifndef AMK_OMIT_PREFIX
    if (!valid_prefix(bootstrap) || length <= prefix ||
        memcmp(text, bootstrap->parent_prefix, prefix))
        return 0;
#else
    (void)valid_prefix;
    if (length <= prefix)
        return 0;
#endif
    size_t leaf = length - prefix;
    if (length > 31 || leaf < 6 || memchr(text + prefix, '/', leaf) ||
        memcmp(text + length - 6, "XXXXXX", 6))
        return 0;
    /* Exactly the selected six trailing placeholders, not a larger suffix. */
    if (leaf > 6 && text[length - 7] == 'X')
        return 0;
    return 1;
}
static int32_t reject(struct amk_run_result *out)
{
    if (out) {
        memset(out, 0, sizeof(*out));
        out->phase = AMK_RUN_ADMISSION;
        out->mutation.progress = AMK_ABSENT;
        out->admission.phase = AMK_PREFLIGHT_REJECTED;
        out->admission.error_kind = AMK_ERROR_INVALID;
        out->admission.errno_value = 22;
        out->command_status = out->final_status = 1;
    }
    return -22;
}
mode_t amk_target_umask(mode_t requested)
{
    if (!active || active->finished) {
        errno = EBADF;
        return (mode_t)-1;
    }
    mode_t previous = active->mask;
    active->mask = requested & (mode_t)0777;
    return previous;
}
int amk_target_name_inputs(const char *text, struct amk_timespec *time,
                           int64_t *identity)
{
    if (!active || active->finished)
        return -EBADF;
    if (active->attempted)
        return -EINVAL;
    if (!text || !time || !identity || payload_length(text) != active->length ||
        memcmp(text, active->original, active->length))
        return -EINVAL;
#ifndef AMK_OMIT_MASK
    if (active->mask != (mode_t)0077)
        return -EINVAL;
#endif
    *time = (struct amk_timespec){0, 0};
    *identity = 0;
#ifndef AMK_NATIVE_MUSL
    const struct amk_observations *observations = active->observations;
    if (!observations || !observations->monotonic ||
        !observations->thread_identity)
        return -EINVAL;
    if (observations->monotonic(observations->state, time))
        return -EIO;
    *identity = observations->thread_identity(observations->state);
#endif
    return 0;
}
int amk_target_create(const char *text, uint32_t mode)
{
    if (!active || active->finished)
        return -EBADF;
    if (!text || active->attempted || mode != 0700 ||
        payload_length(text) != active->length ||
        memcmp(text, active->original, active->length - 6) ||
        memchr(text + active->bootstrap->parent_prefix_length, '/',
               active->length - active->bootstrap->parent_prefix_length))
        return -EINVAL;
#ifndef AMK_OMIT_MASK
    if (active->mask != (mode_t)0077)
        return -EINVAL;
#endif
    active->attempted = 1;
    size_t prefix = active->bootstrap->parent_prefix_length;
    struct amk_mutation_result mutation = {.outcome = AMK_NOT_SENT,
                                           .progress = AMK_ABSENT};
#ifdef AMK_OMIT_MKDIR
    int32_t result = 0;
#else
    int32_t result =
        amk_mkdir(active->borrowed, (const unsigned char *)text + prefix,
                  active->length - prefix, mode, &mutation);
#ifdef AMK_RETRY_COLLISION
    if (result == -17)
        result =
            amk_mkdir(active->borrowed, (const unsigned char *)text + prefix,
                      active->length - prefix, mode, &mutation);
#endif
#endif
    (void)prefix;
    (void)mutation;
#ifdef AMK_OMIT_PROGRESS
    active->out->mutation = (struct amk_mutation_result){
        .outcome = AMK_NOT_SENT, .progress = AMK_ABSENT};
#endif
    return (int)result;
}
int amk_target_terminal_status(int status)
{
    struct execution *execution = active;
    if (!execution)
        return status;
    if (status < 0 || status > 255)
        status = 1;
    int saved_errno = errno;
    execution->out->command_status = (uint32_t)status;
    struct amk_finish_result finish = {0};
    int32_t result = 0;
#ifndef AMK_OMIT_FINISH
    result = amk_finish(execution->borrowed, &finish);
#endif
#ifdef AMK_REPEAT_FINISH
    (void)amk_finish(execution->borrowed, &finish);
#endif
    (void)finish;
    if (result && !status)
        status = 1;
    execution->out->final_status = (uint32_t)status;
    execution->finished = 1;
    active = NULL;
    errno = saved_errno;
    return status;
}
_Noreturn void amk_target_terminal_exit(int status)
{
    struct execution *execution = active;
    status = amk_target_terminal_status(status);
    running = 0;
    if (execution && execution->observations &&
        execution->observations->before_exit) {
        const struct amk_observations *observations = execution->observations;
        if (observations->before_exit(observations->state, execution->out,
                                      (uint32_t)status) &&
            !status)
            status = 1;
        execution->out->final_status = (uint32_t)status;
    }
    _exit(status);
}
static int32_t enter(struct amk_namespace *borrowed, void *application)
{
    struct execution *execution = application;
    execution->borrowed = borrowed;
    active = execution;
    int status = execution->applet(execution->argc, execution->argv);
    if (execution->finished)
        return (int32_t)execution->out->command_status;
    /* A returning fixture has the same final output checks. Actual Toybox's
     * normal terminal path performs these inside upstream xexit instead.
     */
    int flushed = fflush(NULL);
    int failed = ferror(stdout);
#ifndef AMK_OMIT_OUTPUT
    if ((flushed || failed) && !status)
        status = 1;
#else
    (void)flushed;
    (void)failed;
#endif
    (void)amk_target_terminal_status(status);
    return (int32_t)execution->out->command_status;
}
int32_t amk_target_run(const struct amk_bootstrap *bootstrap, int argc,
                       char **argv, char **envp,
                       const struct amk_observations *observations,
                       amk_applet_fn applet, struct amk_run_result *out)
{
    if (running || !bootstrap || !argv || !envp || !applet || !out ||
        argc != 3 || !argv[0] || !argv[1] || !argv[2] || argv[3] ||
        payload_length(argv[0]) > 31 || payload_length(argv[1]) > 31 ||
        payload_length(argv[2]) > 31 || strcmp(argv[0], "mktemp") ||
        strcmp(argv[1], "-d") || !envp[0] || envp[1] ||
        payload_length(envp[0]) > 31 || strcmp(envp[0], "LC_ALL=C") ||
        !valid_template(bootstrap, argv[2], payload_length(argv[2])))
        return reject(out);
#ifndef AMK_NATIVE_MUSL
    if (!observations || !observations->monotonic ||
        !observations->thread_identity)
        return reject(out);
#endif
    struct execution execution = {.bootstrap = bootstrap,
                                  .observations = observations,
                                  .applet = applet,
                                  .out = out,
                                  .argc = argc,
                                  .argv = argv,
                                  .length = strlen(argv[2]),
                                  .mask = 0077};
    memcpy(execution.original, argv[2], execution.length + 1);
    running = 1;
    int32_t result = amk_with_namespace(bootstrap, enter, &execution, out);
    active = NULL;
    running = 0;
    return result;
}
