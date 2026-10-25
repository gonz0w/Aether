/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual Toybox cat and normal-exit witness; bounded admitted stdin only.
 */
#include "transport.h"
#include "toys.h"
#include "vector-write.h"

static _Thread_local volatile unsigned startup_cookie = 23;
static void *startup_buffer;
static unsigned allocated_buffer, configured_buffer;
void *__real_xmalloc(size_t size);
int __real_setvbuf(FILE *stream, char *buffer, int mode, size_t size);
void *__wrap_xmalloc(size_t size)
{
    void *p = __real_xmalloc(size);
    if (size == 4096) {
        startup_buffer = p;
        allocated_buffer++;
    }
    return p;
}
int __wrap_setvbuf(FILE *stream, char *buffer, int mode, size_t size)
{
    int result = __real_setvbuf(stream, buffer, mode, size);
    if (stream == stdout && buffer == startup_buffer && buffer &&
        mode == _IOFBF && size == 4096 && result == 0)
        configured_buffer++;
    return result;
}
static unsigned mask_live, mask_value, mask_calls;
static unsigned requests[2], previous[2];
mode_t umask(mode_t requested)
{
    if (!mask_live) {
        errno = EINVAL;
        return (mode_t)-1;
    }
    unsigned old = mask_value;
    mask_value = requested & 0777u;
    if (mask_calls < 2) {
        requests[mask_calls] = requested;
        previous[mask_calls] = old;
    }
    mask_calls++;
#ifdef MASK_WRONG_OLD
    return requested;
#else
    return old;
#endif
}
ssize_t fixture_writev(int fd, const struct iovec *parts, int count)
{
    long result = vector_write(fd, parts, count);
    if (result < 0) {
        errno = (int)-result;
        return -1;
    }
    return result;
}
void cat_main(void);
static unsigned callback_order, flushed, inspected, finished;
static int flush_result;
#ifdef APP_CLOSE_POLICY
static unsigned finish_reentered;
#endif
#ifdef APP_FINAL_BUFFER
static unsigned char final_bytes[32];
static void callback_write(unsigned offset)
{
    unsigned before = channel_calls;
#ifdef APP_FINAL_CORRUPT
    final_bytes[offset] ^= 1;
#endif
    if (fwrite(final_bytes + offset, 1, 16, stdout) != 16)
        _exit(123);
#ifdef APP_FINAL_EARLY_FLUSH
    (void)fflush(stdout);
#endif
    if (channel_calls != before)
        _exit(123);
}
#endif
static void first_callback(int signal)
{
    callback_order = !signal && callback_order == 1 ? 2 : 99;
#ifdef APP_FINAL_BUFFER
    callback_write(16);
#endif
}
static void second_callback(int signal)
{
    callback_order = !signal && !callback_order ? 1 : 99;
#ifdef APP_FINAL_BUFFER
    callback_write(0);
#endif
}
int __real_fflush(FILE *stream);
int __real_ferror(FILE *stream);
int __wrap_fflush(FILE *stream)
{
    int observed = !stream && callback_order == 2;
    if (observed)
        flushed++;
    int result = __real_fflush(stream);
    if (observed)
        flush_result = result;
    return result;
}
int __wrap_ferror(FILE *stream)
{
    if (stream == stdout && flushed == 1)
        inspected++;
    return __real_ferror(stream);
}
/* Called only at the patched normal _xexit seam, after its rebound branch.
 * Upstream owns callback nodes and stdio; transport owns live alias retirement.
 * This bounded witness does not offer a recursive or signal-safe finalizer. */
int fixture_finish(int status)
{
#ifdef APP_CLOSE_POLICY
    if (finished) {
#ifndef APP_CLOSE_IGNORE_REENTRY
        finish_reentered = 1;
#endif
        return 120;
    }
#endif
    if (finished || callback_order != 2 || flushed != 1 ||
        inspected != (flush_result ? 0u : 1u) || toys.xexit || !live[0] ||
        !live[1] || !live[2])
        return 120;
    finished = 1;
#ifdef APP_CLOSE_POLICY
#ifdef APP_CLOSE_REENTER
    unsigned entry_calls = channel_calls;
    if (fixture_finish(status) != 120 || channel_calls != entry_calls)
        return 121;
#endif
    int close_failed = 0;
    for (int fd = 0; fd < 2; fd++) {
        if (close(fd)) {
            close_failed = 1;
            if (!status)
                status = 1;
        }
#ifdef APP_CLOSE_REPLAY
        if (!fd) {
            live[0] = 1; /* Deliberate protocol replay mutant. */
            (void)close(0);
        }
#endif
    }
#ifndef APP_CLOSE_SKIP_DIAG
    if (close_failed) {
        if (fprintf(stderr, "cat: close failed\n") < 0 && !status)
            status = 1;
        if (fflush(stderr) && !status)
            status = 1;
    }
#else
    (void)close_failed;
#endif
    if (close(2) && !status)
        status = 1;
    if (finish_reentered && !status)
        status = 1;
#else
    for (int fd = 0; fd < 3; fd++) {
#ifdef APP_SKIP_CLOSE
        if (fd == 2)
            continue;
#endif
        if (close(fd) && !status)
            status = 1;
    }
#endif
#ifdef APP_CHECK_UNKNOWN
    if (!poisoned || !poison_calls || channel_calls != poison_calls ||
        live[0] || live[1] || live[2])
        return 121;
#endif
    mask_live = 0;
#ifdef APP_FINISH_REENTER
    unsigned before = channel_calls;
    if (fixture_finish(status) != 120 || channel_calls != before)
        return 121;
#endif
#ifdef APP_FORCE_ZERO
    return 0;
#else
    return status;
#endif
}
/* Profile rejection occurs before Toybox initialization. It uses the same
 * scoped streams, but does not enter Toybox's callback/exit machinery. */
