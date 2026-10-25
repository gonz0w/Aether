"""Hand-authored policy oracles; no real processes or native lifecycle claims."""
import itertools
import json
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prototypes.runtime_model.model import Model, Rejected, Service
from prototypes.runtime_model.control import Control, InvalidRequest, MAX_ID
from copy import deepcopy
from unittest.mock import patch
from prototypes.runtime_model.control_codec import decode_request, InvalidFrame
from prototypes.runtime_model.control_reply import (encode_receipt, decode_receipt,
    encode_observation, decode_observation, encode_wait, decode_wait)
from prototypes.runtime_model.control_reply import encode_error, decode_error
from prototypes.runtime_model.control_delivery import Delivery, Backpressure
from prototypes.runtime_model.control_stream import Stream
from prototypes.runtime_model.control_authority import AuthorizedStream, Denied
from prototypes.runtime_model.effect_ledger import EffectLedger, InvalidEffect
from prototypes.runtime_model.accounted_delivery import AccountedDelivery
from prototypes.runtime_model.event_journal import EventJournal
from prototypes.runtime_model.journal_runtime import JournalRuntime
from prototypes.runtime_model.queued_runtime import QueuedRuntime
from prototypes.runtime_model.confirmed_result import BoundCall, PROFILE
from prototypes.runtime_model.result_applier import ResultApplier
from prototypes.runtime_model.target_registry import TargetRegistry
from prototypes.runtime_model.lifecycle_driver import LifecycleDriver
from prototypes.runtime_model.admitted_resources import AdmittedResources
from prototypes.runtime_model.rejected_launch_cleanup import RejectedLaunchCleanup


class ChannelAcquisitionTests(unittest.TestCase):
    @staticmethod
    def reply(token, result=0xd1000101):
        return dict(schema='abi6-channel-return-v1', profile=PROFILE, producer='a' * 64,
                    token=token, syscall=0x24000, result=result,
                    writer=result + 1 if result > 0 else None)

    def setup(self, services=None):
        return LifecycleDriverTests().setup_driver(services)

    def test_capacity_is_reserved_before_channel_creation(self):
        r, d, owner, (token,) = self.setup()
        self.assertEqual(d.reserve_channel(token, 0, owner=owner), ('channel-create-v1', token, 0x24000))
        self.assertEqual(len(d.registry.slots), 1)
        self.assertEqual(d.registry.slots[0]['phase'], 'reserved')
        self.assertEqual(d.attempts['a']['phase'], 'acquiring')
        self.assertIsNone(d.attempts['a']['reader'])
        self.assertEqual(r.journal.observe(token), 'issued')

    def test_creation_success_routes_to_launch_and_cleanup(self):
        r, d, owner, (token,) = self.setup()
        d.reserve_channel(token, 0, owner=owner)
        call = d.channel_reply('a', self.reply(token), owner=owner)
        self.assertEqual(d.attempts['a']['reader'], 0xd1000101)
        d.launch_reply('a', ResultApplierTests.reply(call), owner=owner)
        d.terminal_reply('a', TargetRegistryTests.status_reply(call.target, 144, 3), owner=owner)
        d.deliver(owner=owner); reclaim, = r.issue_obligations()
        context = BoundCall(r.journal, owner, 'a' * 64, reclaim, 0x20002, call.target)
        d.reclaim(reclaim, ResultApplierTests.reply(context), owner=owner)
        d.attempts['a']['resources'].close_reply(
            AdmittedResourcesTests.reply(call.target, 0xd1000101, 0x24003), owner=owner)
        d.queue_cleanup('a', owner=owner); d.deliver(owner=owner)
        self.assertEqual(d.attempts, {})
        self.assertEqual(d.channel_generations, [1, 0])

    def test_creation_errors_clean_empty_inventory_without_native_calls(self):
        for error in (-13, -22, -16, -28):
            r, d, owner, (token,) = self.setup()
            d.reserve_channel(token, 0, owner=owner)
            self.assertIsNone(d.channel_reply('a', self.reply(token, error), owner=owner))
            self.assertEqual(d.attempts['a']['channel_error'], error)
            self.assertEqual(d.registry.slots, {})
            self.assertEqual(d.channel_generations, [0, 0])
            self.assertIsNone(d.applier.last_applied)
            d.deliver(owner=owner); reclaim, = r.issue_obligations()
            with self.assertRaises(InvalidEffect): d.queue_cleanup('a', owner=owner)
            self.assertEqual(d.reclaim(reclaim, owner=owner),
                             ('local-cleanup-v1', reclaim, 'channel-not-created'))
            d.queue_cleanup('a', owner=owner); d.deliver(owner=owner)
            self.assertFalse(r.model.state['a'].owned)
            self.assertEqual(d.attempts, {})

    def test_pending_and_invalid_reservations_do_not_acquire(self):
        r, d, owner, tokens = self.setup([Service('a'), Service('b')])
        with self.assertRaises(InvalidEffect): d.reserve_channel(tokens[0], True, owner=owner)
        self.assertEqual(d.attempts, {})
        self.assertFalse(hasattr(d, 'channel_generations'))
        d.reserve_channel(tokens[0], 0, owner=owner)
        with self.assertRaises(InvalidEffect): d.reserve_channel(tokens[1], 1, owner=owner)
        with self.assertRaises(InvalidEffect): d.prepare(tokens[1], 1, 101, 102, owner=owner)
        self.assertEqual(list(d.attempts), ['a'])
        self.assertFalse(r.failed)

    def test_malformed_creation_closes_owner_and_keeps_reservation(self):
        for field, value in [('result', None), ('writer', 0xd1000101),
                             ('producer', 'b' * 64), ('result', 0xd1000201)]:
            r, d, owner, (token,) = self.setup()
            d.reserve_channel(token, 0, owner=owner)
            reply = self.reply(token); reply[field] = value
            with self.assertRaises(InvalidEffect): d.channel_reply('a', reply, owner=owner)
            self.assertTrue(r.failed)
            self.assertEqual(r.journal.observe(token), 'unknown')
            self.assertEqual(d.channel_pending, 'a')
            self.assertEqual(d.registry.slots[0]['phase'], 'reserved')
            with self.assertRaises(InvalidEffect): d.channel_reply('a', self.reply(token), owner=owner)

    def test_post_creation_failure_retains_both_endpoints(self):
        r, d, owner, (token,) = self.setup()
        d.reserve_channel(token, 0, owner=owner)
        with patch.object(d.applier, 'bind', side_effect=InvalidEffect('injected bind')):
            with self.assertRaises(InvalidEffect): d.channel_reply('a', self.reply(token), owner=owner)
        self.assertTrue(r.failed)
        self.assertEqual((d.attempts['a']['reader'], d.attempts['a']['writer']), (0xd1000101, 0xd1000102))
        self.assertEqual(d.channel_generations, [1, 0])

    def test_rejected_launch_advances_channel_but_not_target_generation(self):
        r, d, owner, (token,) = self.setup([Service('a', retries=1)])
        d.reserve_channel(token, 0, owner=owner)
        call = d.channel_reply('a', self.reply(token), owner=owner)
        reply = ResultApplierTests.reply(call); reply['result'] = -22
        d.launch_reply('a', reply, owner=owner); d.deliver(owner=owner)
        reclaim, = r.issue_obligations()
        for endpoint in (0xd1000101, 0xd1000102):
            d.attempts['a']['rejected'].close_reply(RejectedLaunchCleanupTests.reply(endpoint), owner=owner)
        d.reclaim(reclaim, owner=owner); d.queue_cleanup('a', owner=owner); d.deliver(owner=owner)
        r.batch(now=1); token, = r.issue_obligations()
        d.reserve_channel(token, 0, owner=owner)
        replacement = d.channel_reply('a', self.reply(token, 0xd1000201), owner=owner)
        self.assertEqual(replacement.target, call.target)
        self.assertEqual(d.channel_generations, [2, 0])
        self.assertEqual(replacement.token[6], 2)


class LifecycleDriverTests(unittest.TestCase):
    def setup_driver(self, services=None):
        r = JournalRuntime(services or [Service('a')]); owner = object()
        d = LifecycleDriver(r, owner=owner, producer='a' * 64)
        r.start(list(r.model.spec)); tokens = r.issue_obligations()
        return r, d, owner, tokens

    def test_admitted_path_terminal_supersedes_launch_and_cleans(self):
        r, d, owner, (token,) = self.setup_driver()
        call = d.prepare(token, 0, 101, 102, owner=owner)
        d.launch_reply('a', ResultApplierTests.reply(call), owner=owner)
        d.terminal_reply('a', TargetRegistryTests.status_reply(call.target, 144, 3), owner=owner)
        self.assertEqual(d.deliver(owner=owner), 1)
        self.assertEqual(r.model.state['a'].terminal, 'stopped')
        self.assertFalse(r.model.state['a'].started)
        reclaim, = r.issue_obligations()
        context = BoundCall(r.journal, owner, 'a' * 64, reclaim, 0x20002, call.target)
        d.reclaim(reclaim, ResultApplierTests.reply(context), owner=owner)
        resources = d.attempts['a']['resources']
        with self.assertRaises(InvalidEffect): d.queue_cleanup('a', owner=owner)
        resources.close_reply(AdmittedResourcesTests.reply(call.target, 101, 0x24003), owner=owner)
        d.queue_cleanup('a', owner=owner)
        self.assertTrue(r.model.state['a'].owned)
        d.deliver(owner=owner)
        self.assertEqual(d.attempts, {})
        self.assertEqual(d.registry.slots, {})
        self.assertFalse(r.model.state['a'].owned)

    def test_rejected_path_local_cleanup_then_new_attempt(self):
        r, d, owner, (token,) = self.setup_driver([Service('a', retries=1)])
        call = d.prepare(token, 0, 101, 102, owner=owner)
        reply = ResultApplierTests.reply(call); reply['result'] = -22
        d.launch_reply('a', reply, owner=owner); d.deliver(owner=owner)
        reclaim, = r.issue_obligations()
        with self.assertRaises(InvalidEffect): d.reclaim(reclaim, owner=owner)
        for endpoint in (101, 102):
            d.attempts['a']['rejected'].close_reply(RejectedLaunchCleanupTests.reply(endpoint), owner=owner)
        with self.assertRaises(InvalidEffect): d.reclaim(reclaim, {}, owner=owner)
        d.reclaim(reclaim, owner=owner); d.queue_cleanup('a', owner=owner); d.deliver(owner=owner)
        r.batch(now=1); retry, = r.issue_obligations()
        next_call = d.prepare(retry, 0, 103, 104, owner=owner)
        self.assertEqual(next_call.target, call.target)
        self.assertEqual(next_call.token[6], 2)
        self.assertEqual(d.applier.last_applied[0], token)

    def test_backpressure_preserves_pending_observation(self):
        r, d, owner, tokens = self.setup_driver([Service('a'), Service('b')])
        first = d.prepare(tokens[0], 0, 101, 102, owner=owner)
        d.launch_reply('a', ResultApplierTests.reply(first), owner=owner)
        event = d.attempts['a']['event']
        with self.assertRaises(InvalidEffect): d.deliver(owner=owner)
        self.assertEqual(d.attempts['a']['event'], event)
        self.assertFalse(r.failed)
        second = d.prepare(tokens[1], 1, 103, 104, owner=owner)
        d.launch_reply('b', ResultApplierTests.reply(second), owner=owner)
        self.assertEqual(d.deliver(owner=owner), 2)
        self.assertTrue(all(s.started for s in r.model.state.values()))

    def test_malformed_launch_closes_owner_and_retains_unknown(self):
        r, d, owner, (token,) = self.setup_driver()
        call = d.prepare(token, 0, 101, 102, owner=owner)
        reply = ResultApplierTests.reply(call); reply['result'] = None
        with self.assertRaises(InvalidEffect): d.launch_reply('a', reply, owner=owner)
        self.assertTrue(r.failed)
        self.assertEqual(r.journal.observe(token), 'unknown')
        self.assertEqual(d.attempts['a']['rejected'].endpoints, {101: True, 102: True})
        self.assertEqual(d.registry.slots[0]['phase'], 'reserved')

    def test_partial_prepare_and_capture_failure_retain_attempt(self):
        r, d, owner, (token,) = self.setup_driver()
        with patch.object(d.applier, 'bind', side_effect=InvalidEffect('injected bind')):
            with self.assertRaises(InvalidEffect): d.prepare(token, 0, 101, 102, owner=owner)
        self.assertTrue(r.failed)
        self.assertEqual(d.attempts['a']['reader'], 101)
        self.assertEqual(d.registry.slots[0]['phase'], 'reserved')
        r, d, owner, (token,) = self.setup_driver()
        call = d.prepare(token, 0, 101, 102, owner=owner)
        d.launch_reply('a', ResultApplierTests.reply(call), owner=owner)
        event = d.attempts['a']['event']
        with patch.object(r.journal, 'capture', side_effect=InvalidEffect('injected capture')):
            with self.assertRaises(InvalidEffect): d.deliver(owner=owner)
        self.assertTrue(r.failed)
        self.assertEqual(d.attempts['a']['event'], event)

    def test_endpoint_overlap_and_runtime_contract(self):
        with self.assertRaises(InvalidEffect):
            LifecycleDriver(QueuedRuntime([Service('a')]), owner=object(), producer='a' * 64)
        oversized = JournalRuntime([Service('a'), Service('b'), Service('c')])
        with self.assertRaises(InvalidEffect):
            LifecycleDriver(oversized, owner=object(), producer='a' * 64)
        self.assertFalse(getattr(oversized, '_result_applier_claimed', False))
        r, d, owner, tokens = self.setup_driver([Service('a'), Service('b')])
        d.prepare(tokens[0], 0, 101, 102, owner=owner)
        with self.assertRaises(InvalidEffect): d.prepare(tokens[1], 1, 102, 103, owner=owner)
        self.assertEqual(list(d.attempts), ['a'])
        self.assertFalse(r.failed)
        with self.assertRaises(InvalidEffect): d.deliver(owner=object())

    def test_conflicting_terminal_event_preserves_first(self):
        r, d, owner, (token,) = self.setup_driver()
        call = d.prepare(token, 0, 101, 102, owner=owner)
        d.launch_reply('a', ResultApplierTests.reply(call), owner=owner)
        terminal = TargetRegistryTests.status_reply(call.target, 144, 3)
        d.terminal_reply('a', terminal, owner=owner)
        d.terminal_reply('a', terminal, owner=owner)
        with self.assertRaises(InvalidEffect):
            d.terminal_reply('a', TargetRegistryTests.status_reply(call.target, 144, 1), owner=owner)
        self.assertEqual(d.attempts['a']['event'][0], 'stopped')

    def test_wait_blocks_composed_cleanup(self):
        r, d, owner, (token,) = self.setup_driver()
        call = d.prepare(token, 0, 101, 102, owner=owner)
        d.launch_reply('a', ResultApplierTests.reply(call), owner=owner); d.deliver(owner=owner)
        resources = d.attempts['a']['resources']; wait = resources.reserve_wait(owner=owner)
        resources.register_reply(AdmittedResourcesTests.reply(call.target, wait, 0x25002, wait), owner=owner)
        d.terminal_reply('a', TargetRegistryTests.status_reply(call.target, 135, 2), owner=owner); d.deliver(owner=owner)
        reclaim, = r.issue_obligations()
        context = BoundCall(r.journal, owner, 'a' * 64, reclaim, 0x20002, call.target)
        d.reclaim(reclaim, ResultApplierTests.reply(context), owner=owner)
        resources.close_reply(AdmittedResourcesTests.reply(call.target, 101, 0x24003), owner=owner)
        with self.assertRaises(InvalidEffect): d.queue_cleanup('a', owner=owner)
        resources.release_reply(AdmittedResourcesTests.reply(call.target, wait, 0x25005), owner=owner)
        d.queue_cleanup('a', owner=owner); d.deliver(owner=owner)
        self.assertEqual(d.attempts, {})


class AdmittedResourcesTests(unittest.TestCase):
    def setup_resources(self):
        helper = TargetRegistryTests()
        r, a, registry, owner = helper.setup_registry()
        target = helper.launch(r, a, registry, owner)
        resources = AdmittedResources(registry, target, 101, owner=owner)
        return r, a, registry, owner, target, resources

    @staticmethod
    def reply(target, resource, syscall, result=0):
        return dict(schema='abi6-resource-return-v1', profile=PROFILE, producer='a' * 64,
                    target=target, resource=resource, syscall=syscall, result=result)

    def register(self, resources, owner):
        token = resources.reserve_wait(owner=owner)
        resources.register_reply(self.reply(resources.target, token, 0x25002, token), owner=owner)
        return token

    def test_wait_release_required_after_native_reclaim(self):
        r, a, registry, owner, target, resources = self.setup_resources()
        self.register(resources, owner)
        resources.close_reply(self.reply(target, 101, 0x24003), owner=owner)
        TargetRegistryTests().reclaim(r, a, registry, owner, target)
        with self.assertRaises(InvalidEffect): resources.cleaned_event(owner=owner)
        self.assertTrue(r.model.state['a'].owned)

    def test_all_cleanup_orders_preserve_ownership_until_complete(self):
        for order in itertools.permutations(('reader', 'wait', 'target')):
            r, a, registry, owner, target, resources = self.setup_resources()
            wait = self.register(resources, owner)
            for index, action in enumerate(order):
                if action == 'reader': resources.close_reply(self.reply(target, 101, 0x24003), owner=owner)
                elif action == 'wait': resources.release_reply(self.reply(target, wait, 0x25005), owner=owner)
                else: TargetRegistryTests().reclaim(r, a, registry, owner, target)
                self.assertTrue(r.model.state['a'].owned)
                if index < 2:
                    with self.assertRaises(InvalidEffect): resources.cleaned_event(owner=owner)
            r.batch([resources.cleaned_event(owner=owner)])
            registry.retire(target, owner=owner)
            self.assertEqual(registry.slots, {})
            self.assertIsNone(registry._wait_holder)

    def test_pending_registration_blocks_release_and_cleanup(self):
        r, a, registry, owner, target, resources = self.setup_resources()
        wait = resources.reserve_wait(owner=owner)
        with self.assertRaises(InvalidEffect): resources.register_reply(self.reply(target, wait, 0x25002, None), owner=owner)
        with self.assertRaises(InvalidEffect): resources.release_reply(self.reply(target, wait, 0x25005), owner=owner)
        resources.close_reply(self.reply(target, 101, 0x24003), owner=owner)
        TargetRegistryTests().reclaim(r, a, registry, owner, target)
        with self.assertRaises(InvalidEffect): resources.cleaned_event(owner=owner)
        self.assertIs(registry._wait_holder, resources)
        self.assertEqual(registry._wait_generation, 0)

    def test_wait_budget_and_stale_token_rejection(self):
        r, a, registry, owner, target, resources = self.setup_resources()
        for generation in range(1, 65):
            token = self.register(resources, owner)
            self.assertEqual(token, 0xe1000000 | generation)
            if generation > 1:
                with self.assertRaises(InvalidEffect): resources.release_reply(self.reply(target, token - 1, 0x25005), owner=owner)
            resources.release_reply(self.reply(target, token, 0x25005), owner=owner)
        with self.assertRaises(InvalidEffect): resources.reserve_wait(owner=owner)
        self.assertEqual(registry._wait_generation, 64)

    def test_selected_errors_and_status_do_not_release_owned_resources(self):
        r, a, registry, owner, target, resources = self.setup_resources()
        wait = resources.reserve_wait(owner=owner)
        self.assertFalse(resources.register_reply(self.reply(target, wait, 0x25002, -22), owner=owner))
        self.assertIsNone(registry._wait_holder)
        self.assertEqual(registry._wait_generation, 0)
        self.assertEqual(self.register(resources, owner), wait)
        for error in (-13, -9, -22):
            self.assertFalse(resources.release_reply(self.reply(target, wait, 0x25005, error), owner=owner))
        for syscall in (0x25003, 0x25004):
            with self.assertRaises(InvalidEffect): resources.release_reply(self.reply(target, wait, syscall, 3), owner=owner)
        self.assertFalse(resources.close_reply(self.reply(target, 101, 0x24003, -13), owner=owner))
        self.assertTrue(resources.reader_open)
        self.assertEqual(resources.wait, wait)

    def test_two_targets_share_one_wait_slot(self):
        r = JournalRuntime([Service('a'), Service('b')]); owner = object()
        a = ResultApplier(r, owner=owner, producer='a' * 64); registry = TargetRegistry(a)
        r.start(['a', 'b']); tokens = r.issue_obligations(); resources = []
        for slot, token in enumerate(tokens):
            target = registry.reserve(token, slot, owner=owner)
            call = a.bind(token, 0x23001, target, owner=owner)
            a.apply(call, ResultApplierTests.reply(call), owner=owner)
            registry.accept_launch(target, owner=owner)
            resources.append(AdmittedResources(registry, target, 101 + slot, owner=owner))
        wait = self.register(resources[0], owner)
        with self.assertRaises(InvalidEffect): resources[1].reserve_wait(owner=owner)
        resources[0].release_reply(self.reply(resources[0].target, wait, 0x25005), owner=owner)
        self.assertEqual(self.register(resources[1], owner), wait + 1)

    def test_identity_and_no_wait_cleanup(self):
        r, a, registry, owner, target, resources = self.setup_resources()
        with self.assertRaises(InvalidEffect): AdmittedResources(registry, target, 102, owner=owner)
        for field, value in [('target', target + 1), ('producer', 'b' * 64),
                             ('resource', True), ('result', True), ('result', -9)]:
            reply = self.reply(target, 101, 0x24003); reply[field] = value
            with self.assertRaises(InvalidEffect): resources.close_reply(reply, owner=owner)
        with self.assertRaises(InvalidEffect): resources.close_reply(self.reply(target, 101, 0x24003), owner=object())
        r.model.state['a'].generation = 2
        with self.assertRaises(InvalidEffect): resources.cleaned_event(owner=owner)
        r.model.state['a'].generation = 1
        resources.close_reply(self.reply(target, 101, 0x24003), owner=owner)
        with self.assertRaises(InvalidEffect): resources.close_reply(self.reply(target, 101, 0x24003), owner=owner)
        TargetRegistryTests().reclaim(r, a, registry, owner, target)
        with self.assertRaises(InvalidEffect): resources.reserve_wait(owner=owner)
        r.batch([resources.cleaned_event(owner=owner)])
        registry.retire(target, owner=owner)
        with self.assertRaises(InvalidEffect): resources.cleaned_event(owner=owner)


class RejectedLaunchCleanupTests(unittest.TestCase):
    def setup_cleanup(self, retries=0):
        r = JournalRuntime([Service('a', retries=retries)])
        owner = object(); a = ResultApplier(r, owner=owner, producer='a' * 64)
        registry = TargetRegistry(a)
        r.start(['a']); token, = r.issue_obligations()
        target = registry.reserve(token, 0, owner=owner)
        call = a.bind(token, 0x23001, target, owner=owner)
        cleanup = RejectedLaunchCleanup(a, call, 101, 102, owner=owner)
        return r, a, registry, owner, call, cleanup

    def reject(self, r, a, registry, owner, call, cleanup, result=-22):
        reply = ResultApplierTests.reply(call); reply['result'] = result
        a.apply(call, reply, owner=owner)
        cleanup.accept_rejection(owner=owner)
        registry.accept_launch(call.target, owner=owner)
        r.batch([cleanup.failure_event(owner=owner)])
        token, = r.issue_obligations()
        return token

    @staticmethod
    def reply(endpoint, result=0):
        return dict(schema='abi6-close-v1', profile=PROFILE, producer='a' * 64,
                    endpoint=endpoint, syscall=0x24003, result=result)

    def test_both_endpoints_required(self):
        args = self.setup_cleanup(); r, a, registry, owner, call, cleanup = args
        token = self.reject(*args)
        cleanup.close_reply(self.reply(101), owner=owner)
        with self.assertRaises(InvalidEffect):
            cleanup.qualify_reclaim(token, owner=owner)
        self.assertTrue(r.model.state['a'].owned)
        self.assertEqual(r.journal.observe(token), 'issued')

    def test_local_cleanup_then_retry_without_native_reclaim(self):
        for order in [(101, 102), (102, 101)]:
            args = self.setup_cleanup(retries=1); r, a, registry, owner, call, cleanup = args
            token = self.reject(*args)
            self.assertEqual(registry.slots, {})
            for endpoint in order: self.assertTrue(cleanup.close_reply(self.reply(endpoint), owner=owner))
            self.assertEqual(cleanup.qualify_reclaim(token, owner=owner),
                             ('local-cleanup-v1', token, 'rejected-launch-endpoints-closed'))
            with self.assertRaises(InvalidEffect): cleanup.cleaned_event(owner=owner)
            r.acknowledge(token, 'executed')
            self.assertTrue(r.model.state['a'].owned)
            r.batch([cleanup.cleaned_event(owner=owner)])
            self.assertFalse(r.model.state['a'].owned)
            r.batch(now=1); new_token, = r.issue_obligations()
            self.assertEqual(new_token[5:8], ('a', 2, 'launch'))
            self.assertEqual(registry.reserve(new_token, 0, owner=owner), call.target)
            self.assertEqual(a.last_applied[0], call.token)  # No native reclaim call applied.
            with self.assertRaises(InvalidEffect): cleanup.cleaned_event(owner=owner)

    def test_unknown_and_admitted_launch_do_not_open_cleanup(self):
        for outcome in ('unknown', 'executed'):
            r, a, registry, owner, call, cleanup = self.setup_cleanup()
            if outcome == 'unknown': r.acknowledge(call.token, 'unknown')
            else: a.apply(call, ResultApplierTests.reply(call), owner=owner)
            with self.assertRaises(InvalidEffect): cleanup.accept_rejection(owner=owner)
            with self.assertRaises(InvalidEffect): cleanup.close_reply(self.reply(101), owner=owner)
            with self.assertRaises(InvalidEffect): cleanup.failure_event(owner=owner)
            self.assertEqual(cleanup.endpoints, {101: True, 102: True})

    def test_failed_malformed_and_duplicate_close_preserve_inventory(self):
        args = self.setup_cleanup(); r, a, registry, owner, call, cleanup = args
        self.reject(*args)
        for result in (-13, -22): self.assertFalse(cleanup.close_reply(self.reply(101, result), owner=owner))
        for field, value in [('result', None), ('result', True), ('result', -9),
                             ('endpoint', 999), ('producer', 'b' * 64), ('syscall', 0x20002)]:
            reply = self.reply(101); reply[field] = value
            with self.assertRaises(InvalidEffect): cleanup.close_reply(reply, owner=owner)
        self.assertEqual(cleanup.endpoints, {101: True, 102: True})
        cleanup.close_reply(self.reply(101), owner=owner)
        with self.assertRaises(InvalidEffect): cleanup.close_reply(self.reply(101), owner=owner)
        self.assertTrue(cleanup.endpoints[102])

    def test_exact_call_and_owner_inventory_claim(self):
        r, a, registry, owner, call, cleanup = self.setup_cleanup()
        with self.assertRaises(InvalidEffect): RejectedLaunchCleanup(a, call, 101, 102, owner=owner)
        fake = BoundCall(r.journal, owner, 'a' * 64, call.token, call.syscall, call.target)
        with self.assertRaises(InvalidEffect): RejectedLaunchCleanup(a, fake, 101, 102, owner=owner)
        with self.assertRaises(InvalidEffect): cleanup.accept_rejection(owner=object())
        self.assertEqual(len(a._cleanup_claims), 1)

    def test_permission_rejection_is_permanent_and_errno_retained(self):
        args = self.setup_cleanup(retries=1); r, a, registry, owner, call, cleanup = args
        self.reject(*args, result=-13)
        self.assertEqual(cleanup.verdict[3], -13)
        self.assertEqual(cleanup.failure_event(owner=owner)[0], 'denied')
        self.assertFalse(r.model.state['a'].retry_allowed)

    def test_stale_generation_cannot_close_or_qualify(self):
        args = self.setup_cleanup(); r, a, registry, owner, call, cleanup = args
        token = self.reject(*args)
        r.model.state['a'].generation = 2
        with self.assertRaises(InvalidEffect): cleanup.close_reply(self.reply(101), owner=owner)
        with self.assertRaises(InvalidEffect): cleanup.qualify_reclaim(token, owner=owner)
        self.assertEqual(cleanup.endpoints, {101: True, 102: True})

    def test_reclaim_identity_and_duplicate_rejection(self):
        args = self.setup_cleanup(); r, a, registry, owner, call, cleanup = args
        token = self.reject(*args)
        with self.assertRaises(InvalidEffect): cleanup.accept_rejection(owner=owner)
        for endpoint in (101, 102): cleanup.close_reply(self.reply(endpoint), owner=owner)
        with self.assertRaises(InvalidEffect): cleanup.qualify_reclaim(call.token, owner=owner)
        wrong = list(token); wrong[6] += 1
        with self.assertRaises(InvalidEffect): cleanup.qualify_reclaim(tuple(wrong), owner=owner)
        self.assertIsNone(cleanup.reclaim)
        fact = cleanup.qualify_reclaim(token, owner=owner)
        self.assertEqual(cleanup.qualify_reclaim(token, owner=owner), fact)
        self.assertEqual(r.journal.observe(token), 'issued')

    def test_unknown_local_reclaim_cannot_complete(self):
        args = self.setup_cleanup(); r, a, registry, owner, call, cleanup = args
        token = self.reject(*args)
        for endpoint in (101, 102): cleanup.close_reply(self.reply(endpoint), owner=owner)
        cleanup.qualify_reclaim(token, owner=owner)
        r.acknowledge(token, 'unknown')
        with self.assertRaises(InvalidEffect): cleanup.cleaned_event(owner=owner)
        self.assertTrue(r.model.state['a'].owned)


