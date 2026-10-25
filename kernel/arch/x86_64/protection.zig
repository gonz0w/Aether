const serial = @import("serial.zig");
const std = @import("std");

const Table = [512]u64;
const Space = struct {
    root: Table align(4096) = @splat(0),
    pdpt: Table align(4096) = @splat(0),
    pd: Table align(4096) = @splat(0),
    code_pt: Table align(4096) = @splat(0),
    stack_pt: Table align(4096) = @splat(0),
    alternate_stack_pt: Table align(4096) = @splat(0),
    code: [4096]u8 align(4096) = @splat(0),
    stack: [4096]u8 align(4096) = @splat(0),
};
// Boot-CPU-owned fixed storage. Only the factory worker bundle is reused.
var spaces: [12]Space = @splat(.{});
var active: usize = 0;
var physical_base: u64 = 0;
var hhdm_offset: u64 = 0;
var virtual_base: u64 = 0;
var kernel_stack: [if (@import("build_options").native_memory_large) 65536 else 16384]u8 align(16) = undefined;
var double_fault_stack: [16384]u8 align(16) = undefined;
var tss: [104]u8 align(16) = @splat(0);
var gdt: [7]u64 = .{ 0, 0x00af9a000000ffff, 0x00cf92000000ffff, 0x00cff2000000ffff, 0x00affa000000ffff, 0, 0 };
const Descriptor = packed struct(u80) { limit: u16, base: u64 };
const Gate = extern struct {
    low: u16,
    selector: u16,
    ist: u8,
    flags: u8,
    middle: u16,
    high: u32,
    reserved: u32 = 0,
};
var idt: [256]Gate = undefined;
extern const exception_vectors: [256]usize;
extern fn load_tables(*const Descriptor, *const Descriptor) callconv(.c) void;
extern fn restore_context(u64, *const Frame) callconv(.c) noreturn;

fn phys(pointer: anytype) u64 {
    return @intFromPtr(pointer) - virtual_base + physical_base;
}
fn stackTop() usize {
    return @intFromPtr(&kernel_stack) + kernel_stack.len;
}
pub fn tables() void {
    std.mem.writeInt(u64, tss[4..12], stackTop(), .little);
    std.mem.writeInt(u64, tss[36..44], @intFromPtr(&double_fault_stack) + double_fault_stack.len, .little);
    // An I/O bitmap beyond the TSS limit denies every port for CPL3/IOPL0.
    std.mem.writeInt(u16, tss[102..104], tss.len, .little);
    const base = @intFromPtr(&tss);
    gdt[5] = 103 | ((base & 0xffffff) << 16) | (@as(u64, 0x89) << 40) | (((base >> 24) & 0xff) << 56);
    gdt[6] = base >> 32;
    for (&idt, exception_vectors, 0..) |*gate, handler, vector| {
        gate.* = .{ .low = @truncate(handler), .selector = 8, .ist = if (vector == 8) 1 else 0, .flags = if (vector == 128 or (vector == 129 and @import("build_options").native_c_test)) 0xee else 0x8e, .middle = @truncate(handler >> 16), .high = @truncate(handler >> 32) };
    }
    const gdtr = Descriptor{ .limit = @sizeOf(@TypeOf(gdt)) - 1, .base = @intFromPtr(&gdt) };
    const idtr = Descriptor{ .limit = @sizeOf(@TypeOf(idt)) - 1, .base = @intFromPtr(&idt) };
    load_tables(&gdtr, &idtr);
}

