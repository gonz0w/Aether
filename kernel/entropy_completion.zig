// SPDX-License-Identifier: BSD-2-Clause
const std = @import("std");
pub const Failure = error{ Index, Head, Length };
// Single outstanding descriptor0, at most256 bytes. No DMA access here.
pub fn validate(sequence: u16, index: u16, head: u32, written: u32, requested: usize) Failure!usize {
    if (index != sequence +% 1) return error.Index;
    if (head != 0) return error.Head;
    if (requested == 0 or requested > 256 or written == 0 or written > requested) return error.Length;
    return @intCast(written);
}
test "partial, exact and sequence wrap" {
    try std.testing.expectEqual(@as(usize, 1), try validate(0, 1, 0, 1, 256));
    try std.testing.expectEqual(@as(usize, 256), try validate(65535, 0, 0, 256, 256));
}
test "reject skipped/repeated index, foreign head and invalid lengths" {
    try std.testing.expectError(error.Index, validate(65535, 1, 0, 16, 16));
    try std.testing.expectError(error.Index, validate(4, 4, 0, 16, 16));
    try std.testing.expectError(error.Head, validate(4, 5, 1, 16, 16));
    try std.testing.expectError(error.Length, validate(4, 5, 0, 0, 16));
    try std.testing.expectError(error.Length, validate(4, 5, 0, 17, 16));
    try std.testing.expectError(error.Length, validate(4, 5, 0, 1, 0));
    try std.testing.expectError(error.Length, validate(4, 5, 0, 257, 257));
}
