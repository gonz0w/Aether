const std = @import("std");
const supervisor = @import("supervisor.zig");
var supervisor_current = false;
var switches: u64 = 0;
var scheduler_ticks: u64 = 0;
var control_denied: u64 = 0;
const stream = @import("display_stream.zig");
const user_cpu = @import("user_cpu.zig");
const serial = @import("serial.zig");
const Frame = @import("context.zig").Frame;
const grants = @import("../../display_grant.zig");
const limine = @import("../../limine.zig");
const Layout = @import("../../framebuffer.zig").Layout;
var image: [4096]u8 align(4096) = @splat(0);
var image_len: usize = 0;
var layout: Layout = undefined;
var grant: grants.Grant = undefined;
// Bootstrap capture, then exclusively BSP-owned. No M3 backing is reused.
var runtime: user_cpu.State = .{};
var framebuffer_pt: [512]u64 align(4096) = @splat(0);
var mapped = false;
var boundary_denied = false;
var invalid: u64 = 0;
var denied: u64 = 0;
var duplicate: u64 = 0;
var link_stats = stream.Stats{};
pub var active = false; // Read only on the BSP dispatch path.
extern fn restore_context(u64, *const Frame) callconv(.c) noreturn;

pub fn capture(fb: limine.Framebuffer, geometry: Layout, hhdm: u64, memory: *const limine.MemoryResponse, module: *const limine.File, supervisor_module: *const limine.File) void {
    supervisor.capture(supervisor_module);
    if (module.size == 0 or module.size > image.len) @panic("invalid display image");
    const bytes = module.address orelse @panic("missing display image");
    image_len = @intCast(module.size);
    @memcpy(image[0..image_len], bytes[0..image_len]);
    layout = geometry;
    const address = @intFromPtr(fb.address.?);
    if (address < hhdm) @panic("framebuffer outside direct mapping");
    grant = grants.Grant.init(address - hhdm, fb.pitch * fb.height) catch @panic("unsupported display grant span");
    const rounded_end = grant.physical + grant.pages * 4096;
    var found = false;
    const entries = memory.entries.?;
    for (entries[0..@intCast(memory.count)]) |entry| {
        const end = std.math.add(u64, entry.base, entry.length) catch @panic("memory span overflow");
        if (entry.kind == 7 and grant.physical >= entry.base and grant.physical + grant.bytes <= end) found = true;
        if (entry.kind != 7 and entry.base < rounded_end and end > grant.physical)
            @panic("framebuffer page overlaps another memory region");
    }
    if (!found) @panic("framebuffer grant is not framebuffer memory");
    if (@import("build_options").no_framebuffer_grant) grant.map_right = false;
}
pub fn start(inputs: user_cpu.Inputs) noreturn {
    supervisor.prepare(inputs);
    var local_inputs = inputs;
    local_inputs.image = image[0..image_len];
    runtime.prepare(local_inputs, 0);
    runtime.frame.rdi = grants.root;
    runtime.frame.r9 = supervisor.link.handle(0);
    runtime.frame.rsi = layout.width;
    runtime.frame.rdx = layout.height;
    runtime.frame.rcx = layout.stride;
    runtime.frame.r8 = @as(u64, layout.red) | (@as(u64, layout.green) << 8) | (@as(u64, layout.blue) << 16) | supervisor.binding;
    // Install the empty hierarchy only; the capability invocation fills PTEs.
    runtime.pd[16] = inputs.physical(&framebuffer_pt) | 7;
    if (runtime.root_physical == supervisor.runtime.root_physical or inputs.physical(&runtime.stack) == inputs.physical(&supervisor.runtime.stack)) @panic("BSP services share private backing");
    active = true;
    user_cpu.startTimer(false);
    serial.write("DISPLAY: fresh Rust domain with framebuffer map/inspect grants\n");
    restore_context(runtime.root_physical, &runtime.frame);
}
fn displayException(frame: *const Frame) *const Frame {
    if (frame.cs != 0x23 or !runtime.runnable) @panic("display kernel fault");
    runtime.frame = frame.*;
    if (frame.vector == 255) return &runtime.frame;
    if (frame.vector == 32) return &runtime.frame;
    if (frame.vector == 14) {
        const address = asm volatile ("mov %%cr2, %[value]"
            : [value] "=r" (-> u64),
        );
        if (!mapped or boundary_denied or frame.error_code != 6 or address != grants.base + grant.pages * 4096 or frame.rax != address)
            @panic("unexpected display user fault");
        boundary_denied = true;
        runtime.frame.rip += 3; // Known MOV byte ptr [RAX],0 fixture instruction.
        return &runtime.frame;
    }
    if (frame.vector != 128) @panic("unexpected display interrupt");
    const result = &runtime.frame;
    result.rdx = 0;
    if (frame.rax == 20) {
        result.rax = 0;
        return result;
    }
    if (frame.rax >= 50 and frame.rax <= 53) {
        control_denied += 1;
        result.rax = 1;
        return result;
    }
    if (frame.rax == 54) {
        if (frame.rdi != supervisor.binding) {
            result.rax = 1;
            return result;
        }
        result.rax = if (supervisor.link.live) 0 else 6;
        if (supervisor.link.live) result.rdx = supervisor.link.handle(0);
        return result;
    }
    if (frame.rax == 1 or frame.rax == 2) {
        const response = stream.invoke(&supervisor.link, &link_stats, frame.rax, frame.rdi, frame.rsi);
        result.rax = response.status;
        result.rdx = response.value;
        return result;
    }
    if (frame.rax == 0) {
        // Fixture evidence only: counts and the rebound namespace come from
        // BSP-owned state, not the user-supplied result payload.
        if (frame.rdi == 5 and link_stats.sent == 20 and link_stats.received == 21 and
            supervisor.link.live and supervisor.link.namespace == (@as(u64, 6) << 32))
            serial.write("DISPLAY: second-generation result rejected after 20 acknowledgments\n");
        if (frame.rdi != 0 or !mapped or !boundary_denied or invalid != 2 or denied != 1 or duplicate != 1 or link_stats.sent != 100 or link_stats.received != 100 or link_stats.invalid != 6 or link_stats.denied != 1)
            @panic("display service checks failed");
        if (!supervisor.done or !stream.finished()) {
            result.rax = 6;
            return result;
        }
        if (control_denied != 1) @panic("display retained control authority");
        if (!stream.drained()) @panic("display queues not drained after publisher exit");
        supervisor.link.live = false;
        runtime.runnable = false;
        result.rax = 0;
        return result;
    }
    if (frame.rax != 40 and frame.rax != 41) {
        result.rax = 1;
        return result;
    }
    grant.require(frame.rdi, frame.rax == 40) catch |err| {
        if (err == error.Invalid) {
            invalid += 1;
            result.rax = 1;
        } else {
            denied += 1;
            result.rax = 2;
        }
        return result;
    };
    result.rax = 0;
    if (frame.rax == 41) {
        result.rdx = grant.bytes;
        return result;
    }
    if (mapped) {
        duplicate += 1;
        result.rax = 6;
        return result;
    }
    // UC matches the bounded MMIO model; no active kernel/HHDM framebuffer alias.
    for (0..grant.pages) |i| framebuffer_pt[i] = grant.physical + i * 4096 | 0x1f | (@as(u64, 1) << 63);
    asm volatile ("mov %[root], %%cr3"
        :
        : [root] "r" (runtime.root_physical),
        : .{ .memory = true });
    mapped = true;
    result.rdx = grants.base;
    return result;
}

