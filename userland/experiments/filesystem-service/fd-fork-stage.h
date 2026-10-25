/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_FORK_STAGE_H
#define AETHER_FD_FORK_STAGE_H
#include "fd-fork-frame.h"
#define AEFD_FORK_IDLE 0
#define AEFD_FORK_ARMED 1
#define AEFD_FORK_CHILD 2
#define AEFD_FORK_READY 3
#define AEFD_FORK_FAILED 4
#define AEFD_FORK_SENDING 5
#define AEFD_FORK_PARENT 6
/* One stable aggregate, boot first. No move/copy/reinitialization after
 * startup; only actual native copy followed by the armed child constructor is
 * supported. Scratch/request storage is reused, never a second admitted
 * context/ledger. */
struct aefd_fork {
    struct aefd_startup boot;
    struct aefd_startup_auxv parent;
    uint64_t counter, sequence, previous_mask;
    long parent_pid;
    aefd_native_call call;
    void *owner;
    unsigned budget;
    int phase;
    int64_t status;
};
/* Host injection is qualification-only. Production uses pinned copy_rebind,
 * native auxv observations/probes and upstream __post_Fork TID/list repair.
 * Rebind must validate old auxv/TLS and update exactly the three native grants.
 */
typedef int (*aefd_fork_rebind)(void *, struct aefd_startup_auxv parent,
                                struct aefd_startup_auxv child);
/* Parent: mask whole snapshot/send; leave guard held on success. The caller
 * must perform exactly one actual native park next. FAILED requires direct
 * fail-stop; never return it as a known no-child errno or call libc finish. */
int64_t aefd_fork_arm(struct aefd_fork *, struct aefd_startup_auxv);
/* Actual positive native child result or raw thaw-11; consumes one correlated
 * owner disposition. IDLE result may return upstream; FAILED must fail-stop. */
int64_t aefd_fork_parent(struct aefd_fork *, int64_t native_result);
/* Only after actual native child return0. Quarantines copied context BEFORE
 * callbacks; never leaves/closes inherited parent borrows. Any failure requires
 * direct fail-stop, with raw new-channel cleanup receipts in boot.closed.
 * A second call cannot consume startup or erase/close an admitted context. */
int64_t aefd_fork_child(struct aefd_fork *, struct aefd_startup_auxv grants,
                        aefd_fork_rebind, void *);
/* Optional binding/native entry, selected only with AEFD_FORK_BINDINGS. */
struct aefd_fork *aefd_shell_fork_context(void);
long __aether_fork_stage(void);
/* CRT-initialized TLS invariant; validation never repairs copied TLS. */
int aefd_fork_tls_valid(void);
#endif
