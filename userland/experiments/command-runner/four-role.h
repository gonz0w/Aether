/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FOUR_ROLE_H
#define AETHER_FOUR_ROLE_H
#include <stddef.h>
#include <stdint.h>
#ifdef NATIVE_SUSTAINED_V2
#define ar_roles_decode ar_roles_decode_sustained_v2
#endif
struct ar_roles {
    uint32_t refs[4];
};
int ar_roles_decode(const unsigned char *, size_t, uint32_t, struct ar_roles *);
#endif
