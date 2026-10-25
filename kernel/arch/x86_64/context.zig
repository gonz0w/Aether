// Normalized x86 interrupt frame: shared by M2 and per-core user runtimes.
pub const Frame = extern struct {
    r15: u64 = 0,
    r14: u64 = 0,
    r13: u64 = 0,
    r12: u64 = 0,
    r11: u64 = 0,
    r10: u64 = 0,
    r9: u64 = 0,
    r8: u64 = 0,
    rsi: u64 = 0,
    rdi: u64 = 0,
    rbp: u64 = 0,
    rdx: u64 = 0,
    rcx: u64 = 0,
    rbx: u64 = 0,
    rax: u64 = 0,
    vector: u64 = 0,
    error_code: u64 = 0,
    rip: u64 = 0,
    cs: u64 = 0,
    flags: u64 = 0,
    rsp: u64 = 0,
    ss: u64 = 0,
};

comptime {
    // protection.S pushes these words in reverse order, then restores them in
    // this order. Equal-sized register reordering must fail before boot.
    const words = .{ "r15", "r14", "r13", "r12", "r11", "r10", "r9", "r8", "rsi", "rdi", "rbp", "rdx", "rcx", "rbx", "rax", "vector", "error_code", "rip", "cs", "flags", "rsp", "ss" };
    if (@sizeOf(Frame) != words.len * 8) @compileError("interrupt frame ABI mismatch");
    for (words, 0..) |name, index| {
        if (@offsetOf(Frame, name) != index * 8) @compileError("interrupt frame field offset mismatch: " ++ name);
    }
}
