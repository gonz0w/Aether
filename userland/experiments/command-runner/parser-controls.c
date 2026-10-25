/* SPDX-License-Identifier: BSD-2-Clause */
#include "runner-parse.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned checks;
static void need(int ok, const char *name)
{
    if (!ok) {
        fprintf(stderr, "ORACLE: %s\n", name);
        exit(90);
    }
    ++checks;
}
static struct ar_startup start(unsigned count, const char *const args[])
{
    struct ar_startup value = {0};
    value.count = count;
    for (unsigned i = 0; i < count; ++i) {
        size_t n = strlen(args[i]);
        need(n < AR_SLOT_SIZE, "fixture-slot");
        memcpy(value.args[i], args[i], n + 1);
    }
    return value;
}
static void encode(unsigned char record[AR_CARRIER_SIZE],
                   const struct ar_startup *value)
{
    memset(record, 0, AR_CARRIER_SIZE);
    memcpy(record, "AERUN001", 8);
    for (unsigned i = 0; i < 4; ++i)
        record[8 + i] = (unsigned char)(value->count >> (i * 8));
    memcpy(record + 32, value->args, sizeof value->args);
}
static void rejected(const unsigned char *record, size_t size,
                     const char *oracle)
{
    struct ar_startup out, before;
    memset(&out, 0xa5, sizeof out);
    memcpy(&before, &out, sizeof before);
    need(!ar_decode(record, size, &out), oracle);
    need(!memcmp(&out, &before, sizeof out), "decode-atomic");
}
int main(void)
{
    static const struct {
        unsigned count, first;
        enum ar_action action;
        const char *args[6];
    } cases[] = {
        {1, 0, AR_USAGE, {"aether-run"}},
        {2, 0, AR_HELP, {"aether-run", "--help"}},
        {2, 0, AR_VERSION, {"aether-run", "--version"}},
        {3, 0, AR_USAGE, {"aether-run", "--help", "extra"}},
        {2, 0, AR_USAGE, {"aether-run", "--unknown"}},
        {2, 0, AR_USAGE, {"aether-run", "--"}},
        {2, 0, AR_USAGE, {"aether-run", ""}},
        {2, 0, AR_USAGE, {"aether-run", "a/b"}},
        {3, 0, AR_USAGE, {"aether-run", "--", ""}},
        {2, 1, AR_LAUNCH, {"aether-run", "bytecount"}},
        {3, 1, AR_LAUNCH, {"aether-run", "bytecount", "--help"}},
        {3, 1, AR_LAUNCH, {"aether-run", "bytecount", "--version"}},
        {4, 1, AR_LAUNCH, {"aether-run", "bytecount", "--", "-x"}},
        {5, 1, AR_LAUNCH, {"aether-run", "bytecount", "", "a b", "$x;*"}},
        {6,
         2,
         AR_LAUNCH,
         {"aether-run", "--", "bytecount", "--decimal", "",
          "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}},
        {6, 0, AR_USAGE, {"aether-run", "bytecount", "1", "2", "3", "4"}},
        {3, 2, AR_LAUNCH, {"aether-run", "--", "--help"}},
        {3, 0, AR_USAGE, {"aether-run", "--", "/bin/sh"}},
        {3, 1, AR_LAUNCH, {"aether-run", "unknown", "LC_ALL=wrong"}},
    };
    for (unsigned i = 0; i < sizeof cases / sizeof cases[0]; ++i) {
        struct ar_startup value = start(cases[i].count, cases[i].args), decoded;
        unsigned char record[AR_CARRIER_SIZE];
        encode(record, &value);
        need(ar_decode(record, sizeof record, &decoded), "valid-carrier");
        memset(record, 0xcc, sizeof record);
        need(!memcmp(&value, &decoded, sizeof value), "owned-startup-copy");
        struct ar_invocation out, before;
        memset(&out, 0xa5, sizeof out);
        memcpy(&before, &out, sizeof before);
        enum ar_action action = ar_select(&decoded, &out);
        need(action == cases[i].action, "selector-action");
        if (action == AR_LAUNCH) {
            struct ar_invocation expected = {0};
            expected.count = cases[i].count - cases[i].first;
            for (unsigned j = 0; j < expected.count; ++j)
                strcpy(expected.args[j], cases[i].args[cases[i].first + j]);
            strcpy(expected.environment, "LC_ALL=C");
            memset(&decoded, 0xdd, sizeof decoded);
            need(!memcmp(&out, &expected, sizeof out),
                 "owned-exact-invocation");
        } else {
            need(!memcmp(&out, &before, sizeof out), "selector-no-publication");
        }
    }
    const char *const args[] = {"aether-run", "bytecount"};
    struct ar_startup value = start(2, args), output;
    unsigned char record[AR_CARRIER_SIZE], bad[AR_CARRIER_SIZE + 1];
    encode(record, &value);
    for (unsigned i = 0; i < AR_CARRIER_SIZE; ++i)
        rejected(record, i, "short-record");
    memcpy(bad, record, sizeof record);
    rejected(bad, sizeof bad, "long-record");
    rejected(NULL, AR_CARRIER_SIZE, "null-record");
    need(!ar_decode(record, sizeof record, NULL), "null-output");
    for (unsigned i = 0; i < 8; ++i) {
        memcpy(bad, record, sizeof record);
        bad[i] ^= 1;
        rejected(bad, sizeof record, "magic");
    }
    for (unsigned i = 12; i < 32; ++i) {
        memcpy(bad, record, sizeof record);
        bad[i] = 1;
        rejected(bad, sizeof record, "reserved");
    }
    for (unsigned i = 96; i < AR_CARRIER_SIZE; ++i) {
        memcpy(bad, record, sizeof record);
        bad[i] = 1;
        rejected(bad, sizeof record, "unused-slot");
    }
    for (unsigned i = 0; i < 3; ++i) {
        memcpy(bad, record, sizeof record);
        memset(bad + 8, i == 2 ? 255 : 0, 4);
        if (i == 1)
            bad[8] = 7;
        rejected(bad, sizeof record, "count");
    }
    for (unsigned slot = 0; slot < 2; ++slot) {
        memcpy(bad, record, sizeof record);
        memset(bad + 32 + slot * 32, 'X', 32);
        rejected(bad, sizeof record, "unterminated");
        memcpy(bad, record, sizeof record);
        bad[63 + slot * 32] = 1;
        rejected(bad, sizeof record, "active-padding");
    }
    const char *const full_args[] = {"aether-run", "--", "bytecount",
                                     "",           "a",  "b"};
    struct ar_startup full = start(6, full_args);
    unsigned char full_record[AR_CARRIER_SIZE];
    encode(full_record, &full);
    for (unsigned slot = 0; slot < AR_STARTUP_ARGS; ++slot) {
        memcpy(bad, full_record, sizeof full_record);
        memset(bad + 32 + slot * 32, 'X', 32);
        rejected(bad, sizeof full_record, "all-active-unterminated");
        for (unsigned offset = (unsigned)strlen(full.args[slot]) + 1;
             offset < AR_SLOT_SIZE; ++offset) {
            memcpy(bad, full_record, sizeof full_record);
            bad[32 + slot * 32 + offset] = 1;
            rejected(bad, sizeof full_record, "all-active-padding");
        }
    }
    memcpy(bad, record, sizeof record);
    bad[32] = 'X';
    rejected(bad, sizeof record, "argv0");
    struct ar_invocation invocation, before;
    memset(&invocation, 0xa5, sizeof invocation);
    memcpy(&before, &invocation, sizeof before);
    need(ar_select(NULL, &invocation) == AR_INVALID_STARTUP, "null-startup");
    need(ar_select(&value, NULL) == AR_INVALID_STARTUP, "null-invocation");
    value.count = 7;
    need(ar_select(&value, &invocation) == AR_INVALID_STARTUP, "typed-count");
    need(!memcmp(&invocation, &before, sizeof invocation), "typed-atomic");
    for (unsigned slot = 0; slot < AR_STARTUP_ARGS; ++slot) {
        struct ar_startup invalid = full;
        memset(invalid.args[slot], 'X', AR_SLOT_SIZE);
        need(ar_select(&invalid, &invocation) == AR_INVALID_STARTUP,
             "typed-unterminated");
        need(!memcmp(&invocation, &before, sizeof invocation), "typed-atomic");
        invalid = full;
        invalid.args[slot][31] = 1;
        need(ar_select(&invalid, &invocation) == AR_INVALID_STARTUP,
             "typed-padding");
        need(!memcmp(&invocation, &before, sizeof invocation), "typed-atomic");
    }
    value = start(2, args);
    value.args[0][0] = 'X';
    need(ar_select(&value, &invocation) == AR_INVALID_STARTUP, "typed-argv0");
    need(!memcmp(&invocation, &before, sizeof invocation), "typed-atomic");
    need(ar_decode(record, sizeof record, &output), "final-valid");
    printf("PASS: parser checks=%u\n", checks);
    return 0;
}
