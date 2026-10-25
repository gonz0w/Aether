const std = @import("std");
const limine = @import("limine.zig");
const framebuffer = @import("framebuffer.zig");
const serial = @import("arch/x86_64/serial.zig");

export var requests_start: [4]u64 align(8) linksection(".limine_requests_start") = .{ 0xf6b8f4b39de7d1ae, 0xfab91a6940fcb9cf, 0x785c6ed015d3e316, 0x181e920a7852b9d9 };
export var base_revision: [3]u64 align(8) linksection(".limine_requests") = .{ 0xf9562b2d5c95a6c8, 0x6a7b384944536bdc, 6 };
export var framebuffer_request: limine.Request(limine.FramebufferResponse) align(8) linksection(".limine_requests") = .{ .id = limine.id(0x9d5827dcd881dd75, 0xa3148604f6fab11b) };
export var memory_request: limine.Request(limine.MemoryResponse) align(8) linksection(".limine_requests") = .{ .id = limine.id(0x67cf3d9d378a806f, 0xe304acdfc50c3c62) };
export var hhdm_request: limine.Request(limine.HhdmResponse) align(8) linksection(".limine_requests") = .{ .id = limine.id(0x48dcf1cb8ad2b852, 0x63984e959a98244b) };
export var address_request: limine.Request(limine.ExecutableAddressResponse) align(8) linksection(".limine_requests") = .{ .id = limine.id(0x71ba76863cc55f63, 0xb2644a48c516a487) };
export var module_request: limine.Request(limine.ModuleResponse) align(8) linksection(".limine_requests") = .{ .id = limine.id(0x3e7e279702be32af, 0xca1c4f3bd1280cee) };
export var requests_end: [2]u64 align(8) linksection(".limine_requests_end") = .{ 0xadc0e0531bb10d03, 0x9572709f31764c62 };

pub const panic = std.debug.FullPanic(panicImpl);
fn panicImpl(message: []const u8, return_address: ?usize) noreturn {
    if (@import("build_options").native_fs_owner_stack) {
        if (return_address) |address| {
            var site: [64]u8 = undefined;
            serial.write(std.fmt.bufPrint(&site, "NATIVE PANIC pc={x}\n", .{address}) catch "NATIVE PANIC pc=unavailable\n");
        }
    }
    serial.write("AETHER PANIC: ");
    serial.write(message);
    serial.write("\n");
    serial.halt();
}
fn log(comptime format: []const u8, args: anytype) void {
    var buffer: [256]u8 = undefined;
    serial.write(std.fmt.bufPrint(&buffer, format, args) catch "log formatting failed\n");
}

export fn _start() callconv(.c) noreturn {
    serial.init();
    serial.write("\nAETHER M1: entered x86_64 kernel\n");
    const revision: *volatile [3]u64 = &base_revision;
    if (revision[2] != 0) @panic("unsupported Limine base revision");
    if (@import("build_options").panic_test) @panic("intentional boot test");

    const mem_request: *volatile limine.Request(limine.MemoryResponse) = &memory_request;
    const memory = mem_request.response orelse @panic("missing memory map");
    if (memory.count == 0 or memory.count > 4096) @panic("invalid memory map count");
    const entries = memory.entries orelse @panic("missing memory map entries");
    var usable: u64 = 0;
    for (entries[0..@intCast(memory.count)]) |entry| {
        _ = std.math.add(u64, entry.base, entry.length) catch @panic("memory map range overflow");
        log("MEM base=0x{x} length=0x{x} type={d}\n", .{ entry.base, entry.length, entry.kind });
        if (entry.kind == 0) usable = std.math.add(u64, usable, entry.length) catch @panic("usable memory overflow");
    }
    // No allocator or reclaim yet: every boot region remains untouched.
    log("MEM entries={d} usable={d} bytes; no memory reclaimed\n", .{ memory.count, usable });
    const fb_request: *volatile limine.Request(limine.FramebufferResponse) = &framebuffer_request;
    const response = fb_request.response orelse @panic("missing framebuffer response");
    if (response.count == 0) @panic("no framebuffer");
    const buffers = response.framebuffers orelse @panic("missing framebuffer list");
    const fb = buffers[0];
    const layout = framebuffer.Layout.validate(fb.*) catch |err| @panic(@errorName(err));
    log("FB width={d} height={d} pitch={d} bpp={d} masks={d},{d},{d}\n", .{ fb.width, fb.height, fb.pitch, fb.bpp, layout.red, layout.green, layout.blue });
    if (!@import("build_options").smp_test) framebuffer.draw(@ptrCast(@alignCast(fb.address.?)), layout);
    serial.write("AETHER M1 PASS\n");
    const hr: *volatile limine.Request(limine.HhdmResponse) = &hhdm_request;
    const ar: *volatile limine.Request(limine.ExecutableAddressResponse) = &address_request;
    const mr: *volatile limine.Request(limine.ModuleResponse) = &module_request;
    const hhdm = hr.response orelse @panic("missing HHDM");
    const address = ar.response orelse @panic("missing executable address");
    if (@import("build_options").backing_test) @import("arch/x86_64/backing_probe.zig").experiment(hhdm.offset, memory, address.physical_base, address.virtual_base, @enumFromInt(@intFromEnum(@import("build_options").backing_mode)));
    if (@import("build_options").entropy_test) @import("arch/x86_64/entropy.zig").experiment(address.physical_base, address.virtual_base, @enumFromInt(@intFromEnum(@import("build_options").entropy_mode)));
    if (@import("build_options").block_test) @import("arch/x86_64/block.zig").experiment(address.physical_base, address.virtual_base, @import("build_options").block_verify);
    const modules = mr.response orelse @panic("missing Rust module");
    if (@import("build_options").native_c_test) {
        if (modules.count != 5) @panic("native C requires explicit fifth module");
        const native = (modules.modules orelse @panic("missing modules"))[4];
        if (native.size > (if (@import("build_options").native_image_large) @as(u64, 8 * 1024 * 1024 + 4096 + 48) else 3 * 1024 * 1024 + 8192 + 80)) @panic("native envelope oversized");
        const content = native.address orelse @panic("missing native envelope");
        @import("arch/x86_64/native_c.zig").start(address.physical_base, address.virtual_base, content[0..@intCast(native.size)], hhdm.offset, memory);
    }
    if (modules.count != 4) @panic("expected protection, display, lifecycle and SMP supervisor modules");
    if (@import("build_options").smp_test) @import("arch/x86_64/display.zig").capture(fb.*, layout, hhdm.offset, memory, modules.modules.?[1], modules.modules.?[3]);
    const module = (modules.modules orelse @panic("missing module list"))[0];
    if (module.size == 0 or module.size > 4096) @panic("invalid Rust module size");
    const bytes = module.address orelse @panic("missing Rust image");
    const supervisor = modules.modules.?[2];
    if (supervisor.size < 33 or supervisor.size > 4128) @panic("invalid lifecycle module length");
    const supervisor_bytes = supervisor.address orelse @panic("missing lifecycle module");
    @import("arch/x86_64/protection.zig").start(hhdm.offset, address.physical_base, address.virtual_base, bytes[0..@intCast(module.size)], supervisor_bytes[0..@intCast(supervisor.size)]);
}
