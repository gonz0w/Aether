/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-startup.h"
_Static_assert(sizeof(long) == 8, "native identity requires64-bit long");

static int consume(struct aefd_startup *b, struct aefd_io io)
{
    size_t offset = 0;
    for (unsigned attempt = 0; attempt < AEFD_IO_BUDGET; ++attempt) {
        size_t goal = offset < 16 ? 16 : AEFD_STARTUP_BYTES;
        int64_t count = io.read(io.context, b->scratch + offset, goal - offset);
        if (count > 0 && (uint64_t)count <= AEFD_STARTUP_BYTES - offset) {
            offset += (size_t)count;
            if (offset == 16 &&
                (memcmp(b->scratch, AEFD_STARTUP_MAGIC, 8) ||
                 aether_fs_session_u32(b->scratch + 8) != 1 ||
                 aether_fs_session_u32(b->scratch + 12) != AEFD_STARTUP_BYTES))
                return -1;
            if (offset == AEFD_STARTUP_BYTES)
                return 1;
        } else if (count != -11 || io.wait(io.context, 0)) {
            return 0;
        }
    }
    return 0;
}
int64_t aefd_startup_start(struct aefd_startup *b, aefd_native_call call,
                           void *owner, struct aefd_startup_auxv observed)
{
    if (!b)
        return -22;
    if (b->phase || b->context.state || b->context.native.initialized ||
        b->context.session.initialized || b->context.client.generation ||
        b->context.client.workspace || b->context.client.live)
        return -16;
    b->phase = 1;
    b->status = -22;
    struct aefd_native guard = {0};
    struct aefd_native_source sources[7] = {0};
    unsigned history[2] = {0};
    if (!aefd_native_init(&guard, call, owner, observed.input, observed.output,
                          sources, history, 0))
        goto done;
    struct aefd_io io = aefd_native_io(&guard);
    b->status = aefd_native_enter(&guard);
    if (b->status)
        goto cleanup;
    if (!observed.memory) {
        b->status = -22;
        goto cleanup;
    }
    int64_t pid = call(owner, 0x10027, 0, 0, 0, 0);
    int64_t parent = call(owner, 0x1006e, 0, 0, 0, 0);
    b->status = -5;
    if (pid <= 0 || parent <= 0)
        goto cleanup;
    int complete = consume(b, io);
    if (complete != 1) {
        b->status = complete < 0 ? -22 : -5;
        goto cleanup;
    }
    const unsigned char *raw = b->scratch;
    struct aether_fs_session_identity identity;
    b->status = -22;
    if (!aether_fs_session_decode(raw + 16, 32, observed.memory, (long)pid,
                                  (long)parent, &identity) ||
        aether_fs_session_u32(raw + 300) !=
#ifdef AEFD_TERMINAL_MODE_BINDINGS
            AEFD_MODE_CONTROL
#else
            0
#endif
    )
        goto cleanup;
    uint32_t factory = aether_fs_session_u32(raw + 296);
    if (factory != (identity.slot == 1 ? UINT32_C(0x76050001) : 0))
        goto cleanup;
    for (unsigned i = 0; i < 7; ++i) {
        const unsigned char *s = raw + 176 + i * 16;
        sources[i] = (struct aefd_native_source){
            aether_fs_session_u32(s), aether_fs_session_u32(s + 4),
            aether_fs_session_u32(s + 8), aether_fs_session_u32(s + 12)};
    }
    history[0] = aether_fs_session_u32(raw + 288);
    history[1] = aether_fs_session_u32(raw + 292);
    b->status = aefd_context_init(
        &b->context, call, owner, observed.input, observed.output, raw + 48,
        128, aefd_word(raw + 48, 1), sources, history, factory);
    if (b->status)
        goto cleanup;
#ifdef AEFD_TERMINAL_MODE_BINDINGS
    b->context.mode_control = aether_fs_session_u32(raw + 300);
#endif
    b->identity = identity;
    b->phase = 2;
    /* The temporary guard relinquishes its channel borrow. Only the context
     * can use/close endpoints after startup. Restore failure is fail-stop. */
    aefd_native_leave(&guard);
    goto done;
cleanup:
    b->close_attempted = 1;
    b->closed = b->context.native.closed ? b->context.native.receipt
                                         : io.close(io.context);
    aefd_native_leave(&guard);
done:
    memset(b->scratch, 0, sizeof(b->scratch));
    if (b->phase != 2)
        b->phase = 3;
    return b->status;
}
