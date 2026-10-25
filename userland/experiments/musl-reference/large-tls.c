/* Linux reference fixture: initialized and zero-filled TLS beyond builtin_tls. */
#include <stdint.h>
#include <unistd.h>

_Alignas(64) static _Thread_local volatile unsigned char initialized[8192] = {
    [0] = 17, [4096] = 93, [8191] = 201
};
_Alignas(64) static _Thread_local volatile unsigned char zeroed[8192];

int main(int argc, char **argv)
{
    if (argc != 2 || argv[1][0] != 'c' || argv[1][1]) return 10;
    if ((uintptr_t)initialized % 64 || (uintptr_t)zeroed % 64) return 11;
    for (unsigned i = 0; i < 8192; i++) {
        unsigned char expected = i == 0 ? 17 : i == 4096 ? 93 : i == 8191 ? 201 : 0;
        if (initialized[i] != expected || zeroed[i] != 0) return 12;
        initialized[i] = (unsigned char)(i * 7 + 3);
        zeroed[i] = (unsigned char)(i * 11 + 5);
    }
    for (unsigned i = 0; i < 8192; i++)
        if (initialized[i] != (unsigned char)(i * 7 + 3) ||
            zeroed[i] != (unsigned char)(i * 11 + 5)) return 13;
    static const char result[] = "AETHER LARGE TLS PASS\n";
    return write(1, result, sizeof result - 1) == sizeof result - 1 ? 0 : 14;
}
