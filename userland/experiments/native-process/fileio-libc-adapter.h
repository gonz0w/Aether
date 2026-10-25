/* SPDX-License-Identifier: BSD-2-Clause */
/* Single validated binding, no local position or remote reference count. */
#include <limits.h>
static unsigned binding_ref,binding_fd,binding_rights;
static int binding_live;
unsigned adapter_requests,adapter_completed,adapter_injected;
static long binding_error(void){
#ifdef WRONG_FD_ERRNO
    return -EACCES;
#else
    return -EBADF;
#endif
}
static long inherited_io(unsigned long op,unsigned long fd,unsigned long buffer,unsigned long count){
    if(op!=0 && op!=1 && op!=3 && op!=32 && op!=33)return -ENOSYS;
    if(fd>INT_MAX || !binding_live || fd!=binding_fd)return binding_error();
    if(op==3)binding_live=0; /* Consuming local close, including uncertain outcome. */
    if(connection_poisoned)return -EIO;
    if(op==32 || op==33)return -ENOTSUP;
    if(op==1 && binding_rights==1)return -EACCES;
    if(op!=3){
        if(count>SSIZE_MAX)return -EINVAL;
        if(!buffer && count)return -EFAULT;
        if(count>16)count=16; /* One bounded short transfer; no hidden loop. */
    }
    unsigned char reply[32]={0},request[32]={0};adapter_requests++;
    put(request,op==3?3:op==1?2:1);put(request+4,binding_ref);put(request+8,binding_fd);
    put(request+12,op==3?0:(unsigned)count);
    if(op==1 && count)memcpy(request+16,(void *)buffer,(size_t)count);
    int result=-999;
    if(move(output,request,32,1) && move(input,reply,32,0))result=(int)word(reply);
    if(result>=0)adapter_completed++;
#if defined(DROP_READ) || defined(DROP_CLOSE) || defined(CORRUPT_READ)
    if(result>=0 && !adapter_injected &&
#ifdef DROP_CLOSE
       op==3
#else
       op==0
#endif
    ){
        adapter_injected++;
#ifdef CORRUPT_READ
        reply[12]=1;
#else
        connection_poisoned=1;return -EIO;
#endif
    }
#endif
    /* Reject unknown/malformed outcomes before publishing caller bytes. */
    int malformed=result < -4095 || result==-999 || result==-998 || result==-997 || result==-996;
    for(unsigned i=4;i<16;i++)if(reply[i])malformed=1;
    if(result>16 || (op!=3 && result>(long)count) || (op==3 && result>0))malformed=1;
    for(unsigned i=op==0 && result>0 && result<=16?16+(unsigned)result:16;i<32;i++)if(reply[i])malformed=1;
    if(malformed){connection_poisoned=1;return -EIO;}
    if(op==3 && result){connection_poisoned=1;return -EIO;}
    if(op==0 && result>0)memcpy((void *)buffer,reply+16,(unsigned)result);
    return result;
}
long __aether_io(unsigned long op,unsigned long fd,unsigned long buffer,unsigned long count){
    int saved=errno;long result=inherited_io(op,fd,buffer,count);
#ifdef LEAK_ERRNO
    (void)saved;errno=EAGAIN;
#else
    errno=saved;
#endif
    return result;
}
extern int inherited_preflight(int fd,unsigned rights);
extern int inherited_read(int fd,unsigned char *r);
extern int inherited_close(int fd);
extern int inherited_after_close(int fd);
extern int inherited_fault(int fd);
