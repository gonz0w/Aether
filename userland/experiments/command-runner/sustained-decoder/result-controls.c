/* SPDX-License-Identifier: BSD-2-Clause */
#include "runner-result.h"
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
static void put(unsigned char *p, uint32_t value)
{
    for (unsigned i = 0; i < 4; ++i)
        p[i] = (unsigned char)(value >> (i * 8));
}
static void frame(unsigned char record[33], uint32_t receipt, uint32_t kind,
                  uint32_t detail)
{
    memset(record, 0, 33);
    put(record + 4, receipt);
    put(record + 8, detail);
    put(record + 12, kind);
}
static enum ar_reply_action decode(int collection, const unsigned char *record,
                                   size_t size, struct ar_reply *out)
{
    return collection ? ar_collection(record, size, 0x7b000001u, out)
                      : ar_admission(record, size, 1, out);
}
static void invalid(int collection, const unsigned char *record, size_t size,
                    const char *name)
{
    struct ar_reply out, before;
    memset(&out, 0xa5, sizeof out);
    memcpy(&before, &out, sizeof before);
    need(decode(collection, record, size, &out) == AR_REPLY_INVALID, name);
    need(!memcmp(&out, &before, sizeof out), "invalid-atomic");
}
int main(void)
{
    unsigned char record[33], bad[33];
    struct ar_reply out;
    const uint32_t epochs[] = {1, 2, 3, 5, 255, 256, 65534, 65535};
    for (unsigned e = 0; e < sizeof epochs / sizeof epochs[0]; ++e) {
        uint32_t generation = epochs[e];
        uint32_t receipt = 0x7b000000u | generation;
        frame(record, receipt, 0, 0);
        need(ar_admission(record, 32, generation, &out) == AR_REPLY_ADMITTED,
             "admission");
        struct ar_reply expected = {0, receipt, 0, 0};
        need(!memcmp(&out, &expected, sizeof out), "admission-fields");
        for (uint32_t detail = 0; detail < 256; ++detail) {
            frame(record, receipt, 1, detail);
            need(ar_collection(record, 32, receipt, &out) == AR_REPLY_COLLECTED,
                 "collection");
            memset(record, 0xcc, sizeof record);
            expected.detail = detail;
            expected.kind = 1;
            need(!memcmp(&out, &expected, sizeof out), "owned-result");
            need(ar_terminal_exit(&out, 1) == detail, "normal-status");
            need(ar_terminal_exit(&out, 0) == 1, "cleanup-status");
            need(ar_terminal_exit(&out, -1) == 1 &&
                     ar_terminal_exit(&out, 2) == 1,
                 "unknown-cleanup");
            need(!memcmp(&out, &expected, sizeof out), "preserved-raw-facts");
        }
        const uint32_t details[] = {0, 134, 143, 255, 256, UINT32_MAX};
        for (unsigned i = 0; i < sizeof details / sizeof details[0]; ++i) {
            for (uint32_t kind = 1; kind <= 3; ++kind) {
                frame(record, receipt, kind, details[i]);
                need(ar_collection(record, 32, receipt, &out) ==
                         AR_REPLY_COLLECTED,
                     "terminal-decode");
                need(out.kind == kind && out.detail == details[i],
                     "terminal-raw");
                unsigned status =
                    kind == 1 && details[i] <= 255 ? details[i] : 1;
                need(ar_terminal_exit(&out, 1) == status, "terminal-kind");
            }
        }
    }
    for (uint32_t error = 1; error <= 4095; ++error) {
        memset(record, 0, sizeof record);
        put(record, UINT32_MAX - error + 1u);
        for (int collection = 0; collection <= 1; ++collection) {
            enum ar_reply_action action =
                collection && error == 11 ? AR_REPLY_PENDING : AR_REPLY_ERROR;
            need(decode(collection, record, 32, &out) == action,
                 "error-action");
            struct ar_reply expected = {-(int32_t)error, 0, 0, 0};
            need(!memcmp(&out, &expected, sizeof out), "error-facts");
            need(ar_terminal_exit(&out, 1) == 1, "error-not-terminal");
        }
    }
    for (int collection = 0; collection <= 1; ++collection) {
        frame(record, 0x7b000001u, collection ? 1u : 0u, 0);
        for (unsigned size = 0; size < 32; ++size)
            invalid(collection, record, size, "short-reply");
        invalid(collection, record, 33, "long-reply");
        invalid(collection, NULL, 32, "null-reply");
        need(decode(collection, record, 32, NULL) == AR_REPLY_INVALID,
             "null-output");
        for (unsigned offset = collection ? 16u : 8u; offset < 32; ++offset) {
            memcpy(bad, record, sizeof bad);
            bad[offset] = 1;
            invalid(collection, bad, 32, "success-padding");
        }
        for (unsigned offset = 4; offset < 8; ++offset) {
            memcpy(bad, record, sizeof bad);
            bad[offset] ^= 0x80;
            invalid(collection, bad, 32, "receipt");
        }
        memcpy(bad, record, sizeof bad);
        put(bad + 4, 0x7b000002u);
        invalid(collection, bad, 32, "foreign-generation");
        const uint32_t wrong[] = {1,           255,         4095,
                                  0x7fffffffu, 0x80000000u, UINT32_MAX - 4095u};
        for (unsigned i = 0; i < sizeof wrong / sizeof wrong[0]; ++i) {
            memset(bad, 0, sizeof bad);
            put(bad, wrong[i]);
            invalid(collection, bad, 32, "status-range");
        }
        for (unsigned offset = 4; offset < 32; ++offset) {
            memset(bad, 0, sizeof bad);
            put(bad, UINT32_MAX);
            bad[offset] = 1;
            invalid(collection, bad, 32, "error-padding");
        }
    }
    const uint32_t kinds[] = {0, 4, 255, UINT32_MAX};
    for (unsigned i = 0; i < sizeof kinds / sizeof kinds[0]; ++i) {
        frame(record, 0x7b000001u, kinds[i], 0);
        invalid(1, record, 32, "kind-range");
    }
    struct ar_reply before;
    memset(&out, 0xa5, sizeof out);
    memcpy(&before, &out, sizeof before);
    const uint32_t generations[] = {0, 65536, 0x0fffffffu, UINT32_MAX};
    frame(record, 0x7b000001u, 0, 0);
    for (unsigned i = 0; i < sizeof generations / sizeof generations[0]; ++i) {
        need(ar_admission(record, 32, generations[i], &out) == AR_REPLY_INVALID,
             "generation-context");
        need(!memcmp(&out, &before, sizeof out), "context-atomic");
    }
    const uint32_t receipts[] = {0,           1,           0x7b000000u,
                                 0x7b010001u, 0x73000001u, UINT32_MAX};
    for (unsigned i = 0; i < sizeof receipts / sizeof receipts[0]; ++i) {
        need(ar_collection(record, 32, receipts[i], &out) == AR_REPLY_INVALID,
             "receipt-context");
        need(!memcmp(&out, &before, sizeof out), "context-atomic");
        struct ar_reply typed = {0, receipts[i], 1, 0};
        need(ar_terminal_exit(&typed, 1) == 1, "typed-receipt");
    }
    need(ar_terminal_exit(NULL, 1) == 1, "null-policy");
    struct ar_reply typed = {0, 0x7b000001u, 0, 0};
    need(ar_terminal_exit(&typed, 1) == 1, "admission-not-terminal");
    puts("PASS: result boundaries");
    printf("CHECKS: %u\n", checks);
    return 0;
}
