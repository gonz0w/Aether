/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_TINFO_DIRECTORY_H
#define AETHER_FD_TINFO_DIRECTORY_H
#include "fd-context.h"
#ifndef AEFD_ZSH_FILESYSTEM_BINDINGS
#error "typed tinfo directory requires the closed Zsh filesystem selection"
#endif
/* One immutable app context's held view only. Neither value is a capability or
 * POSIX inode/device identity. Query anew on each selected iterator cache
 * build. Output is untouched on failure. No general libc stat behavior is
 * supplied. */
int aether_tinfo_directory_probe(const char *,
                                 struct aether_tinfo_directory_view *);
int aether_tinfo_directory_same(const struct aether_tinfo_directory_view *,
                                const struct aether_tinfo_directory_view *);
#endif
