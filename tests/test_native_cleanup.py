# SPDX-License-Identifier: BSD-2-Clause
"""Actual cleanup bodies over small host scaffolding; no native timing claim."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from service_runtime_smoke import check_pool_cleanup_trace


def block(source, anchor):
    start = source.index(anchor)
    opening = source.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


class NativeCleanup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='aether-cleanup-host-')
        cls.addClassCleanup(cls.temporary.cleanup)
        out = Path(cls.temporary.name)
        native = (ROOT / 'kernel/arch/x86_64/native_c.zig').read_text()
        formatter = block(native, 'fn nativeCleanupTrace(')
        finish = block(native, 'fn finish(')
        tail = finish[finish.index('    stopContexts(s);'):]
        tail = tail[:tail.index('    if (!states[1 - active].terminal)')]
        reclaim = block(native, '        0x20002 => {')
        scaffold = '''const std = @import("std");
const options = @import("build_options");
const Frame = struct {};
const Reset = struct {
    value: u8 = 9,
    fn reset(s: *@This()) void { s.value = 0; }
};
const State = struct {
    root: [1]u64 = .{7},
    backing: [2][4096]u8 align(4096) = @splat(@splat(165)),
    records_storage: [2]struct { value: u64 = 0 } = @splat(.{ .value = 9 }),
    children: [2]Reset = @splat(.{}),
    execution: Reset = .{},
    terminal: bool = true,
    admitted: bool = true,
    count: usize = 2,
    generation: u64 = 1,
    fn payload(s: *@This()) *align(4096) [2][4096]u8 { return &s.backing; }
    fn records(s: *@This()) *@TypeOf(s.records_storage) { return &s.records_storage; }
    fn childRecords(s: *@This()) []Reset { return &s.children; }
};
var states: [3]State = @splat(.{});
var active: usize = 0;
var reclaimed: usize = 0;
var response: i64 = 99;
var stopped: bool = false;
var notified: bool = false;
var detached: bool = false;
var frame: Frame = .{};
const supervised = true;
const serial = struct { fn write(s: []const u8) void { std.debug.print("{s}", .{s}); } };
fn require(ok: bool) void {
    if (!ok) {
        std.debug.print("HOST CLEANUP invariant rejected\\n", .{});
        std.process.exit(91);
    }
}
fn stopContexts(_: *State) void { stopped = true; }
fn notifyParent(_: *State) void { require(stopped); notified = true; }
fn rotate() void { require(stopped and notified); active = 2; }
fn select() *const Frame { return &frame; }
fn aliases(s: *State, detach: bool) void {
    require(s.root[0] == 0 and detach and s.admitted and s.terminal);
    detached = true;
}
fn publishSustained() void { require(!states[0].admitted and reclaimed == 1); }
fn result(_: *State, value: i64) void { response = value; }
'''
        source = scaffold + formatter + '\nfn finishTail() *const Frame {\nconst s = &states[0];\n' + tail
        source += 'return select();\n}\nfn reclaim() *const Frame {\n'
        source += 'const slot: usize = 0; const s = &states[slot]; const caller = &states[2];\n'
        source += 'switch (@as(u64, 0x20002)) {\n' + reclaim + ',\nelse => unreachable,\n}\nreturn select();\n}\n'
        source += '''pub fn main() void {
    if (options.live) {
        states[0].terminal = false;
        _ = reclaim();
        require(response == -16 and reclaimed == 0 and !detached);
        require(states[0].admitted and states[0].root[0] == 7);
        for (states[0].backing) |page| for (page) |value| require(value == 165);
    } else {
        _ = finishTail();
        _ = reclaim();
        require(stopped and notified and active == 2 and detached);
        require(response == 0 and reclaimed == 1 and !states[0].admitted);
        require(states[0].count == 0 and states[0].execution.value == 0);
        for (states[0].backing) |page| for (page) |value| require(value == 0);
        for (states[0].records_storage) |record| require(record.value == 0);
        for (states[0].children) |child| require(child.value == 0);
    }
    std.debug.print("HOST CLEANUP PASS\\n", .{});
}
'''
        cls.binaries = {}
        for mode in ('trace', 'disabled', 'live', 'dirty', 'dirty-last'):
            path = out / (mode + '.zig')
            text = source
            if mode in ('dirty', 'dirty-last'):
                anchor = '            for (s.payload()) |*page| require(std.mem.allEqual(u64, std.mem.bytesAsSlice(u64, page), 0));'
                if text.count(anchor) != 1:
                    raise AssertionError('actual reclaim verification context changed')
                dirty = '[0][0]' if mode == 'dirty' else '[1][4095]'
                text = text.replace(anchor, f'            s.payload(){dirty} = 128;\n' + anchor)
            path.write_text(text)
            opts = out / (mode + '-options.zig')
            opts.write_text(f'pub const native_service_cleanup_trace = {str(mode != "disabled").lower()};\n'
                            'pub const native_skip_zero = false;\npub const native_signal_actions = false;\n'
                            f'pub const live = {str(mode == "live").lower()};\n')
            binary = out / mode
            command = ['zig', 'build-exe', '--dep', 'build_options', '-Mroot=' + str(path),
                       '-Mbuild_options=' + str(opts), '-femit-bin=' + str(binary),
                       '--cache-dir', str(out/'cache'), '--global-cache-dir', str(ROOT/'.zig-cache/global')]
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            if result.returncode:
                raise AssertionError(result.stderr)
            cls.binaries[mode] = binary

        # Actual verification expression; every byte offset covers word/page edges.
        verification = 'for (s.payload()) |*page| require(std.mem.allEqual(u64, std.mem.bytesAsSlice(u64, page), 0));'
        if native.count(verification) != 1:
            raise AssertionError('actual full backing verification context changed')
        expression = verification.replace('require(', 'if (!(').replace('));', '))) return false;')
        for mode in ('coverage', 'omit-last-word', 'omit-last-page'):
            check = expression
            if mode == 'omit-last-word':
                check = check.replace('std.mem.bytesAsSlice(u64, page)', 'std.mem.bytesAsSlice(u64, page)[0..511]')
            if mode == 'omit-last-page':
                check = check.replace('s.payload()', 's.payload()[0..1]')
            text = scaffold + 'fn checked(s: *State) bool { ' + check + ' return true; }\n'
            text += '''pub fn main() void {
    const s = &states[0];
    @memset(std.mem.asBytes(&s.backing), 0);
    require(checked(s));
    for (0..8192) |offset| {
        for ([_]u8{1, 128}) |dirty| {
            s.backing[offset / 4096][offset % 4096] = dirty;
            if (checked(s)) {
                std.debug.print("HOST CLEANUP coverage rejected offset={d}\\n", .{offset});
                std.process.exit(91);
            }
            s.backing[offset / 4096][offset % 4096] = 0;
        }
    }
    require(checked(s));
    std.debug.print("HOST CLEANUP coverage PASS\\n", .{});
}
'''
            path = out / (mode + '.zig')
            path.write_text(text)
            binary = out / mode
            command = ['zig', 'build-exe', '--dep', 'build_options', '-Mroot=' + str(path),
                       '-Mbuild_options=' + str(out/'trace-options.zig'), '-femit-bin=' + str(binary),
                       '--cache-dir', str(out/'cache'), '--global-cache-dir', str(ROOT/'.zig-cache/global')]
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            if result.returncode:
                raise AssertionError(result.stderr)
            cls.binaries[mode] = binary

    def run_mode(self, mode):
        return subprocess.run([str(self.binaries[mode])], capture_output=True, text=True, timeout=5)

    def test_actual_stop_select_and_reclaim_order_and_complete_reset(self):
        result = self.run_mode('trace')
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [line for line in result.stderr.splitlines() if line.startswith('NATIVE CLEANUP ')]
        self.assertEqual(rows, [f'NATIVE CLEANUP v=1 slot=0 generation=1 phase={phase} '
                              f'selected={0 if phase == 1 else 2} pages=2 reclaimed={int(phase == 7)}'
                              for phase in range(1, 8)])

    def test_disabled_trace_preserves_cleanup_without_output(self):
        result = self.run_mode('disabled')
        self.assertEqual((result.returncode, result.stderr), (0, 'HOST CLEANUP PASS\n'))

    def test_live_owner_is_denied_before_detach_zero_or_trace(self):
        result = self.run_mode('live')
        self.assertEqual((result.returncode, result.stderr), (0, 'HOST CLEANUP PASS\n'))

    def test_dirty_backing_rejects_before_verified_or_reclaimed_markers(self):
        for mode in ('dirty', 'dirty-last'):
            result = self.run_mode(mode)
            self.assertEqual(result.returncode, 91, result.stderr)
            self.assertIn('HOST CLEANUP invariant rejected\n', result.stderr)
            self.assertIn('phase=5 ', result.stderr)
            self.assertNotIn('phase=6 ', result.stderr)
            self.assertNotIn('phase=7 ', result.stderr)

    def test_complete_word_scan_rejects_every_byte_and_truncated_scans(self):
        result = self.run_mode('coverage')
        self.assertEqual((result.returncode, result.stderr), (0, 'HOST CLEANUP coverage PASS\n'))
        for mode, offset in [('omit-last-word', 4088), ('omit-last-page', 4096)]:
            result = self.run_mode(mode)
            self.assertEqual(result.returncode, 91, result.stderr)
            self.assertIn(f'HOST CLEANUP coverage rejected offset={offset}\n', result.stderr)

    def test_native_oracle_rejects_partial_reordered_foreign_or_false_reclaim(self):
        lines = []
        for generation in (1, 2, 3):
            lines.append(f'NATIVE terminal slot=0 generation={generation} kind=1 detail=0')
            lines.extend(f'NATIVE CLEANUP v=1 slot=0 generation={generation} phase={phase} '
                         f'selected={0 if phase == 1 else 2} pages=8192 '
                         f'reclaimed={generation if phase == 7 else generation-1}'
                         for phase in range(1, 8))
        lines.append('NATIVE supervisor result=100 reclaimed=3')
        serial = '\n'.join(lines) + '\n'
        self.assertEqual(check_pool_cleanup_trace(serial)['cleanup_trace_version'], 1)
        broken = [serial.replace('phase=5 ', 'phase=4 ', 1), serial.replace('slot=0', 'slot=1', 1),
                  serial.replace('pages=8192', 'pages=128', 1), serial.replace('v=1', 'v=2', 1),
                  '\n'.join(lines[:-1])+'\n', serial.replace('reclaimed=1', 'reclaimed=0', 1),
                  '\n'.join(lines[1:])+'\n', serial + lines[1]+'\n']
        reordered = lines.copy()
        reordered[8], reordered[7] = reordered[7], reordered[8]
        broken.append('\n'.join(reordered)+'\n')
        for changed in broken:
            with self.assertRaisesRegex(ValueError, 'pool cleanup v1'):
                check_pool_cleanup_trace(changed)
