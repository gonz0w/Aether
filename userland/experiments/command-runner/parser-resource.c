/* SPDX-License-Identifier: BSD-2-Clause */
#include "runner-parse.h"
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/resource.h>

static void report(void)
{
    struct rusage usage;
    if (getrusage(RUSAGE_SELF, &usage))
        return;
    printf("{\"ru_maxrss\":%ld}\n", usage.ru_maxrss);
}

static int decode_samples(void)
{
    unsigned char record[AR_CARRIER_SIZE] = {0};
    struct ar_startup out;
    memcpy(record, "AERUN001", 8);
    record[8] = 2;
    memcpy(record + 32, "aether-run", 10);
    memcpy(record + 64, "bytecount", 9);
    if (!ar_decode(record, sizeof record, &out) || out.count != 2)
        return 0;
    record[12] = 1;
    memset(&out, 0xa5, sizeof out);
    return !ar_decode(record, sizeof record, &out);
}

int main(int argc, char **argv)
{
    if (argc == 2 && !strcmp(argv[1], "--grow")) {
        size_t length = (size_t)128 << 20;
        char *pages = mmap(0, length, PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANON, -1, 0);
        if (pages == MAP_FAILED)
            return 91;
        memset(pages, 1, length);
        report();
        return 0;
    }
    if (argc == 2 && !strcmp(argv[1], "--reserve")) {
        size_t length = (size_t)128 << 20;
        if (mmap(0, length, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1,
                 0) == MAP_FAILED)
            return 91;
        report();
        return 0;
    }
    if (argc != 1)
        return 91;
    if (!decode_samples())
        return 90;
    report();
    return 0;
}
