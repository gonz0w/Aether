/* SPDX-License-Identifier: BSD-2-Clause */
#include "adapter.h"
#include <sys/auxv.h>
#include <sys/mman.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
static _Thread_local volatile unsigned tls_value = 17;
#ifndef METADATA_DENIAL
static unsigned tid_storage;
#endif
#define CHECK(x, n) do { if (!(x)) return (n); } while (0)
int main(int argc, char **argv)
{
    CHECK(argc == 2, 60);
    unsigned instance = argv[0][11] - '0';
    unsigned long cap = getauxval(0xa000);
    CHECK(cap, 61);
    long initial = memtrap(0x22000, cap, 0, 0, 0);
    #ifdef LARGE_MEMORY
    CHECK(initial > 1536 && initial < 2048, 62);
#if !defined(METADATA_DENIAL)
    /* Fill and verify all four leaf spans, then release only the middle leaf. */
    volatile unsigned char *wide = mmap(0, (size_t)initial * 4096, 3,
                                       MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    CHECK(wide != MAP_FAILED, 120);
    for (size_t i=0; i<(size_t)initial*4096; i++) {
        CHECK(wide[i]==0,121); wide[i]=(unsigned char)(i/4096+instance);
    }
#ifdef FAULT_WRITE
    CHECK(mprotect((void *)(wide+511*4096),2*4096,PROT_READ)==0,122);
    if (instance==1) wide[512*4096]=1;
#endif
    CHECK(mprotect((void *)(wide+511*4096),2*4096,PROT_NONE)==0,122);
#ifdef FAULT_READ
    if (instance==1) { volatile unsigned char bad=wide[512*4096]; (void)bad; }
#endif
    CHECK(memtrap(0x10001,1,(uintptr_t)(wide+512*4096),1,0)==-14,123);
    CHECK(mprotect((void *)(wide+511*4096),2*4096,3)==0,124);
    CHECK(wide[511*4096]==(unsigned char)(511+instance),125);
    CHECK(wide[512*4096]==(unsigned char)(512+instance),126);
    CHECK(munmap((void *)(wide+512*4096),512*4096)==0,127);
#ifdef FAULT_UNMAP
    if (instance==1) { volatile unsigned char bad=wide[512*4096]; (void)bad; }
#endif
    CHECK(wide[0]==instance && wide[1024*4096]==(unsigned char)(1024+instance),128);
    volatile unsigned char *middle=mmap(0,512*4096,3,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
#ifdef BAD_BOUNDARY
    CHECK(middle!=wide+512*4096,129);
#else
    CHECK(middle==wide+512*4096,129);
#endif
    for (size_t i=0;i<512*4096;i++) CHECK(middle[i]==0,130);
    CHECK(munmap((void *)wide,(size_t)initial*4096)==0,131);
#endif
#else
    CHECK(initial > 32 && initial < 128, 62);
#endif
    CHECK(memtrap(0x22001, 0, 4096, 3, 0) == -13, 63);
    CHECK(memtrap(0x22001, cap >= 0x40000100 ? cap - 0x100 : cap + 0x100, 4096, 3, 0) == -13, 64);
    CHECK(memtrap(0x22001, cap ^ 3, 4096, 3, 0) == -13, 65);
    CHECK(memtrap(0x22001, cap, 0, 3, 0) == -22, 66);
    CHECK(memtrap(0x22001, cap, (unsigned long)-1, 3, 0) == -22, 67);
    /* Largest roundable size must reject by quota, never overflow in kernel. */
    CHECK(memtrap(0x22001, cap, (unsigned long)-4096, 3, 0) == -12, 180);
    CHECK(memtrap(0x22001, cap, (unsigned long)-4095, 3, 0) == -22, 181);
    CHECK(memtrap(0x22003, cap, 0x10000000, (unsigned long)-4096, 0) == -22, 182);
    CHECK(memtrap(0x22000, cap, 0, 0, 0) == initial, 183);
    CHECK(memtrap(0x22001, cap, 4096, 7, 0) == -13, 68);
    CHECK(memtrap(0x22001, cap, 4096, 8, 0) == -22, 69);
    CHECK(memtrap(0x22002, cap, 0x8000000, 4096, 3) == -13, 70);
    CHECK(memtrap(0x22003, cap, 0x200000, 4096, 0) == -13, 71);
#ifdef STOP_LIVE
    /* Saturate and inspect every reusable page before allocator metadata exists. */
    volatile unsigned char *held = mmap(0, (size_t)initial*4096, 3,
                                       MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    CHECK(held != MAP_FAILED && memtrap(0x22000,cap,0,0,0)==0,111);
    for (size_t i=0;i<(size_t)initial*4096;i++) {
        CHECK(held[i]==0,112); held[i]=(unsigned char)(instance+80);
    }
    CHECK(mmap(0,4096,3,MAP_PRIVATE|MAP_ANONYMOUS,-1,0)==MAP_FAILED && errno==ENOMEM,113);
    long generation=memtrap(0x20005,0,0,0,0);
    CHECK(generation==1 || generation==2,114);
    if (instance==1 && generation==1) {
        CHECK(mprotect((void *)(held+4096),4096,PROT_READ)==0,115);
        CHECK(mprotect((void *)(held+8192),4096,PROT_NONE)==0,116);
        CHECK(memtrap(0x100da,(uintptr_t)held,0,0,0)==instance,117);
        CHECK(memtrap(0x20004,0,0,0,0)==0,118);
        for (;;) memtrap(0x1fffe,0,0,0,0);
    }
    CHECK(munmap((void *)held,(size_t)initial*4096)==0,119);
#endif
    #ifndef METADATA_DENIAL
    volatile unsigned char *p = mmap(0, 12288, PROT_NONE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    CHECK(p != MAP_FAILED && memtrap(0x22000, cap, 0, 0, 0) == initial - 3, 72);
    CHECK(memtrap(0x10001, 1, (uintptr_t)p, 1, 0) == -14, 73);
    CHECK(mprotect((void *)p, 12288, PROT_READ|PROT_WRITE) == 0, 74);
    for (unsigned i = 0; i < 12288; i++) { CHECK(p[i] == 0, 75); p[i] = (unsigned char)(instance + 40); }
    CHECK(mprotect((void *)(p+4096), 4096, PROT_READ) == 0, 76);
    CHECK(p[4096] == instance + 40, 77);
    CHECK(memtrap(0x100da, (uintptr_t)(p+4096), 0, 0, 0) == -14, 78);
#ifdef FAULT_WRITE
    if (instance == 1) p[4096] = 1;
#endif
    CHECK(mprotect((void *)(p+4096), 4096, PROT_NONE) == 0, 79);
    CHECK(memtrap(0x10001, 1, (uintptr_t)(p+4096), 1, 0) == -14, 80);
    CHECK(memtrap(0x10001, 1, (uintptr_t)(p+4090), 16, 0) == -14, 80);
#ifdef FAULT_READ
    if (instance == 1) { volatile unsigned char bad = p[4096]; (void)bad; }
#endif
    CHECK(mprotect((void *)(p+4096), 4096, PROT_READ|PROT_WRITE) == 0, 81);
    CHECK(p[4096] == instance + 40, 82);
    CHECK(memtrap(0x100da, (uintptr_t)p, 0, 0, 0) == instance, 83);
    CHECK(munmap((void *)p, 4096) == -1 && errno == EACCES, 84);
    CHECK(mprotect((void *)p, 4096, PROT_NONE) == -1 && errno == EACCES, 85);
    CHECK(memtrap(0x100da, (uintptr_t)&tid_storage, 0, 0, 0) == instance, 86);
    unsigned long fs;
    __asm__ __volatile__("movq %%fs:0,%0" : "=r"(fs) : : "memory");
    CHECK(memtrap(0x1009e, 0x1002, (uintptr_t)(p+4096), 0, 0) == 0, 87);
    long pinned = memtrap(0x22003, cap, (uintptr_t)p, 4096, 0);
    long restored = memtrap(0x1009e, 0x1002, fs, 0, 0);
    CHECK(pinned == -13 && restored == 0, 88);
    CHECK(munmap((void *)(p+4096), 4096) == 0, 89);
#ifdef FAULT_UNMAP
    if (instance == 1) { volatile unsigned char bad = p[4096]; (void)bad; }
#endif
    CHECK(memtrap(0x22002, cap, (uintptr_t)p, 12288, 0) == -12, 90);
    CHECK(memtrap(0x22003, cap, (uintptr_t)p, 12288, 0) == -12, 91);
    CHECK(p[0] == instance + 40 && p[8192] == instance + 40, 92);
    volatile unsigned char *q = mmap(0, 4096, 3, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    CHECK(q == p+4096, 93);
    for (unsigned i = 0; i < 4096; i++) CHECK(q[i] == 0, 94);
    CHECK(munmap((void *)p, 12288) == 0, 95);
    for (unsigned round=0; round<
#ifdef LARGE_MEMORY
3
#else
40
#endif
; round++) {
        p=mmap(0, (size_t)initial*4096, 0, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
        CHECK(p != MAP_FAILED && memtrap(0x22000, cap, 0, 0, 0) == 0, 96);
        CHECK(mmap(0,4096,3,MAP_PRIVATE|MAP_ANONYMOUS,-1,0)==MAP_FAILED && errno==ENOMEM,97);
        CHECK(munmap((void *)p,(size_t)initial*4096)==0,98);
        CHECK(memtrap(0x22000,cap,0,0,0)==initial,99);
    }
    #else
    errno=0;
    void *denied=malloc(4096);
    CHECK(!denied && errno==EACCES,110);
    #endif
    /* Real strict musl mallocng: initial brk and remap remain unsupported. */
    unsigned char *a=malloc(4096); CHECK(a,100);
    memset(a,0x5a,4096);
    unsigned char *b=realloc(a,8192); CHECK(b,101);
    for (unsigned i=0;i<4096;i++) CHECK(b[i]==0x5a,102);
    errno=0; unsigned char *huge=realloc(b,
#ifdef LARGE_MEMORY
16*1024*1024
#else
1024*1024
#endif
);
    CHECK(!huge && errno==ENOMEM,103);
    for (unsigned i=0;i<4096;i++) CHECK(b[i]==0x5a,104);
    free(b);
    a=calloc(1024,4);CHECK(a,105);
    for (unsigned i=0;i<4096;i++) CHECK(a[i]==0,106);
    free(a);
    CHECK(tls_value==17,107);tls_value=instance;
    for(unsigned i=0;i<64;i++) {
        unsigned long operation=0x1fffe, got;
        unsigned long sent=0x1122334400000000ul+instance;
        __asm__ __volatile__("movq %2,%%xmm0; int $0x81; movq %%xmm0,%0"
            : "=r"(got), "+a"(operation) : "r"(sent) : "xmm0", "memory", "cc");
        CHECK(got==sent,174);
        CHECK(tls_value==instance,108);
    }
    const char text[]="AETHER MUSL NATIVE PASS\n";
    for(size_t i=0;i<sizeof(text)-1;) { ssize_t n=write(1,text+i,sizeof(text)-1-i);CHECK(n>0,109);i+=(size_t)n; }
    return 0;
}
