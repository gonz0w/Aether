#!/usr/bin/env python3
"""Run model tests, mutation controls and baseline under a 30-second watchdog."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import tracemalloc
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from bounded_capture import OutputLimitError, run_capture


def load_tests():
    spec = importlib.util.spec_from_file_location('runtime_tests', ROOT / 'tests/test_runtime_model.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def worker():
    sys.path.insert(0, str(ROOT))
    module = load_tests()
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    discovered = suite.countTestCases()
    if discovered == 0:
        raise RuntimeError('zero discovered cases')
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped or result.testsRun != discovered:
        raise RuntimeError(output.getvalue())
    source = (ROOT / 'prototypes/runtime_model/model.py').read_text()
    module_name = 'prototypes.runtime_model.model'
    original = sys.modules[module_name]
    controls = [
        ('stale-readiness', 'epoch != self.epoch or generation != s.generation',
         'epoch != self.epoch', 'test_T01_stale_generation'),
        ('reset-retry-budget', 's.ready, s.outcome = True, \'success\'',
         's.ready, s.outcome = True, \'success\'; s.retries_used = 0',
         'test_T11_finite_retry_budget_and_no_ready_reset'),
        ('bypass-cleanup', "s.phase, s.terminal, s.launch_pending = 'terminal', reason, False",
         "s.phase, s.terminal, s.launch_pending = 'terminal', reason, False\n            if s.retry_allowed:\n                s.phase, s.due = 'retry', self.now",
         'test_T15_no_replacement_before_reclaim'),
    ]
    controls.append(('stopped-kind',
        "else kind, permanent=(kind == 'denied')",
        "else ('exit' if kind == 'stopped' else kind), permanent=(kind == 'denied')",
        'test_stopped_preserves_kind_and_requires_cleanup'))
    mutations = []
    for name, old, new, test in controls:
        if source.count(old) != 1:
            raise RuntimeError('mutation anchor mismatch: ' + name)
        mutant = types.ModuleType(module_name)
        sys.modules[module_name] = mutant
        try:
            exec(compile(source.replace(old, new), '<negative-control>', 'exec'), mutant.__dict__)
            target = load_tests()
            negative_output = io.StringIO()
            negative = unittest.TextTestRunner(stream=negative_output).run(target.RuntimeTests(test))
            if len(negative.failures) != 1 or negative.errors:
                raise RuntimeError('negative control not caught by assertion: ' + name + '\n' + negative_output.getvalue())
            mutations.append({'name': name, 'test': test, 'caught': True,
                              'assertion': negative.failures[0][1].splitlines()[-1]})
        finally:
            sys.modules[module_name] = original
    codec_name = 'prototypes.runtime_model.control_codec'
    codec_original = sys.modules[codec_name]
    codec_source = (ROOT / 'prototypes/runtime_model/control_codec.py').read_text()
    for name, old, new, test in [
        ('codec-depth', 'if depth > limit:', 'if False:',
         'test_depth_checked_before_parser'),
        ('codec-duplicate-key', 'if key in result:', 'if False:',
         'test_duplicate_decoded_keys'),
    ]:
        if codec_source.count(old) != 1:
            raise RuntimeError('mutation anchor mismatch: ' + name)
        mutant = types.ModuleType(codec_name)
        sys.modules[codec_name] = mutant
        try:
            exec(compile(codec_source.replace(old, new), '<codec-negative-control>', 'exec'),
                 mutant.__dict__)
            target = load_tests()
            negative_output = io.StringIO()
            negative = unittest.TextTestRunner(stream=negative_output).run(target.CodecTests(test))
            if len(negative.failures) != 3 or negative.errors:
                raise RuntimeError('codec control not caught by assertions: ' + name + '\n' +
                                   negative_output.getvalue())
            mutations.append({'name': name, 'test': test, 'caught': True,
                              'assertion': negative.failures[0][1].splitlines()[-1]})
        finally:
            sys.modules[codec_name] = codec_original
    reply_name = 'prototypes.runtime_model.control_reply'
    reply_original = sys.modules[reply_name]
    reply_source = (ROOT / 'prototypes/runtime_model/control_reply.py').read_text()
    for name, old, new, case, test in [
        ('receipt-fields', '_require(type(value) is dict and value.keys() == set(fields.split()))',
         '_require(type(value) is dict)', 'ReplyTests', 'test_extra_receipt_fields_rejected'),
        ('observation-identity', "_require(operation['epoch'] == epoch and operation['id'] == identity)",
         '_require(True)', 'ObservationReplyTests', 'test_mismatched_identity_rejected'),
        ('error-disposition', "(code == 'internal-error' and disposition == 'unknown')",
         "(code == 'internal-error')", 'DeliveryTests', 'test_internal_error_cannot_claim_no_dispatch'),
    ]:
        if reply_source.count(old) != 1:
            raise RuntimeError('mutation anchor mismatch: ' + name)
        mutant = types.ModuleType(reply_name)
        sys.modules[reply_name] = mutant
        try:
            exec(compile(reply_source.replace(old, new), '<reply-negative-control>', 'exec'),
                 mutant.__dict__)
            target = load_tests()
            negative_output = io.StringIO()
            negative = unittest.TextTestRunner(stream=negative_output).run(getattr(target, case)(test))
            if len(negative.failures) != 1 or negative.errors:
                raise RuntimeError('reply control not caught: ' + name + '\n' + negative_output.getvalue())
            mutations.append({'name': name, 'test': test,
                              'caught': True, 'assertion': negative.failures[0][1].splitlines()[-1]})
        finally:
            sys.modules[reply_name] = reply_original
    # Fixed eight-service dependency chain, start -> observed launch -> ordered stop/reclaim.
    stream_name = 'prototypes.runtime_model.control_stream'
    stream_original = sys.modules[stream_name]
    stream_source = (ROOT / 'prototypes/runtime_model/control_stream.py').read_text()
    old = 'if now >= self.deadline:'
    if stream_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: stream-deadline')
    mutant = types.ModuleType(stream_name)
    sys.modules[stream_name] = mutant
    try:
        exec(compile(stream_source.replace(old, 'if now > self.deadline:'),
                     '<stream-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.StreamTests('test_read_deadline_exact_boundary'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('deadline control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'stream-deadline', 'test': 'test_read_deadline_exact_boundary',
                          'caught': True, 'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[stream_name] = stream_original
    authority_name = 'prototypes.runtime_model.control_authority'
    authority_original = sys.modules[authority_name]
    authority_source = (ROOT / 'prototypes/runtime_model/control_authority.py').read_text()
    old = 'if binding is not self.binding:'
    if authority_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: authority-binding')
    mutant = types.ModuleType(authority_name)
    sys.modules[authority_name] = mutant
    try:
        exec(compile(authority_source.replace(old, 'if False:'),
                     '<authority-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.AuthorityTests('test_foreign_binding_denied_before_effects'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('binding control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'authority-binding', 'test': 'test_foreign_binding_denied_before_effects',
                          'caught': True, 'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[authority_name] = authority_original
    effect_name = 'prototypes.runtime_model.effect_ledger'
    effect_original = sys.modules[effect_name]
    effect_source = (ROOT / 'prototypes/runtime_model/effect_ledger.py').read_text()
    old = "if state == 'reserved' and outcome != 'rejected-before-effects':"
    if effect_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: effect-issued')
    mutant = types.ModuleType(effect_name)
    sys.modules[effect_name] = mutant
    try:
        exec(compile(effect_source.replace(old, 'if False:'), '<effect-negative-control>', 'exec'),
             mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.EffectTests('test_cannot_confirm_unissued_effect'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('issued-state control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'effect-issued', 'test': 'test_cannot_confirm_unissued_effect',
                          'caught': True, 'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[effect_name] = effect_original
    accounted_name = 'prototypes.runtime_model.accounted_delivery'
    accounted_original = sys.modules[accounted_name]
    accounted_source = (ROOT / 'prototypes/runtime_model/accounted_delivery.py').read_text()
    old = 'if self.ledger.closed or self.ledger.live or self.credits or self.ledger.next_id > MAX_ID - 7:'
    if accounted_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: accounted-admission')
    mutant = types.ModuleType(accounted_name)
    sys.modules[accounted_name] = mutant
    try:
        exec(compile(accounted_source.replace(old, 'if False:'),
                     '<accounted-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.AccountedTests('test_capacity_denial_before_dispatch'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('capacity control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'accounted-admission', 'test': 'test_capacity_denial_before_dispatch',
                          'caught': True, 'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[accounted_name] = accounted_original
    journal_name = 'prototypes.runtime_model.event_journal'
    journal_original = sys.modules[journal_name]
    journal_source = (ROOT / 'prototypes/runtime_model/event_journal.py').read_text()
    old = 'if self.ticket is not None or self.live or self.next_cut > MAX_ID:'
    if journal_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: event-reservation')
    mutant = types.ModuleType(journal_name)
    sys.modules[journal_name] = mutant
    try:
        exec(compile(journal_source.replace(old, 'if False:'),
                     '<event-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.EventJournalTests('test_reservation_gate_preserves_unresolved_cut'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('event reservation control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'event-reservation', 'caught': True,
                          'test': 'test_reservation_gate_preserves_unresolved_cut',
                          'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[journal_name] = journal_original
    runtime_name = 'prototypes.runtime_model.journal_runtime'
    runtime_original = sys.modules[runtime_name]
    runtime_source = (ROOT / 'prototypes/runtime_model/journal_runtime.py').read_text()
    old = 'self.owner._admit()\n        super()._begin(count)'
    if runtime_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: journal-admission-order')
    mutant = types.ModuleType(runtime_name)
    sys.modules[runtime_name] = mutant
    try:
        changed = runtime_source.replace(old, 'super()._begin(count)\n        self.owner._admit()')
        exec(compile(changed, '<runtime-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.JournalRuntimeTests('test_capacity_denial_precedes_model_mutation'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('admission order control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'journal-admission-order', 'caught': True,
                          'test': 'test_capacity_denial_precedes_model_mutation',
                          'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[runtime_name] = runtime_original
    queued_name = 'prototypes.runtime_model.queued_runtime'
    queued_original = sys.modules[queued_name]
    queued_source = (ROOT / 'prototypes/runtime_model/queued_runtime.py').read_text()
    old = 'if len(self.inbox) >= 4:'
    if queued_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: observation-capacity')
    mutant = types.ModuleType(queued_name)
    sys.modules[queued_name] = mutant
    try:
        exec(compile(queued_source.replace(old, 'if False:'),
                     '<inbox-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.QueuedRuntimeTests('test_capacity_overflow_closes_without_dropping_accepted_cuts'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('inbox capacity control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'observation-capacity', 'caught': True,
                          'test': 'test_capacity_overflow_closes_without_dropping_accepted_cuts',
                          'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[queued_name] = queued_original
    confirmed_name = 'prototypes.runtime_model.confirmed_result'
    confirmed_original = sys.modules[confirmed_name]
    confirmed_source = (ROOT / 'prototypes/runtime_model/confirmed_result.py').read_text()
    old = "if journal.closed or journal.observe(token) != 'issued':"
    if confirmed_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: confirmed-issued')
    mutant = types.ModuleType(confirmed_name)
    sys.modules[confirmed_name] = mutant
    try:
        exec(compile(confirmed_source.replace(old, 'if journal.closed:'),
                     '<confirmed-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.ConfirmedResultTests('test_unknown_cannot_be_resolved_by_later_ebadf'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('confirmed issued control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'confirmed-issued', 'caught': True,
                          'test': 'test_unknown_cannot_be_resolved_by_later_ebadf',
                          'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[confirmed_name] = confirmed_original
    applier_name = 'prototypes.runtime_model.result_applier'
    applier_original = sys.modules[applier_name]
    applier_source = (ROOT / 'prototypes/runtime_model/result_applier.py').read_text()
    old = 'if self.bindings.get(call.token) is not call:'
    if applier_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: retained-result-binding')
    mutant = types.ModuleType(applier_name)
    sys.modules[applier_name] = mutant
    try:
        exec(compile(applier_source.replace(old, 'if False:'),
                     '<applier-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.ResultApplierTests('test_fabricated_equivalent_context_cannot_apply'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('result binding control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'retained-result-binding', 'caught': True,
                          'test': 'test_fabricated_equivalent_context_cannot_apply',
                          'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[applier_name] = applier_original
    registry_name = 'prototypes.runtime_model.target_registry'
    registry_original = sys.modules[registry_name]
    registry_source = (ROOT / 'prototypes/runtime_model/target_registry.py').read_text()
    old = 'if not state.owned or state.generation != token[6]:'
    if registry_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: target-generation')
    mutant = types.ModuleType(registry_name)
    sys.modules[registry_name] = mutant
    try:
        exec(compile(registry_source.replace(old, 'if not state.owned:'),
                     '<target-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.TargetRegistryTests('test_stale_model_generation_cannot_receive_old_target_fact'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('target generation control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'target-generation', 'caught': True,
                          'test': 'test_stale_model_generation_cannot_receive_old_target_fact',
                          'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[registry_name] = registry_original
    cleanup_name = 'prototypes.runtime_model.rejected_launch_cleanup'
    cleanup_original = sys.modules[cleanup_name]
    cleanup_source = (ROOT / 'prototypes/runtime_model/rejected_launch_cleanup.py').read_text()
    old = 'or any(self.endpoints.values())'
    if cleanup_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: rejected-endpoints')
    mutant = types.ModuleType(cleanup_name)
    sys.modules[cleanup_name] = mutant
    try:
        exec(compile(cleanup_source.replace(old, 'or False'),
                     '<cleanup-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.RejectedLaunchCleanupTests('test_both_endpoints_required'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('endpoint control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'rejected-endpoints', 'caught': True,
                          'test': 'test_both_endpoints_required',
                          'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[cleanup_name] = cleanup_original
    resources_name = 'prototypes.runtime_model.admitted_resources'
    resources_original = sys.modules[resources_name]
    resources_source = (ROOT / 'prototypes/runtime_model/admitted_resources.py').read_text()
    old = 'or self.wait is not None'
    if resources_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: admitted-wait-release')
    mutant = types.ModuleType(resources_name)
    sys.modules[resources_name] = mutant
    try:
        exec(compile(resources_source.replace(old, 'or False'),
                     '<resources-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.AdmittedResourcesTests('test_wait_release_required_after_native_reclaim'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('wait release control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'admitted-wait-release', 'caught': True,
                          'test': 'test_wait_release_required_after_native_reclaim',
                          'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[resources_name] = resources_original
    driver_name = 'prototypes.runtime_model.lifecycle_driver'
    driver_original = sys.modules[driver_name]
    driver_source = (ROOT / 'prototypes/runtime_model/lifecycle_driver.py').read_text()
    old = 'self.runtime.batch([event for _, event in pending])'
    if driver_source.count(old) != 1:
        raise RuntimeError('mutation anchor mismatch: driver-event-retention')
    mutant = types.ModuleType(driver_name)
    sys.modules[driver_name] = mutant
    try:
        replacement = "[a.update(event=None) for a in self.attempts.values()]; " + old
        exec(compile(driver_source.replace(old, replacement),
                     '<driver-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.LifecycleDriverTests('test_backpressure_preserves_pending_observation'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('driver retention control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'driver-event-retention', 'caught': True,
                          'test': 'test_backpressure_preserves_pending_observation',
                          'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[driver_name] = driver_original
    old = 'target = self.registry.reserve(token, slot, owner=owner)'
    # The indented legacy prepare path is deliberately left unchanged.
    anchor = '        ' + old + '\n        if not hasattr(self, \'channel_generations\'):'
    if driver_source.count(anchor) != 1:
        raise RuntimeError('mutation anchor mismatch: channel-reservation')
    mutant = types.ModuleType(driver_name)
    sys.modules[driver_name] = mutant
    try:
        replacement = "        target = 0xb0000101\n        if not hasattr(self, 'channel_generations'):"
        exec(compile(driver_source.replace(anchor, replacement),
                     '<acquisition-negative-control>', 'exec'), mutant.__dict__)
        target = load_tests()
        negative_output = io.StringIO()
        negative = unittest.TextTestRunner(stream=negative_output).run(
            target.ChannelAcquisitionTests('test_capacity_is_reserved_before_channel_creation'))
        if len(negative.failures) != 1 or negative.errors:
            raise RuntimeError('channel reservation control not caught: ' + negative_output.getvalue())
        mutations.append({'name': 'channel-reservation', 'caught': True,
                          'test': 'test_capacity_is_reserved_before_channel_creation',
                          'assertion': negative.failures[0][1].splitlines()[-1]})
    finally:
        sys.modules[driver_name] = driver_original
    # Fixed eight-service dependency chain, start -> observed launch -> ordered stop/reclaim.
    Model, Service = original.Model, original.Service
    graph = [Service('s' + str(i), requires=() if i == 0 else (('s' + str(i-1), 'started'),)) for i in range(8)]
    tracemalloc.start()
    start = time.perf_counter()
    for _ in range(1000):
        m = Model(graph)
        m.start(['s7'])
        for i in range(8):
            m.batch([('launched', 's'+str(i), 1, m.epoch, 0)])
        if m.operations[-1].status != 'success':
            raise RuntimeError('benchmark activation failed')
        m.stop(['s'+str(i) for i in range(8)], shutdown=True)
        for i in reversed(range(8)):
            m.batch([('exit', 's'+str(i), 1, m.epoch, 0)])
            m.batch([('cleaned', 's'+str(i), 1, m.epoch, 0)])
        if m.operations[-1].status != 'success' or any(s.owned for s in m.state.values()):
            raise RuntimeError('benchmark cleanup failed')
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    paths = ['prototypes/runtime_model/model.py', 'prototypes/runtime_model/control.py',
             'prototypes/runtime_model/control_codec.py',
             'prototypes/runtime_model/control_reply.py',
             'prototypes/runtime_model/control_delivery.py',
             'prototypes/runtime_model/control_stream.py',
             'prototypes/runtime_model/control_authority.py',
             'prototypes/runtime_model/effect_ledger.py',
             'prototypes/runtime_model/accounted_delivery.py',
             'prototypes/runtime_model/event_journal.py',
             'prototypes/runtime_model/cut_coordinator.py',
             'prototypes/runtime_model/cut_retirement.py',
             'prototypes/runtime_model/launched_adapter.py',
             'prototypes/runtime_model/terminal_adapter.py',
             'prototypes/runtime_model/cleaned_adapter.py',
             'prototypes/runtime_model/journal_runtime.py',
             'prototypes/runtime_model/queued_runtime.py',
             'prototypes/runtime_model/confirmed_result.py',
             'prototypes/runtime_model/result_applier.py',
             'prototypes/runtime_model/target_registry.py',
             'prototypes/runtime_model/lifecycle_driver.py',
             'prototypes/runtime_model/admitted_resources.py',
             'prototypes/runtime_model/rejected_launch_cleanup.py',
             'tests/test_runtime_model.py', 'scripts/check-runtime-model.py',
             'scripts/bounded_capture.py']
    print(json.dumps({'tests': result.testsRun, 'passed': True, 'test_output': output.getvalue(),
                      'negative_controls': mutations, 'permutation_cases': 24, 'seeded_traces': 100,
                      'python': sys.version, 'platform': platform.platform(),
                      'machine': platform.machine(), 'processor': platform.processor(),
                      'benchmark': {'traces': 1000, 'services': 8, 'events_per_trace': 26,
                                    'elapsed_seconds': elapsed, 'peak_traced_python_bytes': peak,
                                    'memory_method': 'tracemalloc; Python allocations, not process RSS'},
                      'source_sha256': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'out/runtime-model/results.json')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        worker()
    else:
        # Harness only; the model itself performs no process or filesystem operations.
        try:
            run = run_capture([sys.executable, str(Path(__file__).resolve()), '--worker'],
                              timeout=30, cwd=ROOT)
            if run.returncode:
                raise RuntimeError(run.stdout + run.stderr)
            report = json.loads(run.stdout)
        except Exception as exc:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            detail = str(exc)
            if isinstance(exc, (subprocess.TimeoutExpired, OutputLimitError)):
                detail += '\nstdout prefix:\n' + (exc.output or b'').decode(errors='replace')
                detail += '\nstderr prefix:\n' + (exc.stderr or b'').decode(errors='replace')
            args.output.write_text(json.dumps({'passed': False, 'error': detail}, indent=2)+'\n')
            raise
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2)+'\n')
        print(f"PASS: {report['tests']} tests, {len(report['negative_controls'])} negative controls; "
              f"1000 traces in {report['benchmark']['elapsed_seconds']:.3f}s; {args.output}")
