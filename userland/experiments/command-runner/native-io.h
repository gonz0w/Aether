/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef BYTECOUNT_NATIVE_IO_H
#define BYTECOUNT_NATIVE_IO_H
#include <stddef.h>
#ifdef NATIVE_SUSTAINED_V2
/* SUSTAINED.md: no automatic wire fallback or mixed-profile object links. */
#define native_word native_word_sustained_v2
#define native_put native_put_sustained_v2
#define native_bootstrap native_bootstrap_sustained_v2
#define native_runner_bootstrap native_runner_bootstrap_sustained_v2
#define native_exchange native_exchange_sustained_v2
#define native_ref native_ref_sustained_v2
#define native_generation native_generation_sustained_v2
#endif
unsigned native_word(const unsigned char *p);
void native_put(unsigned char *p, unsigned n);
/* One initialization attempt per connection. Failure poisons transport; a
 * repeated call after success rejects without revoking live bindings. */
int native_bootstrap(int child);
#ifdef NATIVE_RUNNER_STARTUP
#include "runner-parse.h"
/* Parent-only carrier entry; arguments publish only with validated bindings.
 * Shares the ordinary entry's single attempt. Failure leaves output unchanged.
 */
int native_runner_bootstrap(struct ar_startup *startup);
#endif
int native_exchange(unsigned char *request, unsigned size,
                    unsigned char reply[32]);
unsigned native_ref(unsigned index);
unsigned native_generation(void);
#endif
