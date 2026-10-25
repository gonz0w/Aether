/* SPDX-License-Identifier: BSD-2-Clause */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>

static volatile int global_value=17;
static _Thread_local int tls_value=23;
#define CHECK(x, code) do { if (!(x)) return (code); } while (0)
static int reaped(pid_t p,int expected) {
    int s; pid_t r;
    do {r=waitpid(p,&s,0);}while(r<0 && errno==EINTR);
    if(r!=p || !WIFEXITED(s) || WEXITSTATUS(s)!=expected)return 0;
    errno=0;return waitpid(p,&s,WNOHANG)==-1 && errno==ECHILD;
}
static int file(void) {
    int fd=open("/scratch/file",O_CREAT|O_EXCL|O_RDWR,0600);
    if(fd<0)return -1;
    if(write(fd,"abcdef",6)!=6 || lseek(fd,0,SEEK_SET)!=0){close(fd);return -1;}
    return fd;
}
static int fork_state(int control) {
    int fd=file(),copy;char *heap=malloc(16),b;
    CHECK(fd>=0 && heap,90);heap[0]='P';
    copy=control?open("/scratch/file",O_RDWR):dup(fd);CHECK(copy>=0,91);
    CHECK(fcntl(fd,F_SETFD,FD_CLOEXEC)==0,92);
    pid_t p=fork();CHECK(p>=0,93);
    if(!p) {
        if(global_value!=17 || tls_value!=23 || heap[0]!='P')_exit(94);
        global_value=18;tls_value=24;heap[0]='C';
        if(lseek(copy,3,SEEK_SET)!=3 || fcntl(fd,F_SETFD,0)!=0)_exit(95);
        if(fcntl(fd,F_SETFL,fcntl(fd,F_GETFL,0)|O_APPEND)!=0)_exit(96);
        if(close(fd)!=0)_exit(97);
        _exit(7);
    }
    CHECK(reaped(p,7),98);
    CHECK(global_value==17 && tls_value==23 && heap[0]=='P',99);
    CHECK(fcntl(fd,F_GETFD,0)==FD_CLOEXEC,100);
    CHECK(fcntl(fd,F_GETFL,0)&O_APPEND,101);
    /* Reopening instead of duplicating must fail this shared-offset oracle. */
    CHECK(lseek(fd,0,SEEK_CUR)==3,20);
    CHECK(read(fd,&b,1)==1 && b=='d' && lseek(copy,0,SEEK_CUR)==4,102);
    CHECK(close(copy)==0 && close(fd)==0,103);free(heap);return 0;
}
static int exec_child(int argc,char **argv) {
    char b;
    CHECK(argc==3 && !strcmp(argv[2],"a b") && getenv("WITNESS") && !strcmp(getenv("WITNESS"),"value"),104);
    errno=0;CHECK(fcntl(40,F_GETFD,0)==-1 && errno==EBADF,21);
    CHECK(fcntl(41,F_GETFD,0)==0 && read(41,&b,1)==1 && b=='c',105);
    CHECK(close(41)==0,106);return 0;
}
static int exec_state(int control) {
    int fd=file();CHECK(fd>=0,107);
    CHECK(dup2(fd,40)==40 && dup2(fd,41)==41 && close(fd)==0,108);
    CHECK(fcntl(40,F_SETFD,control?0:FD_CLOEXEC)==0 && lseek(41,2,SEEK_SET)==2,109);
    pid_t p=fork();CHECK(p>=0,110);
    if(!p) {
        char *args[]={"qemu-x86_64","-strace","/inputs/probe","exec-child","a b",NULL};
        char *env[]={"WITNESS=value","LC_ALL=C",NULL};
        execve("/usr/bin/qemu-x86_64",args,env);_exit(111);
    }
    CHECK(reaped(p,control?21:0),112);
    CHECK(lseek(41,0,SEEK_CUR)==(control?2:3),113);
    CHECK(close(40)==0 && close(41)==0,114);
    return control?21:0;
}
static int failed_exec(void) {
    int fd=file();pid_t before=getpid();char cwd[64],after[64],b;
    CHECK(fd>=0 && getcwd(cwd,sizeof cwd),115);
    CHECK(fcntl(fd,F_SETFD,FD_CLOEXEC)==0 && lseek(fd,2,SEEK_SET)==2,116);
    char *args[]={"test",NULL},*env[]={NULL};
    errno=0;CHECK(execve("/inputs/missing",args,env)==-1 && errno==ENOENT,117);
    errno=0;CHECK(execve("/inputs/not-executable",args,env)==-1 && errno==EACCES,118);
    CHECK(getpid()==before && getcwd(after,sizeof after) && !strcmp(cwd,after),119);
    CHECK(global_value==17 && tls_value==23 && fcntl(fd,F_GETFD,0)==FD_CLOEXEC,120);
    CHECK(read(fd,&b,1)==1 && b=='c',121);
    int s;errno=0;CHECK(waitpid(-1,&s,WNOHANG)==-1 && errno==ECHILD,122);
    CHECK(close(fd)==0,123);return 0;
}
static int pipe_lifetime(int control) {
    int f[2],alias;char b;CHECK(pipe(f)==0,124);
    alias=dup(f[1]);CHECK(alias>=0 && fcntl(f[0],F_SETFL,O_NONBLOCK)==0,125);
    pid_t p=fork();CHECK(p>=0,126);
    if(!p){close(f[0]);close(alias);if(write(f[1],"x",1)!=1)_exit(127);close(f[1]);_exit(0);}
    CHECK(close(f[1])==0 && reaped(p,0),128);
    CHECK(read(f[0],&b,1)==1 && b=='x',129);
    errno=0;CHECK(read(f[0],&b,1)==-1 && errno==EAGAIN,130);
    if(!control)CHECK(close(alias)==0,131);
    int eof=read(f[0],&b,1)==0;
    if(control)CHECK(close(alias)==0,132);
    CHECK(close(f[0])==0,133);
    CHECK(eof,22);
    CHECK(pipe(f)==0 && close(f[0])==0,134);
    CHECK(signal(SIGPIPE,SIG_IGN)!=SIG_ERR,135);
    errno=0;CHECK(write(f[1],"x",1)==-1 && errno==EPIPE,136);
    CHECK(close(f[1])==0,137);return 0;
}
static int descriptor_exhaustion(void) {
    struct rlimit lim={32,32};int fd=file(),list[32],n=0,f[2];
    CHECK(fd>=0 && setrlimit(RLIMIT_NOFILE,&lim)==0,138);
    while(n<32){int d=dup(fd);if(d<0)break;list[n++]=d;}
    CHECK(n>1 && n<32 && errno==EMFILE,139);
    /* Leave one slot: a two-descriptor pipe must fail without consuming it. */
    CHECK(close(list[--n])==0,140);
    errno=0;CHECK(pipe(f)==-1 && errno==EMFILE,141);
    int d=dup(fd);CHECK(d>=0 && close(d)==0,142);
    CHECK(close(list[--n])==0 && pipe(f)==0,143);
    CHECK(close(f[0])==0 && close(f[1])==0,144);
    while(n)CHECK(close(list[--n])==0,145);
    CHECK(close(fd)==0,146);return 0;
}
static int vfork_exit(void) {
    pid_t p=vfork();if(!p)_exit(17);
    CHECK(p>0 && reaped(p,17),147);return 0;
}
int main(int argc,char **argv) {
    if(argc<2)return 89;
    if(!strcmp(argv[1],"fork"))return fork_state(0);
    if(!strcmp(argv[1],"reopen-control"))return fork_state(1);
    if(!strcmp(argv[1],"exec"))return exec_state(0);
    if(!strcmp(argv[1],"cloexec-control"))return exec_state(1);
    if(!strcmp(argv[1],"exec-child"))return exec_child(argc,argv);
    if(!strcmp(argv[1],"failed-exec"))return failed_exec();
    if(!strcmp(argv[1],"pipe"))return pipe_lifetime(0);
    if(!strcmp(argv[1],"writer-control"))return pipe_lifetime(1);
    if(!strcmp(argv[1],"fd-exhaustion"))return descriptor_exhaustion();
    if(!strcmp(argv[1],"vfork-exit"))return vfork_exit();
    return 88;
}
