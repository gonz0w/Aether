/* SPDX-License-Identifier: BSD-2-Clause */
#include "runner-parse.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

static void child_work(void)
{
    unsigned char record[AR_CARRIER_SIZE] = {0};
    struct ar_startup out;
    memcpy(record, "AERUN001", 8);
    record[8] = 2;
    memcpy(record + 32, "aether-run", 10);
    memcpy(record + 64, "bytecount", 9);
    if (!ar_decode(record, sizeof record, &out) || out.count != 2)
        _exit(10);
    record[12] = 1;
    memset(&out, 0xa5, sizeof out);
    if (ar_decode(record, sizeof record, &out))
        _exit(11);
    _exit(0);
}

int main(int argc, char **argv)
{
    if (argc == 2 && !strcmp(argv[1], "--hang")) {
        for (;;)
            continue;
    }
    if (argc != 1)
        return 91;
    pid_t pids[8];
    for (unsigned i = 0; i < 8; ++i) {
        pid_t pid = fork();
        if (pid < 0)
            return 91;
        if (pid == 0)
            child_work();
        pids[i] = pid;
    }
    for (unsigned i = 0; i < 8; ++i) {
        int status;
        if (waitpid(pids[i], &status, 0) != pids[i] || !WIFEXITED(status) ||
            WEXITSTATUS(status) != 0) {
            fprintf(stderr, "ORACLE: child-status\n");
            return 90;
        }
    }
    puts("PASS: concurrency");
    return 0;
}
