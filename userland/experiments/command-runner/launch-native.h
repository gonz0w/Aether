/* SPDX-License-Identifier: BSD-2-Clause */
/* Opt-in consumer witnesses for the pinned owner's launch rejection contract.
 */
#ifdef LAUNCH_CORPUS
static int launch_corpus(void)
{
    /* Wire field boundaries from the owner contract; errno must match exactly.
     */
    static const struct {
        unsigned offset, length;
        unsigned char value;
        int error;
    } cases[] = {
        {4, 1, 2, EINVAL},      {8, 4, 0, EINVAL},      {8, 4, 255, EINVAL},
        {12, 1, 2, EINVAL},     {12, 4, 255, EINVAL},   {16, 1, 1, EINVAL},
        {20, 1, 1, EINVAL},     {31, 1, 1, EINVAL},     {63, 1, 1, ENOENT},
        {80, 1, 1, EINVAL},     {95, 1, 1, EINVAL},     {112, 1, 1, EINVAL},
        {127, 1, 1, EINVAL},    {128, 32, 'X', EINVAL}, {159, 1, 1, EINVAL},
        {160, 32, 'X', EINVAL}, {191, 1, 1, EINVAL},    {192, 1, 'X', EINVAL},
        {192, 32, 'X', EINVAL}, {223, 1, 1, EINVAL},    {224, 1, 1, EINVAL},
        {383, 1, 1, EINVAL},
    };
    unsigned char q[384], r[32];
    for (unsigned i = 0; i < sizeof cases / sizeof cases[0]; ++i) {
        request(q);
        memset(q + cases[i].offset, cases[i].value, cases[i].length);
        if (send(q, sizeof q, r) != -cases[i].error)
            return 0;
        for (unsigned j = 4; j < sizeof r; ++j)
            if (r[j])
                return 0;
    }
    return 1;
}
#endif
#ifdef LAUNCH_PREFIX
#include <sys/auxv.h>
static int prefix_move(unsigned long grant, unsigned char *bytes, unsigned size,
                       int writing)
{
    unsigned used = 0;
    for (unsigned turn = 0; turn < 100000 && used < size; ++turn) {
        unsigned count = size - used;
        if (count > 7)
            count = 7;
        long n = channel_raw(writing ? 0x24002 : 0x24001, grant,
                             (unsigned long)(bytes + used), count);
        if (n == -EAGAIN) {
            channel_yield();
            continue;
        }
        if (n <= 0 || (unsigned long)n > count)
            return 0;
        used += (unsigned)n;
    }
    return used == size;
}
static int launch_prefix(void)
{
    unsigned char q[384];
    request(q);
    unsigned long output = getauxval(0xa002), input = getauxval(0xa001);
    if (!prefix_move(output, q, LAUNCH_PREFIX, 1))
        return 106;
    if (channel_raw(0x24003, output, 0, 0))
        return 107;
    for (unsigned turn = 0; turn < 100000; ++turn) {
        long n = channel_raw(0x24001, input, (unsigned long)q, 1);
        if (n > 0) {
            /* Drain the forbidden reply before exit to avoid teardown races. */
            if (n != 1 || !prefix_move(input, q + 1, 31, 0))
                return 109;
            return 104;
        }
        if (n != -EAGAIN)
            return 108;
        channel_yield();
    }
    return 105;
}
#endif
