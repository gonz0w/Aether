/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_RUNNER_PARSE_H
#define AETHER_RUNNER_PARSE_H
#include <stddef.h>
#include <stdint.h>
#define AR_CARRIER_SIZE 224u
#define AR_STARTUP_ARGS 6u
#define AR_CHILD_ARGS 4u
#define AR_SLOT_SIZE 32u
struct ar_startup {
    uint32_t count;
    char args[AR_STARTUP_ARGS][AR_SLOT_SIZE];
};
struct ar_invocation {
    uint32_t count;
    char args[AR_CHILD_ARGS][AR_SLOT_SIZE];
    char environment[AR_SLOT_SIZE];
};
enum ar_action { AR_INVALID_STARTUP, AR_USAGE, AR_HELP, AR_VERSION, AR_LAUNCH };
/* Callers supply live, disjoint objects and record_size readable input bytes.
 * No arbitrary pointer validation or concurrency guarantee is provided.
 * Decode publishes only on success. Select publishes only on AR_LAUNCH;
 * otherwise output is unchanged and must not be used for launch. No borrowed
 * pointer survives a call. Actions are not process exits or delivered output.
 */
int ar_decode(const unsigned char *record, size_t record_size,
              struct ar_startup *output);
enum ar_action ar_select(const struct ar_startup *startup,
                         struct ar_invocation *output);
#endif
