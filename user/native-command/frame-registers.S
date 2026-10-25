/* SPDX-License-Identifier: BSD-2-Clause */
/* Single-context user fixture. No C calls while registers/red zone are live. */
.text
.p2align 4
.global frame_register_checks
.type frame_register_checks,@function
frame_register_checks:
    pushq %rbx
    pushq %rbp
    pushq %r12
    pushq %r13
    pushq %r14
    pushq %r15
    fxsave64 saved_fp(%rip)
    movq %rsp, expected_rsp(%rip)
    movq $0, entry_flags(%rip)
    fninit
    fld1
    ldmxcsr test_mxcsr(%rip)
    pcmpeqd %xmm0, %xmm0
    pcmpeqd %xmm1, %xmm1
    pcmpeqd %xmm2, %xmm2
    pcmpeqd %xmm3, %xmm3
    pcmpeqd %xmm4, %xmm4
    pcmpeqd %xmm5, %xmm5
    pcmpeqd %xmm6, %xmm6
    pcmpeqd %xmm7, %xmm7
    pcmpeqd %xmm8, %xmm8
    pcmpeqd %xmm9, %xmm9
    pcmpeqd %xmm10, %xmm10
    pcmpeqd %xmm11, %xmm11
    pcmpeqd %xmm12, %xmm12
    pcmpeqd %xmm13, %xmm13
    pcmpeqd %xmm14, %xmm14
    pcmpeqd %xmm15, %xmm15
    movabsq $0x1122334455660101, %rbx
    movabsq $0x1122334455660102, %rcx
    movabsq $0x1122334455660106, %rbp
    movabsq $0x112233445566010a, %r11
    movabsq $0x112233445566010b, %r12
    movabsq $0x112233445566010c, %r13
    movabsq $0x112233445566010d, %r14
    movabsq $0x112233445566010e, %r15
    leaq register_handler(%rip), %rdi
    leaq __restore_rt(%rip), %rsi
    movq $10, %rdx
    movq $0, %r8
    movq $0, %r9
    movq $0, %r10
    pushq $0xed7
    popfq
    movabsq $0x5a5a5a5a5a5a5a5a, %rax
    movq %rax, -8(%rsp)
    movq %rax, -16(%rsp)
    movq %rax, -24(%rsp)
    movq %rax, -32(%rsp)
    movq %rax, -40(%rsp)
    movq %rax, -48(%rsp)
    movq %rax, -56(%rsp)
    movq %rax, -64(%rsp)
    movq %rax, -72(%rsp)
    movq %rax, -80(%rsp)
    movq %rax, -88(%rsp)
    movq %rax, -96(%rsp)
    movq %rax, -104(%rsp)
    movq %rax, -112(%rsp)
    movq %rax, -120(%rsp)
    movq %rax, -128(%rsp)
    movq $0x29000, %rax
    int $0x81
    movq %rax, seen+0(%rip)
    movq %rbx, seen+8(%rip)
    movq %rcx, seen+16(%rip)
    movq %rdx, seen+24(%rip)
    movq %rsi, seen+32(%rip)
    movq %rdi, seen+40(%rip)
    movq %rbp, seen+48(%rip)
    movq %r8, seen+56(%rip)
    movq %r9, seen+64(%rip)
    movq %r10, seen+72(%rip)
    movq %r11, seen+80(%rip)
    movq %r12, seen+88(%rip)
    movq %r13, seen+96(%rip)
    movq %r14, seen+104(%rip)
    movq %r15, seen+112(%rip)
    movq %rsp, seen+120(%rip)
    fxsave64 seen_fp(%rip)
    leaq -128(%rsp), %rsp
    pushfq
    popq seen_flags(%rip)
    leaq 128(%rsp), %rsp
    cld
    cmpq $0xed7, seen_flags(%rip)
    jne bad
    cmpq $0xad7, entry_flags(%rip)
    jne bad
    movq $0, %rax
    cmpq %rax, seen+0(%rip)
    jne bad
    movabsq $0x1122334455660101, %rax
    cmpq %rax, seen+8(%rip)
    jne bad
    movabsq $0x1122334455660102, %rax
    cmpq %rax, seen+16(%rip)
    jne bad
    movq $10, %rax
    cmpq %rax, seen+24(%rip)
    jne bad
    leaq __restore_rt(%rip), %rax
    cmpq %rax, seen+32(%rip)
    jne bad
    leaq register_handler(%rip), %rax
    cmpq %rax, seen+40(%rip)
    jne bad
    movabsq $0x1122334455660106, %rax
    cmpq %rax, seen+48(%rip)
    jne bad
    movq $0, %rax
    cmpq %rax, seen+56(%rip)
    jne bad
    movq $0, %rax
    cmpq %rax, seen+64(%rip)
    jne bad
    movq $0, %rax
    cmpq %rax, seen+72(%rip)
    jne bad
    movabsq $0x112233445566010a, %rax
    cmpq %rax, seen+80(%rip)
    jne bad
    movabsq $0x112233445566010b, %rax
    cmpq %rax, seen+88(%rip)
    jne bad
    movabsq $0x112233445566010c, %rax
    cmpq %rax, seen+96(%rip)
    jne bad
    movabsq $0x112233445566010d, %rax
    cmpq %rax, seen+104(%rip)
    jne bad
    movabsq $0x112233445566010e, %rax
    cmpq %rax, seen+112(%rip)
    jne bad
    movq expected_rsp(%rip), %rax
    cmpq %rax, seen+120(%rip)
    jne bad
    movabsq $0x5a5a5a5a5a5a5a5a, %rax
    cmpq %rax, -8(%rsp)
    jne bad
    cmpq %rax, -16(%rsp)
    jne bad
    cmpq %rax, -24(%rsp)
    jne bad
    cmpq %rax, -32(%rsp)
    jne bad
    cmpq %rax, -40(%rsp)
    jne bad
    cmpq %rax, -48(%rsp)
    jne bad
    cmpq %rax, -56(%rsp)
    jne bad
    cmpq %rax, -64(%rsp)
    jne bad
    cmpq %rax, -72(%rsp)
    jne bad
    cmpq %rax, -80(%rsp)
    jne bad
    cmpq %rax, -88(%rsp)
    jne bad
    cmpq %rax, -96(%rsp)
    jne bad
    cmpq %rax, -104(%rsp)
    jne bad
    cmpq %rax, -112(%rsp)
    jne bad
    cmpq %rax, -120(%rsp)
    jne bad
    cmpq %rax, -128(%rsp)
    jne bad
    cmpq $-1, seen_fp+160(%rip)
    jne bad
    cmpq $-1, seen_fp+168(%rip)
    jne bad
    cmpq $-1, seen_fp+176(%rip)
    jne bad
    cmpq $-1, seen_fp+184(%rip)
    jne bad
    cmpq $-1, seen_fp+192(%rip)
    jne bad
    cmpq $-1, seen_fp+200(%rip)
    jne bad
    cmpq $-1, seen_fp+208(%rip)
    jne bad
    cmpq $-1, seen_fp+216(%rip)
    jne bad
    cmpq $-1, seen_fp+224(%rip)
    jne bad
    cmpq $-1, seen_fp+232(%rip)
    jne bad
    cmpq $-1, seen_fp+240(%rip)
    jne bad
    cmpq $-1, seen_fp+248(%rip)
    jne bad
    cmpq $-1, seen_fp+256(%rip)
    jne bad
    cmpq $-1, seen_fp+264(%rip)
    jne bad
    cmpq $-1, seen_fp+272(%rip)
    jne bad
    cmpq $-1, seen_fp+280(%rip)
    jne bad
    cmpq $-1, seen_fp+288(%rip)
    jne bad
    cmpq $-1, seen_fp+296(%rip)
    jne bad
    cmpq $-1, seen_fp+304(%rip)
    jne bad
    cmpq $-1, seen_fp+312(%rip)
    jne bad
    cmpq $-1, seen_fp+320(%rip)
    jne bad
    cmpq $-1, seen_fp+328(%rip)
    jne bad
    cmpq $-1, seen_fp+336(%rip)
    jne bad
    cmpq $-1, seen_fp+344(%rip)
    jne bad
    cmpq $-1, seen_fp+352(%rip)
    jne bad
    cmpq $-1, seen_fp+360(%rip)
    jne bad
    cmpq $-1, seen_fp+368(%rip)
    jne bad
    cmpq $-1, seen_fp+376(%rip)
    jne bad
    cmpq $-1, seen_fp+384(%rip)
    jne bad
    cmpq $-1, seen_fp+392(%rip)
    jne bad
    cmpq $-1, seen_fp+400(%rip)
    jne bad
    cmpq $-1, seen_fp+408(%rip)
    jne bad
    movabsq $0x8000000000000000, %rax
    cmpq %rax, seen_fp+32(%rip)
    jne bad
    cmpw $0x3fff, seen_fp+40(%rip)
    jne bad
    cmpl $0x1f80, seen_fp+24(%rip)
    jne bad
    xorl %eax, %eax
    jmp cleanup
