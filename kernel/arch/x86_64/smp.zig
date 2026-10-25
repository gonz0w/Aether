const std = @import("std");
const limine = @import("../../limine.zig");
const serial = @import("serial.zig");
const user_cpu = @import("user_cpu.zig");
const stream = @import("display_stream.zig");
const display = @import("display.zig");
const Frame = @import("context.zig").Frame;
const cross_core = @import("../../cross_core.zig");
const Mailbox = @import("../../mailbox.zig").Mailbox;

export var mp_request: limine.MpRequest align(8) linksection(".limine_requests") = .{};
const Descriptor = packed struct(u80) { limit: u16, base: u64 };
const Gate = extern struct { low: u16, selector: u16 = 8, ist: u8 = 0, flags: u8 = 0x8e, middle: u16, high: u32, reserved: u32 = 0 };
const Core = struct {
    id: u32 = 0,
    boot: bool = false,
    processed: u64 = 0,
    caps: cross_core.Table = cross_core.Table.bootstrap(true),
    sent: [3]u64 = @splat(0),
    received: [3]u64 = @splat(0),
    invalid: u64 = 0,
    denied: u64 = 0,
    full: u64 = 0,
    ipc_complete: bool = false,
    transport_denied: bool = false,
    framebuffer_denied: bool = false,
    stack: [16384]u8 align(16) = undefined,
    double_fault_stack: [16384]u8 align(16) = undefined,
    tss: [104]u8 align(16) = @splat(0),
    gdt: [7]u64 = .{ 0, 0x00af9a000000ffff, 0x00cf92000000ffff, 0x00cff2000000ffff, 0x00affa000000ffff, 0, 0 },
    user: user_cpu.State = .{},
    idt: [256]Gate = undefined,
};
// Bootstrap initializes these, then each CPU owns only its designated record.
var cores: [2]Core = @splat(.{});
// Explicit shared transport; no scheduler/capability/task tables are shared.
const QueuePage = struct {
    queue: Mailbox = .{},
    padding: [4096 - @sizeOf(Mailbox)]u8 = @splat(0),
};
comptime {
    if (@sizeOf(QueuePage) != 4096 or @offsetOf(QueuePage, "queue") != 0) @compileError("queue page layout");
}
var queue_pages: [3]QueuePage align(4096) linksection(".transport") = @splat(.{});
const requests = &queue_pages[0].queue;
const replies = &queue_pages[1].queue;
var ready: bool = false;
var failed: bool = false;
var done: bool = false;
var boot_inputs: user_cpu.Inputs = undefined; // Immutable after AP release.
var user_go: bool = false;
var user_ready: [2]bool = .{ false, false };
var user_executed: [2]bool = .{ false, false };
var report_ready: bool = false;
var display_go: bool = false;
var ap_report: struct { ticks: u64, progress: u64 } = undefined;
var ap_info: *limine.MpInfo = undefined;
const budget = 10_000_000;
extern fn smp_run_on_stack(usize, *Core) callconv(.c) noreturn;
extern fn smp_load_tables(*const Descriptor, *const Descriptor) callconv(.c) void;
extern const smp_user_vectors: [256]usize;
extern fn restore_context(u64, *const Frame) callconv(.c) noreturn;
extern fn smp_fault_entry() callconv(.c) noreturn;

