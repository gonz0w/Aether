/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-memory/adapter.h"
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
static _Thread_local volatile unsigned tls = 23;
static unsigned bss;
int main(int argc, char **argv) {
    if (argc != 2 || bss || tls != 23) return 91;
    if (strcmp(argv[0], HELPER == 1 ? "helper-a" : "helper-b")) return 92;
    const char *env = getenv("AETHER_LAUNCH");
    if (!env || strcmp(env, HELPER == 1 ? "one" : "two")) return 93;
    if (memtrap(0x23000,0xa001,0xc001,0,0) != -13) return 94;
    if (memtrap(0x20002,0xb0000101,0,0,0) != -13) return 95;
    if (!strcmp(argv[1], "fault")) { __asm__ __volatile__("ud2"); }
    if (strcmp(argv[1], "exit")) return 96;
    tls = HELPER;
    for (unsigned i=0;i<64;i++) { memtrap(0x1fffe,0,0,0,0); if(tls != HELPER)return 97; }
    const char c = HELPER == 1 ? 'A' : 'B';
    if (write(1,&c,1) != 1) return 98;
    if (HELPER == 1) memtrap(0x1003c,~0UL-238,0,0,0); /* Low eight bits: 17. */
    return HELPER == 1 ? 99 : 29;
}
