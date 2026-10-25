/* SPDX-License-Identifier: BSD-2-Clause */
/* Distinct replacement ELF: no Unix descriptors or application I/O. */
#include "../native-memory/adapter.h"
#include <stdlib.h>
#include <string.h>
#include <sys/auxv.h>
static _Thread_local volatile unsigned cookie = 67;
int main(int argc, char **argv)
{
    if (argc != 3 || strcmp(argv[0], "exec-image") ||
        memtrap(0x10027, 0, 0, 0, 0) != argv[1][0] - '0' ||
        memtrap(0x1006e, 0, 0, 0, 0) != argv[2][0] - '0')
        return 211;
    const char *value = getenv("AETHER_EXEC");
    if (!value || strcmp(value, "1") || cookie != 67 || !getauxval(0xa000) ||
        !getauxval(0xa001) || !getauxval(0xa002))
        return 212;
    if (memtrap(0x23007, 0xa001, 0, 0, 0) != -13 ||
        memtrap(0x23008, 0xa001, 0, 0, 0) != -13 ||
        memtrap(0x23009, 0xa001, 0, 0, 0) != -13)
        return 213;
    return 61;
}
