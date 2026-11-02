/* SPDX-License-Identifier: BSD-2-Clause */
/* Reuse only the actual startup/transport fixture. Its original workload/exit
 * bodies are renamed and never selected by this bounded diagnostic suite. */
#define __real_main aefd_fixture_main
#define __real__exit aefd_fixture_exit
#define main aefd_fixture_entry
#include "fd-zsh-filesystem-tests.c"
#undef main
#undef __real__exit
#undef __real_main
#include <limits.h>
_Noreturn void __wrap__Exit(int);
static unsigned scenario, delegates, nested;
static int after_active = 1, read_result = 1, cleanup_error;
static int delegate_result = 1;
static char delegate_buffer[2], delegate_name[] = "vt100";
int zleactive;
int __real_main(int, char **);
int __real_tgetent(char *, const char *);
_Noreturn void __real__Exit(int);
void aefd_test_filesystem_stdio(void) {}
int __real_tgetent(char *buffer, const char *name)
{
    assert(buffer == delegate_buffer && name == delegate_name);
    ++delegates;
    if (scenario == 20 && !nested) {
        nested = 1;
        delegate_result = 0;
        assert(__wrap_tgetent(buffer, name) == 0);
        delegate_result = 1;
    }
    buffer[0] = 'R';
    errno = E2BIG;
    return delegate_result;
}
static int64_t oracle_call(void *owner, uint64_t operation, uint64_t cap,
                           uint64_t a, uint64_t b, uint64_t c)
{
    int64_t result = call(owner, operation, cap, a, b, c);
    return operation == 0x24003 && cap == 71 && cleanup_error ? -EIO : result;
}
static struct aefd_stream_result oracle_read(void *owner, unsigned kind,
                                             unsigned selector,
                                             unsigned char *out, size_t count)
{
    assert(owner == boot && kind == AEFD_BIND_TERMINAL && selector == 0 &&
           count == 1 && boot->context.native.active);
    if (scenario == 21) {
        unsigned char untouched = 0xa5;
        assert(__aether_io(0, 0, (unsigned long)(uintptr_t)&untouched, 1) ==
                   -EBUSY &&
               untouched == 0xa5);
    }
    zleactive = after_active;
    if (read_result > 0)
        *out = 'Q';
    errno = ENOMEM;
    return (struct aefd_stream_result){1, read_result};
}
int __real_main(int argc, char **argv)
{
    (void)argv;
    assert(argc == 4 && ready_calls == 1 &&
           aether_zsh_diagnostic_status(0) == 144 &&
           aether_zsh_diagnostic_status(23) == 23);
    boot->context.native.call = oracle_call;
    boot->context.session.adapters.reader =
        (struct aefd_stream_reader){boot, oracle_read};
    if (scenario != 1 && scenario != 12 && scenario != 14) {
        if (scenario == 2)
            delegate_result = 0;
        if (scenario == 3)
            delegate_result = -1;
        errno = ERANGE;
        assert(__wrap_tgetent(delegate_buffer, delegate_name) ==
                   delegate_result &&
               errno == E2BIG && delegate_buffer[0] == 'R');
        if (scenario == 11) {
            delegate_result = 0;
            assert(__wrap_tgetent(delegate_buffer, delegate_name) == 0);
            delegate_result = 1;
            assert(__wrap_tgetent(delegate_buffer, delegate_name) == 1);
        }
    }
    zleactive = scenario == 5 || scenario == 7 ? 0 : 1;
    after_active = scenario == 6 ? 0 : 1;
    read_result = scenario == 8 ? 0 : scenario == 9 ? -EINTR : 1;
    unsigned char out = 0xa5;
    int fd = 0;
    if (scenario == 16)
        fd = (int)__aether_io(32, 0, 0, 0);
    if (scenario == 17)
        fd = aether_zsh_open("/dev/tty", O_RDWR, 0);
    if (scenario == 10)
        fd = aether_zsh_open("/home/.terminfo/v/vt100", O_RDONLY, 0);
    if (scenario == 18)
        boot->context.native.sources[0].reference ^= 2;
    if (scenario == 19) {
        unsigned before = calls;
        assert(__aether_io(0, ULONG_MAX, 0, 1) == -EBADF && calls == before);
    }
    if (scenario != 4 && scenario != 12 && scenario != 13 && scenario != 14 &&
        scenario != 19) {
        errno = ERANGE;
        long result = __aether_io(0, (unsigned long)fd,
                                  (unsigned long)(uintptr_t)&out, 1);
        assert(result == (scenario == 10 ? 1 : read_result) && errno == ERANGE);
    }
    if (scenario == 18)
        boot->context.native.sources[0].reference ^= 2;
    if (scenario == 14 || scenario == 15)
        cleanup_error = 1;
    if (scenario == 12 || scenario == 13)
        return 23;
    if (scenario == 22)
        __wrap__Exit(0);
    if (scenario == 23)
        __wrap__exit(0);
    return 0;
}
_Noreturn void __real__Exit(int status)
{
    int expected = scenario == 12 || scenario == 13   ? 23
                   : scenario == 14 || scenario == 15 ? 141
                   : scenario == 0 || scenario == 16 || scenario == 17 ||
                           scenario == 21 || scenario == 22 || scenario == 23
                       ? 0
                       : 144;
    assert(status == expected && closes[0] == 1 && closes[1] == 1 &&
           blocks == restores);
    assert(delegates == (scenario == 1 || scenario == 12 || scenario == 14 ? 0U
                         : scenario == 11                                  ? 3U
                         : scenario == 20                                  ? 2U
                                          : 1U));
    unsigned before = calls;
    assert(__aether_io(0, 0, 0, 0) == -EBADF && calls == before);
    char marker[64];
    int n =
        snprintf(marker, sizeof(marker), "ZSH_DIAGNOSTIC_PASS %u\n", scenario);
    assert(n > 0 && write(1, marker, (size_t)n) == n);
    _Exit(0);
}
int main(int argc, char **argv)
{
    assert(argc == 2);
    scenario = (unsigned)strtoul(argv[1], NULL, 10);
    assert(scenario <= 23);
    char *fixture[] = {"oracle", "0", NULL};
    return aefd_fixture_entry(2, fixture);
}
