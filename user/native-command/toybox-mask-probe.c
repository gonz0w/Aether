/* SPDX-License-Identifier: BSD-2-Clause */
/* Private native startup witness; does not run cat_main or Toybox exit hooks.
 */
#include "transport.h"
#include "toys.h"

static _Thread_local volatile unsigned startup_cookie = 23;
static void *startup_buffer;
static unsigned allocated_buffer, configured_buffer;
void *__real_xmalloc(size_t size);
int __real_setvbuf(FILE *stream, char *buffer, int mode, size_t size);
void *__wrap_xmalloc(size_t size)
{
    void *p = __real_xmalloc(size);
    if (size == 4096) {
        startup_buffer = p;
        allocated_buffer++;
    }
    return p;
}
int __wrap_setvbuf(FILE *stream, char *buffer, int mode, size_t size)
{
    int result = __real_setvbuf(stream, buffer, mode, size);
    if (stream == stdout && buffer == startup_buffer && buffer &&
        mode == _IOFBF && size == 4096 && result == 0)
        configured_buffer++;
    return result;
}
static unsigned mask_live, mask_value, mask_calls;
static unsigned requests[2], previous[2];
mode_t umask(mode_t requested)
{
    if (!mask_live) {
        errno = EINVAL;
        return (mode_t)-1;
    }
    unsigned old = mask_value;
    mask_value = requested & 0777u;
    if (mask_calls < 2) {
        requests[mask_calls] = requested;
        previous[mask_calls] = old;
    }
    mask_calls++;
#ifdef MASK_WRONG_OLD
    return requested;
#else
    return old;
#endif
}
int main(int argc, char **argv)
{
    if (startup_cookie != 23)
        return 115;
    startup_cookie++;
    if (argc != 1 || strcmp(argv[0], "cat") || argv[1] || !bootstrap())
        return 115;
    if (!environ || !environ[0] || strcmp(environ[0], "LC_ALL=C") || environ[1])
        return 115;
    if (!getauxval(0xa000))
        return 116;
    errno = 0;
    if (umask(0) != (mode_t)-1 || errno != EINVAL)
        return 115;
    mask_live = 1;
    mask_value = 0077;
#ifndef MASK_WRONG_OLD
    if (umask(07777) != 0077 || mask_value != 0777 || umask(0077) != 0777)
        return 115;
#endif
    mask_calls = 0;
    if (strcmp(toy_list[0].name, "cat") || (toy_list[0].flags & TOYFLAG_NOFORK))
        return 115;
#ifndef MASK_SKIP_INIT
    toy_singleinit(toy_list, argv);
#endif
    if (startup_cookie != 24 || allocated_buffer != 1 ||
        configured_buffer != 1 || mask_calls != 2 || requests[0] != 0 ||
        requests[1] != 0077 || previous[0] != 0077 || previous[1] != 0 ||
        mask_value != 0077 || toys.old_umask != 0077 ||
        toys.which != toy_list || toys.optc != 0 ||
        strcmp(nl_langinfo(CODESET), "UTF-8"))
        return 115;
    int failed = 0;
    if (close(0))
        failed = 1;
    if (close(1))
        failed = 1;
    if (close(2))
        failed = 1;
    mask_live = 0;
    errno = 0;
    if (umask(0) != (mode_t)-1 || errno != EINVAL)
        return 115;
    return failed ? 1 : 0;
}
