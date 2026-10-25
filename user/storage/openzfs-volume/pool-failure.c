/* SPDX-License-Identifier: BSD-2-Clause */
/* Private diagnostic only: never query resources on a resource failure path.
 * The existing admitted stdout call owns validation/capacity. Failure to record
 * a site leaves the original failure intact; no retry, allocation or locks. */
#include "pthread_impl.h"
#include <stdint.h>

unsigned aether_pool_failure_tid(void) {
  /* Compile against the selected runtime's exact musl TLS layout. */
  return (unsigned)__pthread_self()->tid;
}

void aether_pool_failure_site(unsigned site) {
  unsigned char row[8] = {(unsigned char)site, 0, 0, 0, 0, 0, 0, 0};
  unsigned long operation = 0x10000 + 1;
  register unsigned long r10 __asm__("r10") = 0;
  register unsigned long r8 __asm__("r8") = 0;
  register unsigned long r9 __asm__("r9") = 0;
  __asm__ __volatile__("int $0x81"
                       : "+a"(operation), "+r"(r10), "+r"(r8), "+r"(r9)
                       : "D"(1UL), "S"((uintptr_t)row), "d"(sizeof(row))
                       : "rcx", "r11", "cc", "memory");
}

void aether_pool_failure_allocation(unsigned site, unsigned long long size,
                                    unsigned error) {
  aether_pool_failure_site(site);
  /* Exact failed request and return/errno bits, not resource availability.
   * At creation: 15 phase rows +13 diagnostic rows fit32/256 bytes. */
  for (unsigned i = 0; i < 8; ++i)
    aether_pool_failure_site((size >> (8 * i)) & 255);
  for (unsigned i = 0; i < 4; ++i)
    aether_pool_failure_site((error >> (8 * i)) & 255);
}

void aether_pool_failure_assertion(unsigned line, unsigned long long caller) {
  /* Caller captures its own original return address without walking a stack.
   * It is diagnostic data only; neither value is dereferenced or retried. */
  aether_pool_failure_site(65);
  for (unsigned i = 0; i < 4; ++i)
    aether_pool_failure_site((line >> (8 * i)) & 255);
  for (unsigned i = 0; i < 8; ++i)
    aether_pool_failure_site((caller >> (8 * i)) & 255);
}

void aether_pool_failure_denial(unsigned stage, long error, unsigned value,
                                unsigned tid) {
  /* Invalid sentinels reject attribution without altering the original return.
   * No observer state: concurrent or repeated events must fail host decoding.
   */
  unsigned valid = error >= -32767 && error <= 32767 && error != 0 &&
                   value <= 65535 && tid != 0;
  unsigned bits = valid ? (unsigned)((uint16_t)error) : 0;
  aether_pool_failure_site(120);
  aether_pool_failure_site(valid ? stage : 0);
  for (unsigned i = 0; i < 2; ++i)
    aether_pool_failure_site((bits >> (8 * i)) & 255);
  for (unsigned i = 0; i < 2; ++i)
    aether_pool_failure_site((value >> (8 * i)) & 255);
  for (unsigned i = 0; i < 4; ++i)
    aether_pool_failure_site((tid >> (8 * i)) & 255);
}

void aether_pool_failure_pthread(unsigned long long error, unsigned tid) {
  /* Trusted VERIFY0 captures pthread's original positive int errno, once.
   * Negative/unrepresentable values are invalid, never silently truncated. */
  unsigned bits = error > 0 && error <= 32767 ? (unsigned)error : 0;
  aether_pool_failure_site(66);
  for (unsigned i = 0; i < 2; ++i)
    aether_pool_failure_site((bits >> (8 * i)) & 255);
  for (unsigned i = 0; i < 4; ++i)
    aether_pool_failure_site((tid >> (8 * i)) & 255);
}
