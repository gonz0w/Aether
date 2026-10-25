/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-channel/channel.h"
#include <errno.h>
#include <string.h>
#include <sys/auxv.h>
static _Thread_local volatile unsigned tls=61;
static unsigned long input,output;
static unsigned get(const unsigned char *p){return (unsigned)p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;}
static void put(unsigned char *p,unsigned n){for(unsigned i=0;i<4;i++)p[i]=(unsigned char)(n>>(8*i));}
static int frame(unsigned char *p,int writing){
    unsigned used=0;
    for(unsigned turns=0;turns<100000;turns++){
        unsigned n=32-used,limit=writing?7:5;if(n>limit)n=limit;
        ssize_t r=writing?channel_write(output,p+used,n):channel_read(input,p+used,n);
        if(r<0 && errno==EAGAIN){channel_yield();continue;}
        if(r<=0 || (size_t)r>n)return 0;
        used+=(unsigned)r;if(used==32)return 1;
    }
    return 0;
}
static int exchange(unsigned char *q,unsigned char *r){
    if(!frame(q,1)||!frame(r,0))return -999;
    for(unsigned i=16;i<32;i++)if(r[i])return -998;
    int result=(int)get(r);
    if(result<0 && (get(r+4)||get(r+8)||get(r+12)))return -997;
    return result;
}
static int rpc(unsigned op,unsigned ticket,unsigned inherit,unsigned version,const char *name,unsigned char *r){
    unsigned char q[32]={0};put(q,op);put(q+4,ticket);put(q+8,inherit);put(q+12,version);
    if(name){size_t n=strlen(name);if(n>15)return -996;memcpy(q+16,name,n);}
    return exchange(q,r);
}
#ifdef COEXIST
/* An op-3 rejection still consumes its complete body. Never replay a mutation. */
static int routed(unsigned ticket,unsigned version,unsigned inherit,unsigned op,unsigned handle,unsigned offset,unsigned length,const char *data,unsigned char *r){
    unsigned char header[32]={0},body[32]={0};
    put(header,3);put(header+4,ticket);put(header+8,inherit);put(header+12,version);
    put(body,op);put(body+4,handle);put(body+8,offset);put(body+12,length);
    if(data){size_t n=strlen(data);if(n>16)return -996;memcpy(body+16,data,n);}
    if(!frame(header,1)||!frame(body,1)||!frame(r,0))return -999;
    if(get(r+12))return -998;
    int result=(int)get(r);
    if(result<0){for(unsigned i=4;i<32;i++)if(r[i])return -997;}
    return result;
}
#define FILE_RPC(t,o,h,p,n,d) routed(t,1,0,o,h,p,n,d,r)
#endif
#define CHECK(x,n) do{if(!(x))return(n);}while(0)
int main(int argc,char **argv){
    CHECK(argc==1 && !strcmp(argv[0],"requester") && tls==61,11);
    input=getauxval(0xa001);output=getauxval(0xa002);
    CHECK(input && output && input!=output,12);
    CHECK(channel_raw(0x23000,0xa001,0xc002,0)==-EACCES,13);
    unsigned char r[32],q[32]={0};
#ifdef TRUNCATED
    put(q,1);CHECK(channel_write(output,q,4)==4,14);return 41;
#endif
    CHECK(rpc(1,0,1,1,"worker",r)==-ENOTSUP,51);
    CHECK(rpc(1,0,0,1,"requester",r)==-ENOENT,52);
    CHECK(rpc(1,0,0,1,"../worker",r)==-EINVAL,53);
    CHECK(rpc(1,0,0,2,"worker",r)==-EINVAL,54);
    CHECK(rpc(9,0,0,1,0,r)==-ENOSYS,55);
    CHECK(rpc(2,0xb0000102,0,1,0,r)==-ECHILD,56);
    put(q,1);put(q+12,1);memcpy(q+16,"worker",6);q[31]=1;
    CHECK(exchange(q,r)==-EINVAL,57);
    CHECK(rpc(1,1,0,1,"worker",r)==-EINVAL,58);
    unsigned old=0;
    for(unsigned gen=1;gen<=2;gen++){
        CHECK(rpc(1,0,0,1,"worker",r)==0,59);
        unsigned ticket=get(r+4);CHECK(ticket && ticket!=old && 
#ifdef COEXIST
            get(r+8)==0xf001 && get(r+12)==0xf002
#else
            !get(r+8) && !get(r+12)
#endif
        ,60);
#ifdef EARLY_EXIT
        return 42;
#endif
#ifdef COEXIST
        CHECK(channel_raw(0x24002,0xd1020102,(unsigned long)r,1)==-EACCES,70);
        CHECK(routed(ticket,2,0,5,0xf002,0,3,"scratch",r)==-EINVAL,71);
        CHECK(routed(ticket,1,1,5,0xf002,0,3,"scratch",r)==-EINVAL,72);
        CHECK(FILE_RPC(ticket^0x80000000u,5,0xf002,0,3,"scratch")==-ECHILD,73);
        if(old)CHECK(FILE_RPC(old,5,0xf002,0,3,"scratch")==-ECHILD,74);
        CHECK(FILE_RPC(ticket,1,0xf001,0,1,"scratch")==-ENOENT,75);
        CHECK(FILE_RPC(ticket,1,0xf001,0,1,"message.txt")==0,76);
        unsigned file=get(r+4);CHECK(file && get(r+8)==18,77);
        CHECK(FILE_RPC(ticket,2,file,0,16,0)==16 && !memcmp(r+16,"hello from Aether\n",16),78);
        CHECK(FILE_RPC(ticket,2,file,16,16,0)==2 && !memcmp(r+16,"r\n",2),79);
        CHECK(FILE_RPC(ticket,3,file,0,0,0)==0,80);
        CHECK(FILE_RPC(ticket,5,0xf001,0,3,"scratch")==-EACCES,81);
        CHECK(FILE_RPC(ticket,5,0xf002,0,3,"scratch")==0,82);file=get(r+4);
        CHECK(FILE_RPC(ticket,4,file,0,4,"data")==4,83);
        CHECK(FILE_RPC(ticket,2,file,0,16,0)==4 && !memcmp(r+16,"data",4),84);
        CHECK(FILE_RPC(ticket,3,file,0,0,0)==0,85);
#endif
        CHECK(rpc(1,0,0,1,"worker",r)==-EBUSY,61);
        CHECK(rpc(2,ticket^0x80000000u,0,1,0,r)==-ECHILD,62);
        if(old)CHECK(rpc(2,old,0,1,0,r)==-ECHILD,63);
        CHECK(rpc(2,ticket,1,1,0,r)==-EINVAL && rpc(2,ticket,0,1,"x",r)==-EINVAL,64);
        CHECK(rpc(2,ticket,0,1,0,r)==0 && get(r+4)==ticket && get(r+8)==(
#ifdef COEXIST
            17u
#else
            gen==1?17u:33u
#endif
        ) && get(r+12)==1,65);
        CHECK(rpc(2,ticket,0,1,0,r)==-ECHILD,66);old=ticket;
    }
    CHECK(channel_raw(0x24003,output,0,0)==0,67);
    for(unsigned i=0;i<100000;i++){
        ssize_t n=channel_read(input,r,1);if(n==0)return 29;
        CHECK(n<0 && errno==EAGAIN,68);channel_yield();
    }
    return 69;
}
