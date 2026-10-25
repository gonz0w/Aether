/* SPDX-License-Identifier: BSD-2-Clause */
/* Role/copy witness only; this is not Toybox or its finalization adapter. */
#include "transport.h"
#include <unistd.h>
#ifdef CAT_ADMISSION
extern char **environ;
#endif
static _Thread_local volatile unsigned cookie = 23;
#if defined(CAT_FAULT_BEFORE) || defined(CAT_FAULT_COPY) ||                    \
    defined(CAT_FAULT_DIAG)
static _Noreturn void fault_now(void)
{
#ifdef CAT_SIGNAL_LIVE
    memtrap(0x29002, 15, 0, 0, 0);
    _exit(93);
#elif defined(CAT_FAULT_EXIT)
    _exit(134);
#else
    /* Intentional isolated user fault: no operands, no return path. */
    __asm__ volatile("ud2");
    __builtin_unreachable();
#endif
}
#endif

/* Conformance-only completed re-entry guard; no Toybox callbacks run here. */
static int finished, finished_status;
static int finish_bindings(int status)
{
    if (finished)
        return finished_status;
    finished = 1;
    int failed = 0;
    if (close(0))
        failed = 1;
    if (close(1))
        failed = 1;
#ifndef CAT_SKIP_CLOSE
    if (close(2))
        failed = 1;
#endif
    finished_status = status ? status : failed ? 1 : 0;
    return finished_status;
}

int main(int argc, char **argv)
{
#ifndef CAT_ADMISSION
    if (cookie != 23 || argc != 1 || strcmp(argv[0], "client"))
        return 109;
#endif
    if (!bootstrap()) {
#ifdef CAT_EARLY
        (void)write(1, "!", 1);
#endif
        return 110;
    }
    int status = 0;
    int failed = 0;
    int result = 0;
#ifdef CAT_ADMISSION
    if (cookie != 23 || argc < 1 || strcmp(argv[0], "cat") || argv[argc] ||
        !environ || !environ[0] || strcmp(environ[0], "LC_ALL=C") || environ[1])
        return 109;
#ifdef CAT_FAULT_BEFORE
    fault_now();
#endif
    if (argc != 1) {
        status = 64;
#ifdef CAT_USAGE_READ
        char probe;
        (void)read(0, &probe, 1);
#endif
#ifndef CAT_USAGE_SKIP
        char text[] = "cat: this profile accepts stdin only\n";
#ifdef CAT_USAGE_CORRUPT
        text[0] ^= 1;
#endif
        for (unsigned at = 0; at < sizeof text - 1;) {
            ssize_t done = write(2, text + at, sizeof text - 1 - at);
            if (done <= 0) {
#ifdef CAT_EINTR
                if (errno != EINTR)
                    return 114;
#endif
                failed = 1;
                break;
            }
            at += (unsigned)done;
#ifdef CAT_FAULT_DIAG
            fault_now();
#endif
        }
#endif
        goto finish;
    }
#endif
    unsigned char b[11];
#ifndef CAT_SKIP_COPY
    ssize_t n;
    while ((n = read(0, b, sizeof b)) > 0) {
#ifdef CAT_CORRUPT
        b[0] ^= 1;
#endif
        for (unsigned at = 0; at < (unsigned)n;) {
            ssize_t done = write(1, b + at, (unsigned)n - at);
            if (done <= 0) {
#ifdef CAT_EINTR
                if (errno != EINTR)
                    return 114;
#endif
#ifdef CAT_RETRY_ERROR
                (void)write(1, b + at, (unsigned)n - at);
#endif
                failed = 1;
                goto finish;
            }
            at += (unsigned)done;
#ifdef CAT_FAULT_COPY
            fault_now();
#endif
        }
    }
    if (n < 0) {
#ifdef CAT_EINTR
        if (errno != EINTR)
            return 114;
#endif
        failed = 1;
        goto finish;
    }
#else
    (void)b;
#endif
#ifdef CAT_DIAGNOSTIC
    if (write(2, "D\n", 2) != 2)
        failed = 1;
#endif
#if defined(CAT_ADMISSION) || !defined(CAT_SKIP_COPY)
finish:
#endif
#ifdef CAT_CLEAR_POISON
    poisoned = 0;
#endif
    result = finish_bindings(status ? status : failed ? 1 : 0);
#ifdef CAT_UNKNOWN
    if (!poisoned || !poison_calls || channel_calls != poison_calls)
        return 112;
    for (unsigned j = 0; j < 3; j++) {
        if (live[j])
            return 112;
        errno = 0;
        if (close((int)j) != -1 || errno != EBADF ||
            channel_calls != poison_calls)
            return 112;
    }
#endif
#ifdef CAT_FINAL_TEST
    unsigned before = channel_calls;
#ifdef CAT_FINAL_RESET
    finished = 0;
#endif
    if (finish_bindings(result ? 0 : 64) != result || channel_calls != before)
        return 113;
    for (unsigned j = 0; j < 3; j++)
        if (live[j])
            return 113;
#endif
#ifdef CAT_FORCE_ZERO
    (void)result;
    return 0;
#else
    return result;
#endif
}
