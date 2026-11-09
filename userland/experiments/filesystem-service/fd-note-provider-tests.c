/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual provider and scoped musl fopen/stdio_write bodies. Context native
 * calls and fdopen allocation are explicit doubles, never host path IO. */
#define _POSIX_C_SOURCE 200809L
#include "fd-libc.h"
#include "fd-zsh-external.h"
#include "fd-fork-stage.h"
#include "stdio_impl.h"
#include <errno.h>
#include <stdlib.h>
#include <signal.h>
#define AEFD_NOTE_PROVIDER_TEST
#define main context_cases
#include "fd-note-context-tests.c"
#undef main
int aefd_test_open(const char *, int, ...);
int aefd_test_open64(const char *, int, ...);
int aefd_test_dup2(int, int);
mode_t aefd_test_umask(mode_t);
FILE *aefd_test_fopen(const char *, const char *);
FILE *aefd_test_fdopen(int, const char *);
size_t aefd_test_stdio_write(FILE *, const unsigned char *, size_t);
int aefd_test_sigaction(int, const struct sigaction *, struct sigaction *);
#if !defined(AEFD_ZSH_HOME_CWD_BINDINGS) ||                                  \
    defined(AEFD_ZSH_OPERATOR_NOTE_BINDINGS)
static FILE stream;
static unsigned char stdio_buffer[32];
#endif
FILE *aefd_test_fdopen(int fd, const char *mode)
{
    (void)fd;
    (void)mode;
    /* The actual current fopen wx adds forbidden TRUNC. No allocation may
     * occur when the selected provider rejects that request before effects. */
    abort();
}
int64_t aefd_startup_native(struct aefd_startup *s)
{
    assert(s == aefd_shell_external_startup());
    setup(0);
    s->phase = 2;
    return 0;
}
int __real_main(int n, char **v)
{
    (void)n;
    (void)v;
    abort();
}
_Noreturn void __real__Exit(int status) { _Exit(status); }
int aefd_test_sigaction(int sig, const struct sigaction *a, struct sigaction *b)
{
    (void)sig;
    (void)a;
    (void)b;
    abort();
}
_Noreturn void __assert_fail(const char *expression, const char *file, int line,
                             const char *function)
{
    printf("assertion %s at %s:%d (%s)\n", expression, file, line, function);
    fflush(NULL);
    _Exit(99);
}
#ifdef AEFD_ZSH_OPERATOR_NOTE_BINDINGS
static void operator_setup(int mode)
{
    setup(mode);
    aefd_shell_external_startup()->identity.slot = 1;
    for (size_t i = 0; i < sizeof(f.note_bytes); ++i)
        f.note_bytes[i] = (unsigned char)('a' + i % 26);
}
static void operator_write(size_t length, size_t buffered)
{
    operator_setup(0);
    f.note_length = length;
    const char *note = AEFD_NOTE_CREATE_PATH;
    int flags = O_WRONLY | O_CREAT | O_EXCL | O_NOCTTY;
    f.create_errno = ENOSPC;
    assert(aefd_test_open(note, flags, 0666) == -1 && errno == ENOSPC);
    assert(c.client.live && f.requests == 1);
    f.create_errno = 0;
    errno = EDOM;
    int fd = aefd_test_open(note, flags, 0666);
    assert(fd == 3 && errno == EDOM && c.note_create.remote.txg == 91);
    assert(aether_zsh_raw_fcntl(1, F_DUPFD, 10) == 10);
    assert(aefd_test_dup2(fd, 1) == 1 && c.map.slots[1].selector == 4);
    assert(!aether_zsh_raw_close(fd));

    unsigned before = f.requests;
    struct iovec oversize[2] = {{f.note_bytes, sizeof(f.note_bytes)},
                               {f.note_bytes, 1}};
    assert(aether_zsh_vector_write(1, oversize, 2) == -1 && errno == EINVAL);
    assert(f.requests == before && c.client.live && !f.note_writes);
    struct iovec overlap = {&c, 1};
    assert(aether_zsh_vector_write(1, &overlap, 1) == -1 && errno == EFAULT);
    assert(f.requests == before);

    f.write_errno = ENOSPC;
    const struct iovec vector = {f.note_bytes, length};
    assert(aether_zsh_vector_write(1, &vector, 1) == -1 && errno == ENOSPC);
    assert(c.client.live && f.note_writes == 1);
    f.write_errno = 0;
    memset(&stream, 0, sizeof(stream));
    stream.fd = 1;
    stream.buf = stdio_buffer;
    stream.buf_size = sizeof(stdio_buffer);
    memcpy(stdio_buffer, f.note_bytes, buffered);
    stream.wbase = stdio_buffer;
    stream.wpos = stdio_buffer + buffered;
    errno = EDOM;
    assert(aefd_test_stdio_write(&stream, f.note_bytes + buffered,
                                  length - buffered) == length - buffered);
    assert(errno == EDOM && c.note_write.remote.count == length &&
           c.note_write.remote.staged == length && c.note_write.remote.txg == 92);
    assert(f.note_writes == 2 && f.requests == before + 2);
    assert(aefd_test_dup2(10, 1) == 1 && !c.note_writers);
    assert(!aether_zsh_raw_close(10));
    assert(aether_zsh_vector_write(1, oversize, 2) == 16);
    assert(f.terminal_writes == 1 && f.note_writes == 2);
    close_client();
}
static void operator_note_cases(void)
{
    operator_setup(0);
    const char *note = AEFD_NOTE_CREATE_PATH;
    int flags = O_WRONLY | O_CREAT | O_EXCL | O_NOCTTY;
    assert(aefd_test_open("note", flags, 0666) == -1 && errno == EACCES);
    assert(aefd_test_open(AEFD_HOME_PROFILE_PATH, flags, 0666) == -1 &&
           errno == EOPNOTSUPP);
    assert(aefd_test_open(note, flags | O_TRUNC, 0666) == -1 &&
           errno == EOPNOTSUPP);
    assert(aefd_test_open(note, O_WRONLY | O_NOCTTY, 0) == -1 &&
           errno == EOPNOTSUPP);
    assert(aefd_test_open(note, flags, 0444) == -1 && errno == EOPNOTSUPP);
    aefd_shell_external_startup()->identity.slot = 2;
    assert(aefd_test_open(note, flags, 0666) == -1 && errno == EACCES);
    assert(aefd_test_open(note, O_RDONLY, 0) == -1 && errno == EACCES);
    assert(!f.requests);
    aefd_shell_external_startup()->identity.slot = 1;
    f.create_errno = EEXIST;
    assert(aefd_test_open(note, flags, 0666) == -1 && errno == EEXIST);
    assert(c.client.live && !f.closes && c.note_create.remote.flags == 0);
    int read_fd = aefd_test_open(note, O_RDONLY, 0);
    assert(read_fd == 3 && !aether_zsh_raw_close(read_fd));
    assert(f.requests == 3 && c.client.live);
    close_client();

    operator_write(1, 0);
    operator_write(AEFD_NOTE_WRITE_MAX, 7);

    operator_setup(30);
    f.note_length = 1;
    int fd = aefd_test_open(note, flags, 0666);
    assert(fd == 3 && aefd_test_dup2(fd, 1) == 1);
    const struct iovec single = {f.note_bytes, 1};
    assert(aether_zsh_vector_write(1, &single, 1) == -1 && errno == EIO);
    assert(f.note_writes == 1 && !c.client.live && f.closes == 2);
    puts("operator note flags, preflight, 1/256-byte stdio, bounds and receipts pass");
}
#endif
int main(void)
{
    assert(!aefd_zsh_admit());
#ifdef AEFD_ZSH_OPERATOR_NOTE_BINDINGS
    operator_note_cases();
    return 0;
#elif defined(AEFD_ZSH_HOME_CWD_BINDINGS)
    setup(0);
    f.cwd = 1;
    char out[8];
    memset(out, 99, sizeof out);
    errno = EDOM;
    assert(__wrap_getcwd(out, sizeof out) == out &&
           !strcmp(out, "/home") && errno == EDOM && out[6] == 99);
#ifndef AEFD_CWD_PREIMPLEMENT_TEST
    setup(0);
    assert(!memcmp(AEFD_MAGIC, "AEFP0007", 8));
    uint64_t args[4] = {0};
    struct aefd_reply reply;
    assert(!aefd_client_exchange(&c.client, 7, args, NULL, 0, &reply));
    args[1] = 5;
    args[3] = 1;
    assert(!aefd_client_exchange(&c.client, 13, args,
                                 (const unsigned char *)"/home", 5, &reply));
    assert(!f.requests && c.client.live);
    unsigned before = f.requests;
    errno = EDOM;
    assert(__wrap_chdir("/home") == 0 && errno == EDOM && f.cwd == 1);
    assert(f.requests == before + 1 && f.mask == 0x1234);
    assert(__wrap_getcwd(out, sizeof out) == out && !strcmp(out, "/home"));
    memset(out, 99, sizeof out);
    before = f.requests;
    errno = 0;
    assert(!__wrap_getcwd(out, 2) && errno == ERANGE && out[0] == 99);
    assert(c.client.live && f.requests == before + 1);
    assert(!__wrap_getcwd(out, 0) && errno == EINVAL);
    assert(!__wrap_getcwd((char *)&c, sizeof out) && errno == EFAULT);
    assert(f.requests == before + 1);
    errno = EDOM;
    char *allocated = __wrap_getcwd(NULL, 0);
    assert(allocated && !strcmp(allocated, "/home") && errno == EDOM);
    free(allocated);
    allocated = __wrap_getcwd(NULL, 12);
    assert(allocated && !strcmp(allocated, "/home"));
    free(allocated);
    before = f.requests;
    for (unsigned i = 0; i < 5; i++) {
        static const char *const denied[] = {"", ".", "..", "/home/", "/else"};
        assert(__wrap_chdir(denied[i]) == -1 && errno == EACCES);
    }
    assert(__wrap_chdir(NULL) == -1 && errno == EFAULT);
    assert(__wrap_chdir((char *)&c) == -1 && errno == EFAULT);
    assert(f.requests == before);
    c.native.active = 1;
    assert(__wrap_chdir("/") == -1 && errno == EBUSY && f.cwd == 1);
    c.native.active = 0;
    f.mode = 24;
    assert(__wrap_chdir("/") == -1 && errno == EACCES && f.cwd == 1);
    assert(c.client.live);
    f.mode = 0;
    assert(aether_zsh_open(".zprofile", O_RDONLY, 0) == 3);
    assert(!aether_zsh_raw_close(3));
    before = f.requests;
    assert(aether_zsh_open(".zprofile", O_WRONLY | O_CREAT | O_EXCL, 0600) == -1 &&
           errno == EOPNOTSUPP && f.requests == before);
    assert(__wrap_chdir("/") == 0 && f.cwd == 0);
    assert(__wrap_getcwd(out, sizeof out) == out && !strcmp(out, "/"));
    assert(aether_zsh_open(".zprofile", O_RDONLY, 0) == -1 && errno == EACCES);
    assert(c.client.live && f.cwd == 0);
    close_client();
    for (int mode = 20; mode <= 22; mode++) {
        setup(mode);
        f.cwd = 1;
        memset(out, 99, sizeof out);
        assert(!__wrap_getcwd(out, sizeof out) && errno == EIO && out[0] == 99);
        assert(!c.client.live && f.closes == 2 && f.mask == 0x1234);
        before = f.requests;
        assert(__wrap_chdir("/") == -1 && f.requests == before);
    }
    setup(29);
    memset(out, 99, sizeof out);
    assert(!__wrap_getcwd(out, sizeof out) && errno == EIO && out[0] == 99);
    assert(!c.client.live && f.closes == 2);
    setup(23);
    memset(out, 99, sizeof out);
    assert(!__wrap_getcwd(out, sizeof out) && errno == EACCES && out[0] == 99);
    assert(c.client.live);
    close_client();
    for (int mode = 25; mode <= 28; mode++) {
        setup(mode);
        assert(__wrap_chdir("/home") == -1 && errno == EIO);
        assert(f.cwd == 1 && !c.client.live && f.closes == 2);
        before = f.requests;
        assert(__wrap_chdir("/home") == -1 && f.requests == before);
    }
    setup(0);
    c.map.generation = 0;
    assert(__wrap_chdir("/home") == -1 && errno == EIO && !f.requests);
    assert(!c.client.live && f.closes == 2);
    setup(0);
    c.map.generation = 0;
    assert(!__wrap_getcwd(out, sizeof out) && errno == EIO && !f.requests);
    assert(!c.client.live && f.closes == 2);
#endif
    puts("home CWD actual wrapper/context/codec paths pass");
    return 0;
#else
#ifdef AEFD_ZSH_LOGIN_STARTUP_BINDINGS
    /* Neither the previous profile nor unrelated RC discovery gains authority. */
    for (unsigned i = 0; i < 4; i++) {
        static const char *const denied[] = {"/home/note", "/home/.zshrc",
                                             "/etc/zshenv", "/home/.zprofile.zwc"};
        errno = 0;
        assert(aether_zsh_open(denied[i], O_RDONLY, 0) == -1 && errno == EACCES);
        assert(!f.requests);
    }
#endif
    assert(aefd_test_umask(01777) == 0077);
    assert(aefd_test_umask(0077) == 0777);
    assert(aefd_test_umask(0077) == 0077);
    for (int route = 0; route < 3; route++) {
        setup(0);
        errno = ERANGE;
        assert(aether_zsh_open(AEFD_HOME_PROFILE_PATH, O_WRONLY | O_CREAT | O_EXCL,
                               0444) == -1 &&
               errno == EOPNOTSUPP);
        assert(!f.requests);
        errno = ERANGE;
        int fd;
        if (route == 0)
            fd = aefd_test_open(AEFD_HOME_PROFILE_PATH,
                                O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0666);
        else if (route == 1)
            fd = aefd_test_open64(
                AEFD_HOME_PROFILE_PATH, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0666);
        else
            fd = aether_zsh_open(
                AEFD_HOME_PROFILE_PATH,
                O_WRONLY | O_CREAT | O_EXCL | O_NOCTTY | O_CLOEXEC, 0666);
        assert(fd == 3 && errno == ERANGE && c.note_create.remote.txg == 91);
        unsigned before = f.requests;
        assert(aefd_test_dup2(fd, fd) == fd && f.requests == before);
        assert(aefd_test_dup2(-1, 1) == -1 && errno == EBADF &&
               f.requests == before);
        assert(aether_zsh_raw_fcntl(1, F_DUPFD, 10) == 10);
        assert(__aether_io(33, 3, 1, 0) == 1 && c.map.slots[1].selector == 4);
        assert(aether_zsh_raw_close(3) == 0);
        /* Actual musl two-iovec flush coalesces this one16-byte argument into
         * one typed FILE write, even when split across its buffered prefix. */
        stream.fd = 1;
        stream.buf = stdio_buffer;
        stream.buf_size = 32;
        memcpy(stdio_buffer, "AETHER-", 7);
        stream.wbase = stdio_buffer;
        stream.wpos = stdio_buffer + 7;
        assert(aefd_test_stdio_write(
                   &stream, (const unsigned char *)"HOME-158\n", 9) == 9);
        assert(c.note_write.remote.count == 16 &&
               c.note_write.remote.txg == 92);
        assert(aefd_test_dup2(10, 1) == 1 && !c.note_writers);
        assert(aether_zsh_raw_close(10) == 0);
        close_client();
    }
    setup(0);
    errno = 0;
    assert(!aefd_test_fopen(AEFD_HOME_PROFILE_PATH, "wx") && errno == EOPNOTSUPP);
    assert(!f.requests && !c.note_create_attempted);
    close_client();
    /* Fresh synthetic fork metadata must reject before guard/copy/dispatch. */
    struct aefd_fork fork_scope = {0};
    fork_scope.boot.phase = 2;
    fork_scope.boot.identity.slot = 1;
    fork_scope.boot.context.state = 1;
    fork_scope.boot.context.client.live = 1;
    fork_scope.boot.context.native.input = 71;
    fork_scope.boot.context.native.output = 72;
    fork_scope.boot.context.note_writers = 8;
    struct aefd_startup_auxv aux = {0, 71, 72};
    assert(aefd_fork_arm(&fork_scope, aux) == -16 &&
           fork_scope.phase == AEFD_FORK_IDLE);
    unsigned char snapshot[336];
    memset(snapshot, 0xa5, sizeof snapshot);
    fork_scope.boot.context.native.active = 1;
    assert(aefd_zsh_capture(&fork_scope.boot, aux, 9, 7, snapshot) == -16);
    for (unsigned i = 0; i < sizeof snapshot; i++)
        assert(snapshot[i] == 0xa5);
    fork_scope.phase = AEFD_FORK_ARMED;
    assert(aefd_fork_child(&fork_scope, aux, NULL, NULL) == -5);
    assert(fork_scope.phase == AEFD_FORK_FAILED &&
           fork_scope.boot.context.state == 4);
    setup(0);
    assert(aefd_test_umask(0) == 0077);
    assert(aefd_test_open64(AEFD_HOME_PROFILE_PATH, O_WRONLY | O_CREAT | O_EXCL, 0666) ==
               -1 &&
           errno == EOPNOTSUPP);
    assert(!f.requests);
    assert(aefd_test_umask(0077) == 0);
    close_client();
    puts("note provider mode/open/open64/fopen/flush/raw-dup2/restore pass");
    return 0;
#endif
}
