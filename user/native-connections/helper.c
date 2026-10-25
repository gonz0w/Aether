/* SPDX-License-Identifier: BSD-2-Clause */
#if HELPER==2
#include "../native-process/helper.c"
#else
#include "../native-memory/adapter.h"
#include <sys/auxv.h>
#include <string.h>
static _Thread_local volatile unsigned tls=23;
static int move(unsigned long cap,unsigned char *b,unsigned n,int write){
 unsigned done=0;for(unsigned t=0;t<100000;t++){
 long r=memtrap(write?0x24002:0x24001,cap,(uintptr_t)(b+done),n-done,0);
 if(r==-11){memtrap(0x1fffe,0,0,0,0);continue;}if(r<=0||r>n-done)return 0;done+=(unsigned)r;if(done==n)return 1;
 }return 0;
}
int main(int argc,char**argv){
 unsigned long input=getauxval(0xa001),output=getauxval(0xa002);unsigned char b[32]={1};
 if(tls!=23||argc!=1||strcmp(argv[0],"client")||!input||!output)return 240;
 if(memtrap(0x24002,0xd1000102,(uintptr_t)b,1,0)!=-13)return 241;
 if(memtrap(0x24000,0xd001,0,0,0)!=-13)return 242;
#if HELPER==1
 if(!move(output,b,8,1)||!move(input,b,32,0)||b[0]!=9||b[1]!=3)return 243;
 memset(b,0,32);if(!move(output,b,24,1))return 244;
#else
 if(!move(output,b,32,1))return 244;
#endif
 if(!move(input,b,32,0)||b[0]!=16||memcmp(b+16,"printf 'hello\\n'\n",16))return 245;
 if(memtrap(0x20004,0,0,0,0)!=0)return 246;
 return 29;
}
#endif