class TargetRegistryTests(unittest.TestCase):
    def test_terminal_projection_is_pure_and_kind_preserving(self):
        r, a, registry, owner = self.setup_registry()
        target = self.launch(r, a, registry, owner)
        before = JournalRuntimeTests.snapshot(r)
        self.assertIsNone(registry.terminal_event(self.status_reply(target), owner=owner))
        for result, kind, event, detail in [(144, 1, 'exit', 143),
                (144, 3, 'stopped', 143), (135, 2, 'fault', 134)]:
            self.assertEqual(registry.terminal_event(self.status_reply(target, result, kind), owner=owner),
                             (event, 'a', 1, 'boot-1', detail))
        self.assertEqual(JournalRuntimeTests.snapshot(r), before)
        with self.assertRaises(InvalidEffect):
            registry.terminal_event(self.status_reply(target, 144, 3), owner=object())

    def test_projected_stop_drives_reclaim_but_not_cleanup(self):
        r, a, registry, owner = self.setup_registry()
        target = self.launch(r, a, registry, owner)
        event = registry.terminal_event(self.status_reply(target, 144, 3), owner=owner)
        r.batch([event])
        self.assertEqual(r.model.state['a'].terminal, 'stopped')
        token, = r.issue_obligations()
        self.assertEqual(token[7], 'reclaim')
        call = a.bind(token, 0x20002, target, owner=owner)
        a.apply(call, ResultApplierTests.reply(call), owner=owner)
        registry.accept_reclaim(target, owner=owner)
        self.assertTrue(r.model.state['a'].owned)
        with self.assertRaises(InvalidEffect):
            registry.retire(target, owner=owner)
        # Separate fixture evidence for all model-owned resources, not native status.
        r.batch([('cleaned', 'a', 1, 'boot-1', 0)])
        registry.retire(target, owner=owner)
        self.assertEqual(registry.slots, {})

    def test_delayed_projected_stop_cannot_terminate_replacement(self):
        r, a, registry, owner = self.setup_registry()
        target = self.launch(r, a, registry, owner)
        event = registry.terminal_event(self.status_reply(target, 144, 3), owner=owner)
        self.reclaim(r, a, registry, owner, target)
        r.batch([('cleaned', 'a', 1, 'boot-1', 0)])
        registry.retire(target, owner=owner)
        self.launch(r, a, registry, owner)
        r.batch([event])
        self.assertEqual(r.model.state['a'].generation, 2)
        self.assertIsNone(r.model.state['a'].terminal)
        self.assertTrue(r.model.state['a'].launch_pending)


    def setup_registry(self):
        r = JournalRuntime([Service('a')]); owner = object()
        a = ResultApplier(r, owner=owner, producer='a' * 64)
        return r, a, TargetRegistry(a), owner

    def launch(self, r, a, registry, owner):
        r.start(['a']); token, = r.issue_obligations()
        target = registry.reserve(token, 0, owner=owner)
        call = a.bind(token, 0x23001, target, owner=owner)
        a.apply(call, ResultApplierTests.reply(call), owner=owner)
        registry.accept_launch(target, owner=owner)
        return target

    @staticmethod
    def status_reply(target, result=0, kind=0):
        return dict(schema='abi6-status-v1', profile=PROFILE, producer='a' * 64,
                    target=target, syscall=0x20001, result=result, kind=kind)

    def reclaim(self, r, a, registry, owner, target):
        generation = r.model.state['a'].generation
        r.batch([('fault', 'a', generation, 'boot-1', 0)])
        token, = r.issue_obligations()
        call = a.bind(token, 0x20002, target, owner=owner)
        a.apply(call, ResultApplierTests.reply(call), owner=owner)
        return registry.accept_reclaim(target, owner=owner)

    def test_native_kind_and_detail_remain_distinct(self):
        r, a, registry, owner = self.setup_registry()
        target = self.launch(r, a, registry, owner)
        before = JournalRuntimeTests.snapshot(r)
        self.assertIsNone(registry.status(self.status_reply(target), owner=owner))
        for result, kind, label, detail in [(135, 1, 'normal', 134), (135, 2, 'fault', 134),
                                           (144, 1, 'normal', 143), (144, 3, 'stopped', 143)]:
            self.assertEqual(registry.status(self.status_reply(target, result, kind), owner=owner),
                             ('native-terminal-v1', 'a', 1, 'boot-1', target, label, detail))
        self.assertEqual(JournalRuntimeTests.snapshot(r), before)
        self.assertTrue(r.model.state['a'].launch_pending)

    def test_stale_model_generation_cannot_receive_old_target_fact(self):
        r, a, registry, owner = self.setup_registry()
        target = self.launch(r, a, registry, owner)
        r.model.state['a'].generation = 2
        with self.assertRaises(InvalidEffect):
            registry.status(self.status_reply(target, 135, 2), owner=owner)

    def test_cleanup_fact_precedes_retirement_and_reuse(self):
        r, a, registry, owner = self.setup_registry()
        target = self.launch(r, a, registry, owner)
        fact = self.reclaim(r, a, registry, owner, target)
        self.assertEqual(fact, ('native-cleanup-v1', 'a', 1, 'boot-1', target))
        self.assertTrue(r.model.state['a'].owned)
        with self.assertRaises(InvalidEffect):
            registry.retire(target, owner=owner)
        with self.assertRaises(InvalidEffect):
            registry.status(self.status_reply(target), owner=owner)
        r.batch([('cleaned', 'a', 1, 'boot-1', 0)])
        registry.retire(target, owner=owner)
        replacement = self.launch(r, a, registry, owner)
        self.assertEqual((target, replacement), (0xb0000101, 0xb0000201))
        with self.assertRaises(InvalidEffect):
            registry.status(self.status_reply(target), owner=owner)

    def test_native_generation_is_independent_of_service_generation(self):
        r, a, registry, owner = self.setup_registry()
        first = self.launch(r, a, registry, owner)
        self.reclaim(r, a, registry, owner, first)
        r.batch([('cleaned', 'a', 1, 'boot-1', 0)])
        registry.retire(first, owner=owner)
        r.start(['a']); token, = r.issue_obligations()
        target = registry.reserve(token, 1, owner=owner)
        self.assertEqual((token[6], target), (2, 0xb0000102))
        call = a.bind(token, 0x23001, target, owner=owner)
        a.apply(call, ResultApplierTests.reply(call), owner=owner)
        registry.accept_launch(target, owner=owner)
        fact = registry.status(self.status_reply(target, 1, 1), owner=owner)
        self.assertEqual(fact[1:5], ('a', 2, 'boot-1', target))
        self.assertEqual(registry.generations, [1, 1])

    def test_native_slot_generations_exhaust_without_wrapping(self):
        r, a, registry, owner = self.setup_registry()
        for generation in range(1, 4):
            target = self.launch(r, a, registry, owner)
            self.assertEqual(target, 0xb0000001 | (generation << 8))
            self.reclaim(r, a, registry, owner, target)
            r.batch([('cleaned', 'a', generation, 'boot-1', 0)])
            registry.retire(target, owner=owner)
        r.start(['a']); token, = r.issue_obligations()
        with self.assertRaises(InvalidEffect):
            registry.reserve(token, 0, owner=owner)
        self.assertEqual(registry.generations, [3, 0])
        self.assertEqual(registry.slots, {})

    def test_unknown_launch_preserves_reservation(self):
        r, a, registry, owner = self.setup_registry()
        r.start(['a']); token, = r.issue_obligations()
        target = registry.reserve(token, 0, owner=owner)
        r.acknowledge(token, 'unknown')
        before = deepcopy(registry.slots)
        with self.assertRaises(InvalidEffect):
            registry.accept_launch(target, owner=owner)
        with self.assertRaises(InvalidEffect):
            registry.retire(target, owner=owner)
        self.assertEqual(registry.slots, before)
        self.assertEqual(registry.generations, [0, 0])
        self.assertEqual(r.journal.observe(token), 'unknown')

    def test_rejected_launch_frees_only_native_reservation(self):
        r, a, registry, owner = self.setup_registry()
        r.start(['a']); token, = r.issue_obligations()
        target = registry.reserve(token, 0, owner=owner)
        call = a.bind(token, 0x23001, target, owner=owner)
        a.apply(call, ResultApplierTests.reply(call, -22), owner=owner)
        self.assertEqual(registry.accept_launch(target, owner=owner), 'rejected-before-effects')
        self.assertEqual(registry.slots, {})
        self.assertEqual(registry.generations, [0, 0])
        self.assertTrue(r.model.state['a'].owned)

    def test_registry_ownership_binding_and_duplicate_adoption(self):
        r, a, registry, owner = self.setup_registry()
        with self.assertRaises(InvalidEffect):
            TargetRegistry(a)
        r.start(['a']); token, = r.issue_obligations()
        for slot in [True, 2, -1]:
            with self.assertRaises(InvalidEffect):
                registry.reserve(token, slot, owner=owner)
        target = registry.reserve(token, 0, owner=owner)
        with self.assertRaises(InvalidEffect):
            registry.reserve(token, 1, owner=owner)
        wrong = a.bind(token, 0x23001, 0xb0000102, owner=owner)
        a.apply(wrong, ResultApplierTests.reply(wrong), owner=owner)
        with self.assertRaises(InvalidEffect):
            registry.accept_launch(target, owner=owner)
        self.assertEqual(registry.slots[0]['phase'], 'reserved')
        r, a, registry, owner = self.setup_registry()
        target = self.launch(r, a, registry, owner)
        with self.assertRaises(InvalidEffect):
            registry.accept_launch(target, owner=owner)
        with self.assertRaises(InvalidEffect):
            registry.status(self.status_reply(target), owner=object())

    def test_status_metadata_and_unselected_faults_reject(self):
        r, a, registry, owner = self.setup_registry()
        target = self.launch(r, a, registry, owner)
        reply = self.status_reply(target, 135, 2)
        for field, value in [('profile', 'abi9'), ('producer', 'b' * 64),
                             ('target', 0xb0000102), ('syscall', 0x25001),
                             ('kind', True), ('result', -9), ('result', 142)]:
            with self.assertRaises(InvalidEffect):
                registry.status(reply | {field: value}, owner=owner)
        for result, kind in [(0, 1), (135, 3), (144, 2), (257, 1)]:
            with self.assertRaises(InvalidEffect):
                registry.status(self.status_reply(target, result, kind), owner=owner)
        self.assertTrue(r.model.state['a'].owned)


class ResultApplierTests(unittest.TestCase):
    def setup_applier(self):
        r = JournalRuntime([Service('a')]); owner = object()
        a = ResultApplier(r, owner=owner, producer='a' * 64)
        r.start(['a']); token, = r.issue_obligations()
        call = a.bind(token, 0x23001, 0xb0000101, owner=owner)
        return r, a, call, owner

    @staticmethod
    def reply(call, result=None):
        if result is None:
            result = call.target if call.syscall == 0x23001 else 0
        return dict(schema='abi6-return-v1', profile=PROFILE, producer=call.producer,
                    token=call.token, syscall=call.syscall, target=call.target, result=result)

    def test_application_and_observations_are_separate(self):
        r, a, call, owner = self.setup_applier()
        before = JournalRuntimeTests.snapshot(r)
        verdict = a.apply(call, self.reply(call), owner=owner)
        self.assertEqual(verdict[1], 'executed')
        self.assertEqual(JournalRuntimeTests.snapshot(r), before)
        self.assertEqual(r.journal.observe(call.token), 'executed')
        self.assertTrue(r.model.state['a'].launch_pending)
        r.batch([('launched', 'a', 1, 'boot-1', 0)])
        r.batch([('fault', 'a', 1, 'boot-1', 0)])
        reclaim, = r.issue_obligations()
        cleanup = a.bind(reclaim, 0x20002, call.target, owner=owner)
        a.apply(cleanup, self.reply(cleanup), owner=owner)
        self.assertTrue(r.model.state['a'].owned)
        r.batch([('cleaned', 'a', 1, 'boot-1', 0)])
        self.assertFalse(r.model.state['a'].owned)
        self.assertEqual(a.bindings, {})

    def test_fabricated_equivalent_context_cannot_apply(self):
        r, a, call, owner = self.setup_applier()
        other = BoundCall(r.journal, owner, call.producer, call.token, call.syscall, call.target)
        with self.assertRaises(InvalidEffect):
            a.apply(other, self.reply(other), owner=owner)
        self.assertEqual(r.journal.observe(call.token), 'issued')
        self.assertIs(a.bindings[call.token], call)

    def test_wrong_owner_malformed_and_duplicate_application(self):
        r, a, call, owner = self.setup_applier()
        with self.assertRaises(InvalidEffect):
            a.apply(call, self.reply(call), owner=object())
        with self.assertRaises(InvalidEffect):
            a.apply(call, self.reply(call) | {'producer': 'b' * 64}, owner=owner)
        self.assertIsNone(a.last_attempt)
        self.assertFalse(r.failed)
        with self.assertRaises(InvalidEffect):
            a.bind(call.token, call.syscall, call.target, owner=owner)
        verdict = a.apply(call, self.reply(call, -22), owner=owner)
        self.assertEqual(verdict[1], 'rejected-before-effects')
        self.assertTrue(r.model.state['a'].owned)
        with self.assertRaises(InvalidEffect):
            a.apply(call, self.reply(call, -22), owner=owner)
        self.assertEqual(a.last_applied, (call.token, verdict))

    def test_requalification_rejects_stale_verdict_after_unknown(self):
        r, a, call, owner = self.setup_applier()
        verdict = call.qualify(self.reply(call), owner=owner)
        r.acknowledge(call.token, 'unknown')
        with self.assertRaises(InvalidEffect):
            a.apply(call, self.reply(call), owner=owner)
        self.assertEqual(verdict[1], 'executed')
        self.assertEqual(r.journal.observe(call.token), 'unknown')
        self.assertIsNone(a.last_applied)

    def test_guard_blocks_reentrant_apply_and_lifecycle(self):
        r, a, call, owner = self.setup_applier()
        acknowledge = r.acknowledge
        checked = []
        def nested(token, outcome):
            for action in (lambda: a.apply(call, self.reply(call), owner=owner),
                           lambda: a.bind(token, call.syscall, call.target, owner=owner),
                           lambda: r.batch()):
                with self.assertRaises(InvalidEffect):
                    action()
                checked.append(True)
            return acknowledge(token, outcome)
        with patch.object(r, 'acknowledge', side_effect=nested):
            a.apply(call, self.reply(call), owner=owner)
        self.assertEqual(len(checked), 3)
        self.assertFalse(a.busy)
        self.assertFalse(r.running)

    def test_acknowledgment_failure_closes_and_preserves_attempt(self):
        r, a, call, owner = self.setup_applier()
        with patch.object(r, 'acknowledge', side_effect=MemoryError):
            with self.assertRaises(MemoryError):
                a.apply(call, self.reply(call), owner=owner)
        self.assertTrue(r.failed)
        self.assertEqual(r.journal.observe(call.token), 'unknown')
        self.assertEqual(a.last_attempt[0], call.token)
        self.assertEqual(a.last_attempt[1][1], 'executed')
        self.assertIsNone(a.last_applied)
        self.assertIs(a.bindings[call.token], call)
        with self.assertRaises(InvalidEffect):
            a.apply(call, self.reply(call), owner=owner)

    def test_failure_after_ack_preserves_known_terminal_result(self):
        r, a, call, owner = self.setup_applier()
        acknowledge = r.acknowledge
        def fail_after(token, outcome):
            acknowledge(token, outcome)
            raise RuntimeError('after commit')
        with patch.object(r, 'acknowledge', side_effect=fail_after):
            with self.assertRaises(RuntimeError):
                a.apply(call, self.reply(call), owner=owner)
        self.assertTrue(r.failed)
        self.assertEqual(r.journal.observe(call.token), 'executed')
        self.assertTrue(r.model.state['a'].owned)
        self.assertIsNone(a.last_applied)

    def test_single_applier_claim_and_unexpected_acknowledgment(self):
        r, a, call, owner = self.setup_applier()
        with self.assertRaises(InvalidEffect):
            ResultApplier(r, owner=owner, producer=call.producer)
        with patch.object(r, 'acknowledge', return_value='replayed'):
            with self.assertRaises(InvalidEffect):
                a.apply(call, self.reply(call), owner=owner)
        self.assertTrue(r.failed)
        self.assertEqual(r.journal.observe(call.token), 'unknown')
        with self.assertRaises(InvalidEffect):
            ResultApplier(r, owner=owner, producer=call.producer)


class ConfirmedResultTests(unittest.TestCase):
    def setup_call(self, kind='stop', issue=True):
        journal = EventJournal(epoch='boot-1', revision='config-1', services=['a'])
        ticket = journal.reserve(); journal.begin(ticket)
        token, = journal.capture(ticket, ((kind, 'a', 7, 'activation', 1),))
        if issue:
            journal.issue(token)
        owner = object()
        syscall = {'launch': 0x23001, 'stop': 0x20007, 'reclaim': 0x20002}.get(kind, 0x20007)
        return journal, token, owner, syscall

    def bind(self, kind='stop'):
        journal, token, owner, syscall = self.setup_call(kind)
        call = BoundCall(journal, owner, 'a' * 64, token, syscall, 0xb0000101)
        reply = dict(schema='abi6-return-v1', profile=PROFILE, producer='a' * 64,
                     token=token, syscall=syscall, target=call.target,
                     result=call.target if kind == 'launch' else 0)
        return call, reply, owner

    def test_successes_are_detached_facts_not_lifecycle_mutation(self):
        for kind, fact in [('launch', 'instance-admitted'), ('stop', 'target-terminal'),
                           ('reclaim', 'target-reclaimed')]:
            call, reply, owner = self.bind(kind)
            before = deepcopy((call.journal.live, call.journal.history))
            verdict = call.qualify(reply, owner=owner)
            self.assertEqual(verdict, ('confirmed-result-v1', 'executed', call.syscall,
                                      reply['result'], call.target, fact))
            self.assertEqual((call.journal.live, call.journal.history), before)
            reply['result'] = -9
            self.assertEqual(verdict[1], 'executed')

    def test_exact_negative_returns_preserve_errno(self):
        cases = [('launch', [-13, -22, -16, -28, -14]), ('stop', [-13, -9]),
                 ('reclaim', [-13, -9, -16])]
        for kind, errors in cases:
            call, reply, owner = self.bind(kind)
            for error in errors:
                reply['result'] = error
                self.assertEqual(call.qualify(reply, owner=owner),
                                 ('confirmed-result-v1', 'rejected-before-effects',
                                  call.syscall, error, call.target, 'none'))
                self.assertEqual(call.journal.observe(call.token), 'issued')

    def test_unknown_cannot_be_resolved_by_later_ebadf(self):
        call, reply, owner = self.bind()
        call.journal.acknowledge(call.token, 'unknown')
        reply['result'] = -9
        with self.assertRaises(InvalidEffect):
            call.qualify(reply, owner=owner)
        self.assertEqual(call.journal.observe(call.token), 'unknown')

    def test_owner_and_all_identity_fields_are_exact(self):
        call, reply, owner = self.bind()
        with self.assertRaises(InvalidEffect):
            call.qualify(reply, owner=object())
        changes = [('schema', 'wait-result-v1'), ('profile', 'aether-abi9'),
                   ('producer', 'b' * 64), ('syscall', 0x25001), ('target', 0xb0000201),
                   ('token', call.token[:6] + (8,) + call.token[7:])]
        for field, value in changes:
            with self.assertRaises(InvalidEffect):
                call.qualify(reply | {field: value}, owner=owner)
        boolean_token = list(call.token); boolean_token[3] = True
        with self.assertRaises(InvalidEffect):
            call.qualify(reply | {'token': tuple(boolean_token)}, owner=owner)
        self.assertEqual(call.journal.observe(call.token), 'issued')

    def test_nonissued_closed_and_unsupported_bindings_reject(self):
        j, token, owner, syscall = self.setup_call(issue=False)
        with self.assertRaises(InvalidEffect):
            BoundCall(j, owner, 'a' * 64, token, syscall, 0xb0000101)
        j.issue(token)
        for target in [0, True, 0xb0000103, 0xb0000401]:
            with self.assertRaises(InvalidEffect):
                BoundCall(j, owner, 'a' * 64, token, syscall, target)
        for producer in ['a' * 63, 'g' * 64, 'a' * 65]:
            with self.assertRaises(InvalidEffect):
                BoundCall(j, owner, producer, token, syscall, 0xb0000101)
        with self.assertRaises(InvalidEffect):
            BoundCall(j, None, 'a' * 64, token, syscall, 0xb0000101)
        j.driver_lost()
        with self.assertRaises(InvalidEffect):
            BoundCall(j, owner, 'a' * 64, token, syscall, 0xb0000101)
        j, token, owner, syscall = self.setup_call('force')
        with self.assertRaises(InvalidEffect):
            BoundCall(j, owner, 'a' * 64, token, syscall, 0xb0000101)

    def test_malformed_or_unselected_returns_do_not_qualify(self):
        call, reply, owner = self.bind()
        for result in [True, None, 'EOF', 1, 143, -110, -5, 1 << 63, -(1 << 63) - 1]:
            with self.assertRaises(InvalidEffect):
                call.qualify(reply | {'result': result}, owner=owner)
        for candidate in [list(reply.items()), reply | {'terminal': True},
                          {k: v for k, v in reply.items() if k != 'target'}]:
            with self.assertRaises(InvalidEffect):
                call.qualify(candidate, owner=owner)
        launch, response, binding = self.bind('launch')
        with self.assertRaises(InvalidEffect):
            launch.qualify(response | {'result': 0xb0000201}, owner=binding)

    def test_repeated_calculation_then_acknowledgment_and_retirement(self):
        call, reply, owner = self.bind()
        first = call.qualify(reply, owner=owner)
        self.assertEqual(call.qualify(reply, owner=owner), first)
        call.journal.acknowledge(call.token, first[1])
        with self.assertRaises(InvalidEffect):
            call.qualify(reply, owner=owner)
        for _ in range(65):
            ticket = call.journal.reserve(); call.journal.begin(ticket)
            token, = call.journal.capture(ticket, (('stop', 'a', 7, 'activation', 1),))
            call.journal.acknowledge(token, 'rejected-before-effects')
        self.assertEqual(call.journal.observe(call.token), 'unknown')
        with self.assertRaises(InvalidEffect):
            call.qualify(reply, owner=owner)

    def test_reclaim_fact_does_not_release_model_ownership(self):
        r = JournalRuntime([Service('a')]); r.start(['a'])
        token, = r.issue_obligations(); r.acknowledge(token, 'executed')
        r.batch([('fault', 'a', 1, 'boot-1', 0)])
        reclaim, = r.issue_obligations(); owner = object()
        call = BoundCall(r.journal, owner, 'a' * 64, reclaim, 0x20002, 0xb0000101)
        reply = dict(schema='abi6-return-v1', profile=PROFILE, producer='a' * 64,
                     token=reclaim, syscall=0x20002, target=call.target, result=0)
        before = JournalRuntimeTests.snapshot(r)
        self.assertEqual(call.qualify(reply, owner=owner)[-1], 'target-reclaimed')
        self.assertEqual(JournalRuntimeTests.snapshot(r), before)
        self.assertTrue(r.model.state['a'].owned)


class QueuedRuntimeTests(unittest.TestCase):
    @staticmethod
    def event(kind, value=0):
        return (kind, 'a', 1, 'boot-1', value)

    def test_unknown_retains_terminal_without_reconciliation(self):
        r = QueuedRuntime([Service('a')]); r.start(['a'])
        token, = r.issue_obligations(); r.acknowledge(token, 'unknown')
        before = JournalRuntimeTests.snapshot(r)
        serial = r.batch([self.event('fault')], now=2)
        self.assertEqual(r.peek(), (serial, 2, (self.event('fault'),)))
        self.assertIsNone(r.apply_next())
        self.assertEqual(JournalRuntimeTests.snapshot(r), before)
        self.assertEqual(r.journal.observe(token), 'unknown')
        self.assertTrue(r.model.state['a'].owned)

    def test_acknowledgment_allows_fifo_whole_cut_application(self):
        r = QueuedRuntime([Service('a')]); r.start(['a'])
        token, = r.issue_obligations()
        first = r.batch([self.event('launched')], now=1)
        second = r.batch([self.event('fault')], now=2)
        self.assertIsNone(r.apply_next())
        r.acknowledge(token, 'executed')
        self.assertEqual(r.apply_next(), first)
        self.assertEqual(r.model.now, 1)
        self.assertEqual(r.apply_next(), second)
        reclaim, = r.issue_obligations()
        self.assertEqual(reclaim[5:8], ('a', 1, 'reclaim'))
        self.assertEqual(r.model.now, 2)
        self.assertIsNone(r.peek())
        self.assertTrue(r.model.state['a'].owned)

    def test_capacity_overflow_closes_without_dropping_accepted_cuts(self):
        r = QueuedRuntime([Service('a')])
        for now in range(4):
            r.batch([self.event('log', now)], now=now)
        before = tuple(r.inbox)
        with self.assertRaises(InvalidEffect):
            r.batch([self.event('fault')], now=4)
        self.assertEqual(tuple(r.inbox), before)
        self.assertTrue(r.intake_lost)
        self.assertTrue(r.failed)
        self.assertEqual(r.model.events, 0)
        self.assertEqual(r.next_intake, 5)
        with self.assertRaises(InvalidEffect):
            r.apply_next()
        r.driver_lost()
        self.assertEqual(tuple(r.inbox), before)

    def test_copy_clock_and_invalid_input_precede_full_queue_failure(self):
        r = QueuedRuntime([Service('a')])
        events = [self.event('log', 'original')]
        r.batch(events, now=2)
        events.clear()
        self.assertEqual(r.peek()[2], (self.event('log', 'original'),))
        for _ in range(3):
            r.batch()
        before = tuple(r.inbox)
        for invalid, now in (([('bad',)], 2), ([], 1)):
            with self.assertRaises(Rejected):
                r.batch(invalid, now=now)
        self.assertEqual(tuple(r.inbox), before)
        self.assertFalse(r.failed)
        self.assertFalse(r.intake_lost)
        self.assertTrue(all(cut[1] == 2 for cut in r.inbox))

    def test_retained_integer_and_string_type_bounds(self):
        r = QueuedRuntime([Service('a')])
        class Decorated(str):
            pass
        for event in (('log', 'a', MAX_ID + 1, 'boot-1', 0),
                      self.event('log', 1 << 63), self.event('log', -(1 << 63) - 1),
                      self.event('log', Decorated('text'))):
            with self.assertRaises(Rejected):
                r.batch([event])
            self.assertIsNone(r.peek())
            self.assertEqual(r.next_intake, 1)
        r.batch([self.event('log', -(1 << 63)), self.event('log', (1 << 63) - 1)])
        self.assertEqual(len(r.peek()[2]), 2)

    def test_commands_cannot_pass_queued_observations(self):
        r = QueuedRuntime([Service('a')]); serial = r.batch()
        for method in (r.start, r.stop):
            with self.assertRaises(InvalidEffect):
                method(['a'])
        self.assertEqual(r.model.next_id, 1)
        self.assertEqual(r.apply_next(), serial)
        self.assertEqual(r.start(['a']), 1)

    def test_event_and_intake_id_exhaustion_preserve_queue(self):
        r = QueuedRuntime([Service('a')]); r.model.events = r.model.MAX_EVENTS - 1
        serial = r.batch(); before = tuple(r.inbox)
        with self.assertRaises(Rejected):
            r.batch()
        self.assertEqual(tuple(r.inbox), before)
        self.assertEqual(r.apply_next(), serial)
        self.assertEqual(r.model.events, r.model.MAX_EVENTS)
        r = QueuedRuntime([Service('a')]); r.next_intake = MAX_ID
        self.assertEqual(r.batch(), MAX_ID)
        before = tuple(r.inbox)
        with self.assertRaises(InvalidEffect):
            r.batch()
        self.assertEqual(tuple(r.inbox), before)
        self.assertFalse(r.failed)

    def test_capture_failure_retains_head_without_retry(self):
        r = QueuedRuntime([Service('a')]); r.start(['a'])
        token, = r.issue_obligations(); r.acknowledge(token, 'executed')
        r.batch([self.event('fault')], now=1); before = r.peek()
        with patch.object(r.journal, 'capture', side_effect=MemoryError):
            with self.assertRaises(MemoryError):
                r.apply_next()
        self.assertEqual(r.peek(), before)
        self.assertTrue(r.failed)
        self.assertEqual(r.model.effects, [('reclaim', 'a', 1)])
        self.assertEqual(r.journal.credits, 20)
        with self.assertRaises(InvalidEffect):
            r.apply_next()

    def test_equal_time_cuts_are_not_merged(self):
        r = QueuedRuntime([Service('a')]); r.start(['a'])
        token, = r.issue_obligations(); r.acknowledge(token, 'executed')
        first = r.batch([self.event('launched')], now=1)
        second = r.batch([self.event('fault')], now=1)
        self.assertEqual(len(r.inbox), 2)
        self.assertEqual(r.apply_next(), first)
        self.assertEqual(r.model.state['a'].phase, 'running')
        self.assertEqual(r.apply_next(), second)
        self.assertEqual(r.model.state['a'].phase, 'terminal')


