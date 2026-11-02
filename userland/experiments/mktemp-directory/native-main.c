/* SPDX-License-Identifier: BSD-2-Clause */
/* Selected one-app glue. The only mutable libc facade is this stable FD
 * context; Rust keeps the namespace, trap budget and four-endpoint ledger
 * disjoint. */
#ifdef AMK_NATIVE_TTY_MODE_PROBE
#ifndef AMK_NATIVE_TTY_DUPLEX_PROBE
#define AMK_NATIVE_TTY_DUPLEX_PROBE
#endif
#endif
#ifdef AMK_NATIVE_TTY_DUPLEX_PROBE
#ifndef AMK_NATIVE_TTY_DESCRIPTOR_PROBE
#define AMK_NATIVE_TTY_DESCRIPTOR_PROBE
#endif
#endif
#ifdef AMK_NATIVE_TTY_DESCRIPTOR_PROBE
#ifndef AMK_NATIVE_TTY_BYTE_PROBE
#define AMK_NATIVE_TTY_BYTE_PROBE
#endif
#endif
#include "native.h"
#include "target.h"
#include "fd-startup.h"
#ifdef AMK_NATIVE_TTY_DESCRIPTOR_PROBE
#include "fd-libc.h"
#endif
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#ifndef AMK_NATIVE_APP_HOST
#include <sys/auxv.h>
#include "pthread_impl.h"
#endif
#define AETHER_VECTOR_CORE_ONLY
#include "../../../user/native-command/vector-write.h"

static struct aefd_startup descriptors;
static struct amk_native_receipt raw_receipt;
static struct aefd_finish descriptor_receipt;
static unsigned descriptor_live, descriptor_finished;
static int32_t descriptor_status;

static int narrow_startup(void)
{
    const struct aefd_context *context = &descriptors.context;
    for (unsigned fd = 0; fd < 16; ++fd) {
        const struct aefd_binding *binding = &context->map.slots[fd];
        if (fd == 1 || fd == 2
#ifdef AMK_NATIVE_TTY_BYTE_PROBE
            || fd == 0
#endif
        ) {
            if (binding->kind !=
#ifdef AMK_NATIVE_TTY_DESCRIPTOR_PROBE
                    AEFD_BIND_TERMINAL
#else
                    AEFD_BIND_CONSOLE
#endif
                || binding->selector != fd || binding->cloexec)
                return 0;
        } else if (binding->kind || binding->selector || binding->cloexec) {
            return 0;
        }
    }
    for (unsigned i = 0; i < 7; ++i) {
        const struct aefd_native_source *source = &context->native.sources[i];
        if (i == 1 || i == 2
#ifdef AMK_NATIVE_TTY_BYTE_PROBE
            || i == 0
#endif
        ) {
            if (!source->reference || source->selector != i ||
                source->rights !=
#ifdef AMK_NATIVE_TTY_BYTE_PROBE
                    (i == 0 ? 1U : 2U)
#else
                    2
#endif
                || source->bound != 16)
                return 0;
        } else if (source->reference || source->selector || source->rights ||
                   source->bound) {
            return 0;
        }
    }
#ifdef AMK_NATIVE_TTY_BYTE_PROBE
    if (context->native.sources[0].reference ==
            context->native.sources[1].reference ||
        context->native.sources[0].reference ==
            context->native.sources[2].reference)
        return 0;
#endif
    return context->native.sources[1].reference !=
               context->native.sources[2].reference &&
           !context->native.generations[0] && !context->native.generations[1];
}

#ifdef AMK_NATIVE_TTY_DESCRIPTOR_PROBE
static int32_t finish_descriptors(void *state);
#endif
int64_t amk_native_fd_start(uint64_t memory, uint64_t input, uint64_t output)
{
    if (descriptor_live || descriptor_finished)
        return -16;
    int64_t status =
        aefd_startup_start(&descriptors, amk_native_call, NULL,
                           (struct aefd_startup_auxv){memory, input, output});
    if (status)
        return status;
#ifdef AMK_NATIVE_TTY_DESCRIPTOR_PROBE
    /* Generic admission already owns the process endpoints and aliases. */
    descriptor_live = 1;
    if (!narrow_startup()) {
        int32_t cleanup = finish_descriptors(NULL);
        return cleanup ? cleanup : -22;
    }
#else
    if (!narrow_startup())
        return -22;
    descriptor_live = 1;
#endif
    return 0;
}

