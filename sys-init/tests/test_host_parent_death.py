"""Bounded survival witness; a passing test explicitly does not mean containment."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prototypes.host_runtime.runtime import Command, HostRuntime
from prototypes.runtime_model.model import Service


def receipt(root, name, value):
    temporary = root / (name + '.tmp')
    temporary.write_text(json.dumps(value))
    temporary.replace(root / name)


def bounded_child(root):
    end = time.monotonic() + 10
    original_parent = os.getppid()
    receipt(root, 'hello.json', dict(pid=os.getpid(), parent=original_parent))
    probed = False
    while time.monotonic() < end:
        if (root / 'release').exists():
            receipt(root, 'released.json', dict(result='cooperative-exit-reached'))
            return
        if not probed and (root / 'probe').exists():
            receipt(root, 'alive.json', dict(pid=os.getpid(), parent=os.getppid(),
                                              original_parent=original_parent))
            probed = True
        time.sleep(.005)
    receipt(root, 'expired.json', dict(result='fixture-watchdog'))
    raise SystemExit(3)


def supervisor(root):
    executable = str(Path(sys.executable).resolve())
    command = Command((executable, str(Path(__file__).resolve()), '--child', str(root)),
                      hashlib.sha256(Path(executable).read_bytes()).hexdigest())
    rt = HostRuntime([Service('child', startup=1000)], {'child': command}, cwd=root)
    child = None
    try:
        rt.start(['child'])
        child = rt.children[('child', 1)]
        sys.stdin.readline()
    finally:
        rt.close()
        receipt(root, 'finally.json', dict(remaining=len(rt.children),
                                           returncode=None if child is None else child.returncode))


class ParentDeath(unittest.TestCase):
    def wait_receipt(self, root, name, timeout=4):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            path = root / name
            if path.exists():
                return json.loads(path.read_text())
            time.sleep(.005)
        self.fail('missing bounded fixture receipt: ' + name)

    def experiment(self, abrupt):
        with tempfile.TemporaryDirectory(prefix='sys-init-parent-') as directory:
            root = Path(directory)
            owner = subprocess.Popen([sys.executable, str(Path(__file__).resolve()),
                                      '--supervisor', directory], stdin=subprocess.PIPE,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            hello = None
            try:
                hello = self.wait_receipt(root, 'hello.json')
                self.assertEqual(hello['parent'], owner.pid)
                if abrupt:
                    owner.kill()
                    self.assertEqual(owner.wait(timeout=2), -signal.SIGKILL)
                    self.assertFalse((root / 'finally.json').exists())
                    (root / 'probe').touch()
                    alive = self.wait_receipt(root, 'alive.json')
                    self.assertEqual(alive['pid'], hello['pid'])
                    self.assertEqual(alive['original_parent'], owner.pid)
                    self.assertNotEqual(alive['parent'], owner.pid)
                    (root / 'release').touch()
                    self.assertEqual(self.wait_receipt(root, 'released.json')['result'],
                                     'cooperative-exit-reached')
                    witness = dict(case='abrupt-owner-death', owner_returncode=owner.returncode,
                                   hello=hello, survivor=alive, finally_ran=False,
                                   child_release='cooperative-exit-reached', child_reaping='unobserved')
                else:
                    owner.stdin.close()
                    self.assertEqual(owner.wait(timeout=2), 0)
                    result = self.wait_receipt(root, 'finally.json')
                    self.assertEqual(result['remaining'], 0)
                    self.assertIsInstance(result['returncode'], int)
                    self.assertLess(result['returncode'], 0)
                    witness = dict(case='normal-owner-exit', owner_returncode=owner.returncode,
                                   hello=hello, cleanup=result, finally_ran=True)
                self.assertFalse((root / 'expired.json').exists())
                print('PARENT-DEATH-WITNESS ' + json.dumps(witness, sort_keys=True), file=sys.stderr)
            finally:
                (root / 'release').touch()
                if owner.poll() is None:
                    owner.kill()
                owner.wait(timeout=2)
                owner.stdin.close()
                # A failed assertion must also leave the trusted orphan an exit request.
                if hello is not None and not (root / 'finally.json').exists():
                    self.wait_receipt(root, 'released.json')

    def test_abrupt_owner_death_leaves_child_running(self):
        self.experiment(abrupt=True)

    def test_normal_owner_exit_reaps_child_in_finally(self):
        self.experiment(abrupt=False)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] in ('--child', '--supervisor'):
        (bounded_child if sys.argv[1] == '--child' else supervisor)(Path(sys.argv[2]))
    else:
        unittest.main()
