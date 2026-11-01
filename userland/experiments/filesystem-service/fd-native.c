/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-native.h"

static uint32_t word(const unsigned char *b, unsigned i)
{
    return (uint32_t)b[i] | (uint32_t)b[i + 1] << 8 | (uint32_t)b[i + 2] << 16 |
           (uint32_t)b[i + 3] << 24;
}
static void put(unsigned char *b, unsigned i, uint32_t value)
{
    for (unsigned j = 0; j < 4; ++j)
        b[i + j] = (unsigned char)(value >> (8 * j));
}
static uint32_t pipe_ref(unsigned object, unsigned generation, unsigned end)
{
    return UINT32_C(0x79000000) | object << 16 | generation << 8 | end;
}
static unsigned rights(unsigned i)
{
    return i == 0 || i == 3 || i == 5 ? 1U : 2U;
}
int aefd_native_init(struct aefd_native *n, aefd_native_call call,
                     void *context, uint64_t input, uint64_t output,
                     const struct aefd_native_source sources[7],
                     const unsigned generations[2], uint32_t factory)
{
    if (!n || n->initialized || !call || !input || !output || input == output ||
        !sources || !generations || generations[0] > 9 || generations[1] > 9 ||
        (factory && factory != UINT32_C(0x76050001)))
        return 0;
    for (unsigned i = 0; i < 7; ++i) {
        struct aefd_native_source s = sources[i];
        if (!s.reference) {
            if (s.selector || s.rights || s.bound)
                return 0;
            continue;
        }
        if (s.selector != i || s.rights != rights(i) || s.bound != 16)
            return 0;
        for (unsigned j = 0; j < i; ++j)
            if (sources[j].reference == s.reference)
                return 0;
        if (i >= 3) {
            unsigned object = (i - 3) / 2, end = (i - 3) % 2 + 1;
            if (!generations[object] ||
                s.reference != pipe_ref(object, generations[object], end))
                return 0;
        }
    }
    n->call = call;
    n->context = context;
    n->input = input;
    n->output = output;
    memcpy(n->sources, sources, sizeof(n->sources));
    memcpy(n->generations, generations, sizeof(n->generations));
    n->factory = factory;
    n->initialized = 1;
    return 1;
}
static struct aefd_close_result close_transport(void *context)
{
    struct aefd_native *n = context;
    if (!n->initialized)
        return (struct aefd_close_result){-9, -9};
    if (!n->closed) {
        n->closed = n->retired = 1;
        n->receipt.input = n->call(n->context, 0x24003, n->input, 0, 0, 0);
        n->receipt.output = n->call(n->context, 0x24003, n->output, 0, 0, 0);
    }
    return n->receipt;
}
static int ready(struct aefd_native *n)
{
    return n->initialized && !n->retired && n->active && !n->busy;
}
int64_t aefd_native_enter(struct aefd_native *n)
{
    if (!n || !n->initialized || n->retired)
        return -5;
    if (n->active || n->busy)
        return -16;
    uint64_t mask = UINT64_MAX;
    n->active = 1;
    int64_t result = n->call(n->context, 0x1000e, 0, (uint64_t)(uintptr_t)&mask,
                             (uint64_t)(uintptr_t)&n->saved_mask, 8);
    if (result) {
        n->active = 0;
        n->retired = 1;
        return result < 0 && result >= -4095 ? result : -5;
    }
    return 0;
}
void aefd_native_leave(struct aefd_native *n)
{
    if (!n || !n->initialized || !n->active)
        return;
    if (n->busy || n->call(n->context, 0x1000e, 2,
                           (uint64_t)(uintptr_t)&n->saved_mask, 0, 8)) {
        (void)close_transport(n);
        (void)n->call(n->context, 0x100e7, 125, 0, 0, 0);
        __builtin_trap();
    }
    n->active = 0;
}
static int64_t transfer(struct aefd_native *n, unsigned char *data,
                        size_t count, int writing)
{
    size_t chunk = count > 16 ? 16 : count;
    if (!chunk)
        return 0;
    int64_t result = n->call(n->context, writing ? 0x24002 : 0x24001,
                             writing ? n->output : n->input,
                             (uint64_t)(uintptr_t)data, chunk, 0);
    if (result > (int64_t)chunk || result < -4095) {
        n->retired = 1;
        return -5;
    }
    return result;
}
static int wait_endpoint(struct aefd_native *n, int writing)
{
    return n->call(n->context, 0x24004, writing ? n->output : n->input, 0, 0,
                   0) == 0
               ? 0
               : -1;
}
static int64_t read_file(void *context, unsigned char *data, size_t count)
{
    struct aefd_native *n = context;
    if (!ready(n) || (!data && count))
        return -5;
    n->busy = 1;
    int64_t result = transfer(n, data, count, 0);
    n->busy = 0;
    return result;
}
static int64_t write_file(void *context, const unsigned char *data,
                          size_t count)
{
    struct aefd_native *n = context;
    if (!ready(n) || (!data && count))
        return -5;
    n->busy = 1;
    /* Native ABI borrows a const input for write, never modifies it. */
    int64_t result = transfer(n, (unsigned char *)(uintptr_t)data, count, 1);
    n->busy = 0;
    return result;
}
static int wait_file(void *context, int writing)
{
    struct aefd_native *n = context;
    if (!ready(n))
        return -1;
    n->busy = 1;
    int result = wait_endpoint(n, writing);
    n->busy = 0;
    return result;
}
struct aefd_io aefd_native_io(struct aefd_native *n)
{
    return (struct aefd_io){n, read_file, write_file, wait_file,
                            close_transport};
}
static int move(struct aefd_native *n, unsigned char bytes[32], int writing)
{
    size_t offset = 0;
    for (unsigned attempt = 0; attempt < AEFD_IO_BUDGET; ++attempt) {
        int64_t result = transfer(n, bytes + offset, 32 - offset, writing);
        if (result > 0 && result <= 16 && (uint64_t)result <= 32 - offset) {
            offset += (size_t)result;
            if (offset == 32)
                return 1;
        } else if (result != -11 || wait_endpoint(n, writing)) {
            return 0;
        }
    }
    return 0;
}
static int exchange(struct aefd_native *n, unsigned char bytes[32])
{
    n->busy = 1;
    int ok = move(n, bytes, 1) && move(n, bytes, 0);
    n->busy = 0;
    if (!ok)
        n->retired = 1;
    return ok;
}
static int source_ok(struct aefd_native *n, unsigned kind, unsigned selector)
{
    return ready(n) && selector < 7 && n->sources[selector].reference &&
           (kind == (selector < 3 ? AEFD_BIND_CONSOLE : AEFD_BIND_PIPE)
#ifdef AEFD_TERMINAL_BINDINGS
            || (selector < 3 && kind == AEFD_BIND_TERMINAL)
#endif
           );
}
static struct aefd_stream_result stream(struct aefd_native *n, unsigned kind,
                                        unsigned selector, unsigned char *out,
                                        const unsigned char *in, size_t count,
                                        unsigned op)
{
    struct aefd_stream_result unknown = {0, -5};
    if (!source_ok(n, kind, selector))
        return unknown;
    if ((op == 1 && n->sources[selector].rights != 1) ||
        (op == 2 && n->sources[selector].rights != 2))
        return (struct aefd_stream_result){1, -9};
    size_t chunk = count > 16 ? 16 : count;
    unsigned char bytes[32] = {0};
    put(bytes, 0, op);
    put(bytes, 4, n->sources[selector].reference);
    put(bytes, 8, selector);
    put(bytes, 12, (uint32_t)chunk);
    if (op == 2 && chunk)
        memcpy(bytes + 16, in, chunk);
    if (!exchange(n, bytes))
        return unknown;
    uint32_t raw = word(bytes, 0);
    int64_t result =
        raw <= INT32_MAX ? (int64_t)raw : (int64_t)raw - INT64_C(4294967296);
    unsigned start = op == 1 && result > 0 && (uint64_t)result <= chunk
                         ? 16U + (unsigned)result
                         : 16U;
    int valid = result >= -4095 && (result <= 0 || (uint64_t)result <= chunk);
    for (unsigned i = 4; i < 16; ++i)
        valid = valid && !bytes[i];
    for (unsigned i = start; i < 32; ++i)
        valid = valid && !bytes[i];
    if (!valid || (op == 3 && result != 0)) {
        n->retired = 1;
        return unknown;
    }
    if (op == 1 && result > 0)
        memcpy(out, bytes + 16, (size_t)result);
    if (op == 3)
        memset(&n->sources[selector], 0, sizeof(n->sources[selector]));
    return (struct aefd_stream_result){1, result};
}
static struct aefd_stream_result read_stream(void *context, unsigned kind,
                                             unsigned selector,
                                             unsigned char *out, size_t count)
{
    return stream(context, kind, selector, out, NULL, count, 1);
}
static struct aefd_stream_result write_stream(void *context, unsigned kind,
                                              unsigned selector,
                                              const unsigned char *in,
                                              size_t count)
{
    return stream(context, kind, selector, NULL, in, count, 2);
}
static struct aefd_stream_close_result
close_stream(void *context, unsigned kind, unsigned selector)
{
    struct aefd_stream_result result =
        stream(context, kind, selector, NULL, NULL, 0, 3);
    return (struct aefd_stream_close_result){
        result.complete, result.complete && !result.result, result.result};
}
static struct aefd_pipe_result create_pipe(void *context)
{
    struct aefd_native *n = context;
    struct aefd_pipe_result unknown = {0, -5, 0, 0};
    if (!ready(n))
        return unknown;
    if (!n->factory)
        return (struct aefd_pipe_result){1, -38, 0, 0};
    unsigned char bytes[32] = {0};
    put(bytes, 0, 82);
    put(bytes, 4, n->factory);
    put(bytes, 8, 1);
    if (!exchange(n, bytes))
        return unknown;
    if (word(bytes, 0) == UINT32_C(0xffffffe9)) {
        int valid = 1;
        for (unsigned i = 4; i < 32; ++i)
            valid = valid && !bytes[i];
        if (valid)
            return (struct aefd_pipe_result){1, -23, 0, 0};
    }
    unsigned gen = word(bytes, 4), rsel = word(bytes, 16);
    if (!word(bytes, 0) && (rsel == 3 || rsel == 5)) {
        unsigned object = (rsel - 3) / 2;
        if (gen >= 1 && gen <= 9 && gen == n->generations[object] + 1 &&
            !n->sources[rsel].reference && !n->sources[rsel + 1].reference &&
            word(bytes, 8) == pipe_ref(object, gen, 1) &&
            word(bytes, 12) == pipe_ref(object, gen, 2) &&
            word(bytes, 20) == rsel + 1 && word(bytes, 24) == 256 &&
            word(bytes, 28) == 16) {
            n->sources[rsel] =
                (struct aefd_native_source){word(bytes, 8), rsel, 1, 16};
            n->sources[rsel + 1] =
                (struct aefd_native_source){word(bytes, 12), rsel + 1, 2, 16};
            n->generations[object] = gen;
            return (struct aefd_pipe_result){1, 0, rsel, rsel + 1};
        }
    }
    n->retired = 1;
    return unknown;
}
struct aefd_adapters aefd_native_adapters(struct aefd_native *n)
{
    return (struct aefd_adapters){{n, read_stream},
                                  {n, write_stream},
                                  {n, close_stream},
                                  {n, create_pipe}};
}
