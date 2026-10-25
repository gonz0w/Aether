/* SPDX-License-Identifier: BSD-2-Clause */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <sys/syscall.h>
#include <unistd.h>

static int fallback,deny_at,denial,setters,denied,atomic_calls;
/* Only replacement-object syscall macros reach this hook. Real syscalls below
 * use the unmodified libc wrapper, preserving raw negative-error conventions. */
long test_raw(long n,long a,long b,long c) {
    if((n==SYS_fcntl && b==F_DUPFD_CLOEXEC) || n==SYS_pipe2){
        atomic_calls++;
        if(fallback)return n==SYS_pipe2?-ENOSYS:-EINVAL;
    }
    if(n==SYS_fcntl && (b==F_SETFD || b==F_SETFL)) {
        setters++;
        if(deny_at && setters==deny_at){denied++;return -denial;}
    }
    int saved=errno;
    long r=syscall(n,a,b,c);
    if(r<0)r=-errno;
    errno=saved;return r;
}
#define CHECK(x,n) do {if(!(x))return(n);}while(0)
static int rawflags(int fd,int cmd){return syscall(SYS_fcntl,fd,cmd,0);}
static unsigned long long live(void) {
    unsigned long long s=0;
    for(int i=0;i<64;i++)if(rawflags(i,F_GETFD)>=0)s|=1ULL<<i;
    return s;
}
static int close_pair(int *f) {return close(f[0])==0 && close(f[1])==0;}
int main(int argc,char **argv) {
    CHECK(argc==6,90);
    int strict=atoi(argv[1]),ispipe=!strcmp(argv[2],"pipe");
    fallback=atoi(argv[3]);deny_at=atoi(argv[4]);denial=atoi(argv[5]);
    int original=open("/dev/null",O_RDONLY);CHECK(original>=0 && original<64,91);
    unsigned long long before=live();
    int pair[2]={-7,-9};errno=0;
    int r=ispipe?pipe2(pair,O_CLOEXEC|O_NONBLOCK):fcntl(original,F_DUPFD_CLOEXEC,10);
    int e=errno;
    CHECK(atomic_calls==(fallback && !ispipe?2:1),92);
    CHECK(denied==(deny_at?1:0),93);
    int expected_setters=ispipe?(fallback?4:0):1;
    if(strict && fallback && deny_at)expected_setters=deny_at;
    CHECK(setters==expected_setters,94);
    int failed_flags=0;
    if(strict && fallback && deny_at){
        CHECK(r==-1 && e==denial,95);
        CHECK(!ispipe || (pair[0]==-7 && pair[1]==-9),96);
        CHECK(live()==before,97);
    }else{
        CHECK(r>=0,98);
        if(ispipe){
            CHECK(pair[0]>=0 && pair[1]>=0 && pair[0]<64 && pair[1]<64,99);
            for(int i=0;i<2;i++)if(!(rawflags(pair[i],F_GETFD)&FD_CLOEXEC) || !(rawflags(pair[i],F_GETFL)&O_NONBLOCK))failed_flags=1;
            CHECK(close_pair(pair),100);
        }else{
            CHECK(r>=10 && r<64,101);
            failed_flags=!(rawflags(r,F_GETFD)&FD_CLOEXEC);
            CHECK(close(r)==0,102);
        }
        CHECK(failed_flags==(!strict && fallback && deny_at!=0),103);
        CHECK(live()==before,104);
    }
    CHECK(rawflags(original,F_GETFD)==0,105);
    /* Disable denial, retaining fallback selection; prove successful retry. */
    deny_at=0;setters=denied=atomic_calls=0;
    if(ispipe){CHECK(pipe2(pair,O_CLOEXEC|O_NONBLOCK)==0,106);
        for(int i=0;i<2;i++)CHECK((rawflags(pair[i],F_GETFD)&FD_CLOEXEC) && (rawflags(pair[i],F_GETFL)&O_NONBLOCK),107);
        CHECK(close_pair(pair),108);
    }else{r=fcntl(original,F_DUPFD_CLOEXEC,10);CHECK(r>=10 && (rawflags(r,F_GETFD)&FD_CLOEXEC),109);CHECK(close(r)==0,110);}
    CHECK(live()==before && close(original)==0,111);
    return failed_flags?20:0;
}
