// SPDX-License-Identifier: BSD-2-Clause
const std = @import("std");
pub const Failure = error{ Denied, Closed, Invalid, Exhausted };
pub const Grant = struct {
    selector: u64 = 0,
    remaining: usize = 4096,
    closed: bool = false,
    pub fn check(self: *const Grant, selector: u64) Failure!void {
        if (self.selector == 0 or selector != self.selector) return error.Denied;
        if (self.closed) return error.Closed;
    }
    pub fn prepare(self: *const Grant, selector: u64, count: usize) Failure!void {
        try self.check(selector);
        if (count == 0 or count > 256) return error.Invalid;
        if (count > self.remaining) return error.Exhausted;
    }
    // Called only after full span validation and completed copied draw.
    pub fn complete(self: *Grant, count: usize) void {
        std.debug.assert(count > 0 and count <= 256 and count <= self.remaining and !self.closed);
        self.remaining -= count;
    }
    pub fn close(self: *Grant, selector: u64) Failure!void {
        try self.check(selector);
        self.closed = true;
    }
};
test "bound selector and permanent close; rejected operations preserve quota" {
    var grant = Grant{ .selector = 0x60000101 };
    try std.testing.expectError(error.Denied, grant.prepare(0x60000001, 1));
    try std.testing.expectError(error.Denied, grant.prepare(0x60000102, 1));
    try std.testing.expectError(error.Invalid, grant.prepare(grant.selector, 257));
    try std.testing.expectEqual(@as(usize, 4096), grant.remaining);
    try grant.close(grant.selector);
    try std.testing.expectError(error.Closed, grant.prepare(grant.selector, 1));
    try std.testing.expectError(error.Closed, grant.close(grant.selector));
}
test "only completed draws consume quota; default is unbound" {
    var grant = Grant{ .selector = 1 };
    for (0..16) |_| {
        try grant.prepare(1, 256);
        grant.complete(256);
    }
    try std.testing.expectError(error.Exhausted, grant.prepare(1, 1));
    try std.testing.expectEqual(@as(usize, 0), grant.remaining);
    try std.testing.expectError(error.Denied, (Grant{}).check(1));
}
