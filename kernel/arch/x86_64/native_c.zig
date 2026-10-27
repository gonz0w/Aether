// Bounded opt-in native C experiment. No effect on existing fixture ABIs.
const std = @import("std");
// Diagnostic hooks execute under the existing local IF=0 syscall/IRQ boundary.
// Only object indexes/generations and counters survive a call; no user view does.
const Af09 = @import("../../native_af09_drain.zig");
const af09_mode = Af09.Mode.parse(if (@hasDecl(@import("build_options"), "native_af09_drain")) @import("build_options").native_af09_drain else "none");
const af09_enabled = af09_mode != .none;
var af09: if (af09_enabled) Af09.State else void = if (af09_enabled) .{} else {};
fn af09Row(phase: u8, slot: usize, status: i64, count: u64, aux: u64) void {
    if (!af09_enabled) return;
    af09RowAt(.{ .phase = phase, .slot = slot, .gen = states[slot].generation, .seq = sustained_events.sequence, .tick = total_ticks, .deadline = if (af09.observed) af09.deadline else 0, .status = status, .count = count, .aux = aux });
}
fn af09RowAt(row: Af09.Row) void {
    if (!af09_enabled) return;
    var line: [256]u8 = undefined;
    if (Af09.trace(&af09, &line, af09_mode, row)) |text| serial.write(text);
}
fn af09Fail(slot: usize, failure: i64) void {
    if (!af09_enabled or af09.invalid) return;
    af09.invalid = true;
    af09Row(29, slot, failure, 0, 0);
}
fn af09Object(value: u64, owner: usize) ?Af09.Object {
    if (!af09_enabled) return null;
    const c = ownedChannel(owner, value) orelse return null;
    return .{ .index = @intCast(c.identity), .generation = c.generation };
}
fn af09Matches(c: *const @import("../../native_channel.zig").Channel, object: usize) bool {
    if (!af09_enabled) return false;
    return c.identity == af09.objects[object].index and c.generation == af09.objects[object].generation;
}
fn af09Valid() bool {
    if (!af09_enabled or !af09.bound) return false;
    for ([_]usize{ 0, 1, 2, 6 }) |slot| {
        if (!states[slot].admitted or states[slot].generation != af09.generations[slot]) return false;
    }
    for (af09.objects, 0..) |object, i| {
        if (object.index >= channelCount()) return false;
        const c = &channels[object.index];
        if (c.identity != object.index or c.generation != object.generation) return false;
        // Until settlement, both real endpoints must retain their exact holders.
        const target: usize = if (i < 2) 2 else if (i < 4) 1 else 0;
        const target_end: usize = if (i >= 4) (if (i % 2 == 0) @as(usize, 0) else 1) else if (i % 2 == 0) 1 else 0;
        if (c.owners[target_end] != (if (states[target].terminal) @as(?usize, null) else target) or c.owners[1 - target_end] != 6) return false;
    }
    return true;
}
fn af09Bind(from: usize, child: usize) void {
    if (!af09_enabled) return;
    if (af09.bound or from != 1 or child != 2 or states[6].on_child) {
        af09Fail(child, -1);
        return;
    }
    af09.bound = true;
    for ([_]usize{ 0, 1, 2, 6 }) |slot| af09.generations[slot] = states[slot].generation;
    const slots = [_]usize{ 2, 1, 0 };
    for (slots, 0..) |slot, i| {
        // Process input is its reply reader, output is its request writer.
        af09.objects[2 * i] = af09Object(states[slot].channel_reply_cap, slot) orelse {
            af09Fail(slot, -1);
            return;
        };
        af09.objects[2 * i + 1] = af09Object(states[slot].channel_cap, slot) orelse {
            af09Fail(slot, -1);
            return;
        };
    }
    // Engine input/output directions are reversed relative to process clients.
    const temporary = af09.objects[4];
    af09.objects[4] = af09.objects[5];
    af09.objects[5] = temporary;
    if (!af09Valid()) {
        af09Fail(child, -1);
        return;
    }
    af09.copies += 1;
    af09Row(2, 2, 0, af09.copies, 0);
}
fn af09Blocked(slot: usize) bool {
    if (!af09_enabled) return false;
    return af09.blocked(slot, states[slot].generation);
}
fn af09Hold(slot: usize, hold: Af09.Hold) bool {
    if (!af09_enabled) return false;
    const s = &states[slot];
    if (s.on_child or s.execution.wait.address != 0 or s.channel_wait.endpoint != 0 or
        (slot == 6 and sustained_events.occupied))
    {
        af09Fail(slot, -3);
        return false;
    }
    if (slot == 2) af09.child_hold = hold else if (slot == 0) af09.engine_hold = hold else unreachable;
    af09Row(25, slot, 0, @intFromEnum(hold), 0);
    return true;
}
fn af09Release(slot: usize) void {
    if (!af09_enabled) return;
    const hold = if (slot == 2) af09.child_hold else af09.engine_hold;
    if (hold == .none) return;
    if (states[slot].generation != af09.generations[slot] or states[slot].terminal or !states[slot].admitted) {
        af09Fail(slot, -1);
        af09.cancel(slot, af09.generations[slot]);
        return;
    }
    if (slot == 2) af09.child_hold = .none else af09.engine_hold = .none;
    af09Row(25, slot, 0, @intFromEnum(hold), 1);
}
fn af09Ready(first: bool) void {
    if (!af09_enabled or active != 2 or !af09.bound or !first) return;
    if (!af09Valid() or af09.startup_written != 304 or af09.startup_read != 304 or af09.ready_written != 32) {
        af09Fail(2, -2);
        return;
    }
    af09.child_ready = true;
    if (af09Hold(2, .ready)) af09Row(4, 2, 0, 0, 0);
}
fn ordinaryQuery(caller: *State, target: *State) void {
    result(caller, if (target.terminal) @intCast(target.status + 1) else 0);
    caller.context().frame.rdx = @intFromBool(target.ready);
    caller.context().frame.rcx = target.yields;
    caller.context().frame.r8 = target.terminal_kind;
    if (@import("build_options").native_signal_suspend)
        caller.context().frame.r9 = @intFromBool(target.suspend_mask != null);
}
fn af09Query(slot: usize) bool {
    if (!af09_enabled or !af09.bound or slot != 1 or af09.query_positive or af09.invalid) return false;
    if (!af09Valid()) {
        af09Fail(1, -1);
        return false;
    }
    if (af09.startup_written != 304 or af09.startup_read != 304 or af09.ready_written != 32 or af09.ready_read != 32 or af09.parent_written != 32) {
        af09Fail(6, -2);
        return false;
    }
    const owner = &states[6];
    if (owner.on_child or owner.execution.wait.address != 0 or owner.channel_wait.endpoint != 0 or sustained_events.occupied or af09.query_pending) {
        af09Fail(6, -3);
        return false;
    }
    af09.query_pending = true;
    af09Row(5, 1, 0, 0, 0);
    return true;
}
fn af09Refresh() void {
    if (!af09_enabled or !af09.bound) return;
    // Cancel a retired/replaced generation without releasing any replacement.
    for ([_]usize{ 0, 2, 6 }) |slot| if (states[slot].generation != af09.generations[slot] or !states[slot].admitted or states[slot].terminal) {
        af09.cancel(slot, af09.generations[slot]);
    };
    if (af09.invalid) return;
    if (af09.query_pending) {
        if (!af09Valid()) {
            af09Fail(6, -1);
            return;
        }
        if (af09.child_ready and af09.child_hold == .ready) af09Release(2);
        if (states[1].terminal and states[1].terminal_kind == 1 and states[1].status == 0 and af09.child_ready and af09.late_written == 32 and af09.late_read == 0 and channels[af09.objects[0].index].stream.count == 32) {
            if (states[6].execution.wait.address != 0 or states[6].channel_wait.endpoint != 0 or sustained_events.occupied) {
                af09Fail(6, -3);
                return;
            }
            ordinaryQuery(&states[6], &states[1]);
            af09.query_pending = false;
            af09.query_positive = true;
            af09Row(8, 1, @bitCast(states[6].execution.frame.rax), 0, states[1].terminal_kind);
        }
    }
    if (af09.engine_hold == .ack and af09_mode == .partial_ack and af09.ack_written < 48 and total_ticks >= af09.release_tick) af09Release(0);
    if (af09.deferred_park and total_ticks >= af09.deadline) {
        if (total_ticks != af09.deadline or !af09DeferredValid()) {
            af09Fail(6, -4);
            return;
        }
        // The ordinary Events API preserves its own timeout-before-event rule.
        sustained_events.park(af09.saved_sequence, total_ticks, af09.deadline, !console_closed and serial.inputReady()) catch {
            af09Fail(6, -3);
            return;
        };
        af09.deferred_park = false;
        af09RowAt(.{ .phase = 26, .slot = 6, .gen = states[6].generation, .seq = af09.saved_sequence, .tick = total_ticks, .deadline = af09.deadline, .aux = 1 });
    }
}
fn af09Settled() bool {
    if (!af09_enabled or !af09.bound) return false;
    for ([_]usize{ 0, 6 }) |slot| {
        if (!states[slot].admitted or states[slot].terminal or states[slot].generation != af09.generations[slot]) return false;
    }
    for ([_]usize{ 1, 2 }) |slot| {
        const source = &states[slot];
        if (source.generation != af09.generations[slot] or source.admitted or !source.terminal or source.count != 0) return false;
    }
    if (states[1].terminal_kind != 1 or states[1].status != 0 or states[2].terminal_kind != 3 or states[2].status != 143 or af09.late_written != 32 or af09.late_read != 0) return false;
    for (af09.objects[0..4]) |object| {
        const c = &channels[object.index];
        if (c.generation != object.generation or c.owners[0] != null or c.owners[1] != null or c.stream.count != 0) return false;
    }
    for (af09.objects[4..6], 0..) |object, i| {
        const c = &channels[object.index];
        if (c.generation != object.generation or c.owners[i] != 0 or c.owners[1 - i] != 6) return false;
    }
    return true;
}
fn af09DeferredValid() bool {
    if (!af09_enabled) return false;
    const c = &channels[af09.objects[5].index];
    return af09Settled() and states[6].generation == af09.generations[6] and states[0].generation == af09.generations[0] and states[6].admitted and states[0].admitted and !states[6].terminal and !states[0].terminal and c.generation == af09.objects[5].generation and c.owners[0] == 6 and c.owners[1] == 0 and !sustained_events.occupied and sustained_events.sequence != std.math.maxInt(u64) and af09.saved_sequence < sustained_events.sequence and af09.ack_written == 16 and af09.ack_read == 0 and c.stream.count == 16 and af09.engine_hold == .ack and states[6].execution.wait.address == 0 and states[6].channel_wait.endpoint == 0;
}
fn af09Output(f: *const Frame, offset: usize, count: usize) void {
    if (!af09_enabled or active != 0) return;
    const s = &states[0];
    if (!af09Settled() or s.generation != af09.generations[0] or s.on_child or af09.counter_seen or offset != 0 or count != 8 or f.rdx != 8 or f.r10 | f.r8 | f.r9 != 0 or !af09.observed or total_ticks >= af09.deadline or s.output_count != 8) {
        af09Fail(0, -5);
        return;
    }
    const bytes = s.output[0..8];
    if (bytes[0] != 1 or bytes[1] != 1 or bytes[6] | bytes[7] != 0 or std.mem.readInt(u16, bytes[2..4], .little) != 2 or std.mem.readInt(u16, bytes[4..6], .little) != 3 or af09.engine_requests != 256 or af09.engine_replies != 256) {
        af09Fail(0, -5);
        return;
    }
    af09.counter_seen = true;
    af09Row(16, 0, 8, std.mem.readInt(u16, bytes[2..4], .little), std.mem.readInt(u16, bytes[4..6], .little));
    if (af09_mode == .no_ack or af09_mode == .pending_fragment) _ = af09Hold(0, .counter);
}
fn af09Prefix() bool {
    if (!af09_enabled) return false;
    const stream = &channels[af09.objects[0].index].stream;
    if (stream.count != 32) return false;
    var bytes: [32]u8 = undefined;
    for (&bytes, 0..) |*b, i| b.* = stream.bytes[(stream.head + i) % 32];
    if (af09_mode == .stream) return std.mem.readInt(u32, bytes[0..4], .little) == 2 and std.mem.readInt(u32, bytes[4..8], .little) != 0 and (std.mem.readInt(u32, bytes[8..12], .little) == 4 or std.mem.readInt(u32, bytes[8..12], .little) == 6) and std.mem.readInt(u32, bytes[12..16], .little) == 16 and std.mem.eql(u8, bytes[16..32], "AF09-HOME-WRITE\n");
    if (af09_mode == .exec_prefix or af09_mode == .fork_prefix) return std.mem.eql(u8, bytes[0..8], if (af09_mode == .exec_prefix) "AEEXEC02" else "AEFORK02") and std.mem.readInt(u32, bytes[8..12], .little) == 1 and std.mem.readInt(u32, bytes[12..16], .little) == (if (af09_mode == .exec_prefix) @as(u32, 608) else 304) and std.mem.eql(u8, bytes[16..24], "AEFSH001") and std.mem.readInt(u32, bytes[24..28], .little) == 29 and std.mem.readInt(u32, bytes[28..32], .little) == 7;
    return std.mem.eql(u8, bytes[0..8], "AEFW0001") and std.mem.readInt(u64, bytes[8..16], .little) == 11 and std.mem.readInt(u64, bytes[16..24], .little) != 0 and std.mem.readInt(u64, bytes[24..32], .little) != 0;
}
fn af09Transfer(c: *const @import("../../native_channel.zig").Channel, reading: bool, amount: usize, status: i64) void {
    if (!af09_enabled or !af09.engine_bound) return;
    if (active != 0 and active != 6 and !af09.bound) return;
    if (states[active].generation != af09.generations[active]) {
        af09Fail(active, -1);
        return;
    }
    var direction: u64 = 0;
    if (af09Matches(c, 0)) direction = if (reading) 2 else 1;
    if (af09Matches(c, 4)) direction = if (reading) 4 else 3;
    if (af09Matches(c, 5)) direction = if (reading) 6 else 5;
    if (status == -11 and direction != 0) {
        af09Row(24, active, status, 0, direction);
        if (active == 6 and direction == 6 and af09.counter_seen and af09.ack_read == 0) af09.ack_eagain = true;
    }
    if (amount == 0) return;
    if (af09.bound and af09Matches(c, 1)) {
        if (!reading and active == 6) af09.startup_written += amount;
        if (reading and active == 2) {
            af09.startup_read += amount;
            if (af09.startup_read == 304) af09Row(3, 2, 0, 304, 0);
        }
        if (af09.startup_written > 304 or af09.startup_read > 304) af09Fail(2, -2);
    }
    if (af09.bound and af09Matches(c, 3) and !reading and active == 6 and af09.parent_written < 32) {
        af09.parent_written += amount;
        if (af09.parent_written == 32) af09Row(28, 1, 0, 32, 0);
    }
    if (af09.bound and af09Matches(c, 0)) {
        // Wire READY and native READY may arrive in either order at the owner.
        // The child's completed native return stays held while the owner
        // consumes the real wire READY and publishes parent disposition.
        if (reading and active == 6 and af09.ready_read < 32) {
            af09.ready_read += amount;
            if (af09.ready_read == 32) af09Row(27, 2, 0, 32, 0);
            if (af09.ready_read > 32) af09Fail(2, -2);
        } else if (!reading and active == 2 and af09.ready_written < 32) {
            af09.ready_written += amount;
            if (af09.ready_written > 32) af09Fail(2, -2);
        } else if (!reading and active == 2 and af09.child_ready) {
            af09.late_written += amount;
            af09Row(6, 2, 0, af09.late_written, 0);
            if (!af09.query_pending or af09.late_written > 32 or (af09.late_written == 32 and !af09Prefix())) af09Fail(2, -2);
        } else if (reading and active == 6) {
            af09.late_read += amount;
            af09Row(12, 2, 0, af09.late_read, 0);
            af09Fail(2, -2);
        } else af09Fail(2, -2);
    }
    if (af09Matches(c, 4) and !reading and active == 6) {
        af09.engine_requests += amount;
        if (af09.counter_seen) af09Fail(0, -6);
    }
    if (af09Matches(c, 5)) {
        if (!af09.counter_seen) {
            if (!reading and active == 0) af09.engine_replies += amount;
        } else if (!reading and active == 0) {
            af09.ack_written += amount;
            af09Row(17, 0, 0, af09.ack_written, 0);
            if (states[0].on_child or total_ticks >= af09.deadline or af09.ack_written > 64) {
                af09Fail(0, -4);
                return;
            }
            if (af09_mode == .partial_ack or af09_mode == .pending_fragment) {
                if (amount != 16) {
                    af09Fail(0, -2);
                    return;
                }
                if (af09_mode == .pending_fragment) {
                    if (!af09.deferred_park or af09.ack_written != 16 or af09.saved_sequence >= sustained_events.sequence or c.stream.count != 16) {
                        af09Fail(0, -2);
                        return;
                    }
                    af09.release_tick = af09.deadline;
                } else {
                    af09.release_tick = if (af09.ack_written == 16) af09.t0 + 100 else if (af09.ack_written == 32) af09.t0 + 200 else af09.deadline;
                    if (af09.ack_written > 48 or total_ticks >= af09.release_tick) {
                        af09Fail(0, -4);
                        return;
                    }
                }
                _ = af09Hold(0, .ack);
            }
        } else if (reading and active == 6) {
            af09.ack_read += amount;
            af09Row(18, 6, 0, af09.ack_read, 0);
        }
    }
}
fn af09BeforePark(f: *const Frame) bool {
    if (!af09_enabled or !af09.observed) return false;
    af09RowAt(.{ .phase = 10, .slot = 6, .gen = states[6].generation, .seq = f.rsi, .tick = total_ticks, .deadline = f.rdx });
    if (f.rdx != af09.deadline) {
        af09Fail(6, -4);
        return false;
    }
    if (af09_mode != .pending_fragment or !af09.counter_seen or af09.ack_written != 0 or af09.deferred_park) return false;
    if (!af09.ack_eagain or !af09Settled() or total_ticks >= af09.deadline or sustained_events.occupied or f.rsi > sustained_events.sequence or sustained_events.sequence == std.math.maxInt(u64) or states[6].on_child or states[6].execution.wait.address != 0 or states[6].channel_wait.endpoint != 0 or af09.engine_hold != .counter) {
        af09Fail(6, -3);
        return false;
    }
    af09.saved_sequence = f.rsi;
    af09.deferred_park = true;
    af09RowAt(.{ .phase = 26, .slot = 6, .gen = states[6].generation, .seq = f.rsi, .tick = total_ticks, .deadline = f.rdx });
    af09Release(0);
    return true;
}
fn af09BeforeExit(status: u64, kind: u64) bool {
    if (!af09_enabled or active != 0 or kind != 1) return false;
    af09Row(20, 0, @bitCast(status), 0, 0);
    if (af09_mode != .exit_deadline) return false;
    if (!af09.counter_seen or af09.ack_written != 64 or status != 0 or total_ticks >= af09.deadline or states[0].generation != af09.generations[0]) {
        af09Fail(0, -4);
        return false;
    }
    return af09Hold(0, .exit);
}

fn af09EngineAdmitted() void {
    if (!af09_enabled) return;
    if (af09.engine_bound) {
        af09Fail(0, -1);
        return;
    }
    af09.engine_bound = true;
    af09.generations[0] = states[0].generation;
    af09.generations[6] = states[6].generation;
    af09.objects[4] = af09Object(states[0].channel_cap, 0) orelse {
        af09Fail(0, -1);
        return;
    };
    af09.objects[5] = af09Object(states[0].channel_reply_cap, 0) orelse {
        af09Fail(0, -1);
        return;
    };
    af09Row(1, 6, 0, 0, 0);
}
fn af09Closed(c: *const @import("../../native_channel.zig").Channel, before: usize, status: i64) void {
    if (!af09_enabled or !af09.bound) return;
    if (active == 6 and (af09Matches(c, 4) or af09Matches(c, 5))) {
        af09Row(19, 6, status, 0, @intFromBool(af09Matches(c, 5)));
        af09.source_closes |= if (af09Matches(c, 5)) @as(u8, 2) else 1;
        if (af09.source_closes == 3) af09Row(22, 0, 0, @intFromBool(states[0].admitted), @intFromBool(states[0].count != 0));
    }
    if (af09Matches(c, 0) and before > c.stream.count) af09Row(13, 2, status, before - c.stream.count, af09.late_read);
}

fn af09CloseFailed(value: u64, status: i64) void {
    if (!af09_enabled or !af09.bound) return;
    for ([_]usize{ 4, 5 }) |object| {
        const identity = af09.objects[object];
        const c = &channels[identity.index];
        if (c.generation == identity.generation and value == c.cap(if (object == 4) 1 else 0)) {
            af09Closed(c, c.stream.count, status);
            return;
        }
    }
    af09Fail(6, -1);
}
const elf = @import("../../native_elf.zig");
const serial = @import("serial.zig");
const Frame = @import("context.zig").Frame;
const Table = [512]u64;
const nx = @as(u64, 1) << 63;
extern const kernel_start: u8;
extern const kernel_end: u8;
extern const text_start: u8;
extern const text_end: u8;
extern const rodata_start: u8;
extern const rodata_end: u8;
extern fn restore_context(u64, *const Frame) callconv(.c) noreturn;
const memory = @import("../../native_memory.zig");
const Page = memory.Page;
const service_memory = @import("build_options").native_service_memory;
const FsSession = @import("../../native_fs_session.zig");
const FsRoles = @import("native_fs_roles.zig");
const combined_profile = @hasDecl(@import("build_options"), "native_fs_session") and @import("build_options").native_fs_session;
const combined_init = @hasDecl(@import("build_options"), "native_fs_session_init") and @import("build_options").native_fs_session_init;
const combined_owner_data = @hasDecl(@import("build_options"), "native_fs_owner_data") and @import("build_options").native_fs_owner_data;
const combined_owner_stack = @hasDecl(@import("build_options"), "native_fs_owner_stack") and @import("build_options").native_fs_owner_stack;
const combined_application_profile = @hasDecl(@import("build_options"), "native_fs_application_profile") and @import("build_options").native_fs_application_profile;
comptime {
    if (af09_enabled and (!combined_profile or !combined_init or !combined_owner_stack or combined_application_profile or @import("build_options").native_service_lifetime))
        @compileError("native-af09-drain requires the separate guarded filesystem owner profile");
}
fn threadedSlot(slot: usize) bool {
    return @import("build_options").native_threads and (!combined_profile or FsRoles.threaded(slot));
}
fn processSlot(slot: usize) bool {
    return !combined_profile or FsRoles.process(slot);
}

