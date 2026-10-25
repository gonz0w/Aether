/* SPDX-License-Identifier: BSD-2-Clause */
/* Test-only injection after a complete real service reply; raw oracle RPCs bypass it. */
static unsigned fault_op, exchanges, injections, observed_handle;
static int fault_exchange(unsigned char *q,unsigned char *r){
    ++exchanges;
    int result=exchange(q,r);
    if(fault_op && get(q)==fault_op && result>=0){
        fault_op=0;++injections;observed_handle=get(r+4);
#if FAILURE_MODE == 3
        put(r+4,1); /* invalid handle on a successful close reply */
        return result;
#elif FAILURE_MODE == 4
        return -EIO; /* close consumed remotely, acknowledgement replaced by error */
#else
        return -999; /* discard acknowledgement after service completion */
#endif
    }
    return result;
}
#define exchange fault_exchange
#include "fd-layer.h"
#undef exchange
static int descriptor_failures(unsigned root,unsigned write_root){
    (void)fd_dup;(void)fd_position;(void)fd_io; /* Each image exercises a different API subset. */
    unsigned char r[32];char b[4]={0};
    CHECK(write_root==0xf002,180);
#if FAILURE_MODE == 1
    fault_op=5;
    CHECK(fd_open(write_root,"out",1)==-EIO,181);
    CHECK(!valid_fd(0) && !files[0].refs && !files[1].refs,182);
    CHECK(observed_handle && rpc(2,observed_handle,0,1,0,r)==0,183);
    CHECK(rpc(5,write_root,0,3,"out",r)==-EEXIST,184); /* create actually happened */
    CHECK(rpc(3,observed_handle,0,0,0,r)==0,185);
#else
    int a=fd_open(write_root,"out",1);CHECK(a==0,186);
    struct open_file *source=descriptors[a];unsigned handle=source->handle;
#if FAILURE_MODE == 2
    fault_op=4;
    CHECK(fd_io(a,"abc",3,1)==-EIO && source->position==0,187);
    CHECK(rpc(2,handle,0,3,0,r)==3 && !memcmp(r+16,"abc",3),188);
#elif FAILURE_MODE == 3
    fault_op=3;
    CHECK(fd_close(a)==-EIO && !valid_fd(a) && !source->refs,189);
    CHECK(rpc(2,handle,0,1,0,r)==-EBADF,190);
#else
    int dest=fd_open(root,"message.txt",0);CHECK(dest==1,191);
    unsigned old=descriptors[dest]->handle;
    fault_op=3;
    CHECK(fd_dup2(a,dest)==-EIO && !valid_fd(dest) && descriptors[a]==source,192);
    CHECK(source->refs==1 && !files[1].refs,193);
    CHECK(rpc(2,old,0,1,0,r)==-EBADF && rpc(2,handle,0,1,0,r)==0,194);
#endif
#endif
    CHECK(injections==1 && poisoned,195);
    unsigned count=exchanges;
    CHECK(fd_open(root,"message.txt",0)==-EIO,196);
#if FAILURE_MODE == 2 || FAILURE_MODE == 4
    CHECK(fd_io(a,b,1,0)==-EIO && fd_dup(a)==-EIO && fd_position(a,0)==-EIO,197);
    CHECK(fd_close(a)==-EIO && !valid_fd(a) && !source->refs,198);
    CHECK(rpc(3,handle,0,0,0,r)==0,199); /* test-only service cleanup */
#else
    (void)b;
#endif
    CHECK(exchanges==count,200); /* neither retries nor cleanup used poisoned transport */
    return finish();
}
