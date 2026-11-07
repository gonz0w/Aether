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
static FILE stream;
static unsigned char stdio_buffer[32];
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
int main(void)
{
    assert(!aefd_zsh_admit());
    assert(aefd_test_umask(01777) == 0077);
    assert(aefd_test_umask(0077) == 0777);
    assert(aefd_test_umask(0077) == 0077);
    for (int route = 0; route < 3; route++) {
        setup(0);
        errno = ERANGE;
        assert(aether_zsh_open("/home/note", O_WRONLY | O_CREAT | O_EXCL,
                               0444) == -1 &&
               errno == EOPNOTSUPP);
        assert(!f.requests);
        errno = ERANGE;
        int fd;
        if (route == 0)
            fd = aefd_test_open("/home/note",
                                O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0666);
        else if (route == 1)
            fd = aefd_test_open64(
                "/home/note", O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0666);
        else
            fd = aether_zsh_open(
                "/home/note",
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
    assert(!aefd_test_fopen("/home/note", "wx") && errno == EOPNOTSUPP);
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
    assert(aefd_test_open64("/home/note", O_WRONLY | O_CREAT | O_EXCL, 0666) ==
               -1 &&
           errno == EOPNOTSUPP);
    assert(!f.requests);
    assert(aefd_test_umask(0077) == 0);
    close_client();
    puts("note provider mode/open/open64/fopen/flush/raw-dup2/restore pass");
    return 0;
}