const arena = memory.Arena(if (service_memory) 8192 else if (@import("build_options").native_memory_large) 2048 else 128);
const launch = @import("../../native_launch.zig");
const Execution = @import("native_execution.zig").Execution;
const Child = @import("native_execution.zig").Child;
const service_workers = @import("build_options").native_service_workers;
const legacy_child_count = if (@import("build_options").native_thread_pair) 2 else 1;
const ContextList = if (service_workers) struct {
    items: [83]*Execution = undefined,
    count: usize = 0,
} else [1 + legacy_child_count]*Execution;
fn contextView(list: *const ContextList) []const *Execution {
    return if (service_workers) list.items[0..list.count] else list;
}
const external_backing = @import("build_options").native_backing;
const Payload = [arena.page_count][4096]u8;
const State = struct {
    root: Table align(4096) = @splat(0),
    pdpt: Table align(4096) = @splat(0),
    pd: Table align(4096) = @splat(0),
    pts: [memory.table_capacity]Table align(4096) = @splat(@splat(0)),
    pt_index: [memory.table_capacity]usize = @splat(0),
    pt_count: usize = 0,
    kpdp: Table align(4096) = @splat(0),
    kpd: Table align(4096) = @splat(0),
    kpt: [if (@import("build_options").native_memory_large) 32 else 8]Table align(4096) = @splat(@splat(0)),
    backing: (if (service_memory) []align(4096) [4096]u8 else if (external_backing) *align(4096) Payload else Payload) align(4096) = if (external_backing) undefined else @splat(@splat(0)),
    pages: (if (service_memory) []Page else [arena.page_count]Page) = if (service_memory) undefined else @splat(.{}),
    count: usize = 0,
    memory_cap: u64 = 0,
    entropy_grant: @import("../../native_entropy.zig").Grant = .{},
    channel_cap: u64 = 0,
    channel_reply_cap: u64 = 0,
    channel_wait: @import("../../native_channel.zig").Wait = .{},
    memory_protect_denied: bool = false,
    signal_actions: if (@import("build_options").native_signal_actions) @import("native_pending.zig").State else void = if (@import("build_options").native_signal_actions) .{} else {},
    execution: Execution = .{},
    children: if (service_workers) []Child else [legacy_child_count]Child = if (service_workers) undefined else @splat(.{}),
    selected_child: usize = 0,
    on_child: bool = false,
    child_admissions: u32 = 0,
    thread_cap: u64 = 0,
    input: @import("../../byte_stream.zig").Stream = .{},
    errors: [256]u8 = @splat(0),
    errors_count: usize = 0,
    stream_closed: [3]bool = @splat(false),
    output: [256]u8 = @splat(0),
    output_count: usize = 0,
    yields: usize = 0,
    ticks: usize = 0,
    parent_pid: u64 = 0,
    image_commit: if (@import("build_options").native_process_exec) struct {
        sequence: u64 = 0,
        image: u64 = 0,
        pending: bool = false,
    } else void = if (@import("build_options").native_process_exec) .{} else {},
    suspend_mask: if (@import("build_options").native_signal_suspend) ?u64 else void = if (@import("build_options").native_signal_suspend) null else {},
    freeze_sequence: u64 = 0,
    frozen: bool = false,
    terminal: bool = false,
    admitted: bool = false,
    ready: bool = false,
    revision: u64 = 0,
    generation: u64 = 0,
    status: u64 = 0,
    terminal_kind: u64 = 0,
    fn payload(s: *State) (if (service_memory) []align(4096) [4096]u8 else *align(4096) Payload) {
        return if (external_backing) s.backing else &s.backing;
    }
    fn records(s: *State) (if (service_memory) []Page else *[arena.page_count]Page) {
        return if (service_memory) s.pages else &s.pages;
    }
    fn recordBytes(s: *State) []u8 {
        return if (service_memory) std.mem.sliceAsBytes(s.records()) else std.mem.asBytes(s.records());
    }
    fn payloadBytes(s: *State) []u8 {
        return if (service_memory) std.mem.sliceAsBytes(s.payload()) else std.mem.asBytes(s.payload());
    }
    fn child(s: *State) *@import("native_execution.zig").Child {
        return &s.children[s.selected_child];
    }
    fn childRecords(s: *State) []Child {
        return if (service_workers) s.children else &s.children;
    }
    fn contexts(s: *State) ContextList {
        if (service_workers) {
            var list = ContextList{ .count = 1 + s.children.len };
            std.debug.assert(list.count <= list.items.len);
            list.items[0] = &s.execution;
            for (s.childRecords(), 0..) |*c, i| list.items[i + 1] = &c.execution;
            return list;
        } else {
            var result_contexts: ContextList = undefined;
            result_contexts[0] = &s.execution;
            for (s.childRecords(), 0..) |*c, i| result_contexts[i + 1] = &c.execution;
            return result_contexts;
        }
    }
    fn context(s: *State) *Execution {
        return if (s.on_child) &s.child().execution else &s.execution;
    }
};
const pipeline_capacity = @import("build_options").native_pipeline_capacity;
var states: [if (combined_profile) FsRoles.domain_count else if (pipeline_capacity) 6 else 4]State = @splat(.{});
var backing_pool: if (external_backing) @import("backing_pool.zig").Pool else void = if (external_backing) .{} else {};
var backing_partitions: [if (external_backing) states.len else 0]@import("backing_pool.zig").Partition = undefined;
var service_records: if (service_memory) [8192]Page else void = if (service_memory) @splat(.{}) else {};
var small_records: if (service_memory) [if (combined_application_profile) 1 else if (combined_profile) 6 else 3][128]Page else void = if (service_memory) @splat(@splat(.{})) else {};
var application_records: if (combined_application_profile) [FsRoles.process_count][FsRoles.application_pages]Page else void = if (combined_application_profile) @splat(@splat(.{})) else {};
var service_children: if (service_workers) [82]Child else void = if (service_workers) @splat(.{}) else {};
var small_children: if (service_workers) [if (combined_profile) 6 else 3][if (combined_profile) 0 else 2]Child else void = if (service_workers) @splat(@splat(.{})) else {};
fn bindChildren(state: *State) void {
    if (!service_workers) return;
    const owner = backingOwner(state);
    state.children = if (owner == 0) &service_children else &small_children[owner - 1];
    require(state.children.len == (if (owner == 0) @as(usize, 82) else if (combined_profile) 0 else 2));
}
fn arenaEnd(s: *const State) usize {
    return memory.base + s.pages.len * 4096;
}
fn bindRecords(state: *State) void {
    if (!service_memory) return;
    const owner = backingOwner(state);
    state.pages = if (owner == 0) &service_records else if (combined_application_profile and FsRoles.process(owner)) &application_records[owner - 1] else &small_records[if (combined_application_profile) 0 else owner - 1];
    require(state.pages.len == backing_partitions[owner].count);
}
fn bindPayload(state: *State, address: usize) void {
    if (!external_backing) return;
    if (service_memory) {
        const pointer: [*]align(4096) [4096]u8 = @ptrFromInt(address);
        state.backing = pointer[0..backing_partitions[backingOwner(state)].count];
    } else state.backing = @ptrFromInt(address);
}
var backing_boot_alias: usize = 0;
var backing_boot_views = false;

fn prepareBacking(hhdm: u64, map: *const @import("../../limine.zig").MemoryResponse) void {
    const planner = @import("../../boot_backing.zig");
    const geometry = @import("backing_geometry.zig");
    require(map.count > 0 and map.count <= planner.entry_limit);
    const source = map.entries orelse @panic("native backing map absent");
    var entries: [planner.entry_limit]planner.Entry = undefined;
    for (source[0..@intCast(map.count)], 0..) |entry, i| entries[i] = .{ .base = entry.base, .length = entry.length, .kind = entry.kind };
    const region = planner.select(entries[0..@intCast(map.count)], geometry.bytes) catch @panic("native backing reservation rejected");
    backing_boot_alias = planner.bootAlias(hhdm, region) catch @panic("native backing boot alias rejected");
    const plan = geometry.Plan.init(region.physical, region.bytes, backing_boot_alias) catch @panic("native backing alias geometry rejected");
    const image_bytes = @intFromPtr(&kernel_end) - @intFromPtr(&kernel_start);
    require(virtual == @intFromPtr(&kernel_start) and virtual == 0xffffffff80000000 and physical % 4096 == 0 and
        physical < 1 << 32 and image_bytes <= (1 << 32) - physical and
        (region.physical + region.bytes <= physical or physical + image_bytes <= region.physical));
    for (&states, 0..) |*state, owner| {
        backing_partitions[owner] = (if (combined_application_profile) @import("backing_pool.zig").Partition.filesystemApplication(owner, states.len) else if (combined_profile) @import("backing_pool.zig").Partition.filesystemSession(owner, states.len) else if (service_memory) @import("backing_pool.zig").Partition.service(owner, states.len) else @import("backing_pool.zig").Partition.init(owner, states.len, arena.page_count)) catch @panic("native backing owner geometry rejected");
        bindRecords(state);
        bindChildren(state);
        bindPayload(state, backing_boot_alias + backing_partitions[owner].first * 4096);
    }
    backing_pool.initialize(plan, physical);
    const bytes: [*]u8 = @ptrFromInt(backing_boot_alias);
    @memset(bytes[0..geometry.bytes], 0xa5);
    @memset(bytes[0..geometry.bytes], 0);
    const words: [*]const volatile u64 = @ptrFromInt(backing_boot_alias);
    for (0..geometry.bytes / 8) |i| require(words[i] == 0);
    backing_boot_views = true;
}
fn nativeBackingViews() void {
    if (!external_backing) return;
    require(backing_boot_views);
    for (&states, 0..) |*state, owner| bindPayload(state, backing_partitions[owner].alias());
    backing_boot_views = false;
}
fn backingOwner(state: *const State) usize {
    for (&states, 0..) |*candidate, owner| if (candidate == state) return owner;
    @panic("native backing owner absent");
}
// Reset per-generation authority, retaining the domain's checked physical owner.
// Called only after reclamation or before unpublished child construction.
fn resetState(state: *State) void {
    if (af09_enabled) af09.cancel(backingOwner(state), state.generation);
    @memset(std.mem.asBytes(state), 0);
    if (external_backing) {
        require(!backing_boot_views);
        bindPayload(state, backing_partitions[backingOwner(state)].alias());
        if (service_memory) {
            bindRecords(state);
            @memset(state.records(), .{});
            if (service_workers and !@import("build_options").native_service_workers_skip_rebind) {
                bindChildren(state);
                @memset(state.childRecords(), .{});
            }
        }
    }
}
fn backingFrame(state: *const State, index: usize) u64 {
    if (!external_backing) return phys(&state.backing[index]);
    return backing_partitions[backingOwner(state)].frame(backing_pool.plan, index) catch @panic("native backing frame outside owner");
}
fn setBackingAlias(mapping: *State, owner: *State, index: usize, writable: bool) void {
    if (external_backing) {
        if (!writable and @import("build_options").native_backing_skip_alias_ro) return;
        const partition = backing_partitions[backingOwner(owner)];
        require(index < partition.count);
        backing_pool.writable(partition.first + index, writable);
    } else {
        const n = (@intFromPtr(&owner.backing[index]) - @intFromPtr(&kernel_start)) / 4096;
        mapping.kpt[n / 512][n % 512] = backingFrame(owner, index) | (if (writable) @as(u64, 3) else 1) | nx;
    }
}
fn backingAliasEntry(mapping: *const State, owner: *const State, index: usize) u64 {
    if (external_backing) {
        const partition = backing_partitions[backingOwner(owner)];
        require(index < partition.count);
        return backing_pool.entry(partition.first + index);
    }
    const n = (@intFromPtr(&owner.backing[index]) - @intFromPtr(&kernel_start)) / 4096;
    return mapping.kpt[n / 512][n % 512];
}
var active: usize = 0;
var idle = false;
var idle_ticks: usize = 0;
var idle_stack: [16384]u8 align(16) = undefined;
var idle_frame: Frame = .{};
fn idleEntry() callconv(.c) noreturn {
    while (true) asm volatile ("hlt");
}
// BSP-owned numeric diagnostics only; no authority or context pointer is retained.
const worker_clock = service_workers and @import("build_options").native_clock;
var clock_scan_ticks: usize = 0;
var clock_scan_max_contexts: usize = 0;
var clock_scan_max_ns: u64 = 0;
var clock_scan_valid = true;
const native_tick_limit: usize = if (@import("build_options").native_service_zpl_budget) 6000 else 3000;
fn nativeTick() void {
    total_ticks = std.math.add(usize, total_ticks, 1) catch @panic("native clock exhausted");
    if (combined_profile or (!lifecycleEnabled() and !storageLifetime())) {
        if (total_ticks >= native_tick_limit) {
            var note: [96]u8 = undefined;
            serial.write(std.fmt.bufPrint(&note, "NATIVE assertion id=tick-budget ticks={d} limit={d}\n", .{ total_ticks, native_tick_limit }) catch "NATIVE assertion id=tick-budget\n");
        }
        require(total_ticks < native_tick_limit);
    }
    if (af09_enabled) af09Refresh();
    refreshSustained();
    const monotonic = monotonicNow();
    var scanned: usize = 0;
    for (&states, 0..) |*s, slot| if (s.admitted and !s.terminal) {
        const contexts = s.contexts();
        for (contextView(&contexts)) |context| {
            if (worker_clock) scanned += 1;
            completeWait(context, slot, 0, monotonic);
        }
    };
    if (worker_clock) {
        clock_scan_ticks = std.math.add(usize, clock_scan_ticks, 1) catch @panic("native clock scan exhausted");
        clock_scan_max_contexts = @max(clock_scan_max_contexts, scanned);
        const end = monotonicNow();
        if (monotonic != null and end != null and end.? >= monotonic.?) {
            clock_scan_max_ns = @max(clock_scan_max_ns, end.? - monotonic.?);
        } else clock_scan_valid = false;
    }
}
fn monotonicRead() @import("../../native_clock.zig").Error!u64 {
    if (@import("build_options").native_clock_ticks) return std.math.mul(u64, total_ticks, 10_000_000) catch error.Overflow;
    return @import("clock.zig").read();
}
fn monotonicNow() ?u64 {
    if (!@import("build_options").native_clock) return null;
    return monotonicRead() catch null;
}
fn completeWait(context: *Execution, slot: usize, key: usize, monotonic: ?u64) void {
    const clock_wait = context.wait.monotonic;
    if (context.wait.completeAt(key, total_ticks, monotonic)) |done| {
        if (clock_wait and done.status == -110) {
            var note: [160]u8 = undefined;
            serial.write(std.fmt.bufPrint(&note, "NATIVE CLOCK timeout task={d} now={d} elapsed={d}\n", .{ slot, monotonic.?, done.elapsed }) catch unreachable);
        }
        context.frame.rax = @bitCast(done.status);
        context.frame.rdx = done.elapsed;
    }
}
fn wakeAddress(s: *State, key: usize) usize {
    const contexts = s.contexts();
    return @import("native_execution.zig").wake(contextView(&contexts), key, total_ticks, monotonicNow(), std.math.maxInt(usize));
}
var supervised = false;
var launch_profile = false;
var channel_profile = false;
var file_profile = false;
var init_profile = false;
var init_large = false;
var init_composed = false;
var coexist_profile = false;
var program_profile = false;
var connections_profile = false;
var connections_large = false;
fn supervisorSlot() usize {
    return if (combined_profile) FsRoles.owner_slot else if (pipeline_capacity) 5 else if (program_profile) 3 else 2;
}
fn workerCount() usize {
    return supervisorSlot();
}
const application_image_bytes = if (combined_application_profile) elf.application_limits.file_bytes else 1024 * 1024;
var third_bytes: [application_image_bytes]u8 = undefined;
var third_len: usize = 0;
var third_image: elf.Image = undefined;
var observation: @import("../../native_wait.zig").Wait = .{};
const Channels = [if (combined_profile) FsRoles.channel_count else if (pipeline_capacity) 10 else 6]@import("../../native_channel.zig").Channel;
var channels: Channels = initChannels();
fn initChannels() Channels {
    var result_channels: Channels = @splat(.{});
    for (&result_channels, 0..) |*channel, index| channel.identity = index;
    return result_channels;
}
fn channelCount() usize {
    return if (combined_profile) FsRoles.channel_count else if (@import("build_options").native_service_channel) 2 else if (pipeline_capacity) 10 else if (connections_profile) (if (@import("build_options").native_coexist_small_pool) @as(usize, 4) else 6) else if (coexist_profile) (if (@import("build_options").native_coexist_small_pool) @as(usize, 2) else 4) else if (file_profile) 2 else 1;
}
var second_bytes: [application_image_bytes]u8 = undefined;
var second_len: usize = 0;
var second_image: elf.Image = undefined;
var io_profile = false;
var connections_console = false;
var pipeline_console = false;
const Sustained = @import("../../native_sustained.zig");
var sustained = false;
var session_lifecycle = false;

