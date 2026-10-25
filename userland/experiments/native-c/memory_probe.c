/* SPDX-License-Identifier: BSD-2-Clause */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
extern long native_memory_free_pages(void);
int native_memory_probe(void)
{
    long available = native_memory_free_pages();
    if (available < 32 || available > 128) return 61;
    /* Actual strict mallocng metadata protection precedes the direct checks. */
    unsigned char *p = malloc(1024);
    int retried = 0;
    if (!p && errno == EACCES) { retried = 1; p = malloc(1024); }
#ifdef REQUIRE_METADATA_RETRY
    if (!retried) { free(p); return 81; }
#else
    (void)retried;
#endif
    if (!p) return 62;
    memset(p, 0x5a, 1024);
    unsigned char *q = realloc(p, 8192);
    if (!q) { free(p); return 63; }
    for (unsigned i=0;i<1024;i++) if (q[i]!=0x5a) return 64;
    errno=0;p=realloc(q,128u*4096u);
    if (p || errno!=ENOMEM) { free(p ? p : q); return 65; }
    for (unsigned i=0;i<1024;i++) if(q[i]!=0x5a)return 66;
    free(q);
    q=calloc(128,8);if(!q)return 67;
    for(unsigned i=0;i<1024;i++)if(q[i])return 68;
    free(q);
    /* Metadata may remain retained: query after allocator warm-up. */
    long baseline=native_memory_free_pages();if(baseline<8)return 69;
    q=mmap(0,8192,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    if(q==MAP_FAILED)return 70;
    for(unsigned i=0;i<8192;i++)if(q[i])return 71;
    memset(q,0x6b,8192);
    if(mprotect(q+4096,4096,PROT_NONE))return 72;
    errno=0;if(write(1,q+4096,1)!=-1||errno!=EFAULT)return 73;
    if(mprotect(q,8192,PROT_READ|PROT_WRITE))return 74;
    for(unsigned i=0;i<8192;i++)if(q[i]!=0x6b)return 75;
    if(munmap(q,8192)||native_memory_free_pages()!=baseline)return 76;
    q=mmap(0,8192,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    if(q==MAP_FAILED)return 77;
    for(unsigned i=0;i<8192;i++)if(q[i])return 78;
    if(munmap(q,8192)||native_memory_free_pages()!=baseline)return 79;
    errno=0;if(mmap(0,4096,PROT_READ,MAP_SHARED|MAP_ANONYMOUS,-1,0)!=MAP_FAILED||errno!=ENOSYS)return 80;
    return 0;
}
