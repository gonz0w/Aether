# SPDX-License-Identifier: BSD-2-Clause
"""Corruption checks for actual-musl service-scale clock observations."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from service_libc_clock_smoke import check_trace, adapt, adapt_heap, check_heap_object, INPUT, suite


class ServiceLibcClockTests(unittest.TestCase):
    def test_long_profile_rejects_unsupported_composition_before_build(self):
        for options in ({'long_waits': True, 'openzfs': True},
                        {'long_waits': True, 'arc': True},
                        {'long_waits': True, 'case': 'broadcast'},
                        {'long_waits': True, 'case': ''}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                suite('missing', 'missing', **options)

    def long_trace(self, stopped=False, mode=0):
        serial = self.trace(mode, stopped)
        # Add a second native park per completed worker; the original short
        # condition cohort and its retry deadline remain unchanged.
        for owner, workers in ((0, 82 if stopped else 164), (1, 2)):
            for i in range(workers):
                until = 3000000 + i
                serial += (f'NATIVE CLOCK park task={owner} start=2000000 deadline={until}\n'
                           f'NATIVE CLOCK timeout task={owner} now={until+1000} elapsed=100000\n')
        if stopped:
            # The stopped cohort entered long sleeps after its condition phase;
            # intermediate expiry and live repark precede owner teardown.
            for i in range(82):
                serial += f'NATIVE CLOCK park task=0 start=2000000 deadline={4000000+i}\n'
        return serial

    def test_long_sleep_counts_keep_cohorts_and_cleanup_oracles(self):
        for stopped, mode in ((False, 0), (False, 1), (True, 0)):
            serial = self.long_trace(stopped, mode)
            check_trace(serial, mode, stopped, long_waits=True)
            for old, new, message in (
                    ('reclaimed=3', 'reclaimed=0', 'cleanup'),
                    ('remaining=8172', 'remaining=8171', 'backing accounting'),
                    ('deadline=1000000\n', 'deadline=1000001\n', 'cohort deadline')):
                with self.subTest(stopped=stopped, old=old), self.assertRaisesRegex(RuntimeError, message):
                    check_trace(serial.replace(old, new, 1), mode, stopped, long_waits=True)
        with self.assertRaisesRegex(RuntimeError, 'condition/sleep parks'):
            check_trace(self.trace(), long_waits=True)

    def trace(self, mode=0, stopped=False):
        lines = []
        for owner, generation, workers in ((0, 1, 82), (1, 1, 2), (0, 2, 82)):
            total = 8192 if owner == 0 else 128
            deadline = 1000000 * (generation + owner)
            lines.append(f'NATIVE MEMORY admitted slot={owner} generation={generation} used=20 remaining={total-20}')
            for _ in range(workers * (1 + (mode == 1))):
                lines.append(f'NATIVE CLOCK park task={owner} start=1000 deadline={deadline}')
            stopped_now = stopped and owner == 0 and generation == 1
            if not stopped_now:
                if mode != 2:
                    for _ in range(workers):
                        lines.append(f'NATIVE CLOCK timeout task={owner} now={deadline+1000} elapsed=100000')
                for i in range(workers):
                    until = deadline + 100000 + i
                    lines.append(f'NATIVE CLOCK park task={owner} start={deadline+1000} deadline={until}')
                    lines.append(f'NATIVE CLOCK timeout task={owner} now={until+1000} elapsed=100000')
            detail = 143 if stopped_now else 0x100000 | (66 if owner == 0 else 34) | (2 << 8)
            if not stopped_now:
                lines.append(f'NATIVE terminal slot={owner} generation={generation} kind=1 detail={detail}')
        lines += ['NATIVE CLOCK workers scans=100 max_contexts=89 max_ns=14000000 valid=1',
                  'NATIVE supervisor result=100 reclaimed=3']
        return '\n'.join(lines) + '\n'

    def test_full_cohorts_and_interleaved_expiration(self):
        for mode in range(3):
            with self.subTest(mode=mode):
                self.assertEqual(check_trace(self.trace(mode), mode)['parks'], 498 if mode == 1 else 332)
        self.assertEqual(check_trace(self.trace(stopped=True), stopped=True)['parks'], 250)
        # Wake scans may settle a record without a periodic timeout line.
        line = 'NATIVE CLOCK timeout task=0 now=1001000 elapsed=100000\n'
        check_trace(self.trace().replace(line, '', 1))
        # An absolute sleep may be due before its backend enters; no park needed.
        line = 'NATIVE CLOCK park task=0 start=1001000 deadline=1100000\n'
        check_trace(self.trace().replace(line, '', 1))

    def test_missing_condition_registration_or_changed_deadline(self):
        line = 'NATIVE CLOCK park task=0 start=1000 deadline=1000000\n'
        for replacement in ('', line.replace('1000000\n', '1000001\n')):
            with self.subTest(replacement=replacement), self.assertRaisesRegex(RuntimeError, 'cohort deadline'):
                check_trace(self.trace().replace(line, replacement, 1))

    def test_missing_original_deadline_retry(self):
        line = 'NATIVE CLOCK park task=0 start=1000 deadline=1000000\n'
        with self.assertRaisesRegex(RuntimeError, 'cohort deadline'):
            check_trace(self.trace(1).replace(line, '', 1), 1)

    def test_foreign_owner_and_missing_peer_settlements(self):
        for serial in (self.trace() + 'NATIVE CLOCK park task=2 start=1000 deadline=2000000\n',
                       '\n'.join(l for l in self.trace().splitlines() if not l.startswith('NATIVE CLOCK timeout task=1')) + '\n'):
            with self.assertRaisesRegex(RuntimeError, 'foreign clock owner'):
                check_trace(serial)

    def test_early_timeout_and_source_budget(self):
        with self.assertRaisesRegex(RuntimeError, 'early, late'):
            check_trace(self.trace().replace('now=1001000', 'now=999999', 1))
        for old, new in (('valid=1', 'valid=0'), ('max_contexts=89', 'max_contexts=93'),
                         ('max_ns=14000000', 'max_ns=1000000000')):
            with self.subTest(new=new), self.assertRaisesRegex(RuntimeError, 'source/budget'):
                check_trace(self.trace().replace(old, new))

    def test_changed_mapping_backing_or_cleanup(self):
        for old, new, expected in (('detail=1049154', 'detail=1049153', 'pthread mapping'),
                                   ('used=20 remaining=8172', 'used=21 remaining=8172', 'backing accounting'),
                                   ('reclaimed=3', 'reclaimed=0', 'cleanup/replacement')):
            with self.subTest(new=new), self.assertRaisesRegex(RuntimeError, expected):
                check_trace(self.trace().replace(old, new, 1))

    def test_stop_requires_terminal_observation(self):
        with self.assertRaisesRegex(RuntimeError, 'unexpected stopped terminal'):
            check_trace(self.trace(stopped=True) + 'NATIVE terminal slot=0 generation=1 kind=3 detail=143\n', stopped=True)

    def test_changed_or_duplicate_adapter_context_rejected(self):
        source = (INPUT / 'probe.c').read_text()
        for changed in (source.replace('    gate = 1;\n', ''), source + '\n    gate = 1;\n'):
            with self.assertRaisesRegex(RuntimeError, 'insertion context changed'):
                adapt(changed)

    def test_openzfs_extra_waits_still_require_original_cohorts(self):
        serial = self.trace() + ''.join(f'NATIVE CLOCK park task=0 start=2000000 deadline={2100000+i}\n' for i in range(200))
        check_trace(serial, openzfs=True)
        with self.assertRaisesRegex(RuntimeError, 'cohort deadline'):
            check_trace(serial.replace('NATIVE CLOCK park task=0 start=1000 deadline=1000000\n', '', 1), openzfs=True)
        with self.assertRaisesRegex(RuntimeError, 'excessive owner-specific'):
            check_trace(self.trace() + 'NATIVE CLOCK park task=1 start=1000 deadline=2000000\n' * 100, openzfs=True)

    def test_heap_observations_require_owner_budget_and_full_result(self):
        import re
        def encoded(match):
            detail = int(match[1])
            values = (2745, 1713, 1720) if detail & 255 == 66 else (34, 25, 28)
            return 'detail=' + str(detail | sum(v << s for v, s in zip(values, (24, 37, 50))))
        serial = re.sub(r'detail=([0-9]+)', encoded, self.trace())
        observed = check_trace(serial, heap=True)['heap_observations']
        self.assertEqual([r['probe_peak_pages'] for r in observed], [1032, 9, 1032])
        for bad in (self.trace(), serial.replace('kind=1', 'kind=3', 1)):
            with self.assertRaises(RuntimeError):
                check_trace(bad, heap=True)
        # A peer cannot claim the service's available backing.
        bad = re.sub(r'(slot=1 generation=1 kind=1 detail=)[0-9]+',
                     lambda m: m[1] + str(0x100222 | (2745 << 24) | (1713 << 37) | (1720 << 50)), serial)
        with self.assertRaisesRegex(RuntimeError, 'heap backing'):
            check_trace(bad, heap=True)

    def test_heap_adapter_rejects_changed_inputs(self):
        source = adapt((INPUT / 'probe.c').read_text())[0]
        supervisor = (INPUT / 'supervisor.rs').read_text()
        adapted, _, _ = adapt_heap(source, supervisor)
        # A 64-bit diagnostic exits through the raw native operation, never
        # through int main's truncating C return value.
        self.assertIn('memtrap(0x10000 + 231, 0x100000', adapted)
        for changed in (source.replace('    free(heap);\n', ''), source + '\n    free(heap);\n'):
            with self.assertRaisesRegex(RuntimeError, 'heap fixture insertion'):
                adapt_heap(changed, supervisor)

    def test_optimized_heap_probe_cannot_omit_denied_calls(self):
        text = ''.join(('R_X86_64_PLT32 ' + name + '-0x4\n') * count
                       for name, count in {'malloc': 3, 'calloc': 2, 'posix_memalign': 2, 'free': 11}.items())
        text += '$0x4000000\n' * 3
        self.assertEqual(check_heap_object(text)['malloc'], 3)
        for bad in (text.replace('R_X86_64_PLT32 malloc-0x4\n', '', 1),
                    text.replace('$0x4000000\n', '', 1),
                    'R_X86_64_PLT32 calloc-0x4\nR_X86_64_PLT32 free-0x4\n'):
            with self.assertRaisesRegex(RuntimeError, 'lost required allocation calls'):
                check_heap_object(bad)
