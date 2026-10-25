/* SPDX-License-Identifier: BSD-2-Clause */
/* Private musl conformance backend; no production SDK adoption. */
#include <time.h>
int aether_monotonic_wait(volatile int *, int, clockid_t,
                          const struct timespec *, int);
long aether_sleep_syscall(long, long, long, long, long);
int aether_sleep_probe(void);
