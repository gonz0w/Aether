/* SPDX-License-Identifier: BSD-2-Clause */
static int stream_bootstrap(void)
{
    unsigned char b[32 + BINDINGS * 32];
#ifndef STREAM_IGNORE_CAPACITY
    const unsigned caps[4] = {512, 256, 6, 64};
#endif
    const unsigned modes[4] = {2, 2, 1, 3};
    input = getauxval(0xa001);
    output = getauxval(0xa002);
    if (!input || !output || input == output || !move(b, sizeof b, 0))
        return 0;
    unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    if (memcmp(b,
#if defined(RUNNER_DENIAL) || defined(RUNNER_SUCCESS)
               "AERIO001",
#else
               "AEOUT001",
#endif
               8) ||
        get(b, 8) != BINDINGS || get(b, 12) != gen)
        return 0;
    for (unsigned i = 16; i < 32; i++)
        if (b[i])
            return 0;
    for (unsigned j = 0; j < BINDINGS; j++) {
        unsigned at = 32 + j * 32;
        if (get(b, at) != j + 1 ||
            get(b, at + 4) != (j < 2 ? 0x75000000u + ((j + 1) << 16)
                                     : 0x71000000u + ((j - 2) << 16)) +
                                  gen ||
            get(b, at + 8) != j + 1 || get(b, at + 12) != modes[j]
#ifndef STREAM_IGNORE_CAPACITY
            || get(b, at + 16) != caps[j]
#endif
        )
            return 0;
#ifdef STREAM_EARLY
        refs[j] = get(b, at + 4);
        fds[j] = j + 1;
        rights[j] = modes[j];
        live[j] = 1;
#endif
        for (unsigned i = at + 20; i < at + 32; i++)
            if (b[i])
                return 0;
    }
    for (unsigned j = 0; j < BINDINGS; j++) {
        refs[j] = get(b, 36 + j * 32);
        fds[j] = j + 1;
        rights[j] = modes[j];
        live[j] = 1;
    }
    return 1;
}
