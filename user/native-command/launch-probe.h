/* SPDX-License-Identifier: BSD-2-Clause */
/* Complete-frame rejection corpus. Offsets are wire bytes, not native Args
 * slots. Each request starts fresh, and only one region is changed per case.
 */
static int launch_probe(void)
{
    static const struct {
        unsigned offset, length;
        unsigned char value;
        int error;
    } cases[] = {
        {4, 1, 2, EINVAL},      /* unsupported version */
        {8, 4, 0, EINVAL},      /* argc zero */
        {8, 4, 0xff, EINVAL},   /* argc overflow boundary */
        {12, 1, 2, EINVAL},     /* envc over bound */
        {12, 4, 0xff, EINVAL},  /* envc overflow boundary */
        {16, 1, 1, EINVAL},     /* wrong binding count */
        {20, 1, 1, EINVAL},     /* header reserved start */
        {31, 1, 1, EINVAL},     /* header reserved end */
        {63, 1, 1, ENOENT},     /* command-name padding */
        {80, 1, 1, EINVAL},     /* first entry reserved start */
        {95, 1, 1, EINVAL},     /* first entry reserved end */
        {112, 1, 1, EINVAL},    /* second entry reserved start */
        {127, 1, 1, EINVAL},    /* second entry reserved end */
        {128, 32, 'X', EINVAL}, /* unterminated argv[0] */
        {159, 1, 1, EINVAL},    /* argv[0] padding */
        {160, 32, 'X', EINVAL}, /* unterminated argv[1] */
        {191, 1, 1, EINVAL},    /* argv[1] padding */
        {192, 1, 'X', EINVAL},  /* environment allowlist */
        {192, 32, 'X', EINVAL}, /* unterminated environment */
        {223, 1, 1, EINVAL},    /* environment padding */
        {224, 1, 1, EINVAL},    /* first unused slot */
        {383, 1, 1, EINVAL},    /* final unused byte */
    };
    unsigned char frame[384];
    for (unsigned i = 0; i < sizeof cases / sizeof cases[0]; i++) {
        request(frame);
        memset(frame + cases[i].offset, cases[i].value, cases[i].length);
        if (!exchange(frame, sizeof frame) ||
            (int)get(frame, 0) != -cases[i].error)
            return 0;
        for (unsigned j = 4; j < 32; j++)
            if (frame[j])
                return 0;
    }
    return 1;
}
