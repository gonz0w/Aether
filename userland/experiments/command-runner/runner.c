/* SPDX-License-Identifier: BSD-2-Clause */
/* Independent finite consumer; exit 29 is the producer harness convention. */
#include "native-io.h"
#include "../native-channel/channel.h"
#include <errno.h>
#include <string.h>
#include <unistd.h>
#ifdef NATIVE_MAPPED_RESULTS
#define FAILURE(n) 1
#else
#define FAILURE(n) (n)
#endif
#define CHECK(x, n)                                                            \
    do {                                                                       \
        if (!(x))                                                              \
            return FAILURE(n);                                                 \
    } while (0)
#ifdef NATIVE_RUNNER_STARTUP
static struct ar_invocation invocation;
#endif
static void request(unsigned char q[384])
{
    memset(q, 0, 384);
    native_put(q, 4);
    native_put(q + 4, 1);
    native_put(q + 8, 2);
    native_put(q + 12, 1);
    native_put(q + 16, 2);
    memcpy(q + 32, "bytecount", 9);
    for (unsigned i = 0; i < 2; i++) {
        unsigned b = 64 + i * 32;
        native_put(q + b, native_ref(i));
        native_put(q + b + 4, 3 + i);
        native_put(q + b + 8, i);
        native_put(q + b + 12, i ? 2 : 1);
    }
#ifdef NATIVE_RUNNER_STARTUP
    native_put(q + 8, invocation.count);
    memcpy(q + 32, invocation.args[0], AR_SLOT_SIZE);
    for (unsigned i = 0; i < invocation.count; ++i)
        memcpy(q + 128 + i * AR_SLOT_SIZE, invocation.args[i], AR_SLOT_SIZE);
    memcpy(q + 128 + invocation.count * AR_SLOT_SIZE, invocation.environment,
           AR_SLOT_SIZE);
#ifdef CORRUPT_STARTUP
    q[224] = 'Y';
#endif
#else
    memcpy(q + 128, "bytecount", 9);
    memcpy(q + 160, "--decimal", 9);
    memcpy(q + 192, "LC_ALL=C", 8);
#endif
}
#ifdef NATIVE_MAPPED_RESULTS
#include "mapped-runner.h"
#else
static int send(unsigned char *q, unsigned n, unsigned char *r)
{
    if (!native_exchange(q, n, r))
        return -999;
    int result = (int)native_word(r);
    for (unsigned i = result < 0 ? 4 : 16; i < 32; i++)
        if (r[i])
            return -998;
    return result;
}
#endif
#if defined(LAUNCH_CORPUS) || defined(LAUNCH_PREFIX)
#include "launch-native.h"
#endif
int main(int argc, char **argv)
{
#ifdef NATIVE_RUNNER_STARTUP
    struct ar_startup startup;
    CHECK(argc == 1 && !strcmp(argv[0], "client") &&
              native_runner_bootstrap(&startup) &&
              ar_select(&startup, &invocation) == AR_LAUNCH,
          40);
    memset(&startup, 0xa5, sizeof startup);
#else
    CHECK(argc == 1 && !strcmp(argv[0], "client") && native_bootstrap(0), 40);
#endif
    CHECK(channel_raw(0x23000, 0xa001, 0xc003, 0) == -EACCES, 41);
#ifdef NATIVE_MAPPED_RESULTS
    return mapped_run();
#else
    unsigned char q[384], r[32];
#ifdef LAUNCH_CORPUS
    CHECK(launch_corpus(), 103);
#endif
#ifdef LAUNCH_PREFIX
    return launch_prefix();
#endif
    request(q);
    q[32] = 'X';
    CHECK(send(q, 384, r) == -ENOENT, 42);
    request(q);
    native_put(q + 104, 0);
    CHECK(send(q, 384, r) == -EINVAL, 43);
    request(q);
    native_put(q + 108, 3);
    CHECK(send(q, 384, r) == -EACCES, 44);
    request(q);
    native_put(q + 96, native_ref(0));
    CHECK(send(q, 384, r) == -EBADF, 45);
    request(q);
    native_put(q + 8, 5);
    CHECK(send(q, 384, r) == -EINVAL, 46);
    request(q);
    q[383] = 1;
    CHECK(send(q, 384, r) == -EINVAL, 47);
    request(q);
    native_put(q + 4, 2);
    CHECK(send(q, 384, r) == -EINVAL, 48);
#ifdef REJECT_LAUNCH
    if (native_generation() == 1) {
        request(q);
        CHECK(send(q, 384, r) == -EINVAL, 49);
    }
#endif
#ifdef REJECT_CAPACITY
    if (native_generation() == 1) {
        request(q);
        CHECK(send(q, 384, r) == -EBUSY, 49);
    }
#endif
    request(q);
    CHECK(send(q, 384, r) == 0 &&
              native_word(r + 4) == (0x73000000u | native_generation()) &&
              !native_word(r + 8) && !native_word(r + 12),
          50);
    unsigned receipt = native_word(r + 4);
    memset(q, 0xa5, sizeof q);
    errno = EDOM;
    CHECK(close(3) == 0 && errno == EDOM, 51);
    memset(q, 0, 32);
    native_put(q, 5);
    native_put(q + 4, receipt ^ 8);
    CHECK(send(q, 32, r) == -ECHILD, 52);
    int result = -EAGAIN;
    for (unsigned t = 0; t < 100000 && result == -EAGAIN; t++) {
        memset(q, 0, 32);
        native_put(q, 5);
        native_put(q + 4, receipt);
        result = send(q, 32, r);
        channel_yield();
    }
    CHECK(result == 0 && native_word(r + 4) == receipt &&
              native_word(r + 8) ==
#ifdef TERMINAL_DETAIL
                  TERMINAL_DETAIL
#elif defined(FULL_OUTPUT)
                  1
#else
              0
#endif
              && native_word(r + 12) ==
#ifdef TERMINAL_KIND
                     TERMINAL_KIND,
#else
                     1,
#endif
          53);
    memset(q, 0, 32);
    native_put(q, 5);
    native_put(q + 4, receipt);
    CHECK(send(q, 32, r) == -ECHILD, 54);
    char b[23];
    errno = EDOM;
    CHECK(read(4, b, sizeof b) == 0 && errno == EDOM, 55);
    CHECK(close(4) == 0, 56);
    errno = 0;
    CHECK(read(4, b, 0) == -1 && errno == EBADF, 57);
    return 29;
#endif
}
