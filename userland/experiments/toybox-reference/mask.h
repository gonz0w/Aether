// SPDX-License-Identifier: BSD-2-Clause
#ifndef TOYBOX_MASK_H
#define TOYBOX_MASK_H
#include <stdint.h>
struct tm_state {
    unsigned attempted, live;
    uint32_t generation, mask;
};
/* Private synchronous host candidate. Zeroed process-owned context, no aliases
 * to output storage and no external state mutation. Initial mask/generation
 * must come from accepted startup policy; integers do not confer authority.
 * Failed initialization consumes its attempt. New process means new context.
 * No thread safety, native syscall interception or creation-mode application.
 */
int tm_init(struct tm_state *, uint32_t generation, uint32_t initial);
int tm_exchange(struct tm_state *, uint32_t generation, uint32_t requested,
                uint32_t *previous);
int tm_retire(struct tm_state *, uint32_t generation);
#endif
