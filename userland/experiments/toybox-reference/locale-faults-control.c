// SPDX-License-Identifier: BSD-2-Clause
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <errno.h>
#include <locale.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char *__wrap_setlocale(int category, const char *name);
locale_t __wrap_newlocale(int mask, const char *name, locale_t base);
locale_t __wrap_uselocale(locale_t value);
ssize_t __wrap_read(int fd, void *buf, size_t count);
static int sets;
static int allocations;
static int uses;

char *__real_setlocale(int category, const char *name)
{
    assert(category == LC_CTYPE && !strcmp(name, ""));
    sets++;
    return setlocale(LC_CTYPE, "C");
}
locale_t __real_newlocale(int mask, const char *name, locale_t base)
{
    assert(mask == LC_CTYPE_MASK && !base);
    assert(!strcmp(name, "C.UTF-8") || !strcmp(name, "en_US.UTF-8"));
    allocations++;
    // Host control checks routing/lifetime using C, not Linux locale behavior.
    return newlocale(mask, "C", base);
}
locale_t __real_uselocale(locale_t value)
{
    uses++;
    return uselocale(value);
}
ssize_t __real_read(int fd, void *buf, size_t count)
{
    assert(fd == 0);
    memset(buf, 'x', count);
    return (ssize_t)count;
}
int main(int argc, char **argv)
{
    char data[4];
    assert(argc == 2 && !setenv("TOYBOX_LOCALE_FAULT", argv[1], 1));
    int set_denied = !strcmp(argv[1], "set-denied");
    int all_denied = !strcmp(argv[1], "all-denied");
    char *result = __wrap_setlocale(LC_CTYPE, "");
    assert((result == NULL) == set_denied && sets == !set_denied);
    if (set_denied)
        assert(errno == ENOENT);
    locale_t value = __wrap_newlocale(LC_CTYPE_MASK, "C.UTF-8", (locale_t)0);
    if (!value) {
        assert(errno == ENOMEM);
        value = __wrap_newlocale(LC_CTYPE_MASK, "en_US.UTF-8", (locale_t)0);
    }
    assert((value == (locale_t)0) == all_denied);
    assert(allocations == !all_denied);
    assert(__wrap_uselocale(value));
    assert(uses == 1);
    assert(__wrap_read(0, data, sizeof(data)) == sizeof(data));
    assert(__wrap_read(0, data, sizeof(data)) == sizeof(data));
    assert(!memcmp(data, "xxxx", sizeof(data)));
    if (value) {
        assert(uselocale(LC_GLOBAL_LOCALE));
        freelocale(value);
    }
    return 0;
}
