// SPDX-License-Identifier: CDDL-1.0
/*
 * CDDL HEADER START
 *
 * The contents of this file are subject to the terms of the
 * Common Development and Distribution License, Version 1.0 only
 * (the "License").  You may not use this file except in compliance
 * with the License.
 *
 * You can obtain a copy of the license at usr/src/OPENSOLARIS.LICENSE
 * or https://opensource.org/licenses/CDDL-1.0.
 * See the License for the specific language governing permissions
 * and limitations under the License.
 *
 * When distributing Covered Code, include this CDDL HEADER in each
 * file and include the License file at usr/src/OPENSOLARIS.LICENSE.
 * If applicable, add the following below this CDDL HEADER, with the
 * fields enclosed by brackets "[]" replaced with your own identifying
 * information: Portions Copyright [yyyy] [name of copyright owner]
 *
 * CDDL HEADER END
 */
/*
 * Copyright 2008 Sun Microsystems, Inc.  All rights reserved.
 * Use is subject to license terms.
 */

/* Private native failure policy; this remains the pinned malloc fallback. */
static inline void *umem_alloc(size_t size, int flags)
{
    void *ptr = malloc(size);
    if (ptr == NULL && (flags & UMEM_NOFAIL))
        _Exit(125);
    return ptr;
}

static inline void *umem_alloc_aligned(size_t size, size_t align, int flags)
{
    void *ptr = NULL;
    int error = posix_memalign(&ptr, align, size);
    if (error != 0) {
        if (flags & UMEM_NOFAIL)
            _Exit(125);
        errno = error;
        return NULL;
    }
    return ptr;
}

static inline umem_cache_t *umem_cache_create(const char *name, size_t bufsize,
                                              size_t align,
                                              umem_constructor_t *constructor,
                                              umem_destructor_t *destructor,
                                              umem_reclaim_t *reclaim,
                                              void *priv, void *vmp, int cflags)
{
    umem_cache_t *cp = umem_alloc(sizeof(umem_cache_t), UMEM_NOFAIL);
    strlcpy(cp->cache_name, name, UMEM_CACHE_NAMELEN);
    cp->cache_bufsize = bufsize;
    cp->cache_align = align;
    cp->cache_constructor = constructor;
    cp->cache_destructor = destructor;
    cp->cache_reclaim = reclaim;
    cp->cache_private = priv;
    cp->cache_arena = vmp;
    cp->cache_cflags = cflags;
    return cp;
}

static inline void *umem_cache_alloc(umem_cache_t *cp, int flags)
{
    void *ptr;
    if (cp->cache_align != 0)
        ptr = umem_alloc_aligned(cp->cache_bufsize, cp->cache_align, flags);
    else
        ptr = umem_alloc(cp->cache_bufsize, flags);
    if (ptr && cp->cache_constructor &&
        cp->cache_constructor(ptr, cp->cache_private, UMEM_DEFAULT) != 0) {
        /* The constructor owns partial external cleanup; no destructor runs
         * on an object that was never successfully constructed. */
        if (cp->cache_align != 0)
            umem_free_aligned(ptr, cp->cache_bufsize);
        else
            umem_free(ptr, cp->cache_bufsize);
        if (flags & UMEM_NOFAIL)
            _Exit(125);
        errno = ENOMEM;
        return NULL;
    }
    return ptr;
}