class JournalRuntimeTests(unittest.TestCase):
    @staticmethod
    def event(r, kind, name='a', value=0):
        m = r.model
        return (kind, name, m.state[name].generation, m.epoch, value)

    @staticmethod
    def settle(r):
        tokens = r.issue_obligations()
        for token in tokens:
            r.acknowledge(token, 'executed')
        return tokens

    @staticmethod
    def snapshot(r):
        return deepcopy(({k: v for k, v in r.model.__dict__.items() if k != 'owner'},
                         r.causes, r.attributed, r.pending, r.journal.next_cut))

    def test_capacity_denial_precedes_model_mutation(self):
        r = JournalRuntime([Service('a')]); r.start(['a'])
        events = [self.event(r, 'launched')]
        before = self.snapshot(r)
        with self.assertRaises(InvalidEffect):
            r.batch(events, now=2)
        self.assertEqual(self.snapshot(r), before)
        self.assertEqual(events, [('launched', 'a', 1, 'boot-1', 0)])
        self.assertFalse(r.failed)

    def test_invalid_cut_and_event_exhaustion_do_not_reserve(self):
        r = JournalRuntime([Service('a')])
        for events, now in (([('bad',)], 0), ([], -1)):
            before = self.snapshot(r)
            with self.assertRaises(Rejected):
                r.batch(events, now=now)
            self.assertEqual(self.snapshot(r), before)
        r.model.events = r.model.MAX_EVENTS
        before = self.snapshot(r)
        with self.assertRaises(Rejected):
            r.batch()
        self.assertEqual(self.snapshot(r), before)
        self.assertEqual(r.journal.credits, 0)

    def test_twelve_effect_cut_retains_stop_cause(self):
        names = list('abcdefgh'); r = JournalRuntime([Service(n) for n in names])
        r.start(names); self.settle(r)
        for group in (names[:4], names[4:]):
            r.batch([self.event(r, 'launched', n) for n in group]); self.settle(r)
        operation = r.stop(names); self.settle(r)
        r.batch([self.event(r, 'exit', n) for n in names[:4]], now=5)
        tokens = r.issue_obligations()
        self.assertEqual([(t[7], t[5], t[6]) for t in tokens],
                         [('force', n, 1) for n in names] + [('reclaim', n, 1) for n in names[:4]])
        self.assertTrue(all(t[8:] == ('stop', operation) for t in tokens))
        self.assertEqual(r.issue_obligations(), ())
        self.assertTrue(all(s.owned for s in r.model.state.values()))

    def test_duplicate_force_occurrences_transfer_separately(self):
        r = JournalRuntime([Service('a')]); r.start(['a']); self.settle(r)
        operation = r.stop(['a']); self.settle(r)
        r.batch([self.event(r, 'launched')], now=5)
        first, second = r.issue_obligations()
        self.assertNotEqual(first, second)
        self.assertEqual(first[5:], ('a', 1, 'force', 'stop', operation))
        self.assertEqual(first[5:], second[5:])
        self.assertTrue(r.model.state['a'].owned)

    def test_background_cause_survives_history_and_unrelated_operation(self):
        r = JournalRuntime([Service('a'), Service('b')])
        first = r.start(['a']); self.settle(r)
        r.batch([self.event(r, 'launched')]); self.settle(r)
        for _ in range(65):
            r.start(['a']); self.settle(r)
        self.assertNotIn(first, [op.id for op in r.model.operations])
        other = r.start(['b']); self.settle(r)
        r.batch([self.event(r, 'fault')])
        token, = r.issue_obligations()
        self.assertEqual(token[8:], ('activation', first))
        self.assertEqual(r.model.active.id, other)
        before = self.snapshot(r)
        r.acknowledge(token, 'executed')
        self.assertEqual(self.snapshot(r), before)
        self.assertTrue(r.model.state['a'].owned)

    def test_restart_switches_cause_at_new_launch(self):
        r = JournalRuntime([Service('a')]); r.start(['a']); self.settle(r)
        r.batch([self.event(r, 'launched')]); self.settle(r)
        operation = r.stop(['a'], restart='a')
        stop, = self.settle(r)
        self.assertEqual(stop[8:], ('stop', operation))
        r.batch([self.event(r, 'exit')]); self.settle(r)
        r.batch([self.event(r, 'cleaned')])
        launch, = r.issue_obligations()
        self.assertEqual(launch[5:], ('a', 2, 'launch', 'activation', operation))

    def test_retry_keeps_original_activation_cause(self):
        r = JournalRuntime([Service('a', retries=1)])
        first = r.start(['a']); self.settle(r)
        r.batch([self.event(r, 'launched')]); self.settle(r)
        r.batch([self.event(r, 'fault')]); self.settle(r)
        r.batch([self.event(r, 'cleaned')]); self.settle(r)
        other = r.start(['a']); self.settle(r)
        self.assertNotEqual(first, other)
        r.batch(now=1)
        token, = r.issue_obligations()
        self.assertEqual(token[5:], ('a', 2, 'launch', 'activation', first))

    def test_unknown_blocks_terminal_cut_without_consuming_input(self):
        r = JournalRuntime([Service('a')]); r.start(['a'])
        token, = r.issue_obligations(); r.acknowledge(token, 'unknown')
        events = [self.event(r, 'fault')]; before = self.snapshot(r)
        with self.assertRaises(InvalidEffect):
            r.batch(events, now=2)
        self.assertEqual(self.snapshot(r), before)
        self.assertEqual(events, [('fault', 'a', 1, 'boot-1', 0)])
        self.assertEqual(r.journal.observe(token), 'unknown')

    def test_capture_failure_retains_raw_and_begun_credits(self):
        r = JournalRuntime([Service('a')])
        with patch.object(r.journal, 'capture', side_effect=MemoryError):
            with self.assertRaises(MemoryError):
                r.start(['a'])
        self.assertTrue(r.failed)
        self.assertEqual(r.journal.credits, 20)
        self.assertEqual(r.model.effects, [('launch', 'a', 1)])
        self.assertEqual(r.attributed, [('launch', 'a', 1, 'activation', 1)])
        self.assertTrue(r.model.state['a'].owned)
        with self.assertRaises(InvalidEffect):
            r.issue_obligations()

    def test_partial_transfer_preserves_unknown_and_rejected(self):
        r = JournalRuntime([Service('a'), Service('b')]); r.start(['a', 'b'])
        first, second = r.pending
        issue = r.journal.issue
        def partial(token):
            if token == second:
                raise RuntimeError('transfer failure')
            return issue(token)
        with patch.object(r.journal, 'issue', side_effect=partial):
            with self.assertRaises(RuntimeError):
                r.issue_obligations()
        self.assertTrue(r.failed)
        self.assertEqual(r.journal.observe(first), 'unknown')
        self.assertEqual(r.journal.observe(second), 'rejected-before-effects')
        self.assertTrue(all(s.owned for s in r.model.state.values()))


class EventJournalTests(unittest.TestCase):
    def journal(self):
        return EventJournal(epoch='boot-1', revision='config-1', services=list('abcdefgh'))

    def capture(self, journal, records=(('force', 'a', 1, 'stop', 2),)):
        ticket = journal.reserve()
        journal.begin(ticket)
        return journal.capture(ticket, records)

    def test_reservation_gate_preserves_unresolved_cut(self):
        j = self.journal()
        token, = self.capture(j)
        before = deepcopy((j.live, j.next_cut, j.credits))
        with self.assertRaises(InvalidEffect):
            j.reserve()
        self.assertEqual((j.live, j.next_cut, j.credits), before)
        self.assertEqual(j.observe(token), 'reserved')

    def test_cancel_only_before_mutation_and_ticket_owner(self):
        j, other = self.journal(), self.journal()
        ticket, foreign = j.reserve(), other.reserve()
        with self.assertRaises(InvalidEffect):
            j.begin(foreign)
        j.cancel(ticket)
        self.assertEqual((j.credits, j.next_cut), (0, 2))
        with self.assertRaises(InvalidEffect):
            j.begin(ticket)
        ticket = j.reserve(); j.begin(ticket)
        with self.assertRaises(InvalidEffect):
            j.cancel(ticket)
        self.assertEqual(j.credits, 20)
        self.assertEqual(j.capture(ticket, ()), ())
        self.assertEqual(j.credits, 0)

    def test_twelve_and_twenty_effect_capture(self):
        for count in (12, 20):
            j = self.journal()
            records = tuple(('force', 'abcdefgh'[i % 8], 1, 'stop', 9) for i in range(count))
            tokens = self.capture(j, records)
            self.assertEqual(len(tokens), count)
            self.assertEqual([t[4] for t in tokens], list(range(count)))
            self.assertEqual(j.raw, records)
            self.assertEqual(j.credits, 0)
            self.assertEqual(len(j.live), count)

    def test_force_occurrences_same_and_later_cut(self):
        j = self.journal()
        effect = ('force', 'a', 1, 'stop', 2)
        first, second = self.capture(j, (effect, effect))
        self.assertNotEqual(first, second)
        for token in (first, second):
            j.issue(token); j.acknowledge(token, 'executed')
        third, = self.capture(j, (effect,))
        self.assertEqual((first[3:5], second[3:5], third[3:5]), ((1, 0), (1, 1), (2, 0)))
        self.assertEqual(first[5:], third[5:])

    def test_supplied_cause_survives_operation_history_eviction(self):
        m = Model([Service('a')])
        operation, _ = m.start(['a'])
        m.batch([('launched', 'a', 1, m.epoch, 0)])
        j = self.journal()
        token, = self.capture(j, (('reclaim', 'a', 1, 'activation', operation),))
        for _ in range(65):
            m.start(['a'])
        self.assertNotIn(operation, [op.id for op in m.operations])
        self.assertEqual(token[8:], ('activation', operation))
        self.assertEqual(j.observe(token), 'reserved')
        # The journal retains supplied cause; it does not infer or authenticate it.

    def test_token_mismatch_stale_ticket_and_future_cut(self):
        j = self.journal()
        token, = self.capture(j)
        for index, value in ((0, 'other-v1'), (1, 'boot-2'), (2, 'other'),
                             (3, 2), (4, True), (5, 'b'), (6, 2),
                             (7, 'stop'), (8, 'activation'), (9, 3)):
            changed = list(token); changed[index] = value
            with self.assertRaises(InvalidEffect):
                j.issue(tuple(changed))
        self.assertEqual(j.issue(token), token)
        with self.assertRaises(InvalidEffect):
            j.issue(token)
        self.assertEqual(j.observe(token), 'issued')

    def test_acknowledgment_rules_and_unknown_capacity(self):
        j = self.journal()
        token, = self.capture(j)
        for outcome in ('executed', 'unknown'):
            with self.assertRaises(InvalidEffect):
                j.acknowledge(token, outcome)
        j.issue(token)
        self.assertEqual(j.acknowledge(token, 'unknown'), 'recorded')
        self.assertEqual(j.acknowledge(token, 'unknown'), 'replayed')
        with self.assertRaises(InvalidEffect):
            j.acknowledge(token, 'executed')
        with self.assertRaises(InvalidEffect):
            j.reserve()
        self.assertEqual(len(j.live), 1)

    def test_generation_retirement_poison_preserves_reservation(self):
        j = self.journal()
        token, = self.capture(j, (('force', 'a', 2, 'stop', 2),))
        j.acknowledge(token, 'rejected-before-effects')
        ticket = j.reserve(); j.begin(ticket)
        with self.assertRaises(InvalidEffect):
            j.capture(ticket, (('force', 'a', 1, 'stop', 2),))
        self.assertTrue(j.closed)
        self.assertEqual((j.credits, j.phase), (20, 'recording'))
        self.assertEqual(j.generations['a'], 2)

    def test_bad_capture_cannot_cancel_or_publish_partial_tokens(self):
        valid = ('force', 'a', 1, 'stop', 2)
        for records in ((valid,) * 21, (valid, ('force', 'b', True, 'stop', 2)),
                        (valid, ('force', 'b', 1, 'invented', 2))):
            j = self.journal(); ticket = j.reserve(); j.begin(ticket)
            with self.assertRaises(InvalidEffect):
                j.capture(ticket, records)
            self.assertEqual(j.live, {})
            self.assertEqual(j.generations, dict.fromkeys('abcdefgh', 0))
            self.assertTrue(j.closed)
            self.assertEqual(j.credits, 20)
            with self.assertRaises(InvalidEffect):
                j.cancel(ticket)

    def test_history_and_serial_exhaustion(self):
        j = self.journal()
        first = None
        for _ in range(65):
            token, = self.capture(j)
            if first is None:
                first = token
            j.acknowledge(token, 'rejected-before-effects')
        self.assertEqual(len(j.history), 64)
        self.assertEqual(j.acknowledge(first, 'executed'), 'retired')
        self.assertEqual(j.observe(first), 'unknown')
        j.next_cut = MAX_ID
        ticket = j.reserve(); j.cancel(ticket)
        with self.assertRaises(InvalidEffect):
            j.reserve()
        self.assertEqual(j.next_cut, MAX_ID + 1)

    def test_capture_allocation_failure_retains_raw_and_credits(self):
        j = self.journal(); ticket = j.reserve(); j.begin(ticket)
        records = (('force', 'a', 1, 'stop', 2),)
        with patch('prototypes.runtime_model.event_journal.enumerate', side_effect=MemoryError):
            with self.assertRaises(MemoryError):
                j.capture(ticket, records)
        self.assertEqual(j.raw, records)
        self.assertEqual(j.live, {})
        self.assertEqual(j.credits, 20)
        self.assertTrue(j.closed)
        j.driver_lost()
        self.assertEqual(j.credits, 20)

    def test_driver_loss_preserves_unknown_and_begun_credits(self):
        j = self.journal()
        first, second = self.capture(j, (('force', 'a', 1, 'stop', 2),) * 2)
        j.issue(first); j.driver_lost()
        self.assertEqual(j.observe(first), 'unknown')
        self.assertEqual(j.observe(second), 'rejected-before-effects')
        with self.assertRaises(InvalidEffect):
            j.acknowledge(first, 'executed')
        for begun, expected in ((False, 0), (True, 20)):
            j = self.journal(); ticket = j.reserve()
            if begun:
                j.begin(ticket)
            j.driver_lost()
            self.assertEqual(j.credits, expected)
            with self.assertRaises(InvalidEffect):
                j.reserve()


class EventAccountingBoundaryTests(unittest.TestCase):
    """Reachable integration gaps, not a native force/recovery policy."""

    @staticmethod
    def observation(m, kind, name='a'):
        return (kind, name, m.state[name].generation, m.epoch, 0)

    def test_deadline_cut_exceeds_submission_capacity(self):
        names = list('abcdefgh')
        m = Model([Service(n) for n in names])
        m.start(names)
        for group in (names[:4], names[4:]):
            m.batch([self.observation(m, 'launched', n) for n in group])
        m.stop(names)
        effects = m.batch([self.observation(m, 'exit', n) for n in names[:4]], now=5)
        self.assertEqual(effects, [('force', n, 1) for n in names]
                         + [('reclaim', n, 1) for n in names[:4]])
        self.assertTrue(all(s.owned for s in m.state.values()))

    def test_same_cut_force_occurrences_are_not_unique_by_kind(self):
        m = Model([Service('a')])
        m.start(['a']); m.stop(['a'])
        effects = m.batch([self.observation(m, 'launched')], now=5)
        self.assertEqual(effects, [('force', 'a', 1), ('force', 'a', 1)])
        self.assertEqual(m.state['a'].phase, 'unknown')
        self.assertTrue(m.state['a'].owned)

    def test_later_cut_can_force_same_generation_again(self):
        m = Model([Service('a')])
        m.start(['a']); m.stop(['a'])
        self.assertEqual(m.batch(now=5), [('force', 'a', 1)])
        self.assertEqual(m.batch([self.observation(m, 'launched')], now=6),
                         [('force', 'a', 1)])
        self.assertEqual(m.batch([self.observation(m, 'launched')], now=7), [])
        self.assertTrue(m.state['a'].owned)

    def test_background_effect_after_operation_completion(self):
        m = Model([Service('a')])
        operation, _ = m.start(['a'])
        m.batch([self.observation(m, 'launched')])
        self.assertIsNone(m.active)
        self.assertEqual(m.operations[-1].status, 'success')
        self.assertEqual(m.batch([self.observation(m, 'fault')]), [('reclaim', 'a', 1)])
        self.assertIsNone(m.active)
        self.assertEqual(m.operations[-1].id, operation)

    def test_background_effect_does_not_belong_to_unrelated_active_scope(self):
        m = Model([Service('a'), Service('b')])
        m.start(['a']); m.batch([self.observation(m, 'launched')])
        operation, _ = m.start(['b'])
        self.assertEqual(m.batch([self.observation(m, 'fault')]), [('reclaim', 'a', 1)])
        self.assertEqual(m.active.id, operation)
        self.assertEqual(m.active.scope, ('b',))
        self.assertTrue(m.state['a'].owned)

    def test_executed_reclaim_still_requires_cleanup_observation(self):
        m = Model([Service('a')])
        operation, effects = m.start(['a'])
        ledger = EffectLedger(epoch=m.epoch, revision=m.revision, services=['a'])
        launch, = ledger.reserve(operation, effects)
        ledger.issue(launch); ledger.acknowledge(launch, 'executed')
        m.batch([self.observation(m, 'launched')])
        reclaim, = ledger.reserve(operation, m.batch([self.observation(m, 'fault')]))
        ledger.issue(reclaim)
        before = deepcopy(m.__dict__)
        ledger.acknowledge(reclaim, 'executed')
        self.assertEqual(m.__dict__, before)
        self.assertTrue(m.state['a'].owned)
        self.assertEqual(m.batch([self.observation(m, 'cleaned')]), [])
        self.assertFalse(m.state['a'].owned)


class AccountedTests(unittest.TestCase):
    def setup_delivery(self):
        m = Model([Service('a'), Service('b')])
        return m, AccountedDelivery(m)

    def frame(self, sequence=1, **changes):
        body = json.dumps(dict(version=0, epoch='boot-1', revision='config-1',
            sequence=sequence, verb='start', services=['a'], budget=100) | changes).encode()
        return len(body).to_bytes(4, 'big') + body

    def test_capacity_denial_before_dispatch(self):
        m, d = self.setup_delivery()
        d.ledger.reserve(1, [('launch', 'b', 1)])
        before = deepcopy(m.__dict__)
        d.receive(self.frame())
        self.assertEqual(m.__dict__, before)
        self.assertEqual(decode_error(d.read_reply())['code'], 'busy')
        self.assertEqual(d.control.high_water, 0)
        self.assertEqual(d.credits, 0)

    def test_tokens_transfer_once_and_replay_without_capacity(self):
        m, d = self.setup_delivery()
        d.receive(self.frame())
        reply = d.read_reply()
        self.assertEqual(d.credits, 0)
        with self.assertRaises(InvalidEffect):
            d.take_effects()
        token, = d.issue_obligations()
        self.assertEqual(token[3:], (1, 'a', 1, 'launch'))
        self.assertEqual(d.ledger.observe(token), 'issued')
        self.assertEqual(d.issue_obligations(), ())
        d.receive(self.frame())
        self.assertEqual(d.read_reply(), reply)
        self.assertEqual(d.issue_obligations(), ())
        self.assertEqual(m.state['a'].generation, 1)

    def test_acknowledgment_reopens_capacity_without_observation(self):
        m, d = self.setup_delivery()
        d.receive(self.frame()); d.read_reply()
        token, = d.issue_obligations()
        d.receive(self.frame(2))
        self.assertEqual(decode_error(d.read_reply())['code'], 'busy')
        self.assertEqual(d.acknowledge(token, 'executed'), 'recorded')
        self.assertTrue(m.state['a'].launch_pending)
        d.receive(self.frame(2))
        self.assertEqual(decode_receipt(d.read_reply())['disposition'], 'joined')
        self.assertEqual(d.credits, 0)
        self.assertEqual(d.issue_obligations(), ())

    def test_unknown_retains_capacity(self):
        m, d = self.setup_delivery()
        d.receive(self.frame()); d.read_reply()
        token, = d.issue_obligations()
        d.acknowledge(token, 'unknown')
        before = deepcopy(m.__dict__)
        d.receive(self.frame(2, verb='stop'))
        self.assertEqual(decode_error(d.read_reply())['code'], 'busy')
        self.assertEqual(m.__dict__, before)
        self.assertEqual(d.control.high_water, 1)

    def test_serial_and_operation_exhaustion_before_effects(self):
        m, d = self.setup_delivery()
        d.ledger.next_id = MAX_ID - 6
        d.receive(self.frame())
        self.assertEqual(decode_error(d.read_reply())['code'], 'busy')
        self.assertEqual(m.state['a'].generation, 0)
        d.ledger.next_id = 1
        m.next_id = MAX_ID + 1
        d.receive(self.frame())
        self.assertEqual(decode_error(d.read_reply())['code'], 'invalid-request')
        self.assertEqual(d.credits, 0)
        self.assertEqual(d.control.high_water, 0)

    def test_output_loss_preserves_reserved_tokens(self):
        m, d = self.setup_delivery()
        with patch('prototypes.runtime_model.control_delivery.encode_receipt', side_effect=MemoryError):
            d.receive(self.frame())
        self.assertEqual(decode_error(d.read_reply())['code'], 'internal-error')
        d.disconnect(); d.reconnect()
        token, = d.issue_obligations()
        self.assertEqual(d.ledger.observe(token), 'issued')
        self.assertTrue(m.state['a'].owned)

    def test_capture_failure_retains_raw_effects_and_poison(self):
        m, d = self.setup_delivery()
        with patch.object(d.ledger, 'reserve', side_effect=InvalidEffect('capture failure')):
            with self.assertRaises(InvalidEffect):
                d.receive(self.frame())
        self.assertEqual(d.effects, (('launch', 'a', 1),))
        self.assertEqual(d.credits, 8)
        self.assertTrue(d.control.failed)
        with self.assertRaises(InvalidEffect):
            d.issue_obligations()
        self.assertTrue(m.state['a'].owned)

    def test_dispatch_exception_retains_reserved_capacity(self):
        m, d = self.setup_delivery()
        start = m.start
        def interrupted(*args, **kwargs):
            start(*args, **kwargs)
            raise Backpressure('unexpected after effects')
        with patch.object(m, 'start', interrupted):
            d.receive(self.frame())
        self.assertEqual(decode_error(d.read_reply())['disposition'], 'unknown')
        self.assertEqual(d.credits, 8)
        self.assertTrue(d.control.failed)
        self.assertTrue(m.state['a'].owned)

    def test_driver_loss_and_partial_issue_close(self):
        m, d = self.setup_delivery()
        d.receive(self.frame(services=['a', 'b'])); d.read_reply()
        first, second = d.pending_tokens
        issue = d.ledger.issue
        def interrupted(token):
            if token == second:
                raise RuntimeError('issue interrupted')
            return issue(token)
        with patch.object(d.ledger, 'issue', interrupted):
            with self.assertRaises(RuntimeError):
                d.issue_obligations()
        self.assertTrue(d.control.failed)
        self.assertTrue(d.ledger.closed)
        self.assertFalse(d.connected)
        self.assertEqual(d.ledger.observe(first), 'unknown')
        self.assertEqual(d.ledger.observe(second), 'rejected-before-effects')
        self.assertTrue(all(s.owned for s in m.state.values()))