#ifdef AMK_NATIVE_TTY_DESCRIPTOR_PROBE
struct aefd_startup *aefd_shell_external_startup(void) { return &descriptors; }
#endif
long __aether_io(unsigned long operation, unsigned long fd,
                 unsigned long pointer, unsigned long count)
{
#ifdef AMK_NATIVE_TTY_DESCRIPTOR_PROBE
    if (!descriptor_live || descriptor_finished)
        return -EBADF;
    return (long)aefd_libc_io(&descriptors.context, operation, fd, pointer,
                              count);
#else
    if (!descriptor_live || descriptor_finished ||
        (fd != 1 && fd != 2
#ifdef AMK_NATIVE_TTY_BYTE_PROBE
         && fd != 0
#endif
         ))
        return -EBADF;
#ifdef AMK_NATIVE_TTY_BYTE_PROBE
    if (operation == 0) {
        if (count > (unsigned long)SSIZE_MAX || (count && !pointer))
            return -EINVAL;
        return (long)aefd_context_read(&descriptors.context, (int)fd,
                                       (unsigned char *)(uintptr_t)pointer,
                                       (size_t)count);
    }
#endif
    if (operation == 1) {
        if (count > (unsigned long)SSIZE_MAX || (count && !pointer))
            return -EINVAL;
        return (long)aefd_context_write(
            &descriptors.context, (int)fd,
            (const unsigned char *)(uintptr_t)pointer, (size_t)count);
    }
    if (operation == 3)
        return (long)aefd_context_close(&descriptors.context, (int)fd);
    /* Unsupported operations never acquire an alias or become a successful
     * no-op. The default utility still admits only writes and closes. */
    return -EBADF;
#endif
}
static long descriptor_sink(void *context, int fd, const unsigned char *bytes,
                            size_t count)
{
    (void)context;
    return __aether_io(1, (unsigned long)fd, (unsigned long)(uintptr_t)bytes,
                       (unsigned long)count);
}
long amk_native_vector_write(int fd, const struct iovec *parts, int count)
{
    long status = vector_write_to(NULL, descriptor_sink, fd, parts, count);
    if (status < 0) {
        errno = status >= -4095 ? (int)-status : EIO;
        return -1;
    }
    return status;
}
int amk_native_monotonic(clockid_t id, struct timespec *output)
{
    if (id != CLOCK_MONOTONIC || !output) {
        errno = output ? EINVAL : EFAULT;
        return -1;
    }
    int64_t value = amk_native_clock();
    if (value < 0) {
        errno = value >= -4095 ? (int)-value : EIO;
        return -1;
    }
    *output = (struct timespec){(time_t)(value / INT64_C(1000000000)),
                                (long)(value % INT64_C(1000000000))};
    return 0;
}
static int32_t finish_descriptors(void *state)
{
    (void)state;
    if (descriptor_finished)
        return descriptor_status;
    descriptor_finished = 1;
    if (descriptor_live) {
        int64_t status =
            aefd_context_finish(&descriptors.context, &descriptor_receipt);
        if (status || descriptor_receipt.first_error ||
            descriptor_receipt.unknown || descriptor_receipt.remaining ||
            descriptor_receipt.transport.input ||
            descriptor_receipt.transport.output)
            descriptor_status = -5;
    }
    int64_t raw = amk_native_finish_raw(&raw_receipt);
    if (raw && !descriptor_status)
        descriptor_status = -5;
    descriptor_live = 0;
    return descriptor_status;
}

#ifdef AMK_NATIVE_APP_HOST
/* Test-only reset after all native borrows ended and cleanup was retained. It
 * cannot be built into the selected native artifact. No live facade is moved.
 */
void amk_native_test_reset(void)
{
    if (descriptor_live && !descriptor_finished)
        __builtin_trap();
    memset(&descriptors, 0, sizeof(descriptors));
    memset(&raw_receipt, 0, sizeof(raw_receipt));
    memset(&descriptor_receipt, 0, sizeof(descriptor_receipt));
    descriptor_live = descriptor_finished = 0;
    descriptor_status = 0;
}
int32_t amk_native_test_finish(void) { return finish_descriptors(NULL); }
#else
int clock_gettime(clockid_t id, struct timespec *output)
{
    return amk_native_monotonic(id, output);
}
#ifdef AMK_NATIVE_TTY_MODE_PROBE
extern int amk_tty_mode_probe(int, char **);
#define AMK_SELECTED_APP amk_tty_mode_probe
#elif defined(AMK_NATIVE_TTY_DUPLEX_PROBE)
extern int amk_tty_duplex_probe(int, char **);
#define AMK_SELECTED_APP amk_tty_duplex_probe
#elif defined(AMK_NATIVE_TTY_DESCRIPTOR_PROBE)
extern int amk_tty_descriptor_probe(int, char **);
#define AMK_SELECTED_APP amk_tty_descriptor_probe
#elif defined(AMK_NATIVE_TTY_BYTE_PROBE)
extern int amk_tty_byte_probe(int, char **);
#define AMK_SELECTED_APP amk_tty_byte_probe
#else
extern int amk_toybox_main(int, char **);
#define AMK_SELECTED_APP amk_toybox_main
#endif
static _Alignas(8) unsigned char startup_record[64];
static struct amk_bootstrap namespace;
static struct amk_run_result report;
static const struct amk_native_hooks hooks = {
    amk_native_verify, finish_descriptors, amk_native_terminal, NULL};

int main(int argc, char **argv, char **envp)
{
    uint64_t source = getauxval(0xa003);
    uint64_t memory = getauxval(0xa000);
    uint64_t input = getauxval(0xa001);
    uint64_t output = getauxval(0xa002);
    int status = 1;
    if (source != UINT64_C(0x0800e200))
        goto done;
    /* Only the fixed kernel-authored address is read. Copy before validating
     * the fields; never retain a borrow into the kernel startup region. */
    memcpy(startup_record, (const void *)(uintptr_t)source,
           sizeof(startup_record));
    if (amk_native_initialize(startup_record, source, memory, input, output,
                              &namespace))
        goto done;
    if (amk_native_fd_start(memory, input, output))
        goto done;
    if (__pthread_self()->tid <= 0)
        goto done;
    if (!amk_target_run_native(&namespace, argc, argv, envp, &hooks,
                               AMK_SELECTED_APP, &report))
        status = (int)report.final_status;
done:
    if (finish_descriptors(NULL) && !status)
        status = 1;
    amk_native_terminal((uint32_t)status);
}
#endif
