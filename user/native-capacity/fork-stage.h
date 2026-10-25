/* SPDX-License-Identifier: BSD-2-Clause */
/* Private musl staging hook; upstream _Fork owns post-copy TID repair. */
int copy_rebind(unsigned long, unsigned long, unsigned long, unsigned long *,
                unsigned long *);
static unsigned long fork_input, fork_output;
long __aether_fork_stage(void)
{
#ifdef PIPE_DASH_PARENT
    fork_input = input;
    fork_output = output;
#endif
#ifdef PIPE_INTERLEAVE
    unsigned char header[32] = {0};
    put(header, 0, 83);
    put(header, 4, 64);
    if (!move(header, sizeof header, 1))
        _exit(116);
#endif
#ifdef PIPE_LIVE_FDS
    if (!live_snapshot())
        _exit(116);
#endif
    unsigned long op = 0x23003, memory = 0, reader = 0, writer = 0;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    /* Copy resumes on a private stack; grant registers and buffer effects must
       be explicit before handing control back to upstream libc repair. */
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+D"(memory), "+S"(reader), "+d"(writer),
                           "+r"(r10), "+r"(r8), "+r"(r9)
                         :
                         : "rcx", "r11", "memory");
    if (!op && !copy_rebind(memory, reader, writer, &fork_input, &fork_output))
        _exit(114);
#ifdef PIPE_LIVE_FDS
    if (!op) {
        input = fork_input;
        output = fork_output;
#ifdef PIPE_DASH_PARENT
        dash_copy_ready();
#endif
    }
#endif
    return (long)op;
}
