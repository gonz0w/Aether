/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_MKTEMP_TARGET_H
#define AETHER_MKTEMP_TARGET_H
#include "namespace.h"
#include <sys/types.h>

struct amk_timespec {
    int64_t seconds, nanoseconds;
};
_Static_assert(sizeof(struct amk_timespec) == 16 &&
                   _Alignof(struct amk_timespec) == 8,
               "observation ABI");
/* Host fixture observations are not native grants. State and callbacks remain
 * stable for the synchronous call. Positive identity must come from initialized
 * host TLS storage. No callbacks may reenter, unwind or retain borrowed
 * storage. before_exit is an optional HOST receipt observer, after finish and
 * TLS clear; it may write only its caller-owned sink. A nonzero result fails
 * the command. AMK_NATIVE_MUSL instead reads actual musl TLS and
 * CLOCK_MONOTONIC; its matched native startup/capability binding remains
 * unavailable.
 */
struct amk_observations {
    void *state;
    int32_t (*monotonic)(void *, struct amk_timespec *);
    int64_t (*thread_identity)(void *);
    int32_t (*before_exit)(void *, const struct amk_run_result *, uint32_t);
};
typedef int (*amk_applet_fn)(int, char **);
/* Selected one-app callbacks live in stable disjoint native storage. This is a
 * private C call contract, never a launch/wire record. finish runs only after
 * namespace completion and caches descriptor/raw cleanup. terminal must not
 * return or unwind. No callback may reenter the active target/namespace. */
struct amk_native_hooks {
    amk_verify_fn verify;
    int32_t (*finish)(void *);
    void (*terminal)(uint32_t);
    void *state;
};
/* argv/envp and every active string are initialized stable caller storage.
 * Arrays include their terminating NULL; each active payload is <=31 bytes.
 * envp must describe the actual applet process environment; this function does
 * not replace libc environ. Host fixtures establish that correspondence.
 * bootstrap/prefix, arguments, observations, and out must not overlap mutable
 * storage. An admitted synchronous entry lends a Rust Context through private
 * C TLS. No pointer escapes the frame. No longjmp/exception crosses Rust.
 */
int32_t amk_target_run(const struct amk_bootstrap *, int, char **, char **,
                       const struct amk_observations *, amk_applet_fn,
                       struct amk_run_result *);
int32_t amk_target_run_native(const struct amk_bootstrap *, int, char **,
                              char **, const struct amk_native_hooks *,
                              amk_applet_fn, struct amk_run_result *);
char *amk_checked_mkdtemp(char *);
mode_t amk_target_umask(mode_t);
/* Upstream _exit compile-name hook: callbacks and fflush/ferror already ran in
 * Toybox xexit. Finish while Rust Context lives, clear TLS, observe, real
 * _exit. terminal_status is also the returning-path fixture seam; no process
 * exit.
 */
int amk_target_terminal_status(int);
_Noreturn void amk_target_terminal_exit(int);
/* Private checked-helper bridge, usable only within the admitted C entry.
 * No authority is derived from text. One effect maximum, mode0700/mask0077.
 */
int amk_target_name_inputs(const char *, struct amk_timespec *, int64_t *);
int amk_target_create(const char *, uint32_t);
#endif