pub fn start(hhdm: u64, pbase: u64, vbase: u64, image: []const u8, supervisor_envelope: []const u8) noreturn {
    const supervisor_image = @import("../../lifecycle_image.zig").parse(supervisor_envelope) catch @panic("unsupported lifecycle image ABI or layout");
    tables();
    const cr4 = asm volatile ("mov %%cr4, %[value]"
        : [value] "=r" (-> u64),
    );
    const cr0 = asm volatile ("mov %%cr0, %[value]"
        : [value] "=r" (-> u64),
    );
    const efer = asm volatile ("rdmsr"
        : [low] "={eax}" (-> u32),
        : [msr] "{ecx}" (@as(u32, 0xc0000080)),
        : .{ .edx = true });
    if (cr4 & ((1 << 12) | (1 << 17)) != 0 or cr0 & (1 << 16) == 0 or efer & (1 << 11) == 0)
        @panic("protection requires four-level paging, no PCID, WP and NX");
    // No FP/SIMD contexts yet: trap x87/MMX use rather than leak its state
    // between domains. Limine leaves CR4.OSFXSR/OSXSAVE clear.
    asm volatile ("mov %[value], %%cr0"
        :
        : [value] "r" (cr0 | 0xc),
        : .{ .memory = true });
    if (image.len == 0 or image.len > 4096) @panic("invalid Rust fixture size");
    physical_base = pbase;
    hhdm_offset = hhdm;
    virtual_base = vbase;
    const root = asm volatile ("mov %%cr3, %[value]"
        : [value] "=r" (-> u64),
    );
    const inherited: *const Table = @ptrFromInt(hhdm + (root & 0x000ffffffffff000));
    fixture_image = image;
    for (&spaces, 0..) |*space, i| {
        // No lower-half aliases inherited from the bootloader. Clearing U/S at
        // the root protects every inherited kernel/direct-map descendant.
        for (256..512) |index| space.root[index] = inherited[index] & ~@as(u64, 4);
        space.root[0] = phys(&space.pdpt) | 7;
        space.pdpt[0] = phys(&space.pd) | 7;
        space.pd[2] = phys(&space.code_pt) | 7;
        space.pd[4] = phys(&space.stack_pt) | 7;
        space.code_pt[0] = phys(&space.code) | 5;
        space.stack_pt[0] = phys(&space.stack) | 7 | (@as(u64, 1) << 63);
        if (i == 11) {
            space.root[0] = 0;
            space.code_pt[0] = 0;
            space.stack_pt[0] = 0;
        } else if (i == 10) {
            @memcpy(space.code[0..supervisor_image.len], supervisor_image);
        } else @memcpy(space.code[0..image.len], image);
    }
    serial.write("PROTECTION: entering isolated Rust fixtures\n");
    for (&contexts, 0..) |*context, i| context.* = .{ .rdi = i, .rip = 0x400000, .cs = 0x23, .ss = 0x1b, .rsp = 0x800ff8, .flags = if (i < 6) 2 else 0x202 };
    restore_context(phys(&spaces[0].root), &contexts[0]);
}

// Matches the push order in protection.S, including normalized vector/error.
const Frame = @import("context.zig").Frame;
var contexts: [12]Frame = undefined;
var ticks: [2]u64 = .{ 0, 0 };
var progress: [2]u64 = .{ 0, 0 };
var busy_faulted = false;
var survivor_ticks: u64 = 0;
var survivor_start: u64 = 0;
var run_queue = @import("run_queue.zig").RunQueue{};

pub fn timerStart() void {
    // Limine masks LAPIC LINT0. On this one-CPU q35 baseline, disable the
    // local APIC so the legacy PIC reaches INTR directly. SMP replaces this.
    var low: u32 = undefined;
    var high: u32 = undefined;
    asm volatile ("rdmsr"
        : [low] "={eax}" (low),
          [high] "={edx}" (high),
        : [msr] "{ecx}" (@as(u32, 0x1b)),
    );
    if (low & (1 << 10) != 0) @panic("legacy timer requires xAPIC mode");
    asm volatile ("wrmsr"
        :
        : [low] "{eax}" (low & ~@as(u32, 1 << 11)),
          [high] "{edx}" (high),
          [msr] "{ecx}" (@as(u32, 0x1b)),
    );
    // Remap both 8259s; only PIT IRQ0 is enabled. No other device IRQs.
    serial.out(0x20, 0x11);
    serial.out(0xa0, 0x11);
    serial.out(0x21, 0x20);
    serial.out(0xa1, 0x28);
    serial.out(0x21, 4);
    serial.out(0xa1, 2);
    serial.out(0x21, 1);
    serial.out(0xa1, 1);
    serial.out(0x21, if (@import("build_options").no_timer_test) 0xff else 0xfe);
    serial.out(0xa1, 0xff);
    const divisor: u16 = 11932;
    serial.out(0x43, 0x36);
    serial.out(0x40, @truncate(divisor));
    serial.out(0x40, @truncate(divisor >> 8));
}