class EffectTests(unittest.TestCase):
    def ledger(self, services=('a', 'b')):
        return EffectLedger(epoch='boot-1', revision='config-1', services=services)

    def test_cannot_confirm_unissued_effect(self):
        ledger = self.ledger()
        token, = ledger.reserve(1, [('launch', 'a', 1)])
        with self.assertRaisesRegex(InvalidEffect, 'not issued'):
            ledger.acknowledge(token, 'executed')
        self.assertEqual(ledger.observe(token), 'reserved')

    def test_issue_and_acknowledgment_are_distinct(self):
        ledger = self.ledger()
        token, = ledger.reserve(1, [('launch', 'a', 1)])
        self.assertEqual(ledger.issue(token), token)
        self.assertEqual(ledger.observe(token), 'issued')
        with self.assertRaises(InvalidEffect):
            ledger.issue(token)
        self.assertEqual(ledger.acknowledge(token, 'executed'), 'recorded')
        self.assertEqual(ledger.acknowledge(token, 'executed'), 'replayed')
        with self.assertRaises(InvalidEffect):
            ledger.acknowledge(token, 'unknown')
        with self.assertRaises(InvalidEffect):
            ledger.reserve(2, [('launch', 'a', 1)])

    def test_token_mismatches_preserve_ledger(self):
        ledger = self.ledger()
        token, = ledger.reserve(1, [('launch', 'a', 1)])
        ledger.issue(token)
        before = deepcopy(ledger.__dict__)
        for index, value in [(0, 'old'), (1, 'changed'), (2, True), (3, 2),
                             (4, 'b'), (5, 2), (6, 'stop')]:
            changed = list(token); changed[index] = value
            with self.assertRaises(InvalidEffect):
                ledger.acknowledge(tuple(changed), 'executed')
            self.assertEqual(ledger.__dict__, before)

    def test_atomic_batch_and_capacity(self):
        ledger = self.ledger()
        before = deepcopy(ledger.__dict__)
        for effects in [[('launch', 'a', 1), ('launch', 'missing', 1)],
                        [('launch', 'a', 1), ('launch', 'a', 1)],
                        [('launch', 'a', 1), ('stop', 'a', 2)],
                        [('launch', 'a', True)], []]:
            with self.assertRaises(InvalidEffect):
                ledger.reserve(1, effects)
            self.assertEqual(ledger.__dict__, before)
        names = tuple(chr(97 + i) for i in range(8))
        ledger = self.ledger(names)
        tokens = ledger.reserve(1, [('launch', n, 1) for n in names])
        self.assertEqual(len(ledger.live), 8)
        before = deepcopy(ledger.__dict__)
        with self.assertRaises(InvalidEffect):
            ledger.reserve(2, [('stop', 'a', 1)])
        self.assertEqual(ledger.__dict__, before)
        ledger.acknowledge(tokens[0], 'rejected-before-effects')
        self.assertEqual(len(ledger.reserve(2, [('stop', 'a', 1)])), 1)

    def test_unknown_retains_slot_and_cannot_retry(self):
        ledger = self.ledger()
        token, = ledger.reserve(1, [('launch', 'a', 1)])
        ledger.issue(token)
        ledger.acknowledge(token, 'unknown')
        self.assertEqual(len(ledger.live), 1)
        self.assertEqual(ledger.acknowledge(token, 'unknown'), 'replayed')
        for outcome in ['executed', 'rejected-before-effects']:
            with self.assertRaises(InvalidEffect):
                ledger.acknowledge(token, outcome)
        with self.assertRaises(InvalidEffect):
            ledger.reserve(2, [('launch', 'a', 2)])
        with self.assertRaises(InvalidEffect):
            ledger.issue(token)

    def test_history_eviction_and_generation_retirement(self):
        ledger = self.ledger()
        first = None
        for generation in range(1, 67):
            token, = ledger.reserve(generation, [('launch', 'a', generation)])
            if first is None:
                first = token
            ledger.issue(token)
            ledger.acknowledge(token, 'executed')
        self.assertEqual(len(ledger.history), 64)
        self.assertEqual(ledger.acknowledge(first, 'executed'), 'retired')
        self.assertEqual(ledger.observe(first), 'unknown')
        for generation in [1, 66]:
            with self.assertRaises(InvalidEffect):
                ledger.reserve(70, [('launch', 'a', generation)])
        with self.assertRaises(InvalidEffect):
            ledger.issue(first)

    def test_serial_exhaustion_without_wrap(self):
        ledger = self.ledger()
        ledger.next_id = MAX_ID
        token, = ledger.reserve(MAX_ID, [('launch', 'a', MAX_ID)])
        self.assertEqual(token[2], MAX_ID)
        ledger.issue(token)
        ledger.acknowledge(token, 'executed')
        before = deepcopy(ledger.__dict__)
        with self.assertRaises(InvalidEffect):
            ledger.reserve(1, [('launch', 'b', 1)])
        self.assertEqual(ledger.__dict__, before)
        self.assertEqual(ledger.acknowledge(token, 'executed'), 'replayed')

    def test_driver_loss_retains_unknown_and_closes_mutation(self):
        ledger = self.ledger()
        reserved, issued = ledger.reserve(1, [('launch', 'a', 1), ('launch', 'b', 1)])
        ledger.issue(issued)
        ledger.driver_lost(); ledger.driver_lost()
        self.assertEqual(ledger.observe(reserved), 'rejected-before-effects')
        self.assertEqual(ledger.observe(issued), 'unknown')
        self.assertEqual(len(ledger.live), 1)
        for call in [lambda: ledger.issue(reserved),
                     lambda: ledger.acknowledge(issued, 'executed'),
                     lambda: ledger.reserve(2, [('stop', 'b', 1)])]:
            with self.assertRaisesRegex(InvalidEffect, 'driver closed'):
                call()

    def test_acknowledgment_never_changes_lifecycle_ownership(self):
        m = Model([Service('a')])
        operation, effects = m.start(['a'])
        ledger = self.ledger(('a',))
        token, = ledger.reserve(operation, effects)
        before = deepcopy(m.__dict__)
        ledger.issue(token); ledger.acknowledge(token, 'executed')
        self.assertEqual(m.__dict__, before)
        self.assertTrue(m.state['a'].launch_pending)
        m.batch([('launched', 'a', 1, m.epoch, 0)])
        operation, effects = m.stop(['a'])
        token, = ledger.reserve(operation, effects)
        ledger.issue(token); ledger.acknowledge(token, 'executed')
        self.assertTrue(m.state['a'].owned)
        self.assertEqual(m.active.status, 'pending')
        effects = m.batch([('exit', 'a', 1, m.epoch, 0)])
        token, = ledger.reserve(operation, effects)
        before = deepcopy(m.__dict__)
        ledger.issue(token); ledger.acknowledge(token, 'executed')
        self.assertEqual(m.__dict__, before)
        self.assertTrue(m.state['a'].owned)
        m.batch([('cleaned', 'a', 1, m.epoch, 0)])
        self.assertFalse(m.state['a'].owned)


class AuthorityTests(unittest.TestCase):
    def setup_authority(self, *, services=None, verbs=None, mutate=None, observe=None):
        m = Model(services or [Service('a'), Service('b')])
        binding = object()
        stream = AuthorizedStream(m, binding=binding, policy_revision='policy-1',
            verbs=['start', 'stop', 'shutdown'] if verbs is None else verbs,
            mutate=['a', 'b'] if mutate is None else mutate,
            observe=['a', 'b'] if observe is None else observe)
        return m, binding, stream

    def frame(self, sequence=1, **changes):
        request = dict(version=0, epoch='boot-1', revision='config-1', sequence=sequence,
                       verb='start', services=['a'], budget=100) | changes
        body = json.dumps(request).encode()
        return len(body).to_bytes(4, 'big') + body

    def test_foreign_binding_denied_before_effects(self):
        m, binding, s = self.setup_authority()
        before = deepcopy(m.__dict__)
        with self.assertRaisesRegex(Denied, '^authority$'):
            s.feed(self.frame(), now=0, binding=object())
        self.assertEqual(m.__dict__, before)
        self.assertEqual(s.phase, 'reading')

    def test_missing_binding_and_payload_impersonation(self):
        m, binding, s = self.setup_authority()
        with self.assertRaises(Denied):
            s.feed(self.frame(caller='owner'), now=0)
        s.feed(self.frame(caller='owner'), now=0, binding=binding)
        self.assertEqual(decode_error(s.read(4100, now=0, binding=binding))['code'], 'invalid-request')
        self.assertEqual(s.delivery.control.high_water, 0)
        self.assertEqual(m.state['a'].generation, 0)

    def test_dependency_closure_denied(self):
        m, binding, s = self.setup_authority(services=[Service('a', requires=(('b', 'started'),)), Service('b')], mutate=['a'])
        with self.assertRaises(Denied):
            s.feed(self.frame(), now=0, binding=binding)
        self.assertEqual(s.delivery.control.high_water, 0)
        self.assertEqual([v.generation for v in m.state.values()], [0, 0])
        self.assertEqual(s.phase, 'closed')

    def test_stop_shutdown_and_verb_scope(self):
        for verb, names, verbs in [('stop', ['b'], ['stop']),
                                   ('shutdown', ['a', 'b'], ['shutdown']),
                                   ('start', ['a'], [])]:
            m, binding, s = self.setup_authority(mutate=['a'], verbs=verbs)
            with self.assertRaises(Denied):
                s.feed(self.frame(verb=verb, services=names), now=0, binding=binding)
            self.assertEqual(s.delivery.control.high_water, 0)
            self.assertFalse(m.closed)

    def test_mutation_does_not_grant_disclosure(self):
        m, binding, s = self.setup_authority(observe=[])
        with self.assertRaises(Denied):
            s.feed(self.frame(), now=0, binding=binding)
        self.assertIsNone(s.delivery.reply)
        self.assertEqual(s.delivery.control.high_water, 1)
        self.assertEqual(s.take_effects(), (('launch', 'a', 1),))
        self.assertTrue(m.state['a'].owned)
        with self.assertRaises(Denied):
            s.observe(m.epoch, 1, binding=binding)

    def test_conflict_snapshot_outside_read_scope_is_not_exposed(self):
        m, binding, s = self.setup_authority(observe=['a'])
        # Trusted driver already has b pending; this is not a request from the bound client.
        m.start(['b'])
        with self.assertRaises(Denied):
            s.feed(self.frame(), now=0, binding=binding)
        self.assertIsNone(s.delivery.reply)
        self.assertEqual(s.delivery.control.high_water, 1)
        self.assertEqual(s.delivery.control.receipts[1][1]['disposition'], 'rejected')
        self.assertEqual(m.state['a'].generation, 0)
        s.reconnect(now=1, binding=binding)
        with self.assertRaises(Denied):
            s.feed(self.frame(), now=1, binding=binding)
        self.assertEqual(s.delivery.control.high_water, 1)

    def test_revoke_partial_input(self):
        m, binding, s = self.setup_authority()
        s.feed(self.frame()[:6], now=0, binding=binding)
        s.revoke(); s.revoke()
        self.assertEqual(len(s.buffer), 0)
        self.assertEqual(m.state['a'].generation, 0)
        with self.assertRaises(Denied):
            s.reconnect(now=1, binding=binding)
        with self.assertRaises(Denied):
            s.feed(self.frame(), now=1, binding=binding)

    def test_revoke_after_partial_output_preserves_work(self):
        m, binding, s = self.setup_authority()
        s.feed(self.frame(), now=0, binding=binding)
        self.assertEqual(len(s.read(3, now=0, binding=binding)), 3)
        s.revoke()
        self.assertIsNone(s.delivery.reply)
        self.assertEqual(s.take_effects(), (('launch', 'a', 1),))
        self.assertEqual(s.delivery.control.high_water, 1)
        self.assertTrue(m.state['a'].owned)
        for operation in [lambda: s.read(4100, now=1, binding=binding),
                          lambda: s.observe(m.epoch, 1, binding=binding),
                          lambda: s.wait(m.epoch, 1, now=1, deadline=2, binding=binding)]:
            with self.assertRaises(Denied):
                operation()

    def test_same_binding_reconnect_and_foreign_read(self):
        m, binding, s = self.setup_authority()
        s.feed(self.frame(), now=0, binding=binding)
        reply = s.delivery.reply
        with self.assertRaises(Denied):
            s.read(4100, now=0, binding=object())
        self.assertEqual(s.delivery.reply, reply)
        s.disconnect(); s.take_effects(); s.reconnect(now=1, binding=binding)
        s.feed(self.frame(), now=1, binding=binding)
        self.assertEqual(s.read(4100, now=1, binding=binding), reply)
        self.assertEqual(s.take_effects(), ())
        self.assertEqual(s.wait(m.epoch, 1, now=2, deadline=2, binding=binding)['state'], 'timeout')

    def test_unknown_observation_and_stale_configuration(self):
        m, binding, s = self.setup_authority(observe=['a'])
        with self.assertRaises(Denied):
            s.observe(m.epoch, 99, binding=binding)
        m.revision = 'changed'
        with self.assertRaises(Denied):
            s.feed(self.frame(), now=0, binding=binding)
        self.assertTrue(s.revoked)
        self.assertEqual(m.state['a'].generation, 0)
        m, binding, s = self.setup_authority()
        self.assertEqual(s.observe(m.epoch, 99, binding=binding)['outcome'], 'unknown')

    def test_bootstrap_validation_and_scope_copy(self):
        default = dict(binding=object(), policy_revision='p', verbs=['start'], mutate=['a'], observe=['a'])
        for change in [dict(binding=None), dict(binding=1), dict(policy_revision=''),
                       dict(policy_revision='\ud800'), dict(verbs=['restart']),
                       dict(mutate=['missing']), dict(observe=['a'] * 9)]:
            m = Model([Service('a')])
            with self.assertRaises(ValueError):
                AuthorizedStream(m, **(default | change))
            self.assertFalse(getattr(m, '_control_claimed', False))
        m = Model([Service('a')])
        s = AuthorizedStream(m, **default)
        default['mutate'].clear(); default['observe'].clear(); default['verbs'].clear()
        s.feed(self.frame(), now=0, binding=default['binding'])
        self.assertEqual(decode_receipt(s.read(4100, now=0, binding=default['binding']))['disposition'], 'accepted')


class StreamTests(unittest.TestCase):
    FRAME = (b'{"version":0,"epoch":"boot-1","revision":"config-1",'
             b'"sequence":1,"verb":"start","services":["a"],"budget":100}')

    def frame(self):
        return len(self.FRAME).to_bytes(4, 'big') + self.FRAME

    def setup_stream(self, **options):
        m = Model([Service('a')])
        return m, Stream(m, **options)

    def test_every_frame_split_dispatches_once(self):
        frame = self.frame()
        for split in range(len(frame)):
            m, s = self.setup_stream()
            s.feed(frame[:split], now=0)
            self.assertEqual(m.state['a'].generation, 0)
            s.feed(frame[split:], now=0)
            self.assertEqual(s.take_effects(), (('launch', 'a', 1),))
            self.assertEqual(s.take_effects(), ())
            self.assertEqual(decode_receipt(s.read(4100, now=0))['sequence'], 1)
            self.assertEqual(s.phase, 'reading')

    def test_maximum_frame_and_one_byte_input(self):
        m, s = self.setup_stream()
        body = self.FRAME + b' ' * (4096 - len(self.FRAME))
        frame = len(body).to_bytes(4, 'big') + body
        for byte in frame:
            s.feed(bytes([byte]), now=0)
            self.assertLessEqual(len(s.buffer), 4100)
        self.assertEqual(m.state['a'].generation, 1)
        self.assertEqual(len(s.buffer), 0)
        self.assertEqual(s.phase, 'writing')

    def test_bad_header_trailing_and_oversized_close_before_dispatch(self):
        frame = self.frame()
        for chunks in [(b'\0\0\0\0',), ((4097).to_bytes(4, 'big'),),
                       (frame + b'x',), (frame[:3], frame[3:] + b'x'),
                       (b'x' * 4101,), (bytearray(frame),)]:
            m, s = self.setup_stream()
            with self.assertRaises(InvalidFrame):
                for chunk in chunks:
                    s.feed(chunk, now=0)
            self.assertEqual(s.phase, 'closed')
            self.assertEqual(len(s.buffer), 0)
            self.assertEqual(m.state['a'].generation, 0)

    def test_read_deadline_exact_boundary(self):
        m, s = self.setup_stream(read_budget=5)
        s.feed(self.frame()[:3], now=4)
        self.assertFalse(s.tick(5))
        self.assertEqual(s.phase, 'closed')
        self.assertEqual(m.state['a'].generation, 0)

    def test_progress_does_not_extend_deadlines(self):
        m, s = self.setup_stream(read_budget=5, write_budget=5)
        s.feed(self.frame()[:1], now=1)
        s.feed(self.frame()[1:2], now=4)
        self.assertEqual(s.deadline, 5)
        with self.assertRaises(Backpressure):
            s.feed(self.frame()[2:], now=5)
        self.assertEqual(m.state['a'].generation, 0)
        s.reconnect(now=6)
        s.feed(self.frame(), now=7)
        self.assertEqual(s.deadline, 12)
        self.assertEqual(len(s.read(1, now=11)), 1)
        self.assertEqual(s.deadline, 12)
        with self.assertRaises(Backpressure):
            s.read(4100, now=12)
        self.assertTrue(m.state['a'].owned)
        self.assertEqual(s.take_effects(), (('launch', 'a', 1),))

    def test_partial_output_timeout_reconnect_replays(self):
        m, s = self.setup_stream(write_budget=5)
        s.feed(self.frame(), now=0)
        original = s.delivery.reply
        self.assertEqual(s.read(3, now=4), original[:3])
        self.assertFalse(s.tick(5))
        self.assertIsNone(s.delivery.reply)
        self.assertEqual(s.take_effects(), (('launch', 'a', 1),))
        s.reconnect(now=6)
        s.feed(self.frame(), now=6)
        self.assertEqual(s.read(4100, now=6), original)
        self.assertEqual(s.take_effects(), ())
        self.assertEqual(m.state['a'].generation, 1)

    def test_small_output_and_backpressure(self):
        m, s = self.setup_stream(read_budget=9)
        s.feed(self.frame(), now=2)
        original = s.delivery.reply
        with self.assertRaises(Backpressure):
            s.feed(self.frame(), now=2)
        with self.assertRaises(Backpressure):
            s.reconnect(now=2)
        pieces = []
        while s.phase == 'writing':
            pieces.append(s.read(7, now=3))
        self.assertEqual(b''.join(pieces), original)
        self.assertEqual(s.deadline, 12)
        self.assertEqual(m.state['a'].generation, 1)

    def test_clock_validation_and_exhaustion(self):
        m, s = self.setup_stream(now=10)
        for now in [9, True, MAX_ID + 1]:
            with self.assertRaises(ValueError):
                s.tick(now)
            self.assertEqual(s.now, 10)
        for maximum in [0, True, 4101]:
            with self.assertRaises(ValueError):
                s.read(maximum, now=11)
            self.assertEqual(s.now, 10)
        m, s = self.setup_stream(now=MAX_ID - 1)
        self.assertEqual(s.deadline, MAX_ID)
        self.assertFalse(s.tick(MAX_ID))
        with self.assertRaises(ValueError):
            s.reconnect(now=MAX_ID)
        for options in [dict(now=True), dict(read_budget=0), dict(write_budget=1000001)]:
            m = Model([Service('a')])
            with self.assertRaises(ValueError):
                Stream(m, **options)
            self.assertFalse(getattr(m, '_control_claimed', False))

    def test_disconnect_partial_input_and_bad_json_reply(self):
        m, s = self.setup_stream()
        s.feed(self.frame()[:10], now=0)
        s.disconnect()
        self.assertEqual(len(s.buffer), 0)
        self.assertEqual(m.state['a'].generation, 0)
        s.reconnect(now=1)
        s.feed(b'\0\0\0\1{', now=1)
        self.assertEqual(decode_error(s.read(4100, now=1))['code'], 'invalid-frame')
        self.assertEqual(s.phase, 'closed')

    def test_exceptional_output_closes_but_retains_effects(self):
        m, s = self.setup_stream()
        with patch('prototypes.runtime_model.control_delivery.encode_receipt', side_effect=MemoryError), patch(
                'prototypes.runtime_model.control_delivery.encode_error', side_effect=MemoryError):
            with self.assertRaises(MemoryError):
                s.feed(self.frame(), now=0)
        self.assertEqual(s.phase, 'closed')
        self.assertEqual(len(s.buffer), 0)
        self.assertEqual(s.take_effects(), (('launch', 'a', 1),))
        self.assertTrue(m.state['a'].owned)


class DeliveryTests(unittest.TestCase):
    def setup_delivery(self):
        m = Model([Service('a'), Service('b')])
        return m, Delivery(m)

    def frame(self, sequence=1, **changes):
        value = dict(version=0, epoch='boot-1', revision='config-1', sequence=sequence,
                     verb='start', services=['a'], budget=100) | changes
        body = json.dumps(value).encode()
        return len(body).to_bytes(4, 'big') + body

    def test_error_golden_and_combinations(self):
        body = b'{"code":"busy","disposition":"not-dispatched","schema":"sys-init-control-error-v1"}'
        self.assertEqual(encode_error(decode_error(len(body).to_bytes(4, 'big') + body)),
                         len(body).to_bytes(4, 'big') + body)
        for code in ['invalid-frame', 'invalid-request', 'busy', 'internal-error']:
            for disposition in ['not-dispatched', 'unknown']:
                value = dict(schema='sys-init-control-error-v1', code=code, disposition=disposition)
                if (code == 'internal-error') == (disposition == 'unknown'):
                    self.assertEqual(decode_error(encode_error(value)), value)
                else:
                    with self.assertRaisesRegex(InvalidFrame, '^error-reply$'):
                        encode_error(value)

    def test_internal_error_cannot_claim_no_dispatch(self):
        with self.assertRaisesRegex(InvalidFrame, '^error-reply$'):
            encode_error(dict(schema='sys-init-control-error-v1', code='internal-error',
                              disposition='not-dispatched'))

    def test_error_rejects_unbounded_and_extra_data(self):
        good = dict(schema='sys-init-control-error-v1', code='busy', disposition='not-dispatched')
        for value in [good | {'code': 'x' * 10000}, good | {'message': 'secret'},
                      good | {'sequence': 1}, good | {'code': []}, {}]:
            with patch('prototypes.runtime_model.control_reply.json.dumps') as serializer:
                with self.assertRaisesRegex(InvalidFrame, '^error-reply$'):
                    encode_error(value)
                serializer.assert_not_called()
        for body in [b'{"code":{}}', b'{"code":"busy","code":"busy"}']:
            with self.assertRaises(InvalidFrame):
                decode_error(len(body).to_bytes(4, 'big') + body)

    def test_reply_backpressure_precedes_dispatch(self):
        m, d = self.setup_delivery()
        d.receive(self.frame())
        reply = d.reply
        before = deepcopy(m.__dict__)
        for _ in range(10):
            with self.assertRaises(Backpressure):
                d.receive(self.frame(2))
        self.assertEqual(d.reply, reply)
        self.assertEqual(m.__dict__, before)
        self.assertEqual(d.control.high_water, 1)
        self.assertLessEqual(len(reply), 4100)

    def test_maximum_effect_batch_transfers_once(self):
        names = [chr(97 + index) for index in range(8)]
        m = Model([Service(name) for name in names])
        d = Delivery(m)
        d.receive(self.frame(services=names))
        self.assertEqual(d.take_effects(), tuple(('launch', name, 1) for name in names))
        self.assertEqual(d.take_effects(), ())
        self.assertEqual(decode_receipt(d.read_reply())['operation']['scope'], names)

    def test_disconnect_retains_effects_and_replay(self):
        m, d = self.setup_delivery()
        d.receive(self.frame())
        original = d.reply
        d.disconnect()
        self.assertIsNone(d.reply)
        with self.assertRaises(Backpressure):
            d.receive(self.frame())
        self.assertEqual(d.take_effects(), (('launch', 'a', 1),))
        self.assertEqual(d.take_effects(), ())
        d.reconnect()
        d.receive(self.frame())
        self.assertEqual(d.read_reply(), original)
        self.assertEqual(d.take_effects(), ())
        self.assertTrue(m.state['a'].owned)
        self.assertEqual(m.state['a'].generation, 1)

    def test_effect_backpressure_is_bounded(self):
        m, d = self.setup_delivery()
        d.receive(self.frame())
        d.read_reply()
        before = deepcopy(m.__dict__)
        for _ in range(10):
            d.receive(self.frame(2))
            self.assertEqual(decode_error(d.read_reply())['code'], 'busy')
        self.assertEqual(m.__dict__, before)
        self.assertEqual(d.control.high_water, 1)
        self.assertEqual(d.take_effects(), (('launch', 'a', 1),))
        d.receive(self.frame(2))
        self.assertEqual(decode_receipt(d.read_reply())['disposition'], 'joined')
        self.assertEqual(d.take_effects(), ())

    def test_invalid_frame_closes_without_sequence(self):
        m, d = self.setup_delivery()
        before = deepcopy(m.__dict__)
        d.receive(b'bad')
        with self.assertRaises(Backpressure):
            d.reconnect()
        self.assertEqual(decode_error(d.read_reply())['code'], 'invalid-frame')
        self.assertFalse(d.connected)
        self.assertEqual(m.__dict__, before)
        self.assertEqual(d.control.high_water, 0)
        d.reconnect()
        d.receive(self.frame(version=9))
        self.assertEqual(decode_error(d.read_reply())['code'], 'invalid-request')
        self.assertTrue(d.connected)
        self.assertEqual(d.control.high_water, 0)

    def test_lifecycle_rejection_remains_receipt(self):
        m, d = self.setup_delivery()
        d.receive(self.frame()); d.read_reply(); d.take_effects()
        d.receive(self.frame(2, services=['b']))
        self.assertEqual(decode_receipt(d.read_reply())['disposition'], 'rejected')
        self.assertEqual(d.control.high_water, 2)
        self.assertEqual(m.state['b'].generation, 0)

    def test_receipt_encoding_failure_retains_work(self):
        m, d = self.setup_delivery()
        with patch('prototypes.runtime_model.control_delivery.encode_receipt', side_effect=MemoryError):
            d.receive(self.frame())
        self.assertEqual(decode_error(d.read_reply())['disposition'], 'unknown')
        self.assertEqual(d.take_effects(), (('launch', 'a', 1),))
        d.receive(self.frame())
        self.assertEqual(decode_receipt(d.read_reply())['disposition'], 'accepted')
        self.assertEqual(d.take_effects(), ())
        self.assertTrue(m.state['a'].owned)

    def test_dispatch_failure_stays_unknown_after_reconnect(self):
        m, d = self.setup_delivery()
        start = m.start
        def interrupted(*args, **kwargs):
            start(*args, **kwargs)
            raise RuntimeError('private detail')
        with patch.object(m, 'start', interrupted):
            d.receive(self.frame())
        error = d.read_reply()
        self.assertEqual(decode_error(error)['code'], 'internal-error')
        self.assertNotIn(b'private detail', error)
        self.assertTrue(d.control.failed)
        self.assertTrue(m.state['a'].owned)
        d.disconnect(); d.reconnect(); d.receive(self.frame())
        self.assertEqual(decode_receipt(d.read_reply())['reason'], 'session-failed')
        self.assertEqual(m.state['a'].generation, 1)

    def test_fallback_encoding_failure_preserves_effects(self):
        m, d = self.setup_delivery()
        with patch('prototypes.runtime_model.control_delivery.encode_receipt', side_effect=MemoryError), patch(
                'prototypes.runtime_model.control_delivery.encode_error', side_effect=MemoryError):
            with self.assertRaises(MemoryError):
                d.receive(self.frame())
        self.assertIsNone(d.reply)
        d.disconnect()
        self.assertEqual(d.take_effects(), (('launch', 'a', 1),))
        self.assertTrue(m.state['a'].owned)


