/* SPDX-License-Identifier: BSD-2-Clause */
/* Private single-thread experiment API: negative errno, no libc interposition. */
struct open_file { unsigned handle, position, refs; };
static struct open_file files[2];
static struct open_file *descriptors[4];
static int poisoned;
static void poison_connection(void){
#ifndef IGNORE_POISON
    poisoned=1;
#endif
}
static int free_fd(void){for(int i=0;i<4;i++)if(!descriptors[i])return i;return -EMFILE;}
static int valid_fd(int fd){return fd>=0 && fd<4 && descriptors[fd];}
static int file_rpc(unsigned op,unsigned h,unsigned off,unsigned n,const void *bytes,unsigned char *r){
    if(poisoned)return -EIO;
    unsigned char q[32]={0};put(q,op);put(q+4,h);put(q+8,off);put(q+12,n);
    if(bytes)memcpy(q+16,bytes,op==4?n:strlen(bytes));
    int result=exchange(q,r);
    /* Uncertain transport/protocol outcome ends this connection; never replay. */
    if(result < -4095 || result==-999 || result==-998 || result>16 ||
       (result<0 && (get(r+4)||get(r+8)))){poison_connection();return -EIO;}
    /* Validate operation-specific reply fields before publishing any state. */
    #ifndef RELAX_REPLY
    int opening=op==1 || op==5;
    if((result>=0 && ((opening && (result || !get(r+4) || get(r+8)>64)) ||
                       (!opening && (get(r+4)||get(r+8))) ||
                       (op==3 && result))) ){
        poison_connection();return -EIO;
    }
    #endif
    return result;
}
static int fd_open(unsigned root,const char *name,int create){
    if(poisoned)return -EIO;
    if(strlen(name)>=16)return -EINVAL;
    int fd=free_fd();if(fd<0)return fd;
    struct open_file *f=0;
    for(unsigned i=0;i<2;i++)if(!files[i].refs){f=&files[i];break;}
    if(!f)return -EMFILE;
    unsigned char r[32];int result=file_rpc(create?5:1,root,0,create?3:1,name,r);
    if(result<0)return result;
    if(result || !get(r+4)){poison_connection();return -EIO;}
    *f=(struct open_file){get(r+4),0,1};descriptors[fd]=f;return fd;
}
static int fd_close(int fd){
    if(!valid_fd(fd))return -EBADF;
    struct open_file *f=descriptors[fd];descriptors[fd]=0;
    --f->refs;
#ifdef EARLY_CLOSE
    int last=1;
#else
    int last=!f->refs;
#endif
    if(last){
#ifndef LEAK_CLOSE
        unsigned char r[32];int result=file_rpc(3,f->handle,0,0,0,r);
        if(result){poison_connection();return -EIO;}
#endif
    }
    return poisoned?-EIO:0;
}
static int fd_dup2(int old,int dest){
    if(!valid_fd(old)||dest<0||dest>=4)return -EBADF;
    if(poisoned)return -EIO;
    if(old==dest)return dest;
    struct open_file *f=descriptors[old];
    /* No concurrency: retain source before releasing the destination. */
    ++f->refs;
    if(descriptors[dest] && fd_close(dest)<0){
#ifndef LEAK_RETAIN
        --f->refs;
#endif
        return -EIO;
    }
    descriptors[dest]=f;return dest;
}
static int fd_dup(int old){
    if(!valid_fd(old))return -EBADF;
    int dest=free_fd();return dest<0?dest:fd_dup2(old,dest);
}
static int fd_position(int fd,unsigned position){
    if(!valid_fd(fd))return -EBADF;
    if(poisoned)return -EIO;
    if(position>64)return -EINVAL;
    descriptors[fd]->position=position;return 0;
}
static int fd_io(int fd,void *bytes,unsigned n,int writing){
    if(!valid_fd(fd))return -EBADF;
    if(n>16)return -EINVAL;
    struct open_file *f=descriptors[fd];unsigned char r[32];
    int result=file_rpc(writing?4:2,f->handle,f->position,n,writing?bytes:0,r);
    if(result<0)return result;
    if((unsigned)result>n || get(r+4)||get(r+8)){poison_connection();return -EIO;}
    if(!writing)memcpy(bytes,r+16,(unsigned)result);
#ifndef FROZEN_OFFSET
    f->position+=(unsigned)result;
#endif
    return result;
}
