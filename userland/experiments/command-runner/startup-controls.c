/* SPDX-License-Identifier: BSD-2-Clause */
#include "native-io.h"
#include "../native-channel/channel.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/auxv.h>
extern long __aether_io(unsigned long, unsigned long, unsigned long,
                        unsigned long);
static unsigned char stream[288];
static unsigned cursor, length = sizeof stream, calls, aux_calls;
static struct ar_startup output, before;
static int missing_aux;
static void require(int ok, const char *name)
{
    if (!ok) {
        fprintf(stderr, "ORACLE: %s\n", name);
        exit(90);
    }
}
static void put(unsigned offset, unsigned value)
{
    for (unsigned i = 0; i < 4; ++i)
        stream[offset + i] = (unsigned char)(value >> (i * 8));
}
unsigned long getauxval(unsigned long key)
{
    ++aux_calls;
    return missing_aux ? 0 : key == 0xa001 ? 101 : key == 0xa002 ? 202 : 0;
}
void channel_yield(void) { require(0, "unexpected-yield"); }
long channel_raw(unsigned long op, unsigned long grant, unsigned long address,
                 unsigned long size)
{
    ++calls;
    if (cursor < 256) {
        require(!native_ref(0) && !native_ref(1), "no-mid-read-bindings");
        require(!memcmp(&output, &before, sizeof output),
                "no-mid-read-arguments");
    }
    if (op == 0x20005)
        return 1;
    require(op == 0x24001 && grant == 101, "receive-only");
    require(size && size <= 5, "transfer-bound");
    if (cursor == length)
        return 0;
    if (size > length - cursor)
        size = length - cursor;
    memcpy((void *)address, stream + cursor, size);
    cursor += (unsigned)size;
    return (long)size;
}
int main(int argc, char **argv)
{
    require(argc == 2, "case-argument");
    const char *mode = argv[1];
    const char *const wide[] = {
        "aether-run", "--", "bytecount",
        "--decimal",  "",   "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"};
    const char *const simple[] = {"aether-run", "bytecount", "--decimal"};
    missing_aux = !strcmp(mode, "missing-aux");
    int is_wide = !strcmp(mode, "valid-wide");
    unsigned count = is_wide ? 6u : 3u;
    const char *const *args = is_wide ? wide : simple;
    memcpy(stream, "AERUN001", 8);
    put(8, count);
    for (unsigned i = 0; i < count; ++i)
        memcpy(stream + 32 + i * 32, args[i], strlen(args[i]) + 1);
    for (unsigned i = 0; i < 2; ++i) {
        put(228 + i * 12, 0x71000001u | (i << 16));
        put(232 + i * 12, 3 + i);
        put(236 + i * 12, i ? 3 : 1);
    }
    int valid = !strcmp(mode, "valid-simple") || is_wide;
    if (!strncmp(mode, "prefix-", 7)) {
        length = (unsigned)strtoul(mode + 7, NULL, 10);
        require(length < 256, "prefix-bound");
    } else if (!strncmp(mode, "binding-", 8)) {
        unsigned word = (unsigned)strtoul(mode + 8, NULL, 10);
        require(word < 8, "binding-bound");
        stream[224 + word * 4] ^= 0x80;
    } else if (!strcmp(mode, "bad-carrier")) {
        stream[12] = 1;
    } else if (!strcmp(mode, "legacy-on-carrier") ||
               !strcmp(mode, "null-output") || missing_aux) {
        /* Entry selection itself is the invalid input. */
    } else {
        require(valid, "known-case");
    }
    memset(&output, 0xa5, sizeof output);
    memcpy(&before, &output, sizeof before);
    int result = !strcmp(mode, "legacy-on-carrier")
                     ? native_bootstrap(0)
                     : native_runner_bootstrap(
                           !strcmp(mode, "null-output") ? NULL : &output);
    require(result == valid, "startup-result");
    unsigned saved = calls, saved_aux = aux_calls;
    if (valid) {
        require(cursor == 256 && aux_calls == 2, "exact-startup-consumption");
        struct ar_startup expected = {0};
        expected.count = count;
        for (unsigned i = 0; i < count; ++i)
            strcpy(expected.args[i], args[i]);
        memset(stream, 0xdd, 256);
        require(!memcmp(&output, &expected, sizeof output), "owned-startup");
        require(native_ref(0) == 0x71000001u && native_ref(1) == 0x71010001u,
                "published-bindings");
    } else {
        require(!memcmp(&output, &before, sizeof output),
                "no-failed-arguments");
        require(!native_ref(0) && !native_ref(1), "no-failed-bindings");
        unsigned char sentinel = 0xa5;
        for (unsigned fd = 0; fd < 5; ++fd)
            require(__aether_io(0, fd, (unsigned long)&sentinel, 1) == -EBADF,
                    "no-live-bindings");
        unsigned char q[384] = {4}, r[32];
        require(!native_exchange(q, sizeof q, r), "no-failed-exchange");
        require(sentinel == 0xa5 && calls == saved, "no-failed-traffic");
    }
    struct ar_startup saved_output = output;
    require(!native_runner_bootstrap(&output), "runner-reentry");
    require(calls == saved && aux_calls == saved_aux, "reentry-traffic");
    require(!native_bootstrap(0) && !native_bootstrap(1), "ordinary-reentry");
    require(calls == saved && aux_calls == saved_aux, "cross-entry-traffic");
    require(!memcmp(&output, &saved_output, sizeof output),
            "reentry-publication");
    puts("PASS: startup boundary");
    return 0;
}
