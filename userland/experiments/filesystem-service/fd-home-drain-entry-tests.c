/* SPDX-License-Identifier: BSD-2-Clause */
/* Host entry integration only: compile unchanged fd-shell-entry.c and the exact
 * final native-main block from fd-home-drain.c, with main renamed __real_main
 * and __builtin_trap renamed aefd_home_drain_entry_trap. Use the pinned C17
 * diagnostics, AEFD_EXEC_BINDINGS and one fixed AEFD_HOME_DRAIN_CASE=1. Link
 * this file; all native/runtime boundaries below are explicit host stubs.
 * No replacement shell wrapper, native image, ABI or runtime qualification.
 *
 * The block is everything between the final
 * "#ifndef AEFD_HOME_DRAIN_HOST_TEST\n" and its final "#endif\n".
 * Prefix only #include "fd-home-drain.h" and the noreturn trap declaration.
 * Compile that block with -Dmain=__real_main; compile the unchanged wrapper
 * and this test separately without that rename. The compact run receipt holds
 * the exact extraction hash, compiler argv, headers/tools and cleanup results.
 */
#include "fd-home-drain.h"
#include "fd-libc.h"
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>

int __real_main(int, char **);
int __wrap_main(int, char **);
_Noreturn void __real__exit(int);
_Noreturn void aefd_home_drain_entry_trap(void);

static struct aefd_fork context;
static jmp_buf terminal;
static unsigned started, roles, ready, contexts, runs, traps, finishes, exits;
static int mode;

#define CHECK(value, label)                                                    \
    do {                                                                       \
        if (!(value)) {                                                        \
            fprintf(stderr, "DRAIN_ENTRY_%s:%d\n", label, __LINE__);           \
            exit(1);                                                           \
        }                                                                      \
    } while (0)

int64_t aefd_shell_start(void)
{
    CHECK(!started && !roles && !ready && !runs, "START_ORDER");
    ++started;
    return mode == 2 ? -5 : 0;
}
int64_t aefd_shell_role(void)
{
    CHECK(started == 1 && !roles && !ready && !runs, "ROLE_ORDER");
    ++roles;
    return mode == 3 ? 2 : 1;
}
int64_t aefd_shell_ready(void)
{
    CHECK(started == 1 && roles == 1 && !ready && !runs, "READY_ORDER");
    ++ready;
    return mode == 4 ? -5 : 0;
}
struct aefd_fork *aefd_shell_fork_context(void)
{
    CHECK(started == 1 && roles == 1 && ready == 1 && !contexts,
          "ADMITTED_CONTEXT_AFTER_WRAPPER_READY");
    ++contexts;
    return &context;
}
int aefd_home_drain_run(struct aefd_fork *f, unsigned which)
{
    CHECK(f == &context && context.boot.phase == 2 &&
              context.boot.identity.slot == 1 && contexts == 1 &&
              started == 1 && roles == 1 && ready == 1 && !runs &&
              which == AEFD_DRAIN_FILE_PREFIX,
          "MATCHED_COMPILED_CASE_AND_CONTEXT");
    ++runs;
    if (mode == 1)
        return 110;
    longjmp(terminal,
            1); /* Runtime boundary entered; actual run never returns. */
}
_Noreturn void aefd_home_drain_entry_trap(void)
{
    CHECK(!finishes && !exits, "TRAP_PRECEDES_LIBC_FINISH");
    ++traps;
    longjmp(terminal, 2);
}
_Noreturn void __real__exit(int status)
{
    CHECK(status == 143 && !runs && !traps && !finishes,
          "WRAPPER_REJECTS_BEFORE_NATIVE_MAIN");
    ++exits;
    longjmp(terminal, 3);
}
_Noreturn void __wrap__exit(int status)
{
    (void)status;
    ++finishes;
    longjmp(terminal, 4);
}
static void reset(int selected)
{
    memset(&context, 0, sizeof context);
    context.boot.phase = 2;
    context.boot.identity.slot = 1;
    started = roles = ready = contexts = runs = traps = finishes = exits = 0;
    mode = selected;
}
static int invoke_wrapper(void)
{
    int result = setjmp(terminal);
    if (!result) {
        (void)__wrap_main(0,
                          NULL); /* Wrapper supplies its real sh/-i/+m argv. */
        CHECK(0, "WRAPPER_RETURNED");
    }
    return result;
}
static int invoke_main(int argc)
{
    int result = setjmp(terminal);
    if (!result) {
        (void)__real_main(argc, NULL);
        CHECK(0, "NATIVE_MAIN_RETURNED");
    }
    return result;
}
int main(void)
{
    reset(0);
    CHECK(invoke_wrapper() == 1 && runs == 1 && !traps && !finishes && !exits,
          "WRAPPER_ARGC3_MUST_ENTER_RUNTIME");
    reset(1);
    CHECK(invoke_wrapper() == 2 && runs == 1 && traps == 1 && !finishes,
          "RETURN_FAILURE_MUST_TRAP_BEFORE_LIBC_CLEANUP");
    for (int argc = 0; argc <= 2; argc += 2) {
        reset(0);
        CHECK(invoke_main(argc) == 2 && traps == 1 && !contexts && !runs &&
                  !finishes,
              "UNEXPECTED_ARGC_FAIL_STOP_BEFORE_RUNTIME");
    }
    for (int selected = 2; selected <= 4; ++selected) {
        reset(selected);
        CHECK(invoke_wrapper() == 3 && exits == 1 && !contexts && !runs &&
                  !traps && !finishes,
              "WRAPPER_START_ROLE_READY_DENIAL");
    }
    puts("7 actual wrapper/native-main host entry scenarios pass");
    return 0;
}
