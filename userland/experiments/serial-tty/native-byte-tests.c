/* SPDX-License-Identifier: BSD-2-Clause */
/* Host callback controls link the actual selected facade and FD startup/ledger.
 * The checked helper and direct trap observations below are explicit doubles;
 * target link/native execution must exercise the real helper and kernel. */
#include "../mktemp-directory/target.h"
#include <errno.h>
#include <stdint.h>
#include <string.h>
extern int amk_tty_byte_probe(int, char **);
static unsigned creates, traps;
char *amk_checked_mkdtemp(char *text)
{
    creates++;
    if (strcmp(text, "/home/t.XXXXXX"))
        return NULL;
    memcpy(text + 8, "ABCDEF", 6);
    return text;
}
long amk_tty_test_trap(unsigned long op, unsigned long cap, unsigned long a,
                       unsigned long b, unsigned long c)
{
    if ((op != 0x26000 && op != 0x26001) || cap != 0xf001 || a || b || c)
        return -EINVAL;
    traps++;
    return -EACCES;
}
int amk_test_tty_probe_case(uint32_t kind)
{
    creates = traps = 0;
    /* Literal storage deliberately supplies no argv writability contract. */
    char *argv[] = {"mktemp", "-d", "/home/t.XXXXXX", NULL};
    int status = amk_tty_byte_probe(kind == 3 ? 2 : 3, argv);
    if (strcmp(argv[2], "/home/t.XXXXXX"))
        return 2;
    if (kind == 3)
        return status == 1 && !creates && !traps ? 0 : 3;
    if (creates != 1 || traps != 2)
        return 4;
    return status == (kind == 0 ? 0 : 1) ? 0 : 5;
}
