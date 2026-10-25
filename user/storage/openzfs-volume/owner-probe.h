/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_NAMESPACE_OWNER_PROBE_H
#define AETHER_NAMESPACE_OWNER_PROBE_H
#include <stddef.h>
struct spa;
/* Private synchronous probe only. SPA stays borrowed, hash is the caller's
 * initialized writable SHA2_CTX and both remain valid/nonaliasing until return.
 * Rust owns/closes every ZPL context before return; neither pointer escapes.
 * No client-provided pointers, reentry, callbacks or unwind through C. */
int aether_namespace_owner_probe(struct spa *, void *hash);
int aether_namespace_hash_update(void *hash, const unsigned char *, size_t);
#endif
