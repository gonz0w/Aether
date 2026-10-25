/* SPDX-License-Identifier: BSD-2-Clause */
/* Host peer controls; they do not enforce native authority or cleanup. */
#include "native-io.h"
#include <assert.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

long __aether_io(unsigned long, unsigned long, unsigned long, unsigned long);
static unsigned char boot[384], reply[32];
static unsigned used, size, calls, writes, reads, reply_used, yields;
static long epoch;
static int active, fault;
unsigned long getauxval(unsigned long key)
{
    return key == 0xa001 ? 101 : key == 0xa002 ? 202 : 0;
}
void channel_yield(void) { ++yields; }
long channel_raw(unsigned long op, unsigned long grant, unsigned long address,
                 unsigned long count)
{
    ++calls;
    if (op == 0x20005)
        return epoch;
    assert(op == 0x24001 || op == 0x24002);
    int writing = op == 0x24002;
    assert(grant == (writing ? 202u : 101u));
    assert(count && count <= (writing ? 7u : 5u));
    if (calls % 11 == 0)
        return -EAGAIN;
    if (!active) {
        assert(!writing && count <= size - used);
        if (fault == 3 && used >= 8)
            return 0;
        if (count > 2)
            count = 2;
        memcpy((void *)address, boot + used, count);
        used += (unsigned)count;
        return (long)count;
    }
    if (writing) {
        if (fault == 4 && writes >= 2)
            return -EIO;
        if (count > 3)
            count = 3;
        writes += (unsigned)count;
    } else {
        assert(count <= 32 - reply_used);
        if (count > 2)
            count = 2;
        memcpy((void *)address, reply + reply_used, count);
        reply_used += (unsigned)count;
        reads += (unsigned)count;
    }
    return (long)count;
}
static void fixture(unsigned selected)
{
#ifdef NATIVE_RUNNER_STARTUP
    const unsigned refs[] = {0x75010000, 0x75020000, 0x71000000, 0x71010000};
    const unsigned rights[] = {2, 2, 1, 3}, caps[] = {512, 256, 6, 64};
    memcpy(boot, "AERUN001", 8);
    native_put(boot + 8, 3);
    memcpy(boot + 32, "aether-run", 10);
    memcpy(boot + 64, "bytecount", 9);
    memcpy(boot + 96, "--decimal", 9);
    unsigned char *r = boot + AR_CARRIER_SIZE;
    memcpy(r, "AERIO002", 8);
    native_put(r + 8, 4);
    native_put(r + 12, selected);
    for (unsigned i = 0; i < 4; ++i) {
        unsigned char *entry = r + 32 + i * 32;
        native_put(entry, i + 1);
        native_put(entry + 4, refs[i] | selected);
        native_put(entry + 8, i + 1);
        native_put(entry + 12, rights[i]);
        native_put(entry + 16, caps[i]);
    }
    size = sizeof boot;
#else
    for (unsigned i = 0; i < 2; ++i) {
        native_put(boot + 4 + i * 12, 0x72000000u | (i << 16) | selected);
        native_put(boot + 8 + i * 12, i);
        native_put(boot + 12 + i * 12, i ? 2 : 1);
    }
    native_put(boot + 28, 0x324f494e);
    size = 32;
#endif
}
static void scenario(long native, unsigned wire, int mode)
{
    epoch = native;
    fault = mode;
    fixture(wire);
    if (mode == 1) {
#ifdef NATIVE_RUNNER_STARTUP
        boot[AR_CARRIER_SIZE + 7] = '1';
#else
        native_put(boot + 28, 0);
#endif
    }
    if (mode == 2)
        boot[size - 1] ^= 1;
    if (mode == 6) {
#ifdef NATIVE_RUNNER_STARTUP
        boot[AR_CARRIER_SIZE + 128 + 12] = 2; /* Late file-write rights. */
#else
        native_put(boot + 24, 3); /* Late child-write rights. */
#endif
    }
#ifdef NATIVE_RUNNER_STARTUP
    struct ar_startup startup, sentinel;
    memset(&sentinel, 0xa5, sizeof sentinel);
    startup = sentinel;
    int ok = native_runner_bootstrap(&startup);
#else
    int ok = native_bootstrap(1);
#endif
    int expected = native >= 1 && native <= 65535 &&
                   (unsigned long)native == wire && mode != 1 && mode != 2 &&
                   mode != 3 && mode != 6;
    assert(ok == expected);
    unsigned before = calls;
#ifdef NATIVE_RUNNER_STARTUP
    assert(!native_runner_bootstrap(&startup));
#else
    assert(!native_bootstrap(1));
#endif
    assert(calls == before);
    if (!ok) {
#ifdef NATIVE_RUNNER_STARTUP
        assert(!memcmp(&startup, &sentinel, sizeof startup));
#endif
        assert(!native_ref(0) && !native_ref(1));
        if (native < 1 || native > 65535)
            assert(used == 0 && calls == 1); /* No wire side effects. */
        unsigned char q[32] = {0}, r[32];
        assert(!native_exchange(q, 32, r) && calls == before);
        return;
    }
    assert(used == size && yields && native_generation() == wire);
    assert(native_ref(0) ==
#ifdef NATIVE_RUNNER_STARTUP
           (0x71000000u | wire)
#else
           (0x72000000u | wire)
#endif
    );
#ifdef NATIVE_RUNNER_STARTUP
    assert(startup.count == 3 && !strcmp(startup.args[2], "--decimal"));
    unsigned fd = 4;
#else
    unsigned fd = 0;
#endif
    active = 1;
    unsigned char data[16];
    memset(data, 0xa5, sizeof data);
    native_put(reply, mode == 5 ? (unsigned)-EIO : 2);
    if (mode != 5)
        memcpy(reply + 16, "OK", 2);
    errno = EDOM;
    long result = __aether_io(0, fd, (unsigned long)data, sizeof data);
    assert(errno == EDOM);
    if (mode == 4) {
        assert(result == -EIO && writes == 3 && !reads);
        before = calls;
        unsigned char q[32] = {0}, r[32];
        assert(!native_exchange(q, 32, r) && calls == before);
        assert(data[0] == 0xa5);
        return;
    }
    assert(result == (mode == 5 ? -EIO : 2));
    assert(mode == 5 ? data[0] == 0xa5 : !memcmp(data, "OK", 2));
    writes = reads = reply_used = 0;
    memset(reply, 0, sizeof reply);
    native_put(reply, (unsigned)-EIO);
    assert(__aether_io(3, fd, 0, 0) == -EIO); /* Failed close consumes fd. */
    before = calls;
    assert(__aether_io(3, fd, 0, 0) == -EBADF && calls == before);
    assert(__aether_io(0, fd, (unsigned long)data, 0) == -EBADF);
}
int main(void)
{
    const long epochs[] = {1, 2,  3,     5,       32768,        65535,
                           0, -1, 65536, 0x10001, 0x100000001L, LONG_MAX};
    unsigned cases = 0;
    for (unsigned i = 0; i < sizeof epochs / sizeof epochs[0]; ++i) {
        for (int mode = 0; mode <= 6; ++mode) {
            pid_t pid = fork();
            assert(pid >= 0);
            if (!pid) {
                scenario(epochs[i], (unsigned)epochs[i], mode);
                _exit(0);
            }
            int status;
            assert(waitpid(pid, &status, 0) == pid);
            assert(WIFEXITED(status) && WEXITSTATUS(status) == 0);
            ++cases;
        }
    }
    pid_t pid = fork();
    assert(pid >= 0);
    if (!pid) {
        scenario(5, 4, 0); /* Valid-width divergent cohort. */
        _exit(0);
    }
    int status;
    assert(waitpid(pid, &status, 0) == pid);
    assert(WIFEXITED(status) && WEXITSTATUS(status) == 0);
    printf("PASS: %u isolated bootstrap/transport cases\n", cases + 1);
    return 0;
}
