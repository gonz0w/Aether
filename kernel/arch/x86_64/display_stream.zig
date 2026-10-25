const user_cpu = @import("user_cpu.zig");
const Frame = @import("context.zig").Frame;
const serial = @import("serial.zig");
const cross = @import("../../cross_core.zig");
const life = @import("../../remote_lifetime.zig");
const options = @import("build_options");
const Mailbox = @import("../../mailbox.zig").Mailbox;
pub const Stats = struct { sent: u64 = 0, received: u64 = 0, invalid: u64 = 0, denied: u64 = 0 };
pub const Result = struct { status: u64 = 0, value: u64 = 0 };
// Publisher runtime is AP-owned; only transport snapshots are published to BSP.
var runtime: user_cpu.State = .{};
var caps = cross.Table.display(false);
var stats = Stats{};
var framebuffer_denied = false;
var owner = life.Owner{};
var inputs_saved: user_cpu.Inputs = undefined;
var old_stack_denied = false;
var control_denied = false;
var fault_count: u64 = 0;
var stop_count: u64 = 0;
var reclaim_count: u64 = 0;
const Control = struct { request: u64, snapshot: u64, terminal: u64 };
comptime {
    if (@sizeOf(Mailbox) > 256 or 256 + @sizeOf(Control) > 4096) @compileError("control overlaps queue or page boundary");
}
fn control() *Control {
    return @ptrFromInt(user_cpu.transport_address + 8192 + 256);
}
pub fn snapshot() u64 {
    return @atomicLoad(u64, &control().snapshot, .acquire);
}
pub fn terminal() u64 {
    return @atomicLoad(u64, &control().terminal, .acquire);
}
pub fn request(operation: u64, generation: u32) bool {
    if (@atomicLoad(u64, &control().request, .acquire) != 0) return false;
    @atomicStore(u64, &control().request, (@as(u64, generation) << 32) | operation, .release);
    return true;
}
fn publish() void {
    @atomicStore(u64, &control().terminal, owner.terminal, .release);
    @atomicStore(u64, &control().snapshot, owner.snapshot(), .release);
}
fn command() ?u64 {
    const word = @atomicLoad(u64, &control().request, .acquire);
    if (word == 0) return null;
    const operation = word & 0xffffffff;
    owner.require(@intCast(word >> 32), operation) catch @panic("invalid remote owner command");
    return operation;
}
fn complete(operation: u64) void {
    owner.commit(operation);
    publish();
    @atomicStore(u64, &control().request, 0, .release);
}
pub var active = false; // Accessed only on AP dispatch path.
extern fn restore_context(u64, *const Frame) callconv(.c) noreturn;

pub fn finished() bool {
    return snapshot() == (@as(u64, life.generation_limit) << 32 | 4);
}
pub fn drained() bool {
    const request_queue: *const Mailbox = @ptrFromInt(user_cpu.transport_address);
    const reply: *const Mailbox = @ptrFromInt(user_cpu.transport_address + 4096);
    return request_queue.empty() and reply.empty();
}
// BSP only, after owner-confirmed AP stop and disabled BSP data access.
pub fn discard() u64 {
    var counts: u64 = 0;
    if (!options.skip_remote_discard) {
        const requests: *Mailbox = @ptrFromInt(user_cpu.transport_address);
        const replies: *Mailbox = @ptrFromInt(user_cpu.transport_address + 4096);
        while (requests.pop() != null) counts += @as(u64, 1) << 32;
        while (replies.pop() != null) counts += 1;
    }
    if (!drained()) @panic("remote transport not drained");
    return counts;
}
pub fn invoke(table: *const cross.Table, counts: *Stats, operation: u64, handle: u64, value: u64) Result {
    if (operation != 1 and operation != 2) return .{ .status = 1 };
    const route = table.require(handle, if (operation == 1) .send else .receive) catch |err| {
        if (err == error.Invalid) {
            counts.invalid += 1;
            return .{ .status = 1 };
        }
        counts.denied += 1;
        return .{ .status = 2 };
    };
    const queue: *Mailbox = @ptrFromInt(user_cpu.transport_address + @as(usize, @intFromEnum(route)) * 4096);
    if (operation == 1) {
        if (!queue.push(value)) return .{ .status = 4 };
        counts.sent += 1;
        return .{};
    }
    const received = queue.pop() orelse return .{ .status = 5 };
    counts.received += 1;
    return .{ .value = received };
}
pub fn start(inputs: user_cpu.Inputs) noreturn {
    inputs_saved = inputs;
    launch();
}
fn launch() noreturn {
    stats = .{};
    framebuffer_denied = false;
    old_stack_denied = false;
    control_denied = false;
    runtime.ticks = 0;
    runtime.prepare(inputs_saved, 14);
    const page: usize = owner.generation - 1;
    if (page != 0) {
        runtime.stack_pt[0] = 0;
        runtime.stack_pt[page] = inputs_saved.physical(&runtime.stack) | 7 | (@as(u64, 1) << 63);
        runtime.frame.rsp = 0x800ff8 + page * 4096;
    }
    caps = cross.Table.display(false);
    caps.namespace += (@as(u64, owner.generation - 1) * 2) << 32;
    runtime.frame.rdx = 1 + @as(u64, owner.generation - 1) * 20;
    runtime.frame.rcx = if (page == 0) 0 else 0x800000 + (page - 1) * 4096;
    runtime.frame.r8 = 0x800000 + page * 4096;
    publish();
    runtime.frame.rsi = caps.handle(0);
    active = true;
    user_cpu.startTimer(false);
    restore_context(runtime.root_physical, &runtime.frame);
}
pub fn exception(frame: *const Frame) *const Frame {
    if (frame.cs != 0x23 or !runtime.runnable) @panic("publisher kernel fault");
    runtime.frame = frame.*;
    if (frame.vector == 255) return &runtime.frame;
    if (frame.vector == 32) {
        user_cpu.apicWrite(0xb0, 0);
        runtime.ticks += 1;
        if (runtime.ticks > 1000) @panic("display publisher stalled");
        if (command()) |operation| {
            if (operation != 50) @panic("remote mutation while running");
            stop();
        }
        return &runtime.frame;
    }
    if (frame.vector == 6) fault();
    if (frame.vector == 14) {
        const address = asm volatile ("mov %%cr2, %[value]"
            : [value] "=r" (-> u64),
        );
        if (owner.generation > 1 and address == 0x800000 + @as(u64, owner.generation - 2) * 4096 and frame.rax == address and frame.error_code == 4 and !old_stack_denied) {
            old_stack_denied = true;
            runtime.frame.rip += 3;
            return &runtime.frame;
        }
        if (framebuffer_denied or frame.error_code != 4 or address != 0x02000000 or frame.rax != address)
            @panic("unexpected publisher user fault");
        framebuffer_denied = true;
        runtime.frame.rip += 3; // Known MOV RAX,[RAX] access-denial probe.
        return &runtime.frame;
    }
    if (frame.vector != 128) @panic("unexpected publisher interrupt");
    if (frame.rax == 50) {
        control_denied = true;
        runtime.frame.rax = 1;
        return &runtime.frame;
    }
    if (frame.rax == 0) {
        if (frame.rsi != 140) @panic("display publisher checks failed");
        checkWork();
        if (owner.phase != .running) @panic("duplicate publisher checkpoint");
        owner.phase = .checkpoint;
        publish();
        runtime.frame.rax = 0;
        return &runtime.frame;
    }
    if (frame.rax != 1 and frame.rax != 2) @panic("unsupported publisher operation");
    const result = invoke(&caps, &stats, frame.rax, frame.rdi, frame.rsi);
    runtime.frame.rax = result.status;
    runtime.frame.rdx = result.value;
    return &runtime.frame;
}

