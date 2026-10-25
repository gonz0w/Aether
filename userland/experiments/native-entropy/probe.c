/* SPDX-License-Identifier: BSD-2-Clause */
#include "entropy.h"
#include <errno.h>
#include <stdint.h>
#include <sys/auxv.h>
#include <sys/mman.h>

#define CHECK(condition, code)                                                 \
    do {                                                                       \
        if (!(condition))                                                      \
            return (code);                                                     \
    } while (0)

int diagnostic_probe(void)
{
    unsigned long grant = getauxval(0xa002);
    unsigned char bytes[258];
    for (unsigned i = 0; i < sizeof bytes; ++i)
        bytes[i] = 0xa5;
#ifdef DISABLED
    CHECK(grant == 0, 200);
    CHECK(aether_entropy_draw(grant, bytes + 1, 16) == -ENOSYS, 201);
    CHECK(aether_entropy_close(grant) == -ENOSYS, 202);
#else
    CHECK(grant != 0, 200);
    CHECK(aether_entropy_draw(grant ^ 3, bytes + 1, 16) == -EACCES, 201);
    CHECK(aether_entropy_draw(grant ^ 256, bytes + 1, 16) == -EACCES, 202);
#ifdef SUPERVISED
    unsigned long generation = (grant >> 8) & 255;
    CHECK(generation == 1 || generation == 2, 203);
    CHECK(aether_entropy_draw(grant - 256, bytes + 1, 16) == -EACCES, 204);
#endif
    CHECK(aether_entropy_draw(grant, bytes + 1, 0) == -EINVAL, 205);
    CHECK(aether_entropy_draw(grant, bytes + 1, 257) == -EINVAL, 206);
    CHECK(aether_entropy_draw(grant, 0, 16) == -EFAULT, 207);
    CHECK(aether_entropy_draw(grant, (void *)(UINTPTR_MAX - 7), 16) == -EFAULT,
          208);
    CHECK(aether_entropy_draw(grant, "immutable", 8) == -EFAULT, 209);
    for (unsigned i = 0; i < sizeof bytes; ++i)
        CHECK(bytes[i] == 0xa5, 210);
    unsigned char *pages =
        mmap(0, 8192, PROT_NONE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    CHECK(pages != MAP_FAILED, 211);
    CHECK(mprotect(pages, 4096, PROT_READ | PROT_WRITE) == 0, 212);
    for (unsigned i = 0; i < 256; ++i)
        pages[4096 - 256 + i] = 0xa5;
    CHECK(aether_entropy_draw(grant, pages + 4096 - 8, 16) == -EFAULT, 213);
    for (unsigned i = 0; i < 256; ++i)
        CHECK(pages[4096 - 256 + i] == 0xa5, 214);
    CHECK(aether_entropy_draw(grant, pages + 4096 - 256, 256) == 256, 215);
    CHECK(munmap(pages, 8192) == 0, 216);
    for (unsigned i = 0; i < 15; ++i) {
        errno = EDOM;
        CHECK(aether_entropy_draw(grant, bytes + 1, 256) == 256, 217);
        CHECK(errno == EDOM && bytes[0] == 0xa5 && bytes[257] == 0xa5, 218);
    }
    CHECK(aether_entropy_draw(grant, bytes + 1, 1) == -ENOSPC, 219);
    CHECK(aether_entropy_close(grant) == 0, 220);
    CHECK(aether_entropy_draw(grant, bytes + 1, 1) == -EBADF, 221);
    CHECK(aether_entropy_close(grant) == -EBADF, 222);
#endif
    return 0;
}
