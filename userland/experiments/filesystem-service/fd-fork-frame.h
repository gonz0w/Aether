/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_FORK_FRAME_H
#define AETHER_FD_FORK_FRAME_H
#include "fd-startup.h"
#define AEFD_FORK_REQUEST_BYTES 304U
#define AEFD_FORK_RECEIPT_BYTES 32U
/* Inert borrowed bytes, never authenticated authority or an admitted context.
 */
struct aefd_fork_view {
    const unsigned char *raw;
    struct aether_fs_session_identity parent;
    uint64_t sequence;
};
/* 0 incomplete prefix, -1 incompatible, 1 exact compatible16-byte header.
 * Does not consume transport or authorize leaving a parked caller unresolved.
 */
int aefd_fork_header(const unsigned char *, size_t);
/* Complete request; out untouched on rejection. Native observations must be
 * authenticated externally. All input/output ranges valid and disjoint. */
int aefd_fork_decode(const unsigned char *, size_t, struct aefd_startup_auxv,
                     long pid, long parent_pid, struct aefd_fork_view *);
/* Encode from an immutable AEFDB001-shaped shell snapshot captured under the
 * whole context/owner gate. This does not capture live state. Supports exact
 * in-place conversion; other overlapping ranges are forbidden. On rejection
 * clears the exact304-byte output; wrong output length leaves it untouched. */
int aefd_fork_encode(unsigned char *, size_t, const unsigned char *, size_t,
                     struct aefd_startup_auxv, long pid, long parent_pid,
                     uint64_t sequence);
/* Pure proposed child correspondence check: both frames are revalidated.
 * Child preserves exact FD slots/flags, source labels and pipe histories; has
 * a fresh file generation and distinct actually observed copy-result grants.
 * This is not auxv/TLS repair, context reset or admission. Owner must agree the
 * exact retained-source-label relationship before selecting this profile. */
int aefd_fork_child_match(const unsigned char *request, size_t request_length,
                          struct aefd_startup_auxv parent, long parent_pid,
                          const unsigned char *startup, size_t startup_length,
                          struct aefd_startup_auxv child, long child_pid,
                          struct aether_fs_session_identity *out);
/* Caller owns a nonresetting counter per authenticated channel generation.
 * Reserve once before send; rejection after reservation never permits reuse.
 * Exhaustion leaves both values unchanged; counter/out must be disjoint. */
int aefd_fork_next(uint64_t *counter, uint64_t *out);
/* Parent disposition: requires actual native return, exact owner sequence and
 * canonical child PID or private errno. Raw thaw-11 alone proves no owner
 * error. Successful negative decode relies on authenticated settled no-child
 * owner disposition. Outputs unchanged on any malformed/partial/stale mismatch.
 */
int aefd_fork_parent_reply(const unsigned char *, size_t, uint64_t sequence,
                           int64_t native_result, int64_t *out);
/* Pure child context-ready codec. Calling this is not context construction or
 * sending readiness; only the future armed constructor may publish it. */
int aefd_fork_ready_encode(unsigned char *, size_t, uint64_t sequence,
                           long child_pid);
int aefd_fork_ready_decode(const unsigned char *, size_t, uint64_t sequence,
                           long child_pid);
#endif
