/* SPDX-License-Identifier: BSD-2-Clause */
#include <stdio.h>
#include <sys/uio.h>
static unsigned vector_reads,vector_writes,split_vectors,deny_seek;
FILE *__aether_fdopen_core(int,const char *);
static unsigned scratch_handle;
FILE *fdopen(int fd,const char *mode){
    if(!valid_fd(fd)){errno=EBADF;return 0;}
    if(!mode || (strcmp(mode,"r") && strcmp(mode,"r+"))){errno=ENOTSUP;return 0;}
    if(!strcmp(mode,"r+") && descriptors[fd]->handle!=scratch_handle){errno=EACCES;return 0;}
    return __aether_fdopen_core(fd,mode);
}
FILE *fopen(const char *name,const char *mode){
    if(!mode || strcmp(mode,"r")){errno=ENOTSUP;return 0;}
    int fd=open(name,O_RDONLY);if(fd<0)return 0;
    FILE *f=fdopen(fd,mode);
    if(!f){int saved=errno;close(fd);errno=saved;}
    return f;
}
static ssize_t vector_io(int fd,const struct iovec *iov,int count,int writing){
    if(count<0 || count>2)return libc_result(-EINVAL);
    size_t total=0;
    for(int i=0;i<count;i++){
        if(iov[i].iov_len>(size_t)SSIZE_MAX-total)return libc_result(-EINVAL);
        if(!iov[i].iov_base && iov[i].iov_len)return libc_result(-EFAULT);
        total+=iov[i].iov_len;
    }
    unsigned n=total>16?16:(unsigned)total,at=0;unsigned char data[16];
    if(writing)for(int i=0;i<count && at<n;i++){
        unsigned part=iov[i].iov_len>n-at?n-at:(unsigned)iov[i].iov_len;
        if(part)memcpy(data+at,iov[i].iov_base,part);
        at+=part;
    }
    int result=fd_io(fd,data,n,writing);
    if(result<0)return libc_result(result);
    if(count==2 && iov[0].iov_len && (size_t)result>iov[0].iov_len)++split_vectors;
    if(!writing){
#ifdef CORRUPT_VECTOR
        if(result)data[0]^=1;
#endif
        at=0;for(int i=0;i<count && at<(unsigned)result;i++){
            unsigned part=iov[i].iov_len>(unsigned)result-at?(unsigned)result-at:(unsigned)iov[i].iov_len;
            if(part)memcpy(iov[i].iov_base,data+at,part);
            at+=part;
        }
    }
    return result;
}
ssize_t aether_readv(int fd,const struct iovec *iov,int count){++vector_reads;return vector_io(fd,iov,count,0);}
ssize_t aether_writev(int fd,const struct iovec *iov,int count){++vector_writes;return vector_io(fd,iov,count,1);}
off_t aether_stdio_seek(int fd,off_t offset,int whence){
    if(deny_seek){deny_seek=0;errno=EIO;return -1;}
    return lseek(fd,offset,whence);
}
void stdio_deny_seek_once(void){deny_seek=1;}
unsigned stdio_vector_witness(void){return vector_reads && vector_writes && split_vectors;}
