/* SPDX-License-Identifier: BSD-2-Clause */
/* Separate TU: calls actual externally linked musl entry points. */
#include <errno.h>
#include <limits.h>
#include <string.h>
#include <unistd.h>
extern unsigned adapter_requests,adapter_completed,adapter_injected,wire_frames;
extern int inherited_no_replay(void);
#define CHECK(x,n) do{if(!(x))return(n);}while(0)
int inherited_preflight(int fd,unsigned rights){
    char b[3]={0};unsigned before=adapter_requests;
    errno=0;CHECK(read(-1,b,2)==-1 && errno==EBADF,80);
    errno=0;CHECK(read(fd==3?10:3,b,2)==-1 && errno==EBADF,81);
    errno=EDOM;CHECK(read(fd,0,0)==0 && errno==EDOM,82);
    errno=0;CHECK(read(fd,b,1)==-1 && errno==ENOTSUP,83);
    errno=0;CHECK(read(fd,b,3)==-1 && errno==ENOTSUP,83);
    errno=0;CHECK(read(fd,0,2)==-1 && errno==EFAULT,84);
    errno=0;CHECK(read(fd,b,(size_t)SSIZE_MAX+1)==-1 && errno==EINVAL,84);
    errno=0;CHECK(dup(fd)==-1 && errno==ENOTSUP,85);
    errno=0;CHECK(dup2(fd,fd)==-1 && errno==ENOTSUP,85);
    errno=0;CHECK(write(fd,"x",1)==-1 && errno==(rights==1?EACCES:ENOTSUP),86);
    CHECK(adapter_requests==before,87);return 0;
}
int inherited_read(int fd,unsigned char *r){
    unsigned char b[2]={0};errno=EDOM;
    ssize_t n=read(fd,b,2);
    if(n<0)return -errno;
    if(errno!=EDOM)return -994;
    if(n>2)return -993;
    memset(r,0,32);memcpy(r+16,b,(size_t)n);return (int)n;
}
int inherited_close(int fd){errno=EDOM;int n=close(fd);return n<0?-errno:errno!=EDOM?-994:n;}
int inherited_after_close(int fd){
    unsigned char b[2];errno=0;
    CHECK(read(fd,b,2)==-1 && errno==EBADF,88);
    errno=0;CHECK(close(fd)==-1 && errno==EBADF,88);return 0;
}
int inherited_fault(int fd){
    unsigned char b[2]={0x55,0x66};errno=0;
#ifdef DROP_CLOSE
    CHECK(close(fd)==-1 && errno==EIO,110);
#else
    CHECK(read(fd,b,2)==-1 && errno==EIO && b[0]==0x55 && b[1]==0x66,110);
#endif
    CHECK(adapter_requests==1 && adapter_completed==1 && adapter_injected==1,111);
    errno=0;
#ifdef DROP_CLOSE
    CHECK(read(fd,b,2)==-1 && errno==EBADF,112);
#else
    CHECK(read(fd,b,2)==-1 && errno==EIO,112);
    errno=0;CHECK(close(fd)==-1 && errno==EIO,113);
#endif
    errno=0;CHECK(close(fd)==-1 && errno==EBADF,114);
    CHECK(adapter_requests==1 && adapter_completed==1 && adapter_injected==1,115);
    CHECK(wire_frames==1 && inherited_no_replay() && wire_frames==1,116);
    return 122; /* Verified uncertain outcome; abort this finite workload. */
}
