// Minimal ABI declarations from the Limine protocol at
// 617369cb577108e483c096e373c4f2ecc9d2081d (see boot/DEPENDENCIES.md).
// Only response revision 0 framebuffer fields are consumed.
pub fn Request(comptime Response: type) type {
    return extern struct {
        id: [4]u64,
        revision: u64 = 0,
        response: ?*const Response = null,
    };
}

pub fn id(a: u64, b: u64) [4]u64 {
    return .{ 0xc7b1dd30df4c8b88, 0x0a82e883a194f07b, a, b };
}

pub const Framebuffer = extern struct {
    address: ?[*]u8,
    width: u64,
    height: u64,
    pitch: u64,
    bpp: u16,
    memory_model: u8,
    red_mask_size: u8,
    red_mask_shift: u8,
    green_mask_size: u8,
    green_mask_shift: u8,
    blue_mask_size: u8,
    blue_mask_shift: u8,
    unused: [7]u8 = @splat(0),
    edid_size: u64 = 0,
    edid: ?*const anyopaque = null,
};
pub const FramebufferResponse = extern struct {
    revision: u64,
    count: u64,
    framebuffers: ?[*]const *const Framebuffer,
};
pub const MemoryEntry = extern struct { base: u64, length: u64, kind: u64 };
pub const MemoryResponse = extern struct {
    revision: u64,
    count: u64,
    entries: ?[*]const *const MemoryEntry,
};

comptime {
    if (@sizeOf(Framebuffer) != 64 or @offsetOf(Framebuffer, "edid_size") != 48)
        @compileError("Limine framebuffer ABI mismatch");
    if (@sizeOf(Request(FramebufferResponse)) != 48)
        @compileError("Limine request ABI mismatch");
}

pub const HhdmResponse = extern struct { revision: u64, offset: u64 };
pub const ExecutableAddressResponse = extern struct { revision: u64, physical_base: u64, virtual_base: u64 };
// Only the initial revision-0 fields of limine_file are consumed.
pub const File = extern struct { revision: u64, address: ?[*]const u8, size: u64 };
pub const ModuleResponse = extern struct { revision: u64, count: u64, modules: ?[*]const *const File };

pub const MpInfo = extern struct {
    processor_id: u32,
    lapic_id: u32,
    reserved: u64,
    goto_address: usize,
    extra_argument: u64,
};
pub const MpResponse = extern struct {
    revision: u64,
    flags: u32,
    bsp_lapic_id: u32,
    count: u64,
    cpus: ?[*]const *MpInfo,
};
pub const MpRequest = extern struct {
    id: [4]u64 = @import("limine.zig").id(0x95a67b819a1b857e, 0xa0b61b723b6a73e0),
    revision: u64 = 0,
    response: ?*const MpResponse = null,
    flags: u64 = 0,
};
comptime {
    if (@sizeOf(MpInfo) != 32 or @offsetOf(MpInfo, "goto_address") != 16 or @sizeOf(MpResponse) != 32 or @sizeOf(MpRequest) != 56)
        @compileError("Limine MP ABI mismatch");
}
