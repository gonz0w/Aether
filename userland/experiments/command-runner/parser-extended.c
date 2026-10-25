/* SPDX-License-Identifier: BSD-2-Clause */
#include "runner-parse.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned seed_id, offset_id, value_id, checks, accepted, rejected;
static const unsigned char *active_record;
static size_t active_size;
static int active_must_accept;

static void retain_failure(const char *name)
{
    FILE *bytes = fopen("failure.bin", "wbx");
    if (!bytes)
        exit(91);
    int ok = fwrite(active_record, 1, active_size, bytes) == active_size;
    if (fclose(bytes))
        ok = 0;
    if (!ok)
        exit(91);
    FILE *meta = fopen("failure.json", "wx");
    if (!meta)
        exit(91);
    ok = fprintf(meta, "{\"oracle\":\"%s\",\"size\":%zu,\"must_accept\":%d}\n",
                 name, active_size, active_must_accept) > 0;
    if (fclose(meta))
        ok = 0;
    if (!ok)
        exit(91);
}

static void need(int ok, const char *name)
{
    if (!ok) {
        fprintf(stderr, "ORACLE: %s seed=%u offset=%u value=%u\n", name,
                seed_id, offset_id, value_id);
        if (active_record)
            retain_failure(name);
        exit(90);
    }
}

static void exercise(const unsigned char *record, size_t size, int must_accept)
{
    active_record = record;
    active_size = size;
    active_must_accept = must_accept;
    struct ar_startup out, before;
    memset(&out, 0xa5, sizeof out);
    memcpy(&before, &out, sizeof before);
    int decoded = ar_decode(record, size, &out);
    ++checks;
    need(!must_accept || decoded, "seed-accepted");
    if (!decoded) {
        ++rejected;
        need(!memcmp(&out, &before, sizeof out), "decode-atomic");
        return;
    }
    ++accepted;
    need(size == AR_CARRIER_SIZE, "exact-size");
    need(out.count >= 1 && out.count <= AR_STARTUP_ARGS, "count-bounds");
    unsigned char canonical[AR_CARRIER_SIZE] = {0};
    memcpy(canonical, "AERUN001", 8);
    canonical[8] = (unsigned char)out.count;
    memcpy(canonical + 32, out.args, sizeof out.args);
    need(!memcmp(canonical, record, sizeof canonical), "canonical-carrier");
    struct ar_invocation invocation, old;
    memset(&invocation, 0xa5, sizeof invocation);
    memcpy(&old, &invocation, sizeof old);
    enum ar_action action = ar_select(&out, &invocation);
    need(action >= AR_USAGE && action <= AR_LAUNCH, "decoded-selection");
    need(!must_accept || action == AR_LAUNCH, "seed-launch");
    if (action != AR_LAUNCH) {
        need(!memcmp(&invocation, &old, sizeof old), "select-atomic");
        return;
    }
    need(invocation.count >= 1 && invocation.count <= AR_CHILD_ARGS,
         "child-bounds");
    unsigned first = out.count - invocation.count;
    need(first == 1 || first == 2, "child-offset");
    struct ar_invocation expected = {0};
    expected.count = invocation.count;
    memcpy(expected.args, out.args[first],
           (size_t)expected.count * AR_SLOT_SIZE);
    memcpy(expected.environment, "LC_ALL=C", 9);
    memset(&out, 0xdd, sizeof out);
    need(!memcmp(&expected, &invocation, sizeof expected), "owned-invocation");
}

int main(int argc, char **argv)
{
    if (argc != 1) {
        if (argc != 4 || strcmp(argv[1], "--replay") ||
            (strcmp(argv[3], "0") && strcmp(argv[3], "1")))
            return 91;
        unsigned char record[AR_CARRIER_SIZE + 2];
        FILE *input = fopen(argv[2], "rb");
        if (!input)
            return 91;
        size_t size = fread(record, 1, sizeof record, input);
        int failed = ferror(input);
        if (fclose(input))
            failed = 1;
        if (failed || size > AR_CARRIER_SIZE + 1)
            return 91;
        exercise(record, size, argv[3][0] == '1');
        puts("PASS: replay");
        return 0;
    }
    static const char *const args[3][6] = {
        {"aether-run", "bytecount", "", "", "", ""},
        {"aether-run", "--", "--help", "", "", ""},
        {"aether-run", "--", "bytecount", "", "a b",
         "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"},
    };
    static const unsigned counts[] = {2, 3, 6};
    for (seed_id = 0; seed_id < 3; ++seed_id) {
        unsigned char seed[AR_CARRIER_SIZE + 1] = {0};
        memcpy(seed, "AERUN001", 8);
        seed[8] = (unsigned char)counts[seed_id];
        for (unsigned i = 0; i < counts[seed_id]; ++i)
            memcpy(seed + 32 + i * AR_SLOT_SIZE, args[seed_id][i],
                   strlen(args[seed_id][i]));
        exercise(seed, AR_CARRIER_SIZE, 1);
        for (offset_id = 0; offset_id < AR_CARRIER_SIZE; ++offset_id) {
            exercise(seed, offset_id, 0);
            for (value_id = 0; value_id < 256; ++value_id) {
                if (value_id == seed[offset_id])
                    continue;
                unsigned char changed[AR_CARRIER_SIZE];
                memcpy(changed, seed, sizeof changed);
                changed[offset_id] = (unsigned char)value_id;
                exercise(changed, sizeof changed, 0);
            }
        }
        exercise(seed, sizeof seed, 0);
    }
    active_record = NULL;
    need(checks == 172038 && accepted > 3 && rejected > 675, "discovery");
    printf("{\"checks\":%u,\"accepted\":%u,\"rejected\":%u}\n", checks,
           accepted, rejected);
    return 0;
}
