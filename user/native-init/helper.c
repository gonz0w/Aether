/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-memory/adapter.h"
#include <sys/auxv.h>
#include <string.h>
static _Thread_local volatile unsigned tls=23;
int main(int argc,char **argv) {
    if(argc!=2||tls!=23)return 71;
    unsigned long writer=getauxval(0xa001);
    unsigned char value=42;
    if(memtrap(0x25000,0xe001,0,0,0)!=-13)return 72;
    if(memtrap(0x25003,0xe001,0xe1000001,0,0)!=-13)return 73;
    if(memtrap(0x20001,0xb0000101,0,0,0)!=-13)return 74;
    if(memtrap(0x24002,writer^3,(uintptr_t)&value,1,0)!=-13)return 75;
    if(!strcmp(argv[1],"stale")) {
        if(memtrap(0x24002,0xd1000102,(uintptr_t)&value,1,0)!=-13)return 76;
        return 33;
    }
    if(memtrap(0x24002,writer,(uintptr_t)&value,1,0)!=1)return 77;
    if(memtrap(0x20004,0,0,0,0)!=0)return 78;
    if(!strcmp(argv[1],"exit"))return 17;
    for(;;)memtrap(0x1fffe,0,0,0,0);
}