fn checkWork() void {
    if (stats.sent != (if (owner.generation < life.generation_limit) @as(u64, 21) else 20) or stats.received != 20 or stats.invalid != 2 or stats.denied != 1 or !framebuffer_denied or !control_denied or (owner.generation > 1 and !old_stack_denied))
        @panic("display publisher checks failed");
}
fn fault() noreturn {
    checkWork();
    user_cpu.stopTimer();
    runtime.runnable = false;
    caps.live = false;
    owner.terminate(2, 6) catch @panic("duplicate AP fault terminal");
    fault_count += 1;
    publish();
    serial.write("REMOTE: unsolicited AP user fault retained (#UD)\n");
    awaitControl();
}
fn stop() noreturn {
    user_cpu.stopTimer();
    runtime.runnable = false;
    caps.live = false;
    stop_count += 1;
    complete(50);
    awaitControl();
}
fn awaitControl() noreturn {
    var spins: u64 = 0;
    while (true) : (spins += 1) {
        if (spins > 2_000_000_000) @panic("remote controller stalled");
        asm volatile ("pause");
        if (command()) |operation| {
            if (operation == 52) {
                if (!drained()) @panic("AP reclaim before transport cleanup");
                if (!options.skip_remote_unmap) {
                    runtime.text_pt[0] = 0;
                    runtime.stack_pt[owner.generation - 1] = 0;
                }
                asm volatile ("mov %[root], %%cr3"
                    :
                    : [root] "r" (runtime.root_physical),
                    : .{ .memory = true });
                if (runtime.text_pt[0] != 0) @panic("remote stale mapping retained");
                for (&runtime.stack_pt) |entry| if (entry != 0) @panic("remote stale mapping retained");
                if (!options.skip_remote_zero) {
                    @memset(&runtime.code, 0);
                    @memset(&runtime.stack, 0);
                }
                for (&runtime.code) |byte| if (byte != 0) @panic("remote code not cleared");
                for (&runtime.stack) |byte| if (byte != 0) @panic("remote stack not cleared");
                runtime.frame = .{};
                reclaim_count += 1;
                if (owner.generation == life.generation_limit and (fault_count != 2 or stop_count != 3 or reclaim_count != 5)) @panic("remote recovery totals invalid");
                if (options.drop_remote_terminal and owner.terminal >> 32 == 2) owner.terminal = 0;
                complete(52);
                serial.write("REMOTE: AP confirmed stopped, unmapped and zeroed backing\n");
                if (owner.generation == life.generation_limit) {
                    serial.halt();
                }
            } else if (operation == 53) {
                if (owner.generation >= life.generation_limit) @panic("remote fixture generation quota");
                complete(53);
                launch();
            } else @panic("invalid stopped publisher command");
        }
    }
}
