/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-tinfo-directory.h"
#include "fd-zsh-external.h"
int aether_tinfo_directory_probe(const char *path,
                                 struct aether_tinfo_directory_view *out)
{
    return aether_zsh_directory_probe(path, out);
}
int aether_tinfo_directory_same(const struct aether_tinfo_directory_view *a,
                                const struct aether_tinfo_directory_view *b)
{
    return a && b && a->kind == 2 && b->kind == 2 && a->key && a->epoch &&
           a->key == b->key && a->epoch == b->epoch;
}
