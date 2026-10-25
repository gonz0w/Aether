/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_PRIVATE_CLOCK_H
#define AETHER_PRIVATE_CLOCK_H
#include <stdint.h>

/* Private BSP q35 profile; negative native errors, no errno mutation. */
long aether_clock_observe(unsigned long grant);
long aether_clock_park(unsigned long grant, volatile uint32_t *word,
                       unsigned long expected, unsigned long deadline_ns);
/* Maximum one second in the future; unexpected wake fails with -EIO. */
long aether_clock_sleep_until(unsigned long grant, unsigned long deadline_ns);
#endif
