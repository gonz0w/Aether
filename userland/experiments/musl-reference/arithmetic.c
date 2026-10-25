#include <unistd.h>
/* Expected values computed independently with Python arbitrary-precision integers. */
static volatile struct { unsigned __int128 a, b, q, r; } vectors[] = {
    { (((unsigned __int128)0x0ULL << 64) | 0x0ULL), (((unsigned __int128)0x0ULL << 64) | 0x1ULL), (((unsigned __int128)0x0ULL << 64) | 0x0ULL), (((unsigned __int128)0x0ULL << 64) | 0x0ULL) },
    { (((unsigned __int128)0xffffffffffffffffULL << 64) | 0xffffffffffffffffULL), (((unsigned __int128)0x2ULL << 64) | 0x7ULL), (((unsigned __int128)0x0ULL << 64) | 0x7ffffffffffffffeULL), (((unsigned __int128)0x0ULL << 64) | 0x800000000000000dULL) },
    { (((unsigned __int128)0x1000000000ULL << 64) | 0x3039ULL), (((unsigned __int128)0x0ULL << 64) | 0x25ULL), (((unsigned __int128)0x6eb3e453ULL << 64) | 0x6eb3e45306eb531ULL), (((unsigned __int128)0x0ULL << 64) | 0x24ULL) },
    { (((unsigned __int128)0x8000000000000000ULL << 64) | 0x0ULL), (((unsigned __int128)0x1ULL << 64) | 0x1ULL), (((unsigned __int128)0x0ULL << 64) | 0x7fffffffffffffffULL), (((unsigned __int128)0x0ULL << 64) | 0x8000000000000001ULL) }
};
__attribute__((noinline)) unsigned __int128 quotient(unsigned __int128 a, unsigned __int128 b) { return a/b; }
__attribute__((noinline)) unsigned __int128 remainder128(unsigned __int128 a, unsigned __int128 b) { return a%b; }
__attribute__((noinline)) __int128 signed_quotient(__int128 a, __int128 b) { return a/b; }
int main(void)
{
    for (unsigned i=0; i<sizeof vectors/sizeof vectors[0]; i++) {
        if (quotient(vectors[i].a, vectors[i].b) != vectors[i].q) return 20+i;
        if (remainder128(vectors[i].a, vectors[i].b) != vectors[i].r) return 30+i;
    }
    if (signed_quotient(-(__int128)vectors[2].a, (__int128)vectors[2].b) != -(__int128)vectors[2].q) return 40;
    const char msg[]="AETHER BUILTINS PASS\n";
    return write(1,msg,sizeof msg-1)==sizeof msg-1 ? 0 : 41;
}
