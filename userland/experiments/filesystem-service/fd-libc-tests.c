/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-libc.h"
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>
#ifdef AEFD_CWD_WIRE
int aefd_test_chdir(const char *);
char *aefd_test_getcwd(char *, size_t);
static int allocation_fail;
static size_t allocation_size;
void *aefd_test_malloc(size_t size);
void *aefd_test_malloc(size_t size)
{
    allocation_size = size;
    return allocation_fail ? NULL : malloc(size);
}
#endif
int aefd_test_open(const char *, int, ...);
int aefd_test_open64(const char *, int, ...);
int aefd_test_fcntl(int, int, ...);
int aefd_test_dup(int);
int aefd_test_dup2(int, int);
int aefd_test_pipe(int[2]);
off_t aefd_test_lseek(int, off_t, int);
long aefd_test_io(unsigned long, unsigned long, unsigned long, unsigned long);
#ifdef AEFD_FORK_BINDINGS
#include "fd-fork-stage.h"
void aefd_fork_test_tls_set(uint32_t);
unsigned long aefd_fork_test_auxv(unsigned long);
void aefd_fork_test_park(unsigned long *, unsigned long *, unsigned long *,
                         unsigned long *);
int copy_rebind(unsigned long, unsigned long, unsigned long, unsigned long *,
                unsigned long *);
