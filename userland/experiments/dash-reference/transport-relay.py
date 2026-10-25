#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Test-only bounded opaque TCP relay; no SSH payload logging. Python 3.10+."""
import json
from pathlib import Path
import selectors
import socket
import sys
import time


def main():
    host, port, ready = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
    fault = Path(sys.argv[4]) if len(sys.argv) == 5 else None
    if len(sys.argv) not in (4, 5):
        raise ValueError('host port ready [fault-directory] required')
    if host != '127.0.0.1':
        raise ValueError('loopback target required')
    selector = selectors.DefaultSelector()
    listener = socket.socket()
    peers, pending = {}, {}
    read_eof, write_eof = set(), set()
    clients, not_before = set(), {}
    fault_record = {'delayed_bytes': 0, 'cut': False}

    def close_pair(sock):
        other = peers.get(sock)
        for item in [sock, other]:
            if item is not None and item in peers:
                try:
                    selector.unregister(item)
                except KeyError:
                    pass
                peers.pop(item)
                pending.pop(item)
                read_eof.discard(item)
                write_eof.discard(item)
                clients.discard(item)
                not_before.pop(item, None)
                item.close()

    def watch(sock):
        flags = 0 if sock in read_eof else selectors.EVENT_READ
        if pending[sock] and time.monotonic() >= not_before.get(sock, 0):
            flags |= selectors.EVENT_WRITE
        try:
            selector.get_key(sock)
        except KeyError:
            if flags:
                selector.register(sock, flags)
        else:
            if flags:
                selector.modify(sock, flags)
            else:
                selector.unregister(sock)

    def settle(sock):
        other = peers[sock]
        for item, source in [(sock, other), (other, sock)]:
            if source in read_eof and not pending[item] and item not in write_eof:
                item.shutdown(socket.SHUT_WR)
                write_eof.add(item)
            watch(item)
        if (sock in read_eof and other in read_eof
                and not pending[sock] and not pending[other]):
            close_pair(sock)

    try:
        listener.bind(('127.0.0.1', 0))
        listener.listen(8)
        listener.setblocking(False)
        selector.register(listener, selectors.EVENT_READ)
        ready.with_suffix('.tmp').write_text(
            json.dumps({'port': listener.getsockname()[1]}) + '\n')
        ready.with_suffix('.tmp').replace(ready)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if fault is not None and (fault / 'cut').exists():
                fault_record.update(cut=True, pending_bytes=sum(
                    len(pending[s]) for s in clients))
                break
            for item in list(peers):
                watch(item)
            for key, flags in selector.select(0.02 if fault else 0.1):
                sock = key.fileobj
                if sock is listener:
                    try:
                        incoming, _ = listener.accept()
                    except BlockingIOError:
                        continue
                    if len(peers) >= 16:
                        incoming.close()
                        continue
                    try:
                        remote = socket.create_connection((host, port), timeout=2)
                    except OSError:
                        incoming.close()
                        continue
                    clients.add(incoming)
                    for a, b in [(incoming, remote), (remote, incoming)]:
                        a.setblocking(False)
                        peers[a] = b
                        pending[a] = bytearray()
                        selector.register(a, selectors.EVENT_READ)
                    continue
                if sock not in peers:
                    continue
                try:
                    if flags & selectors.EVENT_READ:
                        data = sock.recv(65536)
                        if not data:
                            read_eof.add(sock)
                            settle(sock)
                            continue
                        other = peers[sock]
                        pending[other].extend(data)
                        if (other in clients and fault is not None
                                and (fault / 'armed').exists()):
                            not_before[other] = time.monotonic() + 0.5
                            fault_record['delayed_bytes'] += len(data)
                        if len(pending[other]) > 1024**2:
                            close_pair(sock)
                            continue
                        watch(other)
                    if flags & selectors.EVENT_WRITE and pending[sock]:
                        sent = sock.send(pending[sock])
                        del pending[sock][:sent]
                        settle(sock)
                except BlockingIOError:
                    continue
                except OSError:
                    close_pair(sock)
    finally:
        for sock in list(peers):
            if sock in peers:
                close_pair(sock)
        listener.close()
        selector.close()
        if fault is not None:
            (fault / 'relay-fault.json').write_text(
                json.dumps(fault_record, indent=2) + '\n')


if __name__ == '__main__':
    main()
