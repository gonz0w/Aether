#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

static unsigned remap_calls, injected_failures;
static int inject;
void *__real___mremap(void *, size_t, size_t, int, ...);
void *__wrap___mremap(void *old, size_t before, size_t after, int flags, ...)
{
    remap_calls++;
    /* This fixture only supports the allocator's four-argument MAYMOVE call. */
    if (flags != MREMAP_MAYMOVE) _exit(11);
    if (inject) { injected_failures++; errno = ENOSYS; return MAP_FAILED; }
    return __real___mremap(old, before, after, flags);
}
int main(int argc, char **argv)
{
    if (argc != 2 || (strcmp(argv[1], "pass") && strcmp(argv[1], "real-remap") &&
        strcmp(argv[1], "corrupt-copy"))) return 10;
    inject = strcmp(argv[1], "real-remap") != 0;
    const size_t before = 1024u * 1024u, after = 2u * 1024u * 1024u;
    unsigned char *p = malloc(before);
    if (!p) return 12;
    for (size_t i = 0; i < before; i++) p[i] = (unsigned char)(i * 17 + i / 4096);
    uintptr_t original = (uintptr_t)p;
    unsigned char *q = realloc(p, after);
    if (!q) { free(p); return 13; }
    if (remap_calls != 1 || injected_failures != 1) { free(q); return 20; }
    if ((uintptr_t)q == original) { free(q); return 14; }
    if (!strcmp(argv[1], "corrupt-copy")) q[0] ^= 1;
    for (size_t i = 0; i < before; i++)
        if (((volatile unsigned char *)q)[i] != (unsigned char)(i * 17 + i / 4096)) {
            free(q); return 21;
        }
    memset(q + before, 0x6b, after - before);
    for (size_t i = before; i < after; i++)
        if (((volatile unsigned char *)q)[i] != 0x6b) { free(q); return 15; }
    free(q);
    static const char result[] = "AETHER ALLOCATOR FALLBACK PASS\n";
    return write(1, result, sizeof result - 1) == sizeof result - 1 ? 0 : 16;
}
