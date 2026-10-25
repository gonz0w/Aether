/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-channel/channel.h"
#include <errno.h>
#include <string.h>
#include <sys/auxv.h>
static _Thread_local volatile unsigned tls=73;
static unsigned untouched;
static int connection_poisoned;
unsigned wire_frames;
static unsigned word(const unsigned char *p){return (unsigned)p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;}
static int move(unsigned long cap,unsigned char *p,unsigned size,int writing){
    if(connection_poisoned)return 0;
    if(writing)wire_frames++;
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
static unsigned long input,output;
static void put(unsigned char *p,unsigned value){for(unsigned i=0;i<4;i++)p[i]=(unsigned char)(value>>(8*i));}
static int rpc(unsigned op,unsigned ref,unsigned fd,unsigned count,int dirty,unsigned char *r){
    unsigned char q[32]={0};put(q,op);put(q+4,ref);put(q+8,fd);put(q+12,count);q[31]=(unsigned char)dirty;
    if(!move(output,q,32,1)||!move(input,r,32,0))return -999;
    for(unsigned i=4;i<16;i++)if(r[i])return -998;
    int result=(int)word(r);
    if(result>2)return -997;
    for(unsigned i=result>0?16+(unsigned)result:16;i<32;i++)if(r[i])return -996;
    return result;
}
#include "inherited-libc-adapter.h"
/* Admission is retried only after an explicit injected rejection, never a lost reply. */
static int launch(unsigned ref,unsigned fd,unsigned count,unsigned target,unsigned rights,unsigned image,unsigned reserved,unsigned char *r){
    unsigned char q[32]={0};unsigned fields[8]={4,ref,fd,count,target,rights,image,reserved};
    for(unsigned i=0;i<8;i++)put(q+4*i,fields[i]);
    if(!move(output,q,32,1)||!move(input,r,32,0))return -999;
    int result=(int)word(r);
    for(unsigned i=result==0?8:4;i<32;i++)if(r[i])return -998;
    return result;
}
static int collect(unsigned ref,unsigned fd,unsigned receipt,int dirty,unsigned char *r){
    unsigned char q[32]={0};put(q,5);put(q+4,ref);put(q+8,fd);put(q+12,receipt);q[31]=(unsigned char)dirty;
    if(!move(output,q,32,1)||!move(input,r,32,0))return -999;
    int result=(int)word(r);
    for(unsigned i=result==0?16:4;i<32;i++)if(r[i])return -998;
    return result;
}
int inherited_no_replay(void){
    unsigned before=wire_frames;unsigned char r[32];
    if(launch(binding_ref,binding_fd,1,10,1,1,0,r)!=-999)return 0;
    if(collect(binding_ref,binding_fd,0x53000001,0,r)!=-999)return 0;
    return wire_frames==before;
}
static int read_pair(unsigned ref,unsigned fd,unsigned char *r){
    for(unsigned turn=0;turn<1000;turn++){
        (void)ref;int result=inherited_read((int)fd,r);
        if(result!=-EAGAIN)return result;
        channel_yield();
    }
    return -995;
}
int main(int argc,char **argv){
    CHECK(argc==1 && !strcmp(argv[0],"client") && tls==73 && !untouched,31);
    tls++;untouched=1;input=getauxval(0xa001);output=getauxval(0xa002);
    unsigned char r[32]={0};
    CHECK(input && output && input!=output,32);
    CHECK(channel_raw(0x24000,0xd001,0,0)==-EACCES,33);
    CHECK(channel_raw(0x23000,0xa001,0xc003,0)==-EACCES,34);
    CHECK(channel_raw(0x24002,0xd1000102,(unsigned long)r,1)==-EACCES,35);
    CHECK(move(input,r,32,0) && word(r)==0,36);
    unsigned ref=word(r+4),fd=word(r+8),rights=word(r+12);
    unsigned gen=(unsigned)channel_raw(0x20005,0,0,0);
#ifdef CHILD_CLIENT
    CHECK(ref==(0x62000000u|gen) && fd==10 && rights==1,37);
#else
    CHECK(ref==(0x61000000u|gen) && fd==3 && rights==3,37);
#endif
    CHECK(gen==1 || gen==2,38);
    for(unsigned i=16;i<32;i++)CHECK(!r[i],39);
    binding_ref=ref;binding_fd=fd;binding_rights=rights;binding_live=1;
    int preflight=inherited_preflight((int)fd,rights);if(preflight)return preflight;
#if defined(DROP_READ) || defined(CORRUPT_READ) || defined(DROP_CLOSE)
    return inherited_fault((int)fd);
#endif

    CHECK(rpc(1,ref^0x03000000u,fd,2,0,r)==-EBADF,40);
    CHECK(rpc(1,ref,16,2,0,r)==-EBADF,41);
    CHECK(rpc(1,ref-1,fd,2,0,r)==-EBADF,42);
    CHECK(rpc(1,0xf002,fd,2,0,r)==-EBADF,43);
    CHECK(rpc(9,ref,fd,0,0,r)==-EINVAL,44);
    CHECK(rpc(1,ref,fd,1,0,r)==-EINVAL,45);
    CHECK(rpc(1,ref,fd,2,1,r)==-EINVAL,46);
    CHECK(rpc(3,ref,fd,1,0,r)==-EINVAL && rpc(3,ref,fd,0,1,r)==-EINVAL,47);
#ifdef CHILD_CLIENT
    CHECK(rpc(2,ref,fd,1,0,r)==-EACCES,48);
    CHECK(read_pair(ref,fd,r)==2 && !memcmp(r+16,"cd",2),49);
#else
    CHECK(rpc(2,ref,fd,1,0,r)==-ENOTSUP,48);
    CHECK(read_pair(ref,fd,r)==2 && !memcmp(r+16,"ab",2),49);
#endif
#ifdef CHILD_CLIENT
    CHECK(launch(ref,fd,1,10,1,1,0,r)==-EACCES,60);
    CHECK(collect(ref,fd,0x53000000u|gen,0,r)==-EACCES,61);
#else
    unsigned receipt=0x53000000u|gen;
    CHECK(collect(ref,fd,receipt,0,r)==-ECHILD,62);
    CHECK(launch(ref,fd,0,10,1,1,0,r)==-EINVAL && launch(ref,fd,2,10,1,1,0,r)==-EINVAL,63);
    CHECK(launch(ref,fd,1,16,1,1,0,r)==-EINVAL,64);
    CHECK(launch(ref,fd,1,10,1,2,0,r)==-EINVAL && launch(ref,fd,1,10,1,1,1,r)==-EINVAL,65);
    CHECK(launch(ref,fd,1,10,3,1,0,r)==-EACCES,66);
    CHECK(launch(ref^0x03000000u,fd,1,10,1,1,0,r)==-EBADF,67);
    CHECK(launch(ref-1,fd,1,10,1,1,0,r)==-EBADF && launch(ref,16,1,10,1,1,0,r)==-EBADF,68);
#ifdef REJECT_CAPACITY
    if(gen==1)CHECK(launch(ref,fd,1,10,1,1,0,r)==-EBUSY,69);
#endif
#ifdef REJECT_LAUNCH
    if(gen==1)CHECK(launch(ref,fd,1,10,1,1,0,r)==-EINVAL,69);
#endif
    CHECK(launch(ref,fd,1,10,1,1,0,r)==0 && word(r+4)==receipt,70);
    CHECK(launch(ref,fd,1,10,1,1,0,r)==-EBUSY,71);
    CHECK(collect(ref^0x03000000u,fd,receipt,0,r)==-EBADF && collect(ref,16,receipt,0,r)==-EBADF,72);
    CHECK(collect(ref,fd,receipt^8u,0,r)==-ECHILD && collect(ref,fd,receipt-1,0,r)==-ECHILD,73);
    CHECK(collect(ref,fd,receipt,1,r)==-EINVAL,74);
#ifndef PARENT_FIRST
    int status=-EAGAIN;
    for(unsigned t=0;t<1000 && status==-EAGAIN;t++){status=collect(ref,fd,receipt,0,r);channel_yield();}
    CHECK(status==0 && word(r+4)==receipt && word(r+8)==29 && word(r+12)==1,75);
    CHECK(collect(ref,fd,receipt,0,r)==-ECHILD,76);
#endif
#endif
#if (!defined(CHILD_CLIENT) && !defined(PARENT_FIRST)) || (defined(CHILD_CLIENT) && defined(PARENT_FIRST))
    CHECK(read_pair(ref,fd,r)==2 && !memcmp(r+16,"ef",2),50);
#endif
#ifndef CHILD_CLIENT
    CHECK(inherited_close((int)fd)==0,51);
    CHECK(inherited_after_close((int)fd)==0,88);
    CHECK(rpc(3,ref,fd,0,0,r)==-EBADF && rpc(1,ref,fd,2,0,r)==-EBADF,52);
#endif
#ifndef CHILD_CLIENT
    CHECK(collect(ref,fd,receipt,0,r)==
#ifdef PARENT_FIRST
        -EAGAIN
#else
        -ECHILD
#endif
    ,77);
#endif
    CHECK(tls==74 && untouched==1,53);
    return 29;
}
