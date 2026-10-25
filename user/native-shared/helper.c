/* SPDX-License-Identifier: BSD-2-Clause */
#if HELPER==2
#include "../native-process/helper.c"
#else
#include "../native-memory/adapter.h"
#include <sys/auxv.h>
#include <string.h>
static _Thread_local volatile unsigned tls=23;
static unsigned long input,output;
static unsigned get(unsigned char*b,unsigned i){return (unsigned)b[i]|(unsigned)b[i+1]<<8|(unsigned)b[i+2]<<16|(unsigned)b[i+3]<<24;}
static void put(unsigned char*b,unsigned i,unsigned v){for(unsigned j=0;j<4;j++)b[i+j]=(unsigned char)(v>>(8*j));}
static int move(unsigned char*b,int write){unsigned n=0;for(unsigned t=0;t<100000;t++){long r=memtrap(write?0x24002:0x24001,write?output:input,(uintptr_t)(b+n),32-n,0);if(r==-11){memtrap(0x1fffe,0,0,0,0);continue;}if(r<=0||r>32-n)return 0;n+=(unsigned)r;if(n==32)return 1;}return 0;}
static int rpc(unsigned op,unsigned ref,unsigned fd,unsigned count,unsigned char*b){memset(b,0,32);put(b,0,op);put(b,4,ref);put(b,8,fd);put(b,12,count);if(!move(b,1)||!move(b,0))return -999;return (int)get(b,0);}
#ifdef REQUESTED
static int spawn(unsigned ref,unsigned fd,unsigned count,unsigned target,unsigned rights,unsigned image,unsigned reserved,unsigned char*b){memset(b,0,32);put(b,0,4);put(b,4,ref);put(b,8,fd);put(b,12,count);put(b,16,target);put(b,20,rights);put(b,24,image);put(b,28,reserved);if(!move(b,1)||!move(b,0))return -999;return (int)get(b,0);}
#endif
#define CHECK(x,n) do{if(!(x))return n;}while(0)
#ifdef FILE_IO
static int file_io(unsigned ref,unsigned fd,unsigned gen){
 unsigned char b[32];
 CHECK(rpc(1,ref,fd,0,b)==0,200);
 CHECK(rpc(1,ref,fd,17,b)==-22,200);
#if HELPER==1
 CHECK(rpc(1,ref,fd,2,b)==2&&!memcmp(b+16,"ab",2),203);
 CHECK(spawn(ref,fd,1,10,1,1,0,b)==0,202);
 int waited=-11;for(unsigned t=0;t<1000&&waited==-11;t++)waited=rpc(5,ref,fd,0x53000000u|gen,b);
 CHECK(waited==0&&get(b,8)==29&&get(b,12)==1,202);
 CHECK(rpc(1,ref,fd,16,b)==0&&rpc(1,ref,fd,0,b)==0,205);
 CHECK(rpc(2,ref,fd,17,b)==-22,206);
 CHECK(rpc(2,ref,fd,0,b)==0,206);
 for(unsigned remaining=58;remaining;){unsigned n=remaining>16?16:remaining;memset(b,0,32);put(b,0,2);put(b,4,ref);put(b,8,fd);put(b,12,n);memset(b+16,'X',n);CHECK(move(b,1)&&move(b,0)&&(int)get(b,0)==(int)n,207);remaining-=n;}
 CHECK(rpc(2,ref,fd,1,b)==-28,208);
 CHECK(rpc(1,ref,fd,16,b)==0,208);
 CHECK(rpc(3,ref,fd,0,b)==0&&rpc(1,ref,fd,0,b)==-9,209);
#else
 (void)gen;
 CHECK(rpc(2,ref,fd,0,b)==-13&&rpc(2,ref,fd,1,b)==-13,201);
 CHECK(rpc(1,ref,fd,3,b)==3&&!memcmp(b+16,"cde",3),204);
 CHECK(rpc(1,ref,fd,16,b)==1&&b[16]=='f',204);
 CHECK(rpc(1,ref,fd,16,b)==0&&rpc(1,ref,fd,1,b)==0,205);
#endif
 return 29;
}
#endif
int main(int argc,char**argv){
 input=getauxval(0xa001);output=getauxval(0xa002);unsigned char b[32];
 CHECK(argc==1&&!strcmp(argv[0],"client")&&tls==23&&input&&output,230);
 CHECK(move(b,0)&&get(b,0)==0,231);unsigned ref=get(b,4),fd=get(b,8);unsigned gen=(unsigned)memtrap(0x20005,0,0,0,0);
 CHECK(ref==((HELPER==1?0x61000000u:0x62000000u)|gen)&&fd==(HELPER==1?3u:10u)&&get(b,12)==(HELPER==1?3u:1u),232);
#ifdef FILE_IO
 return file_io(ref,fd,gen);
#endif

 CHECK(rpc(1,ref^0x03000000u,fd,2,b)==-9,233);
 CHECK(rpc(1,ref,16,2,b)==-9,234);
 CHECK(rpc(1,ref-1,fd,2,b)==-9,235);
 CHECK(rpc(1,0xf002,fd,2,b)==-9,236);
#if HELPER==3
 CHECK(rpc(2,ref,fd,1,b)==-13,237);
#endif
 int result=-11;for(unsigned t=0;t<1000&&result==-11;t++)result=rpc(1,ref,fd,2,b);
 CHECK(result==2&&!memcmp(b+16,HELPER==1?"ab":"cd",2),238);
#ifdef REQUESTED
#if HELPER==1
 CHECK(spawn(ref,fd,2,10,1,1,0,b)==-22,242);
 CHECK(spawn(ref,fd,1,16,1,1,0,b)==-22,242);
 CHECK(spawn(ref,fd,1,10,1,2,0,b)==-22,242);
 CHECK(spawn(ref,fd,1,10,1,1,1,b)==-22,242);
 CHECK(spawn(ref,fd,1,10,3,1,0,b)==-13,243);
 CHECK(spawn(ref^0x03000000u,fd,1,10,1,1,0,b)==-9,243);
#ifdef REJECT_CAPACITY
 if(gen==1)CHECK(spawn(ref,fd,1,10,1,1,0,b)==-16,244);
#endif
#ifdef REJECT_LAUNCH
 if(gen==1)CHECK(spawn(ref,fd,1,10,1,1,0,b)==-22,244);
#endif
 CHECK(spawn(ref,fd,1,10,1,1,0,b)==0&&get(b,4)==(0x53000000u|gen),245);
 CHECK(spawn(ref,fd,1,10,1,1,0,b)==-16,246);
 CHECK(rpc(5,ref,fd,(0x53000000u|gen)^8u,b)==-10,248);
 CHECK(rpc(5,ref,fd,(0x53000000u|gen)-1,b)==-10,248);
#ifndef PARENT_FIRST
 int waited=-11;for(unsigned t=0;t<1000&&waited==-11;t++)waited=rpc(5,ref,fd,0x53000000u|gen,b);
 CHECK(waited==0&&get(b,4)==(0x53000000u|gen)&&get(b,8)==29&&get(b,12)==1,249);
 CHECK(rpc(5,ref,fd,0x53000000u|gen,b)==-10,250);
#endif

#else
 CHECK(spawn(ref,fd,1,10,1,1,0,b)==-13,247);
#endif
#endif
#if (HELPER==1 && !defined(PARENT_FIRST)) || (HELPER==3 && defined(PARENT_FIRST))
 result=-11;for(unsigned t=0;t<1000&&result==-11;t++)result=rpc(1,ref,fd,2,b);
 CHECK(result==2&&!memcmp(b+16,"ef",2),239);
#endif
#if HELPER==1
 CHECK(rpc(3,ref,fd,0,b)==0,240);CHECK(rpc(1,ref,fd,2,b)==-9&&rpc(3,ref,fd,0,b)==-9,241);
#ifdef REQUESTED
 CHECK(rpc(5,ref,fd,0x53000000u|gen,b)==
#ifdef PARENT_FIRST
 -11
#else
 -10
#endif
 ,251);
#endif

#endif
 return 29;
}
#endif
