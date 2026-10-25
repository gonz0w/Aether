/* SPDX-License-Identifier: BSD-2-Clause */
#include "channel.h"
#include <errno.h>
#include <sys/auxv.h>
long channel_raw(unsigned long op,unsigned long grant,unsigned long address,unsigned long length) {
    register unsigned long extra __asm__("r8")=0;
    register unsigned long reserved __asm__("r9")=0;
    register unsigned long fourth __asm__("r10")=0;
    __asm__ volatile("int $0x81" : "+a"(op), "+d"(length), "+r"(extra)
        : "D"(grant), "S"(address), "r"(reserved), "r"(fourth) : "rcx","memory","cc");
    return (long)op;
}
unsigned long channel_grant(void){return getauxval(0xa001);}
static ssize_t result(long r){if(r<0){errno=(int)-r;return -1;}return r;}
ssize_t channel_read(unsigned long g,void *p,size_t n){return result(channel_raw(0x24001,g,(uintptr_t)p,n));}
ssize_t channel_write(unsigned long g,const void *p,size_t n){return result(channel_raw(0x24002,g,(uintptr_t)p,n));}
void channel_yield(void){channel_raw(0x1fffe,0,0,0);}
/* Resolve the retained musl fixture hook using its existing raw transport.
 * No descriptor table, libc read/write adaptation or console service is added. */
long __aether_io(unsigned long op,unsigned long a,unsigned long b,unsigned long c){return channel_raw(0x10000+op,a,b,c);}
