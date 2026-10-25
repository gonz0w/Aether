/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-channel/channel.h"
#include <errno.h>
#include <string.h>
#include <sys/auxv.h>
static _Thread_local volatile unsigned tls=73;
static unsigned untouched;
static unsigned word(const unsigned char *p){return (unsigned)p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;}
static int move(unsigned long cap,unsigned char *p,unsigned size,int writing){
    unsigned used=0;
    for(unsigned turn=0;turn<100000;turn++){
        unsigned n=size-used,limit=writing?3:5;if(n>limit)n=limit;
        ssize_t result=writing?channel_write(cap,p+used,n):channel_read(cap,p+used,n);
        if(result<0 && errno==EAGAIN){channel_yield();continue;}
        if(result<=0 || (size_t)result>n)return 0;
        used+=(unsigned)result;if(used==size)return 1;
    }
    return 0;
}
#define CHECK(x,n) do{if(!(x))return(n);}while(0)
int main(int argc,char **argv){
    CHECK(argc==1 && !strcmp(argv[0],"client") && tls==73 && !untouched,31);
    tls++;untouched=1;
    unsigned long input=getauxval(0xa001),output=getauxval(0xa002);
    unsigned char q[32]={1},r[32]={0};
    CHECK(input && output && input!=output,32);
    CHECK(channel_raw(0x24000,0xd001,0,0)==-EACCES,33);
    CHECK(channel_raw(0x23000,0xa001,0xc003,0)==-EACCES,34);
    CHECK(channel_raw(0x24002,0xd1000102,(unsigned long)q,1)==-EACCES,35);
    CHECK(channel_raw(0x24002,input,(unsigned long)q,1)==-EBADF,36);
    CHECK(channel_raw(0x24001,output,(unsigned long)r,1)==-EBADF,37);
#ifdef PARTIAL_CLIENT
    CHECK(move(output,q,8,1) && move(input,r,32,0),38);
    CHECK(word(r)==777,39);
    for(unsigned i=4;i<32;i++)CHECK(!r[i],40);
    CHECK(move(output,q+8,24,1),41);
#else
    CHECK(move(output,q,32,1),41);
#endif
    CHECK(move(input,r,32,0),42);
    CHECK(word(r)==16 && word(r+4)==0 && word(r+8)==0 && word(r+12)==0,43);
    CHECK(!memcmp(r+16,"printf 'hello\\n'\n",16),44);
    CHECK(tls==74 && untouched==1,45);
    CHECK(channel_raw(0x20004,0,0,0)==0,46);
    return 29;
}
