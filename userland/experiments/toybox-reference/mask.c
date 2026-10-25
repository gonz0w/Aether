// SPDX-License-Identifier: BSD-2-Clause
#include "mask.h"

int tm_init(struct tm_state *s, uint32_t generation, uint32_t initial)
{
    if (!s || s->attempted)
        return 0;
    s->attempted = 1;
    if (!generation || initial > 0777u)
        return 0;
    s->generation = generation;
    s->mask = initial;
    s->live = 1;
    return 1;
}
int tm_exchange(struct tm_state *s, uint32_t generation, uint32_t requested,
                uint32_t *previous)
{
    if (!s || !s->attempted || !s->live || !previous ||
        generation != s->generation)
        return 0;
    *previous = s->mask;
    s->mask = requested & 0777u;
    return 1;
}
int tm_retire(struct tm_state *s, uint32_t generation)
{
    if (!s || !s->live || generation != s->generation)
        return 0;
    s->live = 0;
    s->mask = 0;
    return 1;
}