unsigned long aefd_fork_test_auxv(unsigned long key)
{
    (void)key;
    assert(0);
    return 0;
}
void aefd_fork_test_park(unsigned long *op, unsigned long *memory,
                         unsigned long *input, unsigned long *output)
{
    (void)op;
    (void)memory;
    (void)input;
    (void)output;
    assert(0);
}
int copy_rebind(unsigned long memory, unsigned long input, unsigned long output,
                unsigned long *old_input, unsigned long *old_output)
{
    (void)memory;
    (void)input;
    (void)output;
    (void)old_input;
    (void)old_output;
    assert(0);
    return 0;
}
#endif
struct host {
    struct aefd_startup *boot;
    const char *open_name;
    unsigned char frame[304], request[320], response[4160];
    size_t offset, sent, needed, replied, response_size;
    unsigned blocks, restores, closes, commands, next_selector, last_count;
    int64_t status;
    int drop, wait_result, wait_bad, partial, wrong_replace;
    size_t reply_limit;
#ifdef AEFD_CWD_WIRE
    int bad_cwd;
#endif
};
static struct host *active;
static void put(unsigned char *b, unsigned i, uint32_t v)
{
    for (unsigned j = 0; j < 4; ++j)
        b[i + j] = (unsigned char)(v >> (8 * j));
}
static uint32_t get(const unsigned char *b, unsigned i)
{
    return aether_fs_session_u32(b + i);
}
static void reply(struct host *f)
{
    memset(f->response, 0, sizeof(f->response));
    ++f->commands;
    if (memcmp(f->request, AEFD_MAGIC, 8)) {
        unsigned op = get(f->request, 0), selector = get(f->request, 8);
        unsigned count = get(f->request, 12);
        if (op == 82) {
            assert(get(f->request, 4) == 0x76050001 && get(f->request, 8) == 1);
            put(f->response, 4, 1);
            put(f->response, 8, 0x79000101);
            put(f->response, 12, 0x79000102);
            put(f->response, 16, 3);
            put(f->response, 20, 4);
            put(f->response, 24, 256);
            put(f->response, 28, 16);
            f->response_size = 32;
            return;
        }
        if (op == 68) {
            put(f->response, 0, (uint32_t)f->wait_result);
            if (f->wait_result > 0)
                put(f->response, 4, 0x700);
            if (f->wait_bad)
                f->response[8] = 1;
            f->response_size = 32;
            return;
        }
        assert(op >= 1 && op <= 3 && selector <= 6 && count <= 16);
        uint32_t reference = selector <= 1 ? 101 + selector
                                           : UINT32_C(0x79000100) |
                                                 ((selector - 3) / 2) << 16 |
                                                 ((selector - 3) % 2 + 1);
        assert(get(f->request, 4) == reference);
        if (op == 3)
            assert(!count);
        if (op == 2)
            for (unsigned i = 0; i < count; ++i)
                assert(f->request[16 + i] == 0xcc);
        f->last_count = count;
        put(f->response, 0, op == 3 ? 0 : count);
        if (op == 1)
            memset(f->response + 16, 'r', count);
        f->response_size = 32;
    } else {
        unsigned op = (unsigned)aefd_word(f->request, 1);
        assert(aefd_word(f->request, 2) == 31 && aefd_word(f->request, 3));
#ifdef AEFD_CWD_WIRE
        assert(op >= 1 && op <= 9);
#elif defined(AEFD_DUP2_WIRE)
        assert(op >= 1 && op <= 7);
#else
        assert(op >= 1 && op <= 6);
#endif
        memcpy(f->response, AEFD_MAGIC, 8);
        aefd_put(f->response, 1, (uint64_t)f->status);
        aefd_put(f->response, 2, 31);
        aefd_put(f->response, 3, aefd_word(f->request, 3));
        f->response_size = 64;
        if (f->status)
            return;
        uint64_t value = 0;
        if (op == 1 || op == 4) {
            value = f->next_selector++;
            if (op == 1) {
                const char *name = f->open_name ? f->open_name : "item";
                assert(aefd_word(f->request, 4) <= 1 &&
                       aefd_word(f->request, 5) == strlen(name));
                assert(!memcmp(f->request + 64, name, strlen(name)));
            }
        } else if (op == 2) {
            value = aefd_word(f->request, 5);
            assert(value <= 4096);
            f->last_count = (unsigned)value;
            aefd_put(f->response, 5, value);
            memset(f->response + 64, 'f', (size_t)value);
            f->response_size += ((size_t)value + 63U) / 64U * 64U;
#ifdef AEFD_CWD_WIRE
        } else if (op == 9) {
            value = 13;
            aefd_put(f->response, 5, value);
            memcpy(f->response + 64, "/work/nested", 13);
            f->response_size += 64;
            if (f->bad_cwd == 1)
                f->response[77] = 1;
            if (f->bad_cwd == 2)
                f->response[64] = 'x';
            if (f->bad_cwd == 3)
                aefd_put(f->response, 4, 257);
#endif
        } else if (op == 7) {
            value = aefd_word(f->request, 5) ^ (uint64_t)f->wrong_replace;
        } else if (op == 3) {
            value = 2;
        }
        aefd_put(f->response, 4, value);
#ifdef AEFD_CWD_WIRE
        if (op == 9 && f->bad_cwd == 3)
            aefd_put(f->response, 4, 257);
#endif
    }
}
static int64_t native(void *owner, uint64_t op, uint64_t cap, uint64_t a,
                      uint64_t b, uint64_t c)
{
    struct host *f = owner;
    errno =
        EDOM; /* Actual wrapper must restore caller errno after callbacks. */
    if (op == 0x1000e) {
        assert(a && c == 8);
        if (!cap) {
            assert(b && *(uint64_t *)(uintptr_t)a == UINT64_MAX);
            *(uint64_t *)(uintptr_t)b = 0x1234;
            ++f->blocks;
        } else {
            assert(cap == 2 && !b && *(uint64_t *)(uintptr_t)a == 0x1234);
            ++f->restores;
        }
        return 0;
    }
    if (op == 0x10027 || op == 0x1006e) {
        assert(!cap && !a && !b && !c);
        return op == 0x10027 ? 9 : 7;
    }
    if (op == 0x24003) {
        assert(cap == (f->closes ? 72U : 71U) && !a && !b && !c);
        ++f->closes;
        return 0;
    }
    assert(!c && a && b && b <= 16 && f->blocks == f->restores + 1);
    if (f->boot->phase == 1) {
        assert(op == 0x24001 && cap == 71 && f->offset + b <= 304);
        memcpy((void *)(uintptr_t)a, f->frame + f->offset, (size_t)b);
        f->offset += (size_t)b;
        return (int64_t)b;
    }
    assert(f->boot->phase == 2);
    if (op == 0x24002) {
        assert(cap == 72 && f->sent + b <= sizeof(f->request));
        memcpy(f->request + f->sent, (void *)(uintptr_t)a, (size_t)b);
        f->sent += (size_t)b;
        if (f->sent == 16)
            f->needed = memcmp(f->request, AEFD_MAGIC, 8) ? 32 : 64;
        if (f->sent == 64 && !memcmp(f->request, AEFD_MAGIC, 8) &&
            (aefd_word(f->request, 1) == 1
#ifdef AEFD_CWD_WIRE
             || aefd_word(f->request, 1) == 8
#endif
             ))
            f->needed += ((size_t)aefd_word(f->request, 5) + 63U) / 64U * 64U;
        if (f->sent == f->needed)
            reply(f);
        return (int64_t)b;
    }
    assert(op == 0x24001 && cap == 71 && f->sent == f->needed);
    if (f->drop)
        return 0;
    size_t limit = f->partial && f->reply_limit < f->response_size
                       ? f->reply_limit
                       : f->response_size;
    size_t chunk = (size_t)b;
    if (chunk > limit - f->replied)
        chunk = limit - f->replied;
    if (!chunk)
        return 0;
    memcpy((void *)(uintptr_t)a, f->response + f->replied, chunk);
    f->replied += chunk;
    if (f->replied == f->response_size) {
        f->sent = f->needed = f->replied = f->response_size = 0;
        memset(f->request, 0, sizeof(f->request));
    }
    return (int64_t)chunk;
}
/* Host definition substitutes only the target auxv/int81 entry, not the actual
 * startup consumer/context/libc bindings. Fresh process per scenario. */
