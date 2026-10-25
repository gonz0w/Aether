/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-memory/adapter.h"
#include <sys/auxv.h>
#include <string.h>
static _Thread_local volatile unsigned tls=23;
int main(int argc,char **argv) {
    if(argc!=2 || tls!=23)return 101;
    unsigned long cap=getauxval(0xa001);
    if(!cap)return 102;
    unsigned char buffer[16];
    if(memtrap(0x24001,cap^3,(uintptr_t)buffer,1,0)!=-13)return 104;
    if(memtrap(0x24000,0xd001,0,0,0)!=-13)return 105;
    const int stopping=!strcmp(argv[1],"stop");
    const int broken=!strcmp(argv[1],"broken");
    unsigned total=0, expected=stopping||!strcmp(argv[1],"short")?16:96;
    if(HELPER==1) {
        if(memtrap(0x24001,cap,(uintptr_t)buffer,1,0)!=-9)return 106;
        if(broken) {buffer[0]=1;return memtrap(0x24002,cap,(uintptr_t)buffer,1,0)==-32?33:107;}
        for(unsigned turns=0;total<expected&&turns<10000;turns++) {
            unsigned count=expected-total<16?expected-total:16;
            for(unsigned i=0;i<count;i++)buffer[i]=(unsigned char)(total+i);
            long n=memtrap(0x24002,cap,(uintptr_t)buffer,count,0);
            if(n==-11){memtrap(0x1fffe,0,0,0,0);continue;}
            if(n<=0)return 108;
            total+=(unsigned)n;
        }
        if(total!=expected)return 109;
        if(stopping){memtrap(0x20004,0,0,0,0);for(;;)memtrap(0x1fffe,0,0,0,0);}
        if(!strcmp(argv[1],"fault"))__asm__ __volatile__("ud2");
        return 17; /* Kernel termination closes the writer; no explicit close. */
    }
    if(memtrap(0x24002,cap,(uintptr_t)buffer,1,0)!=-9)return 110;
    for(unsigned turns=0;turns<10000;turns++) {
        long n=memtrap(0x24001,cap,(uintptr_t)buffer,16,0);
        if(n==-11){memtrap(0x1fffe,0,0,0,0);continue;}
        if(n<0)return 111;
        if(!n)return total==expected?29:112;
        for(long i=0;i<n;i++,total++)if(total>=expected||buffer[i]!=(unsigned char)total)return 103;
    }
    return 113;
}
