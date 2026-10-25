#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
static _Thread_local volatile int tls_value = 7;
static long native(unsigned long op, unsigned long a, unsigned long b)
{
    long r;
    __asm__ __volatile__("int $0x81" : "=a"(r) : "a"(op), "D"(a), "S"(b) : "rcx", "rdx", "r8", "memory");
    return r;
}
static void yield(void) { (void)native(0x1fffe,0,0); }
static int send(int fd, const char *s)
{
    size_t n=strlen(s),offset=0;
    while(offset<n) {ssize_t r=write(fd,s+offset,n-offset);if(r<=0)return -1;offset+=(size_t)r;}
    return 0;
}
#ifdef NATIVE_MEMORY
extern int native_memory_probe(void);
static volatile unsigned startup_zero;
static volatile unsigned startup_data = 23;
#endif
int main(int argc, char **argv)
{
#ifdef NATIVE_MEMORY
    const char *environment = getenv("AETHER_PROBE");
    if (argc != 2 || strcmp(argv[1], "check") || !environment ||
        strcmp(environment, "reference") || startup_zero || startup_data != 23)
        return 82;
    int memory_result = native_memory_probe();
    if (memory_result) return memory_result;
#else
    (void)argc; (void)argv;
#endif
    char b[40]={0};
    if(tls_value!=7)return 10;
    errno=0;if(read(0,b,1)!=-1||errno!=EAGAIN)return 11;
    errno=0;if(read(1,b,1)!=-1||errno!=EBADF)return 12;
    errno=0;if(write(0,"x",1)!=-1||errno!=EBADF)return 13;
    int copy=dup(0);if(copy!=3||dup2(copy,copy)!=copy)return 14;
    if(dup2(copy,0)!=0)return 15;
    errno=0;if(dup2(99,0)!=-1||errno!=EBADF)return 16;
    int extra[4];for(int i=0;i<4;i++){extra[i]=dup(0);if(extra[i]!=4+i)return 17;}
    errno=0;if(dup(0)!=-1||errno!=EMFILE)return 18;
    for(int i=0;i<4;i++)if(close(extra[i]))return 19;
    if(native(0x20008,0,0)!=-13)return 20; /* No producer authority. */
    (void)native(0x20004,0,0);
    for(;;){errno=0;ssize_t r=read(0,b,0);if(r!=0)return 21; /* No consumption. */
        errno=0;r=read(copy,(void*)~0ul,4);if(r!=-1||errno!=EFAULT)return 22;
        r=read(copy,b,3);if(r==-1&&errno==EAGAIN){yield();continue;}if(r!=3)return 23;break;}
    size_t n=3;
    while(n<32){ssize_t r=read(0,b+n,sizeof b-n);if(r==-1&&errno==EAGAIN){yield();continue;}if(r<=0||r>4)return 24;n+=(size_t)r;}
    if(memcmp(b,"0123456789abcdefghijklmnopqrstuv",32))return 25;
    if(read(copy,b,1)!=0)return 26;
    if(close(0)||close(copy))return 27;
    errno=0;if(read(copy,b,1)!=-1||errno!=EBADF)return 28;
    if(native(0x21000,0,(unsigned long)b)!=-9)return 29; /* Revoked native stream. */
    int saved=dup(1);if(saved!=0)return 30;
    if(dup2(2,1)!=1)return 31;
    if(send(1,"native error stream\n"))return 32;
    if(send(saved,"native descriptors ok\n"))return 33;
    if(close(1)||close(2)||close(saved))return 34;
    errno=0;if(write(saved,"x",1)!=-1||errno!=EBADF)return 35;
    return 0;
}
