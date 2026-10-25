/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_WRITE_TESTS_H
#define AETHER_FD_WRITE_TESTS_H
#include "fd-stream-tests.h"
int64_t aefd_write_test_open(struct aefd_bindings *, struct aefd_client *,
                             const unsigned char *, size_t, int);
int64_t aefd_write_test_dup(struct aefd_bindings *, struct aefd_client *, int,
                            int, int);
int64_t aefd_write_test_close(struct aefd_bindings *, struct aefd_client *,
                              int);
int64_t aefd_write_test_flags(struct aefd_bindings *, struct aefd_client *, int,
                              int);
#endif
