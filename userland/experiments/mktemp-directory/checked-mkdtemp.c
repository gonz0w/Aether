/* SPDX-License-Identifier: MIT
 * Derived from musl 1.2.6 src/temp/{mkdtemp,__randname}.c.
 * Archive SHA256
 * d585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a. Local
 * changes: bounded admitted template, checked explicit MONOTONIC and
 * initialized positive TLS identity, one MakeDirectory attempt, no retry/reset.
 * Naming is neither cryptographic entropy nor a uniqueness guarantee.
 *
 * Copyright (c) 2005-2020 Rich Felker, et al.
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions: The above copyright
 * notice and this permission notice shall be included in all copies or
 * substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS",
 * WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
 * TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
 * FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
 * THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
#include "target.h"
#include <errno.h>
#include <stdint.h>
#include <string.h>
#ifdef AMK_NATIVE_MUSL
#include <time.h>
#include "pthread_impl.h"
#endif

char *amk_checked_mkdtemp(char *text)
{
    struct amk_timespec observed = {0, 0};
    int64_t identity = 0;
    int result = amk_target_name_inputs(text, &observed, &identity);
    if (result) {
        errno = -result;
        return NULL;
    }
#ifdef AMK_NATIVE_MUSL
    struct timespec native_time = {0, 0};
    if (clock_gettime(CLOCK_MONOTONIC, &native_time)) {
        /* Preserve the actual failing libc observation; do not invent success.
         */
        return NULL;
    }
    observed.seconds = (int64_t)native_time.tv_sec;
    observed.nanoseconds = (int64_t)native_time.tv_nsec;
    identity = (int64_t)__pthread_self()->tid;
#endif
#ifndef AMK_OMIT_CLOCK
    if (observed.seconds < 0 || observed.nanoseconds < 0 ||
        observed.nanoseconds >= INT64_C(1000000000)) {
        errno = EINVAL;
        return NULL;
    }
#endif
#ifndef AMK_OMIT_TLS
    if (identity <= 0) {
        errno = EINVAL;
        return NULL;
    }
#endif
    /* Modular unsigned arithmetic affects only the six-character name seed.
     * Template and authority bounds were checked before these observations.
     */
    uint64_t seed = (uint64_t)observed.seconds +
                    (uint64_t)observed.nanoseconds +
                    (uint64_t)identity * UINT64_C(65537);
    size_t length = strlen(text);
    for (size_t i = 0; i < 6; i++, seed >>= 5) {
        uint64_t character = UINT64_C(65) + (seed & 15) + (seed & 16) * 2;
        text[length - 6 + i] = (char)character;
    }
    result = amk_target_create(text, 0700);
    if (!result)
        return text;
    errno = -result;
    /* Leave the attempted candidate intact on all failures, including EEXIST.
     * No retry, template restoration, unlink or rollback follows this receipt.
     */
    return NULL;
}