fn cpuId() u32 {
    var ebx: u32 = undefined;
    asm volatile ("cpuid"
        : [ebx] "={ebx}" (ebx),
        : [eax] "{eax}" (@as(u32, 1)),
        : .{ .eax = true, .ecx = true, .edx = true });
    return ebx >> 24;
}
fn setup(core: *Core) void {
    std.mem.writeInt(u64, core.tss[4..12], @intFromPtr(&core.stack) + core.stack.len, .little);
    std.mem.writeInt(u64, core.tss[36..44], @intFromPtr(&core.double_fault_stack) + core.double_fault_stack.len, .little);
    std.mem.writeInt(u16, core.tss[102..104], core.tss.len, .little);
    const base = @intFromPtr(&core.tss);
    core.gdt[5] = 103 | ((base & 0xffffff) << 16) | (@as(u64, 0x89) << 40) | (((base >> 24) & 0xff) << 56);
    core.gdt[6] = base >> 32;
    const address = @intFromPtr(&smp_fault_entry);
    for (&core.idt) |*gate| gate.* = .{ .low = @truncate(address), .middle = @truncate(address >> 16), .high = @truncate(address >> 32) };
    const gdtr = Descriptor{ .limit = @sizeOf(@TypeOf(core.gdt)) - 1, .base = @intFromPtr(&core.gdt) };
    const idtr = Descriptor{ .limit = @sizeOf(@TypeOf(core.idt)) - 1, .base = @intFromPtr(&core.idt) };
    smp_load_tables(&gdtr, &idtr);
    const rsp = asm volatile ("mov %%rsp, %[value]"
        : [value] "=r" (-> usize),
    );
    const bottom = @intFromPtr(&core.stack);
    if (cpuId() != core.id or rsp < bottom or rsp >= bottom + core.stack.len) smp_fault();
}
fn spin(remaining: *usize) void {
    if (@atomicLoad(bool, &failed, .acquire) or remaining.* == 0) @panic("SMP peer failed or stalled");
    remaining.* -= 1;
    std.atomic.spinLoopHint();
}
pub fn start(hhdm: u64, physical_base: u64, virtual_base: u64, image: []const u8) noreturn {
    boot_inputs = .{ .hhdm = hhdm, .physical_base = physical_base, .virtual_base = virtual_base, .image = image };
    const request: *volatile limine.MpRequest = &mp_request;
    const response = request.response orelse @panic("missing Limine MP response");
    if (response.revision != 0 or response.flags != 0 or response.count != 2) @panic("SMP probe requires two xAPIC CPUs");
    const cpus = response.cpus orelse @panic("missing CPU list");
    if (cpus[0].lapic_id == cpus[1].lapic_id or cpuId() != response.bsp_lapic_id) @panic("invalid SMP identities");
    if (cpus[0].lapic_id != response.bsp_lapic_id and cpus[1].lapic_id != response.bsp_lapic_id) @panic("boot CPU absent from topology");
    ap_info = if (cpus[0].lapic_id == response.bsp_lapic_id) cpus[1] else cpus[0];
    cores[0].id = response.bsp_lapic_id;
    cores[0].boot = true;
    cores[1].id = ap_info.lapic_id;
    smp_run_on_stack(@intFromPtr(&cores[0].stack) + cores[0].stack.len, &cores[0]);
}
fn apEntry(info: *limine.MpInfo) callconv(.c) noreturn {
    const core: *Core = @ptrFromInt(info.extra_argument);
    smp_run_on_stack(@intFromPtr(&core.stack) + core.stack.len, core);
}
export fn smp_fault() callconv(.c) noreturn {
    @atomicStore(bool, &failed, true, .release);
    serial.halt();
}
export fn smp_main(core: *Core) callconv(.c) noreturn {
    setup(core);
    if (!core.boot) {
        @atomicStore(bool, &ready, true, .release);
        while (core.processed < 100) {
            var remaining: usize = budget;
            const value = while (true) {
                if (requests.pop()) |value| break value;
                if (remaining == 0) smp_fault();
                remaining -= 1;
                std.atomic.spinLoopHint();
            };
            if (value != core.processed) smp_fault();
            remaining = budget;
            while (!replies.push(value * 3 + 1)) {
                if (remaining == 0) smp_fault();
                remaining -= 1;
                std.atomic.spinLoopHint();
            }
            core.processed += 1;
        }
        @atomicStore(bool, &done, true, .release);
        var remaining: usize = budget;
        while (!@atomicLoad(bool, &user_go, .acquire)) spin(&remaining);
        beginUser(core);
    }
    for (0..4) |i| if (!requests.push(i)) @panic("SMP initial queue fill failed");
    if (requests.push(999)) @panic("SMP full queue accepted overwrite");
    serial.write("SMP: releasing second CPU with private stack and state\n");
    ap_info.extra_argument = @intFromPtr(&cores[1]);
    if (!@import("build_options").skip_ap_test)
        @atomicStore(usize, &ap_info.goto_address, @intFromPtr(&apEntry), .release);
    var remaining: usize = budget;
    while (!@atomicLoad(bool, &ready, .acquire)) spin(&remaining);
    var sent: u64 = 4;
    remaining = budget;
    while (core.processed < 100) {
        var advanced = false;
        if (sent < 100 and requests.push(sent)) {
            sent += 1;
            advanced = true;
        }
        if (replies.pop()) |value| {
            if (value != core.processed * 3 + 1) @panic("SMP reply order or value mismatch");
            core.processed += 1;
            advanced = true;
        }
        if (advanced) remaining = budget else spin(&remaining);
    }
    remaining = budget;
    while (!@atomicLoad(bool, &done, .acquire)) spin(&remaining);
    if (sent != 100 or !requests.empty() or !replies.empty()) @panic("SMP transport not drained");
    serial.write("SMP: two CPUs exchanged 100 ordered messages; bounded queues drained\nAETHER SMP BRINGUP PASS\n");
    serial.out(0x21, 0xff);
    serial.out(0xa1, 0xff);
    @atomicStore(bool, &user_go, true, .release);
    beginUser(core);
}