// Lifecycle scheduling is shared; identity and resource profiles remain distinct.
fn lifecycleEnabled() bool {
    return sustained or session_lifecycle;
}
// Separate private storage lifetime; never enables init/SESSION halt semantics.
fn storageLifetime() bool {
    return @import("build_options").native_service_lifetime;
}
fn ownerEventsEnabled() bool {
    return lifecycleEnabled() or storageLifetime();
}
fn storageMagic() []const u8 {
    return if (storageLifetime()) "AENBD005" else if (@import("build_options").native_service_channel_wait) "AENBD004" else "AENBD003";
}
const TickProjectionError = error{Overflow};
fn tickNanoseconds(ticks: usize) TickProjectionError!i64 {
    const ns = std.math.mul(u64, ticks, 10_000_000) catch return error.Overflow;
    if (ns > std.math.maxInt(i64)) return error.Overflow;
    return @intCast(ns);
}
var sustained_events: Sustained.Events = .{};
var pipeline_session = false;
var session_observations: u8 = 0;
var session_report_reclaimed: usize = 0;
fn lifetimeLimit() u64 {
    return if (sustained) Sustained.generation_limit else if (pipeline_session) 15 else 3;
}
var console_profile = false;
var console_closed = false;
var console_handoff = false;
var console_relay = false;
var block_profile = false;
var block_regions = false;
var block_base: u64 = 7;
var block_count: u64 = 1;
var block_closed = false;
var block_rights: u64 = 7;
var block_recipient: ?struct { slot: usize, generation: u64 } = null;
var console_recipient: ?struct { slot: usize, generation: u64 } = null;
var service_bytes: [if (@import("build_options").native_image_large and !combined_profile) 8 * 1024 * 1024 else application_image_bytes]u8 = undefined;
var service_len: usize = 0;
var service_image: elf.Image = undefined;
var engine_bytes: [if (combined_profile) 8 * 1024 * 1024 else 0]u8 = undefined;
var engine_len: usize = 0;
var engine_image: elf.Image = undefined;
var engine_entropy: [32]u8 = undefined;
var bootstrap: [if (pipeline_capacity) 80 else 48]u8 = undefined;
var reclaimed: usize = 0;
var total_ticks: usize = 0;
var physical: u64 = 0;
var virtual: u64 = 0;
fn phys(p: anytype) u64 {
    return @intFromPtr(p) - virtual + physical;
}
fn require(ok: bool) void {
    if (!ok) @panic("native C profile rejected");
}
fn mapKernel(s: *State) void {
    const kstart = @intFromPtr(&kernel_start);
    const end = @intFromPtr(&kernel_end);
    require(kstart == 0xffffffff80000000 and virtual == kstart and end - kstart <= s.kpt.len * memory.leaf_span);
    if (external_backing) backing_pool.attach(&s.root, physical);
    s.root[511] = phys(&s.kpdp) | 3;
    s.kpdp[510] = phys(&s.kpd) | 3;
    if (@import("build_options").native_clock) @import("clock.zig").attach(&s.kpdp);
    for (&s.kpt, 0..) |*pt, i| s.kpd[i] = phys(pt) | 3;
    var a = kstart;
    while (a < end) : (a += 4096) {
        const f: u64 = if (a >= @intFromPtr(&text_start) and a < @intFromPtr(&text_end)) 1 else if (a >= @intFromPtr(&rodata_start) and a < @intFromPtr(&rodata_end)) 1 | nx else 3 | nx;
        const n = (a - kstart) / 4096;
        s.kpt[n / 512][n % 512] = a - kstart + physical | f;
    }
}
fn addPage(s: *State, a: usize, flags: u64) void {
    require(s.count < s.pages.len and a % 4096 == 0 and a < 0x80000000);
    for (s.pages[0..s.count]) |p| require(p.address != a);
    const pd_index = a / (2 * 1024 * 1024);
    var found: ?usize = null;
    for (s.pt_index[0..s.pt_count], 0..) |value, i| if (value == pd_index) {
        found = i;
        break;
    };
    const t = found orelse blk: {
        require(s.pt_count < s.pts.len);
        const n = s.pt_count;
        s.pt_count += 1;
        s.pt_index[n] = pd_index;
        s.pd[pd_index] = phys(&s.pts[n]) | 7;
        break :blk n;
    };
    s.pts[t][a / 4096 % 512] = backingFrame(s, s.count) | flags;
    s.pages[s.count] = .{ .address = a, .flags = flags };
    s.count += 1;
}
fn byte(s: *State, address: usize, write: bool) ?*u8 {
    for (s.pages[0..s.count], 0..) |p, i| if (p.address != 0 and p.flags & 5 == 5 and address >= p.address and address - p.address < 4096) {
        if (write and p.flags & 2 == 0) return null;
        return &s.backing[i][address - p.address];
    };
    return null;
}
// Fixed mask/descriptor inputs copy only into private kernel stack arrays.
// IF=0 binds each checked page to this owner until the copy ends. Partial
// failure changes no caller-visible output or authority; no pointer is retained.
fn readUserBytes(s: *State, address: usize, output: []u8) bool {
    if (output.len == 0) return true;
    if (address > std.math.maxInt(usize) - (output.len - 1)) return false;
    var offset: usize = 0;
    while (offset < output.len) {
        const at = address + offset;
        const source: [*]const u8 = @ptrCast(byte(s, at, false) orelse return false);
        const count = @min(output.len - offset, 4096 - at % 4096);
        // The checked first byte and page boundary bind the complete fragment.
        // The next virtual page requires its own lookup and readable mapping.
        @memcpy(output[offset..][0..count], source[0..count]);
        offset += count;
    }
    return true;
}
const ChannelBuffer = struct { first: []u8, second: []u8 };
// A <=16-byte channel chunk touches at most two pages. Validate both before
// queue effects, preserving requested-count validation even for short transfers.
// IF=0 holds this owner's mappings stable; neither slice leaves this syscall.
fn channelBuffer(s: *State, address: usize, count: usize, write: bool) ?ChannelBuffer {
    std.debug.assert(count > 0 and count <= 16);
    const first: [*]u8 = @ptrCast(byte(s, address, write) orelse return null);
    const length = @min(count, 4096 - address % 4096);
    var second: []u8 = first[0..0];
    if (length < count) {
        const next: [*]u8 = @ptrCast(byte(s, address + length, write) orelse return null);
        second = next[0 .. count - length];
    }
    return .{ .first = first[0..length], .second = second };
}
fn copy(s: *State, address: usize, bytes: []const u8) void {
    var offset: usize = 0;
    while (offset < bytes.len) {
        const at = address + offset;
        const destination: [*]u8 = @ptrCast(byte(s, at, false) orelse @panic("native copy outside mapping"));
        const count = @min(bytes.len - offset, 4096 - at % 4096);
        // The validated first byte and page boundary bind the whole chunk to
        // one private backing allocation. Inputs never alias this destination.
        @memcpy(destination[0..count], bytes[offset..][0..count]);
        offset += count;
    }
}
fn word(s: *State, address: usize, value: u64) void {
    var b: [8]u8 = undefined;
    std.mem.writeInt(u64, &b, value, .little);
    copy(s, address, &b);
}
fn msr(index: u32, value: u64) void {
    asm volatile ("wrmsr"
        :
        : [lo] "{eax}" (@as(u32, @truncate(value))),
          [hi] "{edx}" (@as(u32, @truncate(value >> 32))),
          [index] "{ecx}" (index),
    );
}
fn select() *const Frame {
    refreshWait();
    refreshChannelWaits();
    if (af09_enabled) {
        af09Refresh();
        if (!idle and !states[active].on_child and af09Blocked(active)) rotate();
    }
    const s = &states[active];
    asm volatile ("mov %[p], %%cr3"
        :
        : [p] "r" (phys(&s.root)),
        : .{ .memory = true });
    if (idle) {
        msr(0xc0000100, 0);
        idle_frame = .{ .rip = @intFromPtr(&idleEntry), .rsp = @intFromPtr(&idle_stack) + idle_stack.len - 8, .cs = 8, .ss = 16, .flags = 0x202 };
        return &idle_frame;
    }
    msr(0xc0000100, s.context().fs);
    if (!@import("build_options").native_skip_fp) asm volatile ("fxrstor64 (%[p])"
        :
        : [p] "r" (&s.context().fp),
        : .{ .memory = true });
    return &s.context().frame;
}
pub fn start(pbase: u64, vbase: u64, envelope: []const u8, hhdm: u64, map: *const @import("../../limine.zig").MemoryResponse) noreturn {
    // Reject the selected complete composition before reservation or device setup.
    if (combined_application_profile) {
        _ = FsSession.parseApplication(envelope) catch @panic("invalid filesystem application envelope");
    }
    require(envelope.len > 40);
    const service_block = @import("build_options").native_service_block;
    const service_channel = @import("build_options").native_service_channel;
    const service_magic = if (combined_profile) (if (combined_application_profile) FsSession.application_magic else if (combined_owner_stack) FsSession.owner_stack_magic else if (combined_owner_data) FsSession.owner_data_magic else if (combined_init) FsSession.init_magic else FsSession.magic) else storageMagic();
    if (service_memory) require(std.mem.eql(u8, envelope[0..8], if (service_channel) service_magic else if (service_block) "AENBD002" else "AENSUP01"));
    const direct_native = std.mem.eql(u8, envelope[0..8], "AENATC01") or
        std.mem.eql(u8, envelope[0..8], "AENSUP01") or
        (service_block and std.mem.eql(u8, envelope[0..8], if (service_channel) service_magic else "AENBD002"));
    if (external_backing) {
        require(direct_native);
        asm volatile ("cli" ::: .{ .memory = true });
    }
    require((combined_profile or std.mem.eql(u8, envelope[0..8], "AENMX004") or std.mem.eql(u8, envelope[0..8], "AENMX005") or std.mem.eql(u8, envelope[0..8], "AENMX006") or std.mem.eql(u8, envelope[0..8], "AENMX007") or std.mem.eql(u8, envelope[0..8], "AENMX008") or std.mem.eql(u8, envelope[0..8], "AENMX009")) == pipeline_capacity);
    if (pipeline_capacity) require(!@import("build_options").native_coexist_small_pool and !@import("build_options").native_exec_denial);
    if (@import("build_options").native_thread_pair) require(@import("build_options").native_threads and @import("build_options").native_memory);
    session_lifecycle = combined_profile or std.mem.eql(u8, envelope[0..8], "AENMX009");
    require(session_lifecycle == @import("build_options").native_session_lifecycle);
    sustained = std.mem.eql(u8, envelope[0..8], "AENSI001");
    require(sustained == @import("build_options").native_init_sustained);
    if (sustained) {
        require(!pipeline_capacity and !@import("build_options").native_memory and !@import("build_options").native_threads and !@import("build_options").native_process_copy and !@import("build_options").native_process_exec and !@import("build_options").native_coexist_small_pool);
        for (&channels) |*channel| channel.sustained = true;
    }
    block_regions = std.mem.eql(u8, envelope[0..8], "AENBD002") or (service_channel and std.mem.eql(u8, envelope[0..8], service_magic));
    block_profile = block_regions or std.mem.eql(u8, envelope[0..8], "AENBD001");
    pipeline_session = session_lifecycle or std.mem.eql(u8, envelope[0..8], "AENMX007") or std.mem.eql(u8, envelope[0..8], "AENMX008");
    pipeline_console = session_lifecycle or std.mem.eql(u8, envelope[0..8], "AENMX006") or std.mem.eql(u8, envelope[0..8], "AENMX008");
    connections_console = sustained or std.mem.eql(u8, envelope[0..8], "AENMX003");
    console_relay = std.mem.eql(u8, envelope[0..8], "AENSC003");
    console_handoff = connections_console or console_relay or std.mem.eql(u8, envelope[0..8], "AENSC002");
    console_profile = pipeline_console or console_handoff or std.mem.eql(u8, envelope[0..8], "AENSC001");
    io_profile = std.mem.eql(u8, envelope[0..8], "AENFD001");
    connections_large = pipeline_capacity or connections_console or std.mem.eql(u8, envelope[0..8], "AENMX002");
    connections_profile = connections_large or std.mem.eql(u8, envelope[0..8], "AENMX001");
    program_profile = connections_profile or std.mem.eql(u8, envelope[0..8], "AENPG001");
    coexist_profile = program_profile or std.mem.eql(u8, envelope[0..8], "AENCO001");
    init_composed = std.mem.eql(u8, envelope[0..8], "AENIN003");
    init_large = init_composed or std.mem.eql(u8, envelope[0..8], "AENIN002");
    init_profile = init_large or console_relay or std.mem.eql(u8, envelope[0..8], "AENIN001");
    file_profile = coexist_profile or init_profile or std.mem.eql(u8, envelope[0..8], "AENFS001");
    channel_profile = service_channel or file_profile or std.mem.eql(u8, envelope[0..8], "AENCH001");
    launch_profile = combined_profile or (!service_channel and channel_profile) or std.mem.eql(u8, envelope[0..8], "AENEX001");
    supervised = block_profile or console_profile or launch_profile or io_profile or std.mem.eql(u8, envelope[0..8], "AENSUP01");
    require(supervised or std.mem.eql(u8, envelope[0..8], "AENATC01"));
    if (@import("build_options").native_image_large or @import("build_options").native_threads)
        require(direct_native);
    if (!launch_profile) require(envelope.len <= service_bytes.len + 4096 + 48);
    const bytes = envelope[40..];
    physical = pbase;
    virtual = vbase;
    if (external_backing) {
        const controls = asm volatile ("mov %%cr4, %[value]"
            : [value] "=r" (-> u64),
        );
        const protection = asm volatile ("mov %%cr0, %[value]"
            : [value] "=r" (-> u64),
        );
        const efer = asm volatile ("rdmsr"
            : [low] "={eax}" (-> u32),
            : [index] "{ecx}" (@as(u32, 0xc0000080)),
            : .{ .edx = true });
        require(controls & ((1 << 12) | (1 << 17) | (1 << 18)) == 0 and protection & (1 << 16) != 0 and efer & (1 << 11) != 0);
        prepareBacking(hhdm, map);
    }
    if (@import("build_options").native_entropy) {
        require(direct_native);
        @import("entropy.zig").initialize(pbase, vbase);
    }
    if (block_profile) @import("block.zig").initialize(pbase, vbase);
    if (block_regions) {
        block_base = 0;
        block_count = @import("block.zig").sectorCount();
    }
    if (@import("build_options").native_clock) @import("clock.zig").initialize(pbase, vbase, hhdm, map) catch @panic("native clock source rejected");
    @import("protection.zig").tables();
    const cr0 = asm volatile ("mov %%cr0, %[v]"
        : [v] "=r" (-> u64),
    );
    const cr4 = asm volatile ("mov %%cr4, %[v]"
        : [v] "=r" (-> u64),
    );
    require(cr4 & ((1 << 12) | (1 << 17) | (1 << 18)) == 0 and cr0 & (1 << 16) != 0);
    asm volatile ("mov %[v], %%cr0"
        :
        : [v] "r" ((cr0 | 2) & ~@as(u64, 12)),
        : .{ .memory = true });
    asm volatile ("mov %[v], %%cr4"
        :
        : [v] "r" ((cr4 | (1 << 9) | (1 << 10)) & ~@as(u64, 1 << 7)),
        : .{ .memory = true });
    if (supervised) startSupervised(envelope);
    const legacy_image = parseStartup(bytes) catch @panic("invalid native ELF");
    for (states[0..2], 0..) |*s, instance| {
        load(s, bytes, &legacy_image, envelope[8..40], instance);
    }

    // Every active kernel mapping removes writable aliases of both immutable images.
    for (states[0..2]) |*mapping| for (states[0..2]) |*owner| for (owner.pages[0..owner.count], 0..) |page, i| {
        if (page.address != 0 and page.flags & 2 == 0) {
            setBackingAlias(mapping, owner, i, false);
        }
    };
    nativeBackingViews();
    serial.write("NATIVE C: two isolated source-rebuilt musl instances; developer entropy input\n");
    @import("protection.zig").timerStart();
    msr(0xc0000100, 0);
    asm volatile ("fxrstor64 (%[p])"
        :
        : [p] "r" (&states[0].context().fp),
        : .{ .memory = true });
    restore_context(phys(&states[0].root), &states[0].context().frame);
}
fn result(s: *State, value: i64) void {
    s.context().frame.rax = @bitCast(value);
}
pub fn exception(frame: *const Frame) *const Frame {
    // The dedicated idle frame is the only resumable kernel-mode context.
    // Never save its registers over any blocked user frame.
    if (idle and frame.cs == 8 and frame.vector == 32) {
        serial.out(0x20, 0x20);
        idle_ticks = std.math.add(usize, idle_ticks, 1) catch @panic("native idle clock exhausted");
        nativeTick();
        rotate();
        return select();
    }
    if (frame.cs != 0x23) {
        var b: [160]u8 = undefined;
        serial.write(std.fmt.bufPrint(&b, "NATIVE kernel trap vector={d} cs={x} rip={x} error={x}\n", .{ frame.vector, frame.cs, frame.rip, frame.error_code }) catch "trap\n");
        @panic("native kernel trap");
    }
    const s = &states[active];
    s.context().frame = frame.*;
    asm volatile ("fxsave64 (%[p])"
        :
        : [p] "r" (&s.context().fp),
        : .{ .memory = true });
    if (frame.vector == 32) {
        serial.out(0x20, 0x20);
        s.ticks = std.math.add(usize, s.ticks, 1) catch @panic("native task clock exhausted");
        nativeTick();
        rotate();
        return select();
    }
    if (frame.vector != 129) {
        var b: [128]u8 = undefined;
        serial.write(std.fmt.bufPrint(&b, "NATIVE fault vector={d} rip={x} error={x}\n", .{ frame.vector, frame.rip, frame.error_code }) catch "native fault\n");
        return finish(128 + frame.vector, 2);
    }
    if (@import("build_options").native_entropy and frame.rax >= 0x2b000 and frame.rax <= 0x2b001) return entropyOperation(frame);
    if (block_profile and frame.rax >= 0x27000 and frame.rax <= (if (block_regions) @as(u64, 0x27006) else 0x27004)) return blockOperation(frame);
    if (console_profile and frame.rax >= 0x26000 and frame.rax <= (if (console_handoff) @as(u64, 0x26003) else 0x26002)) return consoleOperation(frame);
    if (ownerEventsEnabled() and frame.rax >= 0x2a000 and frame.rax <= 0x2a002) return sustainedOperation(frame);
    if (init_profile and frame.rax >= 0x25000 and frame.rax <= 0x25005) return waitOperation(frame);
    if (channel_profile and frame.rax >= 0x24000 and frame.rax <= 0x24004) return channelOperation(frame);
    if (@import("build_options").native_process_exec and connections_profile and frame.rax >= 0x23007 and frame.rax <= 0x23009) return execOperation(frame);
    if (@import("build_options").native_process_copy and connections_profile and frame.rax == 0x23006) return copyOperation(frame);
    if (@import("build_options").native_process_freeze and connections_profile and frame.rax >= 0x23003 and frame.rax <= 0x23005) return freezeOperation(frame);
    if (launch_profile and (frame.rax == 0x23000 or (channel_profile and frame.rax == 0x23001) or (file_profile and frame.rax == 0x23002))) return launchOperation(frame);
    if (frame.rax >= 0x22000 and frame.rax <= 0x22003 and @import("build_options").native_memory) return memoryOperation(frame);
    if (io_profile and frame.rax >= 0x21000 and frame.rax <= 0x21002) return streamOperation(frame);
    if (io_profile and (frame.rax == 0x20008 or frame.rax == 0x20009)) return streamControl(frame);
    if (@import("build_options").native_service_channel and frame.rax == 0x20008) return control(frame);
    if (io_profile and frame.rax == 0x10001) {
        result(s, -38);
        return select();
    }
    if (pipeline_session and frame.rax == 0x2000a) return sessionObservation(frame);
    if (supervised and frame.rax >= 0x20000 and frame.rax <= 0x20007) return control(frame);
    if (threadedSlot(active) and frame.rax >= 0x28000 and frame.rax <= 0x28011) return threadOperation(frame);
    if (frame.rax == 0x29000 or frame.rax == 0x1000f) return signalFrameOperation(frame);
    if (frame.rax == 0x29002) {
        if (@import("build_options").native_signal_actions) {
            if (connections_profile and !threadedSlot(active)) {
                if (selfSignalOperation(s, frame)) |terminal| return finish(terminal.detail, terminal.kind);
                return select();
            }
        }
        result(s, -38);
        return select();
    }
    if (frame.rax == 0x29001 or (frame.rax == 0x1000d and @import("build_options").native_signal_public)) {
        if (@import("build_options").native_signal_actions) {
            if (connections_profile and !threadedSlot(active)) {
                actionRecordOperation(s, frame);
                return select();
            }
        }
        result(s, -38);
        return select();
    }
    if (frame.rax == 0x10082) {
        if (@import("build_options").native_signal_suspend) {
            if (connections_profile and !threadedSlot(active) and active != supervisorSlot()) {
                suspendOperation(s, frame);
                rotate();
                return select();
            }
        }
        result(s, -38);
        return select();
    }
    switch (frame.rax) {
        0x10000 + 14 => {
            if (!connections_profile or !@import("build_options").native_runner_local) {
                result(s, -38);
            } else if (frame.r10 != 8) {
                result(s, -22);
            } else {
                // Musl's four-argument transport leaves r8/r9 unspecified.
                changeMask(s, frame.rdi, frame.rsi, frame.rdx);
                if (@import("build_options").native_signal_mask_delivery and !threadedSlot(active)) {
                    if (s.context().frame.rax == 0) _ = deliverPending(s, &s.context().frame, false);
                }
            }
        },
        0x10000 + 110 => {
            // Zero-argument libc call: unused registers have no meaning.
            // In this bounded profile all workers have the fixed direct launcher
            // as parent. Its shutdown cannot leave a running orphan behind.
            if (!connections_profile or (!@import("build_options").native_parent_identity and !@import("build_options").native_process_copy)) {
                result(s, -38);
            } else {
                const parent = supervisorSlot();
                result(s, if (active == parent) 0 else if (@import("build_options").native_process_copy and s.parent_pid != 0) @intCast(s.parent_pid) else @intCast(states[parent].generation * states.len + parent + 1));
            }
        },
        0x10000 + 39 => {
            // Bookkeeping identity only: actual caller slot and nonwrapping lifetime.
            // No PID grants authority; image replacement preserves this identity.
            if (!connections_profile or (!@import("build_options").native_runner_local and !@import("build_options").native_process_copy)) {
                result(s, -38);
            } else {
                result(s, @intCast(s.generation * states.len + active + 1));
            }
        },
        0x1fffe => {
            if (!s.on_child) s.yields = std.math.add(usize, s.yields, 1) catch @panic("native yield counter exhausted");
            result(s, 0);
            rotate();
            return select();
        },
        0x10000 + 158 => { // Native experiment set-FS operation, musl arg translation retained.
            if (frame.rdi != 0x1002 or byte(s, @intCast(frame.rsi), true) == null or
                (s.context().tls_bytes != 0 and (frame.rsi < s.context().tls_base or frame.rsi - s.context().tls_base >= s.context().tls_bytes)))
            {
                result(s, -22);
            } else {
                s.context().fs = frame.rsi;
                result(s, 0);
            }
        },
        0x10000 + 218 => {
            const p: usize = @intCast(frame.rdi);
            if (p > std.math.maxInt(usize) - 4 or byte(s, p, true) == null or byte(s, p + 3, true) == null) {
                result(s, -14);
            } else {
                s.context().clear_tid = p;
                result(s, @intCast(if (@import("build_options").native_process_copy and connections_profile and !threadedSlot(active) and !@import("build_options").native_copy_slot_tid)
                    s.generation * states.len + active + 1
                else if (s.on_child and s.child().execution.tls_bytes != 0) s.child().id else active + 1));
            }
        },
        0x10000 + 1 => {
            if (frame.rdi != 1) {
                result(s, -9);
            } else if (@import("build_options").native_no_output) {
                result(s, -13);
            } else if (frame.rdx > 256 or frame.rsi > std.math.maxInt(u64) - frame.rdx) {
                result(s, -14);
            } else {
                const count: usize = @intCast(@min(frame.rdx, 16));
                var valid = true;
                for (0..count) |i| if (byte(s, @intCast(frame.rsi + i), false) == null) {
                    valid = false;
                };
                if (!valid) {
                    result(s, -14);
                } else if (count > s.output.len - s.output_count) {
                    result(s, -28);
                } else {
                    for (0..count) |i| s.output[s.output_count + i] = byte(s, @intCast(frame.rsi + i), false).?.*;
                    if (@import("build_options").native_service_block and count == 8) {
                        // Uninterpreted numeric observation; output has already
                        // passed the existing authority/pointer/capacity checks.
                        var note: [160]u8 = undefined;
                        serial.write(std.fmt.bufPrint(&note, "NATIVE observation slot={d} generation={d} offset={d} byte={d}\n", .{ active, s.generation, s.output_count, s.output[s.output_count] }) catch unreachable);
                    }
                    const output_offset = s.output_count;
                    s.output_count += count;
                    result(s, @intCast(count));
                    if (af09_enabled) af09Output(frame, output_offset, count);
                }
            }
        },
        0x10000 + 231, 0x10000 + 60 => return finish(frame.rdi, 1),
        else => result(s, -38),
    }
    return select();
}

// Synchronous self-upcall only: no asynchronous entry into the command transport.
fn signalFrameOperation(frame: *const Frame) *const Frame {
    const s = &states[active];
    if (!connections_profile or !@import("build_options").native_runner_local or threadedSlot(active)) {
        result(s, -38);
        return select();
    }
    const signals = @import("native_signal.zig");
    const context = s.context();
    // exception() just executed FXSAVE into owner storage. Never use a user
    // payload's mask to decide what FXRSTOR may accept.
    const hardware_mask = std.mem.readInt(u32, context.fp[28..32], .little);
    const mxcsr_mask = if (hardware_mask == 0) @as(u32, 0xffbf) else hardware_mask;
    var candidate: signals.Candidate = undefined;
    if (frame.rax == 0x1000f) {
        signals.readReturnInto(s.pages[0..s.count], s.backing[0..s.count], frame.rsp, mxcsr_mask, &candidate) catch {
            result(s, -22);
            return select();
        };
    } else {
        if (frame.rdx > 31 or frame.r8 | frame.r9 != 0) {
            result(s, -22);
            return select();
        }
        var request: signals.Entry = undefined;
        request.cpu = frame.*;
        request.cpu.rax = 0;
        request.fp = context.fp;
        request.mask = context.signal_mask;
        request.action_mask = frame.r10;
        request.handler = frame.rdi;
        request.restorer = frame.rsi;
        request.signal = @intCast(frame.rdx);
        request.stack_low = 0x08000000;
        request.stack_high = 0x08010000;
        signals.prepareEntryInto(s.pages[0..s.count], s.backing[0..s.count], &request, mxcsr_mask, &candidate) catch {
            result(s, -22);
            return select();
        };
    }
    // IF=0 excludes execution and mapping mutation until the complete validated
    // candidate is published. No other Execution fields are supplied by user data.
    context.frame = candidate.cpu;
    context.fp = candidate.fp;
    context.signal_mask = candidate.mask;
    return select();
}

