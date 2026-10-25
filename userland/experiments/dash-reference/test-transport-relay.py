#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Real loopback directional-EOF controls; Python 3.10+."""
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
RELAY = Path(__file__).with_name('transport-relay.py')


def read_all(sock):
    chunks = []
    while True:
        data = sock.recv(65536)
        if not data:
            return b''.join(chunks)
        chunks.append(data)
        if sum(map(len, chunks)) > 1024**2:
            raise RuntimeError('fixture receive bound exceeded')


class RelayTests(unittest.TestCase):
    def exercise(self, reverse):
        work = Path(tempfile.mkdtemp(prefix='relay-eof-', dir=ROOT / 'build'))
        print('retained:', work, flush=True)
        response = b'response\x00' * 32768
        request = b'late request\x00' if reverse else b'request\x00'
        observed, errors = [], []
        listener = socket.socket()
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        listener.settimeout(5)

        def serve():
            try:
                with listener.accept()[0] as sock:
                    sock.settimeout(5)
                    if reverse:
                        sock.sendall(response)
                        sock.shutdown(socket.SHUT_WR)
                    observed.append(read_all(sock))
                    if not reverse:
                        sock.sendall(response)
            except OSError as error:
                errors.append(repr(error))
            finally:
                listener.close()

        thread = threading.Thread(target=serve, daemon=True)
        argv = [sys.executable, '-B', str(RELAY), '127.0.0.1',
                str(listener.getsockname()[1]), str(work / 'ready.json')]
        record = dict(argv=argv, python=sys.version, reverse=reverse,
                      relay_sha256=hashlib.sha256(RELAY.read_bytes()).hexdigest())
        received = b''
        with (work / 'relay.stdout').open('wb') as stdout:
            with (work / 'relay.stderr').open('wb') as stderr:
                proc = subprocess.Popen(argv, cwd=work,
                    env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'},
                    stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
                thread.start()
                try:
                    deadline = time.monotonic() + 3
                    while not (work / 'ready.json').exists():
                        if proc.poll() is not None or time.monotonic() > deadline:
                            raise RuntimeError('relay startup failed')
                        time.sleep(0.01)
                    port = json.loads((work / 'ready.json').read_text())['port']
                    with socket.create_connection(('127.0.0.1', port),
                                                  timeout=5) as client:
                        client.settimeout(5)
                        if not reverse:
                            client.sendall(request)
                            client.shutdown(socket.SHUT_WR)
                        received = read_all(client)
                        if reverse:
                            client.sendall(request)
                            client.shutdown(socket.SHUT_WR)
                    thread.join(6)
                finally:
                    if proc.poll() is None:
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            proc.wait(timeout=3)
                    thread.join(6)
                    record.update(relay_exit=proc.returncode,
                                  server_finished=not thread.is_alive(),
                                  server_errors=errors,
                                  received_bytes=len(received),
                                  received_sha256=hashlib.sha256(received).hexdigest(),
                                  expected_sha256=hashlib.sha256(response).hexdigest(),
                                  request_matches=observed == [request])
                    (work / 'result.json').write_text(json.dumps(record,
                                                               indent=2) + '\n')
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(observed, [request])
        self.assertEqual(received, response)

    def test_request_eof_then_response(self):
        self.exercise(False)

    def test_response_eof_then_late_request(self):
        self.exercise(True)


if __name__ == '__main__':
    unittest.main()
