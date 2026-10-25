/* SPDX-License-Identifier: BSD-2-Clause */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
void stdio_deny_seek_once(void);
unsigned stdio_vector_witness(void);
#define CHECK(x,n) do{if(!(x))return(n);}while(0)
int libc_probe(int fd){
    char buffer[16],data[40]={0};
    errno=0;CHECK(!fdopen(fd,"a") && errno==ENOTSUP,180);
    errno=0;CHECK(!fdopen(fd,"re") && errno==ENOTSUP,181);
    FILE *f=fdopen(fd,"r+");CHECK(f,182);
    CHECK(setvbuf(f,buffer,_IOFBF,sizeof buffer)==0,183);
    CHECK(fwrite("abcdef",1,6,f)==6 && fwrite("ghijklmnopqrstuvwxyz",1,20,f)==20,184);
    CHECK(fflush(f)==0 && fseek(f,0,SEEK_SET)==0,185);
    CHECK(fread(data,1,26,f)==26 && !memcmp(data,"abcdefghijklmnopqrstuvwxyz",26),186);
    CHECK(fgetc(f)==EOF && feof(f) && !ferror(f),187);
    CHECK(fseek(f,0,SEEK_SET)==0 && !feof(f) && fgetc(f)=='a',188);
    stdio_deny_seek_once();errno=0;
    CHECK(fflush(f)==EOF && errno==EIO && ferror(f),189);
    clearerr(f);CHECK(fflush(f)==0 && fgetc(f)=='b',190); /* unread bytes retained on failed sync */
    CHECK(fseek(f,0,SEEK_SET)==0 && fread(data,1,26,f)==26 && !memcmp(data,"abcdefghijklmnopqrstuvwxyz",26),191);
    CHECK(fseek(f,60,SEEK_SET)==0 && fwrite("overflow",1,8,f)==8,192);
    errno=0;CHECK(fflush(f)==EOF && errno==ENOSPC && ferror(f),193);
    clearerr(f);CHECK(fseek(f,0,SEEK_SET)==0 && fread(data,1,26,f)==26 && !memcmp(data,"abcdefghijklmnopqrstuvwxyz",26),194);
    CHECK(fseek(f,60,SEEK_SET)==0 && fwrite("overflow",1,8,f)==8,195);
    errno=0;CHECK(fclose(f)==EOF && errno==ENOSPC,196);
    errno=0;CHECK(close(fd)==-1 && errno==EBADF,197);
    FILE *ro=fopen("out","r");CHECK(ro,198);
    CHECK(fread(data,1,sizeof data,ro)==26 && !memcmp(data,"abcdefghijklmnopqrstuvwxyz",26) && feof(ro),199);
    CHECK(fclose(ro)==0 && fflush(0)==0,200);
    errno=0;CHECK(!fopen("out","w") && errno==ENOTSUP,201);
    CHECK(stdio_vector_witness(),202);
    return 0;
}
