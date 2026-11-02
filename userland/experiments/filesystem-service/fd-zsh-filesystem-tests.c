/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only actual entry/context/protocol controls. Native calls and filesystem
 * replies are doubles; this does not qualify native authority or terminfo data.
 */
#define _POSIX_C_SOURCE 200809L
#include "fd-zsh-external.h"
#include "fd-tinfo-directory.h"
#include "fd-libc.h"
#include <assert.h>
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static struct aefd_startup *boot;
static unsigned char startup[336], request[320], reply[4160];
static size_t at, sent, received, request_bytes, reply_bytes;
static unsigned mode, closes[2], source_closes[3], file_closes, files,
    ready_calls;
static unsigned blocks, restores, calls, probes, reentered;
static unsigned bits, reads, fail_allocate;
int aether_test_setenv(const char *, const char *, int);
void *aether_test_malloc(size_t);
int aether_test_setenv(const char *key, const char *value, int overwrite)
{
    if (mode == 46) {
        errno = ENOMEM;
        return -1;
    }
    return setenv(key, value, overwrite);
}
void *aether_test_malloc(size_t n)
{
    if (fail_allocate) {
        errno = ENOMEM;
        return NULL;
    }
    return malloc(n);
}
void aefd_test_filesystem_stdio(void);
static uint64_t revision = 1;
static char *publication;
static void put(unsigned char *p, unsigned at, uint32_t v)
{
    memcpy(p + at, &v, 4);
}
static uint32_t word(const unsigned char *p, unsigned at)
{
    uint32_t v;
    memcpy(&v, p + at, 4);
    return v;
}
static int startup_bad(void)
{
    return (mode >= 1 && mode <= 46) || mode >= 1000;
}
static int fatal(void) { return mode >= 50 && mode <= 66; }
static void respond(void)
{
    memset(reply, 0, sizeof(reply));
    if (memcmp(request, AEFD_MAGIC, 8)) {
        reply_bytes = 32;
        unsigned op = word(request, 0), selector = word(request, 8);
        if (op == 0x10 || op == 0x11) {
            put(reply, 4, op);
            put(reply, 8, 16);
            if (op == 0x11) {
                bits = 7;
                ++revision;
            }
            memcpy(reply + 16, &revision, 8);
            reply[24] = (unsigned char)bits;
            reply[28] = 1;
        } else {
            assert(op == 3 && selector < 3);
            ++source_closes[selector];
        }
        return;
    }
    reply_bytes = 64;
    memcpy(reply, AEFD_MAGIC, 8);
    aefd_put(reply, 2, 31);
    aefd_put(reply, 3, aefd_word(request, 3));
    unsigned op = (unsigned)aefd_word(request, 1);
    if (op == 1 || op == 4) {
        if (op == 1)
            reads = 0;
        ++files;
        aefd_put(reply, 4, files + 2);
    } else if (op == 2) {
        size_t count = reads++ ? 0 : 4;
        if (count > aefd_word(request, 5))
            count = (size_t)aefd_word(request, 5);
        aefd_put(reply, 4, count);
        aefd_put(reply, 5, count);
        reply_bytes = count ? 128 : 64;
        memcpy(reply + 64, "TERM", count);
    } else if (op == 3)
        aefd_put(reply, 4, 0);
    else if (op == 5)
        ++file_closes;
    else if (op == 6 || op == 8) {
    } else if (op == 9) {
        aefd_put(reply, 5, 2);
        reply_bytes = 128;
        reply[64] = '/';
        if (mode == 60)
            aefd_put(reply, 4, 2);
        if (mode == 61)
            aefd_put(reply, 5, 3);
        if (mode == 62)
            reply[64] = 'x';
        if (mode == 63)
            reply[65] = 'x';
        if (mode == 64)
            reply_bytes = 65;
        if (mode == 65)
            reply[66] = 1;
    } else {
        assert(op == 10);
        ++probes;
        aefd_put(reply, 5, 32);
        reply_bytes = 128;
        aefd_put(reply + 64, 0, 2);
        aefd_put(reply + 64, 1, 256);
        aefd_put(reply + 64, 2, 1);
        aefd_put(reply + 64, 3, 7);
        if (mode == 50)
            reply[0] ^= 1;
        if (mode == 51)
            aefd_put(reply, 3, 99);
        if (mode == 52)
            aefd_put(reply, 5, 31);
        if (mode == 53)
            aefd_put(reply + 64, 0, 1);
        if (mode == 54)
            aefd_put(reply + 64, 2, 0);
        if (mode == 55)
            aefd_put(reply + 64, 3, 0);
        if (mode == 56)
            reply[100] = 1;
        if (mode == 57)
            reply_bytes = 80;
        if (mode == 58 && probes == 2)
            aefd_put(reply + 64, 2, 2);
        if (mode == 59 && probes == 2)
            aefd_put(reply + 64, 3, 8);
    }
}
static int64_t call(void *owner, uint64_t op, uint64_t cap, uint64_t a,
                    uint64_t b, uint64_t c)
{
    assert(owner == &mode);
    ++calls;
    if (op == 0x1000e) {
        assert(c == 8);
        if (!cap) {
            ++blocks;
            *(uint64_t *)(uintptr_t)b = 0;
        } else {
            assert(cap == 2);
            ++restores;
            if (publication) {
                assert(publication[0] == '/' && !publication[1]);
                publication = NULL;
            }
        }
        return 0;
    }
    assert(!c);
    if (op == 0x10027)
        return 9;
    if (op == 0x1006e)
        return 7;
    if (op == 0x20004) {
        ++ready_calls;
        assert(bits == 7);
        return 0;
    }
    if (op == 0x24003) {
        assert(cap == 71 || cap == 72);
        ++closes[cap == 72];
        return 0;
    }
    assert(a && b && b <= 16);
    if (boot->phase == 1) {
        assert(op == 0x24001 && cap == 71);
        size_t n = (size_t)b,
               limit = mode >= 1000 ? mode - 1000 : sizeof(startup);
        if (n > limit - at)
            n = limit - at;
        memcpy((void *)(uintptr_t)a, startup + at, n);
        at += n;
        return (int64_t)n;
    }
    assert(boot->phase == 2 && boot->context.native.active);
    if (!reentered && boot->context.state == 1) {
        reentered = 1;
        char out[2] = {1, 1};
        unsigned before = calls;
        assert(!__wrap_getcwd(out, sizeof(out)) && errno == EBUSY &&
               calls == before && out[0] == 1);
    }
    if (op == 0x24002) {
        assert(cap == 72 && sent + b <= sizeof(request));
        memcpy(request + sent, (void *)(uintptr_t)a, (size_t)b);
        sent += (size_t)b;
        if (sent == 16)
            request_bytes = !memcmp(request, AEFD_MAGIC, 8) ? 64 : 32;
        if (sent == 64 && !memcmp(request, AEFD_MAGIC, 8)) {
            uint64_t opcode = aefd_word(request, 1);
            if (opcode == 1 || opcode == 8 || opcode == 10)
                request_bytes += ((aefd_word(request, 5) + 63) / 64) * 64;
        }
        if (sent == request_bytes)
            respond();
        return (int64_t)b;
    }
    assert(op == 0x24001 && cap == 71 && sent == request_bytes);
    size_t n = (size_t)b;
    if (n > reply_bytes - received)
        n = reply_bytes - received;
    memcpy((void *)(uintptr_t)a, reply + received, n);
    received += n;
    if (received == reply_bytes && n && !(mode == 57 && probes) &&
        !(mode == 64 && !memcmp(request, AEFD_MAGIC, 8) &&
          aefd_word(request, 1) == 9))
        sent = received = request_bytes = 0;
    return (int64_t)n;
}
int64_t aefd_startup_native(struct aefd_startup *b)
{
    boot = b;
    return aefd_startup_start(b, call, &mode,
                              (struct aefd_startup_auxv){0x40000102, 71, 72});
}
int aether_test_sigaction(int number, const struct sigaction *action,
                          struct sigaction *old)
{
    assert(number == SIGINT && action->sa_handler == SIG_IGN && !old);
    return 0;
}
_Noreturn void __assert_fail(const char *expr, const char *file, int line,
                             const char *fn)
{
    (void)dprintf(2, "FS_CONSUMER_ASSERT %s:%d %s (%s)\n", file, line, expr,
                  fn);
    abort();
}
_Noreturn void __real__exit(int status)
{
    assert(closes[0] == 1 && closes[1] == 1 && blocks == restores);
    assert(status == (startup_bad() ? 143 : fatal() ? 141 : 19));
    assert(ready_calls == (startup_bad() ? 0U : 1U));
    if (!startup_bad() && !fatal()) {
        assert(file_closes == 3);
        for (unsigned i = 0; i < 3; ++i)
            assert(source_closes[i] == 1);
    }
    unsigned before = calls;
    char out[2] = {1, 1};
    assert(!__wrap_getcwd(out, 2) && errno == EBADF && calls == before);
    assert(__wrap_getuid() == (uid_t)-1 && errno == EAGAIN);
    char marker[64];
    int n = snprintf(marker, sizeof(marker),
                     "ZSH_FILESYSTEM_CONSUMER_PASS %u\n", mode);
    assert(n > 0 && write(1, marker, (size_t)n) == n);
    _Exit(0);
}
int __real_main(int argc, char **argv)
{
    assert(argc == 4 && !strcmp(argv[0], "zsh") &&
           !strcmp(getenv("TERMINFO"), "/home/.terminfo") &&
           !strcmp(getenv("PS1"), "AETHER-ZSH> "));
    errno = ERANGE;
    assert(__wrap_getuid() == 1000 && __wrap_geteuid() == 1000 &&
           __wrap_getgid() == 1000 && __wrap_getegid() == 1000 &&
           errno == ERANGE);
    char root[8] = {1, 1, 1};
    if (mode >= 60 && mode <= 66) {
        if (mode == 66)
            ++boot->context.map.generation;
        assert(!__wrap_getcwd(root, sizeof(root)) && errno == EIO &&
               root[0] == 1 && root[1] == 1);
        return 19;
    }
    publication = root;
    assert(__wrap_getcwd(root, sizeof(root)) == root && !strcmp(root, "/") &&
           root[2] == 1 && errno == ERANGE);
    unsigned allocation_before = calls;
    fail_allocate = 1;
    assert(!__wrap_getcwd(NULL, 0) && errno == ENOMEM &&
           calls == allocation_before);
    fail_allocate = 0;
    errno = ERANGE;
    char *allocated = __wrap_getcwd(NULL, 0);
    assert(allocated && !strcmp(allocated, "/"));
    free(allocated);
    unsigned before = calls;
    assert(!__wrap_getcwd(root, 1) && errno == ERANGE && calls == before);
    assert(__wrap_access("/other", R_OK) == -1 && errno == ENOENT &&
           calls == before);
    assert(__wrap_access("/home/.terminfo/v/vt100", W_OK) == -1 &&
           errno == EOPNOTSUPP && calls == before);
    assert(aether_zsh_open("/home/.terminfo/../v/vt100", O_RDONLY, 0) == -1 &&
           errno == ENOENT && calls == before);
    assert(__wrap_access("/home/.terminfo/v/vt100", F_OK) == 0);
    assert(__wrap_access("/home/.terminfo/./v/vt100", R_OK) == 0);
    struct aether_tinfo_directory_view first = {0}, second = {0};
    if (fatal()) {
        struct aether_tinfo_directory_view original = {9, 9, 9, 9};
        first = original;
        if (mode >= 58)
            assert(!aether_tinfo_directory_probe("/home/.terminfo", &second));
        assert(aether_tinfo_directory_probe("/home/.terminfo", &first) == -1 &&
               errno == EIO && !memcmp(&first, &original, sizeof(first)));
        before = calls;
        assert(aether_tinfo_directory_probe("/home/.terminfo", &first) == -1 &&
               calls == before);
        return 19;
    }
    assert(!aether_tinfo_directory_probe("/home/.terminfo", &first));
    assert(!aether_tinfo_directory_probe("/home/.terminfo", &second));
    assert(aether_tinfo_directory_same(&first, &second));
    second.epoch++;
    assert(!aether_tinfo_directory_same(&first, &second));
    before = calls;
    assert(aether_tinfo_directory_probe("/home/.terminfo/.", &first) == -1 &&
           errno == ENOENT && calls == before);
    uint64_t args[4] = {0};
    struct aefd_reply metadata;
    assert(!aefd_client_exchange(&boot->context.client, 7, args, NULL, 0,
                                 &metadata) &&
           calls == before);
    aefd_test_filesystem_stdio();
    return 19;
}
void aefd_test_filesystem_direct(void);
void aefd_test_filesystem_direct(void)
{
    errno = ERANGE;
    int fd =
        aether_zsh_open("/home/.terminfo/./v/vt100", O_RDONLY | O_CLOEXEC, 0);
    assert(fd == 3 && errno == ERANGE &&
           aether_zsh_raw_fcntl(fd, F_GETFD, 0) == 1);
    assert(aether_zsh_raw_fcntl(fd, F_DUPFD, 4) == 4 && errno == ERANGE);
    assert(aether_zsh_seek(fd, 0, SEEK_SET) == 0 && errno == ERANGE);
    unsigned char bytes[8] = {0};
    assert(aether_zsh_read(fd, bytes, 4) == 4 && !memcmp(bytes, "TERM", 4) &&
           errno == ERANGE);
    assert(aether_zsh_raw_close(fd) == 0 && aether_zsh_raw_close(4) == 0 &&
           errno == ERANGE);
    assert(aether_zsh_raw_close(fd) == -EBADF && errno == ERANGE);
}
int main(int argc, char **argv)
{
    assert(argc == 2);
    mode = (unsigned)strtoul(argv[1], NULL, 10);
    memcpy(startup, AEFD_STARTUP_MAGIC, 8);
    put(startup, 8, 1);
    put(startup, 12, 336);
    memcpy(startup + 16, "AEFSH001", 8);
    put(startup, 24, 29);
    put(startup, 28, 7);
    put(startup, 32, 1);
    put(startup, 36, 1);
    put(startup, 40, 7);
    put(startup, 44, 1);
    memcpy(startup + 48, AEFD_MAP_MAGIC, 8);
    aefd_put(startup + 48, 1, 31);
    aefd_put(startup + 48, 2, 16);
    for (unsigned i = 0; i < 3; ++i) {
        startup[112 + i * 4] = AEFD_BIND_TERMINAL;
        startup[113 + i * 4] = (unsigned char)i;
        put(startup, 176 + i * 16, 0x7a000001 | i << 16);
        put(startup, 180 + i * 16, i);
        put(startup, 184 + i * 16, i ? 2 : 1);
        put(startup, 188 + i * 16, 16);
    }
    put(startup, 300, AEFD_MODE_CONTROL);
    for (unsigned i = 0; i < 4; ++i)
        put(startup, 304 + i * 4, 1000);
    put(startup, 320, 1);
    if (mode >= 1 && mode <= 32)
        startup[303 + mode] ^= 1;
    if (mode == 40)
        memcpy(startup, "AEFDB007", 8);
    if (mode == 41)
        put(startup, 12, 304);
    if (mode == 42)
        put(startup, 296, 0x76050001);
    if (mode == 43)
        startup[48] ^= 1;
    if (mode == 44)
        put(startup, 184, 2);
    if (mode == 45)
        put(startup, 36, 2);
    assert(__wrap_getuid() == (uid_t)-1 && errno == EAGAIN);
    assert(__wrap_geteuid() == (uid_t)-1 && __wrap_getgid() == (gid_t)-1 &&
           __wrap_getegid() == (gid_t)-1);
    assert(__wrap_main(0, NULL) == -1);
    return 1;
}
