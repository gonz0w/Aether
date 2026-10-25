const Frame = @import("context.zig").Frame;
const Table = [512]u64;
const nx = @as(u64, 1) << 63;
pub const transport_address = 0x01000000;
extern const kernel_start: u8;
extern const kernel_end: u8;
extern const text_start: u8;
extern const text_end: u8;
extern const rodata_start: u8;
extern const rodata_end: u8;
extern const transport_start: u8;
extern const transport_end: u8;
pub const apic_address = 0xfee00000;
pub const Inputs = struct {
    hhdm: u64,
    physical_base: u64,
    virtual_base: u64,
    image: []const u8,
    pub fn physical(self: Inputs, pointer: anytype) u64 {
        return @intFromPtr(pointer) - self.virtual_base + self.physical_base;
    }
};

// One owner CPU; no fields are read or written by its peer after bootstrap.
pub const State = struct {
    root: Table align(4096) = @splat(0),
    pdpt: Table align(4096) = @splat(0),
    pd: Table align(4096) = @splat(0),
    text_pt: Table align(4096) = @splat(0),
    stack_pt: Table align(4096) = @splat(0),
    device_pd: Table align(4096) = @splat(0),
    device_pt: Table align(4096) = @splat(0),
    kernel_pdpt: Table align(4096) = @splat(0),
    kernel_pd: Table align(4096) = @splat(0),
    kernel_pts: [8]Table align(4096) = @splat(@splat(0)),
    transport_pt: Table align(4096) = @splat(0),
    code: [4096]u8 align(4096) = @splat(0),
    stack: [4096]u8 align(4096) = @splat(0),
    frame: Frame = .{},
    root_physical: u64 = 0,
    ticks: u64 = 0,
    progress: u64 = 0,
    runnable: bool = false,
    post_fault_ticks: u64 = 0,
    post_fault_progress: u64 = 0,

    pub fn prepare(self: *State, inputs: Inputs, case: usize) void {
        const cr4 = asm volatile ("mov %%cr4, %[value]"
            : [value] "=r" (-> u64),
        );
        const cr0 = asm volatile ("mov %%cr0, %[value]"
            : [value] "=r" (-> u64),
        );
        if (cr4 & ((1 << 12) | (1 << 17) | (1 << 9) | (1 << 18)) != 0 or cr0 & (1 << 16) == 0)
            @panic("unsupported per-core paging or FP state");
        if (readMsr(0xc0000080) & (1 << 11) == 0) @panic("per-core NX unavailable");
        asm volatile ("mov %[value], %%cr0"
            :
            : [value] "r" (cr0 | 0xc),
            : .{ .memory = true });
        self.mapKernel(inputs);
        self.root[0] = inputs.physical(&self.pdpt) | 7;
        self.pdpt[0] = inputs.physical(&self.pd) | 7;
        self.pd[2] = inputs.physical(&self.text_pt) | 7;
        self.pd[8] = inputs.physical(&self.transport_pt) | 3;
        for (0..3) |i| self.transport_pt[i] = inputs.physical(&transport_start) + i * 4096 | 3 | nx;
        self.auditMappings(inputs);
        self.pd[4] = inputs.physical(&self.stack_pt) | 7;
        self.text_pt[0] = inputs.physical(&self.code) | 5;
        self.stack_pt[0] = inputs.physical(&self.stack) | 7 | nx;
        const apic = readMsr(0x1b);
        if (apic & (1 << 10) != 0 or apic & 0x000ffffffffff000 != apic_address)
            @panic("per-core timer requires pinned q35 xAPIC base");
        // PAT index 3 (PCD|PWT) is UC in the pinned Limine handoff contract.
        self.pdpt[3] = inputs.physical(&self.device_pd) | 3;
        self.device_pd[503] = inputs.physical(&self.device_pt) | 3;
        self.device_pt[0] = apic_address | 0x1b | nx;
        if (inputs.image.len == 0 or inputs.image.len > self.code.len) @panic("invalid per-core user image");
        @memcpy(self.code[0..inputs.image.len], inputs.image);
        self.frame = .{ .rdi = case, .rip = 0x400000, .rsp = 0x800ff8, .cs = 0x23, .ss = 0x1b, .flags = 0x202 };
        self.root_physical = inputs.physical(&self.root);
        asm volatile ("mov %[value], %%cr3"
            :
            : [value] "r" (self.root_physical),
            : .{ .memory = true });
        // CR3 does not flush global translations. Drop inherited boot globals.
        asm volatile ("mov %[value], %%cr4"
            :
            : [value] "r" (cr4 & ~@as(u64, 1 << 7)),
            : .{ .memory = true });
        asm volatile ("mov %[value], %%cr4"
            :
            : [value] "r" (cr4),
            : .{ .memory = true });
        writeMsr(0x1b, apic | (1 << 11));
        self.runnable = true;
    }
    fn mapKernel(self: *State, inputs: Inputs) void {
        const start = @intFromPtr(&kernel_start);
        const end = @intFromPtr(&kernel_end);
        if (start != 0xffffffff80000000 or inputs.virtual_base != start or end <= start or
            end - start > 16 * 1024 * 1024 or @intFromPtr(&transport_end) - @intFromPtr(&transport_start) != 3 * 4096)
            @panic("unsupported bounded kernel layout");
        self.root[511] = inputs.physical(&self.kernel_pdpt) | 3;
        self.kernel_pdpt[510] = inputs.physical(&self.kernel_pd) | 3;
        for (&self.kernel_pts, 0..) |*pt, i| self.kernel_pd[i] = inputs.physical(pt) | 3;
        var address = start;
        while (address < end) : (address += 4096) {
            if (address >= @intFromPtr(&transport_start) and address < @intFromPtr(&transport_end) and
                !@import("build_options").wide_transport_test) continue;
            const flags: u64 = if (address >= @intFromPtr(&text_start) and address < @intFromPtr(&text_end)) 1 else if (address >= @intFromPtr(&rodata_start) and address < @intFromPtr(&rodata_end)) 1 | nx else 3 | nx;
            const page = (address - start) / 4096;
            self.kernel_pts[page / 512][page % 512] = address - start + inputs.physical_base | flags;
        }
    }
    fn auditMappings(self: *const State, inputs: Inputs) void {
        if (self.root[@intCast((inputs.hhdm >> 39) & 511)] != 0 or self.pd[7] != 0 or self.pd[9] != 0)
            @panic("broad transport mapping retained");
        for (0..3) |i| {
            const expected = inputs.physical(&transport_start) + i * 4096 | 3 | nx;
            const old_page = (@intFromPtr(&transport_start) - @intFromPtr(&kernel_start)) / 4096 + i;
            if (self.transport_pt[i] != expected or self.kernel_pts[old_page / 512][old_page % 512] != 0)
                @panic("transport mapping permissions or alias invalid");
        }
        for (self.transport_pt[3..]) |entry| if (entry != 0) @panic("transport mapping exceeds quota");
    }
};
fn readMsr(index: u32) u64 {
    var low: u32 = undefined;
    var high: u32 = undefined;
    asm volatile ("rdmsr"
        : [low] "={eax}" (low),
          [high] "={edx}" (high),
        : [index] "{ecx}" (index),
    );
    return (@as(u64, high) << 32) | low;
}
fn writeMsr(index: u32, value: u64) void {
    asm volatile ("wrmsr"
        :
        : [low] "{eax}" (@as(u32, @truncate(value))),
          [high] "{edx}" (@as(u32, @truncate(value >> 32))),
          [index] "{ecx}" (index),
    );
}
pub fn apicRead(offset: usize) u32 {
    const register: *volatile u32 = @ptrFromInt(apic_address + offset);
    return register.*;
}
pub fn apicWrite(offset: usize, value: u32) void {
    const register: *volatile u32 = @ptrFromInt(apic_address + offset);
    register.* = value;
}
pub fn startTimer(masked: bool) void {
    apicWrite(0x80, 0); // TPR: accept all priorities.
    apicWrite(0xf0, 0x1ff); // Software enable, spurious vector 255.
    apicWrite(0x350, 1 << 16); // LINT0 masked; no legacy PIC route.
    apicWrite(0x360, 1 << 16);
    apicWrite(0x370, 1 << 16);
    apicWrite(0x3e0, 3); // Divide by 16.
    apicWrite(0x320, (1 << 17) | 32 | (if (masked) @as(u32, 1 << 16) else 0));
    apicWrite(0x380, 1_000_000);
}
pub fn stopTimer() void {
    apicWrite(0x320, 1 << 16);
    apicWrite(0x380, 0);
}
