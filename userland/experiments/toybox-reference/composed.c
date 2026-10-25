// SPDX-License-Identifier: BSD-2-Clause
#define _POSIX_C_SOURCE 200809L
#include "session.h"
#include "mask.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/uio.h>
#include <unistd.h>
int __real_main(int, char **);
ssize_t __real_write(int, const void *, size_t);
ssize_t __real_read(int, void *, size_t);
int __real_fflush(FILE *);
static struct ts_state session;
static struct tm_state mask;
static unsigned masks, flushes, writes, closes;
static char order[4];
static int observer;
static const char *mode;
static int selected(const char *s) { return !strcmp(mode, s); }
static void observe(const char *text)
{
    size_t n = strlen(text);
    if (__real_write(observer, text, n) != (ssize_t)n)
        _Exit(121);
}
static struct tv_reply backend(void *unused, unsigned sink,
                               const unsigned char *data, size_t count)
{
    (void)unused;
    writes++;
    if (sink == 1 && selected("diagnostic-error"))
        return (struct tv_reply){1, 0, -EIO};
    if (count > 2)
        count = 2;
    ssize_t n = __real_write(sink ? 2 : 1, data, count);
    if (n < 0)
        return (struct tv_reply){1, 0, -errno};
    if (sink == 0 && selected("lost-ack"))
        return (struct tv_reply){0, 0, -EIO};
    return (struct tv_reply){1, (size_t)n, 0};
}
static ssize_t convert(struct tv_reply r)
{
    if (!r.known || r.error) {
        errno = r.known ? -r.error : EIO;
        return -1;
    }
    return (ssize_t)r.count;
}
ssize_t fixture_writev(int fd, const struct iovec *iov, int count)
{
    if ((fd != 1 && fd != 2) || count < 0 || count > 2) {
        errno = EINVAL;
        return -1;
    }
    struct tv_part parts[2] = {{0}};
    for (int i = 0; i < count; i++)
        parts[i] = (struct tv_part){iov[i].iov_base, iov[i].iov_len};
    return convert(ts_write(&session, (unsigned)(fd - 1), parts,
                            (unsigned)count, backend, NULL));
}
ssize_t __wrap_write(int fd, const void *data, size_t count)
{
    struct iovec part = {(void *)data, count};
    return fixture_writev(fd, &part, 1);
}
ssize_t __wrap_read(int fd, void *data, size_t count)
{
    if (session.io.poisoned) {
        errno = EIO;
        return -1;
    }
    return __real_read(fd, data, count > 3 ? 3 : count);
}
mode_t __wrap_umask(mode_t requested)
{
    uint32_t old;
    if (!tm_exchange(&mask, 1, requested, &old))
        _Exit(122);
    masks++;
    return old;
}
int __wrap_fflush(FILE *f)
{
    int result = __real_fflush(f);
    if (!f)
        flushes++;
    return result;
}
static enum tf_result close_role(void *unused, unsigned role)
{
    (void)unused;
    if (!flushes || session.io.poisoned || closes >= 3)
        _Exit(123);
    order[closes++] = (char)('0' + role);
    int result = close((int)role);
    if (role == 0 && selected("close-unknown"))
        return TF_UNKNOWN;
    if (result || (role == 0 &&
                   (selected("close-error") || selected("diagnostic-error"))))
        return TF_ERROR;
    return TF_OK;
}
static enum tf_result diagnostic(void *unused)
{
    (void)unused;
    const unsigned char text[] = "fixture cleanup\n";
    size_t used = 0;
    while (used < sizeof(text) - 1) {
        struct tv_part part = {text + used, sizeof(text) - 1 - used};
        struct tv_reply r = tv_write(&session.io, 1, &part, 1, backend, NULL);
        if (!r.known)
            return TF_UNKNOWN;
        if (r.error || !r.count)
            return TF_ERROR;
        used += r.count;
    }
    return TF_OK;
}
_Noreturn void __wrap__exit(int status)
{
    if (masks != 2 || mask.mask != 0077 || flushes != 1)
        _Exit(124);
    const struct tf_ops ops = {close_role, diagnostic};
    unsigned result = ts_finish(&session, (unsigned)status, 1, &ops, NULL);
    unsigned before = writes;
    const unsigned char byte = 42;
    struct tv_part part = {&byte, 1};
    struct tv_reply late = ts_write(&session, 0, &part, 1, backend, NULL);
    if (late.count || !late.error || writes != before)
        _Exit(125);
    if (!tm_retire(&mask, 1))
        _Exit(126);
    char report[160];
    int n =
        snprintf(report, sizeof(report),
                 "OBS masks=2 restored=77 flush=1 closes=%s consumed=%u "
                 "poison=%u status=%u\n",
                 order, session.finish.consumed, session.io.poisoned, result);
    if (n < 0 || (size_t)n >= sizeof(report))
        _Exit(127);
    observe(report);
    (void)close(observer);
    _Exit((int)result);
}
int __wrap_main(int argc, char **argv)
{
    observer = dup(2);
    if (observer < 3)
        _Exit(120);
    mode = getenv("TOYBOX_COMPOSED");
    if (!mode)
        mode = "baseline";
    if (!tm_init(&mask, 1, selected("invalid-mask") ? 01000 : 0077)) {
        observe("OBS init-rejected\n");
        (void)close(observer);
        _Exit(120);
    }
    return __real_main(argc, argv);
}
