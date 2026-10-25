/* SPDX-License-Identifier: BSD-2-Clause */
#include "channel.h"
#include <errno.h>
#include <string.h>
extern char **environ;
static _Thread_local volatile unsigned tls=41;
static volatile unsigned bss;
int main(int argc,char **argv){
    if(argc!=2 || strcmp(argv[0],"h") || tls!=41 || bss || !environ || environ[0])return 201;
    int stop=!strcmp(argv[1],"stop"),fault=!strcmp(argv[1],"fault");
    int broken=!strcmp(argv[1],"broken"),short_run=!strcmp(argv[1],"short");
    if(!stop && !fault && !broken && !short_run && strcmp(argv[1],"normal"))return 202;
    unsigned long grant=channel_grant();if(!grant)return 203;
    unsigned char bytes[11];
    if(channel_read(grant^3,bytes,1)!=-1 || errno!=EACCES)return 204;
    if(channel_raw(0x24000,0xd001,0,0)!=-EACCES)return 205;
    unsigned target=(stop || short_run)?16:96,total=0;
#ifdef WRITER
    if(channel_read(grant,bytes,1)!=-1 || errno!=EBADF)return 206;
    if(broken){bytes[0]=1;return channel_write(grant,bytes,1)==-1 && errno==EPIPE?33:207;}
    for(unsigned turns=0;turns<20000 && total<target;turns++){
        size_t n=target-total;if(n>sizeof bytes)n=sizeof bytes;
        for(size_t i=0;i<n;i++)bytes[i]=(unsigned char)(total+i);
#ifdef CORRUPT_STREAM
        if(total+n==target)bytes[n-1]^=1;
#endif
        ssize_t sent=channel_write(grant,bytes,n);
        if(sent<0){if(errno!=EAGAIN)return 208;channel_yield();continue;}
        if(!sent || (size_t)sent>n)return 209;
        total+=(unsigned)sent;
    }
    if(total!=target)return 210;
    if(stop){channel_raw(0x20004,0,0,0);for(;;)channel_yield();}
    if(fault)__asm__ volatile("ud2");
    return 17; /* Exit/fault/stop owns endpoint cleanup; no explicit close. */
#else
    if(channel_write(grant,bytes,1)!=-1 || errno!=EBADF)return 211;
    for(unsigned turns=0;turns<20000;turns++){
        ssize_t got=channel_read(grant,bytes,7);
        if(got<0){if(errno!=EAGAIN)return 212;channel_yield();continue;}
        if(got>7)return 213;
        if(!got)return total==target?29:214;
        for(ssize_t i=0;i<got;i++,total++)if(total>=target || bytes[i]!=(unsigned char)total)return 103;
    }
    return 215;
#endif
}