fn selected() *const Frame {
    asm volatile ("mov %[root], %%cr3"
        :
        : [root] "r" (phys(&spaces[active].root)),
        : .{ .memory = true });
    return &contexts[active];
}

export fn protection_exception(frame: *const Frame) callconv(.c) *const Frame {
    if (@import("build_options").backing_alias) return @import("backing_alias.zig").exception(frame);
    if (@import("build_options").native_c_test) return @import("native_c.zig").exception(frame);
    if (frame.cs != 0x23) @panic("kernel exception");
    if (active >= 10) return lifetimeException(frame);
    if (active >= 8) return ipcException(frame);
    if (frame.vector == 32 and active >= 6) {
        serial.out(0x20, 0x20); // EOI before selecting the next task.
        const slot = active - 6;
        ticks[slot] += 1;
        // The loop publishes progress in RAX and keeps register sentinels.
        // An IRQ may arrive during entry, before the fixture initializes them.
        if (frame.r12 == 0x1234 and frame.r13 == 0x5678) {
            if (frame.rax < progress[slot]) @panic("user counter regressed");
            progress[slot] = frame.rax;
        }
        contexts[active] = frame.*;
        if (busy_faulted) {
            survivor_ticks += 1;
            if (survivor_ticks == 3) {
                if (progress[1] <= survivor_start) @panic("survivor made no progress after peer fault");
                serial.write("AETHER SCHEDULER PASS\n");
                run_queue.runnable[7] = false;
                run_queue.runnable[8] = true;
                contexts[8].rsi = endpoint.grant(8, 13) catch @panic("sender grant failed");
                contexts[9].rsi = endpoint.grant(9, 18) catch @panic("receiver grant failed");
                active = 8;
                return selected();
            }
        }
        active = run_queue.next(active) orelse @panic("no runnable task");
        return selected();
    }
    const cr2 = asm volatile ("mov %%cr2, %[value]"
        : [value] "=r" (-> u64),
    );
    var buffer: [256]u8 = undefined;
    serial.write(std.fmt.bufPrint(&buffer, "TRAP task={d} vector={d} error=0x{x} rip=0x{x} cs=0x{x} cr2=0x{x}\n", .{ active, frame.vector, frame.error_code, frame.rip, frame.cs, cr2 }) catch "trap formatting failed\n");
    if (active >= 6) {
        serial.write(std.fmt.bufPrint(&buffer, "SCHED ticks={d},{d} progress={d},{d} flags=0x{x}\n", .{ ticks[0], ticks[1], progress[0], progress[1], frame.flags }) catch "log failure\n");
        if (active != 6 or frame.vector != 14 or frame.error_code != 4 or cr2 != 0 or ticks[0] < 3 or ticks[1] < 3 or progress[0] == 0 or progress[1] == 0)
            @panic("unexpected scheduler fixture result");
        busy_faulted = true;
        run_queue.runnable[active] = false;
        survivor_start = progress[1];
        serial.write("SCHEDULER: busy task fault contained; peer continues\n");
        active = run_queue.next(active) orelse @panic("no survivor");
        return selected();
    }
    const expected = switch (active) {
        0 => frame.vector == 14 and frame.error_code == 5 and cr2 == 0xffffffff80000000,
        1 => frame.vector == 14 and frame.error_code == 7 and cr2 == 0x400000,
        2 => frame.vector == 14 and frame.error_code == 21 and cr2 == 0x800000,
        3 => frame.vector == 13 and frame.error_code == 0,
        4 => frame.vector == 14 and frame.error_code == 4 and cr2 == 0,
        5 => frame.vector == 128 and frame.rax == 42,
        else => false,
    };
    if (!expected) @panic("unexpected protection fixture result");
    active += 1;
    if (active == 6) {
        serial.write("AETHER PROTECTION PASS\nSCHEDULER: starting timer and busy Rust tasks\n");
        run_queue.runnable[6] = true;
        run_queue.runnable[7] = true;
        timerStart();
    }
    return selected();
}

