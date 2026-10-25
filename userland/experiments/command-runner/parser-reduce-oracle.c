/* SPDX-License-Identifier: BSD-2-Clause */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void retain_failure(const char *name, const unsigned char *record,
                           size_t size, int must_accept)
{
    FILE *bytes = fopen("failure.bin", "wbx");
    if (!bytes)
        exit(91);
    int ok = fwrite(record, 1, size, bytes) == size;
    if (fclose(bytes))
        ok = 0;
    if (!ok)
        exit(91);
    FILE *meta = fopen("failure.json", "wx");
    if (!meta)
        exit(91);
    ok = fprintf(meta, "{\"oracle\":\"%s\",\"size\":%zu,\"must_accept\":%d}\n",
                 name, size, must_accept) > 0;
    if (fclose(meta))
        ok = 0;
    if (!ok)
        exit(91);
}

static void fail(const char *name, const unsigned char *record, size_t size,
                 int must_accept)
{
    fprintf(stderr, "ORACLE: %s seed=0 offset=0 value=0\n", name);
    retain_failure(name, record, size, must_accept);
    exit(90);
}

int main(int argc, char **argv)
{
    if (argc != 5 || strcmp(argv[1], "--replay") ||
        (strcmp(argv[3], "0") && strcmp(argv[3], "1")) ||
        (strcmp(argv[4], "nonzero") && strcmp(argv[4], "long")))
        return 91;
    unsigned char record[227];
    FILE *input = fopen(argv[2], "rb");
    if (!input)
        return 91;
    size_t size = fread(record, 1, sizeof record, input);
    int failed = ferror(input);
    if (fclose(input))
        failed = 1;
    if (failed || size > 225)
        return 91;
    int must_accept = argv[3][0] == '1';
    if (!strcmp(argv[4], "long")) {
        if (size > 1)
            fail("too-long", record, size, must_accept);
    } else {
        for (size_t i = 0; i < size; ++i) {
            if (record[i])
                fail("nonzero", record, size, must_accept);
        }
    }
    if (must_accept)
        fail("seed-accepted", record, size, must_accept);
    puts("PASS: replay");
    return 0;
}
