/* SPDX-License-Identifier: BSD-2-Clause */
/* Independent carrier decoder/witness; private storage publishes only after
 * complete validation. All channel buffers are synchronous stack borrows.
 */
static int startup_probe(void)
{
    unsigned char record[224];
    char copied[6][32];
    input = getauxval(0xa001);
    output = getauxval(0xa002);
    if (!input || !output || input == output || !move(record, sizeof record, 0))
        return 0;
    unsigned count = get(record, 8);
    if (memcmp(record, "AERUN001", 8) || count < 1 || count > 6)
        return 0;
    for (unsigned i = 12; i < 32; i++)
        if (record[i])
            return 0;
    for (unsigned j = 0; j < 6; j++) {
        unsigned char *slot = record + 32 + j * 32;
        unsigned end = 0;
        while (end < 32 && slot[end])
            end++;
        if (j < count && end == 32)
            return 0;
        for (unsigned k = j < count ? end : 0; k < 32; k++)
            if (slot[k])
                return 0;
    }
    if (strcmp((char *)record + 32, "aether-run"))
        return 0;
    memcpy(copied, record + 32, sizeof copied);
    memset(record, 0xa5, sizeof record);
#ifdef WIDE_STARTUP
    int valid = count == 6 && !strcmp(copied[0], "aether-run") &&
                !strcmp(copied[1], "--") && !strcmp(copied[2], "bytecount") &&
                !strcmp(copied[3], "--decimal") && !strcmp(copied[4], "") &&
                !strcmp(copied[5], "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx");
#else
    int valid = count == 3 && !strcmp(copied[0], "aether-run") &&
                !strcmp(copied[1], "bytecount") &&
                !strcmp(copied[2], "--decimal");
#endif
#ifdef RUNNER_FORWARD
    if (valid) {
        memcpy(forwarded, copied, sizeof copied);
        forwarded_count = count;
    }
#endif
    return valid;
}
