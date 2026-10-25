// SPDX-License-Identifier: BSD-2-Clause
#include "mask.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void)
{
    const uint32_t high[] = {0, 01000u, 0x80000000u, 0xfffffe00u};
    unsigned cases = 0;
    for (uint32_t initial = 0; initial < 512; initial++)
        for (uint32_t low = 0; low < 512; low++)
            for (unsigned h = 0; h < 4; h++) {
                struct tm_state a = {0}, b = {0};
                assert(tm_init(&a, 41, initial) && tm_init(&b, 42, 0077));
                struct tm_state isolated = b;
                uint32_t previous = UINT32_MAX;
                uint32_t requested = high[h] | low;
                assert(tm_exchange(&a, 41, requested, &previous));
                assert(previous == initial && a.mask == requested % 512);
                assert(!memcmp(&b, &isolated, sizeof(b)));
                // Toybox's save/clear/restore sequence.
                uint32_t saved, zero;
                assert(tm_exchange(&a, 41, 0, &saved));
                assert(saved == low && a.mask == 0);
                assert(tm_exchange(&a, 41, saved, &zero));
                assert(zero == 0 && a.mask == low);
                struct tm_state before = a;
                previous = UINT32_MAX;
                assert(!tm_exchange(&a, 42, 0, &previous));
                assert(previous == UINT32_MAX &&
                       !memcmp(&a, &before, sizeof(a)));
                assert(!tm_retire(&a, 42));
                assert(!tm_init(&a, 43, 0) && !memcmp(&a, &before, sizeof(a)));
                assert(tm_retire(&a, 41) && !a.live && !a.mask);
                before = a;
                assert(!tm_exchange(&a, 41, 0, &previous));
                assert(!tm_retire(&a, 41) && !tm_init(&a, 43, 0));
                assert(previous == UINT32_MAX &&
                       !memcmp(&a, &before, sizeof(a)));
                struct tm_state fresh = {0};
                assert(tm_init(&fresh, 43, 0077));
                assert(!tm_exchange(&fresh, 41, 0, &previous));
                assert(tm_exchange(&fresh, 43, 0, &previous) &&
                       previous == 0077);
                assert(!memcmp(&b, &isolated, sizeof(b)));
                cases++;
            }
    uint32_t sentinel = UINT32_MAX;
    struct tm_state blank = {0};
    assert(!tm_exchange(&blank, 1, 0, &sentinel) && sentinel == UINT32_MAX);
    assert(!tm_retire(&blank, 1) && !blank.attempted);
    for (unsigned n = 0; n < 2; n++) {
        struct tm_state s = {0};
        assert(!tm_init(&s, n ? 1 : 0, n ? 01000 : 0));
        assert(s.attempted && !s.live && !s.mask && !s.generation);
        assert(!tm_init(&s, 1, 0077));
        assert(!tm_exchange(&s, 1, 0, &sentinel) && sentinel == UINT32_MAX);
    }
    assert(!tm_init(NULL, 1, 0));
    assert(!tm_exchange(NULL, 1, 0, &sentinel));
    assert(!tm_retire(NULL, 1));
    assert(tm_init(&blank, 1, 0077));
    struct tm_state before = blank;
    assert(!tm_exchange(&blank, 1, 0, NULL));
    assert(!memcmp(&blank, &before, sizeof(blank)));
    printf("PASS: %u mask scenarios and boundary controls\n", cases);
    return 0;
}
