#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run one trusted, temporary descriptor fixture; not service installation."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from prototypes.host_runtime.descriptors import Prepared


def main():
    executable = Path(sys.executable).resolve()
    with tempfile.TemporaryDirectory(prefix='sys-init-descriptor-example-') as directory:
        path = Path(directory) / 'job.json'
        path.write_text(json.dumps(dict(
            schema='aether-service-experiment-v1', id='job', package='fixture',
            executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),
            target='host-posix-experiment-v1', argv=[str(executable), '-c', 'pass'],
            environment={}, kind='oneshot', requires={}, after=[], readiness='completed',
            restart=dict(mode='never', retries=0, delay_ms=1), authority_requests=[])))
        prepared = Prepared([path])
        runtime = prepared.activate(cwd=directory)
        try:
            if runtime.children:
                raise RuntimeError('activation unexpectedly launched a child')
            runtime.start(['job'])
            runtime.until(lambda: not runtime.children and not runtime.pending, timeout=5)
            if not runtime.model.state['job'].completed:
                raise RuntimeError('oneshot did not complete')
        finally:
            runtime.close()
    print('host descriptor example: pass')


if __name__ == '__main__':
    main()
