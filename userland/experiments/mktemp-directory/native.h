/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_MKTEMP_NATIVE_H
#define AETHER_MKTEMP_NATIVE_H
#include "namespace.h"
#include <sys/uio.h>
#include <time.h>

/* Scalar receipts remain disjoint from Client/FD storage. Bits0..3 identify
 * namespace reader/writer and process reader/writer, in that order. A cached
 * negative close is never retried and never proves settlement. */
struct amk_native_receipt {
    int64_t status[4];
    uint32_t attempted, owned;
    int64_t failure;
    uint32_t terminal, reserved;
};
_Static_assert(sizeof(struct amk_native_receipt) == 56 &&
                   _Alignof(struct amk_native_receipt) == 8,
               "native receipt ABI");
_Static_assert(offsetof(struct amk_native_receipt, failure) == 40 &&
                   offsetof(struct amk_native_receipt, terminal) == 48,
               "native receipt offsets");
int64_t amk_native_initialize(const unsigned char *, uint64_t, uint64_t,
                              uint64_t, uint64_t, struct amk_bootstrap *);
int64_t amk_native_call(void *, uint64_t, uint64_t, uint64_t, uint64_t,
                        uint64_t);
int64_t amk_native_clock(void);
int64_t amk_native_verify(void *);
int64_t amk_native_finish_raw(struct amk_native_receipt *);
_Noreturn void amk_native_terminal(uint32_t);

/* This is the selected musl writev-call replacement, not a general writev ABI.
 * It preserves errno/-1 semantics, two vectors and confirmed partial prefixes.
 */
long amk_native_vector_write(int, const struct iovec *, int);
int amk_native_monotonic(clockid_t, struct timespec *);
int64_t amk_native_fd_start(uint64_t, uint64_t, uint64_t);
#endif
