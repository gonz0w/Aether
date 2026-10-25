# SPDX-License-Identifier: BSD-2-Clause
"""Two-attempt trusted lifecycle composition; caller supplies native replies."""
from .admitted_resources import AdmittedResources
from .confirmed_result import PROFILE
from .effect_ledger import InvalidEffect
from .journal_runtime import JournalRuntime
from .rejected_launch_cleanup import RejectedLaunchCleanup
from .result_applier import ResultApplier
from .target_registry import TargetRegistry


class LifecycleDriver:
    def __init__(self, runtime, *, owner, producer):
        if type(runtime) is not JournalRuntime or len(runtime.model.spec) > 2:
            raise InvalidEffect('synchronous runtime with at most two services required')
        self.applier = ResultApplier(runtime, owner=owner, producer=producer)
        self.registry = TargetRegistry(self.applier)
        self.runtime = runtime
        self.attempts = {}

    def _attempt(self, service, owner):
        self.applier._available(owner)
        if type(service) is not str or service not in self.attempts:
            raise InvalidEffect('unknown attempt')
        return self.attempts[service]

    def prepare(self, token, slot, reader, writer, *, owner):
        self.applier._available(owner)
        if hasattr(self, 'channel_generations'):
            raise InvalidEffect('reserved acquisition mode active')
        if self.runtime.journal.observe(token) != 'issued' or token[7] != 'launch':
            raise InvalidEffect('issued launch required')
        if token[5] in self.attempts or len(self.attempts) >= 2:
            raise InvalidEffect('attempt capacity or duplicate')
        if (any(type(h) is not int or not 0 < h < (1 << 64) for h in (reader, writer))
                or reader == writer):
            raise InvalidEffect('endpoint pair')
        if any(h in (a['reader'], a['writer']) for a in self.attempts.values()
               for h in (reader, writer)):
            raise InvalidEffect('endpoint overlap')
        attempt = dict(token=token, reader=reader, writer=writer, phase='preparing',
                       target=None, call=None, rejected=None, resources=None, event=None)
        self.attempts[token[5]] = attempt
        try:
            target = self.registry.reserve(token, slot, owner=owner)
            attempt['target'] = target
            call = self.applier.bind(token, 0x23001, target, owner=owner)
            attempt['call'] = call
            attempt['rejected'] = RejectedLaunchCleanup(self.applier, call, reader, writer, owner=owner)
            attempt['phase'] = 'prepared'
            return call
        except BaseException:
            self.runtime.driver_lost()
            raise

    def reserve_channel(self, token, slot, *, owner):
        self.applier._available(owner)
        if self.runtime.journal.observe(token) != 'issued' or token[7] != 'launch':
            raise InvalidEffect('issued launch required')
        if token[5] in self.attempts or len(self.attempts) >= 2:
            raise InvalidEffect('attempt capacity or duplicate')
        if getattr(self, 'channel_pending', None) is not None:
            raise InvalidEffect('channel creation pending')
        if not hasattr(self, 'channel_generations') and self.attempts:
            raise InvalidEffect('external acquisition already active')
        target = self.registry.reserve(token, slot, owner=owner)
        if not hasattr(self, 'channel_generations'):
            self.channel_generations = [0, 0]
        self.attempts[token[5]] = dict(token=token, target=target, reader=None, writer=None,
            call=None, rejected=None, resources=None, event=None, phase='acquiring',
            channel_error=None)
        self.channel_pending = token[5]
        return ('channel-create-v1', token, 0x24000)

    def channel_reply(self, service, reply, *, owner):
        attempt = self._attempt(service, owner)
        if attempt['phase'] != 'acquiring' or self.channel_pending != service:
            raise InvalidEffect('channel not reserved')
        try:
            fields = {'schema', 'profile', 'producer', 'token', 'syscall', 'result', 'writer'}
            if type(reply) is not dict or set(reply) != fields:
                raise InvalidEffect('channel reply fields')
            for field, value in (('schema', 'abi6-channel-return-v1'), ('profile', PROFILE),
                                 ('producer', self.applier.producer)):
                if type(reply[field]) is not str or reply[field] != value:
                    raise InvalidEffect('channel reply identity')
            token = attempt['token']
            if (type(reply['token']) is not tuple or reply['token'] != token
                    or self.runtime.journal.observe(reply['token']) != 'issued'
                    or type(reply['syscall']) is not int or reply['syscall'] != 0x24000
                    or type(reply['result']) is not int):
                raise InvalidEffect('channel call mismatch')
            result = reply['result']
            if result in (-13, -22, -16, -28):
                if reply['writer'] is not None:
                    raise InvalidEffect('unused writer output')
                attempt['channel_error'] = result
                if self.runtime.acknowledge(token, 'rejected-before-effects') != 'recorded':
                    raise InvalidEffect('uninvoked launch acknowledgment')
                slot, record = self.registry._target(attempt['target'])
                if record['phase'] != 'reserved' or record['token'] != token:
                    raise InvalidEffect('reservation changed')
                del self.registry.slots[slot]
                attempt['phase'] = 'unacquired'
                attempt['event'] = ('denied' if result == -13 else 'launch_failed',
                                    token[5], token[6], token[1], result)
                self.channel_pending = None
                return None
            pairs = {0xd1000000 | (slot << 16) | (generation << 8) | 1: (slot, generation)
                     for slot in (0, 1) for generation in (1, 2, 3)}
            if (result not in pairs or type(reply['writer']) is not int
                    or reply['writer'] != result + 1):
                raise InvalidEffect('channel pair')
            channel, generation = pairs[result]
            if generation != self.channel_generations[channel] + 1:
                raise InvalidEffect('channel generation')
            attempt['reader'], attempt['writer'] = result, reply['writer']
            self.channel_generations[channel] = generation
            call = self.applier.bind(token, 0x23001, attempt['target'], owner=owner)
            attempt['call'] = call
            attempt['rejected'] = RejectedLaunchCleanup(self.applier, call, result,
                                                        reply['writer'], owner=owner)
            attempt['phase'] = 'prepared'
            self.channel_pending = None
            return call
        except BaseException:
            self.runtime.driver_lost()
            raise

    def launch_reply(self, service, reply, *, owner):
        attempt = self._attempt(service, owner)
        if attempt['phase'] != 'prepared':
            raise InvalidEffect('launch not prepared')
        try:
            verdict = self.applier.apply(attempt['call'], reply, owner=owner)
            if verdict[1] == 'executed':
                self.registry.accept_launch(attempt['target'], owner=owner)
                attempt['resources'] = AdmittedResources(self.registry, attempt['target'],
                                                         attempt['reader'], owner=owner)
                token = attempt['token']
                event = ('launched', token[5], token[6], token[1], 0)
                phase = 'admitted'
            else:
                attempt['rejected'].accept_rejection(owner=owner)
                self.registry.accept_launch(attempt['target'], owner=owner)
                event = attempt['rejected'].failure_event(owner=owner)
                phase = 'rejected'
            attempt['event'], attempt['phase'] = event, phase
            return verdict
        except BaseException:
            self.runtime.driver_lost()
            raise

    def terminal_reply(self, service, reply, *, owner):
        attempt = self._attempt(service, owner)
        if attempt['phase'] != 'admitted' or type(reply) is not dict or reply.get('target') != attempt['target']:
            raise InvalidEffect('terminal attempt mismatch')
        event = self.registry.terminal_event(reply, owner=owner)
        if event is None:
            return
        old = attempt['event']
        if old is not None and old[0] != 'launched' and old != event:
            raise InvalidEffect('pending event conflict')
        attempt['event'] = event

    def reclaim(self, token, reply=None, *, owner):
        self.applier._available(owner)
        if self.runtime.journal.observe(token) != 'issued' or token[7] != 'reclaim':
            raise InvalidEffect('issued reclaim required')
        attempt = self._attempt(token[5], owner)
        if token[1:3] != attempt['token'][1:3] or token[5:7] != attempt['token'][5:7]:
            raise InvalidEffect('reclaim generation mismatch')
        if attempt['phase'] == 'unacquired':
            state = self.runtime.model.state[token[5]]
            if (reply is not None or not state.owned or not state.reclaim_sent
                    or state.generation != token[6] or attempt['channel_error'] is None):
                raise InvalidEffect('empty inventory reclaim mismatch')
            try:
                if self.runtime.acknowledge(token, 'executed') != 'recorded':
                    raise InvalidEffect('empty inventory acknowledgment')
                attempt['local_reclaim'] = token
                return ('local-cleanup-v1', token, 'channel-not-created')
            except BaseException:
                self.runtime.driver_lost()
                raise
        if attempt['phase'] == 'rejected':
            if reply is not None:
                raise InvalidEffect('no native target to reclaim')
            fact = attempt['rejected'].qualify_reclaim(token, owner=owner)
            try:
                if self.runtime.acknowledge(token, 'executed') != 'recorded':
                    raise InvalidEffect('local reclaim acknowledgment')
                return fact
            except BaseException:
                self.runtime.driver_lost()
                raise
        if attempt['phase'] != 'admitted' or reply is None:
            raise InvalidEffect('admitted reclaim reply required')
        try:
            call = self.applier.bind(token, 0x20002, attempt['target'], owner=owner)
            verdict = self.applier.apply(call, reply, owner=owner)
            if verdict[1] == 'executed':
                self.registry.accept_reclaim(attempt['target'], owner=owner)
            return verdict
        except BaseException:
            self.runtime.driver_lost()
            raise

    def queue_cleanup(self, service, *, owner):
        attempt = self._attempt(service, owner)
        if attempt['event'] is not None or attempt['phase'] not in ('admitted', 'rejected', 'unacquired'):
            raise InvalidEffect('cleanup event unavailable')
        if attempt['phase'] == 'unacquired':
            token = attempt.get('local_reclaim')
            state = self.runtime.model.state[service]
            if (token is None or self.runtime.journal.observe(token) != 'executed'
                    or not state.owned or state.generation != token[6]
                    or self.runtime.model.epoch != token[1]):
                raise InvalidEffect('empty cleanup not confirmed')
            attempt['event'] = ('cleaned', token[5], token[6], token[1], 0)
            return
        resources = attempt['resources'] if attempt['phase'] == 'admitted' else attempt['rejected']
        attempt['event'] = resources.cleaned_event(owner=owner)

    def deliver(self, *, owner):
        self.applier._available(owner)
        pending = [(name, a['event']) for name, a in sorted(self.attempts.items())
                   if a['event'] is not None]
        if not pending:
            return 0
        self.runtime.batch([event for _, event in pending])
        try:
            for name, event in pending:
                attempt = self.attempts[name]
                if event[0] == 'cleaned':
                    if attempt['phase'] == 'admitted':
                        self.registry.retire(attempt['target'], owner=owner)
                    del self.attempts[name]
                else:
                    attempt['event'] = None
            return len(pending)
        except BaseException:
            self.runtime.driver_lost()
            raise