class ObservationReplyTests(unittest.TestCase):
    def setup_observation(self):
        m = Model([Service('a')])
        c = Control(m)
        c.submit(dict(version=0, epoch=m.epoch, revision=m.revision, sequence=1,
                      verb='start', services=['a'], budget=100))
        return m, c, c.observe(m.epoch, 1)

    def test_actual_wait_transitions(self):
        m, c, observation = self.setup_observation()
        before = deepcopy(m.__dict__)
        pending = decode_wait(encode_wait(c.wait(m.epoch, 1, now=0, deadline=5)))
        timeout = decode_wait(encode_wait(c.wait(m.epoch, 1, now=5, deadline=5)))
        self.assertEqual((pending['state'], timeout['state']), ('pending', 'timeout'))
        self.assertEqual(timeout['observation']['outcome'], 'pending')
        self.assertEqual(m.__dict__, before)
        m.batch([('launched', 'a', 1, m.epoch, 0)])
        complete = decode_wait(encode_wait(c.wait(m.epoch, 1, now=6, deadline=5)))
        self.assertEqual((complete['state'], complete['observation']['outcome']), ('complete', 'success'))
        unknown = decode_wait(encode_wait(c.wait('old', 1, now=6, deadline=5)))
        self.assertEqual((unknown['state'], unknown['observation']['outcome']), ('unknown', 'unknown'))
        self.assertIsNone(unknown['observation']['operation'])
        self.assertEqual(decode_observation(encode_observation(observation))['outcome'], 'pending')

    def test_state_outcome_matrix(self):
        _, _, base = self.setup_observation()
        for outcome in ['pending', 'success', 'failed', 'cancelled', 'incomplete', 'unknown']:
            observation = base | {'outcome': outcome}
            if outcome == 'unknown':
                observation['operation'] = None
            for state in ['pending', 'timeout', 'complete', 'unknown']:
                value = dict(schema='sys-init-control-wait-v1', state=state, observation=observation)
                allowed = ((outcome == 'pending' and state in ['pending', 'timeout']) or
                           (outcome == 'unknown' and state == 'unknown') or
                           (outcome in ['success', 'failed', 'cancelled', 'incomplete'] and state == 'complete'))
                with self.subTest(outcome=outcome, state=state):
                    if allowed:
                        decoded = decode_wait(encode_wait(value))
                        self.assertEqual(decoded['observation']['outcome'], outcome)
                    else:
                        with self.assertRaisesRegex(InvalidFrame, '^wait$'):
                            encode_wait(value)

    def test_mismatched_identity_rejected(self):
        _, _, observation = self.setup_observation()
        with self.assertRaisesRegex(InvalidFrame, '^observation$'):
            encode_observation(observation | {'id': 2})

    def test_invalid_snapshots_before_serialization(self):
        _, _, observation = self.setup_observation()
        values = [None, {}, observation | {'effects': []}, observation | {'epoch': 'other'},
                  observation | {'id': True}, observation | {'outcome': 'running'},
                  observation | {'outcome': 'unknown'}, observation | {'operation': None},
                  observation | {'schema': 'unknown'}, observation | {'epoch': 'x' * 65},
                  observation | {'epoch': '\ud800'}]
        cyclic = observation.copy(); cyclic['operation'] = cyclic
        values.append(cyclic)
        for value in values:
            with patch('prototypes.runtime_model.control_reply.json.dumps') as serializer:
                with self.assertRaisesRegex(InvalidFrame, '^observation$'):
                    encode_observation(value)
                serializer.assert_not_called()
        wait = dict(schema='sys-init-control-wait-v1', state='pending', observation=observation)
        for value in [wait | {'effects': []}, wait | {'state': 'x' * 10000},
                      wait | {'observation': None}, wait | {'schema': 'unknown'}]:
            with patch('prototypes.runtime_model.control_reply.json.dumps') as serializer:
                with self.assertRaisesRegex(InvalidFrame, '^wait$'):
                    encode_wait(value)
                serializer.assert_not_called()

    def test_maximum_wait_and_detachment(self):
        _, _, observation = self.setup_observation()
        observation.update(epoch='😀' * 64, id=MAX_ID)
        observation['operation'].update(epoch=observation['epoch'], id=MAX_ID,
            revision='😀' * 64, deadline=MAX_ID, scope=[chr(97+i) * 32 for i in range(8)])
        wait = dict(schema='sys-init-control-wait-v1', state='timeout', observation=observation)
        frame = encode_wait(wait)
        self.assertLessEqual(len(frame), 4100)
        decoded = decode_wait(frame)
        self.assertEqual(encode_wait(decoded), frame)
        decoded['observation']['operation']['scope'].clear()
        self.assertEqual(len(observation['operation']['scope']), 8)

    def test_decode_depth_and_schema_separation(self):
        _, _, observation = self.setup_observation()
        frame = encode_wait(dict(schema='sys-init-control-wait-v1', state='pending', observation=observation))
        with self.assertRaisesRegex(InvalidFrame, '^depth$'):
            decode_observation(frame)
        with self.assertRaises(InvalidFrame):
            decode_wait(encode_observation(observation))
        for body in [frame[4:].replace(b'["a"]', b'[["a"]]'),
                     frame[4:].replace(b'"state":"pending"', b'"state":"complete"'),
                     frame[4:-1] + b',"state":"pending"}',
                     frame[4:-1] + b',"effects":[]}']:
            with self.assertRaises(InvalidFrame):
                decode_wait(len(body).to_bytes(4, 'big') + body)
        with self.assertRaises(InvalidFrame):
            decode_wait(frame[:-1])

    def test_encoding_failure_does_not_cancel(self):
        m, c, observation = self.setup_observation()
        before = deepcopy(m.__dict__)
        wait = c.wait(m.epoch, 1, now=1, deadline=1)
        for encoder, value in [(encode_observation, observation), (encode_wait, wait)]:
            with patch('prototypes.runtime_model.control_reply.json.dumps', side_effect=MemoryError):
                with self.assertRaises(MemoryError):
                    encoder(value)
        self.assertEqual(m.__dict__, before)
        self.assertTrue(m.state['a'].owned)
        self.assertFalse(c.failed)

    def test_unknown_golden_frame(self):
        body = (b'{"epoch":"old","id":1,"operation":null,"outcome":"unknown",'
                b'"schema":"sys-init-control-observation-v1"}')
        frame = len(body).to_bytes(4, 'big') + body
        value = decode_observation(frame)
        self.assertEqual(value, dict(epoch='old', id=1, operation=None, outcome='unknown',
                                    schema='sys-init-control-observation-v1'))
        self.assertEqual(encode_observation(value), frame)


class ReplyTests(unittest.TestCase):
    def setup_reply(self):
        m = Model([Service('a'), Service('b')])
        c = Control(m)
        request = dict(version=0, epoch=m.epoch, revision=m.revision,
                       sequence=1, verb='start', services=['a'], budget=100)
        return m, c, request, c.submit(request)

    def test_projection_and_replay_bytes(self):
        m, c, request, submission = self.setup_reply()
        before = deepcopy(m.__dict__)
        frame = encode_receipt(submission['receipt'])
        expected = (b'{"disposition":"accepted","operation":{"deadline":100,"epoch":"boot-1",'
                    b'"id":1,"kind":"start","revision":"config-1","scope":["a"],'
                    b'"shutdown":false},"reason":"","schema":"sys-init-control-receipt-v1",'
                    b'"sequence":1}')
        self.assertEqual(frame, len(expected).to_bytes(4, 'big') + expected)
        self.assertEqual(encode_receipt(c.submit(request)['receipt']), frame)
        self.assertNotIn(b'effects', frame)
        self.assertEqual(submission['effects'], (('launch', 'a', 1),))
        self.assertEqual(m.__dict__, before)

    def test_reject_internal_submission_before_serialization(self):
        _, _, _, submission = self.setup_reply()
        with patch('prototypes.runtime_model.control_reply.json.dumps') as serializer:
            with self.assertRaisesRegex(InvalidFrame, '^receipt$'):
                encode_receipt(submission)
            serializer.assert_not_called()

    def test_extra_receipt_fields_rejected(self):
        _, _, _, submission = self.setup_reply()
        receipt = submission['receipt'] | {'effects': [('launch', 'hidden', 99)]}
        with self.assertRaisesRegex(InvalidFrame, '^receipt$'):
            encode_receipt(receipt)

    def test_actual_dispositions_round_trip(self):
        m, c, request, first = self.setup_reply()
        receipts = [first['receipt'], c.submit(request | {'sequence': 2})['receipt'],
                    c.submit(request | {'sequence': 3, 'services': ['b']})['receipt']]
        for sequence in range(4, 67):
            c.submit(request | {'sequence': sequence})
        receipts.append(c.submit(request)['receipt'])
        c.failed = True
        receipts.append(c.submit(request)['receipt'])
        self.assertEqual([r['disposition'] for r in receipts],
                         ['accepted', 'joined', 'rejected', 'unknown', 'unknown'])
        for receipt in receipts:
            frame = encode_receipt(receipt)
            decoded = decode_receipt(frame)
            self.assertEqual(encode_receipt(decoded), frame)
            self.assertEqual(decoded['disposition'], receipt['disposition'])
        decoded['reason'] = 'changed'
        self.assertEqual(receipts[-1]['reason'], 'session-failed')

    def test_bounds_and_normalization(self):
        _, _, _, submission = self.setup_reply()
        receipt = submission['receipt']
        receipt['sequence'] = MAX_ID
        receipt['operation'].update(epoch='😀' * 64, revision='é' * 64,
                                    id=MAX_ID, deadline=MAX_ID,
                                    scope=[chr(97 + i) * 32 for i in reversed(range(8))])
        frame = encode_receipt(receipt)
        self.assertLessEqual(len(frame), 4100)
        decoded = decode_receipt(frame)
        self.assertEqual(decoded['operation']['epoch'], '😀' * 64)
        self.assertEqual(decoded['operation']['scope'], sorted(receipt['operation']['scope']))
        self.assertEqual(encode_receipt(decoded), frame)

    def test_invalid_values_never_reach_serializer(self):
        _, _, _, submission = self.setup_reply()
        good = submission['receipt']
        invalid = [None, {}, good | {'schema': 'unknown'}, good | {'sequence': True},
                   good | {'sequence': MAX_ID + 1}, good | {'operation': None},
                   good | {'reason': 'unexpected'}, good | {'disposition': 'complete'},
                   good | {'disposition': 'unknown', 'reason': 'session-failed'},
                   good | {'disposition': 'rejected', 'reason': 'secret\x1b'},
                   good | {'reason': 'x' * 10000}]
        for field, value in [('epoch', 'x' * 65), ('epoch', '\ud800'), ('id', 0),
                             ('deadline', -1), ('deadline', MAX_ID + 1),
                             ('shutdown', 1), ('shutdown', True), ('kind', 'restart'),
                             ('scope', ['a'] * 9), ('scope', ['a', 'a']),
                             ('scope', ['INVALID']), ('scope', ['a' * 33])]:
            invalid.append(good | {'operation': good['operation'] | {field: value}})
        cyclic = {}; cyclic['operation'] = cyclic
        invalid.append(cyclic)
        for value in invalid:
            with self.subTest(value_type=type(value).__name__), patch(
                    'prototypes.runtime_model.control_reply.json.dumps') as serializer:
                with self.assertRaisesRegex(InvalidFrame, '^receipt$'):
                    encode_receipt(value)
                serializer.assert_not_called()

    def test_decode_checks_depth_duplicates_and_fields(self):
        _, _, _, submission = self.setup_reply()
        frame = encode_receipt(submission['receipt'])
        self.assertEqual(decode_receipt(frame)['operation']['scope'], ['a'])
        body = frame[4:]
        bad = [body[:-1] + b',"effects":[]}', body[:-1] + b',"sequence":2}',
               body.replace(b'["a"]', b'[["a"]]'), body.replace(b'100', b'1.0'),
               body.replace(b'"accepted"', b'"complete"')]
        for candidate in bad:
            with self.assertRaises(InvalidFrame):
                decode_receipt(len(candidate).to_bytes(4, 'big') + candidate)
        for candidate in [frame[:-1], frame + b' ', (4097).to_bytes(4, 'big') + b' ']:
            with self.assertRaises(InvalidFrame):
                decode_receipt(candidate)
        with self.assertRaisesRegex(InvalidFrame, '^depth$'):
            decode_request(frame)

    def test_output_failure_preserves_owned_work(self):
        m, c, request, submission = self.setup_reply()
        before = deepcopy(m.__dict__)
        with patch('prototypes.runtime_model.control_reply.json.dumps', side_effect=MemoryError):
            with self.assertRaises(MemoryError):
                encode_receipt(submission['receipt'])
        self.assertEqual(m.__dict__, before)
        self.assertFalse(c.failed)
        self.assertEqual(c.submit(request)['effects'], ())
        self.assertTrue(m.state['a'].owned)
        self.assertEqual(decode_receipt(encode_receipt(submission['receipt']))['sequence'], 1)


class CodecTests(unittest.TestCase):
    BODY = (b'{"version":0,"epoch":"boot-1","revision":"config-1",'
            b'"sequence":1,"verb":"start","services":["a"],"budget":100}')

    @staticmethod
    def frame(body):
        return len(body).to_bytes(4, 'big') + body

    def test_hand_authored_frame(self):
        request = decode_request(self.frame(self.BODY))
        self.assertEqual(request, dict(version=0, epoch='boot-1', revision='config-1',
                                      sequence=1, verb='start', services=['a'], budget=100))

    def test_frame_length_edges_before_parser(self):
        padded = self.BODY + b' ' * (4096 - len(self.BODY))
        self.assertEqual(decode_request(self.frame(padded))['sequence'], 1)
        invalid = [b'', b'\x00', b'\x00\x00\x00\x00', self.frame(b''),
                   self.frame(padded + b' '), (4097).to_bytes(4, 'big') + b' ',
                   (0xffffffff).to_bytes(4, 'big') + b' ',
                   self.frame(self.BODY)[:-1], self.frame(self.BODY) + b' ',
                   self.frame(self.BODY) * 2]
        for frame in invalid:
            with self.subTest(frame_size=len(frame)), patch(
                    'prototypes.runtime_model.control_codec.json.loads') as parser:
                with self.assertRaisesRegex(InvalidFrame, '^frame-length$'):
                    decode_request(frame)
                parser.assert_not_called()
        for value in [None, 'text', bytearray(self.frame(self.BODY)), memoryview(self.BODY)]:
            with self.assertRaisesRegex(InvalidFrame, '^frame-type$'):
                decode_request(value)

    def test_depth_checked_before_parser(self):
        for body in [b'{"x":[[]]}', b'{"x":{"y":{}}}', b'[' * 1000 + b']' * 1000]:
            with self.subTest(body_size=len(body)), patch(
                    'prototypes.runtime_model.control_codec.json.loads') as parser:
                with self.assertRaisesRegex(InvalidFrame, '^depth$'):
                    decode_request(self.frame(body))
                parser.assert_not_called()
        self.assertEqual(decode_request(self.frame(b'{"x":[1,2]}')), {'x': [1, 2]})

    def test_quoted_delimiters_and_escape_parity(self):
        value = {'x': ['[]{}', '\\', '\\"[[[', '"', '\\\\', '\n']}
        self.assertEqual(decode_request(self.frame(json.dumps(value).encode())), value)
        for body in [b'{]', b'{"x":1', b'{"x":"unterminated}', b'{"x":}',
                     b'{"x":1,}', b'{}{}', b'{"x":"\n"}']:
            with self.subTest(body=body), self.assertRaisesRegex(InvalidFrame, '^json$'):
                decode_request(self.frame(body))

    def test_duplicate_decoded_keys(self):
        for body in [b'{"x":1,"x":2}', b'{"x":1,"\\u0078":2}',
                     b'{"x":{"y":1,"y":2}}']:
            with self.subTest(body=body), self.assertRaisesRegex(InvalidFrame, '^duplicate-key$'):
                decode_request(self.frame(body))

    def test_unicode_and_root(self):
        self.assertEqual(decode_request(self.frame(b'{"x":"\\ud83d\\ude00"}')), {'x': '😀'})
        self.assertEqual(decode_request(self.frame('{"x":"é"}'.encode())), {'x': 'é'})
        for body in [b'{"x":"\xff"}', b'{"x":"\xed\xa0\x80"}']:
            with self.assertRaisesRegex(InvalidFrame, '^utf8$'):
                decode_request(self.frame(body))
        for body in [b'{"x":"\\ud800"}', b'{"\\udfff":1}', b'{"x":["\\ud800"]}']:
            with self.assertRaisesRegex(InvalidFrame, '^unicode$'):
                decode_request(self.frame(body))
        with self.assertRaisesRegex(InvalidFrame, '^json$'):
            decode_request(self.frame(b'\xef\xbb\xbf{}'))
        for body in [b'[]', b'1', b'null', b'true', b'"text"']:
            with self.assertRaisesRegex(InvalidFrame, '^root$'):
                decode_request(self.frame(body))

    def test_numeric_token_bounds(self):
        for number in [b'0', b'-1', b'18446744073709551615', b'99999999999999999999',
                       b'-99999999999999999999']:
            self.assertEqual(decode_request(self.frame(b'{"x":' + number + b'}'))['x'], int(number))
        for number in [b'100000000000000000000', b'-100000000000000000000', b'1.0',
                       b'1e0', b'1E999999', b'NaN', b'Infinity', b'-Infinity']:
            with self.subTest(number=number), self.assertRaisesRegex(InvalidFrame, '^number$'):
                decode_request(self.frame(b'{"x":' + number + b'}'))
        for number in [b'01', b'+1', b'--1']:
            with self.assertRaisesRegex(InvalidFrame, '^json$'):
                decode_request(self.frame(b'{"x":' + number + b'}'))

    def test_invalid_frames_and_payloads_leave_manager_untouched(self):
        m = Model([Service('a')])
        c = Control(m)
        original = deepcopy(m.__dict__)
        bodies = [b'{"x":[[]]}', b'{"version":0,"version":1}', b'{}',
                  self.BODY.replace(b'"version":0', b'"version":true'),
                  self.BODY.replace(b'"version":0', b'"version":1'),
                  self.BODY.replace(b'"sequence":1', b'"sequence":18446744073709551616'),
                  self.BODY.replace(b'"sequence":1', b'"sequence":-1'),
                  self.BODY.replace(b'"budget":100', b'"budget":1000001'),
                  self.BODY.replace(b'"boot-1"', b'"wrong"'),
                  self.BODY.replace(b'["a"]', b'["a","a"]'),
                  self.BODY.replace(b'["a"]', b'["missing"]'),
                  self.BODY[:-1] + b',"caller":"owner"}']
        for body in bodies:
            with self.subTest(body=body), self.assertRaises((InvalidFrame, InvalidRequest)):
                c.submit(decode_request(self.frame(body)))
            self.assertEqual(m.__dict__, original)
            self.assertEqual(c.high_water, 0)
            self.assertEqual(len(c.receipts), 0)
        self.assertEqual(c.submit(decode_request(self.frame(self.BODY)))['effects'],
                         (('launch', 'a', 1),))

    def test_equivalent_encoding_replays_without_effects(self):
        m = Model([Service('a'), Service('b')])
        c = Control(m)
        first = c.submit(decode_request(self.frame(self.BODY.replace(b'["a"]', b'["a","b"]'))))
        other = (b' { "budget":100,"services":["b","\\u0061"],"verb":"start",'
                 b'"sequence":1,"revision":"config-1","epoch":"boot-1","version":0 }\n')
        before = deepcopy(m.__dict__)
        replay = c.submit(decode_request(self.frame(other)))
        self.assertTrue(replay['replayed'])
        self.assertEqual(replay['receipt'], first['receipt'])
        self.assertEqual(replay['effects'], ())
        with self.assertRaisesRegex(InvalidRequest, 'identity conflict'):
            c.submit(decode_request(self.frame(other.replace(b'100', b'101'))))
        self.assertEqual(m.__dict__, before)


class ControlTests(unittest.TestCase):
    def test_reconstruction_cannot_replay_completed_activation(self):
        m, c = self.setup_control()
        first = c.submit(self.request())
        m.batch([('launched', 'a', 1, m.epoch, 0), ('ready', 'a', 1, m.epoch, 0)])
        c.submit(self.request(2, verb='stop'))
        m.batch([('exit', 'a', 1, m.epoch, 0)])
        m.batch([('cleaned', 'a', 1, m.epoch, 0)])
        before = deepcopy(m.__dict__)
        with self.assertRaisesRegex(InvalidRequest, 'control already claimed'):
            Control(m)
        replay = c.submit(self.request())
        self.assertEqual(replay['receipt'], first['receipt'])
        self.assertEqual(replay['effects'], ())
        self.assertEqual(m.__dict__, before)
        self.assertFalse(m.state['a'].owned)

    def test_disconnect_cannot_reset_retired_sequences(self):
        m, c = self.setup_control()
        for sequence in range(1, 66):
            c.submit(self.request(sequence, verb='stop'))
        c.disconnect()
        before = deepcopy(m.__dict__)
        with self.assertRaisesRegex(InvalidRequest, 'control already claimed'):
            Control(m)
        retired = c.submit(self.request(verb='stop'))
        self.assertEqual(retired['receipt']['reason'], 'receipt-retired')
        self.assertEqual(retired['effects'], ())
        self.assertEqual(c.high_water, 65)
        self.assertEqual(len(c.receipts), 64)
        self.assertEqual(m.__dict__, before)

    def test_failed_session_cannot_be_replaced(self):
        m, c = self.setup_control()
        start = m.start
        def interrupted(*args, **kwargs):
            start(*args, **kwargs)
            raise RuntimeError('ambiguous dispatch')
        m.start = interrupted
        with self.assertRaisesRegex(RuntimeError, 'ambiguous dispatch'):
            c.submit(self.request())
        del m.start
        before = deepcopy(m.__dict__)
        with self.assertRaisesRegex(InvalidRequest, 'control already claimed'):
            Control(m)
        self.assertEqual(c.submit(self.request())['receipt']['reason'], 'session-failed')
        self.assertEqual(m.__dict__, before)
        self.assertTrue(m.state['a'].owned)

    def setup_control(self):
        model = Model([Service('a', milestone='notified-ready'), Service('b')])
        return model, Control(model)

    def request(self, sequence=1, **changes):
        return dict(version=0, epoch='boot-1', revision='config-1',
                    sequence=sequence, verb='start', services=['a'], budget=100) | changes

    def test_replay_never_reissues_effects(self):
        m, c = self.setup_control()
        original = c.submit(self.request())
        self.assertEqual(original['effects'], (('launch', 'a', 1),))
        before = deepcopy(m.__dict__)
        replay = c.submit(self.request())
        self.assertEqual(replay['receipt'], original['receipt'])
        self.assertTrue(replay['replayed'])
        self.assertEqual(replay['effects'], ())
        self.assertEqual(m.__dict__, before)
        m.batch([('launched', 'a', 1, m.epoch, 0), ('ready', 'a', 1, m.epoch, 0)])
        self.assertEqual(c.submit(self.request())['effects'], ())
        self.assertEqual(c.observe(m.epoch, 1)['outcome'], 'success')

    def test_join_differs_from_changed_replay(self):
        m, c = self.setup_control()
        first = c.submit(self.request())
        with self.assertRaisesRegex(InvalidRequest, 'identity conflict'):
            c.submit(self.request(budget=999))
        joined = c.submit(self.request(2, budget=999))
        self.assertEqual(joined['receipt']['disposition'], 'joined')
        self.assertEqual(joined['receipt']['operation'], first['receipt']['operation'])
        self.assertEqual(joined['effects'], ())

    def test_evicted_receipt_never_becomes_new(self):
        m, c = self.setup_control()
        for sequence in range(1, 66):
            c.submit(self.request(sequence))
        self.assertEqual(len(c.receipts), 64)
        self.assertEqual(c.high_water, 65)
        before = deepcopy(m.__dict__)
        retired = c.submit(self.request())
        self.assertEqual(retired['receipt']['reason'], 'receipt-retired')
        self.assertEqual(retired['effects'], ())
        self.assertEqual(m.__dict__, before)
        self.assertEqual(c.observe(m.epoch, 1)['outcome'], 'pending')

    def test_invalid_payloads_do_not_consume_sequence(self):
        m, c = self.setup_control()
        before = deepcopy(m.__dict__)
        bad = [None, {}, self.request(extra=1)]
        for key, value in [('version', True), ('sequence', True), ('budget', False),
                           ('sequence', 0), ('sequence', MAX_ID + 1), ('budget', 1000001),
                           ('epoch', 'wrong'), ('revision', 'wrong'), ('verb', 'restart'),
                           ('services', ['a', 'a']), ('services', ['unknown']),
                           ('services', 'a'), ('services', []), ('services', [1]),
                           ('services', ['a'] * 9)]:
            bad.append(self.request(**{key: value}))
        bad.append(self.request(verb='shutdown'))
        bad.append(self.request(2))
        for request in bad:
            with self.subTest(request=request), self.assertRaises(InvalidRequest):
                c.submit(request)
            self.assertEqual(c.high_water, 0)
            self.assertEqual(len(c.receipts), 0)
            self.assertEqual(m.__dict__, before)

    def test_conflict_receipt_is_cached(self):
        m, c = self.setup_control()
        c.submit(self.request())
        rejected = c.submit(self.request(2, services=['b']))
        self.assertEqual(rejected['receipt']['disposition'], 'rejected')
        self.assertEqual(c.high_water, 2)
        self.assertEqual(c.submit(self.request(2, services=['b']))['receipt'], rejected['receipt'])
        self.assertEqual(m.state['b'].generation, 0)

    def test_wait_and_disconnect_do_not_cancel(self):
        m, c = self.setup_control()
        c.submit(self.request())
        before = deepcopy(m.__dict__)
        self.assertEqual(c.wait(m.epoch, 1, now=4, deadline=5)['state'], 'pending')
        self.assertEqual(c.wait(m.epoch, 1, now=5, deadline=5)['state'], 'timeout')
        c.disconnect()
        self.assertEqual(m.__dict__, before)
        m.batch([('launched', 'a', 1, m.epoch, 0), ('ready', 'a', 1, m.epoch, 0)])
        self.assertEqual(c.wait(m.epoch, 1, now=6, deadline=5)['state'], 'complete')
        self.assertEqual(c.wait('old', 1, now=6, deadline=5)['state'], 'unknown')
        for value in [True, -1, MAX_ID + 1]:
            with self.assertRaises(InvalidRequest):
                c.wait(m.epoch, 1, now=value, deadline=5)

    def test_supersession_keeps_late_launch_owned(self):
        m, c = self.setup_control()
        c.submit(self.request())
        stop = c.submit(self.request(2, verb='stop'))
        self.assertEqual(stop['effects'], ())
        self.assertEqual(c.observe(m.epoch, 1)['outcome'], 'cancelled')
        self.assertEqual(m.batch([('launched', 'a', 1, m.epoch, 0)]), [('stop', 'a', 1)])
        self.assertTrue(m.state['a'].owned)
        self.assertEqual(c.observe(m.epoch, 2)['outcome'], 'pending')
        m.batch([('exit', 'a', 1, m.epoch, 0)])
        m.batch([('cleaned', 'a', 1, m.epoch, 0)])
        self.assertEqual(c.observe(m.epoch, 2)['outcome'], 'success')

    def test_snapshots_and_normalization(self):
        m, c = self.setup_control()
        request = self.request(services=['b', 'a'])
        result = c.submit(request)
        request['services'].clear()
        result['receipt']['operation']['deadline'] = -1
        replay = c.submit(self.request(services=['a', 'b']))
        self.assertEqual(replay['receipt']['operation']['deadline'], 100)
        observation = c.observe(m.epoch, 1)
        observation['operation']['deadline'] = -2
        self.assertEqual(c.observe(m.epoch, 1)['operation']['deadline'], 100)

    def test_identity_exhaustion(self):
        m, c = self.setup_control()
        m.next_id = MAX_ID
        result = c.submit(self.request())
        self.assertEqual(result['receipt']['operation']['id'], MAX_ID)
        with self.assertRaisesRegex(InvalidRequest, 'exhausted'):
            c.submit(self.request(2))
        self.assertEqual(c.submit(self.request())['effects'], ())
        self.assertEqual(c.high_water, 1)
        m, c = self.setup_control()
        c.high_water = MAX_ID - 1
        c.submit(self.request(MAX_ID))
        with self.assertRaises(InvalidRequest):
            c.submit(self.request(MAX_ID + 1))
        self.assertEqual(c.submit(self.request(MAX_ID))['effects'], ())

    def test_session_failure_cannot_redispatch(self):
        m, c = self.setup_control()
        original = m.start
        def broken(*args, **kwargs):
            original(*args, **kwargs)
            raise RuntimeError('failure after effects')
        m.start = broken
        with self.assertRaises(RuntimeError):
            c.submit(self.request())
        m.start = original
        self.assertTrue(c.failed)
        self.assertTrue(m.state['a'].owned)
        self.assertEqual(c.submit(self.request())['receipt']['reason'], 'session-failed')
        self.assertEqual(m.state['a'].generation, 1)
        self.assertEqual(c.observe(m.epoch, 1)['outcome'], 'unknown')
        m, c = self.setup_control()
        m.revision = 'changed'
        self.assertEqual(c.submit(self.request())['receipt']['reason'], 'session-failed')
        self.assertEqual(m.state['a'].generation, 0)

    def test_retired_operation_observation_is_unknown(self):
        m, c = self.setup_control()
        for sequence in range(1, 67):
            c.submit(self.request(sequence, verb='stop'))
        self.assertEqual(len(m.operations), 64)
        self.assertEqual(c.observe(m.epoch, 1)['outcome'], 'unknown')
        self.assertEqual(c.observe(m.epoch, 66)['outcome'], 'success')

    def test_shutdown_receipt_preserves_distinct_intent(self):
        m, c = self.setup_control()
        c.submit(self.request(services=['a', 'b']))
        stopped = c.submit(self.request(2, services=['a', 'b'], verb='stop'))
        self.assertFalse(stopped['receipt']['operation']['shutdown'])
        rejected = c.submit(self.request(3, services=['a', 'b'], verb='shutdown'))
        self.assertEqual(rejected['receipt']['disposition'], 'rejected')
        self.assertFalse(m.closed)
        for name in ['a', 'b']:
            m.batch([('launched', name, 1, m.epoch, 0)])
            m.batch([('exit', name, 1, m.epoch, 0)])
            m.batch([('cleaned', name, 1, m.epoch, 0)])
        shutdown = c.submit(self.request(4, services=['a', 'b'], verb='shutdown'))
        self.assertTrue(shutdown['receipt']['operation']['shutdown'])
        self.assertTrue(m.closed)


