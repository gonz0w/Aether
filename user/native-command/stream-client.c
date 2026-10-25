/* SPDX-License-Identifier: BSD-2-Clause */
#include "transport.h"
#include <unistd.h>
#include "stream-text.h"
static _Thread_local volatile unsigned cookie = 23;
int main(int argc, char **argv)
{
    if (cookie != 23 || argc != 1 || strcmp(argv[0], "client"))
        return 109;
    if (!bootstrap()) {
#ifdef STREAM_EARLY
        (void)write(1, "!", 1);
#endif
        return 110;
    }
#ifdef RUNNER_DENIAL
#ifndef DENIAL_SKIP
    unsigned char request[384] = {0};
    put(request, 0, 4);
    put(request, 4, 1);
    put(request, 8, 2);
    put(request, 12, 1);
    put(request, 16, 2);
    memcpy(request + 32, "bytecount", 9);
    memcpy(request + 128, "bytecount", 9);
    memcpy(request + 160, "--decimal", 9);
    memcpy(request + 192, "LC_ALL=C", 8);
    for (unsigned j = 0; j < 2; j++) {
        unsigned at = 64 + j * 32;
        put(request, at, refs[j + 2]);
        put(request, at + 4, j + 3);
        put(request, at + 8, j);
        put(request, at + 12, j ? 2 : 1);
    }
#if DENIAL_ERRNO == 2
    request[32] = 'X';
#elif DENIAL_ERRNO == 13
    put(request, 76, 3);
#endif
#ifdef DENIAL_REPEAT
    unsigned char repeated[384];
    memcpy(repeated, request, sizeof request);
#endif
    if (!exchange(request, sizeof request) ||
        (int)get(request, 0) != -DENIAL_ERRNO)
        return 125;
    for (unsigned i = 4; i < 32; i++)
        if (request[i])
            return 125;
#ifdef DENIAL_REPEAT
    (void)exchange(repeated, sizeof repeated);
#endif
#endif
#endif
#ifdef STREAM_LAUNCH_HELP
    unsigned char bad_launch[32] = {0};
    put(bad_launch, 0, 4);
    (void)exchange(bad_launch, sizeof bad_launch);
#endif
    int failed = 0;
    char probe;
    errno = 0;
    if (read(1, &probe, 1) != -1 || errno != EACCES)
        return 111;
#ifndef STREAM_SKIP
    unsigned offset = 0;
    while (offset < sizeof stream_text) {
        unsigned char bytes[16];
        unsigned n = sizeof stream_text - offset;
        if (n > sizeof bytes)
            n = sizeof bytes;
        memcpy(bytes, stream_text + offset, n);
#ifdef STREAM_WRONG_BYTE
        if (!offset)
            bytes[0] ^= 1;
#endif
        ssize_t wrote = write(
#ifdef STREAM_WRONG_SINK
            3 - STREAM_FD,
#else
            STREAM_FD,
#endif
            bytes, n);
        if (wrote <= 0 || wrote > n) {
#ifdef STREAM_RETRY
            (void)write(STREAM_FD, bytes, n);
#endif
            failed = 1;
            break;
        }
        offset += (unsigned)wrote;
    }
#endif
#ifdef STREAM_RESUME
    poisoned = 0; /* Deliberately violate the incomplete-reply boundary. */
#endif
#ifndef STREAM_SKIP_CLOSE
    if (close(1)) {
#ifndef STREAM_IGNORE_CLOSE
        failed = 1;
#endif
    }
#endif
    if (close(2))
        failed = 1;
#ifdef RUNNER_DENIAL
    if (close(3))
        failed = 1;
#ifndef DENIAL_SKIP_LAST_CLOSE
    if (close(4))
        failed = 1;
#endif
#endif
#ifdef STREAM_AFTER_CLOSE
    unsigned char bad[32] = {0};
    put(bad, 0, 5);
    (void)move(bad, sizeof bad, 1);
#endif
#ifdef STREAM_AMBIGUOUS
    if (!poisoned || !poison_calls || channel_calls != poison_calls)
        return 124;
    for (unsigned j = 0; j < BINDINGS; j++)
        if (live[j])
            return 124;
#endif
#ifdef DENIAL_HIDE_FAILURE
    (void)failed;
    return STREAM_STATUS;
#elif defined(STREAM_FORCE_ZERO)
    (void)failed;
    return 0;
#elif defined(STREAM_FAKE_FAILURE)
    (void)failed;
    return 1;
#else
    return failed ? 1 : STREAM_STATUS;
#endif
}