bad:
    movl $1, %eax
cleanup:
    cld
    fxrstor64 saved_fp(%rip)
    popq %r15
    popq %r14
    popq %r13
    popq %r12
    popq %rbp
    popq %rbx
    ret
.size frame_register_checks,.-frame_register_checks
.type register_handler,@function
register_handler:
    pushfq
    popq entry_flags(%rip)
#ifdef STARTUP_FRAME_STATE_REG
    movq $0, 48(%rsp) /* saved R12 in the private payload */
#endif
#ifdef STARTUP_FRAME_STATE_REDZONE
    movq 184(%rsp), %rax /* interrupted RSP */
    movq $0, -8(%rax)
#endif
    fninit
    ldmxcsr other_mxcsr(%rip)
    pxor %xmm0, %xmm0
    pxor %xmm1, %xmm1
    pxor %xmm2, %xmm2
    pxor %xmm3, %xmm3
    pxor %xmm4, %xmm4
    pxor %xmm5, %xmm5
    pxor %xmm6, %xmm6
    pxor %xmm7, %xmm7
    pxor %xmm8, %xmm8
    pxor %xmm9, %xmm9
    pxor %xmm10, %xmm10
    pxor %xmm11, %xmm11
    pxor %xmm12, %xmm12
    pxor %xmm13, %xmm13
    pxor %xmm14, %xmm14
    pxor %xmm15, %xmm15
    movq $0xbad, %rax
    movq $0xbad, %rbx
    movq $0xbad, %rcx
    movq $0xbad, %rdx
    movq $0xbad, %rsi
    movq $0xbad, %rdi
    movq $0xbad, %rbp
    movq $0xbad, %r8
    movq $0xbad, %r9
    movq $0xbad, %r10
    movq $0xbad, %r11
    movq $0xbad, %r12
    movq $0xbad, %r13
    movq $0xbad, %r14
    movq $0xbad, %r15
    ret
.size register_handler,.-register_handler
.section .rodata
test_mxcsr: .long 0x1f80
other_mxcsr: .long 0x3f80
.section .bss
.p2align 4
saved_fp: .zero 512
seen_fp: .zero 512
seen: .zero 128
expected_rsp: .zero 8
seen_flags: .zero 8
entry_flags: .zero 8
.section .note.GNU-stack,"",@progbits
