/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_ENTROPY_H
#define AETHER_ENTROPY_H
#include <stddef.h>
/* Private native grant API. Negative errno values; no POSIX errno mutation.
 * Authority is supplied by the owner, never inferred from a name or identity.
 */
long aether_entropy_draw(unsigned long grant, void *buffer, size_t count);
long aether_entropy_close(unsigned long grant);
#endif
