/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_SESSION_RUNTIME_H
#define AETHER_SESSION_RUNTIME_H

#ifdef SESSION_FS_ABI29
/* Prevent old/new application/runtime pairs from silently resolving at link. */
#define aether_session_start aether_fs29_session_start_v1
#endif

/* Experimental AENMX008/ABI23 adapter. Exactly one start per process image;
 * failure must stop that image. A copied child inherits already started state.
 * The result identifies the owner-issued role; it conveys no authority. */
int aether_session_start(unsigned *caller_role);

/* Application may narrow helper admission. The native owner enforces grants. */
int aether_session_exec_allowed(const char *path);
_Noreturn void __wrap__exit(int status);

#endif
