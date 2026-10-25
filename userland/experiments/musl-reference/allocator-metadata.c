#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <unistd.h>

static int active, deny_once;
static unsigned metadata_maps, denied;
void *__real___mmap(void *, size_t, int, int, int, off_t);
void *__wrap___mmap(void *p, size_t n, int prot, int flags, int fd, off_t off)
{
    if (active && !p && prot == PROT_NONE) {
        metadata_maps++;
        if (deny_once) { deny_once = 0; denied++; errno = ENOMEM; return MAP_FAILED; }
    }
    return __real___mmap(p,n,prot,flags,fd,off);
}
int main(int argc, char **argv)
{
    if (argc != 2 || (strcmp(argv[1], "pass") && strcmp(argv[1], "deny-metadata") &&
        strcmp(argv[1], "no-guard"))) return 10;
    uintptr_t initial = (uintptr_t)syscall(SYS_brk, 0);
    if (!initial || initial % 4096) return 11;
    void *guard = MAP_FAILED;
    if (strcmp(argv[1], "no-guard")) {
        guard = mmap((void *)(initial + 4096), 4096, PROT_NONE,
            MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE, -1, 0);
        if (guard == MAP_FAILED || guard != (void *)(initial + 4096)) return 12;
    }
    active = 1;
    deny_once = !strcmp(argv[1], "deny-metadata");
    unsigned char *p = malloc(1024);
    if (!strcmp(argv[1], "deny-metadata")) {
        if (p || errno != ENOMEM || denied != 1) { free(p); return 13; }
        p = malloc(1024);
    }
    if (!p) return 14;
    if (!metadata_maps) { free(p); return 20; }
    if ((uintptr_t)syscall(SYS_brk, 0) != initial) { free(p); return 15; }
    for (unsigned i = 0; i < 1024; i++) p[i] = (unsigned char)(i * 17);
    for (unsigned i = 0; i < 1024; i++)
        if (((volatile unsigned char *)p)[i] != (unsigned char)(i * 17)) return 16;
    free(p);
    p = malloc(1024);
    if (!p) return 17;
    memset(p, 0x5a, 1024);
    for (unsigned i = 0; i < 1024; i++)
        if (((volatile unsigned char *)p)[i] != 0x5a) return 18;
    free(p);
    if (guard != MAP_FAILED && munmap(guard, 4096)) return 19;
    static const char result[] = "AETHER ALLOCATOR METADATA PASS\n";
    return write(1, result, sizeof result - 1) == sizeof result - 1 ? 0 : 21;
}
