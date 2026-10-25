/* SPDX-License-Identifier: BSD-2-Clause */
/* Descriptions report owner-validated inherited stdin/stderr holdings. */
static int standard_description(unsigned binding)
{
    unsigned char frame[16];
    unsigned access = binding == 0 ? 1 : 2;
    unsigned capacity = binding == 0 ? 10 : 32;
    if (!move(frame, sizeof frame, 0) ||
        get(frame, 0) != (0x7a000000U | (binding << 16) | generation) ||
        get(frame, 4) != binding || get(frame, 8) != access ||
        get(frame, 12) != capacity)
        return 0;
    refs[binding] = get(frame, 0);
    fds[binding] = binding;
    rights[binding] = access;
    return 1;
}
