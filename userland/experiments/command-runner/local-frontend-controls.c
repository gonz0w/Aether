/* SPDX-License-Identifier: BSD-2-Clause */
#include "local-frontend.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned scenarios;
static unsigned char texts[6][513];
static size_t lengths[6];
static void need(int ok, const char *oracle)
{
    if (!ok) {
        fprintf(stderr, "ORACLE: %s\n", oracle);
        exit(90);
    }
}
static void word(unsigned char *p, uint32_t value)
{
    for (unsigned i = 0; i < 4; ++i)
        p[i] = (unsigned char)(value >> (8 * i));
}
struct context {
    unsigned admissions, writes, closes, kind, mode;
    size_t used, reply_size;
    int launch, local, known, forbidden;
    unsigned char reply[32];
    struct ar_invocation expected;
};
static int admit(void *context, const struct ar_invocation *invocation,
                 unsigned char reply[32], size_t *size)
{
    struct context *c = context;
    need(c->launch && ++c->admissions == 1, "admission-count");
    need(!memcmp(invocation, &c->expected, sizeof *invocation),
         "copied-invocation");
    memcpy(reply, c->reply, 32);
    *size = c->reply_size;
    return c->known;
}
static struct ar_local_io write_sink(void *context, unsigned sink,
                                     const unsigned char *bytes, size_t size)
{
    struct context *c = context;
    need(c->local, "unexpected-local-output");
    need(!c->forbidden && !c->closes, "no-after-unknown");
    need(sink == (c->kind <= 1 ? 0u : 1u), "selected-stream");
    need(size == lengths[c->kind] - c->used &&
             !memcmp(bytes, texts[c->kind] + c->used, size),
         "fixture-bytes");
    ++c->writes;
    if (c->mode == 1)
        return (struct ar_local_io){1, 0, -28};
    if (c->mode == 3) {
        c->forbidden = 1;
        return (struct ar_local_io){0, 0, -5};
    }
    size_t count = size > 7 ? 7 : size;
    c->used += count;
    return (struct ar_local_io){1, count, 0};
}
static struct ar_local_io close_sink(void *context, unsigned sink)
{
    struct context *c = context;
    need(c->local && !c->forbidden, "no-after-unknown");
    need(sink == c->closes && ++c->closes <= 2, "close-order");
    if (c->mode == 2 && sink == 0)
        return (struct ar_local_io){1, 0, -5};
    if (c->mode == 4 && sink == 0) {
        c->forbidden = 1;
        return (struct ar_local_io){0, 0, -5};
    }
    return (struct ar_local_io){1, 0, 0};
}
static const struct ar_front_ops ops = {admit, {write_sink, close_sink}};
static void scenario(unsigned number, unsigned mode, uint32_t generation)
{
    unsigned char carrier[224] = {0};
    memcpy(carrier, "AERUN001", 8);
    word(carrier + 8, 2);
    memcpy(carrier + 32, "aether-run", 11);
    memcpy(carrier + 64, "--help", 7);
    struct context c = {0};
    c.mode = mode;
    c.known = 1;
    c.reply_size = 32;
    c.local = 1;
    enum ar_action selection = AR_USAGE;
    enum ar_front_action expected = AF_LOCAL;
    if (number == 0)
        selection = AR_HELP;
    else if (number == 1) {
        memset(carrier + 64, 0, 32);
        memcpy(carrier + 64, "--version", 10);
        c.kind = 1;
        selection = AR_VERSION;
    } else if (number <= 6) {
        c.kind = 2;
        memset(carrier + 64, 0, 160);
        if (number == 2)
            word(carrier + 8, 1);
        if (number == 3)
            memcpy(carrier + 64, "--unknown", 10);
        if (number == 4) {
            memcpy(carrier + 64, "--help", 7);
            word(carrier + 8, 3);
            memcpy(carrier + 96, "extra", 6);
        }
        if (number == 6)
            memcpy(carrier + 64, "a/b", 4);
    } else {
        selection = AR_LAUNCH;
        c.launch = 1;
        c.kind = 3;
        memset(carrier + 64, 0, 160);
        word(carrier + 8, 3);
        memcpy(carrier + 64, "bytecount", 10);
        memcpy(carrier + 96, "--decimal", 10);
        c.expected.count = 2;
        memcpy(c.expected.args[0], "bytecount", 10);
        memcpy(c.expected.args[1], "--decimal", 10);
        memcpy(c.expected.environment, "LC_ALL=C", 9);
        word(c.reply, 0xfffffffeu);
        if (number == 8) {
            word(c.reply, 0xfffffff3u);
            c.kind = 4;
        }
        if (number == 9) {
            word(c.reply, 0xfffffff0u);
            c.kind = 5;
        }
        if (number == 10 || number == 16) {
            word(c.reply, 0);
            word(c.reply + 4, 0x73000000u | generation);
            c.local = 0;
            expected = AF_ADMITTED;
            if (number == 16) {
                word(c.reply + 4, 0x73000000u | (3 - generation));
                expected = AF_FAILED;
            }
        } else if (number >= 11 && number <= 17) {
            c.local = 0;
            expected = AF_FAILED;
            if (number == 11)
                word(c.reply, 0xffffffeau);
            if (number == 12)
                word(c.reply, 0xfffffff5u);
            if (number == 13)
                c.known = 0;
            if (number == 14)
                c.reply_size = 31;
            if (number == 15)
                c.reply[31] = 1;
            if (number == 17)
                word(c.reply, 1);
        }
        if (number >= 18 && number <= 23) {
            c.local = c.launch = 0;
            expected = AF_FAILED;
            selection = AR_INVALID_STARTUP;
            if (number == 18)
                carrier[0] = 0;
            if (number == 19)
                carrier[8] = 7;
            if (number == 20)
                carrier[12] = 1;
            if (number == 21)
                memset(carrier + 64, 'x', 32);
            if (number == 22)
                carrier[223] = 1;
            if (number == 23)
                generation = 3;
        }
        if (number == 24) {
            memset(carrier + 64, 0, 160);
            memcpy(carrier + 64, "--", 3);
            memcpy(carrier + 96, "--help", 7);
            memset(&c.expected, 0, sizeof c.expected);
            c.expected.count = 1;
            memcpy(c.expected.args[0], "--help", 7);
            memcpy(c.expected.environment, "LC_ALL=C", 9);
        }
    }
    if (number == 25) {
        memset(carrier + 64, 0, 160);
        word(carrier + 8, 6);
        memcpy(carrier + 64, "--", 3);
        memcpy(carrier + 96, "bytecount", 10);
        memcpy(carrier + 160, "x", 2);
        memcpy(carrier + 192, "--help", 7);
        memset(&c.expected, 0, sizeof c.expected);
        c.expected.count = 4;
        memcpy(c.expected.args[0], "bytecount", 10);
        memcpy(c.expected.args[2], "x", 2);
        memcpy(c.expected.args[3], "--help", 7);
        memcpy(c.expected.environment, "LC_ALL=C", 9);
    }
    if (number == 26 || number == 27) {
        c.local = 0;
        expected = AF_FAILED;
        if (number == 26)
            c.reply_size = 0;
        else
            c.known = 2;
    }
    struct ar_front_state state = {0};
    enum ar_front_action action =
        ar_front_run(&state, carrier, 224, generation, &ops, &c);
    need(action == expected && state.action == expected &&
             state.selection == selection,
         "frontend-action");
    need(c.admissions == (unsigned)c.launch, "admission-count");
    if (c.local) {
        unsigned exit_status = mode          ? 1u
                               : c.kind <= 1 ? 0u
                               : c.kind == 2 ? 64u
                                             : 2u;
        need(state.delivery.exit_status == exit_status, "delivery-status");
        need(state.delivery.kind == (enum ar_local_kind)c.kind, "local-kind");
        need(c.used == (mode == 1 || mode == 3 ? 0 : lengths[c.kind]),
             "delivered-text");
        need(c.closes == (mode == 3   ? 0u
                          : mode == 4 ? 1u
                                      : 2u),
             "cleanup-count");
        if (c.launch)
            need(state.admission_action == AR_REPLY_ERROR &&
                     state.admission.error == (c.kind == 3   ? -2
                                               : c.kind == 4 ? -13
                                                             : -16) &&
                     state.delivery.admission_error == state.admission.error,
                 "rejection-identity");
    } else {
        need(!c.writes && !c.closes && !state.delivery.started,
             "no-local-effects");
        if (expected == AF_ADMITTED)
            need(state.admission.receipt == (0x73000000u | generation) &&
                     !state.admission.error,
                 "admitted-receipt");
        if (number == 11 || number == 12)
            need(state.admission.error == (number == 11 ? -22 : -11),
                 "unclassified-error-retained");
    }
    unsigned calls = c.admissions + c.writes + c.closes;
    struct ar_front_state saved;
    memcpy(&saved, &state, sizeof saved);
    need(ar_front_run(&state, carrier, 224, generation, &ops, &c) ==
                 AF_FAILED &&
             calls == c.admissions + c.writes + c.closes &&
             !memcmp(&saved, &state, sizeof state),
         "frontend-single-use");
    ++scenarios;
}
int main(int argc, char **argv)
{
    need(argc == 7, "fixture-arguments");
    for (unsigned i = 0; i < 6; ++i) {
        FILE *file = fopen(argv[i + 1], "rb");
        need(file != NULL, "fixture-open");
        lengths[i] = fread(texts[i], 1, 513, file);
        need(lengths[i] && lengths[i] <= 512 && !ferror(file), "fixture-size");
        need(fclose(file) == 0, "fixture-close");
    }
    for (uint32_t generation = 1; generation <= 2; ++generation)
        for (unsigned number = 0; number < 28; ++number)
            for (unsigned mode = 0; mode < 5; ++mode)
                scenario(number, mode, generation);
    printf("PASS: %u local frontend scenarios\n", scenarios);
    return 0;
}