int64_t aefd_startup_native(struct aefd_startup *boot)
{
    active->boot = boot;
    return aefd_startup_start(boot, native, active,
                              (struct aefd_startup_auxv){0x40000102, 71, 72});
}
_Noreturn void __real__exit(int);
_Noreturn void __real__exit(int status)
{
    assert(active->closes == 2);
    _exit(status);
}
static void scenario(unsigned which)
{
    struct host f = {0};
    active = &f;
    f.next_selector = AEFD_FIRST_FILE;
    memcpy(f.frame, AEFD_STARTUP_MAGIC, 8);
    put(f.frame, 8, 1);
    put(f.frame, 12, 304);
    memcpy(f.frame + 16, "AEFSH001", 8);
    put(f.frame, 24, 29);
    put(f.frame, 28, 7);
    put(f.frame, 32, 1);
    put(f.frame, 36, 1);
    put(f.frame, 40, 7);
    put(f.frame, 44, 1);
    memcpy(f.frame + 48, AEFD_MAP_MAGIC, 8);
    aefd_put(f.frame + 48, 1, 31);
    aefd_put(f.frame + 48, 2, 16);
    for (unsigned i = 0; i < 2; ++i) {
        f.frame[112 + i * 4] = AEFD_BIND_CONSOLE;
        f.frame[113 + i * 4] = (unsigned char)i;
        put(f.frame, 176 + i * 16, 101 + i);
        put(f.frame, 180 + i * 16, i);
        put(f.frame, 184 + i * 16, i ? 2 : 1);
        put(f.frame, 188 + i * 16, 16);
    }
    put(f.frame, 296, 0x76050001);
    unsigned char buffer[8192];
    memset(buffer, 0xcc, sizeof(buffer));
    errno = EALREADY;
    assert(aefd_test_io(0, 0, (unsigned long)(uintptr_t)buffer, 1) == -5 &&
           errno == EALREADY);
    assert(aefd_shell_role() == -EIO);
#ifdef AEFD_FORK_BINDINGS
    if (!which) {
        assert(aefd_fork_tls_valid());
        aefd_fork_test_tls_set(0);
        assert(aefd_shell_start() == -EIO && errno == EALREADY);
        assert(!f.boot && !f.offset && !f.closes && !f.commands);
        /* Test-only fixture restoration, never production admission repair. */
        aefd_fork_test_tls_set(UINT32_C(0x73657373));
    }
#endif
    assert(!aefd_shell_start() && errno == EALREADY && aefd_shell_role() == 1);
    assert(aefd_shell_start() == -16 && f.offset == 304);
    unsigned before = f.commands;
    switch (which) {
    case 0:
        assert(aefd_test_io(1, 1, (unsigned long)(uintptr_t)buffer,
                            UINT64_MAX) == 16);
        assert(f.last_count == 16 && errno == EALREADY);
        break;
    case 1:
        assert(aefd_test_io(0, 0, (unsigned long)(uintptr_t)buffer,
                            sizeof(buffer)) == 16);
        assert(buffer[0] == 'r' && buffer[15] == 'r' && buffer[16] == 0xcc &&
               errno == EALREADY);
        break;
    case 2:
    case 3: {
        int fd = which == 2 ? aefd_test_open("item", O_RDONLY | O_CLOEXEC)
                            : aefd_test_open64("item", O_RDONLY);
        assert(fd == 2 && errno == EALREADY);
        assert(aefd_test_fcntl(fd, F_GETFD) == (which == 2 ? 1 : 0));
        assert(aefd_test_io(0, (unsigned long)fd,
                            (unsigned long)(uintptr_t)buffer,
                            UINT64_MAX) == 4096);
        assert(f.last_count == 4096 && buffer[4095] == 'f' &&
               buffer[4096] == 0xcc && errno == EALREADY);
        assert(aefd_test_lseek(fd, -1, SEEK_CUR) == 2 && errno == EALREADY);
        assert(aefd_test_fcntl(fd, F_SETFD, 0) == 0);
        assert(aefd_test_fcntl(fd, F_DUPFD_CLOEXEC, 5) == 5);
        assert(aefd_test_fcntl(5, F_GETFD) == 1);
        assert(aefd_test_io(3, (unsigned long)fd, 0, 0) == 0);
        break;
    }
    case 4: {
        assert(aefd_test_fcntl(1, F_DUPFD_CLOEXEC, 3) == 3);
        assert(aefd_test_fcntl(3, F_GETFD) == 1 &&
               !aefd_test_fcntl(3, F_SETFD, 0));
        assert(aefd_test_dup(3) == 2);
        assert(!aefd_test_io(3, 1, 0, 0) && !aefd_test_io(3, 3, 0, 0) &&
               f.commands == before);
        assert(!aefd_test_io(3, 2, 0, 0) && f.commands == before + 1);
        break;
    }
    case 5:
        assert(aefd_test_open(NULL, O_RDONLY) == -1 && errno == EFAULT);
        break;
    case 6:
        assert(aefd_test_open("item", O_WRONLY) == -1 && errno == EOPNOTSUPP);
        break;
    case 7:
        assert(aefd_test_open("item", O_CREAT | O_RDONLY, 0600) == -1 &&
               errno == EOPNOTSUPP);
        break;
    case 8:
#ifdef AEFD_PATH_WIRE
        f.open_name = "/item";
        assert(aefd_test_open("/item", O_RDONLY) == 2);
#else
        assert(aefd_test_open("/item", O_RDONLY) == -1 && errno == EOPNOTSUPP);
#endif
        break;
    case 9:
#ifdef AEFD_PATH_WIRE
        f.open_name = "a/item";
        assert(aefd_test_open("a/item", O_RDONLY) == 2);
#else
        assert(aefd_test_open("a/item", O_RDONLY) == -1 && errno == EOPNOTSUPP);
#endif
        break;
    case 10:
        assert(aefd_test_open("", O_RDONLY) == -1 && errno == EINVAL);
        break;
    case 11:
#ifdef AEFD_CWD_WIRE
        f.open_name = ".";
        f.status = -EISDIR;
        assert(aefd_test_open(".", O_RDONLY) == -1 && errno == EISDIR);
#else
        assert(aefd_test_open(".", O_RDONLY) == -1 && errno == EINVAL);
#endif
        break;
    case 12:
#ifdef AEFD_CWD_WIRE
        f.open_name = "..";
        f.status = -EISDIR;
        assert(aefd_test_open("..", O_RDONLY) == -1 && errno == EISDIR);
#else
        assert(aefd_test_open("..", O_RDONLY) == -1 && errno == EINVAL);
#endif
        break;
    case 13: {
        char path[257];
        memset(path, 'x', 256);
        path[256] = 0;
        assert(aefd_test_open(path, O_RDONLY) == -1 && errno == ENAMETOOLONG);
        break;
    }
    case 14:
        assert(aefd_test_fcntl(1, F_GETFL) == -1 && errno == EOPNOTSUPP);
        break;
    case 15:
        assert(aefd_test_fcntl(1, F_SETFD, 2) == -1 && errno == EINVAL);
        break;
    case 16:
        assert(aefd_test_fcntl(1, F_DUPFD, 16) == -1 && errno == EINVAL);
        break;
    case 17:
        assert(aefd_test_fcntl(16, F_GETFD) == -1 && errno == EBADF);
        break;
    case 18:
#ifdef AEFD_DUP2_WIRE
        assert(aefd_test_dup2(1, 0) == 0 && errno == EALREADY);
#else
        assert(aefd_test_dup2(1, 0) == -1 && errno == EOPNOTSUPP);
#endif
        break;
    case 19:
#ifdef AEFD_DUP2_WIRE
        assert(aefd_test_dup2(1, 1) == 1 && errno == EALREADY);
#else
        assert(aefd_test_dup2(1, 1) == -1 && errno == EOPNOTSUPP);
#endif
        break;
    case 20:
        assert(aefd_test_pipe(NULL) == -1 && errno == EFAULT);
        break;
    case 21:
        assert(aefd_test_lseek(1, 0, SEEK_SET) == -1 && errno == ESPIPE);
        break;
    case 22:
        assert(aefd_test_lseek(1, 0, -1) == -1 && errno == EINVAL);
        break;
    case 23:
        assert(aefd_test_io(8, 0, 0, 0) == -ENOSYS && errno == EALREADY);
        break;
    case 24:
        assert(aefd_test_io(0, UINT64_MAX, (unsigned long)(uintptr_t)buffer,
                            1) == -EBADF &&
               errno == EALREADY);
        break;
    case 25:
        assert(aefd_test_io(0, 0, 0, 1) == -EFAULT && errno == EALREADY);
        break;
    case 26:
        assert(aefd_test_io(1, 1, 0, 1) == -EFAULT && errno == EALREADY);
        break;
    case 27: {
        assert(aefd_test_open("item", O_RDONLY) == 2);
        f.status = -5000;
        assert(aefd_test_lseek(2, 0, SEEK_SET) == -1 && errno == EIO);
        errno = EALREADY;
        assert(aefd_test_io(0, 2, (unsigned long)(uintptr_t)buffer, 1) ==
                   -EIO &&
               errno == EALREADY);
        f.status = 0;
        break;
    }
    case 28: {
        f.drop = 1;
        assert(aefd_test_io(1, 1, (unsigned long)(uintptr_t)buffer, 5) ==
                   -EIO &&
               errno == EALREADY);
        assert(f.commands == before + 1 && f.closes == 2);
        assert(aefd_test_io(1, 1, (unsigned long)(uintptr_t)buffer, 5) ==
                   -EIO &&
               f.commands == before + 1);
        break;
    }
    case 29: {
        assert(!aefd_shell_snapshot(buffer, 128, 0) && errno == EALREADY);
        assert(!memcmp(buffer, AEFD_MAP_MAGIC, 8) &&
               buffer[112 - 48] == AEFD_BIND_CONSOLE);
        struct aefd_redirect_result r = aefd_shell_redirect(1, 3);
        assert(r.status == 3 && r.committed && !r.unknown &&
               errno == EALREADY && f.commands == before);
        break;
    }
    case 30:
    case 31:
    case 32:
    case 33:
    case 34:
    case 35:
    case 36:
    case 37:
    case 38:
    case 39:
    case 40: {
        int status = 0x12345678;
        f.wait_result = which == 32 || which == 37 ? 0
                        : which == 33              ? -ECHILD
                        : which == 34              ? 9
                                                   : 10;
        f.wait_bad = which == 36;
        f.drop = which == 40;
        long result = __aether_waitpid(which == 31   ? 10
                                       : which == 35 ? 11
                                                     : -1,
                                       which == 39 ? NULL : &status,
                                       which == 32   ? WNOHANG
                                       : which == 38 ? 2
                                                     : 0);
        long expected = which == 38 ? -EINVAL
                        : which == 34 || which == 35 || which == 36 ||
                                which == 37 || which == 40
                            ? -EIO
                            : f.wait_result;
        assert(result == expected && errno == EALREADY);
        assert(status == (result > 0 && which != 39 ? 0x700 : 0x12345678));
        break;
    }
    case 41:
        __wrap__exit(23);
    case 42:
        f.drop = 1;
        assert(aefd_test_io(1, 1, (unsigned long)(uintptr_t)buffer, 5) == -EIO);
        __wrap__exit(0);
    case 75: {
        assert(!aefd_native_enter(&f.boot->context.native));
        f.boot->context.native.retired = 1;
        errno = EALREADY;
        int status = 0x1234;
        assert(__aether_waitpid(-1, &status, 0) == -EBUSY && status == 0x1234 &&
               errno == EALREADY && !f.closes);
        f.boot->context.native.retired = 0;
        aefd_native_leave(&f.boot->context.native);
        break;
    }
    case 76: {
        int pair[2] = {-99, -98};
        assert(!aefd_test_pipe(pair) && pair[0] == 2 && pair[1] == 3 &&
               errno == EALREADY);
        assert(!aefd_test_fcntl(pair[0], F_GETFD) &&
               !aefd_test_fcntl(pair[1], F_GETFD));
        assert(aefd_test_io(0, (unsigned long)pair[0],
                            (unsigned long)(uintptr_t)buffer, 32) == 16);
        memset(buffer, 0xcc, 16);
        assert(aefd_test_io(1, (unsigned long)pair[1],
                            (unsigned long)(uintptr_t)buffer, 32) == 16 &&
               errno == EALREADY);
        break;
    }
    case 77:
        assert(aefd_test_open("item", O_RDONLY) == 2);
        assert(aefd_test_io(1, 2, (unsigned long)(uintptr_t)buffer, 32) ==
                   -EROFS &&
               errno == EALREADY && f.commands == before + 1);
        break;
#ifdef AEFD_DUP2_WIRE
    case 78:
        assert(aefd_test_open("item", O_RDONLY | O_CLOEXEC) == 2);
        assert(aefd_test_open("item", O_RDONLY | O_CLOEXEC) == 3);
        assert(aefd_test_dup2(2, 3) == 3 && errno == EALREADY);
        assert(aefd_test_fcntl(3, F_GETFD) == 0);
        assert(aefd_test_fcntl(2, F_GETFD) == 1);
        break;
    case 79:
        assert(aefd_test_open("item", O_RDONLY | O_CLOEXEC) == 2);
        assert(aefd_test_dup2(2, 0) == 0 && errno == EALREADY);
        assert(!aefd_shell_snapshot(buffer, 128, 0));
        assert(buffer[64] == AEFD_BIND_FILE && buffer[65] == 1 && !buffer[66]);
        break;
    case 80:
        assert(aefd_test_open("item", O_RDONLY | O_CLOEXEC) == 2);
        assert(aefd_test_dup2(1, 2) == 2 && errno == EALREADY);
        assert(aefd_test_fcntl(2, F_GETFD) == 0);
        break;
    case 81:
        assert(aefd_test_dup2(-1, 0) == -1 && errno == EBADF);
        errno = EALREADY;
        assert(aefd_test_open("item", O_RDONLY | O_CLOEXEC) == 2);
        assert(aefd_test_dup2(2, 2) == 2 && errno == EALREADY);
        assert(aefd_test_fcntl(2, F_GETFD) == 1);
        break;
    case 82:
    case 83:
        assert(aefd_test_open("item", O_RDONLY) == 2);
        assert(aefd_test_open("item", O_RDONLY) == 3);
        if (which == 82)
            f.drop = 1;
        else
            f.wrong_replace = 1;
        (void)aefd_test_dup2(2, 3);
        assert(0 && "uncertain replacement must not return");
        break;
#endif
#ifdef AEFD_CWD_WIRE
    case 84:
        assert(aefd_test_chdir("/work/../work") == 0 && errno == EALREADY);
        break;
    case 85:
        assert(aefd_test_getcwd((char *)buffer, sizeof(buffer)) ==
               (char *)buffer);
        assert(!strcmp((char *)buffer, "/work/nested") && buffer[13] == 0xcc &&
               errno == EALREADY);
        break;
    case 86:
    case 87: {
        char *path = aefd_test_getcwd(NULL, which == 86 ? 0 : 32);
        assert(path && !strcmp(path, "/work/nested") &&
               allocation_size == (which == 86 ? 13U : 32U) &&
               errno == EALREADY);
        free(path);
        break;
    }
    case 88:
        assert(!aefd_test_getcwd((char *)buffer, 4) && errno == ERANGE &&
               buffer[0] == 0xcc);
        break;
    case 89:
        assert(!aefd_test_getcwd((char *)buffer, 0) && errno == EINVAL &&
               f.commands == before);
        break;
    case 90:
        allocation_fail = 1;
        assert(!aefd_test_getcwd(NULL, 0) && errno == ENOMEM);
        break;
    case 91:
        assert(aefd_test_chdir(NULL) == -1 && errno == EFAULT &&
               f.commands == before);
        break;
    case 92:
        assert(aefd_test_chdir("") == -1 && errno == ENOENT &&
               f.commands == before);
        break;
    case 93:
        memset(buffer, 'x', 256);
        buffer[256] = 0;
        assert(aefd_test_chdir((char *)buffer) == -1 && errno == ENAMETOOLONG &&
               f.commands == before);
        break;
    case 94:
        f.status = -ENOENT;
        assert(aefd_test_chdir("missing") == -1 && errno == ENOENT);
        break;
    case 95:
        f.status = -ENOENT;
        assert(!aefd_test_getcwd((char *)buffer, sizeof(buffer)) &&
               errno == ENOENT && buffer[0] == 0xcc);
        break;
    case 96:
    case 97:
    case 98:
        f.bad_cwd = (int)which - 95;
        (void)aefd_test_getcwd((char *)buffer, sizeof(buffer));
        assert(0 && "malformed cwd must exit");
        break;
    case 99:
    case 100:
    case 101:
    case 102:
        f.partial = 1;
        f.reply_limit = which == 99    ? 0
                        : which == 100 ? 63
                        : which == 101 ? 64
                                       : 127;
        (void)aefd_test_getcwd((char *)buffer, sizeof(buffer));
        assert(0 && "partial cwd must exit");
        break;
    case 103:
        f.drop = 1;
        (void)aefd_test_chdir("work");
        assert(0 && "unknown chdir must exit");
        break;
#endif
    default: {
        assert(which >= 43 && which <= 74);
        f.wait_result = 10;
        f.partial = 1;
        f.reply_limit = which - 43;
        int status = 0x1234;
        assert(__aether_waitpid(-1, &status, 0) == -EIO && status == 0x1234 &&
               errno == EALREADY && f.closes == 2);
        unsigned commands = f.commands;
        assert(__aether_waitpid(-1, &status, 0) == -EIO &&
               f.commands == commands && status == 0x1234);
        break;
    }
    }
#ifdef AEFD_PATH_WIRE
    if (which == 8 || which == 9
#ifdef AEFD_CWD_WIRE
        || which == 11 || which == 12
#endif
#ifdef AEFD_DUP2_WIRE
        || which == 18
#endif
    )
        assert(f.commands == before + 1);
    else
#endif
        if (which >= 5 && which <= 26)
        assert(f.commands == before);
    struct aefd_finish r;
    errno = EALREADY;
    assert(!aefd_shell_finish(&r) && errno == EALREADY && f.closes == 2);
    assert(r.unknown == (which == 28 || which == 34 || which == 35 ||
                         which == 36 || which == 37 || which == 40 ||
                         (which >= 43 && which <= 74)));
    unsigned commands = f.commands, blocks = f.blocks;
    assert(!aefd_shell_finish(&r) && f.commands == commands &&
           f.blocks == blocks);
    assert(aefd_test_fcntl(0, F_GETFD) == -1 && errno == EIO);
    assert(f.blocks == f.restores);
}
int main(void)
{
#ifdef AEFD_CWD_WIRE
    const unsigned count = 104;
#elif defined(AEFD_DUP2_WIRE)
    const unsigned count = 84;
#else
    const unsigned count = 78;
#endif
    for (unsigned i = 0; i < count; ++i) {
        pid_t child = fork();
        assert(child >= 0);
        if (!child) {
            scenario(i);
            _exit(0);
        }
        int status;
        assert(waitpid(child, &status, 0) == child && WIFEXITED(status) &&
               WEXITSTATUS(status) ==
                   (i == 41                                      ? 23
                    : (i == 42 || i == 82 || i == 83 || i >= 96) ? 141
                                                                 : 0));
    }
    printf("%u actual libc binding host scenarios pass\n", count);
    return 0;
}
