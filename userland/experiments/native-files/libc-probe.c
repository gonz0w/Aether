/* SPDX-License-Identifier: BSD-2-Clause */
/* Separate translation unit: all file calls resolve external libc/adapter symbols. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#define CHECK(x,n) do{if(!(x))return(n);}while(0)
int libc_probe(int scratch){
    char b[32]={0};
    errno=0;CHECK(read(-1,b,1)==-1 && errno==EBADF,200);
    errno=0;CHECK(open("message.txt",O_RDONLY|O_CLOEXEC)==-1 && errno==ENOTSUP,201);
    const int flags[]={O_WRONLY,O_RDWR,O_CREAT|O_EXCL|O_RDWR,O_APPEND,O_TRUNC,O_NONBLOCK};
    for(unsigned i=0;i<sizeof(flags)/sizeof(flags[0]);i++){
        errno=0;CHECK(open("message.txt",flags[i],0600)==-1 && errno==ENOTSUP,202);
    }
    CHECK(write(scratch,"abcdefghijklmnopQRST",20)==16,203);
    int alias=dup(scratch);CHECK(alias==1 && lseek(alias,0,SEEK_SET)==0,204);
    CHECK(read(scratch,b,3)==3 && !memcmp(b,"abc",3) && read(alias,b,3)==3 && !memcmp(b,"def",3),205);
    CHECK(lseek(scratch,-2,SEEK_CUR)==4 && read(alias,b,2)==2 && !memcmp(b,"ef",2),206);
    errno=0;CHECK(lseek(alias,INT64_MIN,SEEK_CUR)==-1 && errno==EINVAL && lseek(alias,0,SEEK_CUR)==6,207);
    errno=0;CHECK(lseek(alias,INT64_MAX,SEEK_SET)==-1 && errno==EINVAL,208);
    errno=0;CHECK(lseek(alias,0,SEEK_END)==-1 && errno==ENOTSUP,209);
    int ro=open("out",O_RDONLY);CHECK(ro==2 && read(ro,b,3)==3 && !memcmp(b,"abc",3),210);
    errno=0;CHECK(write(ro,"X",1)==-1 && errno==EACCES && lseek(ro,0,SEEK_CUR)==3,211);
    CHECK(dup2(scratch,ro)==ro && dup2(ro,ro)==ro && dup(scratch)==3,212);
    errno=0;CHECK(dup(scratch)==-1 && errno==EMFILE,213);
    errno=0;CHECK(dup2(-1,scratch)==-1 && errno==EBADF,214);
    CHECK(close(3)==0 && close(scratch)==0 && close(alias)==0,215);
    CHECK(lseek(ro,0,SEEK_SET)==0 && read(ro,b,sizeof b)==16 && !memcmp(b,"abcdefghijklmnop",16) && read(ro,b,1)==0,216);
    errno=0;CHECK(write(ro,b,(size_t)SSIZE_MAX+1)==-1 && errno==EINVAL,217);
    CHECK(close(ro)==0,218);
    errno=0;CHECK(close(ro)==-1 && errno==EBADF,219);
    int seed=open("message.txt",O_RDONLY);CHECK(seed==0,220);
    CHECK(read(seed,b,sizeof b)==16 && read(seed,b+16,sizeof b-16)==2 && !memcmp(b,"hello from Aether\n",18),221);
    CHECK(close(seed)==0,222);
    errno=0;CHECK(open("../out",O_RDONLY)==-1 && errno==EINVAL,223);
    errno=0;CHECK(open("missing",O_RDONLY)==-1 && errno==ENOENT,224);
    errno=0;CHECK(openat(AT_FDCWD,"out",O_RDONLY)==-1 && errno==ENOSYS,225);
    errno=0;CHECK(pipe((int[2]){-1,-1})==-1 && errno==ENOSYS,226);
    return 0;
}
