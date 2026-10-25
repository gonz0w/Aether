# SPDX-License-Identifier: BSD-2-Clause
"""Fixed, read-only QMP snapshots for a bounded writer diagnostic."""
import json
from pathlib import Path
import re
import socket
import time

SCHEDULE = (32, 36, 40, 44, 48, 52, 55, 57)
LINE_LIMIT = 8192
TEXT_LIMIT = 65536


def response(stream, budget=None):
    """Bound replies/events; never consume an unbounded monitor stream."""
    for _ in range(16):
        if budget is not None:
            budget()
        line = stream.readline(LINE_LIMIT + 1)
        if not line or len(line) > LINE_LIMIT or not line.endswith(b"\n"):
            raise ValueError("monitor reply missing or oversized")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError("monitor reply type")
        if "error" in value:
            raise ValueError("monitor command failed")
        if "return" in value:
            return value["return"]
    raise ValueError("monitor event limit")


def capture(path):
    """Only registers and sixteen words from that observed stack address."""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        deadline = time.monotonic() + 0.2

        def budget():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("monitor snapshot deadline")
            client.settimeout(remaining)

        budget()
        client.connect(str(path))
        with client.makefile("rb") as stream:
            budget()
            greeting = stream.readline(LINE_LIMIT + 1)
            value = json.loads(greeting)
            if len(greeting) > LINE_LIMIT or not isinstance(value, dict) or "QMP" not in value:
                raise ValueError("monitor greeting")
            budget()
            client.sendall(b'{"execute":"qmp_capabilities"}\n')
            response(stream, budget)
            command = {"execute": "human-monitor-command",
                       "arguments": {"command-line": "info registers"}}
            budget()
            client.sendall(json.dumps(command).encode() + b"\n")
            registers = response(stream, budget)
            if not isinstance(registers, str):
                raise ValueError("monitor register type")
            match = re.search(r"\bRSP=([0-9a-fA-F]{1,16})\b", registers)
            if match is None:
                raise ValueError("monitor stack register missing")
            # Parse a bounded integer; guest text never becomes a command.
            stack_address = int(match[1], 16)
            command["arguments"]["command-line"] = f"x/16gx 0x{stack_address:x}"
            budget()
            client.sendall(json.dumps(command).encode() + b"\n")
            stack = response(stream, budget)
            if not isinstance(stack, str):
                raise ValueError("monitor stack type")
            return {"registers": registers, "stack_address": stack_address,
                    "stack_words": stack}


class Snapshots:
    """Eight attempts before58s, <=64KiB host text; no pause/write/extra guest."""
    def __init__(self, socket_path, result_path):
        self.socket_path = Path(socket_path)
        self.result_path = Path(result_path)
        self.started = time.monotonic()
        self.rows = []
        self.text_bytes = 0

    def poll(self):
        elapsed = time.monotonic() - self.started
        if len(self.rows) == len(SCHEDULE) or elapsed < SCHEDULE[len(self.rows)]:
            return
        row = {"scheduled_seconds": SCHEDULE[len(self.rows)],
               "elapsed_seconds": round(elapsed, 6)}
        # A delayed host poll cannot initiate a query next to the watchdog.
        if elapsed >= 58:
            row["error"] = "snapshot deadline passed"
        else:
            try:
                data = capture(self.socket_path)
                count = len(json.dumps(data).encode())
                if self.text_bytes + count > TEXT_LIMIT:
                    raise ValueError("monitor text limit")
                row.update(data)
                self.text_bytes += count
            except (OSError, ValueError) as error:
                row["error"] = str(error)[:160]
        self.rows.append(row)
        self.result_path.write_text(json.dumps({"schedule_seconds": SCHEDULE,
            "text_limit": TEXT_LIMIT, "rows": self.rows,
            "scope": "read-only non-atomic diagnostic; not uptime qualification"},
            indent=2) + "\n")
