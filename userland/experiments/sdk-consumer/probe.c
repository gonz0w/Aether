/* SPDX-License-Identifier: BSD-2-Clause */
#include <stddef.h>
#include <string.h>

/* Link-only consumer. Caller would need a live NUL-terminated string. */
size_t sdk_probe(const char *text);

size_t sdk_probe(const char *text) { return strlen(text); }
