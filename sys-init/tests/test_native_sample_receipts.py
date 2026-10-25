# SPDX-License-Identifier: BSD-2-Clause
"""Host Rust logic coverage; no native syscall or producer qualification."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'terminal_mapping_and_collisions', 'live_is_one_receipt_without_fact',
    'prefix_survives_native_error', 'invalid_booleans_are_local',
    'zero_terminal_revision_rejects_before_status',
    'incoherent_samples_preserve_all_receipts', 'unsupported_pairs_are_local_and_retained',
    'synthetic_interruption_retains_only_received_prefix',
    'signed_revision_and_wide_result_are_not_truncated',
}


class NativeSampleReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = ROOT / 'out/sample-receipts'
        parent.mkdir(parents=True, exist_ok=True)
        cls.work = Path(tempfile.mkdtemp(prefix='run-', dir=parent))
        print('sample receipt artifacts: ' + str(cls.work), file=sys.stderr)
        cls.record = {'schema': 'sys-init-sample-receipts-v1', 'result': 'running', 'checks': {}, 'scope': 'synthetic host Rust logic; native not run', 'commands': [], 'sources': {}}
        for name in ['prototypes/native-supervisor/sample_receipts.rs', 'tests/native_sample_receipts.rs', 'tests/native_pending_history.rs',
                     'prototypes/native-supervisor/pending_history.rs', 'prototypes/native-supervisor/cut_reservation.rs', 'tests/native_cut_reservation.rs',
                     'prototypes/native-supervisor/service_owner.rs', 'tests/native_service_owner.rs',
                     'prototypes/native-supervisor/service_pair.rs', 'tests/native_service_pair.rs',
                     'prototypes/native-supervisor/connection_owner.rs', 'tests/native_connection_owner.rs',
                     'prototypes/native-command/byte_compare.rs', 'tests/native_byte_compare.rs',
                     'tests/test_native_sample_receipts.py', 'scripts/check-all.py']:
            dst = cls.work / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dst)
            cls.record['sources'][name] = hashlib.sha256(dst.read_bytes()).hexdigest()
        cls.save()
        # Lookup only: invoke the installed compiler directly, never rustup install/run.
        found = cls.command(['rustup', 'which', '--toolchain', '1.98.0', 'rustc'], 'compiler-path')
        if found.returncode:
            raise RuntimeError('installed Rust 1.98.0 compiler required')
        cls.rustc = (cls.work / 'compiler-path.stdout').read_text().strip()
        cls.record['compiler_sha256'] = hashlib.sha256(Path(cls.rustc).read_bytes()).hexdigest()
        version = cls.command([cls.rustc, '--version', '--verbose'], 'compiler-version')
        if version.returncode or not (cls.work / 'compiler-version.stdout').read_text().startswith('rustc 1.98.0 '):
            raise RuntimeError('wrong Rust compiler version')
        cls.save()

    @classmethod
    def tearDownClass(cls):
        expected = {'conflict_skip_close', 'conflict_ignore_contents', 'conflict_skip_guard',
                    'conflict_overwrite_primary', 'cleaned-transition-control', 'reservation',
                    'receipt_forget_prefix', 'history-control', 'receipt_invent_errno',
                    'history', 'positive', 'service-owner', 'service-pair', 'connection-owner', 'byte-compare'}
        cls.record['result'] = 'pass' if set(cls.record['checks']) == expected and all(cls.record['checks'].values()) else 'fail'
        cls.save()
        if cls.record['result'] != 'pass':
            raise AssertionError('incomplete or failed Rust evidence receipt')

    @classmethod
    def save(cls):
        (cls.work / 'results.json').write_text(json.dumps(cls.record, indent=2) + '\n')

    @classmethod
    def command(cls, argv, label):
        entry = {'argv': argv, 'label': label, 'timeout_seconds': 20}
        cls.record['commands'].append(entry)
        cls.save()
        try:
            with (cls.work / (label + '.stdout')).open('wb') as out, (cls.work / (label + '.stderr')).open('wb') as err:
                result = subprocess.run(argv, cwd=cls.work, stdout=out, stderr=err, timeout=20,
                                        env=dict(os.environ, RUST_BACKTRACE='0'))
            entry['returncode'] = result.returncode
            return result
        except (OSError, subprocess.TimeoutExpired) as error:
            entry['error'] = type(error).__name__
            raise
        finally:
            cls.save()

    def compile(self, label, cfg=None, source="tests/native_sample_receipts.rs"):
        binary = self.work / label
        argv = [self.rustc, '--edition=2024', '--test', '-C', 'opt-level=2',
                source, '-o', str(binary)]
        if cfg:
            argv += ['--cfg', cfg]
        result = self.command(argv, label + '-build')
        self.assertEqual(result.returncode, 0, str(self.work / (label + '-build.stderr')))
        return binary

    def test_positive(self):
        binary = self.compile('positive')
        self.assertEqual(self.command([str(binary), '--list'], 'list').returncode, 0)
        listed = (self.work / 'list.stdout').read_text()
        self.assertEqual({line[:-6] for line in listed.splitlines() if line.endswith(': test')}, EXPECTED)
        self.assertEqual(self.command([str(binary)], 'positive-run').returncode, 0)
        self.assertIn('9 passed; 0 failed; 0 ignored', (self.work / 'positive-run.stdout').read_text())
        for name, pin in self.record['sources'].items():
            self.assertEqual(hashlib.sha256((self.work / name).read_bytes()).hexdigest(), pin)
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), pin)
        self.assertEqual(hashlib.sha256(Path(self.rustc).read_bytes()).hexdigest(), self.record['compiler_sha256'])
        self.record['checks']['positive'] = True
        self.save()

    def control(self, cfg, name, assertion):
        binary = self.compile(cfg, cfg)
        self.assertEqual(self.command([str(binary), '--exact', name], cfg + '-run').returncode, 101)
        output = (self.work / (cfg + '-run.stdout')).read_text()
        self.assertIn('0 passed; 1 failed; 0 ignored', output)
        self.assertIn(assertion, output)
        self.record['checks'][cfg] = True
        self.save()

    def test_forget_prefix_control(self):
        self.control('receipt_forget_prefix', 'prefix_survives_native_error',
                     'received prefix must survive native rejection')

    def test_invent_errno_control(self):
        self.control('receipt_invent_errno', 'invalid_booleans_are_local',
                     'local rejection must not invent native errno')

    def test_pending_history(self):
        binary = self.compile('history', source='tests/native_pending_history.rs')
        self.assertEqual(self.command([str(binary), '--list'], 'history-list').returncode, 0)
        listed = (self.work / 'history-list.stdout').read_text()
        self.assertEqual({line[:-6] for line in listed.splitlines() if line.endswith(': test')},
                         {'duplicate_preserves_exact_sample', 'every_identity_field_denies', 'nonterminal_cannot_mint',
                          'independent_duplicate_keeps_primary', 'conflicts_preserve_first_and_candidate',
                          'closed_store_does_not_produce', 'wrong_request_denies_before_production',
                          'produced_identity_and_absent_view_deny', 'equal_result_different_kind_conflicts'})
        self.assertEqual(self.command([str(binary)], 'history-run').returncode, 0)
        self.assertIn('9 passed; 0 failed; 0 ignored', (self.work / 'history-run.stdout').read_text())
        self.record['checks']['history'] = True
        self.save()

    def test_history_identity_control(self):
        binary = self.compile('history-skip-token', 'history_skip_token', 'tests/native_pending_history.rs')
        self.assertEqual(self.command([str(binary), '--exact', 'every_identity_field_denies'], 'history-control-run').returncode, 101)
        output = (self.work / 'history-control-run.stdout').read_text()
        self.assertIn('0 passed; 1 failed; 0 ignored', output)
        self.assertIn('every token field must deny substitution', output)
        self.record['checks']['history-control'] = True
        self.save()

    def conflict_control(self, cfg, name, assertion):
        binary = self.compile(cfg, cfg, 'tests/native_pending_history.rs')
        self.assertEqual(self.command([str(binary), '--exact', name], cfg + '-run').returncode, 101)
        output = (self.work / (cfg + '-run.stdout')).read_text()
        self.assertIn('0 passed; 1 failed; 0 ignored', output)
        self.assertIn(assertion, output)
        self.record['checks'][cfg] = True
        self.save()

    def test_conflict_overwrite_control(self):
        self.conflict_control('conflict_overwrite_primary', 'conflicts_preserve_first_and_candidate',
                              'first history must never be replaced')

    def test_conflict_close_control(self):
        self.conflict_control('conflict_skip_close', 'conflicts_preserve_first_and_candidate',
                              'conflict must close the local store')

    def test_conflict_guard_control(self):
        self.conflict_control('conflict_skip_guard', 'closed_store_does_not_produce',
                              'closed store must deny before candidate production')

    def test_conflict_content_control(self):
        self.conflict_control('conflict_ignore_contents', 'conflicts_preserve_first_and_candidate',
                              'different qualified history must conflict')

    def test_cut_reservation(self):
        source = 'tests/native_cut_reservation.rs'
        binary = self.compile('reservation', source=source)
        self.assertEqual(self.command([str(binary)], 'reservation-run').returncode, 0)
        self.assertIn('26 passed; 0 failed; 0 ignored', (self.work / 'reservation-run.stdout').read_text())
        for cfg, name, message in [
            ('reservation_partial', 'invalid_is_atomic', 'denial must not reserve credits'),
            ('reservation_forget', 'cancel_retains_history_and_serials', 'cancelled history must survive'),
            ('reservation_reuse', 'cancel_retains_history_and_serials', 'cancel must not reuse serials')]:
            binary = self.compile(cfg, cfg, source)
            self.assertEqual(self.command([str(binary), '--exact', 'cut_reservation::tests::' + name], cfg + '-run').returncode, 101)
            output = (self.work / (cfg + '-run.stdout')).read_text()
            self.assertIn('0 passed; 1 failed; 0 ignored', output)
            self.assertIn(message, output)
        for cfg, name, message in [
            ('application_skip_transition', 'dependency_transition_and_complete_capture', 'complete transition and capture required'),
            ('application_drop_capture', 'dependency_transition_and_complete_capture', 'complete transition and capture required'),
            ('application_corrupt_capture', 'dependency_transition_and_complete_capture', 'complete transition and capture required'),
            ('application_reopen', 'failed_verification_retains_unknown_and_capture', 'ambiguous application must stay closed')]:
            binary = self.compile(cfg, cfg, source)
            self.assertEqual(self.command([str(binary), '--exact', 'cut_reservation::application_tests::' + name], cfg + '-run').returncode, 101)
            output = (self.work / (cfg + '-run.stdout')).read_text()
            self.assertIn('0 passed; 1 failed; 0 ignored', output)
            self.assertIn(message, output)
        for cfg, message in [('effect_skip_token', 'every occurrence field must match'),
                             ('effect_early_ack', 'ack requires an applied return')]:
            binary = self.compile(cfg, cfg, source)
            self.assertEqual(self.command([str(binary), '--exact', 'cut_reservation::effect_tests::full_token_and_stage_order'], cfg + '-run').returncode, 101)
            output = (self.work / (cfg + '-run.stdout')).read_text()
            self.assertIn('0 passed; 1 failed; 0 ignored', output)
            self.assertIn(message, output)
        for cfg, name, message in [
            ('retire_skip_retain', 'retain_before_release_and_apply_dependent_once', 'retention must precede release'),
            ('retire_forget_count', 'retain_before_release_and_apply_dependent_once', 'historical count must survive retirement'),
            ('retire_skip_ack', 'retirement_requires_ack_and_exact_owner_occurrence', 'retirement requires acknowledgment')]:
            binary = self.compile(cfg, cfg, source)
            self.assertEqual(self.command([str(binary), '--exact', 'cut_reservation::retirement_tests::' + name], cfg + '-run').returncode, 101)
            output = (self.work / (cfg + '-run.stdout')).read_text()
            self.assertIn('0 passed; 1 failed; 0 ignored', output)
            self.assertIn(message, output)
        for cfg, name, message in [
            ('terminal_skip_transition', 'each_terminal_order_captures_exact_reclaim_once', 'terminal transition and reclaim capture required'),
            ('terminal_drop_capture', 'each_terminal_order_captures_exact_reclaim_once', 'terminal transition and reclaim capture required'),
            ('terminal_corrupt_capture', 'each_terminal_order_captures_exact_reclaim_once', 'terminal transition and reclaim capture required'),
            ('terminal_reopen', 'ambiguous_terminal_preserves_actual_state_and_effect_inventory', 'ambiguous terminal must stay closed')]:
            binary = self.compile(cfg, cfg, source)
            self.assertEqual(self.command([str(binary), '--exact', 'cut_reservation::terminal_application_tests::' + name], cfg + '-run').returncode, 101)
            output = (self.work / (cfg + '-run.stdout')).read_text()
            self.assertIn('0 passed; 1 failed; 0 ignored', output)
            self.assertIn(message, output)
        binary = self.compile('cleaned-transition', 'cleaned_skip_transition', 'tests/native_cut_reservation.rs')
        result = self.command([str(binary), '--exact', 'cut_reservation::cleaned_tests::cleaned_requires_acknowledged_retired_reclaim_and_replays'], 'cleaned-transition-run')
        self.assertEqual(result.returncode, 101)
        self.assertIn('Cleaned must apply after acknowledged reclaim', (self.work / 'cleaned-transition-run.stdout').read_text())
        self.record['checks']['cleaned-transition-control'] = True
        self.save()

        argv = [self.rustc, '--edition=2024', '--crate-type=lib', '--target=x86_64-unknown-none',
                str(self.work / source), '-o', str(self.work / 'reservation-target.rlib')]
        self.assertEqual(self.command(argv, 'reservation-target').returncode, 0)
        self.record['checks']['reservation'] = True
        self.save()

    def test_service_owner(self):
        binary = self.compile('service-owner', source='tests/native_service_owner.rs')
        result = self.command([str(binary)], 'service-owner-run')
        self.assertEqual(result.returncode, 0)
        self.assertIn('8 passed; 0 failed; 0 ignored', (self.work / 'service-owner-run.stdout').read_text())
        # Mutate private copies, never the accepted source or target fixture.
        original = (self.work / 'prototypes/native-supervisor/service_owner.rs').read_text()
        for label, old, new, test in [
            ('owner-identity', '!core::ptr::eq(self.owner, key.owner) || key.generation != self.generation || self.generation == 0', 'self.generation == 0', 'repeated_cycles_and_budget'),
            ('owner-unknown', 'self.phase = Phase::Unknown;', 'self.phase = Phase::Cleanup;', 'unknown_never_replays'),
            ('owner-writer', 'self.writer = Some(writer);', 'self.writer = None;', 'channel_and_launch_failure_cleanup'),
        ]:
            self.assertEqual(original.count(old), 2 if label == 'owner-identity' else 1)
            root = self.work / label
            target = root / 'prototypes/native-supervisor/service_owner.rs'
            target.parent.mkdir(parents=True)
            target.write_text(original.replace(old, new))
            entry = root / 'tests/native_service_owner.rs'
            entry.parent.mkdir()
            shutil.copyfile(self.work / 'tests/native_service_owner.rs', entry)
            executable = self.compile(label + '-binary', source=str(entry))
            self.assertEqual(self.command([str(executable), '--exact', test], label + '-run').returncode, 101)
            self.assertIn('0 passed; 1 failed; 0 ignored', (self.work / (label + '-run.stdout')).read_text())
        self.record['checks']['service-owner'] = True
        self.save()

    def test_service_pair(self):
        binary = self.compile('service-pair', source='tests/native_service_pair.rs')
        self.assertEqual(self.command([str(binary)], 'service-pair-run').returncode, 0)
        self.assertIn('5 passed; 0 failed; 0 ignored', (self.work / 'service-pair-run.stdout').read_text())
        original = (self.work / 'prototypes/native-supervisor/service_pair.rs').read_text()
        reversed_stop = original.split('    pub fn shutdown', 1)
        tail = reversed_stop[1].replace('self.dependent', 'self.swap').replace('self.provider', 'self.dependent').replace('self.swap', 'self.provider')
        guard = 'if !self.provider_running(backend)? { return Err(Error::Busy); }'
        self.assertEqual(original.count(guard), 1)
        for label, changed, test in [
            ('pair-admission', original.replace(guard, ''), 'provider_loss_blocks_admission_until_clean_replacement'),
            ('pair-order', reversed_stop[0] + '    pub fn shutdown' + tail, 'direct_start_restart_and_reverse_shutdown'),
        ]:
            root = self.work / label
            target = root / 'prototypes/native-supervisor/service_pair.rs'
            target.parent.mkdir(parents=True)
            target.write_text(changed)
            shutil.copyfile(self.work / 'prototypes/native-supervisor/service_owner.rs', target.parent / 'service_owner.rs')
            entry = root / 'tests/native_service_pair.rs'
            entry.parent.mkdir()
            shutil.copyfile(self.work / 'tests/native_service_pair.rs', entry)
            executable = self.compile(label + '-binary', source=str(entry))
            self.assertEqual(self.command([str(executable), '--exact', test], label + '-run').returncode, 101)
            self.assertIn('0 passed; 1 failed; 0 ignored', (self.work / (label + '-run.stdout')).read_text())
        self.record['checks']['service-pair'] = True
        self.save()

    def test_connection_owner(self):
        binary = self.compile('connection-owner', source='tests/native_connection_owner.rs')
        self.assertEqual(self.command([str(binary)], 'connection-owner-run').returncode, 0)
        self.assertIn('8 passed; 0 failed; 0 ignored', (self.work / 'connection-owner-run.stdout').read_text())
        original = (self.work / 'prototypes/native-supervisor/connection_owner.rs').read_text()
        for label, before, after, test in [
            ('connection-forgot-pair', 'self.readers[i] = Some(reader); self.writers[i] = Some(writer);',
             'if i != 0 { self.readers[i] = Some(reader); self.writers[i] = Some(writer); }',
             'each_partial_start_retains_exact_ownership'),
            ('connection-repeat-close', 'self.writers[i] = None;', '',
             'backend_eof_precedes_terminal_without_repeated_close'),
        ]:
            self.assertEqual(original.count(before), 1)
            root = self.work / label
            target = root / 'prototypes/native-supervisor/connection_owner.rs'
            target.parent.mkdir(parents=True)
            target.write_text(original.replace(before, after))
            shutil.copyfile(self.work / 'prototypes/native-supervisor/service_owner.rs', target.parent / 'service_owner.rs')
            entry = root / 'tests/native_connection_owner.rs'
            entry.parent.mkdir()
            shutil.copyfile(self.work / 'tests/native_connection_owner.rs', entry)
            executable = self.compile(label + '-binary', source=str(entry))
            self.assertEqual(self.command([str(executable), '--exact', test], label + '-run').returncode, 101)
            self.assertIn('0 passed; 1 failed; 0 ignored', (self.work / (label + '-run.stdout')).read_text())
        self.record['checks']['connection-owner'] = True
        self.save()

    def test_byte_compare(self):
        binary = self.compile('byte-compare', source='tests/native_byte_compare.rs')
        self.assertEqual(self.command([str(binary)], 'byte-compare-run').returncode, 0)
        self.assertIn('3 passed; 0 failed; 0 ignored', (self.work / 'byte-compare-run.stdout').read_text())
        original = (self.work / 'prototypes/native-command/byte_compare.rs').read_text()
        for label, before, after in [
            ('compare-signed', 'i32::from(a) - i32::from(b)', 'i32::from(a as i8) - i32::from(b as i8)'),
            ('compare-equal', 'if a != b { return i32::from(a) - i32::from(b); }', 'if a != b { return 0; }'),
        ]:
            self.assertEqual(original.count(before), 1)
            root = self.work / label
            target = root / 'prototypes/native-command/byte_compare.rs'
            target.parent.mkdir(parents=True)
            target.write_text(original.replace(before, after))
            entry = root / 'tests/native_byte_compare.rs'
            entry.parent.mkdir()
            shutil.copyfile(self.work / 'tests/native_byte_compare.rs', entry)
            executable = self.compile(label + '-binary', source=str(entry))
            self.assertEqual(self.command([str(executable), '--exact', 'unsigned_order_all_byte_values'], label + '-run').returncode, 101)
            self.assertIn('0 passed; 1 failed; 0 ignored', (self.work / (label + '-run.stdout')).read_text())
        self.record['checks']['byte-compare'] = True
        self.save()
