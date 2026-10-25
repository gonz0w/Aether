/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-memory/adapter.h"
#include <sys/auxv.h>
#include <string.h>
#include <unistd.h>
static _Thread_local volatile unsigned tls=23;
static volatile unsigned bss;
int main(int argc,char **argv){
 if(argc!=1||strcmp(argv[0],"program")||tls!=23||bss)return 180;
 if(getauxval(0xa001)||getauxval(0xa002))return 181;
 if(memtrap(0x23000,0xa001,0xc003,0,0)!=-13)return 182;
 if(memtrap(0x20002,0xb0000101,0,0,0)!=-13)return 183;
 if(memtrap(0x24000,0xd001,0,0,0)!=-13)return 184;
 bss=37;
 if(write(1,"P",1)!=1||memtrap(0x20004,0,0,0,0)!=0)return 185;
 for(;;){memtrap(0x1fffe,0,0,0,0);if(tls!=23||bss!=37)return 186;}
}