// Explicit self-post/poll only. IF=0 serializes selection, checked frame copy
// and dequeue; no command-transport or timer return injects a handler here.
fn selfSignalOperation(s: *State, frame: *const Frame) ?@import("native_pending.zig").SignalTerminal {
    const actions = @import("native_pending.zig");
    if (frame.rdi > 31 or frame.rsi | frame.rdx | frame.r10 | frame.r8 | frame.r9 != 0) {
        result(s, -22);
        return null;
    }
    if (frame.rdi != 0) {
        const signal: u8 = @intCast(frame.rdi);
        const action = s.signal_actions.action(signal) catch {
            result(s, -22);
            return null;
        };
        if (action == .default and (actions.defaultEffect(signal) catch unreachable) != .ignore) {
            if (!@import("build_options").native_signal_termination or active == supervisorSlot() or
                (actions.defaultEffect(signal) catch unreachable) != .terminate)
            {
                result(s, -95);
                return null;
            }
        }
        s.signal_actions.post(signal) catch unreachable;
    }
    result(s, 0);
    return deliverPending(s, &s.context().frame, true);
}

// Automatic callers have already committed their syscall: preserve its result
// on preparation failure. Only explicit polls may publish a default terminal.
fn deliverPending(s: *State, frame: *const Frame, explicit: bool) ?@import("native_pending.zig").SignalTerminal {
    const actions = @import("native_pending.zig");
    const selected = s.signal_actions.peek(s.context().signal_mask) orelse {
        return null;
    };
    if (!explicit and selected.action != .handler) return null;
    if (selected.action == .default and @import("build_options").native_signal_termination and active != supervisorSlot()) {
        const terminal = actions.defaultTermination(selected.signal) catch {
            if (explicit) result(s, -95);
            return null;
        };
        s.signal_actions.commit(selected.signal) catch unreachable;
        return terminal;
    }
    if (selected.action != .handler) {
        if (explicit) result(s, -95);
        return null;
    }
    const handler = selected.action.handler;
    const signals = @import("native_signal.zig");
    const context = s.context();
    const hardware_mask = std.mem.readInt(u32, context.fp[28..32], .little);
    const request: signals.Entry = .{
        .cpu = frame.*,
        .fp = context.fp,
        .mask = context.signal_mask,
        .action_mask = handler.mask,
        .handler = handler.entry,
        .restorer = handler.restorer,
        .signal = @intCast(selected.signal),
        .stack_low = 0x08000000,
        .stack_high = 0x08010000,
    };
    var candidate: signals.Candidate = undefined;
    signals.prepareEntryInto(s.pages[0..s.count], s.backing[0..s.count], &request, if (hardware_mask == 0) 0xffbf else hardware_mask, &candidate) catch {
        if (explicit) result(s, -22);
        return null;
    };
    s.signal_actions.commit(selected.signal) catch unreachable;
    context.frame = candidate.cpu;
    context.fp = candidate.fp;
    context.signal_mask = candidate.mask;
    return null;
}

// Opt-in, BSP-only. Trap/selection serialization stays held through frame
// validation, pending dequeue and publication. No user pointer is retained.
fn resumeSuspended(s: *State) void {
    if (!@import("build_options").native_signal_suspend) return;
    const original = s.suspend_mask orelse return;
    const actions = @import("native_pending.zig");
    var selected = s.signal_actions.peek(s.context().signal_mask) orelse return;
    while (selected.action == .ignore or (selected.action == .default and (actions.defaultEffect(selected.signal) catch unreachable) == .ignore)) {
        s.signal_actions.commit(selected.signal) catch unreachable;
        selected = s.signal_actions.peek(s.context().signal_mask) orelse return;
    }
    // This initial handler-only profile preserves unsupported defaults explicitly.
    if (selected.action != .handler) {
        s.context().signal_mask = original;
        s.suspend_mask = null;
        result(s, -95);
        return;
    }
    const handler = selected.action.handler;
    const signals = @import("native_signal.zig");
    const context = s.context();
    var interrupted = context.frame;
    interrupted.rax = @bitCast(@as(i64, -4));
    const request: signals.Entry = .{
        .cpu = interrupted,
        .fp = context.fp,
        .mask = context.signal_mask,
        .action_mask = handler.mask,
        .handler = handler.entry,
        .restorer = handler.restorer,
        .signal = @intCast(selected.signal),
        .stack_low = 0x08000000,
        .stack_high = 0x08010000,
    };
    const mxcsr = std.mem.readInt(u32, context.fp[28..32], .little);
    var candidate: signals.Candidate = undefined;
    signals.prepareSuspendEntryInto(s.pages[0..s.count], s.backing[0..s.count], &request, original, if (mxcsr == 0) 0xffbf else mxcsr, &candidate) catch {
        context.signal_mask = original;
        s.suspend_mask = null;
        result(s, -22);
        return;
    };
    s.signal_actions.commit(selected.signal) catch unreachable;
    context.frame = candidate.cpu;
    context.fp = candidate.fp;
    context.signal_mask = candidate.mask;
    s.suspend_mask = null;
}
fn suspendOperation(s: *State, f: *const Frame) void {
    if (!@import("build_options").native_signal_suspend) return;
    if (f.rsi != 8) {
        result(s, -22);
        return;
    }
    if (f.rdi > std.math.maxInt(u64) - 7) {
        result(s, -14);
        return;
    }
    var raw: [8]u8 = undefined;
    for (&raw, 0..) |*v, i| v.* = (byte(s, f.rdi + i, false) orelse {
        result(s, -14);
        return;
    }).*;
    s.suspend_mask = s.context().signal_mask;
    s.context().signal_mask = std.mem.readInt(u64, &raw, .little) & ~@as(u64, (1 << 8) | (1 << 18));
    resumeSuspended(s);
}
// Only the native copy operation writes this relationship. Its generation is
// revalidated; names and caller-supplied PIDs never select a notification target.
fn notifyParent(child: *const State) void {
    if (!@import("build_options").native_signal_suspend or threadedSlot(active)) return;
    if (child.parent_pid == 0) return;
    for (states[0..workerCount()], 0..) |*parent, slot| {
        if (parent.admitted and !parent.terminal and child.parent_pid == parent.generation * states.len + slot + 1) {
            parent.signal_actions.post(17) catch unreachable;
            return;
        }
    }
}

fn actionRecordOperation(s: *State, f: *const Frame) void {
    const actions = @import("native_pending.zig");
    if (f.rdi > 64 or f.r10 != 8 or (f.rax == 0x29001 and f.r8 | f.r9 != 0)) {
        result(s, -22);
        return;
    }
    const signal: u8 = @intCast(f.rdi);
    const owner = if (@import("build_options").native_signal_actions_shared) &states[0] else s;
    const old = owner.signal_actions.query(signal) catch {
        result(s, -22);
        return;
    };
    var raw: [32]u8 = undefined;
    if (f.rsi != 0) {
        if (f.rsi > std.math.maxInt(usize) - 31) {
            result(s, -14);
            return;
        }
        for (&raw, 0..) |*v, i| v.* = (byte(s, f.rsi + i, false) orelse {
            result(s, -14);
            return;
        }).*;
    }
    if (f.rdx != 0) {
        if (f.rdx > std.math.maxInt(usize) - 31) {
            result(s, -14);
            return;
        }
        for (0..32) |i| if (byte(s, f.rdx + i, true) == null) {
            result(s, -14);
            return;
        };
    }
    if (f.rsi != 0) {
        const next = std.mem.bytesAsValue(actions.Record, &raw).*;
        if (next.entry > 1) {
            for ([_]u64{ next.entry, next.restorer }) |address| {
                var rx = false;
                for (s.pages[0..s.count]) |page| {
                    if (page.address == address & ~@as(u64, 4095) and page.flags & (nx | 7) == 5) rx = true;
                }
                if (!rx) {
                    result(s, -22);
                    return;
                }
            }
        }
        const installed = if (f.rax == 0x1000d)
            owner.signal_actions.installPublicRecord(signal, next)
        else
            owner.signal_actions.installRecord(signal, next);
        _ = installed catch |err| {
            result(s, if (err == error.NotSupported) -95 else -22);
            return;
        };
    }
    // IF=0 serializes all mapping and record changes through publication.
    // Input was snapshotted, so overlapping old-output cannot change next.
    if (f.rdx != 0) for (std.mem.asBytes(&old), 0..) |value, i| {
        byte(s, f.rdx + i, true).?.* = value;
    };
    result(s, 0);
}

// Both caller protocols mutate one context-owned mask. No user pointer is retained.
fn changeMask(s: *State, how: u64, set: u64, old_address: u64) void {
    if (set != 0 and how > 2) {
        result(s, -22);
        return;
    }
    var input: [8]u8 = undefined;
    // Owner executes with IF=0. Snapshot input and validate all output bytes
    // before committing: input/output may overlap or cross a page boundary.
    if (set != 0) {
        if (set > std.math.maxInt(usize) - 7) {
            result(s, -14);
            return;
        }
        if (!readUserBytes(s, set, &input)) {
            result(s, -14);
            return;
        }
    }
    if (old_address != 0) {
        if (old_address > std.math.maxInt(usize) - 7) {
            result(s, -14);
            return;
        }
        // Eight bytes span at most two pages; validate both endpoints before
        // the existing page-fragment write, including overlapping input/output.
        if (byte(s, old_address, true) == null or byte(s, old_address + 7, true) == null) {
            result(s, -14);
            return;
        }
    }
    const old = s.context().signal_mask;
    const next = if (set == 0) old else @import("native_execution.zig").maskAfter(old, how, std.mem.readInt(u64, &input, .little)) catch unreachable;
    if (old_address != 0) word(s, old_address, old);
    s.context().signal_mask = next;
    result(s, 0);
}

fn clearTid(s: *State, context: *Execution) void {
    if (context.clear_tid != 0) {
        for (0..4) |i| (byte(s, context.clear_tid + i, true) orelse @panic("stale clear-tid")).* = 0;
        _ = wakeAddress(s, context.clear_tid);
        context.clear_tid = 0;
    }
}
fn stopContexts(s: *State) void {
    s.channel_wait = .{};
    if (@import("build_options").native_signal_suspend) s.suspend_mask = null;
    s.frozen = false;
    s.execution.wait = .{};
    clearTid(s, &s.execution);
    for (s.childRecords()) |*c| {
        c.execution.wait = .{};
        clearTid(s, &c.execution);
        c.running = false;
    }
    s.on_child = false;
    s.thread_cap = 0;
}

// IF remains clear from pointer validation through TID write and publication.
// The child owns no mappings: all backing and authority stay in this domain.
fn threadOperation(f: *const Frame) *const Frame {
    const s = &states[active];
    if (!s.admitted or s.terminal or s.thread_cap == 0 or f.rdi != s.thread_cap) {
        result(s, -13);
    } else if (f.rax == 0x28011) {
        if (!@import("build_options").native_rtc) {
            result(s, -38);
        } else if (f.rsi == 0 or f.rsi % 8 != 0 or f.rdx != 64 or f.r10 != 0 or f.r8 != 0 or f.r9 != 0) {
            result(s, -22);
        } else {
            if (f.rsi > std.math.maxInt(usize) - 63) {
                result(s, -14);
                return select();
            }
            for (0..64) |i| if (byte(s, f.rsi + i, true) == null) {
                result(s, -14);
                return select();
            };
            const rtc_value = @import("rtc.zig").observe() catch |err| {
                result(s, switch (err) {
                    error.Unavailable => -38,
                    error.Busy => -11,
                    error.Regression => -5,
                    error.Overflow => -75,
                });
                return select();
            };
            for (std.mem.asBytes(&rtc_value), 0..) |value, i| byte(s, f.rsi + i, true).?.* = value;
            result(s, 0);
        }
    } else if (f.rax == 0x2800f or f.rax == 0x28010) {
        if (!@import("build_options").native_clock) {
            result(s, -38);
        } else if (f.r8 != 0 or f.r9 != 0 or
            (f.rax == 0x2800f and (f.rsi != 0 or f.rdx != 0 or f.r10 != 0)) or
            (f.rax == 0x28010 and (f.rsi == 0 or f.rsi % 4 != 0 or f.rdx > std.math.maxInt(u32))))
        {
            result(s, -22);
        } else if (f.rax == 0x28010 and (f.rsi > std.math.maxInt(usize) - 4 or
            byte(s, f.rsi, true) == null or byte(s, f.rsi + 3, true) == null))
        {
            result(s, -14);
        } else {
            const now = monotonicRead() catch |err| {
                result(s, switch (err) {
                    error.Unavailable => -38,
                    error.Regression => -5,
                    error.Overflow => -75,
                });
                return select();
            };
            if (f.rax == 0x2800f) {
                result(s, @intCast(now));
            } else {
                var bytes: [4]u8 = undefined;
                for (&bytes, 0..) |*v, i| v.* = byte(s, f.rsi + i, true).?.*;
                const status = s.context().wait.parkAbsolute(f.rsi, std.mem.readInt(u32, &bytes, .little), @intCast(f.rdx), now, f.r10);
                result(s, status);
                s.context().frame.rdx = 0;
                if (status == 0) {
                    var note: [160]u8 = undefined;
                    serial.write(std.fmt.bufPrint(&note, "NATIVE CLOCK park task={d} start={d} deadline={d}\n", .{ active, now, f.r10 }) catch unreachable);
                    if (@import("build_options").native_clock_skip_wait) {
                        s.context().wait = .{};
                        result(s, -110);
                    } else rotate();
                    return select();
                }
            }
        }
    } else if ((f.rax == 0x2800b or f.rax == 0x2800c or f.rax == 0x2800d or f.rax == 0x2800e) and !@import("build_options").native_thread_pair) {
        result(s, -38);
    } else if (f.rax == 0x2800e) {
        if (f.rsi != 0 or f.rdx != 0 or f.r10 != 0 or f.r8 != 0 or f.r9 != 0) {
            result(s, -22);
        } else {
            // Boot-local delivered time, not calibrated wall time. IF is clear.
            result(s, tickNanoseconds(total_ticks) catch -75);
        }
    } else if (f.rax == 0x2800d) {
        if (f.rsi == 0 or f.r8 == 0 or f.rsi == f.r8 or f.rsi % 4 != 0 or f.r8 % 4 != 0 or f.rdx > std.math.maxInt(i32) or f.r10 > std.math.maxInt(i32) or f.r9 != 0) {
            result(s, -22);
        } else if (f.rsi > std.math.maxInt(usize) - 4 or f.r8 > std.math.maxInt(usize) - 4 or
            byte(s, f.rsi, true) == null or byte(s, f.rsi + 3, true) == null or
            byte(s, f.r8, true) == null or byte(s, f.r8 + 3, true) == null)
        {
            result(s, -14);
        } else {
            const destination = if (@import("build_options").native_requeue_skip_move) f.rsi else f.r8;
            const contexts = s.contexts();
            result(s, @intCast(@import("native_execution.zig").requeue(contextView(&contexts), f.rsi, destination, total_ticks, monotonicNow(), @intCast(f.rdx), @intCast(f.r10))));
        }
    } else if (f.rax == 0x2800c) {
        if (f.rsi == 0 or f.rsi % 4 != 0 or f.rdx > std.math.maxInt(i32) or f.r10 != 0 or f.r8 != 0 or f.r9 != 0) {
            result(s, -22);
        } else if (f.rsi > std.math.maxInt(usize) - 4 or byte(s, f.rsi, true) == null or byte(s, f.rsi + 3, true) == null) {
            result(s, -14);
        } else {
            const limit: usize = if (@import("build_options").native_wake_unlimited and f.rdx != 0) std.math.maxInt(usize) else @intCast(f.rdx);
            const contexts = s.contexts();
            result(s, @intCast(@import("native_execution.zig").wake(contextView(&contexts), f.rsi, total_ticks, monotonicNow(), limit)));
        }
    } else if (f.rax == 0x2800a or f.rax == 0x2800b) {
        if (s.on_child and !@import("build_options").native_thread_origin) {
            result(s, -13);
        } else if (f.rsi == 0 or f.rsi > std.math.maxInt(u32) or f.rdx != 0 or f.r10 != 0 or f.r8 != 0 or f.r9 != 0) {
            result(s, -22);
        } else {
            // Exit stopped execution and handled clear-TID; retire touches no mappings.
            var any = false;
            var found: ?*@import("native_execution.zig").Child = null;
            for (s.childRecords()) |*c| if (c.used) {
                any = true;
                if (c.id == f.rsi) found = c;
            };
            if (found) |c| {
                if (f.rax == 0x2800a) result(s, c.retire(@intCast(f.rsi))) else {
                    result(s, if (c.running) 0 else @as(i64, c.status) + 1);
                    s.context().frame.rdx = @intFromBool(c.execution.wait.address != 0);
                }
            } else result(s, if (any) -9 else -2);
        }
    } else if (f.rax == 0x28009) {
        if (f.r8 != 0 or f.r9 != 0 or (f.rdx != 0 and f.rsi > 2)) {
            result(s, -22);
            return select();
        }
        changeMask(s, f.rsi, f.rdx, f.r10);
    } else if (f.rax == 0x28007) {
        if (f.rsi != 0 or f.rdx != 0 or f.r10 != 0 or f.r8 != 0 or f.r9 != 0) {
            result(s, -22);
        } else {
            result(s, @intCast(if (!s.on_child) active + 1 else s.child().id));
        }
    } else if (f.rax == 0x28003 or f.rax == 0x28004 or f.rax == 0x28008) {
        if (f.rsi == 0 or f.rsi % 4 != 0 or f.r8 != 0 or f.r9 != 0 or
            (f.rax == 0x28003 and (f.rdx > std.math.maxInt(u32) or f.r10 == 0 or f.r10 > 100)) or
            (f.rax == 0x28004 and (f.rdx != 0 or f.r10 != 0)) or
            (f.rax == 0x28008 and (f.rdx > std.math.maxInt(u32) or f.r10 != 0)))
        {
            result(s, -22);
            return select();
        }
        if (f.rsi > std.math.maxInt(usize) - 4 or byte(s, f.rsi, true) == null or byte(s, f.rsi + 3, true) == null) {
            result(s, -14);
            return select();
        }
        if (f.rax == 0x28004) {
            result(s, @intCast(wakeAddress(s, f.rsi)));
        } else {
            var bytes: [4]u8 = undefined;
            for (&bytes, 0..) |*v, i| v.* = byte(s, f.rsi + i, true).?.*;
            const value = if (@import("build_options").native_wait_skip_compare) @as(u32, @intCast(f.rdx)) else std.mem.readInt(u32, &bytes, .little);
            const status = if (f.rax == 0x28008)
                s.context().wait.parkIndefinite(f.rsi, value, @intCast(f.rdx), total_ticks)
            else
                s.context().wait.park(f.rsi, value, @intCast(f.rdx), total_ticks, f.r10);
            result(s, status);
            s.context().frame.rdx = 0;
            if (status == 0) rotate();
        }
    } else if (f.rax == 0x28000 or f.rax == 0x28005 or f.rax == 0x28006) {
        if (s.on_child and !@import("build_options").native_thread_origin) {
            result(s, -13);
            return select();
        }
        var available: ?usize = null;
        for (s.children, 0..) |c, i| if (!c.used) {
            available = i;
            break;
        };
        if (available == null or s.child_admissions >= @import("native_execution.zig").admissionLimit(@import("build_options").native_thread_reuse)) {
            result(s, -28);
            return select();
        }
        var request = f.*;
        var stack_bytes: u64 = 4096;
        var tls_base: u64 = 0;
        var tls_bytes: u64 = 0;
        var parent_tid: u64 = 0;
        const storage = f.rax == 0x28006;
        var rsp = std.math.add(u64, f.rdx, 4088) catch 0;
        if (f.rax == 0x28005 or storage) {
            if (f.rdx != 0 or f.r10 != 0 or f.r8 != 0 or f.r9 != 0) {
                result(s, -22);
                return select();
            }
            const descriptor_bytes: usize = if (storage) 96 else 64;
            if (f.rsi > std.math.maxInt(usize) - descriptor_bytes) {
                result(s, -14);
                return select();
            }
            var descriptor: [96]u8 = undefined;
            if (!readUserBytes(s, f.rsi, descriptor[0..descriptor_bytes])) {
                result(s, -14);
                return select();
            }
            if (std.mem.readInt(u32, descriptor[0..4], .little) != 1 or std.mem.readInt(u32, descriptor[4..8], .little) != descriptor_bytes) {
                result(s, -22);
                return select();
            }
            if (storage) {
                tls_base = std.mem.readInt(u64, descriptor[64..72], .little);
                tls_bytes = std.mem.readInt(u64, descriptor[72..80], .little);
                parent_tid = std.mem.readInt(u64, descriptor[80..88], .little);
                if (std.mem.readInt(u64, descriptor[88..96], .little) != 0 or parent_tid == 0 or parent_tid % 4 != 0) {
                    result(s, -22);
                    return select();
                }
            }
            request.rsi = std.mem.readInt(u64, descriptor[8..16], .little);
            request.rdx = std.mem.readInt(u64, descriptor[16..24], .little);
            stack_bytes = std.mem.readInt(u64, descriptor[24..32], .little);
            rsp = std.mem.readInt(u64, descriptor[32..40], .little);
            request.r10 = std.mem.readInt(u64, descriptor[40..48], .little);
            request.r9 = std.mem.readInt(u64, descriptor[48..56], .little);
            request.r8 = std.mem.readInt(u64, descriptor[56..64], .little);
            @import("native_execution.zig").stackRange(request.rdx, stack_bytes, rsp, memory.base, arenaEnd(s)) catch {
                result(s, -22);
                return select();
            };
        }
        const r = &request;
        if (r.rdx % 4096 != 0 or r.r9 % 4 != 0 or r.r9 == 0 or r.r10 == 0) {
            result(s, -22);
            return select();
        }
        if (storage) {
            if (tls_base < memory.base or tls_base > arenaEnd(s) or tls_base % 4096 != 0 or
                tls_bytes == 0 or tls_bytes % 4096 != 0 or tls_bytes > arenaEnd(s) - tls_base or
                r.r10 < tls_base or r.r10 - tls_base >= tls_bytes)
            {
                result(s, -22);
                return select();
            }
        }
        const stack_plan = arena.range(s.records(), r.rdx, stack_bytes, 0, 0) catch {
            result(s, -14);
            return select();
        };
        var stack_slots = stack_plan.rangeSlots(s.records());
        for (0..stack_plan.count) |offset| if (s.pages[if (service_workers) stack_slots.next().? else stack_plan.slot(s.records(), offset)].flags != 7 | nx) {
            result(s, -14);
            return select();
        };
        var entry = false;
        for (s.pages[0..s.count]) |page| {
            if (page.address != 0 and page.flags & (nx | 7) == 5 and r.rsi >= page.address and r.rsi - page.address < 4096) entry = true;
        }
        if (!entry or byte(s, r.r10, true) == null or r.r9 > std.math.maxInt(usize) - 4 or
            byte(s, r.r9, true) == null or byte(s, r.r9 + 3, true) == null)
        {
            result(s, -14);
            return select();
        }
        if (storage) {
            const tls_plan = arena.range(s.records(), tls_base, tls_bytes, 0, 0) catch {
                result(s, -14);
                return select();
            };
            var tls_slots = tls_plan.rangeSlots(s.records());
            for (0..tls_plan.count) |offset| if (s.pages[if (service_workers) tls_slots.next().? else tls_plan.slot(s.records(), offset)].flags != 7 | nx) {
                result(s, -14);
                return select();
            };
            if (parent_tid > std.math.maxInt(usize) - 4 or byte(s, parent_tid, true) == null or byte(s, parent_tid + 3, true) == null) {
                result(s, -14);
                return select();
            }
        }
        for (s.children) |other| if (other.running) {
            if (@import("native_execution.zig").overlaps(r.rdx, stack_bytes, other.stack, other.stack_bytes) or
                @import("native_execution.zig").overlaps(r.rdx, stack_bytes, other.execution.tls_base, other.execution.tls_bytes) or
                @import("native_execution.zig").overlaps(tls_base, tls_bytes, other.stack, other.stack_bytes) or
                @import("native_execution.zig").overlaps(tls_base, tls_bytes, other.execution.tls_base, other.execution.tls_bytes))
            {
                result(s, -22);
                return select();
            }
        };
        const c = &s.children[available.?];
        c.* = .{};
        // The free candidate cannot alias the running creator. Under IF=0,
        // capture the actual creator mask before publishing its child.
        if (!@import("build_options").native_mask_skip_inherit) c.execution.signal_mask = s.context().signal_mask;
        c.execution.frame = .{ .rip = r.rsi, .rsp = rsp, .cs = 0x23, .ss = 0x1b, .flags = 0x202, .rdi = r.r8 };
        c.execution.fs = r.r10;
        c.execution.clear_tid = r.r9;
        c.execution.tls_base = tls_base;
        c.execution.tls_bytes = tls_bytes;
        std.mem.writeInt(u16, c.execution.fp[0..2], 0x037f, .little);
        std.mem.writeInt(u32, c.execution.fp[24..28], 0x1f80, .little);
        word(s, c.execution.frame.rsp, 0);
        const ordinal = if (@import("build_options").native_child_same_id) 0 else s.child_admissions;
        const tid = @import("native_execution.zig").childIdForProfile(ordinal, active, storage, @import("build_options").native_thread_reuse).?;
        c.id = tid;
        s.child_admissions += 1;
        var tid_bytes: [4]u8 = undefined;
        std.mem.writeInt(u32, &tid_bytes, tid, .little);
        for (tid_bytes, 0..) |v, i| byte(s, (if (storage) parent_tid else r.r9) + i, true).?.* = v;
        c.stack = r.rdx;
        c.stack_bytes = stack_bytes;
        c.used = true;
        c.running = true;
        result(s, tid);
    } else if (f.rdx != 0 or f.r10 != 0 or f.r8 != 0 or f.r9 != 0 or (f.rax == 0x28002 and f.rsi != 0) or (f.rax == 0x28001 and f.rsi > 255)) {
        result(s, -22);
    } else if (f.rax == 0x28001) {
        if (!s.on_child) {
            result(s, -13);
            return select();
        }
        clearTid(s, &s.child().execution);
        s.child().status = @intCast(f.rsi);
        s.child().running = false;
        s.on_child = false;
        rotate();
    } else {
        result(s, if (s.on_child) -13 else if (!s.children[0].used) -2 else if (s.children[0].running) 0 else @as(i64, s.children[0].status) + 1);
        s.context().frame.rdx = @intFromBool(s.children[0].execution.wait.address != 0);
    }
    return select();
}

