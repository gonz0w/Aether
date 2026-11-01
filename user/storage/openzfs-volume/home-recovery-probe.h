/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_HOME_RECOVERY_PROBE_H
#define AETHER_HOME_RECOVERY_PROBE_H
#include <stdint.h>
#include <sys/spa.h>
/* Private fixed AF09 read-only oracle. The initial thread exclusively borrows
 * a live fresh read-only SPA; no concurrent/reentrant mutation, export or
 * teardown. digest32 is live/disjoint writable storage for32 bytes, retained by
 * the caller. No pointer escapes. Output is zero on failure. utc_min is
 * inclusive and utc_max exclusive, seconds from the selected enforced
 * RuntimeUtc window. Success checks the fixed namespace/data and returns
 * canonical preserved- metadata SHA256. A prospective qualifier must compare
 * all32 digest bytes from pristine and recovery readers; this function does not
 * authorize reclamation, make a durability claim or emit output. Compile
 * instead of separate zpl-read.c. expectation is a closed internal integer:
 * 0 requires the pristine namespace/home absence; 1 requires the recovered
 *16-byte AF09-HOME-WRITE payload/EOF; 2 requires recovered probe size0 and
 * an actual nonzero-length read returning EOF. Modes0/1 keep their existing
 * meaning. Mode2 is selected only from the approved drain profile; it grants
 * no new input, writer or native authority. Unknown modes reject before I/O.
 */
int aether_home_readback(spa_t *, int expectation, uint64_t utc_min,
                         uint64_t utc_max, unsigned char digest32[32]);
/* Separate private mktemp oracle. Same exclusive read-only SPA borrow and
 * inclusive/exclusive UTC window as above; recovered is exactly 0 or 1.
 * result40 is caller-owned, live, disjoint writable storage for 40 bytes.
 * Failure zeros all 40 bytes. Pristine returns preserved digest32 + zero leaf8;
 * recovery returns preserved digest32 + the actual eight-byte generated leaf.
 * These are candidate bytes only: the importing caller must withhold external
 * publication until read-only SPA close/disown/eviction and all later runtime,
 * TLS, resource and phase-health checks succeed. Readers never spa_export.
 */
int aether_home_mktemp_readback(spa_t *, int recovered, uint64_t utc_min,
                                uint64_t utc_max, unsigned char result40[40]);
#endif