// Two fixed BSP domains share the CPU's TSS/interrupt stack, not user mappings.
pub fn exception(frame: *const Frame) *const Frame {
    _ = if (supervisor_current) supervisor.exception(frame) else displayException(frame);
    if (frame.vector == 32) {
        user_cpu.apicWrite(0xb0, 0);
        scheduler_ticks += 1;
        if (scheduler_ticks > 1000) @panic("BSP services stalled; resources reserved");
    }
    if (supervisor.done and !runtime.runnable) {
        if (switches < 4 or scheduler_ticks == 0) @panic("BSP scheduling not exercised");
        user_cpu.stopTimer();
        serial.write("DISPLAY: 100 generation-checked results rendered across replacement\nAETHER DISPLAY PASS\nAETHER LIVE DISPLAY PASS\nAETHER REMOTE LIFETIME PASS\nSUPERVISOR: isolated Rust controller verified five reclaims, two faults and three stops\nAETHER SMP SUPERVISOR PASS\nAETHER FAULT RECOVERY PASS\n");
        serial.halt();
    }
    if (frame.vector == 32 or (frame.vector == 128 and frame.rax == 20) or
        (supervisor_current and !supervisor.runtime.runnable) or (!supervisor_current and !runtime.runnable))
    {
        const other_runnable = if (supervisor_current) runtime.runnable else supervisor.runtime.runnable;
        if (other_runnable) {
            supervisor_current = !supervisor_current;
            switches += 1;
        }
    }
    const selected = if (supervisor_current) &supervisor.runtime else &runtime;
    asm volatile ("mov %[root], %%cr3"
        :
        : [root] "r" (selected.root_physical),
        : .{ .memory = true });
    return &selected.frame;
}
