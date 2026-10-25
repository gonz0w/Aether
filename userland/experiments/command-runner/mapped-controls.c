/* SPDX-License-Identifier: BSD-2-Clause */
/* Exchange-boundary host witness; no native transport or cleanup claim. */
#include "mapped-controls.h"
#include "native-io.h"
#include "runner-result.h"
#include "../native-channel/channel.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
ssize_t control_read(int fd, void *bytes, size_t count);
int control_close(int fd);
unsigned result_policy(const struct ar_reply *reply, int complete);
static const char *mode;
static unsigned launches, polls, yields, closes_in, closes_out, reads, policies;
static unsigned pending, raw_kind = 1, raw_detail;
static int forbidden;
static void need(int ok, const char *name)
{
    if (!ok) {
        fprintf(stderr, "ORACLE: %s\n", name);
        exit(90);
    }
}
static int is(const char *name) { return !strcmp(mode, name); }
static void active(void) { need(!forbidden, "no-after-unknown-or-malformed"); }
static void put(unsigned char *p, unsigned value)
{
    for (unsigned i = 0; i < 4; ++i)
        p[i] = (unsigned char)(value >> (8 * i));
}
void native_put(unsigned char *p, unsigned value) { put(p, value); }
unsigned native_ref(unsigned index)
{
    need(index < 2, "reference-index");
    return 0x71000001u | (index << 16);
}
unsigned native_generation(void) { return 1; }
int native_runner_bootstrap(struct ar_startup *startup)
{
    memset(startup, 0, sizeof *startup);
    startup->count = 3;
    strcpy(startup->args[0], "aether-run");
    strcpy(startup->args[1], "bytecount");
    strcpy(startup->args[2], "--decimal");
    return 1;
}
long channel_raw(unsigned long op, unsigned long a, unsigned long b,
                 unsigned long c)
{
    active();
    need(op == 0x23000 && a == 0xa001 && b == 0xc003 && !c, "authority-probe");
    return -EACCES;
}
void channel_yield(void)
{
    active();
    ++yields;
    need(yields <= pending && yields == polls, "yield-only-pending");
}
int native_exchange(unsigned char *q, unsigned size, unsigned char r[32])
{
    active();
    memset(r, 0, 32);
    if (!launches) {
        need(!polls && !closes_in && size == 384, "admission-order");
        unsigned char expected[384] = {4};
        put(expected + 4, 1);
        put(expected + 8, 2);
        put(expected + 12, 1);
        put(expected + 16, 2);
        memcpy(expected + 32, "bytecount", 9);
        for (unsigned i = 0; i < 2; ++i) {
            put(expected + 64 + i * 32, 0x71000001u | (i << 16));
            put(expected + 68 + i * 32, 3 + i);
            put(expected + 72 + i * 32, i);
            put(expected + 76 + i * 32, i ? 2 : 1);
        }
        memcpy(expected + 128, "bytecount", 9);
        memcpy(expected + 160, "--decimal", 9);
        memcpy(expected + 192, "LC_ALL=C", 8);
        need(!memcmp(q, expected, sizeof expected), "exact-launch");
        ++launches;
        put(r + 4, 0x73000001u);
        if (is("admission-lost")) {
            forbidden = 1;
            return 0;
        }
        if (is("admission-receipt"))
            r[4] ^= 8;
        if (is("admission-padding"))
            r[31] = 1;
        if (is("admission-positive"))
            put(r, 1);
        if (is("admission-error")) {
            memset(r, 0, 32);
            put(r, 0xfffffffeu);
        }
        if (!strncmp(mode, "admission-", 10))
            forbidden = 1;
        return 1;
    }
    need(closes_in == 1, "collection-after-input-close");
    need(polls < 100000, "collection-budget");
    unsigned char expected[32] = {5};
    put(expected + 4, 0x73000001u);
    need(size == 32 && !memcmp(q, expected, 32), "exact-collection");
    ++polls;
    if (polls <= pending) {
        put(r, 0xfffffff5u);
        return 1;
    }
    if (is("collection-lost") || is("pending-lost")) {
        forbidden = 1;
        return 0;
    }
    put(r + 4, 0x73000001u);
    put(r + 8, raw_detail);
    put(r + 12, raw_kind);
    if (is("collection-receipt"))
        r[4] ^= 8;
    if (is("collection-padding"))
        r[31] = 1;
    if (is("collection-kind"))
        put(r + 12, 0);
    if (is("collection-error")) {
        memset(r, 0, 32);
        put(r, 0xfffffff6u);
    }
    if (is("pending-malformed")) {
        memset(r, 0, 32);
        put(r, 0xfffffff5u);
        r[31] = 1;
    }
    if (!strncmp(mode, "collection-", 11) || is("pending-malformed"))
        forbidden = 1;
    return 1;
}
int control_close(int fd)
{
    active();
    if (fd == 3) {
        need(launches == 1 && !polls && !closes_in++, "input-close-once");
        return is("input-close-error") ? -1 : 0;
    }
    need(fd == 4 && reads == 1 && !closes_out++, "output-close-once");
    return is("output-close-error") ? -1 : 0;
}
ssize_t control_read(int fd, void *bytes, size_t count)
{
    active();
    need(fd == 4 && bytes && count == 23 && polls == pending + 1 &&
             closes_in == 1 && !reads++,
         "read-after-terminal");
    return is("read-error") ? -1 : is("not-eof") ? 1 : 0;
}
unsigned ar_terminal_exit(const struct ar_reply *reply, int complete)
{
    active();
    need(!policies++ && reads == 1 && closes_out == 1, "policy-after-cleanup");
    need(reply && !reply->error && reply->receipt == 0x73000001u &&
             reply->kind == raw_kind && reply->detail == raw_detail,
         "raw-terminal-facts");
    int expected = !(is("input-close-error") || is("output-close-error") ||
                     is("read-error") || is("not-eof"));
    need(complete == expected, "cleanup-facts");
    return result_policy(reply, complete);
}
int main(int argc, char **argv)
{
    need(argc == 2, "case-argument");
    mode = argv[1];
    if (is("normal64"))
        raw_detail = 64;
    if (is("normal255"))
        raw_detail = 255;
    if (is("fault")) {
        raw_kind = 2;
        raw_detail = 134;
    }
    if (is("stop")) {
        raw_kind = 3;
        raw_detail = 143;
    }
    if (is("wide"))
        raw_detail = 0xffffffffu;
    if (is("pending-one") || is("pending-lost"))
        pending = 1;
    if (is("pending-last"))
        pending = 99999;
    if (is("pending-budget"))
        pending = 100000;
    char *startup[] = {"client", NULL};
    int result = runner_main(1, startup);
    int aborted = forbidden || is("pending-budget");
    int bad_cleanup = is("input-close-error") || is("output-close-error") ||
                      is("read-error") || is("not-eof");
    int expected = aborted || bad_cleanup || raw_kind != 1 || raw_detail > 255
                       ? 1
                       : (int)raw_detail;
    need(result == expected && launches == 1, "status-and-one-launch");
    if (!strncmp(mode, "admission-", 10)) {
        need(!polls && !closes_in && !reads && !closes_out && !policies,
             "admission-abort");
    } else {
        need(closes_in == 1 &&
                 polls == pending + (is("pending-budget") ? 0u : 1u),
             "collection-count");
        need(yields == pending, "pending-count");
        need(reads == (aborted ? 0u : 1u) && closes_out == reads &&
                 policies == reads,
             "abort-or-complete-effects");
    }
    puts("PASS: mapped boundary");
    return 0;
}