def event(m, kind, name='a', value=0, generation=None, epoch=None):
    return (kind, name, m.state[name].generation if generation is None else generation,
            m.epoch if epoch is None else epoch, value)


def inject(m, kind, name='a', value=0, **kw):
    return m.batch([event(m, kind, name, value, **kw)])


def ready_model(retries=0):
    m = Model([Service('a', milestone='notified-ready', retries=retries)])
    m.start(['a'])
    inject(m, 'launched')
    return m


class RuntimeTests(unittest.TestCase):
    def test_stopped_preserves_kind_and_requires_cleanup(self):
        m = Model([Service('a', retries=1)])
        m.start(['a'])
        effects = m.batch([('stopped', 'a', 1, m.epoch, 143)])
        self.assertEqual(m.state['a'].terminal, 'stopped')
        self.assertEqual(m.state['a'].terminal_detail, 143)
        self.assertEqual(effects, [('reclaim', 'a', 1)])
        self.assertTrue(m.state['a'].owned)
        self.assertEqual(m.state['a'].generation, 1)
        m.batch([('cleaned', 'a', 1, m.epoch, 0)])
        self.assertFalse(m.state['a'].owned)
        self.assertEqual(m.batch(now=1), [('launch', 'a', 2)])

    def test_stopped_never_completes_oneshot_or_accepts_same_cut_ready(self):
        m = Model([Service('a', kind='oneshot', milestone='completed')])
        m.start(['a'])
        m.batch([('launched', 'a', 1, m.epoch, 0),
                 ('ready', 'a', 1, m.epoch, 0), ('stopped', 'a', 1, m.epoch, 0)])
        state = m.state['a']
        self.assertEqual(state.terminal, 'stopped')
        self.assertFalse(state.completed or state.ready or state.started)
        self.assertEqual(state.outcome, 'failure')

    def test_stopped_after_cancel_cannot_retry(self):
        m = Model([Service('a', retries=1)])
        m.start(['a']); m.batch([('launched', 'a', 1, m.epoch, 0)])
        m.stop(['a'])
        self.assertEqual(m.batch([('stopped', 'a', 1, m.epoch, 143)]), [('reclaim', 'a', 1)])
        self.assertFalse(m.state['a'].retry_allowed)
        m.batch([('cleaned', 'a', 1, m.epoch, 0)])
        self.assertEqual(m.batch(now=1), [])
        self.assertEqual(m.operations[-1].status, 'success')

    def test_stopped_stale_duplicate_and_invalid_detail(self):
        m = Model([Service('a')]); m.start(['a'])
        before = deepcopy(m.__dict__)
        for detail in (True, -1, 256, '143'):
            with self.assertRaises(Rejected):
                m.batch([('stopped', 'a', 1, m.epoch, detail)])
            self.assertEqual(m.__dict__, before)
        m.batch([('stopped', 'a', 0, m.epoch, 143),
                 ('stopped', 'a', 1, 'other', 143)])
        self.assertIsNone(m.state['a'].terminal)
        m.batch([('stopped', 'a', 1, m.epoch, 143)])
        self.assertEqual(m.batch([('stopped', 'a', 1, m.epoch, 0)]), [])
        self.assertEqual(m.state['a'].terminal_detail, 143)


    def test_T01_stale_generation(self):
        m = ready_model(1)
        inject(m, 'fault'); inject(m, 'cleaned'); m.batch(now=1)
        inject(m, 'launched')
        self.assertEqual(m.state['a'].generation, 2)
        inject(m, 'ready', generation=1)
        self.assertFalse(m.state['a'].ready)
        inject(m, 'ready', epoch='old-boot')
        self.assertFalse(m.state['a'].ready)

    def test_T02_observation_lost(self):
        m = ready_model()
        inject(m, 'lost')
        self.assertEqual(m.status('a')['phase'], 'unknown')
        self.assertTrue(m.status('a')['owned'])
        self.assertFalse(m.status('a')['ready'])
        self.assertEqual(m.operations[-1].status, 'incomplete')

    def test_T03_invalid_graph(self):
        cases = [[Service('a', after=('missing',))],
                 [Service('a', after=('b',)), Service('b', after=('a',))],
                 [Service('a', supported=False)], [Service('a'), Service('a')],
                 [Service('a', requires=(('a', 'started'),))]]
        for graph in cases:
            with self.subTest(graph=graph), self.assertRaises(Rejected):
                Model(graph)

    def test_T04_after_rejection_and_requires_block(self):
        m = Model([Service('a'), Service('b', after=('a',)),
                   Service('c', requires=(('a', 'started'),))])
        self.assertEqual(m.start(['b', 'c'])[1], [('launch', 'a', 1)])
        effects = inject(m, 'denied')
        self.assertIn(('launch', 'b', 1), effects)
        self.assertEqual(m.state['c'].generation, 0)
        self.assertEqual(m.state['c'].reason, 'dependency-failed')

    def test_T05_oneshot_session(self):
        m = Model([Service('a', kind='oneshot', milestone='completed')])
        m.start(['a']); inject(m, 'launched'); inject(m, 'exit'); inject(m, 'cleaned')
        self.assertEqual(m.start(['a'])[1], [])
        self.assertEqual(m.state['a'].generation, 1)
        m.stop(['a'])
        self.assertEqual(m.start(['a'])[1], [('launch', 'a', 2)])
        fresh = Model([Service('a', kind='oneshot', milestone='completed')], epoch='new')
        self.assertFalse(fresh.state['a'].completed)

    def test_T06_strong_evidence_and_delayed_admission(self):
        with self.assertRaises(Rejected):
            Model([Service('a'), Service('b', requires=(('a', 'notified-ready'),))])
        m = Model([Service('a', milestone='notified-ready'),
                   Service('b', requires=(('a', 'notified-ready'),))])
        m.start(['b']); self.assertEqual(inject(m, 'launched'), [])
        self.assertEqual(m.state['b'].generation, 0)
        self.assertEqual(inject(m, 'ready'), [('launch', 'b', 1)])

    def test_T07_all_24_observation_permutations(self):
        for order in itertools.permutations(('ready', 'fault', 'log', 'launched')):
            with self.subTest(order=order):
                m = Model([Service('a', milestone='notified-ready'),
                           Service('b', requires=(('a', 'notified-ready'),))])
                m.start(['b'])
                effects = m.batch([event(m, k, value='noise' if k == 'log' else 0) for k in order])
                self.assertNotIn(('launch', 'b', 1), effects)
                self.assertFalse(m.state['a'].ready)
                self.assertEqual(m.state['a'].phase, 'terminal')

    def test_T07_deadline_and_stop_win_ready(self):
        m = ready_model()
        m.batch([event(m, 'ready')], now=10)
        self.assertFalse(m.state['a'].ready)
        self.assertEqual(m.state['a'].reason, 'startup-timeout')
        m = ready_model(); m.stop(['a'])
        inject(m, 'ready')
        self.assertFalse(m.state['a'].ready)

    def test_T08_later_provider_loss(self):
        m = Model([Service('a', milestone='notified-ready', retries=1),
                   Service('b', requires=(('a', 'notified-ready'),))])
        m.start(['b']); inject(m, 'launched'); inject(m, 'ready'); inject(m, 'launched', 'b')
        effects = inject(m, 'fault')
        self.assertEqual(m.state['b'].phase, 'running')
        self.assertNotIn(('stop', 'b', 1), effects)
        self.assertEqual(m.status('b')['dependency_loss'], ('a',))

    def test_T09_partial_setup_needs_reclaim(self):
        m = Model([Service('a', retries=2)])
        m.start(['a'])
        self.assertEqual(inject(m, 'denied'), [('reclaim', 'a', 1)])
        self.assertTrue(m.state['a'].owned)
        inject(m, 'cleanup_failed')
        self.assertEqual(m.operations[-1].status, 'incomplete')
        with self.assertRaises(Rejected): m.start(['a'])
        self.assertEqual(m.state['a'].generation, 1)

    def test_T11_finite_retry_budget_and_no_ready_reset(self):
        m = ready_model(2)
        for generation in range(1, 4):
            inject(m, 'ready')
            inject(m, 'fault'); inject(m, 'cleaned')
            if generation < 3:
                self.assertEqual(m.batch(now=generation), [('launch', 'a', generation + 1)])
                inject(m, 'launched')
        self.assertEqual(m.state['a'].generation, 3)
        self.assertEqual(m.state['a'].retries_used, 2)
        self.assertEqual(m.batch(now=20), [])
        self.assertEqual(m.state['a'].outcome, 'failure')

    def test_T11_success_never_retries(self):
        m = ready_model(2); inject(m, 'ready'); inject(m, 'exit'); inject(m, 'cleaned')
        self.assertEqual(m.batch(now=50), [])
        self.assertEqual(m.state['a'].generation, 1)

    def test_T12_retry_after_completed_operation(self):
        m = ready_model(2); inject(m, 'ready')
        self.assertEqual(m.operations[-1].status, 'success')
        inject(m, 'fault'); inject(m, 'cleaned')
        m.start(['a'])
        m.batch(now=1); inject(m, 'launched'); inject(m, 'ready')
        self.assertEqual(m.state['a'].retries_used, 1)
        m.start(['a'])
        self.assertEqual(m.state['a'].retries_used, 1)

    def test_T13_operation_timeout_partial_success(self):
        m = Model([Service('a', milestone='notified-ready', startup=100),
                   Service('b', requires=(('a', 'started'),))])
        m.start(['b'], budget=5); inject(m, 'launched'); inject(m, 'launched', 'b')
        effects = m.batch(now=5)
        self.assertIn(('stop', 'a', 1), effects)
        self.assertEqual(m.state['b'].phase, 'running')
        self.assertFalse(m.state['a'].desired)
        inject(m, 'exit'); inject(m, 'cleaned')
        self.assertEqual(m.operations[-1].status, 'failed')

    def test_T14_rejected_stop_is_pure(self):
        m = Model([Service('a'), Service('b', requires=(('a', 'started'),))])
        m.start(['b']); inject(m, 'launched'); inject(m, 'launched', 'b')
        before = (m.status('a'), m.status('b'), m.events, list(m.records))
        with self.assertRaises(Rejected): m.stop(['a'])
        self.assertEqual(before, (m.status('a'), m.status('b'), m.events, list(m.records)))

    def test_T15_stop_order_and_cleanup_gate(self):
        m = Model([Service('a'), Service('b', requires=(('a', 'started'),))])
        m.start(['b']); inject(m, 'launched'); inject(m, 'launched', 'b')
        self.assertEqual(m.stop(['a', 'b'])[1], [('stop', 'b', 1)])
        self.assertEqual(inject(m, 'exit', 'b'), [('reclaim', 'b', 1)])
        self.assertEqual(inject(m, 'cleaned', 'b'), [('stop', 'a', 1)])
        inject(m, 'exit'); inject(m, 'cleanup_failed')
        self.assertEqual(m.operations[-1].status, 'incomplete')

    def test_T15_no_replacement_before_reclaim(self):
        m = ready_model(2); inject(m, 'fault')
        m.batch(now=1)
        self.assertEqual(m.state['a'].generation, 1)
        self.assertNotEqual(m.state['a'].phase, 'retry')
        inject(m, 'cleaned'); m.batch(now=2)
        self.assertEqual(m.state['a'].generation, 2)

    def test_T15_restart_live_only(self):
        m = Model([Service('a')])
        with self.assertRaises(Rejected): m.stop(['a'], restart='a')
        m.start(['a']); inject(m, 'launched')
        op, effects = m.stop(['a'], restart='a')
        self.assertEqual(effects, [('stop', 'a', 1)])
        inject(m, 'exit'); self.assertEqual(inject(m, 'cleaned'), [('launch', 'a', 2)])
        inject(m, 'launched')
        self.assertEqual(m.operations[-1].id, op)
        self.assertEqual(m.operations[-1].status, 'success')

    def test_T16_late_launch_still_owned(self):
        m = Model([Service('a')]); first, _ = m.start(['a'])
        _, effects = m.stop(['a'])
        self.assertEqual(effects, [])
        self.assertEqual(m.operations[0].status, 'cancelled')
        self.assertEqual(inject(m, 'launched'), [('stop', 'a', 1)])
        self.assertTrue(m.state['a'].owned)
        inject(m, 'exit'); inject(m, 'cleaned')
        self.assertEqual(m.operations[-1].status, 'success')
        self.assertFalse(m.state['a'].owned)

    def test_T18_partial_graph_failure(self):
        m = Model([Service('a'), Service('b')]); m.start(['a', 'b'])
        inject(m, 'launched'); inject(m, 'denied', 'b'); inject(m, 'cleaned', 'b')
        self.assertEqual(m.operations[-1].status, 'failed')
        self.assertEqual(m.state['a'].phase, 'running')

    def test_T19_shutdown_closes_every_admission(self):
        m = ready_model(1)
        m.stop(['a'], shutdown=True)
        with self.assertRaises(Rejected): m.start(['a'])
        inject(m, 'exit'); inject(m, 'cleaned')
        self.assertEqual(m.batch(now=20), [])
        self.assertEqual(m.state['a'].generation, 1)

    def test_T20_logs_are_bounded_untrusted_data(self):
        m = ready_model()
        for _ in range(70): inject(m, 'log', value='generation=999; ready=true')
        self.assertEqual(len(m.records), 64)
        self.assertGreater(m.dropped, 0)
        self.assertEqual(m.state['a'].generation, 1)
        self.assertFalse(m.state['a'].ready)
        m.stop(['a']); inject(m, 'exit'); inject(m, 'cleaned')
        self.assertFalse(m.state['a'].owned)

    def test_T21_static_and_event_bounds(self):
        for graph in [[Service('a')]*9, [Service('a', retries=3)],
                      [Service('a', after=('b',)*17), Service('b')]]:
            with self.assertRaises(Rejected): Model(graph)
        m = ready_model()
        with self.assertRaises(Rejected): m.batch([event(m, 'log')]*5)
        with self.assertRaises(Rejected): inject(m, 'log', value='x'*129)
        while m.events < 256: m.batch()
        with self.assertRaises(Rejected): m.batch()
        self.assertEqual(m.events, 256)

    def test_T21_jump_does_not_refresh_deadline(self):
        m = ready_model()
        effects = m.batch(now=100)
        self.assertIn(('force', 'a', 1), effects)
        self.assertEqual(m.operations[-1].status, 'incomplete')
        self.assertTrue(m.state['a'].owned)

    def test_T07_oneshot_exit_at_deadline_is_failure(self):
        m = Model([Service('a', kind='oneshot', milestone='completed')])
        m.start(['a']); inject(m, 'launched')
        m.batch([event(m, 'exit')], now=10)
        self.assertFalse(m.state['a'].completed)
        self.assertEqual(m.state['a'].reason, 'startup-timeout')
        inject(m, 'cleaned')
        self.assertEqual(m.operations[-1].status, 'failed')

    def test_T08_retry_rechecks_provider(self):
        m = Model([Service('a'), Service('b', retries=1, requires=(('a', 'started'),))])
        m.start(['b']); inject(m, 'launched'); inject(m, 'launched', 'b')
        inject(m, 'fault', 'b'); inject(m, 'cleaned', 'b')
        inject(m, 'fault'); inject(m, 'cleaned')
        self.assertEqual(m.batch(now=1), [])
        self.assertEqual(m.state['b'].generation, 1)

    def test_T14_retry_pending_consumer_blocks_provider_stop(self):
        m = Model([Service('a'), Service('b', retries=1, requires=(('a', 'started'),))])
        m.start(['b']); inject(m, 'launched'); inject(m, 'launched', 'b')
        inject(m, 'fault', 'b'); inject(m, 'cleaned', 'b')
        with self.assertRaises(Rejected): m.stop(['a'])
        self.assertTrue(m.state['a'].desired)

    def test_T15_cleanup_ack_must_follow_effect(self):
        m = ready_model()
        inject(m, 'cleaned')
        self.assertTrue(m.state['a'].owned)
        self.assertEqual(m.state['a'].phase, 'running')

    def test_T17_join_does_not_extend_operation(self):
        m = ready_model()
        op = m.active.id
        deadline = m.active.deadline
        m.batch(now=1)
        self.assertEqual(m.start(['a'], budget=999), (op, []))
        self.assertEqual(m.active.deadline, deadline)
        # Reads model a waiting client; no timeout transport is implemented.
        self.assertEqual(m.status('a')['operation'], op)

    def test_C02_stop_join_preserves_deadline(self):
        m = ready_model()
        operation, _ = m.stop(['a'], budget=10)
        end = m.active.deadline
        m.batch(now=1)
        self.assertEqual(m.stop(['a'], budget=999), (operation, []))
        self.assertEqual(m.active.deadline, end)
        self.assertFalse(m.closed)

    def test_C03_stop_and_shutdown_do_not_join(self):
        for first_shutdown in (False, True):
            m = ready_model()
            m.stop(['a'], shutdown=first_shutdown)
            before = (m.status('a'), m.active.id, m.active.deadline,
                      m.closed, m.next_id, m.events)
            with self.assertRaises(Rejected):
                m.stop(['a'], shutdown=not first_shutdown)
            self.assertEqual(before, (m.status('a'), m.active.id, m.active.deadline,
                                      m.closed, m.next_id, m.events))
            operation = m.active.id
            self.assertEqual(m.stop(['a'], shutdown=first_shutdown), (operation, []))

    def test_C06_partial_stop_preserves_pending_start(self):
        m = Model([Service('a'), Service('b')])
        m.start(['a', 'b'])
        before = (m.status('a'), m.status('b'), m.active.id,
                  m.active.deadline, m.events, m.next_id)
        with self.assertRaises(Rejected):
            m.stop(['a'])
        self.assertEqual(before, (m.status('a'), m.status('b'), m.active.id,
                                 m.active.deadline, m.events, m.next_id))

    def test_T20_terminal_detail_and_detached_snapshot(self):
        m = ready_model(); inject(m, 'exit', value=42)
        snapshot = m.status('a')
        self.assertEqual(snapshot['terminal_detail'], 42)
        snapshot['desired'] = False
        self.assertTrue(m.state['a'].desired)

    def test_T09_duplicate_ready_has_no_new_effect(self):
        m = ready_model()
        self.assertEqual(inject(m, 'ready'), [])
        generation = m.state['a'].generation
        self.assertEqual(inject(m, 'ready'), [])
        self.assertEqual(m.state['a'].generation, generation)

    def test_T16_stop_cancels_retry_timer(self):
        m = ready_model(2); inject(m, 'ready'); inject(m, 'fault'); inject(m, 'cleaned')
        m.stop(['a'])
        self.assertEqual(m.batch(now=5), [])
        self.assertFalse(m.state['a'].desired)
        self.assertEqual(m.state['a'].generation, 1)

    def test_T21_invalid_batch_has_no_partial_effect(self):
        m = ready_model()
        before = (m.status('a'), m.now, m.events)
        with self.assertRaises(Rejected):
            m.batch([event(m, 'ready'), ('exit', 'a', 1, m.epoch, 'invalid')], now=3)
        self.assertEqual(before, (m.status('a'), m.now, m.events))

    def test_T21_seeded_bounded_event_traces(self):
        for seed in range(100):
            rng = random.Random(seed)
            m = ready_model(2)
            trace = []
            try:
                for _ in range(20):
                    kind = rng.choice(['launched', 'ready', 'fault', 'cleaned', 'log'])
                    e = event(m, kind)
                    cut_time = m.now + rng.randrange(2)
                    trace.append({'now': cut_time, 'event': e})
                    effects = m.batch([e], now=cut_time)
                    s = m.state['a']
                    self.assertLessEqual(s.generation, 3)
                    self.assertFalse(s.ready and s.phase != 'running')
                    self.assertFalse(s.phase == 'retry' and s.owned)
                    self.assertTrue(all(action in ('launch', 'stop', 'force', 'reclaim') for action, _, _ in effects))
            except Exception:
                # Failure output is a replayable counterexample, not a generated oracle.
                print(json.dumps({'seed': seed, 'events': trace, 'status': m.status('a')}, default=str))
                raise



class CutCoordinatorTests(unittest.TestCase):
    """Synthetic retained origins and counted application, never native resources."""
    @staticmethod
    def fixture(module=None):
        if module is None:
            from prototypes.runtime_model import cut_coordinator as module
        owner = object()
        sources = tuple(module.Source(owner, a, (1, 2, 3, 1, a, a + 4, 1, 6, 7, 1),
                                      0xb0000101 + a, phase, (phase, a, 18))
                        for a in range(2) for phase in range(1, 4))

        class Adapter:
            phases = (0, 0)
            ticket = None
            calls = 0
            reservations = 0
            mode = 'normal'

            def reserve(self, credits):
                if credits != 20 or self.ticket is not None:
                    raise module.CutError('journal busy')
                self.ticket = object()
                self.reservations += 1
                return self.ticket

            def cancel(self, ticket):
                if ticket is not self.ticket:
                    raise module.CutError('journal ticket')
                self.ticket = None

            def apply(self, ticket, cut):
                if ticket is not self.ticket:
                    raise module.CutError('journal ticket')
                self.calls += 1
                before = self.phases
                if self.mode == 'before-failure':
                    raise module.CutError('before mutation')
                after = list(before)
                for member in cut.members:
                    after[member.attempt] = member.phase
                if self.mode != 'no-op':
                    self.phases = tuple(after)
                if self.mode == 'after-failure':
                    raise module.CutError('after mutation')
                self.ticket = None
                return module.Receipt(cut if self.mode != 'wrong-cut' else module.Cut(cut.serial, cut.members),
                                      self.reservations, before, tuple(after))

        adapter = Adapter()
        return module, owner, sources, adapter, module.CutCoordinator(owner, sources, adapter)

    def test_cut_ordered_two_service_replay(self):
        m, owner, sources, adapter, c = self.fixture()
        for phase in range(3):
            members = (sources[phase], sources[phase + 3])
            cut = c.reserve(owner, members)
            self.assertEqual(c.inspect(owner, cut), ('reserved', None))
            self.assertIs(c.reserve(owner, members), cut)
            receipt = c.apply(owner, cut)
            self.assertEqual((receipt.before, receipt.after), ((phase, phase), (phase + 1, phase + 1)))
            self.assertIs(c.apply(owner, cut), receipt, 'duplicate receipt changed')
            self.assertEqual(adapter.calls, phase + 1, 'duplicate applied again')
        self.assertEqual((len(c.records), c.next_serial, adapter.reservations), (3, 4, 3))
        self.assertEqual(tuple(s.content for s in sources), tuple((p, a, 18) for a in range(2) for p in range(1, 4)))

    def test_cut_identity_denials(self):
        from dataclasses import replace
        m, owner, sources, adapter, c = self.fixture()
        cut = c.reserve(owner, (sources[0],))
        with self.assertRaisesRegex(m.CutError, 'owner'):
            c.apply(object(), cut)
        with self.assertRaisesRegex(m.CutError, 'cut identity'):
            c.apply(owner, m.Cut(cut.serial, cut.members))
        for i in range(10):
            token = list(sources[0].token)
            token[i] += 1
            with self.assertRaisesRegex(m.CutError, 'membership'):
                c.reserve(owner, (replace(sources[0], token=tuple(token)),))
        for changes in ({}, {'worker': 44}, {'content': (99,)}, {'owner': object()}, {'attempt': 1}):
            with self.assertRaisesRegex(m.CutError, 'membership'):
                c.reserve(owner, (replace(sources[0], **changes),))
        self.assertEqual((adapter.calls, c.next_serial, len(c.records)), (0, 2, 1), 'identity changed state')
        self.assertEqual(c.inspect(owner, cut), ('reserved', None))

    def test_cut_whole_membership_and_phase_denial(self):
        m, owner, sources, adapter, c = self.fixture()
        for members in ((), (sources[0], sources[1]), (sources[3], sources[0]), (sources[0],) * 3):
            with self.assertRaisesRegex(m.CutError, 'membership'):
                c.reserve(owner, members)
        for members in ((sources[1],), (sources[0], sources[4])):
            with self.assertRaisesRegex(m.CutError, 'phase'):
                c.reserve(owner, members)
        self.assertEqual((adapter.calls, adapter.reservations, c.records, c.next_serial), (0, 0, [], 1))

    def test_cut_busy_and_changed_preconditions(self):
        m, owner, sources, adapter, c = self.fixture()
        adapter.ticket = object()
        with self.assertRaisesRegex(m.CutError, 'journal busy'):
            c.reserve(owner, (sources[0],))
        self.assertEqual((c.records, c.next_serial), ([], 1))
        adapter.ticket = None
        cut = c.reserve(owner, (sources[0],))
        with self.assertRaisesRegex(m.CutError, 'busy'):
            c.reserve(owner, (sources[3],))
        adapter.phases = (0, 1)  # Explicit synthetic revalidation fault.
        with self.assertRaisesRegex(m.CutError, 'changed application state'):
            c.apply(owner, cut)
        self.assertEqual((adapter.calls, c.inspect(owner, cut)), (0, ('reserved', None)))
        c.cancel(owner, cut)
        self.assertEqual(c.inspect(owner, cut), ('cancelled', None))

    def test_cut_capacity_and_cancelled_serials(self):
        m, owner, sources, adapter, c = self.fixture()
        cuts = []
        for serial in range(1, 7):
            cut = c.reserve(owner, (sources[0],))
            cuts.append(cut)
            self.assertEqual(cut.serial, serial)
            c.cancel(owner, cut)
            with self.assertRaisesRegex(m.CutError, 'not reserved'):
                c.apply(owner, cut)
        with self.assertRaisesRegex(m.CutError, 'full'):
            c.reserve(owner, (sources[0],))
        self.assertEqual((len(c.records), c.next_serial, adapter.calls, adapter.phases), (6, 7, 0, (0, 0)))
        self.assertTrue(all(c.inspect(owner, cut) == ('cancelled', None) for cut in cuts))
        m, owner, sources, adapter, c = self.fixture()
        c.next_serial = m.MAX_SERIAL  # Synthetic exhaustion boundary, not normal reuse.
        cut = c.reserve(owner, (sources[0],))
        c.cancel(owner, cut)
        with self.assertRaisesRegex(m.CutError, 'full'):
            c.reserve(owner, (sources[0],))
        self.assertEqual(cut.serial, m.MAX_SERIAL)
        self.assertEqual(adapter.reservations, 1)

    def test_cut_unknown_never_reapplies(self):
        for mode in ('before-failure', 'after-failure', 'no-op', 'wrong-cut'):
            with self.subTest(mode=mode):
                m, owner, sources, adapter, c = self.fixture()
                adapter.mode = mode
                cut = c.reserve(owner, (sources[0], sources[3]))
                with self.assertRaises(m.CutError):
                    c.apply(owner, cut)
                self.assertEqual(c.inspect(owner, cut), ('unknown', None), 'uncaptured cut accepted')
                self.assertTrue(c.closed)
                with self.assertRaisesRegex(m.CutError, 'closed'):
                    c.apply(owner, cut)
                self.assertEqual(adapter.calls, 1)
                self.assertEqual(adapter.phases, (0, 0) if mode in ('before-failure', 'no-op') else (1, 1))
                self.assertIs(c.active.cut, cut)
                self.assertEqual(c.active.returned is None, mode in ('before-failure', 'after-failure'))

    def test_cut_applied_receipt_survives_lost_delivery(self):
        m, owner, sources, adapter, c = self.fixture()
        cut = c.reserve(owner, (sources[0],))
        c.apply(owner, cut)  # Caller deliberately discards the returned receipt.
        state, receipt = c.inspect(owner, cut)
        self.assertEqual(state, 'applied')
        self.assertIs(c.apply(owner, cut), receipt)
        c.closed = True  # Later local closure; inspection adds no authority.
        self.assertEqual(c.inspect(owner, cut), ('applied', receipt))
        with self.assertRaisesRegex(m.CutError, 'closed'):
            c.apply(owner, cut)
        self.assertEqual(adapter.calls, 1)

    def test_cut_adapter_reentry_is_denied(self):
        m, owner, sources, adapter, c = self.fixture()
        reserve = adapter.reserve
        def guarded_reserve(credits):
            with self.assertRaisesRegex(m.CutError, 'reentry'):
                c.reserve(owner, (sources[3],))
            return reserve(credits)
        with patch.object(adapter, 'reserve', guarded_reserve):
            cut = c.reserve(owner, (sources[0],))
        apply = adapter.apply
        def guarded_apply(ticket, supplied):
            with self.assertRaisesRegex(m.CutError, 'reentry'):
                c.apply(owner, supplied)
            return apply(ticket, supplied)
        with patch.object(adapter, 'apply', guarded_apply):
            c.apply(owner, cut)
        cut = c.reserve(owner, (sources[1],))
        cancel = adapter.cancel
        def guarded_cancel(ticket):
            with self.assertRaisesRegex(m.CutError, 'reentry'):
                c.cancel(owner, cut)
            return cancel(ticket)
        with patch.object(adapter, 'cancel', guarded_cancel):
            c.cancel(owner, cut)
        self.assertEqual((adapter.calls, len(c.records), c.running), (1, 2, False))

    def test_cut_synthetic_source_validation(self):
        from dataclasses import replace
        m, owner, sources, adapter, c = self.fixture()
        for invalid in (replace(sources[0], attempt=True), replace(sources[0], content=(object(),)),
                        replace(sources[0], token=(1,)), replace(sources[0], worker=0)):
            with self.assertRaises(m.CutError):
                m.CutCoordinator(owner, (invalid,), adapter)
        adapter.phases = (False, False)
        with self.assertRaisesRegex(m.CutError, 'nonempty adapter'):
            m.CutCoordinator(owner, sources, adapter)
        adapter.phases = (0, 0)
        with self.assertRaisesRegex(m.CutError, 'inconsistent binding'):
            m.CutCoordinator(owner, (sources[0], replace(sources[1], worker=4)), adapter)

    def test_cut_omission_controls(self):
        import types
        path = Path(__file__).resolve().parents[1] / 'prototypes/runtime_model/cut_coordinator.py'
        text = path.read_text()
        controls = [
            ('identity', 'if cut is record.cut:', 'if cut.serial == record.cut.serial:', 'identity admitted'),
            ('capture', "raise CutError('application not captured')", 'pass', 'uncaptured accepted'),
            ('ordering', 'if not _state(self.adapter.phases) or any(self.adapter.phases[s.attempt] != s.phase - 1 for s in members):', 'if False:', 'unordered phase applied'),
            ('replay', "return record.receipt\n        if record is not self.active", "return self.adapter.apply(self.adapter.reserve(20), cut)\n        if record is not self.active", 'replay invoked'),
        ]
        for name, old, new, oracle in controls:
            self.assertEqual(text.count(old), 1)
            module = types.ModuleType('_cut_control_' + name)
            sys.modules[module.__name__] = module
            try:
                exec(compile(text.replace(old, new), str(path), 'exec'), module.__dict__)
                m, owner, sources, adapter, c = self.fixture(module)
                cut = c.reserve(owner, (sources[1 if name == 'ordering' else 0],))
                with self.assertRaisesRegex(AssertionError, oracle):
                    if name == 'identity':
                        denied = False
                        try:
                            c.apply(owner, m.Cut(cut.serial, cut.members))
                        except m.CutError:
                            denied = True
                        self.assertTrue(denied, oracle)
                    elif name == 'ordering':
                        c.apply(owner, cut)
                        self.assertEqual(adapter.phases, (0, 0), oracle)
                    elif name == 'capture':
                        adapter.mode = 'no-op'
                        try:
                            c.apply(owner, cut)
                        except m.CutError:
                            pass
                        self.assertEqual(c.inspect(owner, cut)[0], 'unknown', oracle)
                    else:
                        c.apply(owner, cut)
                        c.apply(owner, cut)
                        self.assertEqual(adapter.calls, 1, oracle)
            finally:
                del sys.modules[module.__name__]



