/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_ZSH_PROCESS_H
#define AETHER_FD_ZSH_PROCESS_H
#include "fd-startup.h"
#ifndef AEFD_ZSH_PROCESS_BINDINGS
#error "Zsh process codec requires the selected process profile"
#endif
#define AEFD_ZSH_FORK_BYTES 368U
#define AEFD_ZSH_EXEC_BYTES 672U
/* Inert checked view. Endpoint/native identity authentication is the caller's
 * responsibility. Output publishes only after complete validation; no I/O,
 * pointer rebind, resource admission or authority follows from these bytes. */
struct aefd_zsh_snapshot {
    const unsigned char *raw;
    struct aether_fs_session_identity identity;
    uint64_t generation;
};
int aefd_zsh_snapshot_decode(const unsigned char *, size_t,
                             struct aefd_startup_auxv, long, long,
                             struct aefd_zsh_snapshot *);
/* Encoders permit disjoint input/output or exact in-place snapshot expansion.
 * Arguments may also already occupy their exact output field. Path inputs
 * and all decoded output records must be disjoint from
 * their output/input frame respectively. Invalid input leaves output untouched.
 * Fixed authenticated observations and exclusive valid C buffers are required;
 * these functions do not park/replay.
 */
int aefd_zsh_fork_encode(unsigned char *, size_t, const unsigned char[336],
                         struct aefd_startup_auxv, long, long, uint64_t);
int aefd_zsh_fork_decode(const unsigned char *, size_t,
                         struct aefd_startup_auxv, long, long, uint64_t,
                         struct aefd_zsh_snapshot *, uint64_t *);
int aefd_zsh_child_match(const unsigned char *, size_t,
                         struct aefd_startup_auxv, long,
                         const unsigned char[336], struct aefd_startup_auxv,
                         long, struct aefd_zsh_snapshot *);
int aefd_zsh_exec_encode(unsigned char *, size_t, const unsigned char[336],
                         struct aefd_startup_auxv, long, long, uint64_t,
                         const char *, const unsigned char[272]);
int aefd_zsh_exec_decode(const unsigned char *, size_t,
                         struct aefd_startup_auxv, long, long, uint64_t,
                         struct aefd_zsh_snapshot *, uint64_t *);
/* Only the three selected receipt kinds are admitted. Result policy (actual
 * copy PID, ready PID or negative refusal) remains with the typed caller. */
int aefd_zsh_receipt_encode(unsigned char[32], const char[8], uint64_t,
                            int64_t);
int aefd_zsh_receipt_decode(const unsigned char[32], const char[8], uint64_t,
                            int64_t *);
#endif
