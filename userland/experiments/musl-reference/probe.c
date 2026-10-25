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
    tls_value = 29;
    errno = 0;
    if (write(-1, "x", 1) != -1 || errno != EBADF)
        return 11;
#ifdef WITH_ALLOCATOR
    unsigned char *p = malloc(131072);
    if (!p) return 12;
    memset(p, 0xa5, 131072);
    for (unsigned i = 0; i < 131072; i++)
        if (((volatile unsigned char *)p)[i] != 0xa5) return 13;
    free(p);
#endif
    const char message[] = "AETHER MUSL REFERENCE PASS\n";
    size_t offset = 0;
    while (offset < sizeof message - 1) {
        ssize_t n = write(1, message + offset, sizeof message - 1 - offset);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) return 14;
        offset += (size_t)n;
    }
    return tls_value == 29 ? 0 : 15;
}
