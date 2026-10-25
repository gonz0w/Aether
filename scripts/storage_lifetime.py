# SPDX-License-Identifier: BSD-2-Clause
"""Separate private AENBD005/controller27 idle qualification, no public ABI."""
import re


def validate(selected, directories, reader=False, case='normal'):
    if not isinstance(selected, bool) or (selected and (not directories or case != 'normal')):
        raise ValueError('storage lifetime requires the separate normal directory profile')
    if not isinstance(reader, bool):
        raise ValueError('storage lifetime requires an exact reader role')


def controller(text):
    old = 'abi == 26'
    if text.count(old) != 1:
        raise ValueError('storage lifetime controller ABI context')
    return text.replace(old, 'abi == 27', 1)


def trace(serial):
    rows = [line for line in serial.splitlines() if line.startswith('NATIVE STORAGE ') and not line.startswith('NATIVE STORAGE WAIT ')]
    tick = None
    start = None
    deadline = None
    parks = 0
    for row in rows:
        observed = re.fullmatch(r'NATIVE STORAGE observe tick=(\d+)', row)
        parked = re.fullmatch(r'NATIVE STORAGE park tick=(\d+) deadline=(\d+)', row)
        woke = re.fullmatch(r'NATIVE STORAGE wake tick=(\d+) outcome=(event|deadline)', row)
        if observed:
            if start is not None or parks:
                raise ValueError('storage idle observation reset')
            start = int(observed[1])
            deadline = start + 6500
        elif parked:
            now, until = map(int, parked.groups())
            if tick is not None or parks >= 32:
                raise ValueError('storage idle park overlap/budget')
            if start is None:
                raise ValueError('storage idle observation required')
            if until != deadline or until - start != 6500 or now < start or now >= until:
                raise ValueError('storage idle fixed deadline')
            tick = now
            parks += 1
        elif woke:
            now = int(woke[1])
            if tick is None or now < tick or (woke[2] == 'deadline' and now < deadline):
                raise ValueError('storage idle wake identity/time')
            tick = None
            end = now
        else:
            raise ValueError('storage idle trace syntax')
    if not parks or tick is not None or end - start < 6500 or end <= 6000:
        raise ValueError('storage idle6500 ticks and paired completion required')
    return {'idle_start_tick': start, 'idle_end_tick': end,
            'idle_delivered_ticks': end-start, 'idle_park_attempts': parks,
            'post_idle_service_io_qualified': True}
