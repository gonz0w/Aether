/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only actual aefd leave bridge. The Rust test process supplies raw kernel
 * observations and terminates at the exit/fault boundary; no unwind crosses C.
 * Compile this section with AMK_NATIVE_LEAVE_TESTS and link actual fd-native.c.
 */
#ifdef AMK_NATIVE_LEAVE_TESTS
#include "native.h"
#include "fd-native.h"
extern void amk_test_before_leave(uint32_t);
void amk_test_actual_fd_leave(uint32_t kind)
{
    struct aefd_native native = {0};
    const struct aefd_native_source sources[7] = {0};
    const unsigned generations[2] = {0};
    if (!aefd_native_init(&native, amk_native_call, NULL, UINT64_C(0xd1000101),
                          UINT64_C(0xd1010102), sources, generations, 0) ||
        aefd_native_enter(&native))
        __builtin_trap();
    amk_test_before_leave(kind);
    aefd_native_leave(&native);
    __builtin_trap();
}
#endif
#ifdef AMK_NATIVE_STDIO_TESTS
/* Compile with the prepared native-shaped musl FILE header and public headers.
 * Host-only _INTERNAL_SYSCALL_H excludes unused x86 raw inline definitions;
 * the actual upstream body has only its writev-call expression replaced. */
#include "native.h"
#include "stdio_impl.h"
#include <errno.h>
#include <string.h>
int32_t amk_test_actual_stdio_case(uint32_t kind)
{
    unsigned char buffer[32] = {'a', 'b', 'c'};
    const unsigned char payload[] = "0123456789ABCDEFGHIJ";
    FILE stream = {.fd = kind == 1 || kind == 3 ? 2 : 1,
                   .wbase = buffer,
                   .wpos = buffer + 3,
                   .buf = buffer,
                   .buf_size = sizeof(buffer)};
    errno = 0;
    if (kind == 4) {
        const struct iovec parts[2] = {{buffer, 3},
                                       {(void *)payload, sizeof(payload) - 1}};
        return amk_native_vector_write(1, parts, 2) == -1 && errno == EIO ? 0
                                                                          : 3;
    }
    size_t written = __stdio_write(&stream, payload, sizeof(payload) - 1);
    if (kind < 2)
        return written == sizeof(payload) - 1 && !(stream.flags & F_ERR) &&
                       stream.wpos == buffer && stream.wbase == buffer &&
                       stream.wend == buffer + sizeof(buffer)
                   ? 0
                   : 1;
    return written == (kind == 3 ? 4U : 0U) && (stream.flags & F_ERR) &&
                   !stream.wpos && !stream.wbase && !stream.wend &&
                   errno == (kind == 3 ? EPIPE : EIO)
               ? 0
               : 2;
}
#endif
