/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-fork-stage.h"

static void put32(unsigned char *raw, unsigned offset, uint32_t value)
{
    for (unsigned i = 0; i < 4; ++i)
        raw[offset + i] = (unsigned char)(value >> (i * 8));
}
static int move(struct aefd_io io, unsigned char *raw, size_t length,
                int writing, unsigned *budget, int startup)
{
    size_t offset = 0;
    while (offset < length && *budget) {
        --*budget;
        size_t goal = startup && offset < 16 ? 16 : length;
        size_t chunk = goal - offset;
        if (chunk > 16)
            chunk = 16;
        int64_t count = writing ? io.write(io.context, raw + offset, chunk)
                                : io.read(io.context, raw + offset, chunk);
        if (count > 0 && (uint64_t)count <= chunk) {
            offset += (size_t)count;
            if (startup && offset == 16 &&
                (memcmp(raw, AEFD_STARTUP_MAGIC, 8) ||
                 aether_fs_session_u32(raw + 8) != 1 ||
                 aether_fs_session_u32(raw + 12) != AEFD_STARTUP_BYTES))
                return 0;
        } else if (count != -11 || io.wait(io.context, writing)) {
            return 0;
        }
    }
    return offset == length;
}
static int64_t parent_failure(struct aefd_fork *f)
{
    f->phase = AEFD_FORK_FAILED;
    f->status = -5;
    aefd_client_abort(&f->boot.context.client);
    aefd_native_leave(&f->boot.context.native);
    memset(f->boot.scratch, 0, sizeof f->boot.scratch);
    return f->status;
}
int64_t aefd_fork_arm(struct aefd_fork *f, struct aefd_startup_auxv observed)
{
    if (!f)
        return -22;
    struct aefd_startup *b = &f->boot;
    if (f->phase != AEFD_FORK_IDLE || b->context.native.active ||
        b->context.native.busy)
        return -16;
    if (b->phase != 2 || b->context.state != 1 || b->identity.slot != 1 ||
        b->context.client.live != 1 || b->context.native.retired ||
        observed.input != b->context.native.input ||
        observed.output != b->context.native.output)
        return -22;
    if (f->counter == UINT64_MAX)
        return -75;
    f->previous_mask = b->context.native.saved_mask;
    int64_t result = aefd_native_enter(&b->context.native);
    if (result)
        return parent_failure(f);
    f->call = b->context.native.call;
    f->owner = b->context.native.context;
    int64_t pid = f->call(f->owner, 0x10027, 0, 0, 0, 0);
    int64_t parent = f->call(f->owner, 0x1006e, 0, 0, 0, 0);
    unsigned char *raw = b->scratch;
    memset(raw, 0, AEFD_STARTUP_BYTES);
    memcpy(raw, AEFD_STARTUP_MAGIC, 8);
    put32(raw, 8, 1);
    put32(raw, 12, AEFD_STARTUP_BYTES);
    memcpy(raw + 16, "AEFSH001", 8);
    put32(raw, 24, 29);
    put32(raw, 28, 7);
    put32(raw, 32, b->identity.slot);
    put32(raw, 36, b->identity.epoch);
    put32(raw, 40, 7);
    put32(raw, 44, b->identity.shell_generation);
    result = aefd_session_snapshot(&b->context.session, raw + 48, 128, 0);
    for (unsigned i = 0; i < 7; ++i) {
        struct aefd_native_source source = b->context.native.sources[i];
        put32(raw, 176 + i * 16, source.reference);
        put32(raw, 180 + i * 16, source.selector);
        put32(raw, 184 + i * 16, source.rights);
        put32(raw, 188 + i * 16, source.bound);
    }
    put32(raw, 288, b->context.native.generations[0]);
    put32(raw, 292, b->context.native.generations[1]);
    put32(raw, 296, b->context.native.factory);
    if (result || !aefd_fork_encode(raw, 304, raw, 304, observed, (long)pid,
                                    (long)parent, f->counter + 1)) {
        if (!b->context.client.live)
            return parent_failure(f);
        aefd_native_leave(&b->context.native);
        b->context.native.saved_mask = f->previous_mask;
        memset(raw, 0, AEFD_STARTUP_BYTES);
        return -22;
    }
    f->parent = observed;
    f->parent_pid = (long)pid;
    f->sequence = ++f->counter;
    f->phase = AEFD_FORK_SENDING;
    f->status = 0;
    f->budget = AEFD_IO_BUDGET;
    if (!move(aefd_native_io(&b->context.native), raw, 304, 1, &f->budget, 0))
        return parent_failure(f);
    f->phase = AEFD_FORK_ARMED;
    return 0;
}
int64_t aefd_fork_parent(struct aefd_fork *f, int64_t native_result)
{
    if (!f || f->phase != AEFD_FORK_ARMED)
        return -16;
    if (native_result != -11 &&
        (native_result <= 0 || native_result > 110 ||
         !aether_fs_session_child_pid((long)native_result)))
        return parent_failure(f);
    f->phase = AEFD_FORK_PARENT;
    int64_t result;
    if (!move(aefd_native_io(&f->boot.context.native), f->boot.scratch, 32, 0,
              &f->budget, 0) ||
        !aefd_fork_parent_reply(f->boot.scratch, 32, f->sequence, native_result,
                                &result))
        return parent_failure(f);
    aefd_native_leave(&f->boot.context.native);
    f->boot.context.native.saved_mask = f->previous_mask;
    memset(f->boot.scratch, 0, sizeof f->boot.scratch);
    f->phase = AEFD_FORK_IDLE;
    f->status = result;
    return result;
}
static int child_grants(struct aefd_fork *f, struct aefd_startup_auxv grants,
                        long pid, long parent)
{
    if (!aether_fs_session_child_pid(pid) || parent != f->parent_pid ||
        grants.memory == f->parent.memory || !grants.input || !grants.output ||
        grants.input == grants.output || grants.input == f->parent.input ||
        grants.input == f->parent.output || grants.output == f->parent.input ||
        grants.output == f->parent.output)
        return 0;
    unsigned value = (unsigned)pid - 1;
    return grants.memory == (UINT64_C(0x40000000) | (uint64_t)(value / 7) << 8 |
                             (value % 7 + 1));
}
int64_t aefd_fork_child(struct aefd_fork *f, struct aefd_startup_auxv grants,
                        aefd_fork_rebind rebind, void *rebind_context)
{
    if (!f || f->phase != AEFD_FORK_ARMED)
        return -16;
    struct aefd_startup *b = &f->boot;
    /* This branch is entered only on native child return0. From this point no
     * inherited context callback, mask leave, abort or cleanup may execute. */
    f->phase = AEFD_FORK_CHILD;
    b->phase = 4;
    b->context.state = 4;
    f->status = -5;
    struct aefd_native guard = {0};
    struct aefd_native_source sources[7] = {0};
    unsigned history[2] = {0};
    int borrowed = 0, reset = 0, constructed = 0;
    if (!f->call || !f->sequence ||
        aefd_word(b->scratch + 296, 0) != f->sequence)
        goto failed;
    int64_t pid = f->call(f->owner, 0x10027, 0, 0, 0, 0);
    int64_t parent = f->call(f->owner, 0x1006e, 0, 0, 0, 0);
    if (!child_grants(f, grants, (long)pid, (long)parent) || !rebind ||
        !rebind(rebind_context, f->parent, grants))
        goto failed;
    /* Only now do the actual new grants become a temporary channel borrow. */
    if (!aefd_native_init(&guard, f->call, f->owner, grants.input,
                          grants.output, sources, history, 0))
        goto failed;
    borrowed = 1;
    if (aefd_native_enter(&guard))
        goto failed;
    memmove(b->context.workspace, b->scratch, AEFD_STARTUP_BYTES);
    memset(b->scratch, 0, AEFD_STARTUP_BYTES);
    if (!move(aefd_native_io(&guard), b->scratch, 304, 0, &f->budget, 1))
        goto failed;
    struct aether_fs_session_identity identity;
    if (!aefd_fork_child_match(b->context.workspace, 304, f->parent,
                               f->parent_pid, b->scratch, 304, grants,
                               (long)pid, &identity))
        goto failed;
    for (unsigned i = 0; i < 7; ++i) {
        const unsigned char *raw = b->scratch + 176 + i * 16;
        sources[i] = (struct aefd_native_source){
            aether_fs_session_u32(raw), aether_fs_session_u32(raw + 4),
            aether_fs_session_u32(raw + 8), aether_fs_session_u32(raw + 12)};
    }
    history[0] = aether_fs_session_u32(b->scratch + 288);
    history[1] = aether_fs_session_u32(b->scratch + 292);
    /* Native ownership and exact correspondence now justify rebuilding only
     * this child's private metadata. Never execute inherited borrow cleanup. */
    memset(&b->context, 0, sizeof b->context);
    reset = 1;
    if (aefd_context_init(&b->context, f->call, f->owner, grants.input,
                          grants.output, b->scratch + 48, 128,
                          aefd_word(b->scratch + 48, 1), sources, history, 0))
        goto failed;
    constructed = 1;
    b->context.native.active = 1;
    b->context.native.saved_mask = guard.saved_mask;
    /* Transfer the one masked new-channel borrow without restoring/leaving it.
     * The temporary metadata must no longer be usable as a second owner. */
    guard.active = 0;
    guard.initialized = 0;
    b->identity = identity;
    if (!aefd_fork_ready_encode(b->scratch, 32, f->sequence, (long)pid) ||
        !move(aefd_native_io(&b->context.native), b->scratch, 32, 1, &f->budget,
              0))
        goto failed;
    memset(b->scratch, 0, sizeof b->scratch);
    b->phase = 2;
    b->status = 0;
    f->phase = AEFD_FORK_READY;
    f->status = 0;
    aefd_native_leave(&b->context.native);
    return 0;
failed:
    if (borrowed) {
        b->close_attempted = 1;
        if (constructed) {
            aefd_client_abort(&b->context.client);
            b->closed = b->context.native.receipt;
            aefd_native_leave(&b->context.native);
        } else {
            struct aefd_io io = aefd_native_io(&guard);
            b->closed = reset && b->context.native.closed
                            ? b->context.native.receipt
                            : io.close(io.context);
            aefd_native_leave(&guard);
        }
    }
    memset(b->scratch, 0, sizeof b->scratch);
    memset(b->context.workspace, 0, sizeof b->context.workspace);
    b->phase = 4;
    b->context.state = 4;
    f->phase = AEFD_FORK_FAILED;
    return f->status;
}
