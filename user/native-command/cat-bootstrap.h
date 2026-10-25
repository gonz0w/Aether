/* SPDX-License-Identifier: BSD-2-Clause */
#ifdef STARTUP_IDENTITY
static unsigned startup_ids[4];
#endif
#ifdef STARTUP_CWD
static unsigned startup_directory;
#endif
#ifdef STARTUP_FILES
static unsigned startup_root;
#endif
#ifdef STARTUP_QUEUED_BODY
static int startup_queued_witness;
#endif
static int cat_bootstrap(void)
{
#ifdef STARTUP_FILES
    unsigned char b[224];
#elif defined(STARTUP_IDENTITY)
#ifdef STARTUP_CWD
    unsigned char b[192];
#else
    unsigned char b[160];
#endif
#else
    unsigned char b[128];
#endif
    input = getauxval(0xa001);
    output = getauxval(0xa002);
    if (!input || !output || input == output || !move(b, 32, 0))
        return 0;
#ifdef STARTUP_QUEUED_BODY
    /* Header consumption empties the queue before the owner's atomic body write.
     * Read only its first byte: version rejection must leave the other 15 unread. */
    unsigned char witness[32] = {0};
    memcpy(witness, "AEQUEUE1", 8);
    unsigned witness_gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    put(witness, 8, witness_gen);
    if (!move(witness, 32, 1) || !move(witness, 1, 0) ||
        witness[0] != (unsigned char)(0xa0 + witness_gen))
        return 0;
    startup_queued_witness = 1;
#endif
#ifdef STARTUP_FILES
    if (memcmp(b, "AECAT004", 8))
        return 0;
#elif defined(STARTUP_IDENTITY)
#ifdef STARTUP_CWD
    if (memcmp(b, "AECAT003", 8))
#else
    if (memcmp(b, "AECAT002", 8))
#endif
        return 0;
#else
    if (memcmp(b, "AECAT001", 8))
        return 0;
#endif
    if (!move(b + 32, sizeof b - 32, 0))
        return 0;
    unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    if (get(b, 8) != 3 || get(b, 12) != gen)
        return 0;
    for (unsigned j = 16; j < 32; j++)
        if (b[j])
            return 0;
    for (unsigned j = 0; j < 3; j++) {
        unsigned at = 32 + j * 32;
        if (get(b, at) != j + 1 ||
            get(b, at + 4) != 0x76000000u + (j << 16) + gen ||
            get(b, at + 8) != j || get(b, at + 12) != (j ? 2u : 1u) ||
            get(b, at + 16) != (j == 2 ? 256u : 32u))
            return 0;
        for (unsigned k = at + 20; k < at + 32; k++)
            if (b[k])
                return 0;
#ifdef CAT_EARLY
        refs[j] = get(b, at + 4);
        fds[j] = j;
        rights[j] = j ? 2 : 1;
        live[j] = 1;
#endif
    }
#ifdef STARTUP_IDENTITY
    if (get(b, 144) != 1 || get(b, 148) || get(b, 152) || get(b, 156))
        return 0;
    for (unsigned j = 0; j < 4; j++)
        if (get(b, 128 + j * 4) == UINT_MAX)
            return 0;
#ifdef STARTUP_CWD
    if (!get(b, 160) || get(b, 164) != 1 || get(b, 168) != 1 ||
        get(b, 172) != gen)
        return 0;
    for (unsigned j = 176; j < 192; j++)
        if (b[j])
            return 0;
    for (unsigned j = 0; j < 3; j++)
        if (get(b, 160) == get(b, 36 + j * 32))
            return 0;
#ifdef STARTUP_FILES
#ifdef STARTUP_FILES_EARLY
    startup_root = get(b, 192); /* Negative control: publish before late validation. */
#endif
    if (gen == 0 || gen > 255 || get(b, 192) != 0x76040000u + gen ||
        get(b, 196) != 1 || get(b, 200) != 1 || get(b, 204) != gen)
        return 0;
    for (unsigned j = 208; j < 224; j++)
        if (b[j])
            return 0;
    if (get(b, 192) == get(b, 160))
        return 0;
#ifndef STARTUP_FILES_SKIP
    startup_root = get(b, 192);
#endif
#endif
#ifndef STARTUP_CWD_SKIP
    startup_directory = get(b, 160);
#endif
#endif
#ifndef STARTUP_IDENTITY_SKIP
    for (unsigned j = 0; j < 4; j++)
        startup_ids[j] = get(b, 128 + j * 4);
#endif
#endif
    for (unsigned j = 0; j < 3; j++) {
        refs[j] = get(b, 36 + j * 32);
        fds[j] = j;
        rights[j] = j ? 2 : 1;
        live[j] = 1;
    }
    return 1;
}
