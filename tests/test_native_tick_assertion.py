# SPDX-License-Identifier: BSD-2-Clause
"""Execute the actual tick guard and panic output; no VM timer claim."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from test_native_cleanup import block, af09_prelude, af09_command

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'NATIVE assertion id=tick-budget ticks=3000 limit=3000\n'
PANIC = 'AETHER PANIC: native C profile rejected\n'


class NativeTickAssertion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='aether-tick-assertion-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.output = Path(cls.temporary.name)
        native = (ROOT / 'kernel/arch/x86_64/native_c.zig').read_text()
        tick = block(native, 'fn nativeTick(')
        cls.prefix = tick[:tick.index('    refreshSustained();')] + '}\n'
        cls.limit_declaration = next(line for line in native.splitlines() if line.startswith('const native_tick_limit:'))
        cls.af09 = af09_prelude(native)
        cls.require = block(native, 'fn require(')
        cls.lifecycle = block(native, 'fn lifecycleEnabled(') + '\n' + block(native, 'fn storageLifetime(')
        cls.panic = block((ROOT / 'kernel/main.zig').read_text(), 'fn panicImpl(')

    def run_case(self, name, start=2999, sustained=False, session=False,
                 prefix=None, iterations=1, extended=False, storage=False, combined=False):
        source = '''const std = @import("std");
const serial = struct {
    fn write(text: []const u8) void { std.debug.print("{s}", .{text}); }
    fn halt() noreturn { std.process.exit(93); }
};
pub const panic = std.debug.FullPanic(panicImpl);
'''
        source += (f'var total_ticks: usize = {start};\n'
                   f'const combined_profile = {str(combined).lower()};\n'
                   f'var sustained = {str(sustained).lower()};\n'
                   f'var session_lifecycle = {str(session).lower()};\n')
        source += self.af09
        source += self.limit_declaration + '\n'
        source += self.lifecycle + '\n' + self.require + '\n' + self.panic + '\n'
        source += self.prefix if prefix is None else prefix
        source += ('pub fn main() void {\n'
                   f'for (0..{iterations}) |_| nativeTick();\n'
                   'std.debug.print("HOST TICK CONTINUE ticks={d}\\n", .{total_ticks});\n}\n')
        path = self.output / (name + '.zig')
        path.write_text(source)
        binary = self.output / name
        options = self.output / (name + '-options.zig')
        options.write_text('pub const native_fs_owner_stack = false;\n' + 'pub const native_service_zpl_budget = ' + str(extended).lower() + ';\npub const native_service_lifetime = ' + str(storage).lower() + ';\n')
        command = ['zig', 'build-exe', '-OReleaseSafe', '--dep', 'build_options',
                   '-Mroot=' + str(path), '-Mbuild_options=' + str(options),
                   '-femit-bin=' + str(binary), '--cache-dir', str(self.output / 'cache'),
                   '--global-cache-dir', str(ROOT / '.zig-cache/global')]
        built = subprocess.run(af09_command(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, timeout=180)
        self.assertEqual(built.returncode, 0, built.stdout)
        return subprocess.run(af09_command([str(binary)]), stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, timeout=5)

    @staticmethod
    def assert_budget_rejection(result, limit=3000):
        marker = f'NATIVE assertion id=tick-budget ticks={limit} limit={limit}\n'
        if result.returncode != 93 or result.stdout != marker + PANIC:
            raise AssertionError('exact tick assertion marker before unchanged panic')

    def test_actual_guard_permits2999_and_rejects3000(self):
        ordinary = self.run_case('ordinary', start=2998)
        self.assertEqual((ordinary.returncode, ordinary.stdout),
                         (0, 'HOST TICK CONTINUE ticks=2999\n'))
        self.assert_budget_rejection(self.run_case('boundary'))
        self.assert_budget_rejection(self.run_case('all-ticks', start=0, iterations=3000))

    def test_existing_lifecycle_exemptions_remain(self):
        for name, sustained, session in (('sustained', True, False),
                                         ('session', False, True)):
            with self.subTest(name=name):
                result = self.run_case(name, sustained=sustained, session=session)
                self.assertEqual((result.returncode, result.stdout),
                                 (0, 'HOST TICK CONTINUE ticks=3000\n'))

    def test_combined_session_retains_approved6000_ceiling_despite_lifecycle(self):
        result=self.run_case('combined-before',start=5998,session=True,extended=True,combined=True)
        self.assertEqual((result.returncode,result.stdout),(0,'HOST TICK CONTINUE ticks=5999\n'))
        self.assert_budget_rejection(self.run_case('combined-at',start=5999,session=True,extended=True,combined=True),6000)
        weakened=self.prefix.replace('combined_profile or (!lifecycleEnabled() and !storageLifetime())','!lifecycleEnabled() and !storageLifetime()')
        self.assertNotEqual(weakened,self.prefix)
        result=self.run_case('combined-exemption-omitted',start=5999,session=True,extended=True,combined=True,prefix=weakened)
        self.assertEqual((result.returncode,result.stdout),(0,'HOST TICK CONTINUE ticks=6000\n'))

    def test_checked_counter_overflow_is_distinct(self):
        result = self.run_case('overflow', start='std.math.maxInt(usize)')
        self.assertEqual((result.returncode, result.stdout),
                         (93, 'AETHER PANIC: native clock exhausted\n'))

    def test_compiling_missing_late_marker_and_weakened_guard_fail_named_oracle(self):
        begin = self.prefix.index('        if (total_ticks >= native_tick_limit) {')
        marker = block(self.prefix, '        if (total_ticks >= native_tick_limit) {')
        without = self.prefix[:begin] + self.prefix[begin:].replace(marker + '\n', '', 1)
        guard = '        require(total_ticks < native_tick_limit);'
        self.assertEqual(without.count(guard), 1)
        late = without.replace(guard, guard + '\n' + marker, 1)
        weaker = self.prefix.replace('require(total_ticks < native_tick_limit)',
                                    'require(total_ticks < native_tick_limit + 1)', 1)
        for name, source in (('missing', without), ('late', late), ('weaker', weaker)):
            with self.subTest(name=name):
                result = self.run_case(name, prefix=source)
                with self.assertRaisesRegex(AssertionError, 'exact tick assertion marker'):
                    self.assert_budget_rejection(result)

    def test_explicit_extended_profile_permits5999_and_rejects6000(self):
        ordinary = self.run_case('extended-ordinary', start=5998, extended=True)
        self.assertEqual((ordinary.returncode, ordinary.stdout),
                         (0, 'HOST TICK CONTINUE ticks=5999\n'))
        self.assert_budget_rejection(self.run_case('extended-boundary', start=5999,
                                                   extended=True), limit=6000)
        for name, sustained, session in (('extended-sustained', True, False),
                                         ('extended-session', False, True)):
            result = self.run_case(name, start=5999, sustained=sustained,
                                   session=session, extended=True)
            self.assertEqual((result.returncode, result.stdout),
                             (0, 'HOST TICK CONTINUE ticks=6000\n'))

    def test_separate_storage_lifetime_crosses6000_without_disabling_overflow(self):
        r=self.run_case('storage-life',start=5999,extended=True,storage=True,iterations=6501)
        self.assertEqual((r.returncode,r.stdout),(0,'HOST TICK CONTINUE ticks=12500\n'))
        r=self.run_case('storage-overflow',start='std.math.maxInt(usize)',storage=True)
        self.assertEqual((r.returncode,r.stdout),(93,'AETHER PANIC: native clock exhausted\n'))