class CutRetirementTests(unittest.TestCase):
    @staticmethod
    def fixture(module=None, phase=3):
        if module is None:
            from prototypes.runtime_model import cut_retirement as module
        m, owner, sources, application, core = CutCoordinatorTests.fixture()
        class ResourcesAdapter:
            calls = 0
            seen = 0
            mode = None
            bad = None
            marked = [False, False]
            pending = None
            release_calls = 0
            release_mode = None

            def pending_source(self):
                return self.pending

            def release(self, source, receipt):
                self.release_calls += 1
                if self.release_mode != 'no-op':
                    self.pending = None
                if self.release_mode == 'lost':
                    raise m.CutError('release lost')
                return None if self.release_mode == 'wrong' else receipt

            def inspect(self, source):
                self.seen += 1
                if self.bad is not None and source.attempt == 1:
                    return self.bad(source)
                return module.Resources(source, (False,) * 4, True, False)

            def mark(self, source, receipt):
                self.calls += 1
                if self.mode == 'before' and source.attempt == 0:
                    raise m.CutError('mark failed')
                self.marked[source.attempt] = True
                if self.mode == 'after' and source.attempt == 1:
                    raise m.CutError('mark failed')
                if self.mode == 'wrong':
                    return None
                return receipt

        adapter = ResourcesAdapter()
        retirement = module.Retirement(core, adapter)
        receipts = []
        for p in range(phase):
            cut = core.reserve(owner, (sources[p], sources[p + 3]))
            receipts.append(core.apply(owner, cut))
            if p == 1:
                # Sequential synthetic positions, not two native pending samples.
                for source in cut.members:
                    adapter.pending = source
                    retirement.release_pending(owner, receipts[-1], source)
        return module, m, owner, sources, application, core, adapter, retirement, receipts

    def test_retirement_whole_cut_and_replay(self):
        r, m, owner, sources, app, core, adapter, retirement, receipts = self.fixture()
        records = tuple(core.records)
        self.assertEqual(retirement.retire(owner, receipts[-1]), 'retired')
        self.assertEqual(retirement.retire(owner, receipts[-1]), 'already-retired')
        self.assertEqual((adapter.calls, adapter.seen, adapter.marked), (2, 2, [True, True]))
        self.assertIs(core.sources, sources, 'history was reset')
        self.assertEqual(tuple(core.records), records)
        self.assertEqual((core.next_serial, app.calls), (4, 3))
        for receipt in receipts:
            self.assertEqual(core.inspect(owner, receipt.cut), ('applied', receipt))
        self.assertEqual(retirement.dispositions, [('retired', receipts[-1])] * 2)

    def test_retirement_receipt_and_phase_denial(self):
        r, m, owner, sources, app, core, adapter, retirement, receipts = self.fixture(phase=2)
        with self.assertRaisesRegex(m.CutError, 'cleaned cut required'):
            retirement.retire(owner, receipts[-1])
        self.assertEqual((adapter.calls, adapter.seen), (0, 0))
        reserved = core.reserve(owner, (sources[2], sources[5]))
        unconfirmed = m.Receipt(reserved, 3, (2, 2), (3, 3))
        with self.assertRaisesRegex(m.CutError, 'busy'):
            retirement.retire(owner, unconfirmed)
        self.assertEqual(core.inspect(owner, reserved), ('reserved', None))
        self.assertEqual((adapter.calls, adapter.seen, retirement.dispositions), (0, 0, [None, None]))
        r, m, owner, sources, app, core, adapter, retirement, receipts = self.fixture()
        receipt = receipts[-1]
        for bad in (m.Receipt(receipt.cut, receipt.journal_serial, receipt.before, receipt.after),
                    m.Receipt(m.Cut(receipt.cut.serial, receipt.cut.members), 3, (2, 2), (3, 3))):
            with self.assertRaises(m.CutError):
                retirement.retire(owner, bad)
        with self.assertRaisesRegex(m.CutError, 'owner'):
            retirement.retire(object(), receipt)
        with self.assertRaisesRegex(m.CutError, 'cleaned cut required'):
            retirement.retire(owner, receipts[0])
        self.assertEqual((adapter.calls, retirement.dispositions), (0, [None, None]))

    def test_retirement_inventory_denies_whole_cut(self):
        for index in range(6):
            r, m, owner, sources, app, core, adapter, retirement, receipts = self.fixture()
            def bad(source):
                live = tuple(i == index for i in range(4))
                return r.Resources(source, live, index != 4, index == 5)
            adapter.bad = bad
            with self.assertRaisesRegex(m.CutError, 'resources unresolved'):
                retirement.retire(owner, receipts[-1])
            self.assertEqual((adapter.calls, adapter.marked), (0, [False, False]), 'nonempty inventory retired')
            self.assertEqual(retirement.observations, [None, None])
            self.assertFalse(core.closed)
            self.assertIs(core.sources, sources)

    def test_retirement_stale_or_malformed_disposition(self):
        from dataclasses import replace
        for mode in ('foreign-source', 'numeric-boolean'):
            r, m, owner, sources, app, core, adapter, retirement, receipts = self.fixture()
            adapter.bad = lambda source: r.Resources(
                replace(source, worker=source.worker + 1) if mode == 'foreign-source' else source,
                (0, False, False, False) if mode == 'numeric-boolean' else (False,) * 4, True, False)
            with self.assertRaisesRegex(m.CutError, 'disposition identity'):
                retirement.retire(owner, receipts[-1])
            self.assertEqual(adapter.calls, 0)

    def test_retirement_partial_failure_retains_progress(self):
        for mode in ('before', 'after', 'wrong'):
            r, m, owner, sources, app, core, adapter, retirement, receipts = self.fixture()
            adapter.mode = mode
            with self.assertRaises(m.CutError):
                retirement.retire(owner, receipts[-1])
            self.assertTrue(core.closed)
            self.assertEqual(retirement.dispositions[0][0], 'retired' if mode == 'after' else 'started')
            self.assertEqual(retirement.dispositions[1], ('started', receipts[-1]) if mode == 'after' else None)
            self.assertTrue(all(s is not None for s in retirement.observations))
            self.assertEqual(adapter.marked, [False, False] if mode == 'before' else [True, mode == 'after'])
            calls = adapter.calls
            with self.assertRaisesRegex(m.CutError, 'closed'):
                retirement.retire(owner, receipts[-1])
            self.assertEqual(adapter.calls, calls)
            self.assertIs(core.sources, sources)
            self.assertEqual(core.inspect(owner, receipts[-1].cut), ('applied', receipts[-1]))
            self.assertEqual(app.calls, 3)
            self.assertEqual(retirement.returned[0], (None,) if mode == 'wrong' else
                             (receipts[-1],) if mode == 'after' else None)

    def test_retirement_single_owner(self):
        r, m, owner, sources, app, core, adapter, retirement, receipts = self.fixture()
        with self.assertRaisesRegex(m.CutError, 'retirement owner unavailable'):
            r.Retirement(core, adapter)
        self.assertIs(core.retirement, retirement)
        self.assertEqual(adapter.calls, 0)

    def test_retirement_callback_reentry_denied(self):
        r, m, owner, sources, app, core, adapter, retirement, receipts = self.fixture()
        for name in ('inspect', 'mark'):
            original = getattr(adapter, name)
            def wrapped(*args):
                with self.assertRaisesRegex(m.CutError, 'reentry'):
                    retirement.retire(owner, receipts[-1])
                return original(*args)
            with patch.object(adapter, name, wrapped):
                # Start a fresh owner for each callback boundary below.
                retirement.retire(owner, receipts[-1])
            r, m, owner, sources, app, core, adapter, retirement, receipts = self.fixture()

    def test_retirement_omission_controls(self):
        import types
        path = Path(__file__).resolve().parents[1] / 'prototypes/runtime_model/cut_retirement.py'
        text = path.read_text()
        controls = [
            ('early', 'members = tuple(s for s in self._applied(owner, receipt) if s.phase == 3)', 'members = self._applied(owner, receipt)', 'premature retirement'),
            ('inventory', 'if any(state.live) or not state.reclaim_applied or state.unresolved:', 'if False:', 'nonempty inventory retired'),
            ('reset', "self.dispositions[index] = ('retired', receipt)", "self.dispositions[index] = ('retired', receipt)\n                self.core.sources = ()", 'history was reset'),
        ]
        for name, old, new, message in controls:
            self.assertEqual(text.count(old), 1)
            module = types.ModuleType('prototypes.runtime_model._retirement_control_' + name)
            module.__package__ = 'prototypes.runtime_model'
            sys.modules[module.__name__] = module
            try:
                exec(compile(text.replace(old, new), str(path), 'exec'), module.__dict__)
                r, m, owner, sources, app, core, adapter, retirement, receipts = self.fixture(module, 2 if name == 'early' else 3)
                if name == 'inventory':
                    adapter.bad = lambda source: r.Resources(source, (True, False, False, False), True, False)
                retirement.retire(owner, receipts[-1])
                with self.assertRaisesRegex(AssertionError, message):
                    if name == 'reset':
                        self.assertIs(core.sources, sources, message)
                    else:
                        self.assertEqual(adapter.calls, 0, message)
            finally:
                del sys.modules[module.__name__]



class CutPendingTests(unittest.TestCase):
    @staticmethod
    def terminal_fixture(module=None):
        values = CutRetirementTests.fixture(module, phase=1)
        r, m, owner, sources, app, core, adapter, retirement, receipts = values
        cut = core.reserve(owner, (sources[1],))
        receipt = core.apply(owner, cut)
        adapter.pending = sources[1]
        return values, receipt

    def test_pending_exact_release_and_replay(self):
        values, receipt = self.terminal_fixture()
        r, m, owner, sources, app, core, adapter, retirement, receipts = values
        self.assertEqual(retirement.release_pending(owner, receipt, sources[1]), 'released')
        adapter.pending = sources[4]  # Another synthetic position must survive old replay.
        self.assertEqual(retirement.release_pending(owner, receipt, sources[1]), 'already-released')
        self.assertIs(adapter.pending, sources[4])
        self.assertEqual(adapter.release_calls, 1)
        self.assertIs(core.sources, sources)
        self.assertEqual(core.inspect(owner, receipt.cut), ('applied', receipt))
        self.assertEqual((app.calls, core.next_serial), (2, 3))

    def test_pending_wrong_member_and_identity(self):
        values, receipt = self.terminal_fixture()
        r, m, owner, sources, app, core, adapter, retirement, receipts = values
        with self.assertRaisesRegex(m.CutError, 'terminal member required'):
            retirement.release_pending(owner, receipt, sources[4])
        adapter.pending = sources[4]
        with self.assertRaisesRegex(m.CutError, 'pending identity'):
            retirement.release_pending(owner, receipt, sources[1])
        self.assertEqual((adapter.release_calls, retirement.releases), (0, [None, None]))

    def test_pending_unconfirmed_results_close(self):
        for mode in ('no-op', 'wrong', 'lost'):
            values, receipt = self.terminal_fixture()
            r, m, owner, sources, app, core, adapter, retirement, receipts = values
            adapter.release_mode = mode
            with self.assertRaises(m.CutError):
                retirement.release_pending(owner, receipt, sources[1])
            self.assertTrue(core.closed)
            self.assertEqual(retirement.releases[0], ('started', receipt))
            self.assertIs(retirement.release_observations[0], sources[1])
            self.assertEqual(retirement.release_returns[0], None if mode == 'lost' else
                             (None,) if mode == 'wrong' else (receipt,))
            self.assertIs(adapter.pending, sources[1] if mode == 'no-op' else None)
            with self.assertRaisesRegex(m.CutError, 'closed'):
                retirement.release_pending(owner, receipt, sources[1])
            self.assertEqual(adapter.release_calls, 1)
            self.assertEqual(core.inspect(owner, receipt.cut), ('applied', receipt))

    def test_pending_required_before_retirement(self):
        values, receipt = self.terminal_fixture()
        r, m, owner, sources, app, core, adapter, retirement, receipts = values
        cleaned = core.apply(owner, core.reserve(owner, (sources[2],)))
        with self.assertRaisesRegex(m.CutError, 'pending release required'):
            retirement.retire(owner, cleaned)
        self.assertEqual(adapter.calls, 0)
        self.assertIs(adapter.pending, sources[1])

    def test_pending_callback_reentry_denied(self):
        values, receipt = self.terminal_fixture()
        r, m, owner, sources, app, core, adapter, retirement, receipts = values
        original = adapter.release
        def release(source, accepted):
            with self.assertRaisesRegex(m.CutError, 'reentry'):
                retirement.release_pending(owner, accepted, source)
            return original(source, accepted)
        with patch.object(adapter, 'release', release):
            retirement.release_pending(owner, receipt, sources[1])
        self.assertEqual(adapter.release_calls, 1)
        self.assertFalse(core.running)

    def test_mixed_cut_retires_only_cleaned_member(self):
        for other_phase in (1, 2):
            r, m, owner, sources, app, core, adapter, retirement, receipts = CutRetirementTests.fixture(phase=0)
            launched = (sources[0],) if other_phase == 1 else (sources[0], sources[3])
            core.apply(owner, core.reserve(owner, launched))
            terminal = core.apply(owner, core.reserve(owner, (sources[1],)))
            adapter.pending = sources[1]
            retirement.release_pending(owner, terminal, sources[1])
            mixed = core.apply(owner, core.reserve(owner, (sources[2], sources[2 + other_phase])))
            adapter.pending = sources[4] if other_phase == 2 else None
            self.assertEqual(retirement.retire(owner, mixed), 'retired')
            self.assertEqual(retirement.dispositions, [('retired', mixed), None])
            self.assertEqual((adapter.calls, adapter.seen, adapter.marked), (1, 1, [True, False]))
            self.assertIs(adapter.pending, sources[4] if other_phase == 2 else None)
            self.assertIs(core.sources, sources)
            self.assertEqual(retirement.retire(owner, mixed), 'already-retired')
            self.assertEqual(core.inspect(owner, mixed.cut), ('applied', mixed))
            if other_phase == 2:
                retirement.release_pending(owner, mixed, sources[4])
                self.assertIsNone(adapter.pending)
                self.assertEqual(retirement.dispositions[1], None)

    def test_mixed_cut_mark_failure_preserves_other_member(self):
        values, terminal = self.terminal_fixture()
        r, m, owner, sources, app, core, adapter, retirement, receipts = values
        retirement.release_pending(owner, terminal, sources[1])
        mixed = core.apply(owner, core.reserve(owner, (sources[2], sources[4])))
        adapter.pending = sources[4]
        adapter.mode = 'wrong'
        with self.assertRaisesRegex(m.CutError, 'retirement not confirmed'):
            retirement.retire(owner, mixed)
        self.assertTrue(core.closed)
        self.assertEqual(retirement.dispositions, [('started', mixed), None])
        self.assertIs(adapter.pending, sources[4])
        self.assertEqual(adapter.marked, [True, False])
        self.assertEqual(core.inspect(owner, mixed.cut), ('applied', mixed))

    def test_pending_omission_controls(self):
        import types
        path = Path(__file__).resolve().parents[1] / 'prototypes/runtime_model/cut_retirement.py'
        text = path.read_text()
        controls = [
            ('member', 'if pending is not source:', 'if False:', 'wrong pending released'),
            ('confirmation', 'if result is not receipt or self.core._invoke(self.adapter.pending_source) is not None:', 'if False:', 'unconfirmed pending release'),
        ]
        for name, old, new, message in controls:
            self.assertEqual(text.count(old), 1)
            module = types.ModuleType('prototypes.runtime_model._pending_control_' + name)
            module.__package__ = 'prototypes.runtime_model'
            sys.modules[module.__name__] = module
            try:
                exec(compile(text.replace(old, new), str(path), 'exec'), module.__dict__)
                values, receipt = self.terminal_fixture(module)
                r, m, owner, sources, app, core, adapter, retirement, receipts = values
                if name == 'member':
                    adapter.pending = sources[4]
                else:
                    adapter.release_mode = 'no-op'
                retirement.release_pending(owner, receipt, sources[1])
                with self.assertRaisesRegex(AssertionError, message):
                    if name == 'member':
                        self.assertEqual(adapter.release_calls, 0, message)
                    else:
                        self.assertTrue(core.closed, message)
            finally:
                del sys.modules[module.__name__]



class LaunchedAdapterTests(unittest.TestCase):
    @staticmethod
    def fixture(module=None):
        if module is None:
            from prototypes.runtime_model import launched_adapter as module
        from prototypes.runtime_model import cut_coordinator as c
        runtime = JournalRuntime([Service('a'), Service('b', requires=(('a', 'started'),))])
        runtime.start(['b'])
        token, = runtime.issue_obligations()
        runtime.acknowledge(token, 'executed')  # Logical outcome only, not native launch.
        owner = object()
        source = c.Source(owner, 0, (1, 2, 3, token[3], token[4], 4, token[6], 6, 7, token[9]),
                          0xb0000101, 1, (0,))
        adapter = module.LaunchedAdapter(runtime, owner, ((source, token),))
        core = c.CutCoordinator(owner, (source,), adapter)
        return c, runtime, owner, source, adapter, core

    def test_launched_real_cut_captures_dependency_effect(self):
        c, runtime, owner, source, adapter, core = self.fixture()
        cut = core.reserve(owner, (source,))
        receipt = core.apply(owner, cut)
        self.assertEqual((cut.serial, receipt.journal_serial), (1, 2))
        self.assertEqual((receipt.before, receipt.after), ((0, 0), (1, 0)))
        token, = runtime.pending
        self.assertEqual(token, ('event-effect-v1', 'boot-1', 'config-1', 2, 0, 'b', 1, 'launch', 'activation', 1))
        self.assertEqual(runtime.journal.observe(token), 'reserved')
        self.assertTrue(runtime.model.state['b'].launch_pending)
        before = JournalRuntimeTests.snapshot(runtime)
        self.assertIs(core.apply(owner, cut), receipt)
        self.assertEqual(JournalRuntimeTests.snapshot(runtime), before)

    def test_launched_empty_effect_capture_is_still_bound(self):
        from prototypes.runtime_model.launched_adapter import LaunchedAdapter
        from prototypes.runtime_model.cut_coordinator import Source, CutCoordinator
        runtime = JournalRuntime([Service('a')])
        runtime.start(['a'])
        token, = JournalRuntimeTests.settle(runtime)
        owner = object()
        source = Source(owner, 0, (1, 2, 3, token[3], token[4], 4, token[6], 6, 7, token[9]),
                        0xb0000101, 1, (0,))
        adapter = LaunchedAdapter(runtime, owner, ((source, token),))
        core = CutCoordinator(owner, (source,), adapter)
        receipt = core.apply(owner, core.reserve(owner, (source,)))
        self.assertEqual(receipt.journal_serial, 2)
        self.assertEqual((runtime.pending, runtime.journal.raw, runtime.journal.live), ((), (), {}))
        self.assertTrue(runtime.model.state['a'].started)
        self.assertIsNone(runtime.journal.ticket)

    def test_launched_prepared_blocks_commands_and_cancel_consumes_serial(self):
        c, runtime, owner, source, adapter, core = self.fixture()
        cut = core.reserve(owner, (source,))
        before = JournalRuntimeTests.snapshot(runtime)
        with self.assertRaises(InvalidEffect):
            runtime.stop(['a'])
        self.assertEqual(JournalRuntimeTests.snapshot(runtime), before)
        core.cancel(owner, cut)
        self.assertIsNone(runtime.prepared)
        self.assertEqual(runtime.journal.next_cut, 3)
        receipt = core.apply(owner, core.reserve(owner, (source,)))
        self.assertEqual(receipt.journal_serial, 3)

    def test_launched_queued_runtime_cannot_reserve_application(self):
        runtime = QueuedRuntime([Service('a')])
        before = JournalRuntimeTests.snapshot(runtime)
        with self.assertRaisesRegex(InvalidEffect, 'reserved batch runtime profile'):
            runtime.reserve_batch()
        self.assertEqual(JournalRuntimeTests.snapshot(runtime), before)
        self.assertIsNone(runtime.prepared)
        self.assertEqual(list(runtime.inbox), [])

    def test_launched_journal_busy_denies_without_model_change(self):
        c, runtime, owner, source, adapter, core = self.fixture()
        external = runtime.journal.reserve()
        before = JournalRuntimeTests.snapshot(runtime)
        with self.assertRaises(InvalidEffect):
            core.reserve(owner, (source,))
        self.assertEqual(JournalRuntimeTests.snapshot(runtime), before)
        self.assertEqual((core.records, core.next_serial), ([], 1))
        runtime.journal.cancel(external)

    def test_launched_revalidates_real_launch_state(self):
        c, runtime, owner, source, adapter, core = self.fixture()
        cut = core.reserve(owner, (source,))
        runtime.model.state['a'].generation = 2  # Deliberate trusted-state corruption.
        with self.assertRaisesRegex(c.CutError, 'launch state'):
            core.apply(owner, cut)
        self.assertTrue(runtime.failed and core.closed)
        self.assertEqual(core.inspect(owner, cut), ('unknown', None))
        self.assertFalse(runtime.model.state['a'].started)

    def test_launched_rejects_changed_full_token(self):
        from dataclasses import replace
        from prototypes.runtime_model.launched_adapter import LaunchedAdapter
        c, runtime, owner, source, adapter, core = self.fixture()
        token = adapter.bindings[0][1]
        for index in range(10):
            scalars = list(source.token)
            scalars[index] += 1
            with self.assertRaises(c.CutError):
                LaunchedAdapter(runtime, owner, ((replace(source, token=tuple(scalars)), token),))

    def test_launched_transition_and_capture_fail_closed(self):
        for mode in ('transition', 'capture'):
            c, runtime, owner, source, adapter, core = self.fixture()
            cut = core.reserve(owner, (source,))
            if mode == 'transition':
                original = runtime.model.batch
                patched = patch.object(runtime.model, 'batch', lambda events, now: original((), now=now))
            else:
                original = runtime.journal.capture
                def lose(ticket, records):
                    tokens = original(ticket, records)
                    runtime.journal.live.clear()
                    return tokens
                patched = patch.object(runtime.journal, 'capture', lose)
            with patched, self.assertRaises(c.CutError):
                core.apply(owner, cut)
            self.assertTrue(core.closed and runtime.failed)
            self.assertEqual(core.inspect(owner, cut), ('unknown', None))
            self.assertEqual(runtime.model.state['a'].started, mode == 'capture')
            self.assertIsNotNone(adapter.captured)

    def test_launched_adapter_omission_controls(self):
        import types
        path = Path(__file__).resolve().parents[1] / 'prototypes/runtime_model/launched_adapter.py'
        text = path.read_text()
        for name, anchor in [('transition', "raise CutError('launch transition missing')"),
                             ('capture', "raise CutError('journal capture missing')")]:
            self.assertEqual(text.count(anchor), 1)
            module = types.ModuleType('prototypes.runtime_model._launched_' + name)
            module.__package__ = 'prototypes.runtime_model'
            sys.modules[module.__name__] = module
            try:
                exec(compile(text.replace(anchor, 'pass'), str(path), 'exec'), module.__dict__)
                c, runtime, owner, source, adapter, core = self.fixture(module)
                cut = core.reserve(owner, (source,))
                if name == 'transition':
                    original = runtime.model.batch
                    patched = patch.object(runtime.model, 'batch', lambda events, now: original((), now=now))
                else:
                    original = runtime.journal.capture
                    def lose(ticket, records):
                        tokens = original(ticket, records)
                        runtime.journal.live.clear()
                        return tokens
                    patched = patch.object(runtime.journal, 'capture', lose)
                denied = False
                with patched:
                    try:
                        adapter.apply(adapter.ticket, cut)  # Test the adapter boundary independently.
                    except c.CutError:
                        denied = True
                with self.assertRaisesRegex(AssertionError, name + ' omission accepted'):
                    self.assertTrue(denied, name + ' omission accepted')
            finally:
                del sys.modules[module.__name__]



