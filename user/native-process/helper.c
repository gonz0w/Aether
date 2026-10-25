/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-memory/adapter.h"
#include <sys/auxv.h>
#include <string.h>
static _Thread_local volatile unsigned tls=23;
#if defined(COEXIST) && HELPER==2
static unsigned long input,output;
long bridge_read(unsigned char*p,unsigned long n){return memtrap(0x24001,input,(uintptr_t)p,n,0);}
long bridge_write(const unsigned char*p,unsigned long n){return memtrap(0x24002,output,(uintptr_t)p,n,0);}
void bridge_yield(void){memtrap(0x1fffe,0,0,0,0);}
_Noreturn void bridge_abort(void){memtrap(0x1003c,123,0,0,0);for(;;){}}
extern int file_service(void);
#endif
#if HELPER==1
static unsigned long input,output;
static unsigned get(const unsigned char*b,unsigned i){return (unsigned)b[i]|(unsigned)b[i+1]<<8|(unsigned)b[i+2]<<16|(unsigned)b[i+3]<<24;}
static void put(unsigned char*b,unsigned i,unsigned v){for(unsigned j=0;j<4;j++)b[i+j]=(unsigned char)(v>>(8*j));}
static int transfer(unsigned char*b,int write){unsigned n=0;for(unsigned t=0;t<100000;t++){
 long r=memtrap(write?0x24002:0x24001,write?output:input,(uintptr_t)(b+n),32-n,0);
 if(r==-11){memtrap(0x1fffe,0,0,0,0);continue;}if(r<=0||r>32-n)return 0;n+=(unsigned)r;if(n==32)return 1;
}return 0;}
static int rpc(unsigned op,unsigned ticket,unsigned inherit,unsigned version,const char*name,unsigned char*reply){
 unsigned char b[32]={0};put(b,0,op);put(b,4,ticket);put(b,8,inherit);put(b,12,version);if(name)memcpy(b+16,name,strlen(name));
 if(!transfer(b,1)||!transfer(reply,0))return -999;
 for(unsigned i=16;i<32;i++)if(reply[i])return -998;
 int result=(int)get(reply,0);if(result<0&&(get(reply,4)||get(reply,8)||get(reply,12)))return -997;
 return result;
}
#ifdef COEXIST
static int file_rpc(unsigned ticket,unsigned op,unsigned handle,unsigned offset,unsigned length,const char*data,unsigned char*reply){
 unsigned char header[32]={0},body[32]={0};put(header,0,3);put(header,4,ticket);put(header,12,1);
 put(body,0,op);put(body,4,handle);put(body,8,offset);put(body,12,length);
 if(data)memcpy(body+16,data,strlen(data));
 if(!transfer(header,1)||!transfer(body,1)||!transfer(reply,0))return -999;
 return (int)get(reply,0);
}
#endif
#define CHECK(x,n) do{if(!(x))return n;}while(0)
#endif
int main(int argc,char**argv){
 if(argc!=1||tls!=23)return 198;
#if HELPER==2
#ifdef COEXIST
 input=getauxval(0xa001);output=getauxval(0xa002);
 if(!input||!output||input==output||strcmp(argv[0],"worker"))return 189;
 unsigned char foreign=0;
 if(memtrap(0x24002,0xd1000102,(uintptr_t)&foreign,1,0)!=-13)return 191;
 int status=file_service();return status?status:17;
#else
 if(strcmp(argv[0],"worker")||getauxval(0xa001)||getauxval(0xa002))return 190;
 unsigned char b=7;
 if(memtrap(0x24002,0xd1000102,(uintptr_t)&b,1,0)!=-13)return 191;
 if(memtrap(0x23000,0xa001,0xc002,0,0)!=-13)return 192;
 for(unsigned i=0;i<64;i++)memtrap(0x1fffe,0,0,0,0);
 long gen=memtrap(0x20005,0,0,0,0);return gen==1?17:gen==2?33:193;
#endif
#else
 input=getauxval(0xa001);output=getauxval(0xa002);CHECK(input&&output&&!strcmp(argv[0],"requester"),201);
 CHECK(memtrap(0x23000,0xa001,0xc002,0,0)==-13,210);
 unsigned char reply[32];
#ifdef TRUNCATED
 unsigned char b[4]={1,0,0,0};CHECK(memtrap(0x24002,output,(uintptr_t)b,4,0)==4,211);return 41;
#endif
 CHECK(rpc(1,0,1,1,"worker",reply)==-95,202);
 CHECK(rpc(1,0,0,1,"requester",reply)==-2,203);
 CHECK(rpc(1,0,0,1,"../worker",reply)==-22,212);
 CHECK(rpc(1,0,0,2,"worker",reply)==-22,213);
 CHECK(rpc(9,0,0,1,0,reply)==-38,214);
 CHECK(rpc(2,0xb0000102,0,1,0,reply)==-10,215);
 unsigned old=0;
 for(unsigned gen=1;gen<=2;gen++){
  CHECK(rpc(1,0,0,1,"worker",reply)==0,204);unsigned ticket=get(reply,4);CHECK(ticket==(0x51000000u|gen),216);
#ifdef EARLY_EXIT
  return 42;
#endif
#ifdef COEXIST
  unsigned root=get(reply,8),write_root=get(reply,12);CHECK(root==0xf001&&write_root==0xf002,219);
#ifdef PROGRAM
  CHECK(rpc(4,0,1,1,"program",reply)==-95,230);
  CHECK(rpc(4,0,0,1,"worker",reply)==-2,231);
  CHECK(rpc(4,0,0,1,"program",reply)==0,232);unsigned program=get(reply,4);
  CHECK(program==(0x52000000u|gen),233);
  CHECK(rpc(4,0,0,1,"program",reply)==-16,234);
  CHECK(rpc(2,ticket,0,1,0,reply)==-16,235);
  CHECK(rpc(5,ticket,0,1,0,reply)==-10,236);
#endif
  unsigned char denied=0;
  CHECK(memtrap(0x24002,0xd1020102,(uintptr_t)&denied,1,0)==-13,220);
  if(old)CHECK(file_rpc(old,1,root,0,1,"hello.sh",reply)==-10,221);
  CHECK(file_rpc(ticket,1,root,0,1,"hello.sh",reply)==0,222);unsigned file=get(reply,4);
  CHECK(file_rpc(ticket,2,file,0,16,0,reply)==16&&!memcmp(reply+16,"printf 'hello\\n'\n",16),223);
  CHECK(file_rpc(ticket,3,file,0,0,0,reply)==0,224);
  CHECK(file_rpc(ticket,1,root,0,1,"scratch",reply)==-2,225);
  CHECK(file_rpc(ticket,5,write_root,0,3,"scratch",reply)==0,226);file=get(reply,4);
  CHECK(file_rpc(ticket,4,file,0,4,"data",reply)==4,227);
  CHECK(file_rpc(ticket,2,file,0,4,0,reply)==4&&!memcmp(reply+16,"data",4),228);
  CHECK(file_rpc(ticket,3,file,0,0,0,reply)==0,229);
#ifdef PROGRAM
  CHECK(rpc(5,program,0,1,0,reply)==0&&get(reply,8)==143&&get(reply,12)==3,237);
  CHECK(rpc(5,program,0,1,0,reply)==-10,238);
#endif
#endif
  if(old)CHECK(rpc(2,old,0,1,0,reply)==-10,217);
  CHECK(rpc(1,0,0,1,"worker",reply)==-16,205);
  CHECK(rpc(2,ticket^8,0,1,0,reply)==-10,206);
  CHECK(rpc(2,ticket,0,1,0,reply)==0&&get(reply,4)==ticket&&get(reply,8)==(
#ifdef COEXIST
  17u
#else
  gen==1?17u:33u
#endif
  )&&get(reply,12)==1,208);
  CHECK(rpc(2,ticket,0,1,0,reply)==-10,207);old=ticket;
 }
 CHECK(memtrap(0x24003,output,0,0,0)==0,218);
 return 29;
#endif
}
