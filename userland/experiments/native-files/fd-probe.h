/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-layer.h"
static int descriptor_probe(unsigned root,unsigned write_root){
    char b[16];unsigned char r[32];
    CHECK(write_root==0xf002,200);
    CHECK(fd_open(root,"missing",0)==-ENOENT,201);
    CHECK(fd_open(root,"out",1)==-EACCES,202);
    int a=fd_open(write_root,"out",1);CHECK(a==0,203);
    unsigned stale=descriptors[a]->handle;
    CHECK(fd_io(a,"abcdefghijklmnop",16,1)==16 && fd_position(a,0)==0,204);
    int alias=fd_dup(a);CHECK(alias==1,205);
    CHECK(fd_io(a,b,3,0)==3 && !memcmp(b,"abc",3),206);
    CHECK(fd_io(alias,b,3,0)==3 && !memcmp(b,"def",3),207);
    int separate=fd_open(root,"out",0);CHECK(separate==2,208);
    CHECK(fd_io(separate,b,3,0)==3 && !memcmp(b,"abc",3),209);
    CHECK(fd_io(separate,"X",1,1)==-EACCES && fd_io(separate,b,1,0)==1 && b[0]=='d',210);
    CHECK(fd_dup2(-1,a)==-EBADF && fd_dup2(a,4)==-EBADF && fd_dup2(a,a)==a,211);
    CHECK(fd_dup(a)==3 && fd_dup(a)==-EMFILE && fd_open(write_root,"second",1)==-EMFILE,212);
    CHECK(fd_close(3)==0 && fd_io(alias,b,1,0)==1 && b[0]=='g',213);
    CHECK(fd_open(root,"message.txt",0)==-EMFILE,214); /* OFD table full */
    CHECK(fd_dup2(a,separate)==separate,215); /* last RO close frees service slot */
    CHECK(fd_open(root,"message.txt",0)==3,216);
    CHECK(fd_close(a)==0 && fd_close(alias)==0 && fd_io(separate,b,1,0)==1 && b[0]=='h',217);
    CHECK(fd_position(separate,60)==0 && fd_io(separate,"overflow",8,1)==-ENOSPC,218);
    CHECK(descriptors[separate]->position==60 && fd_position(separate,65)==-EINVAL,219);
    CHECK(fd_position(separate,16)==0 && fd_io(separate,b,1,0)==0 && descriptors[separate]->position==16,220);
    CHECK(fd_close(separate)==0 && fd_close(separate)==-EBADF,221);
    CHECK(rpc(2,stale,0,1,0,r)==-EBADF,222); /* actual service handle consumed */
    int fresh=fd_open(root,"out",0);CHECK(fresh==0,223);
    CHECK(fd_io(fresh,b,3,0)==3 && !memcmp(b,"abc",3),224);
    CHECK(fd_close(fresh)==0 && fd_close(3)==0,225);
    CHECK(fd_io(-1,b,1,0)==-EBADF && fd_dup(4)==-EBADF,226);
    /* A real closed transport poisons subsequent calls; no automatic replay. */
    CHECK(channel_raw(0x24003,output,0,0)==0,228);
    CHECK(fd_open(root,"out",0)==-EIO && poisoned,227);
    CHECK(fd_open(root,"out",0)==-EIO,229);
    for(unsigned i=0;i<100000;i++){
        ssize_t n=channel_read(input,b,1);
        if(n==0)return 29;
        CHECK(n<0 && errno==EAGAIN,230);channel_yield();
    }
    return 231;
}