fn beginUser(core: *Core) noreturn {
    core.caps = cross_core.Table.bootstrap(core.boot);
    core.user.prepare(boot_inputs, if (core.boot) 12 else 13);
    core.user.frame.rsi = core.caps.handle(0);
    for (&core.idt, smp_user_vectors, 0..) |*gate, handler, vector| {
        gate.* = .{ .low = @truncate(handler), .middle = @truncate(handler >> 16), .high = @truncate(handler >> 32), .ist = if (vector == 8) 1 else 0, .flags = if (vector == 128) 0xee else 0x8e };
    }
    if (user_cpu.apicRead(0x20) >> 24 != core.id) smp_fault();
    user_cpu.startTimer(!core.boot and @import("build_options").skip_ap_timer_test);
    const slot: usize = if (core.boot) 0 else 1;
    @atomicStore(bool, &user_ready[slot], true, .release);
    var remaining: usize = budget;
    while (!@atomicLoad(bool, &user_ready[1 - slot], .acquire)) spin(&remaining);
    if (core.boot) serial.write("SMP USER: private ring-3 workers and local APIC timers ready\n");
    restore_context(core.user.root_physical, &core.user.frame);
}
fn currentCore() *Core {
    const id = cpuId();
    // IDs are immutable routing metadata, not a shared mutable task table.
    if (id == cores[0].id) return &cores[0];
    if (id == cores[1].id) return &cores[1];
    smp_fault();
}
export fn smp_user_exception(frame: *const Frame) callconv(.c) *const Frame {
    const core = currentCore();
    if (!core.boot and stream.active) return stream.exception(frame);
    if (core.boot and display.active) return display.exception(frame);
    if (frame.cs != 0x23 or !core.user.runnable) smp_fault();
    core.user.frame = frame.*;
    if (frame.vector == 128) {
        invoke(core);
        return &core.user.frame;
    }
    if (frame.vector == 255) return &core.user.frame; // Spurious APIC interrupt: no EOI.
    if (frame.vector == 32) {
        user_cpu.apicWrite(0xb0, 0);
        core.user.ticks += 1;
        if (@atomicLoad(bool, &failed, .acquire) or core.user.ticks > 1000) @panic("SMP user peer failed or stalled");
        if (frame.r12 == 0x1234 and frame.r13 == 0x5678) {
            if (frame.rax < core.user.progress) smp_fault();
            core.user.progress = frame.rax;
            if (frame.rax > 0) @atomicStore(bool, &user_executed[if (core.boot) 0 else 1], true, .release);
        }
        if (core.boot and @atomicLoad(bool, &report_ready, .acquire)) {
            if (core.user.post_fault_ticks == 0) core.user.post_fault_progress = core.user.progress;
            core.user.post_fault_ticks += 1;
            if (core.user.post_fault_ticks == 4) {
                if (!core.ipc_complete or core.user.ticks < 3 or ap_report.ticks < 3 or ap_report.progress == 0 or core.user.progress <= core.user.post_fault_progress) smp_fault();
                user_cpu.stopTimer();
                core.user.runnable = false;
                var buffer: [200]u8 = undefined;
                serial.write(std.fmt.bufPrint(&buffer, "SMP USER: BSP ticks={d}, AP ticks={d}; BSP advanced after AP user fault\n", .{ core.user.ticks, ap_report.ticks }) catch "user timer log failure\n");
                serial.write("AETHER SMP USER PASS\nAETHER SMP IPC PASS\nAETHER M3 PASS\n");
                core.caps.live = false;
                if (!stream.drained()) @panic("M3 queues not quiescent before display handoff");
                @atomicStore(bool, &display_go, true, .release);
                display.start(boot_inputs);
            }
        }
        return &core.user.frame;
    }
    const cr2 = asm volatile ("mov %%cr2, %[value]"
        : [value] "=r" (-> u64),
    );
    if (!core.boot and core.ipc_complete and !core.framebuffer_denied and frame.vector == 14 and
        frame.error_code == 4 and cr2 == 0x02000000 and frame.rcx == 0x02000000)
    {
        core.framebuffer_denied = true;
        core.user.frame.rip += 3;
        return &core.user.frame;
    }
    if (!core.boot and core.ipc_complete and !core.transport_denied and frame.vector == 14 and
        frame.error_code == 5 and cr2 == user_cpu.transport_address and frame.rcx == user_cpu.transport_address)
    {
        core.transport_denied = true;
        core.user.frame.rip += 3; // Fixture's MOV RCX,[RCX]; not a general fault recovery ABI.
        return &core.user.frame;
    }
    if (!core.framebuffer_denied or !core.transport_denied or !core.ipc_complete or core.boot or frame.vector != 14 or frame.error_code != 5 or cr2 != user_cpu.apic_address or core.user.ticks < 3 or core.user.progress == 0 or !@atomicLoad(bool, &user_executed[0], .acquire)) smp_fault();
    user_cpu.stopTimer();
    core.user.runnable = false;
    core.caps.live = false;
    ap_report = .{ .ticks = core.user.ticks, .progress = core.user.progress };
    @atomicStore(bool, &report_ready, true, .release);
    var remaining: usize = budget;
    while (!@atomicLoad(bool, &display_go, .acquire)) spin(&remaining);
    var local_inputs = boot_inputs;
    // Boot HHDM is gone; copy from this owner's reserved immutable M3 code page.
    local_inputs.image = core.user.code[0..boot_inputs.image.len];
    stream.start(local_inputs);
}

