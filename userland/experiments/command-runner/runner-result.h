/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_RUNNER_RESULT_H
#define AETHER_RUNNER_RESULT_H
#include <stddef.h>
#include <stdint.h>
#ifdef NATIVE_SUSTAINED_V2
#define ar_admission ar_admission_sustained_v2
#define ar_collection ar_collection_sustained_v2
#define ar_terminal_exit ar_terminal_exit_sustained_v2
#endif
struct ar_reply {
    int32_t error;
    uint32_t receipt, detail, kind;
};
enum ar_reply_action {
    AR_REPLY_INVALID,
    AR_REPLY_ERROR,
    AR_REPLY_ADMITTED,
    AR_REPLY_PENDING,
    AR_REPLY_COLLECTED
};
/* Live disjoint caller storage; no retained pointer, transport or lifecycle
 * state. Invalid input leaves output unchanged: dispatch on the returned
 * action. Valid error replies carry no receipt. EAGAIN is pending only for
 * collection. These bytes do not prove authority, cleanup, reclaim or
 * permission to retry. */
enum ar_reply_action ar_admission(const unsigned char *record, size_t size,
                                  uint32_t generation, struct ar_reply *output);
enum ar_reply_action ar_collection(const unsigned char *record, size_t size,
                                   uint32_t receipt, struct ar_reply *output);
/* Use only after AR_REPLY_COLLECTED. cleanup_complete must be exactly 1.
 * Invalid/unrepresentable/abnormal facts map to 1; raw facts remain unchanged.
 * This is terminal policy, not local-action or precondition-error policy. */
unsigned ar_terminal_exit(const struct ar_reply *reply, int cleanup_complete);
#endif