// Private v1 boundary observations; no payload, pointer or authority is exposed.
// A completed write of one line observes only the named preceding operation.
fn nativeCleanupTrace(slot: usize, phase: u8) void {
    if (!@import("build_options").native_service_cleanup_trace) return;
    const s = &states[slot];
    var note: [160]u8 = undefined;
    serial.write(std.fmt.bufPrint(&note, "NATIVE CLEANUP v=1 slot={d} generation={d} phase={d} selected={d} pages={d} reclaimed={d}\n", .{ slot, s.generation, phase, active, s.payload().len, reclaimed }) catch unreachable);
}

fn finish(raw_status: u64, kind: u64) *const Frame {
    const status = if (launch_profile and kind == 1) raw_status & 0xff else raw_status;
    if (af09_enabled and af09BeforeExit(status, kind)) {
        rotate();
        return select();
    }
    if (supervised and active == supervisorSlot()) {
        if (init_profile) closeInit();
        @panic("native supervisor terminated");
    }
    const s = &states[active];
    var note: [100]u8 = undefined;
    serial.write(std.fmt.bufPrint(&note, "NATIVE terminal slot={d} generation={d} kind={d} detail={d}\n", .{ active, s.generation, kind, status }) catch "terminal\n");

    if (channel_profile) closeChannels(active);
    s.status = status;
    s.terminal_kind = kind;
    if (io_profile) {
        s.stream_closed = @splat(true);
        s.input.reader_closed = true;
    }
    s.terminal = true;
    s.revision += 1;
    if (af09_enabled) {
        if (active == 1 and af09.bound) {
            if (kind == 1) af09Row(7, 1, @bitCast(status), 0, 0) else af09Fail(1, -6);
        }
        if (active == 0 and kind == 1) af09Row(21, 0, @bitCast(status), 0, 0);
        af09.cancel(active, s.generation);
    }
    publishSustained();
    s.memory_cap = 0;
    s.entropy_grant.selector = 0;
    stopContexts(s);
    nativeCleanupTrace(active, 1);
    notifyParent(s);
    if (supervised) {
        const finished_slot = active;
        rotate();
        nativeCleanupTrace(finished_slot, 2);
        return select();
    }
    if (!states[1 - active].terminal) {
        rotate();
        return select();
    }
    var success = true;
    for (states[0..2], 0..) |*state, idx| {
        var b: [128]u8 = undefined;
        serial.write(std.fmt.bufPrint(&b, "NATIVE terminal task={d} status={d} output={d} fs={x} ticks={d}\n", .{ idx, state.status, state.output_count, state.context().fs, state.ticks }) catch "terminal\n");
        success = success and state.status == 0 and state.context().fs != 0 and state.yields == 64 and std.mem.eql(u8, state.output[0..state.output_count], "AETHER MUSL NATIVE PASS\n");
        state.root[0] = 0;
    }
    // Flush both user translations before zeroing and retaining terminal outcome.
    asm volatile ("mov %[v], %%cr3"
        :
        : [v] "r" (phys(&s.root)),
        : .{ .memory = true });
    for (states[0..2]) |*state| {
        // Make kernel-only backing aliases writable again after all user mappings are gone.
        for (0..state.count) |i| {
            setBackingAlias(s, state, i, true);
        }
    }
    asm volatile ("mov %[v], %%cr3"
        :
        : [v] "r" (phys(&s.root)),
        : .{ .memory = true });
    for (states[0..2]) |*state| {
        if (!@import("build_options").native_skip_zero) for (state.payload()) |*page| {
            @memset(page, 0);
        };
        for (state.payload()) |*page| for (page) |value| {
            if (value != 0) @panic("native backing not zeroed");
        };
        state.context().fs = 0;
    }
    msr(0xc0000100, 0);
    require(success);
    if (@import("build_options").native_threads) {
        var idle_note: [64]u8 = undefined;
        serial.write(std.fmt.bufPrint(&idle_note, "NATIVE WAIT idle ticks={d}\n", .{idle_ticks}) catch "idle\n");
    }
    serial.write("AETHER NATIVE C PASS\n");
    serial.halt();
}

fn parseStartup(bytes: []const u8) !elf.Image {
    const image = try elf.parseWithLimits(bytes, if (@import("build_options").native_image_large) elf.large_limits else .{});
    launch.layout(&image) catch @panic("invalid native layout");
    return image;
}

// Cached images and source metadata remain kernel-owned under IF=0. Reject
// capacity/table failures before reset, zeroing, alias edits or publication.
fn imagePreflight(s: *const State, image: *const elf.Image) bool {
    const count = launch.backingPages(image) catch return false;
    if (count > s.pages.len or count > s.backing.len) return false;
    launch.layout(image) catch return false;
    if (combined_application_profile and FsRoles.process(backingOwner(s))) {
        if (count > elf.application_limits.pages) return false;
        elf.applicationWindow(image) catch return false;
    }
    return true;
}
fn copyPreflight(source: *const State, child: *const State) bool {
    // The five application slots have equal private pools. No source can borrow
    // another role's metadata/backing, including the ungranted reservation tail.
    if (source.pages.len != child.pages.len or source.backing.len != source.pages.len or child.backing.len != child.pages.len or
        source.count > source.pages.len or source.pt_count > source.pts.len or source.pt_count > child.pts.len) return false;
    return true;
}
fn load(s: *State, bytes: []const u8, image: *const elf.Image, entropy: []const u8, instance: usize) void {
    require(imagePreflight(s, image));
    mapKernel(s);
    s.root[0] = phys(&s.pdpt) | 7;
    s.pdpt[0] = phys(&s.pd) | 7;
    // One bounded low-quarter PD; mappings outside this experiment are rejected.
    for (image.segments[0..image.count]) |segment| {
        require(segment.address + segment.memsz < 0x10000000);
        var a = segment.address & ~@as(usize, 4095);
        const end = (segment.address + segment.memsz + 4095) & ~@as(usize, 4095);
        const flags: u64 = if (segment.flags == 5) 5 else if (segment.flags == 6) 7 | nx else 5 | nx;
        while (a < end) : (a += 4096) addPage(s, a, flags);
        copy(s, segment.address, bytes[segment.offset..][0..segment.filesz]);
    }

    const stack_start: usize = 0x08000000; // Native experiment differs from host proposal.
    for (0..16) |i| addPage(s, stack_start + i * 4096, 7 | nx);
    const data = stack_start + 0xe000;
    copy(s, data, "native-probe\x00check\x00AETHER_PROBE=reference\x00");
    (byte(s, data + 11, true) orelse unreachable).* = @intCast('1' + instance);
    copy(s, data + 128, entropy[(if (combined_profile and instance != 0) instance - 1 else instance) * 16 ..][0..16]);
    const rsp = stack_start + 0xc000;
    if (@import("build_options").native_memory and !@import("build_options").native_memory_no_grant)
        s.memory_cap = 0x40000000 | (s.generation << 8) | (instance + 1);
    const words = [_]u64{ 2, data, data + 13, 0, data + 19, 0, 3, image.phdr, 4, 56, 5, image.phnum, 6, 4096, 9, image.entry, 11, 1000, 12, 1000, 13, 1000, 14, 1000, 23, 0, 25, data + 128, 31, data, 0, 0 };
    for (words, 0..) |v, i| word(s, rsp + i * 8, v);
    if (@import("build_options").native_memory) {
        word(s, rsp + (words.len - 2) * 8, 0xa000);
        word(s, rsp + (words.len - 1) * 8, s.memory_cap);
        word(s, rsp + words.len * 8, 0);
        word(s, rsp + (words.len + 1) * 8, 0);
    }
    if (threadedSlot(instance)) {
        s.thread_cap = 0x50000000 | (s.generation << 8) | (instance + 1);
        word(s, rsp + words.len * 8, 0xa001);
        word(s, rsp + (words.len + 1) * 8, s.thread_cap);
        word(s, rsp + (words.len + 2) * 8, 0);
        word(s, rsp + (words.len + 3) * 8, 0);
    }
    if (@import("build_options").native_entropy and (!combined_profile or instance == FsRoles.engine_slot)) {
        s.entropy_grant = .{ .selector = 0x60000000 | (s.generation << 8) | (instance + 1) };
        word(s, rsp + (words.len + 2) * 8, 0xa002);
        word(s, rsp + (words.len + 3) * 8, s.entropy_grant.selector);
        word(s, rsp + (words.len + 4) * 8, 0);
        word(s, rsp + (words.len + 5) * 8, 0);
    }
    if (@import("build_options").native_service_channel and (!combined_profile or instance == FsRoles.engine_slot)) {
        word(s, rsp + (words.len + 4) * 8, 0xa004);
        word(s, rsp + (words.len + 5) * 8, s.channel_cap);
        word(s, rsp + (words.len + 6) * 8, 0xa005);
        word(s, rsp + (words.len + 7) * 8, s.channel_reply_cap);
        word(s, rsp + (words.len + 8) * 8, 0);
        word(s, rsp + (words.len + 9) * 8, 0);
    }
    // Finalize RELRO and remove writable kernel aliases of immutable user pages.
    const phoff = std.mem.readInt(u64, bytes[32..40], .little);
    for (0..image.phnum) |i| {
        const h = bytes[@intCast(phoff + i * 56)..][0..56];
        if (std.mem.readInt(u32, h[0..4], .little) != 0x6474e552) continue;
        const addr = std.mem.readInt(u64, h[16..24], .little);
        const len = std.mem.readInt(u64, h[40..48], .little);
        for (s.pages[0..s.count]) |*page| if (page.address >= addr & ~@as(u64, 4095) and page.address < addr + len) {
            page.flags = 5 | nx;
        };
    }
    for (s.pages[0..s.count], 0..) |page, i| {
        const d = page.address / (2 * 1024 * 1024);
        for (s.pt_index[0..s.pt_count], 0..) |idx, t| if (idx == d) {
            s.pts[t][page.address / 4096 % 512] = backingFrame(s, i) | page.flags;
        };
        if (page.address != 0 and page.flags & 2 == 0) {
            setBackingAlias(s, s, i, false);
            if (external_backing and backingAliasEntry(s, s, i) & 2 != 0) @panic("native backing immutable alias writable");
        }
    }
    s.context().frame = .{ .rip = image.entry, .rsp = rsp, .cs = 0x23, .ss = 0x1b, .flags = 0x202 };
    std.mem.writeInt(u16, s.context().fp[0..2], 0x037f, .little);
    std.mem.writeInt(u32, s.context().fp[24..28], 0x1f80, .little);
    s.admitted = true;
    if (@import("build_options").native_memory) {
        var budget: [120]u8 = undefined;
        const used = arena.used(s.records());
        serial.write(std.fmt.bufPrint(&budget, "NATIVE MEMORY admitted slot={d} generation={d} used={d} remaining={d}\n", .{ instance, s.generation, used, s.pages.len - used }) catch "native memory budget\n");
    }
}

fn rotate() void {
    if (af09_enabled) af09Refresh();
    refreshSustained();
    refreshChannelWaits();
    idle = false;
    const limit: usize = if (supervised) supervisorSlot() + 1 else 2;
    var waiting: ?usize = null;
    for (1..limit + 1) |offset| {
        const candidate = (active + offset) % limit;
        const next = &states[candidate];
        if (!next.admitted or next.terminal or next.frozen) continue;
        if (session_lifecycle and next.channel_wait.endpoint != 0) {
            waiting = candidate;
            continue;
        }
        if (ownerEventsEnabled() and candidate == supervisorSlot() and sustained_events.parked()) {
            waiting = candidate;
            continue;
        }
        if (@import("build_options").native_signal_suspend) {
            resumeSuspended(next);
            if (next.suspend_mask != null) {
                waiting = candidate;
                continue;
            }
        }
        if (@import("native_execution.zig").nextContext(next.childRecords(), if (next.on_child) next.selected_child + 1 else 0, next.execution.wait.address != 0 or storagePrimaryWaiting(next) or (af09_enabled and af09Blocked(candidate)))) |selected| {
            active = candidate;
            next.on_child = selected != 0;
            if (selected != 0) next.selected_child = selected - 1;
            return;
        }
        if (storagePrimaryWaiting(next) or (af09_enabled and af09Blocked(candidate))) waiting = candidate;
        const contexts = next.contexts();
        for (contextView(&contexts)) |context| if (context.wait.address != 0) {
            waiting = candidate;
        };
    }
    if (waiting) |owner| {
        active = owner;
        idle = true;
        return;
    }
    @panic("no native runnable owner");
}

