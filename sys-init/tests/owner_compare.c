// SPDX-License-Identifier: BSD-2-Clause
// Host-only oracle for the separately selected, unchanged musl comparison leaf.
#include <stddef.h>
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>

extern int aether_owner_memcmp(const void *, const void *, size_t);

static int sign(int value) { return (value > 0) - (value < 0); }

static int check(const unsigned char *left, const unsigned char *right,
                 size_t size)
{
    int expected = 0;
    for (size_t index = 0; index < size; ++index) {
        if (left[index] != right[index]) {
            expected = left[index] < right[index] ? -1 : 1;
            break;
        }
    }
    if (sign(aether_owner_memcmp(left, right, size)) != expected) {
        fputs("comparison ordering mismatch\n", stderr);
        return 1;
    }
    return 0;
}

int main(void)
{
    for (unsigned int left = 0; left < 256; ++left) {
        for (unsigned int right = 0; right < 256; ++right) {
            unsigned char a = (unsigned char)left;
            unsigned char b = (unsigned char)right;
            if (check(&a, &b, 1)) {
                return 1;
            }
        }
    }
    const size_t lengths[] = {0,  1,  2,  3,  7,   8,   15,  16,
                              31, 32, 63, 64, 255, 256, 4096};
    unsigned char left[4128];
    unsigned char right[4128];
    for (size_t a = 0; a < 16; ++a) {
        for (size_t b = 0; b < 16; ++b) {
            for (size_t item = 0; item < sizeof(lengths) / sizeof(lengths[0]);
                 ++item) {
                size_t size = lengths[item];
                for (size_t index = 0; index <= size; ++index) {
                    left[a + index] = right[b + index] =
                        (unsigned char)(index * 73);
                }
                // A difference just outside the range must have no effect.
                right[b + size] ^= 255;
                if (check(left + a, right + b, size)) {
                    return 1;
                }
                if (size != 0) {
                    const size_t positions[] = {0, size / 2, size - 1};
                    for (size_t item2 = 0; item2 < 3; ++item2) {
                        size_t position = positions[item2];
                        right[b + position] ^= 255;
                        if (check(left + a, right + b, size) ||
                            check(right + b, left + a, size)) {
                            return 1;
                        }
                        right[b + position] ^= 255;
                    }
                }
            }
        }
    }
    long page = sysconf(_SC_PAGESIZE);
    if (page <= 0) {
        return 2;
    }
    unsigned char *guard = mmap(NULL, (size_t)page * 2, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANON, -1, 0);
    if (guard == MAP_FAILED ||
        mprotect(guard + page, (size_t)page, PROT_NONE) != 0) {
        return 2;
    }
    for (size_t index = 0; index < (size_t)page; ++index) {
        guard[index] = (unsigned char)(index * 73);
    }
    // Both zero-length pointers may address inaccessible storage. Equal ranges
    // end exactly at the guard; a word-rounded overread must fault this test.
    if (aether_owner_memcmp(guard + page, guard + page, 0) != 0) {
        return 1;
    }
    for (size_t size = 1; size <= 4096 && size <= (size_t)page; ++size) {
        if (check(guard + page - size, guard + page - size, size)) {
            return 1;
        }
    }
    if (munmap(guard, (size_t)page * 2) != 0) {
        return 2;
    }
    puts("unsigned ordering, bounded ranges and guard pages pass");
    return 0;
}
