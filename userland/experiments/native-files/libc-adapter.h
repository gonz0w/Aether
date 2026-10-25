/* SPDX-License-Identifier: BSD-2-Clause */
/* Bounded, single-thread adapter. No standard streams or permission-mode model. */
#include <fcntl.h>
#include <limits.h>
#include <unistd.h>
#include "fd-layer.h"
static unsigned libc_root;
static long libc_result(long result){if(result<0){errno=(int)-result;return -1;}return result;}
int open(const char *name,int flags,...){
    if(!name)return (int)libc_result(-EFAULT);
#ifndef IGNORE_FLAGS
    if(flags!=O_RDONLY)return (int)libc_result(-ENOTSUP);
#else
    (void)flags;
#endif
    return (int)libc_result(fd_open(libc_root,name,0));
}
off_t lseek(int fd,off_t offset,int whence){
    if(!valid_fd(fd))return (off_t)libc_result(-EBADF);
    if(whence!=SEEK_SET && whence!=SEEK_CUR)return (off_t)libc_result(-ENOTSUP);
    /* Check without signed addition overflow, including OFF_MIN. */
    off_t base=whence==SEEK_CUR?descriptors[fd]->position:0;
    if(offset < -base || offset > 64-base)return (off_t)libc_result(-EINVAL);
    unsigned position=(unsigned)(base+offset);
    int result=fd_position(fd,position);
    return result<0?(off_t)libc_result(result):(off_t)position;
}
static long libc_io_raw(unsigned long op,unsigned long a,unsigned long b,unsigned long c){
    if(op!=0 && op!=1 && op!=3 && op!=32 && op!=33)return -ENOSYS;
#ifdef WRONG_ERRNO
    if(a>INT_MAX)return -EACCES;
#else
    if(a>INT_MAX)return -EBADF;
#endif
    if(op==3)return fd_close((int)a);
    if(op==32)return fd_dup((int)a);
    if(op==33)return b>INT_MAX?-EBADF:fd_dup2((int)a,(int)b);
    if(!valid_fd((int)a))return -EBADF;
    if(c>SSIZE_MAX)return -EINVAL;
    if(!b && c)return -EFAULT;
    /* One protocol transfer per call; libc callers must handle short I/O. */
    return fd_io((int)a,(void *)b,c>16?16:(unsigned)c,op==1);
}
long __aether_io(unsigned long op,unsigned long a,unsigned long b,unsigned long c){
    /* The hook returns raw negative errno; transport polling must not alter libc errno. */
    int saved=errno;
    long result=libc_io_raw(op,a,b,c);
#ifdef LEAK_POLL_ERRNO
    (void)saved;errno=EAGAIN;
#else
    errno=saved;
#endif
    return result;
}
#ifdef STDIO_FILES
#include "stdio-adapter.h"
#endif
int libc_probe(int scratch);
static int libc_setup(unsigned root,unsigned write_root){
    libc_root=root;
    int scratch_fd=fd_open(write_root,"out",1);
    CHECK(scratch_fd==0,179);
    #ifdef STDIO_FILES
    scratch_handle=descriptors[scratch_fd]->handle;
    #endif
    int result=libc_probe(scratch_fd);
    if(result)return result;
    for(unsigned i=0;i<4;i++)CHECK(!descriptors[i],178);
    CHECK(!files[0].refs && !files[1].refs,177);
    return finish();
}