fn aliases(owner: *State, writable: bool) void {
    for (&states) |*mapping| {
        for (owner.pages[0..owner.count], 0..) |page, i| {
            if (page.address == 0) continue;
            setBackingAlias(mapping, owner, i, writable or page.flags & 2 != 0);
        }
    }
    asm volatile ("mov %[v], %%cr3"
        :
        : [v] "r" (phys(&states[active].root)),
        : .{ .memory = true });
}
fn supervisedEnvelopeValid(envelope: []const u8) bool {
    if (envelope.len < 48) return false;
    const len = std.mem.readInt(u32, envelope[8..12], .little);
    const supervisor_len = std.mem.readInt(u32, envelope[12..16], .little);
    const limit: usize = if (@import("build_options").native_service_activation) 8192 else 4096;
    return len > 0 and len <= service_bytes.len and supervisor_len > 0 and supervisor_len <= limit and envelope.len == 48 + @as(usize, len) + supervisor_len;
}
fn mapOwnerStack(s: *State) void {
    const pages: usize = if (combined_owner_stack) 2 else 1;
    for (0..pages) |i| {
        if (combined_owner_stack) {
            require(combined_owner_data and s == &states[supervisorSlot()] and s.count < s.backing.len);
            @memset(&s.backing[s.count], 0);
        }
        addPage(s, 0x800000 + i * 4096, 7 | nx);
    }
}
fn mapOwnerData(s: *State) void {
    require(combined_profile and combined_init and combined_owner_data and s == &states[supervisorSlot()]);
    for (0..FsRoles.owner_data_bytes / 4096) |i| {
        require(s.count < s.backing.len);
        @memset(&s.backing[s.count], 0);
        addPage(s, FsRoles.owner_data_base + i * 4096, 7 | nx);
    }
}
fn ownerDataStartup(frame: *Frame) void {
    if (!combined_owner_data) return;
    require(combined_profile and combined_init and frame.rdi == 29);
    frame.rdi = if (combined_owner_stack) 31 else 30;
    if (combined_owner_stack) frame.rsp = 0x802000 - 8;
    frame.r10 = FsRoles.owner_data_base;
    frame.r11 = FsRoles.owner_data_bytes;
}
fn auditOwnerStack(s: *State, code_pages: usize) void {
    if (!combined_owner_stack) return;
    require(s == &states[supervisorSlot()] and s.count == code_pages + 4);
    for (0..2) |i| {
        const page = s.pages[code_pages + i];
        require(page.address == 0x800000 + i * 4096 and page.flags == 7 | nx);
        for (s.backing[code_pages + i]) |value| require(value == 0);
    }
    // byte() checks actual mapping membership; no extra authority or mapping.
    require(byte(s, 0x7ff000, false) == null and byte(s, 0x802000, false) == null);
    require(s.context().frame.rdi == 31 and s.context().frame.rsp == 0x802000 - 8);
}
fn startSupervised(envelope: []const u8) noreturn {
    require(envelope.len >= 48);
    var supervisor_code: []const u8 = undefined;
    if (combined_profile) {
        const bundle = (if (combined_application_profile) FsSession.parseApplication(envelope) else if (combined_owner_stack) FsSession.parseOwnerStack(envelope) else if (combined_owner_data) FsSession.parseOwnerData(envelope) else FsSession.parseProfile(envelope, combined_init)) catch @panic("invalid filesystem SESSION envelope");
        engine_len = bundle.engine.len;
        @memcpy(engine_bytes[0..engine_len], bundle.engine);
        engine_image = parseStartup(engine_bytes[0..engine_len]) catch @panic("invalid filesystem engine ELF");
        @memcpy(&engine_entropy, bundle.engine_entropy);
        service_len = bundle.session.images[0].len;
        second_len = bundle.session.images[1].len;
        third_len = bundle.session.images[2].len;
        @memcpy(service_bytes[0..service_len], bundle.session.images[0]);
        @memcpy(second_bytes[0..second_len], bundle.session.images[1]);
        @memcpy(third_bytes[0..third_len], bundle.session.images[2]);
        service_image = (if (combined_application_profile) elf.parseApplication(service_bytes[0..service_len]) else elf.parse(service_bytes[0..service_len])) catch unreachable;
        second_image = (if (combined_application_profile) elf.parseApplication(second_bytes[0..second_len]) else elf.parse(second_bytes[0..second_len])) catch unreachable;
        third_image = (if (combined_application_profile) elf.parseApplication(third_bytes[0..third_len]) else elf.parse(third_bytes[0..third_len])) catch unreachable;
        @memcpy(bootstrap[0..bundle.session.entropy.len], bundle.session.entropy);
        supervisor_code = bundle.session.supervisor;
    } else if (launch_profile) {
        const bundle = (if (pipeline_capacity) launch.pipelineBundle(envelope) else launch.bundle(envelope)) catch @panic("invalid launch envelope");
        service_len = bundle.images[0].len;
        second_len = bundle.images[1].len;
        @memcpy(service_bytes[0..service_len], bundle.images[0]);
        @memcpy(second_bytes[0..second_len], bundle.images[1]);
        service_image = elf.parse(service_bytes[0..service_len]) catch @panic("invalid launch ELF");
        second_image = elf.parse(second_bytes[0..second_len]) catch @panic("invalid launch ELF");
        launch.layout(&service_image) catch @panic("invalid launch layout");
        launch.layout(&second_image) catch @panic("invalid launch layout");
        if (program_profile) {
            third_len = bundle.images[2].len;
            @memcpy(third_bytes[0..third_len], bundle.images[2]);
            third_image = elf.parse(third_bytes[0..third_len]) catch @panic("invalid launch ELF");
            launch.layout(&third_image) catch @panic("invalid launch layout");
        }
        @memcpy(bootstrap[0..bundle.entropy.len], bundle.entropy);
        supervisor_code = bundle.supervisor;
    } else {
        const len = std.mem.readInt(u32, envelope[8..12], .little);
        require(supervisedEnvelopeValid(envelope));
        service_len = len;
        @memcpy(service_bytes[0..len], envelope[48..][0..len]);
        service_image = parseStartup(service_bytes[0..len]) catch @panic("invalid supervised ELF");
        @memcpy(bootstrap[0..32], envelope[16..48]);
        supervisor_code = envelope[48 + @as(usize, len) ..];
    }
    for (&states) |*state| mapKernel(state);
    const s = &states[supervisorSlot()];
    s.root[0] = phys(&s.pdpt) | 7;
    s.pdpt[0] = phys(&s.pd) | 7;
    for (0..(supervisor_code.len + 4095) / 4096) |i| addPage(s, 0x400000 + i * 4096, 5);
    mapOwnerStack(s);
    if (combined_owner_data) mapOwnerData(s);
    copy(s, 0x400000, supervisor_code);
    if (init_large and @import("build_options").native_init_large_dirty_tail and supervisor_code.len % 4096 != 0) s.backing[supervisor_code.len / 4096][supervisor_code.len % 4096] = 0xa5;
    s.context().frame = .{ .rip = 0x400000, .rsp = 0x801000 - 8, .cs = 0x23, .ss = 0x1b, .flags = 0x202, .rdi = if (combined_profile) (if (combined_init) 29 else 28) else if (storageLifetime()) 27 else if (@import("build_options").native_service_channel_wait) 26 else if (@import("build_options").native_service_channel) 25 else if (session_lifecycle) 24 else if (sustained) 22 else if (pipeline_session and pipeline_console) 23 else if (pipeline_session) 21 else if (pipeline_console) 20 else if (pipeline_capacity) 19 else if (connections_console) 18 else if (connections_large) 17 else if (init_composed) 16 else if (init_large) 15 else if (block_regions) 14 else if (block_profile) 13 else if (console_relay) 12 else if (console_handoff) 11 else if (console_profile) 10 else if (connections_profile) 9 else if (program_profile) 8 else if (coexist_profile) 7 else if (init_profile) 6 else if (file_profile) 5 else if (channel_profile) 4 else if (launch_profile) 3 else if (io_profile) 2 else 1, .rsi = 0xa001, .rdx = if (block_profile) 0xf101 else if (console_profile and !console_relay and !connections_console and !pipeline_console) 0xf001 else if (launch_profile) 0xc001 else 0, .rcx = if (launch_profile) 0xc002 else 0, .r8 = if (channel_profile) 0xd001 else 0, .r9 = if (storageLifetime()) 0xe002 else if (program_profile) 0xc003 else if (init_profile) 0xe001 else 0 };
    ownerDataStartup(&s.context().frame);
    auditOwnerStack(s, (supervisor_code.len + 4095) / 4096);
    std.mem.writeInt(u16, s.context().fp[0..2], 0x037f, .little);
    std.mem.writeInt(u32, s.context().fp[24..28], 0x1f80, .little);
    s.admitted = true;
    active = supervisorSlot();
    // Do not switch CR3 on the bootloader stack. Finalize aliases without a reload.
    for (&states) |*mapping| for (s.pages[0..s.count], 0..) |page, i| {
        if (page.flags & 2 != 0) continue;
        setBackingAlias(mapping, s, i, false);
        if (external_backing and backingAliasEntry(mapping, s, i) & 2 != 0) @panic("native backing immutable alias writable");
    };
    if (init_large or connections_large or @import("build_options").native_service_activation) {
        const code_pages = (supervisor_code.len + 4095) / 4096;
        for (s.pages[0..code_pages], 0..) |page, i| {
            require(page.address == 0x400000 + i * 4096 and page.flags == 5);
            for (&states) |*mapping| require(backingAliasEntry(mapping, s, i) == backingFrame(s, i) | 1 | nx);
        }
        require(s.pages[code_pages].address == 0x800000 and s.pages[code_pages].flags == 7 | nx);
        for (supervisor_code.len..code_pages * 4096) |i| if (s.backing[i / 4096][i % 4096] != 0) {
            @panic("native init code tail not zeroed");
        };
    }
    if (init_large) {
        const code_pages = (supervisor_code.len + 4095) / 4096;
        var note: [100]u8 = undefined;
        serial.write(std.fmt.bufPrint(&note, "NATIVE INIT {s} bytes={d} pages={d} mappings=verified\n", .{ if (init_composed) @as([]const u8, "COMPOSED") else "LARGE", supervisor_code.len, code_pages }) catch "init mapping check\n");
    }
    nativeBackingViews();
    serial.write("NATIVE SUPERVISION: sys-init owns launch/retry policy; bounded local grants\n");
    @import("protection.zig").timerStart();
    msr(0xc0000100, 0);
    asm volatile ("fxrstor64 (%[p])"
        :
        : [p] "r" (&s.context().fp),
        : .{ .memory = true });
    restore_context(phys(&s.root), &s.context().frame);
}
fn handle(slot: usize) u64 {
    if (sustained) return Sustained.identity(.instance, @intCast(slot), @intCast(states[slot].generation)) catch unreachable;
    return 0xb0000000 | (states[slot].generation << 8) | (slot + 1);
}
fn lookup(value: u64) ?usize {
    for (0..workerCount()) |slot| if (states[slot].admitted and value == handle(slot)) return slot;
    return null;
}
fn control(frame: *const Frame) *const Frame {
    const caller = &states[active];
    if (frame.rax == 0x20004 or frame.rax == 0x20005) {
        if (active == supervisorSlot()) {
            result(caller, -13);
        } else if (frame.rax == 0x20004) {
            const first_ready = !caller.ready;
            if (!caller.ready) {
                caller.revision += 1;
                publishSustained();
            }
            caller.ready = true;
            result(caller, 0);
            if (af09_enabled) af09Ready(first_ready);
        } else result(caller, @intCast(caller.generation));
        return select();
    }
    if (active != supervisorSlot()) {
        result(caller, -13);
        return select();
    }
    if (frame.rax == 0x20006) {
        if (lifecycleEnabled()) {
            result(caller, -38);
            return select();
        }
        var b: [100]u8 = undefined;
        if (worker_clock) {
            var clock_note: [160]u8 = undefined;
            serial.write(std.fmt.bufPrint(&clock_note, "NATIVE CLOCK workers scans={d} max_contexts={d} max_ns={d} valid={d}\n", .{ clock_scan_ticks, clock_scan_max_contexts, clock_scan_max_ns, @intFromBool(clock_scan_valid) }) catch unreachable);
        }
        serial.write(std.fmt.bufPrint(&b, "NATIVE supervisor result={d} reclaimed={d}\n", .{ frame.rdi, reclaimed }) catch "supervisor result\n");
        require(!@import("build_options").native_runner_local or connections_profile);
        if (@import("build_options").native_exec_denial) require(connections_profile and states[0].generation == 1 and states[1].generation == 1 and states[2].generation == 2);
        require(frame.rdi == 100);
        if (pipeline_session) {
            require(@import("../../native_session_observation.zig").finished(session_observations, session_report_reclaimed, reclaimed));
        } else require(reclaimed == (if (pipeline_capacity) @as(usize, 15) else if (@import("build_options").native_exec_denial) @as(usize, 4) else if (@import("build_options").native_process_copy) @as(usize, 6) else if (@import("build_options").native_runner_local) (if (@import("build_options").native_runner_files) @as(usize, 6) else 4) else if (connections_profile) @as(usize, 6) else if (program_profile) @as(usize, 5) else if (io_profile) @as(usize, 2) else 3));
        for (states[0..workerCount()]) |*worker| require(!worker.admitted);
        if (channel_profile) for (channels[0..channelCount()]) |*c| {
            require(c.owners[0] == null and c.owners[1] == null);
            for (c.stream.bytes) |value| require(value == 0);
        };
        serial.write(if (block_profile) "AETHER NATIVE BLOCK PASS\n" else if (console_profile) "AETHER NATIVE CONSOLE PASS\n" else if (connections_profile) "AETHER NATIVE CONNECTIONS PASS\n" else if (program_profile) "AETHER NATIVE PROGRAM PASS\n" else if (coexist_profile) "AETHER NATIVE COEXIST PASS\n" else if (init_composed) "AETHER NATIVE INIT COMPOSED PASS\n" else if (init_large) "AETHER NATIVE INIT LARGE PASS\n" else if (init_profile) "AETHER NATIVE INIT PASS\n" else if (file_profile) "AETHER NATIVE FILE SERVICE PASS\n" else if (channel_profile) "AETHER NATIVE CHANNEL PASS\n" else if (launch_profile) "AETHER NATIVE LAUNCH PASS\n" else if (io_profile) "AETHER NATIVE IO PASS\n" else "AETHER NATIVE SUPERVISION PASS\n");
        serial.halt();
    }
    if (frame.rax == 0x20000 or (@import("build_options").native_service_channel and frame.rax == 0x20008)) {
        if (@import("build_options").native_service_channel and frame.rax == 0x20000) {
            result(caller, -38);
            return select();
        }
        if (launch_profile and !combined_profile) {
            result(caller, -38);
            return select();
        }
        if (frame.rdi != 0xa001) {
            result(caller, -13);
            return select();
        }
        if (frame.rsi >= workerCount()) {
            result(caller, -22);
            return select();
        }
        const slot: usize = @intCast(frame.rsi);
        if (combined_profile and slot != FsRoles.engine_slot) {
            result(caller, -13);
            return select();
        }
        const s = &states[slot];
        if (s.admitted) {
            result(caller, -16);
            return select();
        }
        if (s.generation >= (if (combined_profile) @as(u64, 3) else lifetimeLimit())) {
            result(caller, -28);
            return select();
        }
        if (service_memory and !@import("build_options").native_service_skip_image_budget and (launch.backingPages(if (combined_profile) &engine_image else &service_image) catch unreachable) > s.pages.len) {
            result(caller, -12);
            return select();
        }
        if (@import("build_options").native_service_channel) {
            if (frame.r8 | frame.r9 != 0) {
                result(caller, -22);
                return select();
            }
            if (@import("../../native_channel.zig").connectionPair(channels[(if (combined_profile) FsRoles.process_channels else 0)..channelCount()], active, frame.rdx, frame.r10) == null) {
                result(caller, -13);
                return select();
            }
        }
        const generation = s.generation + 1;
        // Prior reclamation removed mappings, flushed aliases and zeroed all backing.
        resetState(s);
        s.generation = generation;
        if (@import("build_options").native_service_channel) {
            // IF=0 and no fallible operation remains. Publish the worker only
            // after both retained endpoint bindings and its auxv are complete.
            const pair = @import("../../native_channel.zig").connectionPair(channels[(if (combined_profile) FsRoles.process_channels else 0)..channelCount()], active, frame.rdx, frame.r10).?;
            require(pair.request.transfer(active, frame.rdx, slot));
            require(pair.reply.transfer(active, frame.r10, slot));
            s.channel_cap = frame.rdx;
            s.channel_reply_cap = frame.r10;
        }
        load(s, if (combined_profile) engine_bytes[0..engine_len] else service_bytes[0..service_len], if (combined_profile) &engine_image else &service_image, if (combined_profile) &engine_entropy else &bootstrap, slot);
        // New mappings must also protect every other immutable domain's aliases.
        for (&states) |*owner| aliases(owner, false);
        result(caller, @intCast(handle(slot)));
        if (af09_enabled and slot == 0) af09EngineAdmitted();
        return select();
    }
    const slot = lookup(frame.rdi) orelse {
        result(caller, -9);
        return select();
    };
    const s = &states[slot];
    switch (frame.rax) {
        0x20001 => {
            if (af09_enabled and af09Query(slot)) {
                rotate();
                return select();
            }
            ordinaryQuery(caller, s);
        },
        0x20002 => {
            if (!s.terminal) {
                result(caller, -16);
                return select();
            }
            nativeCleanupTrace(slot, 3);
            s.root[0] = 0;
            aliases(s, true); // Current CR3 reload also flushes the detached local domain.
            nativeCleanupTrace(slot, 4);
            if (!@import("build_options").native_skip_zero) for (s.payload()) |*page| {
                @memset(page, 0);
            };
            nativeCleanupTrace(slot, 5);
            // Page alignment/geometry permit a complete word scan with no tail.
            for (s.payload()) |*page| require(std.mem.allEqual(u64, std.mem.bytesAsSlice(u64, page), 0));
            nativeCleanupTrace(slot, 6);
            s.admitted = false;
            // Retired image metadata must not re-protect zeroed backing when a
            // different slot loads before this slot is reused.
            s.count = 0;
            @memset(s.records(), .{});
            if (@import("build_options").native_signal_actions) s.signal_actions.reset();
            s.execution.reset();
            for (s.childRecords()) |*c| c.reset();
            reclaimed += 1;
            publishSustained();
            nativeCleanupTrace(slot, 7);
            result(caller, 0);
            if (af09_enabled) {
                af09Row(15, slot, 0, 0, 0);
                af09.cancel(slot, s.generation);
            }
        },
        0x20003 => {
            result(caller, if (frame.rsi < s.output_count) s.output[@intCast(frame.rsi)] else -11);
        },
        0x20007 => {
            if (!s.terminal) {
                if (channel_profile) closeChannels(slot);
                s.terminal = true;
                s.revision += 1;
                publishSustained();
                s.memory_cap = 0;
                s.entropy_grant.selector = 0;
                s.status = 143;
                s.terminal_kind = 3;
                if (pipeline_session) {
                    var note: [100]u8 = undefined;
                    serial.write(std.fmt.bufPrint(&note, "NATIVE terminal slot={d} generation={d} kind=3 detail=143\n", .{ slot, s.generation }) catch unreachable);
                }
                if (io_profile) {
                    s.stream_closed = @splat(true);
                    s.input.reader_closed = true;
                }
                stopContexts(s);
                notifyParent(s);
            }
            result(caller, 0);
            if (af09_enabled) {
                af09Row(14, slot, 0, 0, 0);
                af09.cancel(slot, s.generation);
            }
        },
        else => result(caller, -38),
    }
    return select();
}

fn entropyError(s: *State, err: @import("../../native_entropy.zig").Failure) void {
    result(s, switch (err) {
        error.Denied => -13,
        error.Closed => -9,
        error.Invalid => -22,
        error.Exhausted => -28,
    });
}
// IF stays clear through full preflight, DMA, copying and volatile clearing.
fn entropyOperation(f: *const Frame) *const Frame {
    const s = &states[active];
    if (!s.admitted or s.terminal or (supervised and active == supervisorSlot())) {
        result(s, -13);
        return select();
    }
    s.entropy_grant.check(f.rdi) catch |err| {
        entropyError(s, err);
        return select();
    };
    const closing = f.rax == 0x2b001;
    if (f.r10 | f.r8 | f.r9 != 0 or (closing and f.rsi | f.rdx != 0)) {
        result(s, -22);
    } else if (closing) {
        s.entropy_grant.close(f.rdi) catch unreachable;
        result(s, 0);
    } else if (f.rdx == 0 or f.rdx > 256) {
        result(s, -22);
    } else if (f.rsi > std.math.maxInt(u64) - f.rdx) {
        result(s, -14);
    } else {
        const count: usize = @intCast(f.rdx);
        for (0..count) |i| if (byte(s, @intCast(f.rsi + i), true) == null) {
            result(s, -14);
            return select();
        };
        s.entropy_grant.prepare(f.rdi, count) catch |err| {
            entropyError(s, err);
            return select();
        };
        var buffer: [256]u8 = undefined;
        @import("entropy.zig").draw(buffer[0..count]);
        for (buffer[0..count], 0..) |value, i| byte(s, @intCast(f.rsi + i), true).?.* = value;
        @import("entropy.zig").clear(buffer[0..count]);
        if (!@import("build_options").native_entropy_skip_quota) s.entropy_grant.complete(count);
        result(s, @intCast(count));
    }
    return select();
}

// BSP-only copied block transport. IF stays clear through validation and DMA
// completion; user mappings cannot change between validation and copying.
fn blockOperation(f: *const Frame) *const Frame {
    const s = &states[active];
    const owns = if (block_recipient) |owner|
        active == owner.slot and s.admitted and !s.terminal and s.generation == owner.generation
    else
        active == supervisorSlot();
    if (!owns or f.rdi != 0xf101) {
        result(s, -13);
    } else if (block_closed) {
        result(s, -9);
    } else if (f.rax == 0x27006) {
        if (f.rdx != 32 or f.r10 != 0) {
            result(s, -22);
        } else if (f.rsi > std.math.maxInt(u64) - 32) {
            result(s, -14);
        } else {
            for (0..32) |i| if (byte(s, @intCast(f.rsi + i), true) == null) {
                result(s, -14);
                return select();
            };
            var info: [32]u8 = @splat(0);
            std.mem.writeInt(u64, info[0..8], 512, .little);
            std.mem.writeInt(u64, info[8..16], block_count, .little);
            std.mem.writeInt(u64, info[16..24], block_rights, .little);
            for (info, 0..) |value, i| byte(s, @intCast(f.rsi + i), true).?.* = value;
            result(s, 0);
        }
    } else if (f.rax == 0x27005) {
        if (active != supervisorSlot()) {
            result(s, -13);
        } else if (f.r10 != 24) {
            result(s, -22);
        } else if (f.rdx > std.math.maxInt(u64) - 24) {
            result(s, -14);
        } else {
            var record: [24]u8 = undefined;
            for (&record, 0..) |*value, i| {
                const p = byte(s, @intCast(f.rdx + i), false) orelse {
                    result(s, -14);
                    return select();
                };
                value.* = p.*;
            }
            const region_start = std.mem.readInt(u64, record[0..8], .little);
            const count = std.mem.readInt(u64, record[8..16], .little);
            const rights = std.mem.readInt(u64, record[16..24], .little);
            if (count == 0 or region_start >= block_count or count > block_count - region_start or rights == 0 or rights & ~block_rights != 0) {
                result(s, -22);
            } else if (lookup(f.rsi)) |slot| {
                if (combined_profile and slot != FsRoles.engine_slot) {
                    result(s, -13);
                } else if (states[slot].terminal) {
                    result(s, -9);
                } else {
                    block_base += region_start;
                    block_count = count;
                    block_rights = rights;
                    block_recipient = .{ .slot = slot, .generation = states[slot].generation };
                    result(s, 0);
                }
            } else result(s, -9);
        }
    } else if (f.rax == 0x27003) {
        if (active != supervisorSlot()) {
            result(s, -13);
        } else if (f.rdx == 0 or f.rdx & ~block_rights != 0 or f.r10 != 0) {
            result(s, -22);
        } else if (lookup(f.rsi)) |slot| {
            if (combined_profile and slot != FsRoles.engine_slot) {
                result(s, -13);
            } else if (states[slot].terminal) {
                result(s, -9);
            } else {
                block_recipient = .{ .slot = slot, .generation = states[slot].generation };
                block_rights = f.rdx;
                result(s, 0);
            }
        } else result(s, -9);
    } else if (f.rax == 0x27004) {
        if (f.rsi != 0 or f.rdx != 0 or f.r10 != 0) {
            result(s, -22);
        } else {
            block_closed = true;
            result(s, 0);
        }
    } else {
        const right: u64 = if (f.rax == 0x27000) 1 else if (f.rax == 0x27001) 2 else 4;
        if (block_rights & right == 0) {
            result(s, -13);
        } else if (f.rax == 0x27002) {
            if (f.rsi != 0 or f.rdx != 0 or f.r10 != 0) {
                result(s, -22);
            } else {
                @import("block.zig").flush();
                result(s, 0);
            }
        } else if (f.rsi >= block_count or f.r10 != 512) {
            result(s, -22);
        } else if (f.rdx > std.math.maxInt(u64) - 512) {
            result(s, -14);
        } else {
            const reading = f.rax == 0x27000;
            // IF stays clear: validation, copying and synchronous completion cannot
            // overlap a user unmap, stop or task replacement on this BSP profile.
            // A sector spans at most two pages. Validate both before effects;
            // IF=0 pins each owner-local backing borrow until this call returns.
            var fragments: [2][]u8 = undefined;
            var fragment_count: usize = 0;
            var offset: usize = 0;
            while (offset < 512) {
                const address: usize = @intCast(f.rdx + offset);
                const first = byte(s, address, reading) orelse {
                    result(s, -14);
                    return select();
                };
                const count = @min(512 - offset, 4096 - address % 4096);
                const pointer: [*]u8 = @ptrCast(first);
                fragments[fragment_count] = pointer[0..count];
                fragment_count += 1;
                offset += count;
            }
            var buffer: [512]u8 = undefined;
            if (reading) @import("block.zig").readSector(block_base + f.rsi, &buffer) catch unreachable;
            offset = 0;
            for (fragments[0..fragment_count]) |fragment| {
                if (reading) @memcpy(fragment, buffer[offset..][0..fragment.len]) else @memcpy(buffer[offset..][0..fragment.len], fragment);
                offset += fragment.len;
            }
            if (!reading) @import("block.zig").writeSector(block_base + f.rsi, &buffer) catch unreachable;
            result(s, 512);
        }
    }
    return select();
}

