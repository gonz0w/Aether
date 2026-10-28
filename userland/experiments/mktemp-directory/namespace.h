/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_MKTEMP_NAMESPACE_H
#define AETHER_MKTEMP_NAMESPACE_H
#include <stddef.h>
#include <stdint.h>

/* Private synchronous host-candidate ABI, not a wire or native constructor.
 * The opaque borrow exists only within entry. Never copy/dereference it from C,
 * retain it after entry, or reenter through an I/O callback. Callback state,
 * prefix and reports are valid stable disjoint caller storage for the whole
 * run. No callback may longjmp, unwind, retain buffers or escape the borrow.
 */
struct amk_namespace;
typedef int64_t (*amk_transfer_fn)(void *, uint32_t, unsigned char *, size_t);
typedef int64_t (*amk_wait_fn)(void *, uint32_t);
typedef void (*amk_close_fn)(void *, int64_t[2]);
typedef int32_t (*amk_entry_fn)(struct amk_namespace *, void *);
struct amk_io {
    void *state;
    amk_transfer_fn transfer;
    amk_wait_fn wait;
    amk_close_fn close;
};
struct amk_bootstrap {
    struct amk_io io;
    uint64_t epoch;
    const unsigned char *parent_prefix;
    size_t parent_prefix_length;
};
#define AMK_NOT_SENT 0u
#define AMK_REPORTED 1u
#define AMK_UNKNOWN 2u
#define AMK_COMPLETED_SUCCESS 3u
#define AMK_UNASSIGNED 0u
#define AMK_COMMITTED 1u
#define AMK_COMPLETED 2u
#define AMK_PROGRESS_UNKNOWN 3u
#define AMK_ABSENT 4u
#define AMK_ERROR_NONE 0u
#define AMK_ERROR_INVALID 1u
#define AMK_ERROR_CLOSED 2u
#define AMK_ERROR_FULL 3u
#define AMK_ERROR_PROTOCOL 4u
#define AMK_ERROR_TRANSPORT 5u
#define AMK_ERROR_REMOTE 6u
#define AMK_ADMISSION_NOT_STARTED 0u
#define AMK_PREFLIGHT_REJECTED 1u
#define AMK_GREETING_FAILED 2u
#define AMK_ADMITTED 3u
#define AMK_RUN_NOT_STARTED 0u
#define AMK_RUN_ADMISSION 1u
#define AMK_RUN_ENTRY 2u
#define AMK_RUN_FINISHED 3u
#define AMK_NOT_FINISHED 0u
#define AMK_FINISHED 1u
struct amk_mutation_result {
    uint32_t outcome, progress, error_kind, errno_value;
    int64_t error_value;
    uint64_t txg, bytes_staged;
};
struct amk_admission_result {
    uint32_t phase, error_kind;
    int64_t error_value;
    uint32_t errno_value, endpoints_accepted;
};
struct amk_finish_result {
    uint32_t phase, disconnect_attempted, error_kind, errno_value;
    int64_t error_value;
    uint32_t cleanup_present, cleanup_uncertain;
    int64_t reader_close, writer_close;
};
struct amk_run_result {
    uint32_t phase, command_status, final_status, reserved_zero;
    struct amk_admission_result admission;
    struct amk_mutation_result mutation;
    struct amk_finish_result finalization;
};
/* The caller initializes/checks full argv and prefix correspondence separately.
 * Preflight rejection does not consume endpoints. Once accepted, failed
 * greeting consumes both closes once. Home15 is the sole parent; no pathname
 * resolver. A normal callback return0..255 is command status, not this
 * function's return. Return0 means adapter execution completed; negative errno
 * means admission or adapter failure. Final command status remains observable
 * in out independently.
 */
int32_t amk_with_namespace(const struct amk_bootstrap *, amk_entry_fn, void *,
                           struct amk_run_result *out);
/* One valid mkdir0700 invocation; invalid local input has no effect. Initialize
 * every out. Return negative errno without modifying libc errno; C projects it.
 * The first dispatched progress record remains in the run report thereafter.
 */
int32_t amk_mkdir(struct amk_namespace *, const unsigned char *, size_t,
                  uint32_t mode, struct amk_mutation_result *out);
/* Active client: real disconnect ACK then raw closes. Retired client: cached
 * local receipt, no further request. Repeated finish is inert/cached. No
 * export, quiescence or reclaim claim. Before terminal _exit, finish while
 * borrow valid, record command/final status in caller out, CLEAR the C TLS
 * borrow, then exit. Never rely on Rust Drop after terminal exit or longjmp
 * across the Rust frame.
 */
int32_t amk_finish(struct amk_namespace *, struct amk_finish_result *out);

_Static_assert(sizeof(void *) == 8 && sizeof(size_t) == 8,
               "selected 64-bit ABI");
_Static_assert(sizeof(struct amk_io) == 32 && _Alignof(struct amk_io) == 8,
               "io ABI");
_Static_assert(sizeof(struct amk_bootstrap) == 56 &&
                   _Alignof(struct amk_bootstrap) == 8,
               "bootstrap ABI");
_Static_assert(offsetof(struct amk_bootstrap, epoch) == 32 &&
                   offsetof(struct amk_bootstrap, parent_prefix) == 40 &&
                   offsetof(struct amk_bootstrap, parent_prefix_length) == 48,
               "bootstrap offsets");
_Static_assert(sizeof(struct amk_mutation_result) == 40 &&
                   _Alignof(struct amk_mutation_result) == 8,
               "mutation ABI");
_Static_assert(offsetof(struct amk_mutation_result, error_value) == 16 &&
                   offsetof(struct amk_mutation_result, txg) == 24 &&
                   offsetof(struct amk_mutation_result, bytes_staged) == 32,
               "mutation offsets");
_Static_assert(sizeof(struct amk_admission_result) == 24 &&
                   _Alignof(struct amk_admission_result) == 8,
               "admission ABI");
_Static_assert(offsetof(struct amk_admission_result, error_value) == 8 &&
                   offsetof(struct amk_admission_result, errno_value) == 16,
               "admission offsets");
_Static_assert(sizeof(struct amk_finish_result) == 48 &&
                   _Alignof(struct amk_finish_result) == 8,
               "finish ABI");
_Static_assert(offsetof(struct amk_finish_result, error_value) == 16 &&
                   offsetof(struct amk_finish_result, cleanup_present) == 24 &&
                   offsetof(struct amk_finish_result, reader_close) == 32 &&
                   offsetof(struct amk_finish_result, writer_close) == 40,
               "finish offsets");
_Static_assert(sizeof(struct amk_run_result) == 128 &&
                   _Alignof(struct amk_run_result) == 8,
               "run ABI");
_Static_assert(offsetof(struct amk_run_result, admission) == 16 &&
                   offsetof(struct amk_run_result, mutation) == 40 &&
                   offsetof(struct amk_run_result, finalization) == 80,
               "run offsets");
#endif