const capabilities = @import("../../capability.zig");
var endpoint = capabilities.Owner{};
var statuses: u8 = 0;
var sends: usize = 0;
var receives: usize = 0;
var derived: usize = 0;
var revoked: usize = 0;
var closed: usize = 0;
fn invoke(frame: *const Frame) capabilities.Error!u64 {
    switch (frame.rax) {
        1 => {
            try endpoint.send(active, frame.rdi, frame.rsi);
            sends += 1;
        },
        2 => {
            const value = try endpoint.receive(active, frame.rdi);
            receives += 1;
            return value;
        },
        3 => {
            const handle = try endpoint.derive(active, frame.rdi, frame.rsi);
            derived += 1;
            return handle;
        },
        4 => {
            try endpoint.revoke(active, frame.rdi);
            revoked += 1;
        },
        5 => {
            try endpoint.close(active, frame.rdi);
            closed += 1;
        },
        6 => try endpoint.destroy(active, frame.rdi),
        else => return error.Invalid,
    }
    return 0;
}
fn ipcException(frame: *const Frame) *const Frame {
    contexts[active] = frame.*;
    if (frame.vector == 32) {
        serial.out(0x20, 0x20);
        active = run_queue.next(active) orelse @panic("no IPC task runnable");
        return selected();
    }
    if (frame.vector != 128) @panic("IPC user fault");
    if (frame.rax == 0) {
        if (active == 8 and frame.rsi == 80) {
            run_queue.runnable[8] = false;
            run_queue.runnable[9] = true;
            active = 9;
            return selected();
        }
        if (active != 9 or frame.rsi != 90 or endpoint.live or sends != 4 or receives != 4 or statuses != 0x7e or derived < 9 or revoked < 2 or closed == 0)
            @panic("IPC acceptance failed");
        serial.write("AETHER IPC PASS\n");
        run_queue.runnable[9] = false;
        run_queue.runnable[10] = true;
        contexts[10].rdi = 1;
        contexts[10].rdx = 1;
        contexts[10].rcx = 4096;
        contexts[10].rsi = endpoint.grantObject(10, 63, .factory) catch @panic("factory grant failed");
        active = 10;
        return selected();
    }
    contexts[active].rax = 0;
    contexts[active].rdx = invoke(frame) catch |err| {
        const status: u8 = switch (err) {
            error.Invalid => 1,
            error.Denied => 2,
            error.Exhausted => 3,
            error.Full => 4,
            error.Empty => 5,
            error.Busy => 6,
        };
        statuses |= @as(u8, 1) << @intCast(status);
        contexts[active].rax = status;
        contexts[active].rdx = 0;
        return selected();
    };
    return selected();
}

const lifetime = @import("../../lifetime.zig");
var pool = lifetime.Pool{};
var fixture_image: []const u8 = undefined;
var stack_address: u64 = 0;
var previous_stack: u64 = 0;
var releases: usize = 0;
var worker_faults: usize = 0;
var worker_exits: usize = 0;
var live_stops: usize = 0;
var acknowledgments: usize = 0;
var lifetime_ticks: usize = 0;

