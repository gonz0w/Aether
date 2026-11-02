// SPDX-License-Identifier: BSD-2-Clause
// Selected console query only. UART observation follows complete scalar authority checks.
const std = @import("std");

pub fn selectedOperation(console: bool, handoff: bool, selected: bool, operation: u64) bool {
    return console and ((operation >= 0x26000 and operation <= (if (handoff) @as(u64, 0x26003) else 0x26002)) or
        (selected and operation == 0x26004));
}

pub const Guard = struct {
    selected: bool,
    owns: bool,
    closed: bool,
    grant: u64,
    arguments: [5]u64,
};

pub fn query(guard: Guard, uart: anytype) i64 {
    if (!guard.selected) return -38;
    for (guard.arguments) |argument| if (argument != 0) return -22;
    if (!guard.owns or guard.grant != 0xf001) return -13;
    if (guard.closed) return -9;
    return uart.transmitterEmpty();
}

test "selected query never broadens legacy handoff dispatch" {
    for ([_]bool{ false, true }) |console| for ([_]bool{ false, true }) |handoff| for ([_]bool{ false, true }) |selected| {
        for ([_]u64{ 0x25fff, 0x26000, 0x26001, 0x26002, 0x26003, 0x26004, 0x26005 }) |operation| {
            const expected = console and switch (operation) {
                0x26000...0x26002 => true,
                0x26003 => handoff,
                0x26004 => selected,
                else => false,
            };
            try std.testing.expectEqual(expected, selectedOperation(console, handoff, selected, operation));
        }
    };
}

test "query denials precede observation and valid queries observe exactly once" {
    const Uart = struct {
        calls: usize = 0,
        answer: i64 = -11,
        fn transmitterEmpty(self: *@This()) i64 {
            self.calls += 1;
            return self.answer;
        }
    };
    const valid: Guard = .{ .selected = true, .owns = true, .closed = false, .grant = 0xf001, .arguments = @splat(0) };
    var uart: Uart = .{};
    for (0..9) |bad| {
        var guard = valid;
        const expected: i64 = switch (bad) {
            0 => blk: {
                guard.selected = false;
                break :blk -38;
            },
            1 => blk: {
                guard.owns = false;
                break :blk -13;
            },
            2 => blk: {
                guard.closed = true;
                break :blk -9;
            },
            3 => blk: {
                guard.grant = 0;
                break :blk -13;
            },
            else => blk: {
                guard.arguments[bad - 4] = 1;
                break :blk -22;
            },
        };
        try std.testing.expectEqual(expected, query(guard, &uart));
        try std.testing.expectEqual(@as(usize, 0), uart.calls);
    }
    for ([_]i64{ -11, 0, -5 }) |answer| {
        uart.answer = answer;
        const before = uart.calls;
        try std.testing.expectEqual(answer, query(valid, &uart));
        try std.testing.expectEqual(before + 1, uart.calls);
    }
}
