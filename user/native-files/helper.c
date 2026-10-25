/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-memory/adapter.h"
#include <sys/auxv.h>
#include <string.h>
static _Thread_local volatile unsigned tls=23;
static unsigned long input,output;
long bridge_read(unsigned char *p,unsigned long n){return memtrap(0x24001,input,(uintptr_t)p,n,0);}
long bridge_write(const unsigned char *p,unsigned long n){return memtrap(0x24002,output,(uintptr_t)p,n,0);}
void bridge_yield(void){memtrap(0x1fffe,0,0,0,0);}
_Noreturn void bridge_abort(void){memtrap(0x1003c,123,0,0,0);for(;;){}}
#if HELPER == 1
extern int file_service(void);
#else
static int transfer(unsigned char *b,int writing){
    unsigned pos=0;for(unsigned turns=0;turns<100000;turns++){
        long n=writing?bridge_write(b+pos,32-pos):bridge_read(b+pos,32-pos);
        if(n==-11){bridge_yield();continue;}if(n<=0||n>32-pos)return 0;pos+=(unsigned)n;if(pos==32)return 1;
    }return 0;
}
static void put(unsigned char *b,unsigned pos,unsigned value){for(unsigned i=0;i<4;i++)b[pos+i]=(unsigned char)(value>>(i*8));}
static unsigned get(const unsigned char*b,unsigned pos){unsigned v=0;for(unsigned i=0;i<4;i++)v|=(unsigned)b[pos+i]<<(8*i);return v;}
static int rpc(unsigned op,unsigned handle,unsigned offset,unsigned len,const char*name,unsigned char *reply){
    unsigned char request[32]={0};put(request,0,op);put(request,4,handle);put(request,8,offset);put(request,12,len);
    if(name){size_t n=strlen(name);if(n>=16)return -999;memcpy(request+16,name,n);}
    if(!transfer(request,1)||!transfer(reply,0))return -999;return (int)get(reply,0);
}
#ifdef WRITABLE
static int write_rpc(unsigned handle,unsigned offset,unsigned length,const char*data,unsigned char*reply){
    unsigned char request[32]={0};put(request,0,4);put(request,4,handle);put(request,8,offset);put(request,12,length);
    if(length<=16&&data)memcpy(request+16,data,length);
    if(!transfer(request,1)||!transfer(reply,0))return -999;return (int)get(reply,0);
}
#endif
#define CHECK(x,n) do{if(!(x))return(n);}while(0)
#endif
int main(int argc,char **argv){
    if(argc!=2||tls!=23)return 124;
    input=getauxval(0xa001);output=getauxval(0xa002);
    if(!strcmp(argv[1],"probe"))return !input&&!output&&memtrap(0x24000,0xd001,0,0,0)==-13?33:125;
    if(!input||!output)return 126;
#if HELPER == 1
    int r=file_service();return r?r:17;
#else
    unsigned char reply[32];CHECK(transfer(reply,0),201);unsigned root=get(reply,4);CHECK(root==0xf001,202);
#ifdef WRITABLE
    unsigned write_root=get(reply,8);CHECK(write_root==0xf002,228);
#endif
#ifdef TRUNCATED
    unsigned char partial[4]={1,0,0,0};
    CHECK(bridge_write(partial,4)==4&&memtrap(0x24003,output,0,0,0)==0,225);
    for(unsigned i=0;i<100000;i++){long n=bridge_read(reply,1);if(!n)return 29;if(n!=-11)return 226;bridge_yield();}
    return 227;
#endif
    CHECK(rpc(1,0,0,1,"message.txt",reply)==-13,203);
    CHECK(rpc(1,root,0,1,"../message",reply)==-22,204);
    CHECK(rpc(1,root,0,1,"missing",reply)==-2,205);
    CHECK(rpc(1,root,0,3,"message.txt",reply)==-13,206);
    CHECK(rpc(1,root,0,1,"message.txt",reply)==0,207);unsigned message=get(reply,4);CHECK(get(reply,8)==18,208);
    CHECK(rpc(1,root,0,1,"hello.sh",reply)==0,209);unsigned script=get(reply,4);
    CHECK(rpc(1,root,0,1,"message.txt",reply)==-24,210);
    CHECK(rpc(2,message,0,5,0,reply)==5&&memcmp(reply+16,"hello",5)==0,211);
    CHECK(rpc(2,message,5,16,0,reply)==13&&memcmp(reply+16," from Aether\n",13)==0,212);
    CHECK(rpc(2,message,18,16,0,reply)==0,213);
    CHECK(rpc(2,message,0,17,0,reply)==-22,214);
    CHECK(rpc(4,message,0,0,0,reply)==-13,215);
    CHECK(rpc(2,script,0,16,0,reply)==16&&memcmp(reply+16,"printf 'hello\\n'\n",16)==0,216);
    CHECK(rpc(3,message,0,0,0,reply)==0,217);
    CHECK(rpc(2,message,0,1,0,reply)==-9,218);
    CHECK(rpc(1,root,0,1,"message.txt",reply)==0&&get(reply,4)!=message,219);unsigned fresh=get(reply,4);
    CHECK(rpc(2,message,0,1,0,reply)==-9,220);
#ifdef WRITABLE
    CHECK(rpc(1,write_root,0,3,"hello.sh",reply)==-13,229);
    CHECK(rpc(5,write_root,0,3,"hello.sh",reply)==-17,229);
    CHECK(rpc(5,root,0,3,"output.txt",reply)==-13,229);
    CHECK(rpc(5,write_root,0,3,"output.txt",reply)==-24,230);
#endif
    CHECK(rpc(3,fresh,0,0,0,reply)==0&&rpc(3,script,0,0,0,reply)==0,221);
#ifdef WRITABLE
    CHECK(rpc(5,write_root,0,3,"output.txt",reply)==0&&get(reply,8)==0,231);unsigned scratch=get(reply,4);
    CHECK(rpc(5,write_root,0,3,"output.txt",reply)==-17,232);
    CHECK(rpc(5,write_root,0,3,"another.txt",reply)==-28,233);
    CHECK(rpc(1,root,0,3,"output.txt",reply)==-13,234);
    CHECK(write_rpc(scratch,0,16,"abcdefghijklmnop",reply)==16,235);
    CHECK(write_rpc(scratch,64,0,0,reply)==0&&rpc(2,scratch,16,1,0,reply)==0,237);
    CHECK(write_rpc(scratch,60,8,"overflow",reply)==-28,237);
    CHECK(write_rpc(scratch,~0u,1,"x",reply)==-28,237);
    CHECK(rpc(2,scratch,0,16,0,reply)==16&&memcmp(reply+16,"abcdefghijklmnop",16)==0,238);
    CHECK(rpc(1,root,0,1,"output.txt",reply)==0,239);unsigned ro=get(reply,4);
    CHECK(write_rpc(ro,0,1,"X",reply)==-13,240);
    CHECK(rpc(6,ro,0,0,0,reply)==-13,241);
    CHECK(rpc(2,ro,0,16,0,reply)==16&&memcmp(reply+16,"abcdefghijklmnop",16)==0,242);
    CHECK(write_rpc(scratch,32,4,"tail",reply)==4,243);
    CHECK(rpc(2,ro,16,16,0,reply)==16,244);for(unsigned i=0;i<16;i++)CHECK(reply[16+i]==0,245);
    CHECK(rpc(2,ro,32,16,0,reply)==4&&memcmp(reply+16,"tail",4)==0,246);
    CHECK(rpc(6,scratch,4,0,0,reply)==0&&rpc(6,scratch,20,0,0,reply)==0,247);
    CHECK(rpc(2,ro,4,16,0,reply)==16,248);for(unsigned i=0;i<16;i++)CHECK(reply[16+i]==0,236);
    CHECK(rpc(6,scratch,65,0,0,reply)==-28&&rpc(2,scratch,20,1,0,reply)==0,249);
    CHECK(write_rpc(scratch,0,17,0,reply)==-22,250);
    CHECK(rpc(3,scratch,0,0,0,reply)==0&&write_rpc(scratch,0,1,"x",reply)==-9,251);
    CHECK(rpc(3,ro,0,0,0,reply)==0&&rpc(1,write_root,0,3,"output.txt",reply)==0,252);unsigned reopened=get(reply,4);
    CHECK(reopened!=scratch&&rpc(2,reopened,0,4,0,reply)==4&&memcmp(reply+16,"abcd",4)==0,253);
    CHECK(rpc(3,reopened,0,0,0,reply)==0,254);
#endif
    CHECK(memtrap(0x24003,output,0,0,0)==0,222);
    for(unsigned i=0;i<100000;i++){long n=bridge_read(reply,1);if(!n)return 29;if(n!=-11)return 223;bridge_yield();}
    return 224;
#endif
}