fn consoleOperation(f: *const Frame) *const Frame {
    const s = &states[active];
    const owns = if (console_recipient) |owner|
        active == owner.slot and s.admitted and !s.terminal and s.generation == owner.generation
    else
        active == supervisorSlot();
    if (lifecycleEnabled() and (f.r10 != 0 or f.r8 != 0 or f.r9 != 0 or (f.rax == 0x26002 and (f.rsi != 0 or f.rdx != 0)))) {
        result(s, -22);
    } else if (!owns or f.rdi != 0xf001) {
        result(s, -13);
    } else if (console_closed) {
        result(s, -9);
    } else if (f.rax == 0x26003) {
        if (lifecycleEnabled() or active != supervisorSlot()) {
            result(s, -13);
        } else if (f.rdx != 0) {
            result(s, -22);
        } else if (lookup(f.rsi)) |slot| {
            if (states[slot].terminal) {
                result(s, -9);
            } else {
                console_recipient = .{ .slot = slot, .generation = states[slot].generation };
                result(s, 0);
            }
        } else {
            result(s, -9);
        }
    } else if (f.rax == 0x26002) {
        console_closed = true;
        result(s, 0);
    } else if (f.rdx > 256 or f.rsi > std.math.maxInt(u64) - f.rdx) {
        result(s, -14);
    } else {
        const reading = f.rax == 0x26000;
        const count: usize = @intCast(@min(f.rdx, 16));
        for (0..count) |i| if (byte(s, @intCast(f.rsi + i), reading) == null) {
            result(s, -14);
            return select();
        };
        var used: usize = 0;
        var failure: i64 = -11;
        while (used < count) : (used += 1) {
            const p = byte(s, @intCast(f.rsi + used), reading).?;
            if (reading) {
                const value = serial.readByte() catch {
                    failure = -5;
                    break;
                };
                p.* = value orelse break;
            } else if (!serial.writeByte(p.*)) break;
        }
        result(s, if (used > 0 or count == 0) @intCast(used) else failure);
    }
    return select();
}

fn streamOperation(f: *const Frame) *const Frame {
    const s = &states[active];
    if (active == supervisorSlot() or f.rdi > 2) {
        result(s, -13);
        return select();
    }
    const id: usize = @intCast(f.rdi);
    if (s.stream_closed[id]) {
        result(s, -9);
        return select();
    }
    if (f.rax == 0x21002) {
        s.stream_closed[id] = true;
        if (id == 0) s.input.reader_closed = true;
        result(s, 0);
        return select();
    }
    const reading = f.rax == 0x21000;
    if ((reading and id != 0) or (!reading and id == 0)) {
        result(s, -9);
        return select();
    }
    if (!reading and @import("build_options").native_no_output) {
        result(s, -13);
        return select();
    }
    if (f.rdx > 256 or f.rsi > std.math.maxInt(u64) - f.rdx) {
        result(s, -14);
        return select();
    }
    const count: usize = @intCast(@min(f.rdx, if (reading) @as(u64, 4) else 16));
    for (0..count) |i| if (byte(s, @intCast(f.rsi + i), reading) == null) {
        result(s, -14);
        return select();
    };
    if (count == 0) {
        result(s, 0);
        return select();
    }
    if (reading) {
        if (s.input.count == 0) {
            result(s, if (s.input.sealed) 0 else -11);
            return select();
        }
        const amount = @min(count, s.input.count);
        for (0..amount) |i| byte(s, @intCast(f.rsi + i), true).?.* = @intCast(s.input.pop());
        result(s, @intCast(amount));
    } else {
        const buffer = if (id == 1) &s.output else &s.errors;
        const used = if (id == 1) &s.output_count else &s.errors_count;
        if (count > buffer.len - used.*) {
            result(s, -11);
            return select();
        }
        for (0..count) |i| buffer[used.* + i] = byte(s, @intCast(f.rsi + i), false).?.*;
        used.* += count;
        result(s, @intCast(count));
    }
    return select();
}
fn streamControl(f: *const Frame) *const Frame {
    const caller = &states[active];
    if (active != supervisorSlot()) {
        result(caller, -13);
        return select();
    }
    const slot = lookup(f.rdi) orelse {
        result(caller, -9);
        return select();
    };
    const s = &states[slot];
    if (f.rax == 0x20008) {
        if (f.rsi > 256) result(caller, -22) else if (s.input.reader_closed or s.terminal) result(caller, -32) else if (f.rsi == 256) {
            s.input.sealed = true;
            result(caller, 0);
        } else result(caller, s.input.push(@intCast(f.rsi)));
    } else {
        const id = f.rsi >> 32;
        const offset: usize = @intCast(f.rsi & 0xffffffff);
        if (id != 1 and id != 2) {
            result(caller, -22);
            return select();
        }
        const buffer = if (id == 1) &s.output else &s.errors;
        const used = if (id == 1) s.output_count else s.errors_count;
        result(caller, if (offset < used) buffer[offset] else if (s.stream_closed[@intCast(id)]) 256 else -11);
    }
    return select();
}

// The interrupt gate keeps IF clear; this BSP-only transaction cannot be
// preempted by a user task, supervisor stop, or timer. Nothing is published
// until the full plan is validated. No fallible operation follows PTE commit.
fn memoryError(s: *State, err: memory.Error) *const Frame {
    result(s, switch (err) {
        error.Invalid => -22,
        error.Denied => -13,
        error.Exhausted => -12,
    });
    return select();
}
fn memoryAlias(s: *State, index: usize, writable: bool) void {
    for (&states) |*mapping| setBackingAlias(mapping, s, index, writable);
}
fn flushMemory() void {
    asm volatile ("mov %[p], %%cr3"
        :
        : [p] "r" (phys(&states[active].root)),
        : .{ .memory = true });
}
fn memoryOperation(f: *const Frame) *const Frame {
    const s = &states[active];
    if (!s.admitted or s.terminal or s.memory_cap == 0 or f.rdi != s.memory_cap or (supervised and active == supervisorSlot()))
        return memoryError(s, error.Denied);
    // Unused inputs are reserved and must be zero, never interpreted as flags.
    if (f.r8 != 0 or f.r9 != 0 or (f.rax != 0x22002 and f.r10 != 0)) return memoryError(s, error.Invalid);
    if (f.rax == 0x22000) {
        if (f.rsi != 0 or f.rdx != 0) return memoryError(s, error.Invalid);
        result(s, @intCast(s.pages.len - arena.used(s.records())));
        s.context().frame.rdx = memory.base;
        s.context().frame.rcx = arenaEnd(s);
        s.context().frame.r8 = s.pages.len;
        return select();
    }
    if (f.rax == 0x22001) {
        const plan = arena.map(s.records(), f.rsi, f.rdx, .{}) catch |err| return memoryError(s, err);
        const tables = memory.tables(s.pt_index[0..s.pt_count], s.pts.len, plan.address, plan.count, true) catch |err| return memoryError(s, err);
        const flags = memory.flags(f.rdx) catch unreachable;
        // Resolve every backing, record and table slot before any mutation.
        // PROT_NONE reserves and zeros backing and retains its table too.
        for (tables.entries[0..tables.count]) |entry| if (entry.fresh) {
            const t = entry.slot;
            @memset(&s.pts[t], 0);
            s.pt_index[t] = entry.directory;
            s.pd[s.pt_index[t]] = phys(&s.pts[t]) | 7;
            s.pt_count = @max(s.pt_count, t + 1);
        };
        var backing_slots = plan.freeSlots(s.records());
        for (0..plan.count) |i| {
            const slot = backing_slots.next().?;
            @memset(&s.backing[slot], 0);
            const address = plan.address + i * 4096;
            const t = tables.slot(address);
            s.pages[slot] = .{ .address = address, .flags = flags, .anonymous = true };
            s.count = @max(s.count, @as(usize, slot) + 1);
            s.pts[t][address / 4096 % 512] = if (flags & 1 != 0) backingFrame(s, slot) | flags else 0;
            memoryAlias(s, slot, flags & 2 != 0);
        }
        result(s, @intCast(plan.address));
        return select(); // CR3 reload completes translation invalidation.
    }
    const plan = arena.range(s.records(), f.rsi, f.rdx, s.execution.fs, s.execution.clear_tid) catch |err| return memoryError(s, err);
    for (s.children) |c| if (c.running and !@import("build_options").native_threads_skip_pin) {
        plan.checkPins(c.execution.fs, c.execution.clear_tid) catch |err| return memoryError(s, err);
        if (c.execution.tls_bytes != 0 and plan.address < c.execution.tls_base + c.execution.tls_bytes and
            plan.address + plan.count * 4096 > c.execution.tls_base) return memoryError(s, error.Denied);
        if (plan.address < c.stack + c.stack_bytes and plan.address + plan.count * 4096 > c.stack)
            return memoryError(s, error.Denied);
    };
    if (!@import("build_options").native_wait_skip_pin) {
        const contexts = s.contexts();
        for (contextView(&contexts)) |context| {
            const key = context.wait.address;
            if (key != 0 and plan.address < key + 4 and plan.address + plan.count * 4096 > key)
                return memoryError(s, error.Denied);
        }
    }
    const tables = memory.tables(s.pt_index[0..s.pt_count], s.pts.len, plan.address, plan.count, false) catch |err| return memoryError(s, err);
    if (f.rax == 0x22002) {
        const flags = memory.flags(f.r10) catch |err| return memoryError(s, err);
        if (@import("build_options").native_memory_deny_protect_once and !s.memory_protect_denied) {
            s.memory_protect_denied = true;
            return memoryError(s, error.Denied);
        }
        if (!@import("build_options").native_memory_skip_protect or flags & 2 != 0) {
            var slots = plan.rangeSlots(s.records());
            for (0..plan.count) |offset| {
                const slot = if (service_memory) slots.next().? else plan.slot(s.records(), offset);
                const t = tables.slot(s.pages[slot].address);
                s.pages[slot].flags = flags;
                s.pts[t][s.pages[slot].address / 4096 % 512] = if (flags & 1 != 0) backingFrame(s, slot) | flags else 0;
                memoryAlias(s, slot, flags & 2 != 0);
            }
        }
    } else {
        var slots = plan.rangeSlots(s.records());
        for (0..plan.count) |offset| {
            const slot = if (service_memory) slots.next().? else plan.slot(s.records(), offset);
            const t = tables.slot(s.pages[slot].address);
            s.pts[t][s.pages[slot].address / 4096 % 512] = 0;
            memoryAlias(s, slot, true);
        }
        flushMemory(); // Access removed before zeroing and returning quota.
        slots = plan.rangeSlots(s.records());
        for (0..plan.count) |offset| {
            const slot = if (service_memory) slots.next().? else plan.slot(s.records(), offset);
            if (!@import("build_options").native_memory_skip_zero) @memset(&s.backing[slot], 0);
            for (&s.backing[slot]) |value| if (value != 0) @panic("native runtime backing not zeroed");
            s.pages[slot] = .{};
        }
        for (tables.entries[0..tables.count]) |entry| {
            var any = false;
            for (s.records()) |page| if (page.address != 0 and page.address / memory.leaf_span == entry.directory) {
                any = true;
                break;
            };
            if (!any) {
                s.pd[entry.directory] = 0;
                @memset(&s.pts[entry.slot], 0);
                s.pt_index[entry.slot] = memory.vacant_table;
            }
        }
    }
    result(s, 0);
    return select();
}

// Scalar-only cooperative boundary. IF=0 excludes scheduling through validation
// and state publication; the interrupt entry already saved registers and FX state.
fn freezeOperation(f: *const Frame) *const Frame {
    const caller = &states[active];
    if (f.rax == 0x23003) {
        var error_code: i64 = 0;
        if (active == supervisorSlot()) error_code = -13 else if (f.rdi | f.rsi | f.rdx | f.r10 | f.r8 | f.r9 != 0) error_code = -22 else if (threadedSlot(active) or (@import("build_options").native_signal_actions and !@import("build_options").native_copy_signals)) error_code = -95 else if (caller.frozen) error_code = -16 else if (caller.freeze_sequence == std.math.maxInt(i64)) error_code = -28;
        if (error_code != 0) {
            result(caller, error_code);
            return select();
        }
        caller.freeze_sequence += 1;
        caller.frozen = !@import("build_options").native_freeze_skip_park;
        if (session_lifecycle) publishSustained();
        // Cancellation returns EAGAIN; opt-in private copy can install a child result.
        result(caller, -11);
        rotate();
        return select();
    }
    if (active != supervisorSlot()) {
        result(caller, -13);
        return select();
    }
    if (f.rdx | f.r10 | f.r8 | f.r9 != 0 or (f.rax == 0x23004 and f.rsi != 0)) {
        result(caller, -22);
        return select();
    }
    const slot = lookup(f.rdi) orelse {
        result(caller, -9);
        return select();
    };
    const source = &states[slot];
    if (!processSlot(slot)) {
        result(caller, -13);
        return select();
    }
    if (source.terminal) {
        result(caller, -16);
    } else if (f.rax == 0x23004) {
        result(caller, if (source.frozen) @intCast(source.freeze_sequence) else 0);
    } else if (@import("build_options").native_process_exec and source.image_commit.pending) {
        result(caller, -16);
    } else if (!source.frozen) {
        result(caller, -16);
    } else if ((f.rsi == 0 or f.rsi != source.freeze_sequence) and !@import("build_options").native_freeze_ignore_token) {
        result(caller, -9);
    } else {
        source.frozen = false;
        result(source, -11);
        result(caller, 0);
    }
    return select();
}

// Source is parked and IF=0. Only owned backing is copied; no kernel pointers,
// source endpoint ownership, waits or clear-TID registrations enter the child.
fn copyOperation(f: *const Frame) *const Frame {
    const caller = &states[active];
    if (active != supervisorSlot() or f.rdi != 0xa001) {
        result(caller, -13);
        return select();
    }
    const from = lookup(f.rsi) orelse {
        result(caller, -9);
        return select();
    };
    if (f.rdx >= workerCount() or f.rdx == from) {
        result(caller, -22);
        return select();
    }
    const source = &states[from];
    const slot: usize = @intCast(f.rdx);
    const child = &states[slot];
    if (source.terminal or !source.frozen or child.admitted or
        (@import("build_options").native_process_exec and source.image_commit.pending and !@import("build_options").native_exec_copy))
    {
        result(caller, -16);
        return select();
    }
    if (f.r10 == 0 or f.r10 != source.freeze_sequence) {
        result(caller, -9);
        return select();
    }
    if (threadedSlot(from) or !processSlot(from) or !processSlot(slot) or (@import("build_options").native_signal_actions and !@import("build_options").native_copy_signals)) {
        result(caller, -95);
        return select();
    }
    if (child.generation >= lifetimeLimit()) {
        result(caller, -28);
        return select();
    }
    const reader = ownedChannel(active, f.r8) orelse {
        result(caller, -13);
        return select();
    };
    const writer = ownedChannel(active, f.r9) orelse {
        result(caller, -13);
        return select();
    };
    if (reader == writer or reader.lookup(active, f.r8).? != 0 or writer.lookup(active, f.r9).? != 1 or
        reader.owners[0] != active or reader.owners[1] != active or writer.owners[0] != active or writer.owners[1] != active or
        reader.stream.count != 0 or writer.stream.count != 0 or reader.stream.sealed or reader.stream.reader_closed or writer.stream.sealed or writer.stream.reader_closed)
    {
        result(caller, -13);
        return select();
    }
    if (!copyPreflight(source, child)) {
        result(caller, -12);
        return select();
    }
    // Identical fixed pools bound every source live page and leaf directory. The
    // source metadata is kernel-owned and validated at each map/load operation.
    const prior_generation = child.generation;
    resetState(child);
    child.generation = prior_generation;
    mapKernel(child);
    child.root[0] = phys(&child.pdpt) | 7;
    child.pdpt[0] = phys(&child.pd) | 7;
    for (source.pages[0..source.count], 0..) |page, i| {
        if (page.address == 0) continue;
        addPage(child, page.address, page.flags);
        const at = child.count - 1;
        child.pages[at].anonymous = page.anonymous and !@import("build_options").native_copy_lose_anonymous;
        @memcpy(&child.backing[at], &source.backing[i]);
        if (@import("build_options").native_copy_share and page.anonymous and page.flags & 2 != 0 and
            !(source.execution.fs >= page.address and source.execution.fs - page.address < 4096))
        {
            for (child.pt_index[0..child.pt_count], 0..) |directory, t| {
                if (directory == page.address / memory.leaf_span) child.pts[t][page.address / 4096 % 512] = backingFrame(source, i) | page.flags;
            }
        }
    }
    if (@import("build_options").native_copy_fail_stage) {
        child.root[0] = 0; // Never installed in CR3 or published to a worker.
        if (!@import("build_options").native_copy_skip_zero) @memset(child.payloadBytes(), 0);
        for (child.payload()) |*page| for (page) |value| {
            if (value != 0) @panic("native copy rollback not zeroed");
        };
        resetState(child);
        child.generation = prior_generation;
        result(caller, -12);
        return select();
    }
    child.generation = prior_generation + 1;
    child.execution = .{
        .frame = source.execution.frame,
        .fp = source.execution.fp,
        .fs = source.execution.fs,
        .tls_base = source.execution.tls_base,
        .tls_bytes = source.execution.tls_bytes,
        .signal_mask = source.execution.signal_mask,
    };
    // Private dispositions, empty child pending set, before publication.
    if (@import("build_options").native_signal_actions) {
        if (!@import("build_options").native_copy_signals_drop) child.signal_actions.inheritFrom(&source.signal_actions);
        if (@import("build_options").native_copy_signals_pending) child.signal_actions.pending = source.signal_actions.pending;
        if (@import("build_options").native_copy_signals_parent) source.signal_actions.pending = 0;
    }
    child.parent_pid = source.generation * states.len + from + 1;
    child.memory_cap = 0x40000000 | (child.generation << 8) | (slot + 1);
    child.channel_cap = f.r8;
    child.channel_reply_cap = f.r9;
    child.execution.frame.rax = 0;
    child.execution.frame.rdi = child.memory_cap;
    child.execution.frame.rsi = child.channel_cap;
    child.execution.frame.rdx = child.channel_reply_cap;
    // Protect every domain's immutable aliases and flush before publication.
    for (&states) |*owner| aliases(owner, false);
    require(reader.transfer(active, f.r8, slot) and writer.transfer(active, f.r9, slot));
    child.admitted = true;
    if (af09_enabled) af09Bind(from, slot);
    source.frozen = false;
    result(source, @intCast(child.generation * states.len + slot + 1));
    result(caller, @intCast(handle(slot)));
    return select();
}

// Private image-only primitive. The owner publishes after its descriptor policy;
// this operation never interprets Unix FD flags or creates executable authority.
fn execOperation(f: *const Frame) *const Frame {
    const caller = &states[active];
    if (active != supervisorSlot() or f.rdi != 0xa001) {
        result(caller, -13);
        return select();
    }
    const slot = lookup(f.rsi) orelse {
        result(caller, -9);
        return select();
    };
    const s = &states[slot];
    if (!processSlot(slot)) {
        result(caller, -13);
        return select();
    }
    if (f.rax == 0x23008) {
        if (f.rdx | f.r10 | f.r8 | f.r9 != 0) {
            result(caller, -22);
        } else {
            result(caller, @intCast(s.image_commit.sequence));
            caller.execution.frame.rdx = s.image_commit.image;
            caller.execution.frame.r8 = @intFromBool(s.image_commit.pending);
        }
        return select();
    }
    if (s.terminal) {
        result(caller, -16);
        return select();
    }
    if (f.rax == 0x23009) {
        if (f.r10 | f.r8 | f.r9 != 0) {
            result(caller, -22);
        } else if ((f.rdx == 0 or f.rdx != s.image_commit.sequence or s.freeze_sequence != s.image_commit.sequence) and !@import("build_options").native_exec_token) {
            result(caller, -9);
        } else {
            s.image_commit.pending = false;
            s.frozen = false;
            result(caller, 0);
        }
        return select();
    }
    if (f.rdx != 0xc001 and f.rdx != 0xc002 and f.rdx != 0xc003) {
        result(caller, -13);
        return select();
    }
    if (f.r9 != 0) {
        result(caller, -22);
        return select();
    }
    if (!s.frozen or s.image_commit.pending) {
        result(caller, -16);
        return select();
    }
    if (f.r10 == 0 or f.r10 != s.freeze_sequence) {
        result(caller, -9);
        return select();
    }
    var raw: [launch.record_size]u8 = undefined;
    if (f.r8 > std.math.maxInt(u64) - raw.len) {
        result(caller, -14);
        return select();
    }
    for (&raw, 0..) |*v, index| {
        const address = byte(caller, @intCast(f.r8 + index), false) orelse {
            result(caller, -14);
            return select();
        };
        v.* = address.*;
    }
    const args = launch.arguments(&raw) catch {
        result(caller, -22);
        return select();
    };
    const image = if (f.rdx == 0xc001) &service_image else if (f.rdx == 0xc002) &second_image else &third_image;
    const bytes = if (f.rdx == 0xc001) service_bytes[0..service_len] else if (f.rdx == 0xc002) second_bytes[0..second_len] else third_bytes[0..third_len];
    if (!imagePreflight(s, image)) {
        result(caller, -12);
        return select();
    }
    // Boot-validated immutable image and fixed pools: no recoverable operation
    // follows this point. We execute under IF=0 on the supervisor's CR3.
    const next = s.execution.forImage(image.entry, 0x0800c000);
    aliases(s, true);
    @memset(std.mem.asBytes(&s.root), 0);
    @memset(std.mem.asBytes(&s.pdpt), 0);
    @memset(std.mem.asBytes(&s.pd), 0);
    @memset(std.mem.asBytes(&s.pts), 0);
    @memset(std.mem.asBytes(&s.pt_index), 0);
    @memset(s.payloadBytes(), 0);
    @memset(s.recordBytes(), 0);
    s.count = 0;
    s.pt_count = 0;
    s.execution = .{};
    if (@import("build_options").native_signal_actions) s.signal_actions = s.signal_actions.forImage();
    load(s, bytes, image, &bootstrap, slot);
    s.execution = next;
    launchStack(s, &args, image);
    s.ready = false;
    s.image_commit = .{ .sequence = f.r10, .image = f.rdx, .pending = true };
    s.frozen = !@import("build_options").native_exec_early;
    for (&states) |*owner| aliases(owner, false);
    if (af09_enabled and af09.engine_bound) af09Fail(slot, -6);
    result(caller, 0);
    return select();
}

