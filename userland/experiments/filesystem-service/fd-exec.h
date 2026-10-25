/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_EXEC_H
#define AETHER_FD_EXEC_H
#include "fd-fork-stage.h"
/* Current immutable-helper exec, child only. Arguments/observations are
 * borrowed synchronously under the sole context guard. Unknown outcomes
 * fail-stop; no success return, context reset, old wire fallback or successful
 * no-op. */
int64_t aefd_exec(struct aefd_fork *, struct aefd_startup_auxv, const char *,
                  char *const[], char *const[]);
/* Publish readiness only after the new startup context has actually admitted.
 */
int64_t aefd_startup_ready(struct aefd_startup *);
int64_t aefd_shell_ready(void);
#endif
