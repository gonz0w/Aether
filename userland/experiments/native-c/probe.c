#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static _Thread_local volatile unsigned tls_value = 17;
static volatile unsigned zeroed;
static volatile unsigned initialized = 23;

int main(int argc, char **argv)
{
    const char *setting = getenv("AETHER_PROBE");
    if (argc != 2 || strcmp(argv[1], "check") || !setting ||
        strcmp(setting, "reference") || zeroed || initialized != 23 ||
        tls_value != 17)
        return 10;
    unsigned instance = (unsigned)(argv[0][11] - '0');
    if (instance < 1 || instance > 2) return 16;
    tls_value = 29 + instance;
    for (unsigned round = 0; round < 64; round++) {
        unsigned long sent = 0x1122334400000000ul + instance, got;
        __asm__ __volatile__("movq %1,%%xmm0; int $0x81; movq %%xmm0,%0"
            : "=r"(got) : "r"(sent), "a"(0x1fffeul) : "xmm0", "memory");
        if (got != sent || tls_value != 29 + instance) return 17;
    }
    errno = 0;
    if (write(-1, "x", 1) != -1 || errno != EBADF)
        return 11;
#ifdef NATIVE_FAULT_FIRST
    if (instance == 1) __asm__ __volatile__("ud2");
#endif
    errno = 0;
    if (write(1, (const void *)0xfffffffffffffffful, 1) != -1 || errno != EFAULT)
        return 18;
    if (write(1, "", 0) != 0) return 19;
    long unsupported;
    __asm__ __volatile__("int $0x81" : "=a"(unsupported) : "a"(0x1fffful) : "memory");
    if (unsupported != -38) return 20;
#ifdef WITH_ALLOCATOR
    unsigned char *p = malloc(131072);
    if (!p) return 12;
    memset(p, 0xa5, 131072);
    for (unsigned i = 0; i < 131072; i++)
        if (((volatile unsigned char *)p)[i] != 0xa5) return 13;
    free(p);
#endif
    const char message[] = "AETHER MUSL NATIVE PASS\n";
    size_t offset = 0;
    while (offset < sizeof message - 1) {
        ssize_t n = write(1, message + offset, sizeof message - 1 - offset);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) return 14;
        offset += (size_t)n;
    }
#ifdef NATIVE_SUPERVISED
    long denied;
    __asm__ __volatile__("int $0x81" : "=a"(denied) : "a"(0x20000ul), "D"(0xa001ul), "S"(0ul) : "rcx", "rdx", "memory");
    if (denied != -13) return 21;
    unsigned long generation;
    __asm__ __volatile__("int $0x81" : "=a"(generation) : "a"(0x20005ul) : "rcx", "rdx", "memory");
    __asm__ __volatile__("int $0x81" : : "a"(0x20004ul) : "rcx", "rdx", "memory");
    for (unsigned round = 0; instance == 2 || round < 64; round++) {
        __asm__ __volatile__("int $0x81" : : "a"(0x1fffeul) : "rcx", "rdx", "memory");
    }
    if (generation == 1) __asm__ __volatile__("ud2");
#endif
    return tls_value == 29 + instance ? 0 : 15;
}
