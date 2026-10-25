/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-fork-stage.h"
#include <errno.h>
#ifdef AEFD_FORK_HOST_TEST
unsigned long aefd_fork_test_auxv(unsigned long);
void aefd_fork_test_park(unsigned long *, unsigned long *, unsigned long *,
                         unsigned long *);
#define getauxval aefd_fork_test_auxv
#else
#include <sys/auxv.h>
#endif
int copy_rebind(unsigned long, unsigned long, unsigned long, unsigned long *,
                unsigned long *);
_Noreturn void __real__exit(int);
_Static_assert(sizeof(unsigned long) == 8 && sizeof(void *) == 8,
               "native x86-64 fork ABI required");
/* Real initialized TLS template, retained by live startup/copy checks. This
 * matches the old session invariant; never reset it to conceal a bad rebind. */
static _Thread_local volatile uint32_t fork_tls = UINT32_C(0x73657373);
int aefd_fork_tls_valid(void) { return fork_tls == UINT32_C(0x73657373); }
#ifdef AEFD_FORK_HOST_TEST
void aefd_fork_test_tls_set(uint32_t);
void aefd_fork_test_tls_set(uint32_t value) { fork_tls = value; }
#endif
static int native_rebind(void *context, struct aefd_startup_auxv parent,
                         struct aefd_startup_auxv child)
{
    (void)context;
    unsigned long input = parent.input, output = parent.output;
    if (getauxval(0xa000) != parent.memory ||
        getauxval(0xa001) != parent.input ||
        getauxval(0xa002) != parent.output ||
        !copy_rebind(child.memory, child.input, child.output, &input, &output))
        return 0;
    return aefd_fork_tls_valid() && input == child.input &&
           output == child.output && getauxval(0xa000) == child.memory &&
           getauxval(0xa001) == child.input &&
           getauxval(0xa002) == child.output;
}
long __aether_fork_stage(void)
{
    int saved = errno;
    if (!aefd_fork_tls_valid())
        __real__exit(116);
    struct aefd_fork *f = aefd_shell_fork_context();
    struct aefd_startup_auxv observed = {getauxval(0xa000), getauxval(0xa001),
                                         getauxval(0xa002)};
    int64_t result = aefd_fork_arm(f, observed);
    if (result) {
        if (f->phase == AEFD_FORK_FAILED)
            __real__exit(116);
        errno = saved;
        return (long)result;
    }
    unsigned long op = 0x23003, memory = 0, input = 0, output = 0;
#ifdef AEFD_FORK_HOST_TEST
    aefd_fork_test_park(&op, &memory, &input, &output);
#else
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    /* Actual copy resumes on private backing. Preserve all three child grant
     * outputs before any C call; parent receives positive PID or raw thaw-11.
     */
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+D"(memory), "+S"(input), "+d"(output),
                           "+r"(r10), "+r"(r8), "+r"(r9)
                         :
                         : "rcx", "r11", "memory");
#endif
    if (op) {
        result = aefd_fork_parent(f, (long)op);
        if (f->phase == AEFD_FORK_FAILED)
            __real__exit(116);
    } else {
        struct aefd_startup_auxv grants = {memory, input, output};
        result = aefd_fork_child(f, grants, native_rebind, NULL);
        if (result)
            __real__exit(114);
    }
    /* Pinned _Fork now performs __post_Fork: no TID/list repair here. */
    errno = saved;
    return (long)result;
}
