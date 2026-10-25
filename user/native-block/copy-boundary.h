/* SPDX-License-Identifier: BSD-2-Clause */
/* One admitted owner executes this witness. CALL is its existing scalar trap.
 * The input is a synchronous 512-byte borrow; no pointer survives this call. */
static _Alignas(4096) unsigned char boundary_pages[8192];
static int block_copy_boundary(unsigned long sector,
                               const unsigned char reference[512],
                               int write_allowed)
{
    unsigned char *crossing = boundary_pages + 4095;
    crossing[-1] = 0x5a;
    crossing[512] = 0x5a;
    for (unsigned i = 0; i < 512; ++i)
        crossing[i] = 0x5a;
    if (CALL(0x27000, sector, crossing, 512) != 512)
        return 0;
    for (unsigned i = 0; i < 512; ++i)
        if (crossing[i] != reference[i])
            return 0;
    if (crossing[-1] != 0x5a || crossing[512] != 0x5a)
        return 0;
    if (CALL(0x27001, sector, crossing, 512) != (write_allowed ? 512 : -13))
        return 0;
    volatile unsigned char *edge = (volatile unsigned char *)0x0800ffffUL;
    *edge = 0x5a;
    if (CALL(0x27000, sector, edge, 512) != -14 || *edge != 0x5a ||
        CALL(0x27000, sector, getauxval(3), 512) != -14 ||
        CALL(0x27001, sector, edge, 512) != (write_allowed ? -14 : -13))
        return 0;
    if (*edge != 0x5a || CALL(0x27000, sector, crossing, 512) != 512)
        return 0;
    for (unsigned i = 0; i < 512; ++i)
        if (crossing[i] != reference[i])
            return 0;
    return crossing[-1] == 0x5a && crossing[512] == 0x5a;
}
