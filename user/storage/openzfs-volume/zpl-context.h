/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_ZPL_CONTEXT_H
#define AETHER_ZPL_CONTEXT_H
#include "zpl-read.h"
/* Exclusive original view/SPA borrow, no concurrent namespace mutation/export.
 * Root and target identities come only from enforcing service handles. Outputs
 * are initialized/disjoint, path has256 bytes; no pointer/ownership escapes.
 * Success returns an actual root-relative physical path including NUL and its
 * checked parent node. Errors publish no partial path or identity. */
int aether_zpl_context(aether_zpl_view *, uint64_t, uint64_t, uint64_t,
                       uint64_t, unsigned char *, size_t *, aether_zpl_node *);
#endif
