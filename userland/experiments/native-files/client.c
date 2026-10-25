/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-channel/channel.h"
#include <sys/auxv.h>
#include <errno.h>
#include <string.h>
static unsigned long input,output;
static _Thread_local volatile unsigned tls=47;
static unsigned get(const unsigned char *p){return (unsigned)p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;}
static void put(unsigned char *p,unsigned n){for(unsigned i=0;i<4;i++)p[i]=(unsigned char)(n>>(8*i));}
static int frame(unsigned char *p,int sending){
    unsigned used=0;
    for(unsigned turns=0;turns<100000;turns++){
        unsigned n=32-used,chunk=sending?5:9;if(n>chunk)n=chunk;
        ssize_t done=sending?channel_write(output,p+used,n):channel_read(input,p+used,n);
        if(done<0 && errno==EAGAIN){channel_yield();continue;}
        if(done<=0 || (size_t)done>n)return 0;
        used+=(unsigned)done;if(used==32)return 1;
    }
    return 0;
}
static int exchange(unsigned char *q,unsigned char *r){
    if(!frame(q,1)||!frame(r,0))return -999;
    if(get(r+12))return -998;
    return (int)get(r);
}
static int rpc(unsigned op,unsigned h,unsigned off,unsigned n,const char *name,unsigned char *r){
    unsigned char q[32]={0};put(q,op);put(q+4,h);put(q+8,off);put(q+12,n);
    if(name){size_t len=strlen(name);if(len>=16)return -997;memcpy(q+16,name,len);}
    return exchange(q,r);
}
#define CHECK(x,n) do{if(!(x))return(n);}while(0)
static int finish(void){
    unsigned char b;
    CHECK(channel_raw(0x24003,output,0,0)==0,190);
    for(unsigned i=0;i<100000;i++){
        ssize_t n=channel_read(input,&b,1);
        if(n==0)return 29;
        CHECK(n<0 && errno==EAGAIN,191);channel_yield();
    }
    return 192;
}
#ifdef LIBC_FILES
#include "libc-adapter.h"
#elif defined(FD_FAILURES)
#include "fd-failures.h"
#elif defined(DESCRIPTORS)
#include "fd-probe.h"
#endif
#ifdef WRITABLE
static int write_request(unsigned h,unsigned off,unsigned n,const char *bytes,unsigned char *r){
    unsigned char q[32]={0};put(q,4);put(q+4,h);put(q+8,off);put(q+12,n);
    if(bytes && n<=16)memcpy(q+16,bytes,n);
    return exchange(q,r);
}
static int scratch(unsigned root,unsigned write_root){
    unsigned char r[32],q[32]={0};
    CHECK(write_root==0xf002 && root!=write_root,200);
    CHECK(rpc(5,root,0,3,"out",r)==-EACCES && rpc(5,0,0,3,"out",r)==-EACCES,201);
    CHECK(rpc(5,write_root,1,3,"out",r)==-EINVAL && rpc(5,write_root,0,3,"../out",r)==-EINVAL,202);
    CHECK(rpc(1,root,0,1,"message.txt",r)==0,203);unsigned seed=get(r+4);
    CHECK(write_request(seed,0,1,"X",r)==-EACCES && rpc(6,seed,0,0,0,r)==-EACCES,204);
    CHECK(rpc(2,seed,0,5,0,r)==5 && !memcmp(r+16,"hello",5),205);
    CHECK(rpc(1,root,0,1,"hello.sh",r)==0,206);unsigned other=get(r+4);
    CHECK(rpc(5,write_root,0,3,"out",r)==-EMFILE,207);
    CHECK(rpc(3,seed,0,0,0,r)==0 && rpc(3,other,0,0,0,r)==0,208);
    /* Same name succeeds after failed create: it was not published on EMFILE. */
    CHECK(rpc(5,write_root,0,3,"out",r)==0 && get(r+8)==0,209);unsigned rw=get(r+4);
    CHECK(rpc(5,write_root,0,3,"out",r)==-EEXIST && rpc(5,write_root,0,3,"second",r)==-ENOSPC,210);
    CHECK(rpc(1,root,0,3,"out",r)==-EACCES && rpc(1,write_root,0,3,"message.txt",r)==-EACCES,211);
    CHECK(write_request(rw,0,16,"abcdefghijklmnop",r)==16,212);
    CHECK(rpc(1,root,0,1,"out",r)==0 && get(r+8)==16,213);unsigned ro=get(r+4);
    CHECK(write_request(ro,0,1,"X",r)==-EACCES,218);
    CHECK(rpc(6,ro,0,0,0,r)==-EACCES,214);
    CHECK(rpc(2,ro,0,16,0,r)==16 && !memcmp(r+16,"abcdefghijklmnop",16),215);
    for(unsigned i=0;i<4;i++){
        int result;
        if(i==0)result=write_request(rw,60,8,"overflow",r);
        else if(i==1)result=write_request(rw,~0u,1,"X",r);
        else if(i==2)result=rpc(6,rw,65,0,0,r);
        else result=write_request(rw,0,17,0,r);
        CHECK(result==(i==3?-EINVAL:-ENOSPC),216);
        CHECK(rpc(2,ro,0,16,0,r)==16 && !memcmp(r+16,"abcdefghijklmnop",16) && rpc(2,ro,16,1,0,r)==0,217);
    }
    put(q,4);put(q+4,rw);put(q+12,1);q[16]='X';q[31]=1;
    CHECK(exchange(q,r)==-EINVAL,220);
    CHECK(rpc(2,ro,0,16,0,r)==16 && !memcmp(r+16,"abcdefghijklmnop",16),221);
    CHECK(write_request(rw,64,0,0,r)==0 && rpc(2,ro,16,1,0,r)==0,222);
    CHECK(write_request(rw,60,4,"TAIL",r)==4,223);
    for(unsigned off=16;off<60;off+=16){
        unsigned count=60-off;if(count>16)count=16;
        CHECK(rpc(2,ro,off,count,0,r)==(int)count,224);
        for(unsigned i=0;i<count;i++)CHECK(r[16+i]==0,225);
    }
    CHECK(rpc(2,ro,60,16,0,r)==4 && !memcmp(r+16,"TAIL",4) && rpc(2,ro,64,1,0,r)==0,226);
    CHECK(rpc(6,rw,3,0,0,r)==0 && rpc(6,rw,20,0,0,r)==0,227);
    CHECK(rpc(2,ro,0,3,0,r)==3 && !memcmp(r+16,"abc",3),228);
    CHECK(rpc(2,ro,3,16,0,r)==16,229);
    for(unsigned i=0;i<16;i++)CHECK(r[16+i]==0,219);
    CHECK(rpc(2,ro,19,16,0,r)==1 && r[16]==0 && rpc(2,ro,20,1,0,r)==0,230);
    CHECK(rpc(6,rw,64,0,0,r)==0 && rpc(2,ro,60,4,0,r)==4,231);
    for(unsigned i=0;i<4;i++)CHECK(r[16+i]==0,219); /* formerly TAIL */
    CHECK(rpc(3,rw,0,0,0,r)==0 && write_request(rw,0,1,"X",r)==-EBADF,232);
    CHECK(rpc(1,write_root,0,3,"out",r)==0 && get(r+8)==64,233);unsigned reopened=get(r+4);
    CHECK(reopened!=rw && rpc(2,reopened,0,3,0,r)==3 && !memcmp(r+16,"abc",3),234);
    CHECK(rpc(3,reopened,0,0,0,r)==0 && rpc(3,ro,0,0,0,r)==0,235);
    return finish();
}
#endif
int main(int argc,char **argv){
    CHECK(argc==2 && !strcmp(argv[0],"h") && tls==47,140);
    input=getauxval(0xa001);output=getauxval(0xa002);
    if(!strcmp(argv[1],"probe"))return !input&&!output&&channel_raw(0x24000,0xd001,0,0)==-EACCES?33:139;
    CHECK(!strcmp(argv[1],"files") && input && output && input!=output,141);
    unsigned char r[32],q[32]={0};CHECK(frame(r,0),142);
    CHECK(get(r)==0 && get(r+4)==0xf001 && get(r+12)==0,143);
    for(unsigned i=16;i<32;i++)CHECK(r[i]==0,144);
    unsigned root=get(r+4),write_root=get(r+8);
#ifndef WRITABLE
    CHECK(write_root==0,143);
#endif
    CHECK(channel_read(output,r,1)==-1 && errno==EBADF,145);
    CHECK(channel_write(input,r,1)==-1 && errno==EBADF,146);
#ifdef WRITABLE
    #ifdef LIBC_FILES
    (void)scratch;
    return libc_setup(root,write_root);
    #elif defined(FD_FAILURES)
    (void)scratch;
    return descriptor_failures(root,write_root);
    #elif defined(DESCRIPTORS)
    (void)scratch;
    return descriptor_probe(root,write_root);
    #else
    return scratch(root,write_root);
    #endif
#endif
#ifdef TRUNCATED
    put(q,1);CHECK(channel_write(output,q,5)==5,147);return finish();
#endif
    CHECK(rpc(1,0,0,1,"message.txt",r)==-EACCES,150);
    CHECK(rpc(1,root,0,3,"message.txt",r)==-EACCES,151);
    CHECK(rpc(1,root,0,1,"missing",r)==-ENOENT,152);
    CHECK(rpc(1,root,0,1,"../message",r)==-EINVAL,153);
    CHECK(rpc(1,root,0,1,".",r)==-EINVAL && rpc(1,root,0,1,"",r)==-EINVAL,154);
    CHECK(rpc(1,root,1,1,"message.txt",r)==-EINVAL,155);
    put(q,1);put(q+4,root);put(q+12,1);memset(q+16,'x',16);
    CHECK(exchange(q,r)==-EINVAL,156); /* unterminated */
    memset(q+16,0,16);memcpy(q+16,"message.txt",11);q[31]=1;
    CHECK(exchange(q,r)==-EINVAL,157); /* nonzero trailing padding */
    CHECK(rpc(99,0,0,0,0,r)==-EINVAL,158);
    CHECK(rpc(1,root,0,1,"message.txt",r)==0 && get(r+8)==18,159);unsigned message=get(r+4);
    CHECK(rpc(1,root,0,1,"hello.sh",r)==0 && get(r+8)==17,160);unsigned script=get(r+4);
    CHECK(message!=script && rpc(1,root,0,1,"hello.sh",r)==-EMFILE,161);
    CHECK(rpc(2,message,0,17,0,r)==-EINVAL,162);
    CHECK(rpc(2,message,0,1,"x",r)==-EINVAL,163);
    CHECK(rpc(3,message,1,0,0,r)==-EINVAL,164);
    CHECK(rpc(4,message,0,0,0,r)==-EACCES,165);
    const char expected[]="hello from Aether\n";
    const unsigned chunks[]={4,9,5};unsigned at=0;
    for(unsigned j=0;j<3;j++){
        unsigned n=chunks[j];CHECK(rpc(2,message,at,n,0,r)==(int)n,170);
        CHECK(!memcmp(r+16,expected+at,n),171);
        for(unsigned i=16+n;i<32;i++)CHECK(r[i]==0,172);
        CHECK(get(r+4)==0 && get(r+8)==0,173);at+=n;
    }
    CHECK(rpc(2,message,18,16,0,r)==0 && rpc(2,message,~0u,16,0,r)==0,174);
    CHECK(rpc(2,script,0,16,0,r)==16 && !memcmp(r+16,"printf 'hello\\n'\n",16),175);
    CHECK(rpc(2,script,16,16,0,r)==1 && r[16]=='\n' && rpc(2,script,17,1,0,r)==0,186);
    CHECK(rpc(3,message,0,0,0,r)==0 && rpc(3,message,0,0,0,r)==-EBADF,176);
    for(unsigned i=0;i<2;i++){
        CHECK(rpc(1,root,0,1,"message.txt",r)==0,177);unsigned h=get(r+4);
        CHECK(h!=message && rpc(2,message,0,1,0,r)==-EBADF,178);
        CHECK(rpc(3,h,0,0,0,r)==0,179);
    }
    CHECK(rpc(1,root,0,1,"message.txt",r)==-EMFILE,180); /* first slot retired, second live */
    CHECK(rpc(3,script,0,0,0,r)==0,181);
    for(unsigned i=0;i<2;i++){
        CHECK(rpc(1,root,0,1,"hello.sh",r)==0,182);unsigned h=get(r+4);
        CHECK(h!=script && rpc(2,script,0,1,0,r)==-EBADF,183);
        CHECK(rpc(3,h,0,0,0,r)==0,184);
    }
    CHECK(rpc(1,root,0,1,"hello.sh",r)==-EMFILE,185); /* both slots retired */
    return finish();
}
