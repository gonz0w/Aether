/* SPDX-License-Identifier: BSD-2-Clause */
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static int output(const char *p, size_t n) {
    while (n) { ssize_t k=write(1,p,n); if(k<0){if(errno==EINTR)continue;return -1;} if(!k)return -1; p+=k;n-=k; } return 0;
}
int main(int argc,char **argv) {
    char b[4096]; ssize_t n;
    if(argc<2)return 90;
    if(!strcmp(argv[1],"argv")) {
        if(argc!=4 || strcmp(argv[2],"a b") || strcmp(argv[3],"*") || !getenv("WITNESS") || strcmp(getenv("WITNESS"),"value"))return 91;
        return output("argv ok\n",8)?92:0;
    }
    if(!strcmp(argv[1],"status"))return 7;
    if(!strcmp(argv[1],"copy")) { while((n=read(0,b,sizeof b))!=0){if(n<0){if(errno==EINTR)continue;return 93;}if(output(b,n))return 94;}return 0; }
    if(!strcmp(argv[1],"closed")) { for(int i=3;i<64;i++){errno=0;if(fcntl(i,F_GETFD)!=-1 || errno!=EBADF)return 95;}return 0; }
    if(!strcmp(argv[1],"one"))return read(0,b,1)==1?0:96;
    if(!strcmp(argv[1],"pump")) { if(signal(SIGPIPE,SIG_IGN)==SIG_ERR)return 97; memset(b,'x',sizeof b); for(int i=0;i<4096;i++)if(output(b,sizeof b))return errno==EPIPE?42:98;return 99; }
    return 90;
}
