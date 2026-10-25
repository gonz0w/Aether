/* SPDX-License-Identifier: BSD-2-Clause */
#include "local-output.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned scenarios;
static void need(int ok, const char *oracle)
{
    if (!ok) {
        fprintf(stderr, "ORACLE: %s\n", oracle);
        exit(90);
    }
}
struct fixture {
    unsigned char text[513], sinks[2][512];
    size_t size, used, chunk, prefix;
    unsigned sink, writes, closes;
    int write_fault, close_fault, close_at, forbidden;
};
static struct ar_local_io write_sink(void *context, unsigned sink,
                                     const unsigned char *text, size_t size)
{
    struct fixture *f = context;
    need(!f->forbidden, "no-after-unknown");
    need(sink == f->sink, "stream-separation");
    need(text == f->text + f->used && size == f->size - f->used,
         "unwritten-suffix");
    ++f->writes;
    need(f->writes <= f->size + 1, "write-bound");
    if (f->write_fault && f->used == f->prefix) {
        if (f->write_fault == 1)
            return (struct ar_local_io){1, 0, 0};
        if (f->write_fault == 2)
            return (struct ar_local_io){1, 0, -28};
        f->forbidden = 1;
        if (f->write_fault == 3)
            return (struct ar_local_io){0, 0, -5};
        if (f->write_fault == 4)
            return (struct ar_local_io){1, size + 1, 0};
        if (f->write_fault == 5)
            return (struct ar_local_io){1, 1, -5};
        if (f->write_fault == 6)
            return (struct ar_local_io){2, 0, 0};
        if (f->write_fault == 7)
            return (struct ar_local_io){1, 0, 1};
        return (struct ar_local_io){1, 0, -4096};
    }
    size_t count = size < f->chunk ? size : f->chunk;
    if (f->write_fault && count > f->prefix - f->used)
        count = f->prefix - f->used;
    need(count && f->used + count <= sizeof f->sinks[0], "sink-bound");
    memcpy(f->sinks[sink] + f->used, text, count);
    f->used += count;
    return (struct ar_local_io){1, count, 0};
}
static struct ar_local_io close_sink(void *context, unsigned sink)
{
    struct fixture *f = context;
    need(!f->forbidden, "no-after-unknown");
    need(sink == f->closes && ++f->closes <= 2, "close-once-order");
    if ((int)sink == f->close_at && f->close_fault) {
        if (f->close_fault == 1)
            return (struct ar_local_io){1, 0, -5};
        f->forbidden = 1;
        return f->close_fault == 2 ? (struct ar_local_io){0, 0, -5}
                                   : (struct ar_local_io){1, 1, 0};
    }
    return (struct ar_local_io){1, 0, 0};
}
static const struct ar_local_ops ops = {write_sink, close_sink};
static void scenario(struct fixture *f, enum ar_local_kind kind)
{
    memset(f->sinks, 0, sizeof f->sinks);
    f->used = 0;
    f->writes = f->closes = 0;
    f->forbidden = 0;
    f->sink = kind <= AL_VERSION ? 0u : 1u;
    const int32_t errors[] = {0, 0, 0, -2, -13, -16};
    const unsigned statuses[] = {0, 0, 64, 2, 2, 2};
    struct ar_local_plan p = {kind, f->text, f->size, errors[kind]};
    struct ar_local_state state = {0};
    unsigned result = ar_local_deliver(&state, &p, &ops, f);
    unsigned expected = f->write_fault || f->close_fault ? 1u : statuses[kind];
    need(result == expected && state.exit_status == expected,
         "outcome-precedence");
    need(state.kind == kind && state.intended_exit == statuses[kind] &&
             state.admission_error == errors[kind],
         "original-outcome");
    size_t confirmed = f->write_fault ? f->prefix : f->size;
    need(f->used == confirmed && state.delivered == confirmed &&
             !memcmp(f->sinks[f->sink], f->text, confirmed),
         "exact-prefix");
    for (size_t i = 0; i < 512; ++i) {
        need(!f->sinks[1 - f->sink][i], "other-sink-empty");
        if (i >= confirmed)
            need(!f->sinks[f->sink][i], "no-extra-bytes");
    }
    unsigned closes = f->write_fault >= 3   ? 0u
                      : f->close_fault >= 2 ? (unsigned)f->close_at + 1
                                            : 2u;
    need(f->closes == closes, "cleanup-count");
    for (unsigned i = 0; i < 2; ++i) {
        enum ar_local_close close_result =
            i >= closes ? AL_UNATTEMPTED
            : f->close_fault && (int)i == f->close_at
                ? (f->close_fault == 1 ? AL_CLOSE_FAILED : AL_CLOSE_UNKNOWN)
                : AL_CLOSED;
        need(state.closes[i] == close_result, "cleanup-facts");
        int32_t error =
            close_result == AL_CLOSE_FAILED ||
                    (close_result == AL_CLOSE_UNKNOWN && f->close_fault == 2)
                ? -5
                : 0;
        need(state.close_error[i] == error, "close-error-identity");
    }
    enum ar_local_failure failure = !f->write_fault       ? AL_NONE
                                    : f->write_fault == 1 ? AL_ZERO
                                    : f->write_fault == 2 ? AL_WRITE_ERROR
                                                          : AL_UNKNOWN;
    need(state.failure == failure, "delivery-facts");
    int32_t error = f->write_fault == 2                          ? -28
                    : f->write_fault == 3 || f->write_fault == 5 ? -5
                    : f->write_fault == 7                        ? 1
                    : f->write_fault == 8                        ? -4096
                                                                 : 0;
    need(state.write_error == error, "write-error-identity");
    struct ar_local_state saved;
    memcpy(&saved, &state, sizeof saved);
    unsigned calls = f->writes + f->closes;
    need(ar_local_deliver(&state, &p, &ops, f) == 1 &&
             f->writes + f->closes == calls &&
             !memcmp(&saved, &state, sizeof state),
         "single-use");
    ++scenarios;
}
int main(int argc, char **argv)
{
    need(argc == 7, "fixture-arguments");
    for (unsigned k = 0; k < 6; ++k) {
        struct fixture f = {0};
        FILE *input = fopen(argv[k + 1], "rb");
        need(input != NULL, "fixture-open");
        f.size = fread(f.text, 1, sizeof f.text, input);
        need(!ferror(input) && f.size && f.size <= 512, "fixture-size");
        need(fclose(input) == 0, "fixture-close");
        for (f.chunk = 1; f.chunk <= f.size; ++f.chunk)
            scenario(&f, (enum ar_local_kind)k);
        f.chunk = 7;
        for (f.write_fault = 1; f.write_fault <= 8; ++f.write_fault)
            for (f.prefix = 0; f.prefix < f.size; ++f.prefix)
                scenario(&f, (enum ar_local_kind)k);
        for (f.write_fault = 0; f.write_fault <= 2; ++f.write_fault)
            for (f.close_at = 0; f.close_at < 2; ++f.close_at)
                for (f.close_fault = 1; f.close_fault <= 3; ++f.close_fault) {
                    f.prefix = f.size / 2;
                    scenario(&f, (enum ar_local_kind)k);
                }
    }
    struct fixture f = {0};
    struct ar_local_plan p = {AL_HELP, f.text, 1, 0};
    for (unsigned i = 0; i < 8; ++i) {
        struct ar_local_state s = {0};
        struct ar_local_plan bad = p;
        struct ar_local_ops callbacks = ops;
        if (i == 0)
            bad.kind = (enum ar_local_kind)99;
        if (i == 1)
            bad.text = NULL;
        if (i == 2)
            bad.size = 0;
        if (i == 3)
            bad.size = 513;
        if (i == 4)
            bad.admission_error = -2;
        if (i == 5)
            callbacks.write = NULL;
        if (i == 6)
            callbacks.close = NULL;
        need(ar_local_deliver(&s, i == 7 ? NULL : &bad, &callbacks, &f) == 1 &&
                 s.started && s.failure == AL_INVALID && !f.writes && !f.closes,
             "invalid-no-effects");
        ++scenarios;
    }
    struct ar_local_state invalid = {0};
    need(ar_local_deliver(NULL, &p, &ops, &f) == 1 &&
             ar_local_deliver(&invalid, &p, NULL, &f) == 1 && !f.writes &&
             !f.closes,
         "null-no-effects");
    scenarios += 2;
    printf("PASS: %u local delivery scenarios\n", scenarios);
    return 0;
}