fn transport(route: cross_core.Route) *Mailbox {
    return @ptrFromInt(user_cpu.transport_address + @as(usize, @intFromEnum(route)) * 4096);
}
fn invoke(core: *Core) void {
    const frame = &core.user.frame;
    const operation = frame.rax;
    frame.rax = 0;
    frame.rdx = 0;
    if (operation == 0) {
        const expected_sent: [3]u64 = if (core.boot) .{ 100, 0, 0 } else .{ 0, 104, 1 };
        const expected_received: [3]u64 = if (core.boot) .{ 0, 104, 1 } else .{ 100, 0, 0 };
        if (core.ipc_complete or frame.rsi != @as(u64, if (core.boot) 120 else 130) or
            !std.mem.eql(u64, &core.sent, &expected_sent) or
            !std.mem.eql(u64, &core.received, &expected_received) or
            core.invalid < 3 or core.denied < 1 or (!core.boot and core.full == 0))
        {
            @panic("SMP IPC worker checks failed");
        }
        core.ipc_complete = true;
        return;
    }
    if (core.ipc_complete or (operation != 1 and operation != 2)) {
        frame.rax = 1;
        return;
    }
    const route = core.caps.require(frame.rdi, if (operation == 1) .send else .receive) catch |err| {
        switch (err) {
            error.Invalid => {
                core.invalid += 1;
                frame.rax = 1;
            },
            error.Denied => {
                core.denied += 1;
                frame.rax = 2;
            },
        }
        return;
    };
    const queue = transport(route);
    const index = @intFromEnum(route);
    if (operation == 1) {
        if (queue.push(frame.rsi)) {
            core.sent[index] += 1;
        } else {
            core.full += 1;
            frame.rax = 4;
        }
    } else if (queue.pop()) |value| {
        core.received[index] += 1;
        frame.rdx = value;
    } else frame.rax = 5;
}