class TerminalAdapterTests(unittest.TestCase):
    @staticmethod
    def fixture(kind=1, result=18, module=None, dependent=False):
        from prototypes.runtime_model import cut_coordinator as c
        if module is None:
            from prototypes.runtime_model import terminal_adapter as module
        services = [Service('a')]
        if dependent:
            services.append(Service('b', requires=(('a', 'started'),)))
        runtime = JournalRuntime(services)
        runtime.start(['b' if dependent else 'a'])
        token, = JournalRuntimeTests.settle(runtime)
        owner = object()
        encoded = (1, 2, 3, token[3], token[4], 4, token[6], 6, 7, token[9])
        launch = c.Source(owner, 0, encoded, 0xb0000101, 1, (0,))
        terminal = c.Source(owner, 0, encoded, 0xb0000101, 2, (1, result, kind, 1))
        adapter = module.TerminalAdapter(runtime, owner, ((launch, token),), ((terminal, token),))
        core = c.CutCoordinator(owner, (launch, terminal), adapter)
        return c, runtime, owner, launch, terminal, adapter, core

    def test_terminal_kind_collisions_and_reclaim(self):
        for kind, result, label, detail in [(1, 1, 'exit-0', 0), (1, 18, 'exit', 17),
                                           (1, 135, 'exit', 134), (2, 135, 'fault', None),
                                           (1, 144, 'exit', 143), (3, 144, 'stopped', 143)]:
            c, runtime, owner, launch, terminal, adapter, core = self.fixture(kind, result)
            core.apply(owner, core.reserve(owner, (launch,)))
            cut = core.reserve(owner, (terminal,))
            receipt = core.apply(owner, cut)
            state = runtime.model.state['a']
            self.assertEqual((state.terminal, state.terminal_detail), (label, detail))
            token, = runtime.pending
            self.assertEqual(token, ('event-effect-v1', 'boot-1', 'config-1', 3, 0, 'a', 1, 'reclaim', 'activation', 1))
            self.assertEqual(runtime.journal.observe(token), 'reserved')
            self.assertEqual((receipt.before, receipt.after, receipt.journal_serial), ((1, 0), (2, 0), 3))
            self.assertTrue(state.owned and state.reclaim_sent)
            self.assertEqual(state.cleanup, 'pending')
            before = JournalRuntimeTests.snapshot(runtime)
            self.assertIs(core.apply(owner, cut), receipt)
            self.assertEqual(JournalRuntimeTests.snapshot(runtime), before)
            self.assertEqual(terminal.content, (1, result, kind, 1))

    def test_terminal_before_launch_and_busy_journal(self):
        c, runtime, owner, launch, terminal, adapter, core = self.fixture(dependent=True)
        with self.assertRaisesRegex(c.CutError, 'phase'):
            core.reserve(owner, (terminal,))
        core.apply(owner, core.reserve(owner, (launch,)))
        before = JournalRuntimeTests.snapshot(runtime)
        with self.assertRaises(InvalidEffect):
            core.reserve(owner, (terminal,))
        self.assertEqual(JournalRuntimeTests.snapshot(runtime), before)
        JournalRuntimeTests.settle(runtime)
        receipt = core.apply(owner, core.reserve(owner, (terminal,)))
        self.assertEqual(receipt.after, (2, 0))

    def test_terminal_fact_bounds_and_pairs(self):
        from prototypes.runtime_model.terminal_adapter import TerminalAdapter
        for content in [(0, 18, 1, 1), (1, 135, 3, 1), (1, 144, 2, 0),
                        (1, 18, 1, 2), (True, 18, 1, 1), (1, 257, 1, 0),
                        (1, 18, 1), (1 << 64, 18, 1, 1)]:
            with self.assertRaisesRegex(ValueError, 'terminal fact'):
                TerminalAdapter._fact(content)
        self.assertEqual(TerminalAdapter._fact(((1 << 64) - 1, 256, 1, 0)), (256, 1))

    def test_terminal_stale_generation_closes_before_transition(self):
        c, runtime, owner, launch, terminal, adapter, core = self.fixture()
        core.apply(owner, core.reserve(owner, (launch,)))
        cut = core.reserve(owner, (terminal,))
        runtime.model.state['a'].generation = 2
        with self.assertRaisesRegex(c.CutError, 'terminal state'):
            core.apply(owner, cut)
        self.assertTrue(core.closed and runtime.failed)
        self.assertEqual(runtime.model.state['a'].phase, 'running')
        self.assertEqual(core.inspect(owner, cut), ('unknown', None))

    def test_terminal_wrong_kind_after_apply_is_retained_unknown(self):
        c, runtime, owner, launch, terminal, adapter, core = self.fixture(2, 135)
        core.apply(owner, core.reserve(owner, (launch,)))
        cut = core.reserve(owner, (terminal,))
        original = runtime.model.batch
        def wrong(events, now):
            return original([('exit', *event[1:]) for event in events], now=now)
        with patch.object(runtime.model, 'batch', wrong), self.assertRaisesRegex(c.CutError, 'terminal kind missing'):
            core.apply(owner, cut)
        self.assertTrue(core.closed and runtime.failed)
        self.assertEqual(core.inspect(owner, cut), ('unknown', None))
        self.assertEqual(runtime.model.state['a'].terminal, 'exit')
        self.assertEqual(len(adapter.captured), 1)
        self.assertTrue(runtime.model.state['a'].owned)

    def test_terminal_missing_reclaim_closes(self):
        c, runtime, owner, launch, terminal, adapter, core = self.fixture()
        core.apply(owner, core.reserve(owner, (launch,)))
        cut = core.reserve(owner, (terminal,))
        original = runtime.model._effect
        def omit(action, name):
            if action != 'reclaim':
                return original(action, name)
        with patch.object(runtime.model, '_effect', omit), self.assertRaisesRegex(c.CutError, 'reclaim obligation missing'):
            core.apply(owner, cut)
        self.assertTrue(core.closed and runtime.failed)
        self.assertEqual(runtime.model.state['a'].phase, 'terminal')
        self.assertTrue(runtime.model.state['a'].owned)
        self.assertEqual(adapter.captured, ())
        self.assertEqual(core.inspect(owner, cut), ('unknown', None))

    def test_terminal_binding_cannot_change_worker(self):
        from dataclasses import replace
        from prototypes.runtime_model.terminal_adapter import TerminalAdapter
        c, runtime, owner, launch, terminal, adapter, core = self.fixture()
        token = adapter.bindings[0][1]
        with self.assertRaisesRegex(c.CutError, 'terminal binding'):
            TerminalAdapter(runtime, owner, ((launch, token),), ((replace(terminal, worker=44), token),))

    def test_terminal_omission_controls(self):
        import types
        path = Path(__file__).resolve().parents[1] / 'prototypes/runtime_model/terminal_adapter.py'
        text = path.read_text()
        controls = [
            ('collision', "event_kind = {1: 'exit', 2: 'fault', 3: 'stopped'}[kind]",
             "event_kind = 'fault' if result == 135 else {1: 'exit', 2: 'fault', 3: 'stopped'}[kind]"),
            ('verification', "raise CutError('terminal kind missing')", 'pass'),
        ]
        for name, old, new in controls:
            self.assertEqual(text.count(old), 1)
            module = types.ModuleType('prototypes.runtime_model._terminal_' + name)
            module.__package__ = 'prototypes.runtime_model'
            sys.modules[module.__name__] = module
            try:
                exec(compile(text.replace(old, new), str(path), 'exec'), module.__dict__)
                c, runtime, owner, launch, terminal, adapter, core = self.fixture(1 if name == 'collision' else 2, 135, module)
                core.apply(owner, core.reserve(owner, (launch,)))
                cut = core.reserve(owner, (terminal,))
                if name == 'collision':
                    core.apply(owner, cut)
                    with self.assertRaisesRegex(AssertionError, 'terminal kind collapsed'):
                        self.assertEqual(runtime.model.state['a'].terminal, 'exit', 'terminal kind collapsed')
                else:
                    original = runtime.model.batch
                    def wrong(events, now):
                        return original([('exit', *event[1:]) for event in events], now=now)
                    with patch.object(runtime.model, 'batch', wrong):
                        core.apply(owner, cut)
                    with self.assertRaisesRegex(AssertionError, 'terminal verification omitted'):
                        self.assertTrue(core.closed, 'terminal verification omitted')
            finally:
                del sys.modules[module.__name__]


class CleanedAdapterTests(unittest.TestCase):
    @staticmethod
    def fixture(module=None, count=1, retries=0):
        from prototypes.runtime_model import cut_coordinator as c
        from prototypes.runtime_model.cut_retirement import Resources
        if module is None:
            from prototypes.runtime_model import cleaned_adapter as module
        names = ('a', 'b')[:count]
        runtime = JournalRuntime([Service(n, retries=retries) for n in names])
        runtime.start(list(names))
        tokens = JournalRuntimeTests.settle(runtime)
        owner = object()
        phases = []
        for phase in (1, 2, 3):
            phases.append(tuple(c.Source(owner, i,
                (1, 2, 3, t[3], t[4], i + 4, t[6], 6, 7, t[9]),
                0xb0000101 + i, phase, (1, 18, 1, 1) if phase == 2 else (0,))
                for i, t in enumerate(tokens)))
        launch, terminal, cleaned = phases
        states = {s: Resources(s, (False,) * 4, True, False) for s in cleaned}
        reads = []
        def inspect(source):
            reads.append(source)
            return states[source]
        adapter = module.CleanedAdapter(runtime, owner, tuple(zip(launch, tokens)),
            tuple(zip(terminal, tokens)), tuple(zip(cleaned, tokens)), inspect)
        core = c.CutCoordinator(owner, launch + terminal + cleaned, adapter)
        core.apply(owner, core.reserve(owner, launch))
        terminal_receipt = core.apply(owner, core.reserve(owner, terminal))
        return c, runtime, owner, cleaned, adapter, core, states, reads, terminal_receipt

    def test_cleaned_applies_and_replays_without_inspection(self):
        for retries in (0, 1):
            c, runtime, owner, cleaned, adapter, core, states, reads, terminal = self.fixture(retries=retries)
            reclaim, = JournalRuntimeTests.settle(runtime)
            self.assertEqual(adapter.reclaims[0], reclaim)
            cut = core.reserve(owner, cleaned)
            receipt = core.apply(owner, cut)
            state = runtime.model.state['a']
            self.assertEqual((receipt.before, receipt.after, receipt.journal_serial), ((2, 0), (3, 0), 4))
            self.assertEqual((state.owned, state.cleanup, state.deadline, state.generation), (False, 'complete', None, 1))
            self.assertEqual(state.phase, 'retry' if retries else 'terminal')
            self.assertEqual(runtime.pending, ())
            self.assertIs(adapter.observations[0], states[cleaned[0]])
            before = JournalRuntimeTests.snapshot(runtime)
            self.assertIs(core.apply(owner, cut), receipt)
            self.assertEqual(JournalRuntimeTests.snapshot(runtime), before)
            self.assertEqual(reads, list(cleaned))
            self.assertEqual(core.inspect(owner, terminal.cut), ('applied', terminal))

    def test_cleaned_requires_executed_reclaim(self):
        for outcome in ('reserved', 'issued', 'unknown', 'rejected-before-effects'):
            c, runtime, owner, cleaned, adapter, core, states, reads, _ = self.fixture()
            token, = runtime.pending
            if outcome != 'reserved':
                runtime.issue_obligations()
            if outcome in ('unknown', 'rejected-before-effects'):
                runtime.acknowledge(token, outcome)
            if outcome != 'rejected-before-effects':
                with self.assertRaises(InvalidEffect):
                    core.reserve(owner, cleaned)
                self.assertEqual(reads, [])
            else:
                cut = core.reserve(owner, cleaned)
                with self.assertRaisesRegex(c.CutError, 'reclaim not executed'):
                    core.apply(owner, cut)
                self.assertTrue(core.closed and runtime.failed)
                self.assertEqual(core.inspect(owner, cut), ('unknown', None))
            self.assertTrue(runtime.model.state['a'].owned)
            self.assertEqual(runtime.model.state['a'].cleanup, 'pending')

    def test_cleaned_resource_inspection_denials(self):
        from dataclasses import replace
        for change in ([{'live': tuple(i == j for i in range(4))} for j in range(4)] +
                       [{'unresolved': True}, {'reclaim_applied': False}, {'live': (0,) * 4},
                        {'live': (False,) * 3}, {'source': object()}, {'reclaim_applied': 1}]):
            c, runtime, owner, cleaned, adapter, core, states, reads, _ = self.fixture()
            JournalRuntimeTests.settle(runtime)
            source, = cleaned
            states[source] = replace(states[source], **change)
            cut = core.reserve(owner, cleaned)
            with self.assertRaises(c.CutError):
                core.apply(owner, cut)
            self.assertTrue(core.closed and runtime.failed and runtime.model.state['a'].owned)
            self.assertIs(adapter.observations[0], states[source])
            self.assertEqual(runtime.model.state['a'].cleanup, 'pending')

    def test_cleaned_preflights_both_members(self):
        from dataclasses import replace
        c, runtime, owner, cleaned, adapter, core, states, reads, _ = self.fixture(count=2)
        JournalRuntimeTests.settle(runtime)
        states[cleaned[1]] = replace(states[cleaned[1]], live=(False, False, True, False))
        cut = core.reserve(owner, cleaned)
        with self.assertRaisesRegex(c.CutError, 'resources unresolved'):
            core.apply(owner, cut)
        self.assertEqual(reads, list(cleaned))
        self.assertTrue(all(s.owned and s.cleanup == 'pending' for s in runtime.model.state.values()))
        self.assertEqual(core.inspect(owner, cut), ('unknown', None))

    def test_cleaned_two_members_success(self):
        c, runtime, owner, cleaned, adapter, core, states, reads, _ = self.fixture(count=2)
        tokens = JournalRuntimeTests.settle(runtime)
        self.assertEqual(tuple(adapter.reclaims), tokens)
        receipt = core.apply(owner, core.reserve(owner, cleaned))
        self.assertEqual((receipt.before, receipt.after), ((2, 2), (3, 3)))
        self.assertTrue(all(not s.owned and s.cleanup == 'complete' for s in runtime.model.state.values()))
        self.assertEqual(runtime.pending, ())

    def test_cleaned_revalidates_after_inspection(self):
        c, runtime, owner, cleaned, adapter, core, states, reads, _ = self.fixture()
        JournalRuntimeTests.settle(runtime)
        cut = core.reserve(owner, cleaned)
        def inspect(source):
            runtime.model.state['a'].generation = 2
            return states[source]
        adapter.inspect_resources = inspect
        with self.assertRaisesRegex(c.CutError, 'cleaned state'):
            core.apply(owner, cut)
        self.assertTrue(core.closed and runtime.failed and runtime.model.state['a'].owned)

    def test_cleaned_callback_failure_and_reentry(self):
        for reentry in (False, True):
            c, runtime, owner, cleaned, adapter, core, states, reads, _ = self.fixture()
            JournalRuntimeTests.settle(runtime)
            cut = core.reserve(owner, cleaned)
            def inspect(source):
                if reentry:
                    core.apply(owner, cut)
                raise RuntimeError('inspection failed')
            adapter.inspect_resources = inspect
            with self.assertRaisesRegex(c.CutError if reentry else RuntimeError, 'reentry' if reentry else 'inspection failed'):
                core.apply(owner, cut)
            self.assertTrue(core.closed and runtime.failed and runtime.model.state['a'].owned)
            self.assertEqual(adapter.observations, [None, None])

    def test_cleaned_missing_transition_closes(self):
        c, runtime, owner, cleaned, adapter, core, states, reads, _ = self.fixture()
        JournalRuntimeTests.settle(runtime)
        cut = core.reserve(owner, cleaned)
        original = runtime.model.batch
        def omit(events, now):
            return original([], now=now)
        with patch.object(runtime.model, 'batch', omit), self.assertRaisesRegex(c.CutError, 'cleaned transition missing'):
            core.apply(owner, cut)
        self.assertTrue(core.closed and runtime.failed and runtime.model.state['a'].owned)
        self.assertEqual(adapter.captured, ())
        self.assertEqual(core.inspect(owner, cut), ('unknown', None))

    def test_cleaned_omission_controls(self):
        import types
        from dataclasses import replace
        path = Path(__file__).resolve().parents[1] / 'prototypes/runtime_model/cleaned_adapter.py'
        text = path.read_text()
        for name, old in [('reclaim', "raise CutError('reclaim not executed')"),
                          ('resources', 'Retirement._empty(observation, source)')]:
            self.assertEqual(text.count(old), 1)
            module = types.ModuleType('prototypes.runtime_model._cleaned_' + name)
            module.__package__ = 'prototypes.runtime_model'
            sys.modules[module.__name__] = module
            try:
                exec(compile(text.replace(old, 'pass'), str(path), 'exec'), module.__dict__)
                c, runtime, owner, cleaned, adapter, core, states, reads, _ = self.fixture(module)
                if name == 'reclaim':
                    token, = runtime.issue_obligations()
                    runtime.acknowledge(token, 'rejected-before-effects')
                else:
                    JournalRuntimeTests.settle(runtime)
                    states[cleaned[0]] = replace(states[cleaned[0]], live=(True, False, False, False))
                core.apply(owner, core.reserve(owner, cleaned))
                with self.assertRaisesRegex(AssertionError, name + ' check omitted'):
                    self.assertTrue(runtime.model.state['a'].owned, name + ' check omitted')
            finally:
                del sys.modules[module.__name__]


class JournalRetirementTests(unittest.TestCase):
    @staticmethod
    def fixture(module=None):
        from types import SimpleNamespace
        from prototypes.runtime_model import cut_coordinator as c
        from prototypes.runtime_model import cut_retirement as r
        from prototypes.runtime_model.cleaned_adapter import CleanedAdapter
        if module is None:
            module = r
        runtime = JournalRuntime([Service('a'), Service('b')])
        runtime.start(['a', 'b'])
        tokens = JournalRuntimeTests.settle(runtime)
        owner = object()
        phases = [tuple(c.Source(owner, i,
            (1, 2, 3, t[3], t[4], i + 4, t[6], 6, 7, t[9]),
            0xb0000101 + i, phase, (1, 18, 1, 1) if phase == 2 else (0,))
            for i, t in enumerate(tokens)) for phase in (1, 2, 3)]
        launch, terminal, cleaned = phases
        class ResourcesAdapter:
            def __init__(self):
                self.pending = None
                self.marked = [None, None]
                self.states = {s: r.Resources(s, (False,) * 4, True, False) for s in cleaned}
                self.release_mode = self.mark_mode = None
                self.release_calls = self.mark_calls = 0
            def pending_source(self):
                return self.pending
            def release(self, source, receipt):
                self.release_calls += 1
                if self.release_mode != 'no-op':
                    self.pending = None
                if self.release_mode == 'lost':
                    raise c.CutError('release lost')
                return None if self.release_mode == 'wrong' else receipt
            def inspect(self, source):
                return self.states[source]
            def mark(self, source, receipt):
                self.mark_calls += 1
                self.marked[source.attempt] = receipt
                if self.mark_mode == 'lost':
                    raise c.CutError('mark lost')
                return None if self.mark_mode == 'wrong' else receipt
        resources = ResourcesAdapter()
        adapter = CleanedAdapter(runtime, owner, tuple(zip(launch, tokens)),
            tuple(zip(terminal, tokens)), tuple(zip(cleaned, tokens)), resources.inspect)
        core = c.CutCoordinator(owner, launch + terminal + cleaned, adapter)
        retirement = module.Retirement(core, resources)
        def apply(members):
            return core.apply(owner, core.reserve(owner, members))
        return SimpleNamespace(c=c, runtime=runtime, owner=owner, launch=launch,
            terminal=terminal, cleaned=cleaned, resources=resources, adapter=adapter,
            core=core, retirement=retirement, apply=apply)

    @staticmethod
    def mixed(other=2, module=None, release=True):
        f = JournalRetirementTests.fixture(module)
        f.apply(f.launch if other == 2 else (f.launch[0],))
        terminal = f.apply((f.terminal[0],))
        f.resources.pending = f.terminal[0]
        if release:
            f.retirement.release_pending(f.owner, terminal, f.terminal[0])
        JournalRuntimeTests.settle(f.runtime)
        mixed = f.apply((f.cleaned[0], f.terminal[1] if other == 2 else f.launch[1]))
        return f, terminal, mixed

    def test_real_mixed_retirement_preserves_journal_and_other_member(self):
        for other in (1, 2):
            f, terminal, mixed = self.mixed(other)
            f.resources.pending = f.terminal[1] if other == 2 else None
            before = JournalRuntimeTests.snapshot(f.runtime)
            records = tuple(f.core.records)
            pending = f.runtime.pending
            if other == 2:
                self.assertEqual(len(pending), 1)
                self.assertEqual(pending[0][5:8], ('b', 1, 'reclaim'))
                self.assertEqual(f.runtime.journal.observe(pending[0]), 'reserved')
            self.assertEqual(mixed.after, (3, other))
            self.assertEqual(f.retirement.retire(f.owner, mixed), 'retired')
            self.assertEqual(f.retirement.retire(f.owner, mixed), 'already-retired')
            self.assertEqual(f.resources.marked, [mixed, None])
            self.assertEqual(f.resources.mark_calls, 1)
            self.assertEqual(JournalRuntimeTests.snapshot(f.runtime), before)
            self.assertEqual(tuple(f.core.records), records)
            self.assertEqual(f.core.inspect(f.owner, mixed.cut), ('applied', mixed))
            self.assertEqual(f.retirement.release_pending(f.owner, terminal, f.terminal[0]), 'already-released')
            self.assertIs(f.resources.pending, f.terminal[1] if other == 2 else None)
            self.assertEqual(f.runtime.pending, pending)
            if other == 2:
                f.retirement.release_pending(f.owner, mixed, f.terminal[1])
                JournalRuntimeTests.settle(f.runtime)
                last = f.apply((f.cleaned[1],))
                self.assertEqual(f.retirement.retire(f.owner, last), 'retired')
                self.assertEqual(f.adapter.phases, (3, 3))
                self.assertEqual(f.resources.marked, [mixed, last])

    def test_real_cleanup_does_not_replace_pending_release(self):
        f, terminal, mixed = self.mixed(release=False)
        before = JournalRuntimeTests.snapshot(f.runtime)
        with self.assertRaisesRegex(f.c.CutError, 'pending release required'):
            f.retirement.retire(f.owner, mixed)
        self.assertEqual(f.resources.mark_calls, 0)
        self.assertIs(f.resources.pending, f.terminal[0])
        self.assertEqual(JournalRuntimeTests.snapshot(f.runtime), before)
        f.retirement.release_pending(f.owner, terminal, f.terminal[0])
        self.assertEqual(f.retirement.retire(f.owner, mixed), 'retired')

    def test_real_retirement_reinspects_resources(self):
        from dataclasses import replace
        f, _, mixed = self.mixed()
        source = f.cleaned[0]
        f.resources.states[source] = replace(f.resources.states[source], live=(False, True, False, False))
        before = JournalRuntimeTests.snapshot(f.runtime)
        with self.assertRaisesRegex(f.c.CutError, 'resources unresolved'):
            f.retirement.retire(f.owner, mixed)
        self.assertEqual(f.resources.mark_calls, 0)
        self.assertEqual(JournalRuntimeTests.snapshot(f.runtime), before)
        self.assertEqual(f.core.inspect(f.owner, mixed.cut), ('applied', mixed))

    def test_real_release_uncertainty_retains_applied_terminal(self):
        for mode in ('no-op', 'wrong', 'lost'):
            f = self.fixture()
            f.apply(f.launch)
            terminal = f.apply((f.terminal[0],))
            f.resources.pending = f.terminal[0]
            f.resources.release_mode = mode
            before = JournalRuntimeTests.snapshot(f.runtime)
            with self.assertRaises(f.c.CutError):
                f.retirement.release_pending(f.owner, terminal, f.terminal[0])
            self.assertTrue(f.core.closed)
            self.assertEqual(f.retirement.releases[0], ('started', terminal))
            self.assertEqual(f.core.inspect(f.owner, terminal.cut), ('applied', terminal))
            self.assertEqual(JournalRuntimeTests.snapshot(f.runtime), before)
            with self.assertRaisesRegex(f.c.CutError, 'closed'):
                f.retirement.release_pending(f.owner, terminal, f.terminal[0])
            self.assertEqual(f.resources.release_calls, 1)
            self.assertTrue(f.runtime.model.state['a'].owned)

    def test_real_mixed_mark_uncertainty_preserves_other_reclaim(self):
        for mode in ('wrong', 'lost'):
            f, _, mixed = self.mixed()
            f.resources.pending = f.terminal[1]
            f.resources.mark_mode = mode
            before = JournalRuntimeTests.snapshot(f.runtime)
            with self.assertRaises(f.c.CutError):
                f.retirement.retire(f.owner, mixed)
            self.assertTrue(f.core.closed)
            self.assertEqual(f.retirement.dispositions, [('started', mixed), None])
            self.assertEqual(f.resources.marked, [mixed, None])
            self.assertIs(f.resources.pending, f.terminal[1])
            self.assertEqual(JournalRuntimeTests.snapshot(f.runtime), before)
            self.assertEqual(f.core.inspect(f.owner, mixed.cut), ('applied', mixed))
            with self.assertRaisesRegex(f.c.CutError, 'closed'):
                f.retirement.retire(f.owner, mixed)
            self.assertEqual(f.resources.mark_calls, 1)

    def test_real_path_rejects_copied_receipt(self):
        from dataclasses import replace
        f, _, mixed = self.mixed()
        with self.assertRaisesRegex(f.c.CutError, 'unapplied receipt'):
            f.retirement.retire(f.owner, replace(mixed))
        self.assertEqual(f.resources.mark_calls, 0)

    def test_real_retirement_omission_controls(self):
        import types
        path = Path(__file__).resolve().parents[1] / 'prototypes/runtime_model/cut_retirement.py'
        text = path.read_text()
        for name, old, new in [
            ('release', "raise CutError('pending release required')", 'continue'),
            ('member', 'if s.phase == 3)', 'if s.phase in (2, 3))')]:
            self.assertEqual(text.count(old), 1)
            module = types.ModuleType('prototypes.runtime_model._integrated_' + name)
            module.__package__ = 'prototypes.runtime_model'
            sys.modules[module.__name__] = module
            try:
                exec(compile(text.replace(old, new), str(path), 'exec'), module.__dict__)
                # Resources keeps its canonical type: only the retirement algorithm is mutated.
                from prototypes.runtime_model.cut_retirement import Resources
                module.Resources = Resources
                f, _, mixed = self.mixed(module=module, release=name != 'release')
                if name == 'member':
                    f.resources.pending = f.terminal[1]
                    f.retirement.release_pending(f.owner, mixed, f.terminal[1])
                    f.resources.states[f.terminal[1]] = Resources(f.terminal[1], (False,) * 4, True, False)
                f.retirement.retire(f.owner, mixed)
                with self.assertRaisesRegex(AssertionError, name + ' integration omitted'):
                    self.assertEqual(f.resources.mark_calls, 0 if name == 'release' else 1,
                                     name + ' integration omitted')
            finally:
                del sys.modules[module.__name__]


if __name__ == '__main__':
    unittest.main()
