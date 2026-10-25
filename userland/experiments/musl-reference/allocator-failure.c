/* Bounded Linux data-limit exhaustion, not host/physical memory pressure. */
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define CHUNK (8u * 1024u * 1024u)
#define LIMIT 16
static int fail(int code, void **blocks, unsigned count)
{
    while (count) free(blocks[--count]);
    return code;
}
int main(int argc, char **argv)
{
    if (argc != 2 || (strcmp(argv[1], "64") && strcmp(argv[1], "256"))) return 10;
    void *blocks[LIMIT] = {0};
    unsigned count;
    for (count = 0; count < LIMIT; count++) {
        errno = 0;
        blocks[count] = malloc(CHUNK);
        if (!blocks[count]) {
            if (errno != ENOMEM) return fail(11, blocks, count);
            break;
        }
        memset(blocks[count], (int)(count + 1), CHUNK);
    }
    /* A roomy control must fail this oracle, not appear to test exhaustion. */
    if (!count || count == LIMIT) return fail(20, blocks, count);
    for (unsigned i = 0; i < count; i++) {
        volatile unsigned char *p = blocks[i];
        for (unsigned j = 0; j < CHUNK; j++)
            if (p[j] != i + 1) return fail(12, blocks, count);
    }
    unsigned char *saved = blocks[0];
    errno = 0;
    void *grown = realloc(saved, 128u * 1024u * 1024u);
    if (grown) {
        blocks[0] = grown;
        return fail(13, blocks, count);
    }
    if (errno != ENOMEM) return fail(14, blocks, count);
    for (unsigned j = 0; j < CHUNK; j++)
        if (saved[j] != 1) return fail(15, blocks, count);
    volatile size_t enormous = SIZE_MAX;
    errno = 0;
    void *overflow = calloc(enormous, 2);
    if (overflow) { free(overflow); return fail(16, blocks, count); }
    if (errno != ENOMEM) return fail(17, blocks, count);
    while (count) free(blocks[--count]);
    unsigned char *again = malloc(CHUNK);
    if (!again) return 18;
    memset(again, 0x6b, CHUNK);
    for (unsigned j = 0; j < CHUNK; j++)
        if (((volatile unsigned char *)again)[j] != 0x6b) { free(again); return 19; }
    free(again);
    static const char result[] = "AETHER ALLOCATOR FAILURE PASS\n";
    return write(1, result, sizeof result - 1) == sizeof result - 1 ? 0 : 21;
}
