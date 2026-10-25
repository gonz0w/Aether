const life = @import("../../remote_lifetime.zig");
const cross = @import("../../cross_core.zig");
const stream = @import("display_stream.zig");
const user_cpu = @import("user_cpu.zig");
const Frame = @import("context.zig").Frame;
const limine = @import("../../limine.zig");
var image: [4096]u8 align(4096) = @splat(0);
var image_len: usize = 0;
// All fields are BSP-owned. The AP is accessed only through stream transport.
pub var runtime: user_cpu.State = .{};
pub var link = cross.Table.display(true);
pub var done = false;
pub const binding: u64 = @as(u64, 9) << 32;
var generation: u32 = 1;
var invalid: u64 = 0;
var denied: u64 = 0;
var framebuffer_denied = false;
var device_denied: u64 = 0;
var data_denied: u64 = 0;
var discarded_generation: u32 = 0;
var discarded_results: u64 = 0;
var replacing = false;
pub fn capture(module: *const limine.File) void {
    if (module.size == 0 or module.size > image.len) @panic("invalid SMP supervisor image");
    const bytes = module.address orelse @panic("missing SMP supervisor image");
    image_len = @intCast(module.size);
    @memcpy(image[0..image_len], bytes[0..image_len]);
}
pub fn prepare(inputs: user_cpu.Inputs) void {
    var local = inputs;
    local.image = image[0..image_len];
    runtime.prepare(local, 0);
    runtime.frame.rdi = life.handle(1, false);
}
pub fn exception(frame: *const Frame) *const Frame {
    if (frame.cs != 0x23 or !runtime.runnable) @panic("SMP supervisor kernel fault");
    runtime.frame = frame.*;
    const result = &runtime.frame;
    if (frame.vector == 32 or frame.vector == 255) return result;
    if (frame.vector == 14) {
        const address = asm volatile ("mov %%cr2, %[value]"
            : [value] "=r" (-> u64),
        );
        if (framebuffer_denied or address != 0x02000000 or frame.rax != address or frame.error_code != 4)
            @panic("SMP supervisor fault; resources reserved");
        framebuffer_denied = true;
        result.rip += 3;
        return result;
    }
    if (frame.vector != 128) @panic("SMP supervisor fault; resources reserved");
    result.rdx = 0;
    result.rax = 0;
    if (frame.rax == 20) return result;
    if (frame.rax == 40) {
        device_denied += 1;
        result.rax = 1;
        return result;
    }
    if (frame.rax == 1) {
        data_denied += 1;
        result.rax = 1;
        return result;
    }
    if (frame.rax == 0) {
        if (frame.rdi != 0 or generation != life.generation_limit or invalid != 5 or denied != 6 or !framebuffer_denied or device_denied != 1 or data_denied != 1 or discarded_results != 4 or discarded_generation != life.generation_limit or !stream.finished())
            @panic("SMP supervisor checks failed");
        done = true;
        runtime.runnable = false;
        return result;
    }
    if ((frame.rax < 50 or frame.rax > 53) and frame.rax != 56 and frame.rax != 57) {
        result.rax = 1;
        return result;
    }
    life.requireHandle(frame.rdi, generation, frame.rax != 51 and frame.rax != 57) catch |err| {
        if (err == error.Invalid) {
            invalid += 1;
            result.rax = 1;
        } else {
            denied += 1;
            result.rax = 2;
        }
        return result;
    };
    const word = stream.snapshot();
    if (word == 0) {
        result.rax = 6;
        return result;
    }
    const observed_generation: u32 = @intCast(word >> 32);
    if (frame.rax == 51) {
        if (observed_generation != generation) {
            if (observed_generation != generation + 1) @panic("remote generation jump");
            generation = observed_generation;
            replacing = false;
            link.namespace += @as(u64, 2) << 32;
            link.live = true;
        }
        if (@as(u32, @truncate(word)) >= 3) link.live = false;
        result.rdx = word;
        return result;
    }
    if (frame.rax == 57) {
        const phase: u32 = @truncate(word);
        if (replacing or observed_generation != generation or (phase != 3 and phase != 4)) {
            result.rax = 6;
            return result;
        }
        result.rdx = stream.terminal();
        return result;
    }
    if (frame.rax == 56) {
        if (word != (@as(u64, generation) << 32 | 3) or discarded_generation == generation) {
            result.rax = 6;
            return result;
        }
        if (link.live) @panic("discard while BSP data access active");
        const counts = stream.discard();
        discarded_generation = generation;
        discarded_results += counts & 0xffffffff;
        result.rdx = counts;
        return result;
    }
    const observed = life.Owner{ .generation = observed_generation, .phase = @enumFromInt(@as(u32, @truncate(word))) };
    observed.require(generation, frame.rax) catch |err| {
        result.rax = if (err == error.Busy) 6 else if (err == error.Exhausted) 3 else 1;
        return result;
    };
    if (frame.rax == 52 and discarded_generation != generation) {
        result.rax = 6;
        return result;
    }
    const accepted = stream.request(frame.rax, generation);
    if (accepted and frame.rax == 50) link.live = false;
    if (accepted and frame.rax == 53) replacing = true;
    result.rax = if (accepted) 0 else 6;
    return result;
}
