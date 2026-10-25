/* SPDX-License-Identifier: BSD-2-Clause */
/* Private capacity witness, not a libc or service implementation. */
#include <stdint.h>
#include <string.h>
#include <sys/auxv.h>
#include <unistd.h>
#include "../native-memory/adapter.h"

#ifdef PIPE_PUBLIC_FORK
#include "fork-stage.h"
#endif

static _Thread_local volatile unsigned tls_marker = 19;

#ifdef PIPE_DISPATCH
static int fragment(unsigned long cap, unsigned char *bytes, unsigned count,
                    int writing)
{
    unsigned used = 0;
    for (unsigned attempt = 0; attempt < 100000; ++attempt) {
        unsigned chunk = count - used;
        unsigned bound = writing ? 7 : 5;
        if (chunk > bound)
            chunk = bound;
        long n = memtrap(writing ? 0x24002 : 0x24001, cap,
                         (unsigned long)(bytes + used), chunk, 0);
        if (n == -11) {
            memtrap(0x1fffe, 0, 0, 0, 0);
            continue;
        }
        if (n <= 0 || (unsigned long)n > chunk)
            return -1;
        used += (unsigned)n;
        if (used == count)
            return 0;
    }
    return -1;
}

static int pipe_call(unsigned long input, unsigned long output,
                     unsigned generation, unsigned object, unsigned end,
                     unsigned op, unsigned count, unsigned char *data)
{
    uint32_t frame[8] = {op,
                         0x79000000U | (object << 16) | (generation << 8) | end,
                         2 + object * 2 + end,
                         count,
                         0,
                         0,
                         0,
                         0};
    if (op == 2)
        memcpy((unsigned char *)frame + 16, data, count);
    if (fragment(output, (unsigned char *)frame, 32, 1) ||
        fragment(input, (unsigned char *)frame, 32, 0))
        return -1;
    int result = (int32_t)frame[0];
    if (result < 0) {
        for (unsigned i = 1; i < 8; ++i)
            if (frame[i])
                return -1;
        return result;
    }
    if ((unsigned)result > count || frame[1] || frame[2] || frame[3])
        return -1;
    if (op == 1 && result)
        memcpy(data, (unsigned char *)frame + 16, (unsigned)result);
    return result;
}

static int pipe_probe(unsigned slot, unsigned generation, unsigned long input,
                      unsigned long output)
{
    unsigned char expected[] = "pipe data\n";
    unsigned char buffer[16];
#ifdef PIPE_EARLY_READER
    if (slot == 4) {
#ifdef PIPE_READER_EXIT
        return 0;
#else
        return pipe_call(input, output, generation, 1, 1, 3, 0, buffer) == 0
                   ? 0
                   : 98;
#endif
    }
#endif
#ifdef PIPE_COPY
    /* Fork retains all four ends, even the CLOEXEC alias. Close only this
       child's unused holders before entering its pipeline role. */
    for (unsigned object = 0; object < 2; ++object)
        for (unsigned end = 1; end <= 2; ++end) {
            int keep = (slot == 2 && object == 0 && end == 2) ||
                       (slot == 3 && ((object == 0 && end == 1) ||
                                      (object == 1 && end == 2))) ||
                       (slot == 4 && object == 1 && end == 1);
            if (!keep &&
                pipe_call(input, output, generation, object, end, 3, 0, buffer))
                return 99;
        }
#endif
    if (slot == 2) {
        if (pipe_call(input, output, generation, 0, 2, 2, 10, expected) != 10)
            return 90;
#ifdef PIPE_EARLY_READER
        if (pipe_call(input, output, generation, 0, 2, 2, 10, expected) != -32)
            return 96;
#endif
        if (pipe_call(input, output, generation, 0, 2, 3, 0, buffer) != 0)
            return 90;
        return 0;
    }
#ifdef PIPE_STOP_REQUEST
    const unsigned expected_count = 0;
#else
    const unsigned expected_count = 10;
#endif
    unsigned total = 0, object = slot == 3 ? 0 : 1;
    for (;;) {
        int count =
            pipe_call(input, output, generation, object, 1, 1, 16, buffer);
        if (count < 0)
            return 91;
        if (!count)
            break;
        if (total + (unsigned)count > expected_count ||
            memcmp(buffer, expected + total, (unsigned)count))
            return 92;
        total += (unsigned)count;
#ifdef PIPE_EARLY_READER
        if (total != 10 || pipe_call(input, output, generation, 1, 2, 2,
                                     (unsigned)count, buffer) != -32)
            return 97;
        break;
#endif
        if (slot == 3 && pipe_call(input, output, generation, 1, 2, 2,
                                   (unsigned)count, buffer) != count)
            return 93;
    }
    if (total != expected_count ||
        pipe_call(input, output, generation, object, 1, 3, 0, buffer) != 0)
        return 94;
    if (slot == 3 &&
        pipe_call(input, output, generation, 1, 2, 3, 0, buffer) != 0)
        return 95;
    return 0;
}
#endif