fn resetWorker() void {
    const space = &spaces[11];
    stack_address = if (pool.generation % 2 == 1) 0x800000 else 0xa00000;
    previous_stack = if (pool.generation == 1) 0 else if (stack_address == 0x800000) 0xa00000 else 0x800000;
    space.root[0] = phys(&space.pdpt) | 7;
    space.pdpt[0] = phys(&space.pd) | 7;
    space.pd[2] = phys(&space.code_pt) | 7;
    space.code_pt[0] = phys(&space.code) | 5;
    const leaf = if (stack_address == 0x800000) &space.stack_pt else &space.alternate_stack_pt;
    space.pd[@intCast(stack_address >> 21)] = phys(leaf) | 7;
    leaf[0] = phys(&space.stack) | 7 | (@as(u64, 1) << 63);
    @memcpy(space.code[0..fixture_image.len], fixture_image);
    contexts[11] = .{ .rdi = 11, .rsi = pool.generation, .rdx = stack_address, .rcx = previous_stack, .rip = 0x400000, .rsp = stack_address + 4096 - 8, .cs = 0x23, .ss = 0x1b, .flags = 0x202 };
}

fn destroyWorker() void {
    run_queue.runnable[11] = false;
    const space = &spaces[11];
    space.root[0] = 0;
    if (!@import("build_options").skip_unmap_test) {
        space.pdpt = @splat(0);
        space.pd = @splat(0);
        space.code_pt = @splat(0);
        space.stack_pt = @splat(0);
        space.alternate_stack_pt = @splat(0);
    }
    contexts[11] = .{};
    // Single CPU, PCID disabled, user leaves non-global. Completion of this
    // CR3 reload precedes capability invalidation, detachment, and reuse.
    _ = selected();
    endpoint.invalidate(.task);
    pool.completeStop();
    if (@import("build_options").drop_terminal_test) pool.terminal = null;
}
fn releaseMemory() void {
    endpoint.invalidate(.memory);
    if (!@import("build_options").skip_zero_test) {
        @memset(&spaces[11].code, 0);
        @memset(&spaces[11].stack, 0);
    }
    for (&spaces[11].code) |byte| if (byte != 0) {
        @panic("backing was not zeroed before reuse");
    };
    for (&spaces[11].stack) |byte| if (byte != 0) {
        @panic("backing was not zeroed before reuse");
    };
    pool.completeRelease();
    releases += 1;
    var buffer: [160]u8 = undefined;
    serial.write(std.fmt.bufPrint(&buffer, "LIFETIME generation={d} unmapped, references invalidated, backing zeroed\n", .{pool.generation}) catch "lifetime log failure\n");
}
fn lifetimeInvoke(frame: *const Frame) (capabilities.Error || lifetime.Error)!u64 {
    switch (frame.rax) {
        3 => return endpoint.derive(active, frame.rdi, frame.rsi),
        4 => try endpoint.revoke(active, frame.rdi),
        5 => try endpoint.close(active, frame.rdi),
        30 => {
            try endpoint.require(active, frame.rdi, .factory, 16);
            return 1;
        },
        31 => {
            try endpoint.require(active, frame.rdi, .task, 16);
            return pool.generation;
        },
        34, 35, 36 => {
            try endpoint.require(active, frame.rdi, .factory, 16);
            const record = pool.terminal orelse return 0;
            return switch (frame.rax) {
                34 => record.generation,
                35 => record.reason,
                else => record.detail,
            };
        },
        37 => {
            try endpoint.require(active, frame.rdi, .factory, 32);
            const record = pool.terminal;
            try pool.acknowledge(frame.rsi);
            acknowledgments += 1;
            var buffer: [160]u8 = undefined;
            serial.write(std.fmt.bufPrint(&buffer, "LIFECYCLE v1 instance={d} reason={d} detail={d} acknowledged after reclaim\n", .{ record.?.generation, record.?.reason, record.?.detail }) catch "lifecycle trace failure\n");
        },
        10 => {
            try endpoint.require(active, frame.rdi, .factory, 1);
            try pool.canAllocate();
            const handle = try endpoint.grantObject(active, 15, .memory);
            pool.allocate() catch unreachable;
            return handle;
        },
        11 => {
            try endpoint.require(active, frame.rdi, .factory, 2);
            try endpoint.require(active, frame.rsi, .memory, 1);
            try pool.canCreate();
            const handle = try endpoint.grantObject(active, 31, .task);
            pool.create() catch unreachable;
            resetWorker();
            return handle;
        },
        12 => {
            try endpoint.require(active, frame.rdi, .task, 1);
            try pool.start();
            run_queue.runnable[11] = true;
        },
        13 => {
            try endpoint.require(active, frame.rdi, .task, 16);
            return pool.result;
        },
        14 => {
            try endpoint.require(active, frame.rdi, .task, 2);
            const was_running = pool.task == .running;
            try pool.beginStop();
            if (was_running and pool.generation == 9 and spaces[11].stack[0] == 9) live_stops += 1;
            destroyWorker();
        },
        15 => {
            try endpoint.require(active, frame.rdi, .memory, 2);
            try pool.beginRelease();
            releaseMemory();
        },
        else => return error.Invalid,
    }
    return 0;
}
fn lifetimeException(frame: *const Frame) *const Frame {
    contexts[active] = frame.*;
    if (frame.vector == 32 or (frame.vector == 128 and frame.rax == 20)) {
        if (frame.vector == 32) {
            serial.out(0x20, 0x20);
            lifetime_ticks += 1;
            if (lifetime_ticks > 1000) @panic("lifecycle supervisor watchdog expired");
        }
        if (frame.vector == 128) {
            contexts[active].rax = 0;
            contexts[active].rdx = 0;
        }
        active = run_queue.next(active) orelse @panic("no lifetime task runnable");
        return selected();
    }
    if (active == 11 and (frame.vector == 14 or (frame.vector == 128 and frame.rax == 0))) {
        const cr2 = asm volatile ("mov %%cr2, %[value]"
            : [value] "=r" (-> u64),
        );
        if (spaces[11].stack[0] != pool.generation) @panic("worker failed to dirty backing");
        if (frame.vector == 14) {
            if (pool.generation < 2 or frame.error_code != 4 or cr2 != previous_stack)
                @panic("unexpected reused-worker fault");
            worker_faults += 1;
            pool.finish(2, 14);
        } else {
            if (pool.generation != 1 or frame.rsi != 110) @panic("reused worker check failed");
            worker_exits += 1;
            pool.finish(1, frame.rsi);
        }
        run_queue.runnable[11] = false;
        active = 10;
        return selected();
    }
    if (frame.vector != 128) @panic("lifecycle supervisor failed; recovery unsupported");
    if (frame.rax == 0) {
        var buffer: [160]u8 = undefined;
        serial.write(std.fmt.bufPrint(&buffer, "LIFETIME exit={d} releases={d} faults={d} exits={d} live_stops={d}\n", .{ frame.rsi, releases, worker_faults, worker_exits, live_stops }) catch "lifetime log failure\n");
        if (active != 10 or frame.rsi != 100 or releases != 9 or worker_faults != 7 or worker_exits != 1 or live_stops != 1 or pool.memory != .free or pool.task != .free or pool.terminal != null or acknowledgments != 9)
            @panic("lifetime acceptance failed");
        serial.write("AETHER LIFETIME PASS\nAETHER LIFECYCLE V1 PASS\n");
        if (@import("build_options").smp_test) @import("smp.zig").start(hhdm_offset, physical_base, virtual_base, fixture_image);
        serial.halt();
    }
    contexts[active].rax = 0;
    contexts[active].rdx = lifetimeInvoke(frame) catch |err| {
        contexts[active].rax = switch (err) {
            error.Invalid => 1,
            error.Denied => 2,
            error.Exhausted => 3,
            error.Full => 4,
            error.Empty => 5,
            error.Busy => 6,
        };
        contexts[active].rdx = 0;
        return selected();
    };
    return selected();
}