static int reject_usage(void)
{
#ifdef APP_USAGE_READ
    char byte;
    (void)read(0, &byte, 1);
#endif
    char message[] = "cat: this profile accepts stdin only\n";
#ifdef APP_USAGE_CORRUPT
    message[0] ^= 1;
#endif
    int result = fprintf(stderr, "%s", message);
    if ((result >= 0 && result != (int)sizeof message - 1) ||
        (result < 0 && (!ferror(stderr) || (errno != EIO && errno != EINTR))))
        return 122;
    (void)fflush(stderr);
    unsigned before = channel_calls;
    for (int fd = 0; fd < 3; fd++) {
#ifdef APP_USAGE_SKIP_CLOSE
        if (fd == 2)
            continue;
#endif
        (void)close(fd);
    }
    if (poisoned && channel_calls != before)
        return 122;
#ifdef CAT_UNKNOWN
    if (poisoned && (!poison_calls || channel_calls != poison_calls))
        return 122;
#endif
    if (mask_live || mask_calls || allocated_buffer || configured_buffer ||
        callback_order || flushed || inspected || finished || toys.which)
        return 122;
#ifdef APP_USAGE_ZERO
    return 0;
#else
    return 64;
#endif
}
int main(int argc, char **argv)
{
    if (startup_cookie != 23)
        return 115;
    startup_cookie++;
    if (argc < 1 || argc > 4 || strcmp(argv[0], "cat") || argv[argc] ||
        !bootstrap())
        return 115;
    if (!environ || !environ[0] || strcmp(environ[0], "LC_ALL=C") || environ[1])
        return 115;
    if (argc != 1)
        return reject_usage();
    if (!getauxval(0xa000))
        return 116;
    errno = 0;
    if (umask(0) != (mode_t)-1 || errno != EINVAL)
        return 115;
    mask_live = 1;
    mask_value = 0077;
#ifndef MASK_WRONG_OLD
    if (umask(07777) != 0077 || mask_value != 0777 || umask(0077) != 0777)
        return 115;
#endif
    mask_calls = 0;
    if (strcmp(toy_list[0].name, "cat") || (toy_list[0].flags & TOYFLAG_NOFORK))
        return 115;
#ifndef MASK_SKIP_INIT
    toy_singleinit(toy_list, argv);
#endif
    if (startup_cookie != 24 || allocated_buffer != 1 ||
        configured_buffer != 1 || mask_calls != 2 || requests[0] != 0 ||
        requests[1] != 0077 || previous[0] != 0077 || previous[1] != 0 ||
        mask_value != 0077 || toys.old_umask != 0077 ||
        toys.which != toy_list || toys.optc != 0 ||
        strcmp(nl_langinfo(CODESET), "UTF-8"))
        return 115;
    struct arg_list *first = xmalloc(sizeof *first);
    struct arg_list *second = xmalloc(sizeof *second);
    first->arg = (char *)first_callback;
    first->next = 0;
    second->arg = (char *)second_callback;
    second->next = first;
#ifndef APP_SKIP_CALLBACK
    toys.xexit = second;
#else
    free(second);
    free(first);
#endif
#ifdef APP_FINAL_BUFFER
    unsigned at = 0;
    while (at < sizeof final_bytes) {
        ssize_t n = read(0, final_bytes + at, sizeof final_bytes - at);
        if (n <= 0 || (unsigned)n > sizeof final_bytes - at)
            return 123;
        at += (unsigned)n;
    }
    unsigned char extra;
    if (read(0, &extra, 1) != 0)
        return 123;
#else
#ifndef APP_SKIP_COPY
    cat_main();
#endif
#endif
#ifdef APP_FINAL_STATUS
    toys.exitval = 64;
#endif
    xexit();
    return 120;
}
