// SPDX-License-Identifier: CDDL-1.0
/*
 * CDDL HEADER START
 *
 * The contents of this file are subject to the terms of the
 * Common Development and Distribution License (the "License").
 * You may not use this file except in compliance with the License.
 *
 * You can obtain a copy of the license at usr/src/OPENSOLARIS.LICENSE
 * or https://opensource.org/licenses/CDDL-1.0.
 * See the License for the specific language governing permissions
 * and limitations under the License.
 *
 * When distributing Covered Code, include this CDDL HEADER in each
 * file and include the License file at usr/src/OPENSOLARIS.LICENSE.
 * If applicable, add the following below this CDDL HEADER, with the
 * fields enclosed by brackets "[]" replaced with your own identifying
 * information: Portions Copyright [yyyy] [name of copyright owner]
 *
 * CDDL HEADER END
 */
/*
 * Copyright (c) 2005, 2010, Oracle and/or its affiliates. All rights reserved.
 * Copyright (c) 2012, 2018 by Delphix. All rights reserved.
 * Copyright (c) 2016 Actifio, Inc. All rights reserved.
 * Copyright (c) 2025, Klara, Inc.
 */

/* Private libzpool replacement. Init precedes workers; fini follows quiescence.
 * Every native draw is bounded and synchronous. Partial fills never succeed.
 * The bootstrap grant cannot be reopened after close in the same domain. */
static uintptr_t aether_random_grant;
const char *random_path = "/dev/random";
const char *urandom_path = "/dev/urandom";

static long aether_random_call(unsigned long op, uint8_t *ptr, size_t len)
{
    unsigned long grant = aether_random_grant;
    unsigned long address = (uintptr_t)ptr, count = len;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0;
    register unsigned long r9 __asm__("r9") = 0;
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+D"(grant), "+S"(address), "+d"(count),
                           "+r"(r10), "+r"(r8), "+r"(r9)
                         :
                         : "rcx", "r11", "cc", "memory");
    return (long)op;
}

void random_init(void)
{
    if (aether_random_grant)
        _Exit(125);
    aether_random_grant = getauxval(0xa002);
    if (!aether_random_grant)
        _Exit(125);
    uint8_t check[8];
    long result = aether_random_call(0x2b000, check, sizeof(check));
    for (size_t i = 0; i < sizeof(check); ++i)
        ((volatile uint8_t *)check)[i] = 0;
    if (result != (long)sizeof(check))
        _Exit(125);
}

void random_fini(void)
{
    if (!aether_random_grant)
        return;
    if (aether_random_call(0x2b001, NULL, 0) != 0)
        _Exit(125);
    aether_random_grant = 0;
}

static int aether_random_fill(uint8_t *ptr, size_t len)
{
    if (!aether_random_grant || len > 4096 ||
        (len && (!ptr || (uintptr_t)ptr > UINTPTR_MAX - len)))
        _Exit(125);
    while (len) {
        size_t count = len > 256 ? 256 : len;
        if (aether_random_call(0x2b000, ptr, count) != (long)count)
            _Exit(125);
        ptr += count;
        len -= count;
    }
    return 0;
}

int random_get_bytes(uint8_t *ptr, size_t len)
{
    return aether_random_fill(ptr, len);
}

int random_get_pseudo_bytes(uint8_t *ptr, size_t len)
{
    return aether_random_fill(ptr, len);
}