int main(int argc, char **argv)
{
    if (tls_marker != 19)
        return 81;
    tls_marker = 23;
    if (argc != 3)
        return 70;
    unsigned slot = (unsigned)(argv[1][0] - '0');
    unsigned generation = (unsigned)(argv[2][0] - '0');
    if (slot >= 5 || generation < 1 || generation >
#ifdef SESSION_LIFETIME
        15
#else
        3
#endif
    )
        return 71;
    if ((unsigned)getpid() != generation * 6 + slot + 1 ||
        (unsigned)getppid() !=
#ifdef PIPE_REPLACEMENT
            generation * 6 + 1
#else
            6
#endif
    )
        return 72;
    if (memtrap(0x10027, 1, 2, 3, 4) != getpid())
        return 82;
    const unsigned char *entropy = (const unsigned char *)getauxval(AT_RANDOM);
    for (unsigned i = 0; i < 16; ++i)
        if (entropy[i] != slot + 1)
            return 73;
    unsigned long input = getauxval(0xa001), output = getauxval(0xa002);
    if (!input || !output)
        return 74;
    /* The adjacent writer belongs to the supervisor, not this worker. */
    if (memtrap(0x24003, input + 1, 0, 0, 0) != -13 ||
        memtrap(0x24000, 0xd001, 0, 0, 0) != -13 ||
        memtrap(0x20001, 0xb0000101, 0, 0, 0) != -13)
        return 75;
#ifdef PIPE_REPLACEMENT
    if (strcmp(argv[0], "replacement"))
        return 105;
    unsigned char installed[64], expected[64] = {0};
    if (fragment(input, installed, sizeof installed, 0))
        return 105;
    for (unsigned binding = 0; binding < 7; ++binding) {
        int keep =
#ifndef PIPE_LIBC
            binding < 3 ||
#endif
            (slot == 2 && binding == 4) ||
            (slot == 3 && (binding == 3 || binding == 6)) ||
            (slot == 4 && binding == 5);
        if (keep) {
            expected[binding * 4] = (unsigned char)binding;
            expected[binding * 4 + 2] = 1;
        }
    }
    if (memcmp(installed, expected, sizeof installed))
        return 105;
#endif
#ifdef SESSION_LIFETIME
    if (memtrap(0x26000, 0xf001, 0, 0, 0) != -38)
        return 83;
#endif
    uint64_t reply[2] = {(uint64_t)getpid(), (uint64_t)slot + 1};
#ifdef SESSION_STALE_ID
    if (generation == 4)
        reply[0] -= 6;
#endif
    if (memtrap(0x24002, output, (unsigned long)reply, sizeof(reply), 0) != 16)
        return 76;
    if (memtrap(0x20004, 0, 0, 0, 0) != 0)
        return 77;
#ifdef PIPE_COPY
    volatile unsigned char table[64] = {0};
    if (slot == 0) {
        for (unsigned binding = 0; binding < 7; ++binding) {
            table[binding * 4] = (unsigned char)binding;
            table[binding * 4 + 2] = 1;
        }
        table[40] = 3;
        table[41] = 1;
        table[42] = 1;
        for (unsigned child = 2; child <= 4; ++child) {
            if (fragment(output, (unsigned char *)table, sizeof(table), 1))
                return 100;
            unsigned long op = 0x23003, memory = 0, reader = 0, writer = 0;
#ifdef PIPE_PUBLIC_FORK
            unsigned long old_memory = getauxval(0xa000);
            fork_input = input;
            fork_output = output;
            op = (unsigned long)fork();
            memory = getauxval(0xa000);
            reader = fork_input;
            writer = fork_output;
            if (gettid() != getpid())
                return 115;
#else
            register unsigned long r10 __asm__("r10") = 0;
            register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
            /* Kernel resumes the same instruction in a private copied stack;
               grants are explicit outputs, all buffer effects clobber memory.
             */
            __asm__ __volatile__("int $0x81"
                                 : "+a"(op), "+D"(memory), "+S"(reader),
                                   "+d"(writer), "+r"(r10), "+r"(r8), "+r"(r9)
                                 :
                                 : "rcx", "r11", "memory");
#endif
            if (tls_marker != 23 || table[40] != 3 || table[41] != 1 ||
                table[42] != 1)
                return 101;
            if (op == 0) {
                if ((unsigned)getpid() != generation * 6 + child + 1 ||
                    (unsigned)getppid() != generation * 6 + 1 ||
#ifdef PIPE_PUBLIC_FORK
                    memory == old_memory || getauxval(0xa001) != reader ||
                    getauxval(0xa002) != writer ||
#else
                    memory == getauxval(0xa000) ||
#endif
                    memtrap(0x24001, input, 0, 0, 0) != -13 ||
                    memtrap(0x24002, output, 0, 0, 0) != -13)
                    return 102;
                tls_marker = 47;
                table[41] = 0;
                input = reader;
                output = writer;
                slot = child;
                uint64_t child_report[2] = {(uint64_t)getpid(), slot + 1};
                if (memtrap(0x24002, output, (uintptr_t)child_report, 16, 0) !=
                        16 ||
                    memtrap(0x20004, 0, 0, 0, 0))
                    return 103;
                break;
            }
            if (op != generation * 6 + child + 1)
                return 104;
        }
    }
#endif
    unsigned char token = 0;
    for (unsigned i = 0; i < 100000; ++i) {
        long n = memtrap(0x24001, input, (unsigned long)&token, 1, 0);
        if (n == 1) {
#ifdef PIPE_EXEC
            if (token == 2 && slot >= 2) {
                memset((void *)table, 0, sizeof table);
                for (unsigned binding = 0; binding < 7; ++binding) {
                    int keep =
#ifndef PIPE_LIBC
                        binding < 3 ||
#endif
                        (slot == 2 && binding == 4) ||
                        (slot == 3 && (binding == 3 || binding == 6)) ||
                        (slot == 4 && binding == 5);
                    table[binding * 4] = (unsigned char)binding;
                    table[binding * 4 + 1] = (unsigned char)!keep;
                    table[binding * 4 + 2] = 1;
                }
                table[40] = 3;
                table[41] = 1;
                table[42] = 1;
                if (fragment(output, (unsigned char *)table, sizeof table, 1))
                    return 106;
                memtrap(0x23003, 0, 0, 0, 0);
                return 106; /* Successful image replacement never returns here.
                             */
            }
#endif
            if (token != 1)
                return 78;
#ifdef PIPE_COPY
            if (slot == 0 && (tls_marker != 23 || table[41] != 1))
                return 101;
#endif
#ifdef PIPE_DISPATCH
            if (slot >= 2)
                return pipe_probe(slot, generation, input, output);
#endif
            return 0;
        }
        if (n != -11)
            return 79;
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
    return 80;
}
