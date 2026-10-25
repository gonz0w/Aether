# SPDX-License-Identifier: BSD-2-Clause
"""Trusted incremental stream simulation; its caller supplies logical time."""
from .control import MAX_ID
from .control_codec import InvalidFrame, MAX_BODY
from .control_delivery import Delivery, Backpressure


class Stream:
    def __init__(self, model, *, now=0, read_budget=100, write_budget=100):
        if type(now) is not int or not 0 <= now < MAX_ID:
            raise ValueError('clock')
        for budget in (read_budget, write_budget):
            if type(budget) is not int or not 1 <= budget <= 1000000:
                raise ValueError('budget')
        self.delivery = Delivery(model)
        self.now = now
        self.read_budget, self.write_budget = read_budget, write_budget
        self.phase = 'reading'
        self.deadline = min(MAX_ID, now + read_budget)
        self.buffer = bytearray()
        self.target = None
        self.offset = 0

    def _clock(self, now):
        if type(now) is not int or not self.now <= now <= MAX_ID:
            raise ValueError('clock')

    def tick(self, now):
        self._clock(now)
        self.now = now
        if self.phase == 'closed':
            return False
        if now >= self.deadline:
            self.disconnect()
            return False
        return True

    def feed(self, chunk, *, now):
        if not self.tick(now) or self.phase != 'reading':
            raise Backpressure('input unavailable')
        if type(chunk) is not bytes or len(chunk) > MAX_BODY + 4:
            self.disconnect()
            raise InvalidFrame('frame-length')
        cursor = 0
        if self.target is None:
            count = min(4 - len(self.buffer), len(chunk))
            self.buffer.extend(chunk[:count])
            cursor = count
            if len(self.buffer) < 4:
                return
            length = int.from_bytes(self.buffer, 'big')
            if not 1 <= length <= MAX_BODY:
                self.disconnect()
                raise InvalidFrame('frame-length')
            self.target = length + 4
        if len(chunk) - cursor > self.target - len(self.buffer):
            self.disconnect()
            raise InvalidFrame('frame-length')
        self.buffer.extend(chunk[cursor:])
        if len(self.buffer) == self.target:
            frame = bytes(self.buffer)
            self.buffer.clear()
            self.target = None
            try:
                self._receive(frame)
            except BaseException:
                self.disconnect()
                raise
            self.phase = 'writing'
            self.offset = 0
            self.deadline = min(MAX_ID, now + self.write_budget)

    def _receive(self, frame):
        self.delivery.receive(frame)

    def read(self, maximum, *, now):
        if type(maximum) is not int or not 1 <= maximum <= MAX_BODY + 4:
            raise ValueError('read bound')
        if not self.tick(now) or self.phase != 'writing':
            raise Backpressure('output unavailable')
        reply = self.delivery.reply
        part = reply[self.offset:self.offset + maximum]
        self.offset += len(part)
        if self.offset == len(reply):
            self.delivery.read_reply()
            self.offset = 0
            self.phase = 'reading' if self.delivery.connected else 'closed'
            self.deadline = min(MAX_ID, now + self.read_budget)
        return part

    def disconnect(self):
        self.delivery.disconnect()
        self.buffer.clear()
        self.target = None
        self.offset = 0
        self.phase = 'closed'

    def reconnect(self, *, now):
        self._clock(now)
        if self.phase != 'closed':
            raise Backpressure('connection active')
        if now == MAX_ID:
            raise ValueError('clock exhausted')
        self.delivery.reconnect()
        self.now = now
        self.phase = 'reading'
        self.deadline = min(MAX_ID, now + self.read_budget)

    def take_effects(self):
        return self.delivery.take_effects()
