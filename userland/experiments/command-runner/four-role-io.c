/* SPDX-License-Identifier: BSD-2-Clause */
#include "native-io.h"
#include "four-role.h"
#include "../native-channel/channel.h"
#include <errno.h>
#include <limits.h>
#include <string.h>
#include <sys/auxv.h>
static _Thread_local volatile unsigned tls = 89;
static unsigned long input, output;
static unsigned refs[4], fds[4], rights[4], generation;
static int live[4], poisoned, bootstrap_attempted;
unsigned native_word(const unsigned char *p)
{
    return (unsigned)p[0] | (unsigned)p[1] << 8 | (unsigned)p[2] << 16 |
           (unsigned)p[3] << 24;
}
void native_put(unsigned char *p, unsigned n)
{
    for (unsigned i = 0; i < 4; i++)
        p[i] = (unsigned char)(n >> (8 * i));
}
unsigned native_ref(unsigned i) { return i < 2 ? refs[i + 2] : 0; }
unsigned native_generation(void) { return generation; }
static int transfer(unsigned char *p, unsigned size, int writing)
{
    if (poisoned)
        return 0;
    unsigned used = 0;
    for (unsigned turn = 0; turn < 100000; turn++) {
        unsigned n = size - used, limit = writing ? 7 : 5;
        if (n > limit)
            n = limit;
        long result =
            channel_raw(writing ? 0x24002 : 0x24001, writing ? output : input,
                        (unsigned long)(p + used), n);
        if (result == -EAGAIN) {
            channel_yield();
            continue;
        }
        if (result <= 0 || (unsigned long)result > n)
            break;
        used += (unsigned)result;
        if (used == size)
            return 1;
    }
    poisoned = 1;
    return 0;
}
int native_exchange(unsigned char *q, unsigned size, unsigned char r[32])
{
    if (size != 32 && size != 384) {
        poisoned = 1;
        return 0;
    }
    return transfer(q, size, 1) && transfer(r, 32, 0);
}
#ifdef NATIVE_RUNNER_STARTUP
static int bootstrap(int child, struct ar_startup *startup, int carrier)
#else
int native_bootstrap(int child)
#endif
{
    /* Initialization consumes this connection even when admission fails. */
    if (bootstrap_attempted)
        return 0;
    bootstrap_attempted = 1;
    if (tls != 89 || input || output)
        goto failed;
    input = getauxval(0xa001);
    output = getauxval(0xa002);
#ifdef NATIVE_SUSTAINED_V2
    /* Compare the complete native value before narrowing or wire effects.
     * Private epochs equal the native cohort; truncation is not admission. */
    long native_epoch = channel_raw(0x20005, 0, 0, 0);
    if (native_epoch < 1 || native_epoch > 65535)
        goto failed;
    generation = (unsigned)native_epoch;
#endif
#ifdef NATIVE_RUNNER_STARTUP
    struct ar_startup candidate;
    if (carrier) {
        unsigned char record[AR_CARRIER_SIZE];
        if (!startup || !input || !output || input == output ||
            !transfer(record, sizeof record, 0) ||
            !ar_decode(record, sizeof record, &candidate))
            goto failed;
    }
#endif
    unsigned char r[160];
    struct ar_roles roles;
    if (child || !input || !output || input == output ||
        !transfer(r, sizeof r, 0))
        goto failed;
#ifndef NATIVE_SUSTAINED_V2
    generation = (unsigned)channel_raw(0x20005, 0, 0, 0);
#endif
    if (!ar_roles_decode(r, sizeof r, generation, &roles))
        goto failed;
    const unsigned modes[4] = {2, 2, 1, 3};
    for (unsigned i = 0; i < 4; ++i) {
        refs[i] = roles.refs[i];
        fds[i] = i + 1;
        rights[i] = modes[i];
        live[i] = 1;
    }
#ifdef NATIVE_RUNNER_STARTUP
    if (carrier)
        *startup = candidate;
#endif
    tls++;
    return 1;
failed:
    poisoned = 1;
    return 0;
}
#ifdef NATIVE_RUNNER_STARTUP
int native_bootstrap(int child) { return bootstrap(child, NULL, 0); }
int native_runner_bootstrap(struct ar_startup *startup)
{
    return bootstrap(0, startup, 1);
}
#endif
static long file_io(unsigned long op, unsigned long fd, unsigned long ptr,
                    unsigned long count)
{
    if (op != 0 && op != 1 && op != 3 && op != 32 && op != 33)
        return -ENOSYS;
    unsigned i = 0;
    while (i < 4 && fds[i] != fd)
        i++;
    if (fd > INT_MAX || i == 4 || !live[i])
        return -EBADF;
    if (op == 3)
        live[i] = 0;
    if (poisoned)
        return -EIO;
    if (op == 32 || op == 33)
        return -ENOTSUP;
    if (op != 3) {
        if (!(rights[i] & (op == 0 ? 1 : 2)))
            return -EACCES;
        if (count > SSIZE_MAX)
            return -EINVAL;
        if (count && !ptr)
            return -EFAULT;
    }
    unsigned n = op == 3 ? 0 : count > 16 ? 16 : (unsigned)count;
    unsigned char q[32] = {0}, r[32];
    native_put(q, op == 0 ? 1 : op == 1 ? 2 : 3);
    native_put(q + 4, refs[i]);
    native_put(q + 8, (unsigned)fd);
    native_put(q + 12, n);
    if (op == 1 && n)
        memcpy(q + 16, (void *)ptr, n);
    if (!native_exchange(q, 32, r))
        return -EIO;
    int result = (int)native_word(r), bad = result < -4095 || result > (int)n;
    for (unsigned j = 4; j < 16; j++)
        if (r[j])
            bad = 1;
    unsigned start =
        op == 0 && result > 0 && result <= (int)n ? 16 + (unsigned)result : 16;
    for (unsigned j = start; j < 32; j++)
        if (r[j])
            bad = 1;
    if (bad || (op == 3 && result)) {
        poisoned = 1;
        return -EIO;
    }
    if (op == 0 && result > 0)
        memcpy((void *)ptr, r + 16, (unsigned)result);
    return result;
}
long __aether_io(unsigned long op, unsigned long fd, unsigned long ptr,
                 unsigned long n)
{
    int saved = errno;
    long r = file_io(op, fd, ptr, n);
    errno = saved;
    return r;
}
