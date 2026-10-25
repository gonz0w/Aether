/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_ZPL_READ_H
#define AETHER_ZPL_READ_H

#include <stddef.h>
#include <stdint.h>

struct spa;
typedef struct aether_zpl_view aether_zpl_view;

typedef struct aether_zpl_node {
    uint64_t object;
    uint64_t generation;
    uint64_t size;
    uint64_t mode;
} aether_zpl_node;

/* Private engine-owner FFI, NOT a client/capability API. The configured name
 * and raw object identities must never come directly from untrusted clients.
 * Serialized calls only. SPA stays borrowed through close; no concurrent
 * mutation/export/teardown. All pointers must be valid, and output storage
 * must not alias the context, names or other arguments. Positive errno results.
 * open owns one objset and small context; close consumes/nulls that context.
 * Nodes are copied scalars, never permission tokens. No pointer survives read.
 */
int aether_zpl_open(struct spa *, const char *, aether_zpl_view **);
void aether_zpl_close(aether_zpl_view **);
int aether_zpl_root(aether_zpl_view *, aether_zpl_node *);
int aether_zpl_lookup(aether_zpl_view *, uint64_t directory,
                      uint64_t generation, const unsigned char *name,
                      size_t length, aether_zpl_node *);
/* Buffer holds length writable bytes (0..4096); count is always initialized.
 * On error with valid arguments the entire requested buffer is zeroed.
 * On success count describes bytes only, not any durability acknowledgment. */
int aether_zpl_read(aether_zpl_view *, uint64_t object, uint64_t generation,
                    uint64_t offset, void *buffer, size_t length,
                    size_t *count);

#endif
