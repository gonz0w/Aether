/* SPDX-License-Identifier: BSD-2-Clause */
/* Separate TU, actual musl calls, valid local buffers only. */
#include <errno.h>
#include <limits.h>
#include <string.h>
#include <unistd.h>
extern unsigned adapter_requests,adapter_completed,adapter_injected,wire_frames;
extern int inherited_no_replay(void);
#define CHECK(x,n) do{if(!(x))return(n);}while(0)
int fileio_preflight(int fd,unsigned rights){
    char b[32]={0};unsigned before=adapter_requests;
    errno=0;CHECK(read(-1,b,2)==-1 && errno==EBADF,80);
    errno=0;CHECK(read(fd==3?10:3,b,0)==-1 && errno==EBADF,81);
    errno=0;CHECK(read(fd,0,1)==-1 && errno==EFAULT,84);
    errno=0;CHECK(read(fd,b,(size_t)SSIZE_MAX+1)==-1 && errno==EINVAL,84);
    errno=0;CHECK(dup(fd)==-1 && errno==ENOTSUP,85);
    errno=0;CHECK(dup2(fd,fd)==-1 && errno==ENOTSUP,85);
    if(rights==1){errno=0;CHECK(write(fd,0,0)==-1 && errno==EACCES,86);}
    else {errno=0;CHECK(write(fd,0,1)==-1 && errno==EFAULT,86);}
    CHECK(adapter_requests==before,87);
    errno=EDOM;CHECK(read(fd,0,0)==0 && errno==EDOM && adapter_requests==before+1,82);
    return 0;
}
int fileio_read(int fd,unsigned count,const char *expected,unsigned n){
    unsigned char b[32];memset(b,0x55,sizeof b);errno=EDOM;
    CHECK(read(fd,b,count)==(ssize_t)n && errno==EDOM && !memcmp(b,expected,n),1);
    for(unsigned i=n;i<sizeof b;i++)CHECK(b[i]==0x55,2);return 0;
}
int fileio_fill(int fd){
    char b[58];memset(b,'X',sizeof b);errno=EDOM;
    CHECK(write(fd,0,0)==0 && errno==EDOM,1);
    for(unsigned remaining=58;remaining;){
        unsigned n=remaining>16?16:remaining;errno=EDOM;
        CHECK(write(fd,b,remaining)==(ssize_t)n && errno==EDOM,2);remaining-=n;
    }
    errno=0;CHECK(write(fd,b,1)==-1 && errno==ENOSPC,3);
    CHECK(fileio_read(fd,16,"",0)==0,4);
    errno=EDOM;CHECK(write(fd,0,0)==0 && errno==EDOM,5);return 0;
}
int inherited_close(int fd){errno=EDOM;int n=close(fd);return n<0?-errno:errno!=EDOM?-994:n;}
int inherited_after_close(int fd){
    unsigned char b[2];errno=0;CHECK(read(fd,b,0)==-1 && errno==EBADF,88);
    errno=0;CHECK(write(fd,0,0)==-1 && errno==EBADF,88);
    errno=0;CHECK(close(fd)==-1 && errno==EBADF,88);return 0;
}
int inherited_fault(int fd){
    unsigned requests=adapter_requests,completed=adapter_completed,frames=wire_frames;
    unsigned char b[2]={0x55,0x66};errno=0;
#ifdef DROP_CLOSE
    CHECK(close(fd)==-1 && errno==EIO,110);
#else
    CHECK(read(fd,b,2)==-1 && errno==EIO && b[0]==0x55 && b[1]==0x66,110);
#endif
    CHECK(adapter_requests==requests+1 && adapter_completed==completed+1 && adapter_injected==1,111);
    errno=0;
#ifdef DROP_CLOSE
    CHECK(read(fd,b,2)==-1 && errno==EBADF,112);
#else
    CHECK(read(fd,b,2)==-1 && errno==EIO,112);
    errno=0;CHECK(close(fd)==-1 && errno==EIO,113);
#endif
    errno=0;CHECK(close(fd)==-1 && errno==EBADF,114);
    CHECK(adapter_requests==requests+1 && adapter_completed==completed+1 && adapter_injected==1,115);
    CHECK(wire_frames==frames+1 && inherited_no_replay() && wire_frames==frames+1,116);
    return 122; /* Verified uncertain outcome; abort this finite workload. */
}