// Complete user record copy and validation precede any slot/generation mutation.
fn launchOperation(f: *const Frame) *const Frame {
    const caller = &states[active];
    var failure: i64 = 0;
    const paired = f.rax == 0x23002;
    const transferring = f.rax == 0x23001 or paired;
    if (!processSlot(@intCast(f.rdx)) or active != supervisorSlot() or f.rdi != 0xa001 or (f.rsi != 0xc001 and f.rsi != 0xc002 and !(program_profile and f.rsi == 0xc003)) or (transferring and ownedChannel(active, f.r8) == null) or (paired and (f.r8 == f.r9 or ownedChannel(active, f.r9) == null))) {
        failure = -13;
    } else if (f.rdx >= workerCount() or (!transferring and f.r8 != 0) or (!paired and f.r9 != 0)) {
        failure = -22;
    } else if (states[@intCast(f.rdx)].admitted) {
        failure = -16;
    } else if (states[@intCast(f.rdx)].generation >= lifetimeLimit()) {
        failure = -28;
    }
    var raw: [launch.record_size]u8 = undefined;
    if (failure == 0) {
        if (f.r10 > std.math.maxInt(u64) - raw.len) {
            failure = -14;
        } else for (&raw, 0..) |*v, i| {
            const p = byte(caller, @intCast(f.r10 + i), false) orelse {
                failure = -14;
                break;
            };
            v.* = p.*;
        }
    }
    if (failure != 0) {
        result(caller, failure);
        return select();
    }
    const args = launch.arguments(&raw) catch {
        result(caller, -22);
        return select();
    };
    const slot: usize = @intCast(f.rdx);
    const s = &states[slot];
    const second = f.rsi == 0xc002;
    const third = program_profile and f.rsi == 0xc003;
    const image = if (third) &third_image else if (second) &second_image else &service_image;
    if (!imagePreflight(s, image)) {
        result(caller, -12);
        return select();
    }
    const generation = s.generation + 1;
    resetState(s);
    s.generation = generation;
    load(s, if (third) third_bytes[0..third_len] else if (second) second_bytes[0..second_len] else service_bytes[0..service_len], image, &bootstrap, slot);
    if (transferring) {
        require(ownedChannel(active, f.r8).?.transfer(active, f.r8, slot));
        s.channel_cap = f.r8;
    }
    if (paired) {
        require(ownedChannel(active, f.r9).?.transfer(active, f.r9, slot));
        s.channel_reply_cap = f.r9;
    }
    launchStack(s, &args, image);
    for (&states) |*owner| aliases(owner, false);
    publishSustained();
    result(caller, @intCast(handle(slot)));
    return select();
}
fn launchStack(s: *State, args: *const launch.Arguments, image: *const elf.Image) void {
    const data = 0x0800e000;
    // Preserve the entropy at data+128 populated by load; strings use data+256.
    const strings = data + 256;
    for (&args.strings, 0..) |*value, i| copy(s, strings + i * 32, value);
    const rsp = 0x0800c000;
    var index: usize = 0;
    word(s, rsp, args.argc);
    index += 1;
    for (0..args.argc) |i| {
        word(s, rsp + index * 8, strings + i * 32);
        index += 1;
    }
    word(s, rsp + index * 8, 0);
    index += 1;
    for (0..args.envc) |i| {
        word(s, rsp + index * 8, strings + (4 + i) * 32);
        index += 1;
    }
    word(s, rsp + index * 8, 0);
    index += 1;
    const aux = [_]u64{ 3, image.phdr, 4, 56, 5, image.phnum, 6, 4096, 9, image.entry, 11, 1000, 12, 1000, 13, 1000, 14, 1000, 23, 0, 25, data + 128, 31, strings };
    for (aux) |value| {
        word(s, rsp + index * 8, value);
        index += 1;
    }
    if (@import("build_options").native_memory) {
        word(s, rsp + index * 8, 0xa000);
        word(s, rsp + (index + 1) * 8, s.memory_cap);
        index += 2;
    }
    if (s.channel_cap != 0) {
        word(s, rsp + index * 8, 0xa001);
        word(s, rsp + (index + 1) * 8, s.channel_cap);
        index += 2;
    }
    if (s.channel_reply_cap != 0) {
        word(s, rsp + index * 8, 0xa002);
        word(s, rsp + (index + 1) * 8, s.channel_reply_cap);
        index += 2;
    }
    word(s, rsp + index * 8, 0);
    word(s, rsp + (index + 1) * 8, 0);
}

fn channelOperation(f: *const Frame) *const Frame {
    const s = &states[active];
    if (f.rax == 0x24004 and !channelWaitEnabled()) {
        result(s, -38);
        return select();
    }
    if (f.rax == 0x24000) {
        if (active != supervisorSlot() or (if (combined_profile) FsRoles.channelRange(f.rdi) == null else f.rdi != 0xd001)) {
            result(s, -13);
            return select();
        }
        if (f.rsi != 0 or f.rdx != 0 or f.r10 != 0 or f.r8 != 0 or f.r9 != 0) {
            result(s, -22);
            return select();
        }
        var free: ?*@import("../../native_channel.zig").Channel = null;
        var busy = false;
        const range = if (combined_profile) FsRoles.channelRange(f.rdi).? else FsRoles.ChannelRange{ .first = 0, .end = channelCount() };
        for (channels[range.first..range.end]) |*c| {
            if (c.owners[0] != null or c.owners[1] != null) {
                busy = true;
                continue;
            }
            if (c.generation < (if (combined_profile and range.first == FsRoles.process_channels) @as(u64, 3) else lifetimeLimit())) {
                free = c;
                break;
            }
        }
        const selected = free orelse {
            result(s, if (busy) -16 else -28);
            return select();
        };
        const r = if (sustained) selected.createSustained(active) else if (pipeline_session and (!combined_profile or range.first == 0)) selected.createSession(active) else selected.create(active);
        result(s, r);
        if (r >= 0) {
            s.context().frame.rdx = selected.cap(1);
            publishSustained();
        }
        return select();
    }
    const selected = ownedChannel(active, f.rdi) orelse {
        result(s, -13);
        if (af09_enabled and f.rax == 0x24003 and active == 6) af09CloseFailed(f.rdi, -13);
        return select();
    };
    const end = selected.lookup(active, f.rdi).?;
    if (f.rax == 0x24004) {
        if (@import("build_options").native_service_channel_wait and s.on_child) {
            result(s, -22);
            return select();
        }
        if (f.rsi | f.rdx | f.r10 | f.r8 | f.r9 != 0) {
            result(s, -22);
        } else if (s.channel_wait.begin(selected, active, f.rdi, channelInterrupted(s))) |done| {
            result(s, done);
        } else {
            // IF=0 spans readiness check, registration and scheduler exclusion.
            traceStorageChannelWait(active, "park", 0);
            rotate();
        }
        return select();
    }
    if (f.r10 != 0 or f.r8 != 0 or f.r9 != 0 or f.rdx > 256 or (f.rax == 0x24003 and (f.rsi != 0 or f.rdx != 0))) {
        result(s, -22);
        return select();
    }
    if (f.rax == 0x24003) {
        const queued_before_close = selected.stream.count;
        const closed = selected.close(active, f.rdi);
        if (af09_enabled) af09Closed(selected, queued_before_close, closed);
        result(s, closed);
        if (closed == 0) publishSustained();
        return select();
    }
    const reading = f.rax == 0x24001;
    if ((reading and end != 0) or (!reading and end != 1)) {
        result(s, -9);
        return select();
    }
    const count: usize = @intCast(@min(f.rdx, 16));
    if (f.rsi > std.math.maxInt(u64) - count) {
        result(s, -14);
        return select();
    }
    if (count == 0) {
        result(s, 0);
        return select();
    }
    const buffer = channelBuffer(s, @intCast(f.rsi), count, reading) orelse {
        result(s, -14);
        return select();
    };
    if (!reading and selected.stream.reader_closed) {
        result(s, -32);
        return select();
    }
    const amount = @min(count, if (reading) selected.stream.count else 32 - selected.stream.count);
    if (amount == 0) {
        const transfer_status: i64 = if (reading and selected.stream.sealed) 0 else -11;
        result(s, transfer_status);
        if (af09_enabled) af09Transfer(selected, reading, 0, transfer_status);
        return select();
    }
    for (0..amount) |i| {
        const p = if (i < buffer.first.len) &buffer.first[i] else &buffer.second[i - buffer.first.len];
        if (reading) p.* = @intCast(selected.stream.pop()) else require(selected.stream.push(p.*) == 0);
    }
    if (amount > 0) publishSustained();
    result(s, @intCast(amount));
    if (af09_enabled) af09Transfer(selected, reading, amount, @intCast(amount));
    return select();
}

fn ownedChannel(owner: usize, value: u64) ?*@import("../../native_channel.zig").Channel {
    for (channels[0..channelCount()]) |*c| if (c.lookup(owner, value) != null) return c;
    return null;
}
fn closeChannels(owner: usize) void {
    for (channels[0..channelCount()]) |*c| {
        const before = c.stream.count;
        c.closeOwner(owner);
        if (af09_enabled and af09.bound and af09Matches(c, 0) and before > c.stream.count) af09Row(13, 2, 0, before - c.stream.count, af09.late_read);
    }
}

fn channelInterrupted(s: *const State) bool {
    if (!@import("build_options").native_signal_actions) return false;
    return s.signal_actions.interrupts(s.execution.signal_mask);
}

fn channelWaitEnabled() bool {
    return session_lifecycle or @import("build_options").native_service_channel_wait;
}
fn storagePrimaryWaiting(s: *const State) bool {
    return @import("build_options").native_service_channel_wait and s.channel_wait.endpoint != 0;
}
fn traceStorageChannelWait(owner: usize, phase: []const u8, status: i64) void {
    if (!@import("build_options").native_service_channel_wait) return;
    // The traced ABI31 console shares UART with partial shell output. Keep the
    // machine row on its own line; old profiles retain their exact output.
    if (combined_owner_stack) serial.write("\n");
    var line: [128]u8 = undefined;
    serial.write(std.fmt.bufPrint(&line, "NATIVE STORAGE WAIT slot={d} generation={d} phase={s} status={d}\n", .{ owner, states[owner].generation, phase, status }) catch unreachable);
}
fn refreshChannelWaits() void {
    if (!channelWaitEnabled()) return;
    for (&states, 0..) |*s, owner| {
        if (!s.admitted or s.terminal or s.channel_wait.endpoint == 0) continue;
        const channel = ownedChannel(owner, s.channel_wait.endpoint);
        if (s.channel_wait.poll(channel, owner, channelInterrupted(s))) |done| {
            // Only a registered primary context receives this completion, once.
            s.execution.frame.rax = @bitCast(done);
            traceStorageChannelWait(owner, "wake", done);
        }
    }
}

fn refreshWait() void {
    if (!init_profile or !observation.occupied) return;
    const slot = lookup(observation.target);
    observation.refresh(total_ticks, if (slot) |i| states[i].revision else null);
}
fn waitOperation(f: *const Frame) *const Frame {
    const caller = &states[active];
    if (active != supervisorSlot() or f.rdi != 0xe001) {
        result(caller, -13);
        return select();
    }
    if (f.r8 != 0 or f.r9 != 0 or (f.rax != 0x25002 and (f.rdx != 0 or f.r10 != 0)) or (f.rax == 0x25000 and f.rsi != 0)) {
        result(caller, -22);
        return select();
    }
    refreshWait();
    if (f.rax == 0x25000) {
        result(caller, @intCast(total_ticks));
    } else if (f.rax == 0x25001 or f.rax == 0x25002) {
        const slot = lookup(f.rsi) orelse {
            result(caller, -9);
            return select();
        };
        const target = &states[slot];
        if (f.rax == 0x25001) {
            result(caller, @intCast(target.revision));
            caller.context().frame.rdx = if (target.terminal) target.status + 1 else 0;
            caller.context().frame.r8 = @intFromBool(target.ready);
        } else result(caller, observation.register(f.rsi, f.rdx, if (@import("build_options").native_init_skip_deadline) std.math.maxInt(u64) else f.r10, total_ticks, target.revision));
    } else if (!observation.valid(f.rsi)) {
        result(caller, -9);
    } else if (f.rax == 0x25005) {
        observation.occupied = false;
        result(caller, 0);
    } else {
        if (f.rax == 0x25004) observation.cancel(total_ticks);
        result(caller, @intCast(observation.status));
        caller.context().frame.rdx = observation.revision;
        caller.context().frame.r8 = observation.completed;
    }
    return select();
}
// This profile shuts down the entire BSP domain; it does not select a successor.
fn closeInit() noreturn {
    var live: usize = 0;
    var terminal: usize = 0;
    for (states[0..2]) |*s| if (s.admitted) {
        if (s.terminal) terminal += 1 else live += 1;
    };
    var note: [128]u8 = undefined;
    serial.write(std.fmt.bufPrint(&note, "NATIVE init closing live={d} terminal={d} queued={d} wait={d}\n", .{ live, terminal, channels[0].stream.count + channels[1].stream.count, @intFromBool(observation.occupied) }) catch "init closing\n");
    observation = .{};
    // Stop all user execution and detach roots before making backing writable.
    for (&states, 0..) |*s, i| {
        s.terminal = true;
        s.admitted = false;
        s.memory_cap = 0;
        s.entropy_grant.selector = 0;
        s.channel_cap = 0;
        s.channel_reply_cap = 0;
        s.root[0] = 0;
        closeChannels(i);
    }
    for (&states) |*s| aliases(s, true);
    for (&states) |*s| {
        if (!@import("build_options").native_skip_zero) for (s.payload()) |*page| {
            @memset(page, 0);
        };
        for (s.payload()) |*page| for (page) |v| if (v != 0) {
            @panic("native init cleanup not zeroed");
        };
        s.input = .{};
        @memset(&s.output, 0);
        @memset(&s.errors, 0);
        s.output_count = 0;
        s.errors_count = 0;
        s.context().fs = 0;
        s.context().clear_tid = 0;
        s.ready = false;
        s.revision = 0;
        s.status = 0;
        s.terminal_kind = 0;
    }
    for (channels[0..channelCount()]) |*c| {
        require(c.owners[0] == null and c.owners[1] == null);
        for (c.stream.bytes) |v| require(v == 0);
    }
    msr(0xc0000100, 0);
    serial.write(if (init_composed) "AETHER NATIVE INIT COMPOSED CLOSED\n" else if (init_large) "AETHER NATIVE INIT LARGE CLOSED\n" else "AETHER NATIVE INIT CLOSED\n");
    serial.halt();
}

fn sessionObservation(f: *const Frame) *const Frame {
    const caller = &states[active];
    if (active != supervisorSlot() or f.rdi != 0xa001) {
        result(caller, -13);
        return select();
    }
    if (session_observations == 3) {
        result(caller, -28);
        return select();
    }
    if (f.rdx != 176 or f.r8 | f.r9 != 0) {
        result(caller, -22);
        return select();
    }
    if (f.r10 != @as(u64, session_observations) + 1) {
        result(caller, -9);
        return select();
    }
    var raw: [176]u8 = undefined;
    if (f.rsi > std.math.maxInt(u64) - raw.len) {
        result(caller, -14);
        return select();
    }
    for (&raw, 0..) |*value, index| {
        const pointer = byte(caller, @intCast(f.rsi + index), false) orelse {
            result(caller, -14);
            return select();
        };
        value.* = pointer.*;
    }
    const record = @import("../../native_session_observation.zig").parse(&raw) catch {
        result(caller, -22);
        return select();
    };
    for (states[0..workerCount()]) |*worker| if (worker.admitted) {
        result(caller, -16);
        return select();
    };
    for (channels[0..channelCount()]) |*channel| if (channel.owners[0] != null or channel.owners[1] != null or channel.stream.count != 0) {
        result(caller, -16);
        return select();
    };
    if (reclaimed - session_report_reclaimed != @as(usize, record.copies) + 1) {
        result(caller, -22);
        return select();
    }
    var header: [100]u8 = undefined;
    serial.write(std.fmt.bufPrint(&header, "NATIVE SESSION generation={d} copies={d} execs={d} stdout=", .{ f.r10, record.copies, record.execs }) catch unreachable);
    const digits = "0123456789abcdef";
    for (record.stdout) |value| {
        const pair = [_]u8{ digits[value >> 4], digits[value & 15] };
        serial.write(&pair);
    }
    serial.write(" stderr=");
    for (record.stderr) |value| {
        const pair = [_]u8{ digits[value >> 4], digits[value & 15] };
        serial.write(&pair);
    }
    serial.write("\n");
    session_observations += 1;
    session_report_reclaimed = reclaimed;
    result(caller, 0);
    return select();
}

fn publishSustained() void {
    if (ownerEventsEnabled()) sustained_events.publish(total_ticks) catch @panic("native event sequence exhausted");
}

fn refreshSustained() void {
    if (!ownerEventsEnabled()) return;
    sustained_events.poll(total_ticks, !storageLifetime() and !console_closed and serial.inputReady());
    if (sustained_events.take()) |completion| {
        const owner = &states[supervisorSlot()];
        result(owner, switch (completion.outcome) {
            .event => 0,
            .deadline => -110,
            .cancelled => -125,
        });
        owner.context().frame.rdx = completion.sequence;
        owner.context().frame.r8 = completion.tick;
        if (af09_enabled and af09.observed) af09RowAt(.{ .phase = 11, .slot = supervisorSlot(), .gen = owner.generation, .seq = completion.sequence, .tick = completion.tick, .deadline = af09.deadline, .status = @bitCast(owner.context().frame.rax) });
        if (storageLifetime()) {
            var note: [128]u8 = undefined;
            serial.write(std.fmt.bufPrint(&note, "NATIVE STORAGE wake tick={d} outcome={s}\n", .{ completion.tick, @tagName(completion.outcome) }) catch unreachable);
        }
    }
}

// IF=0 serializes the caller checks, snapshot comparison and scheduler publication.
fn sustainedOperation(f: *const Frame) *const Frame {
    const owner = &states[active];
    const halt = f.rax == 0x2a002;
    if (active != supervisorSlot() or f.rdi != (if (halt) @as(u64, 0xf002) else 0xe002)) {
        result(owner, -13);
        return select();
    }
    if (f.r10 != 0 or f.r8 != 0 or f.r9 != 0 or (f.rax != 0x2a001 and f.rdx != 0) or (f.rax == 0x2a000 and f.rsi != 0)) {
        result(owner, -22);
        return select();
    }
    if (halt) {
        if (storageLifetime()) {
            result(owner, -38);
            return select();
        }
        if (f.rsi != 0) {
            result(owner, -38);
            return select();
        }
        var busy = sustained_events.occupied or !console_closed or (combined_profile and !block_closed);
        for (states[0..workerCount()]) |*worker| busy = busy or worker.admitted;
        for (channels[0..channelCount()]) |*channel| busy = busy or channel.owners[0] != null or channel.owners[1] != null or channel.stream.count != 0;
        if (busy) {
            result(owner, -16);
            return select();
        }
        var note: [128]u8 = undefined;
        serial.write(std.fmt.bufPrint(&note, "NATIVE init halted ticks={d} idle={d} reclaimed={d}\n", .{ total_ticks, idle_ticks, reclaimed }) catch unreachable);
        if (af09_enabled) {
            af09Row(23, active, 0, 0, 0);
            if (af09_mode.negative()) af09Fail(active, -6);
        }
        if (combined_profile) serial.write("AETHER NATIVE BLOCK PASS\n");
        serial.halt();
    }
    if (f.rax == 0x2a000) {
        result(owner, 0);
        owner.context().frame.rdx = sustained_events.sequence;
        owner.context().frame.r8 = total_ticks;
        if (af09_enabled and af09.query_positive and !af09.observed) {
            if (af09.beginDrain(total_ticks)) af09Row(9, active, 0, 0, 0) else af09Fail(active, -4);
        }
        if (storageLifetime()) {
            var note: [128]u8 = undefined;
            serial.write(std.fmt.bufPrint(&note, "NATIVE STORAGE observe tick={d}\n", .{total_ticks}) catch unreachable);
        }
        return select();
    }
    if (af09_enabled and af09BeforePark(f)) {
        rotate();
        return select();
    }
    sustained_events.park(f.rsi, total_ticks, if (f.rdx == 0) null else f.rdx, !storageLifetime() and !console_closed and serial.inputReady()) catch |err| {
        result(owner, switch (err) {
            error.Busy => -16,
            error.FutureSequence => -22,
            error.Exhausted => -28,
        });
        return select();
    };
    if (storageLifetime()) {
        var note: [128]u8 = undefined;
        serial.write(std.fmt.bufPrint(&note, "NATIVE STORAGE park tick={d} deadline={d}\n", .{ total_ticks, f.rdx }) catch unreachable);
    }
    refreshSustained();
    if (sustained_events.parked()) rotate();
    return select();
}
