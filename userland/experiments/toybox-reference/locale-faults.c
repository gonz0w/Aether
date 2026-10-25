// SPDX-License-Identifier: BSD-2-Clause
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <langinfo.h>
#include <locale.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char *__real_setlocale(int category, const char *name);
locale_t __real_newlocale(int mask, const char *name, locale_t base);
locale_t __real_uselocale(locale_t value);
ssize_t __real_read(int fd, void *buf, size_t count);

static int selected(const char *name)
{
    const char *mode = getenv("TOYBOX_LOCALE_FAULT");
    return mode && !strcmp(mode, name);
}

static void trace(const char *text)
{
    size_t length = strlen(text);
    if (write(2, text, length) != (ssize_t)length)
        _exit(90);
}

char *__wrap_setlocale(int category, const char *name)
{
    if (selected("set-denied")) {
        trace("SET_DENIED\n");
        errno = ENOENT;
        return NULL;
    }
    char *result = __real_setlocale(category, name);
    trace(result ? "SET_OK\n" : "SET_FAILED\n");
    return result;
}

locale_t __wrap_newlocale(int mask, const char *name, locale_t base)
{
    int primary = !strcmp(name, "C.UTF-8");
    if (selected("all-denied") || (primary && selected("primary-denied"))) {
        trace(primary ? "PRIMARY_DENIED\n" : "FALLBACK_DENIED\n");
        errno = ENOMEM;
        return (locale_t)0;
    }
    locale_t result = __real_newlocale(mask, name, base);
    trace(primary ? (result ? "PRIMARY_OK\n" : "PRIMARY_FAILED\n")
                  : (result ? "FALLBACK_OK\n" : "FALLBACK_FAILED\n"));
    return result;
}

locale_t __wrap_uselocale(locale_t value)
{
    trace(value ? "USE_SET\n" : "USE_QUERY\n");
    return __real_uselocale(value);
}

ssize_t __wrap_read(int fd, void *buf, size_t count)
{
    static int observed;
    if (fd == 0 && !observed++) {
        const char *codeset = nl_langinfo(CODESET);
        trace(!strcmp(codeset, "UTF-8") ? "READ_UTF8\n" : "READ_OTHER\n");
    }
    return __real_read(fd, buf, count);
}
