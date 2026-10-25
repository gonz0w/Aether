# SPDX-License-Identifier: BSD-2-Clause
"""Host-only read-only monitor bounds and unchanged guest watchdog semantics."""
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import emulator
import native_monitor as monitor
import native_smoke as native


class Monitor(unittest.TestCase):
    def test_protocol_only_allows_fixed_register_and_hex_stack_reads(self):
        replies = (b'{"QMP":{}}\n{"return":{}}\n' +
                   json.dumps({"return": "RIP=0000000000401234 RSP=000000001234abcd"}).encode() + b"\n" +
                   json.dumps({"return": "1234abcd: 0000000000401234"}).encode() + b"\n")
        client = Mock()
        client.__enter__ = Mock(return_value=client)
        client.__exit__ = Mock(return_value=False)
        stream = io.BytesIO(replies)
        client.makefile.return_value = stream
        with patch.object(monitor.socket, "socket", return_value=client):
            result = monitor.capture("/owned/monitor.sock")
        sent = [json.loads(c.args[0]) for c in client.sendall.call_args_list]
        self.assertEqual(sent, [{"execute": "qmp_capabilities"},
            {"execute": "human-monitor-command", "arguments": {"command-line": "info registers"}},
            {"execute": "human-monitor-command", "arguments": {"command-line": "x/16gx 0x1234abcd"}}])
        self.assertEqual(result["stack_address"], 0x1234abcd)
        self.assertTrue(all(0 < c.args[0] <= 0.2 for c in client.settimeout.call_args_list))

    def test_malformed_oversized_and_event_floods_are_bounded(self):
        for data in (b"", b"[]\n", b"null\n", b"x" * (monitor.LINE_LIMIT + 1),
                     b'{"event":"tick"}\n' * 17, b'{"error":{}}\n'):
            with self.subTest(data=data[:20]), self.assertRaises(ValueError):
                monitor.response(io.BytesIO(data))

    def test_exact_eight_before58s_and_text_errors_never_expand_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            with patch.object(monitor.time, "monotonic", return_value=0):
                sampler = monitor.Snapshots("/owned/monitor.sock", output)
            with patch.object(monitor, "capture", return_value={"registers": "r", "stack_words": "s"}) as capture:
                for tick in (31, *monitor.SCHEDULE, 58, 59, 60):
                    with patch.object(monitor.time, "monotonic", return_value=tick):
                        sampler.poll()
                self.assertEqual(capture.call_count, 8)
            self.assertEqual(len(json.loads(output.read_text())["rows"]), 8)
            with patch.object(monitor.time, "monotonic", return_value=0):
                late = monitor.Snapshots("/owned/monitor.sock", output)
            with patch.object(monitor, "capture") as capture, patch.object(monitor.time, "monotonic", return_value=58):
                late.poll()
                capture.assert_not_called()
                self.assertIn("deadline", late.rows[0]["error"])
            with patch.object(monitor.time, "monotonic", return_value=0):
                full = monitor.Snapshots("/owned/monitor.sock", output)
            with patch.object(monitor, "capture", return_value={"registers": "x" * monitor.TEXT_LIMIT}), patch.object(monitor.time, "monotonic", return_value=32):
                full.poll()
                self.assertEqual(full.text_bytes, 0)
                self.assertIn("text limit", full.rows[0]["error"])

    def test_poll_still_times_out_and_never_masks_panic(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "serial.log"
            log.write_bytes(b"")
            process = Mock()
            process.poll.return_value = None
            callback = Mock()
            with self.assertRaises(TimeoutError):
                emulator.wait_for_boot(process, log, 0.07, poll=callback)
            self.assertGreater(callback.call_count, 0)
            log.write_bytes(b"AETHER PANIC: fixture\n")
            callback.reset_mock()
            with self.assertRaises(RuntimeError):
                emulator.wait_for_boot(process, log, 0.1, poll=callback)
            callback.assert_not_called()

    def test_monitor_selector_rejects_non_writer_before_any_input(self):
        for kwargs in ({}, {"_pair_stop": True}, {"_zpl_writer_60s": True},
                       {"_pair_stop": True, "_zpl_writer_60s": True, "_zpl_mutation_seed": True}):
            with patch.object(native, "verify", side_effect=AssertionError("unexpected input")):
                with self.assertRaises(ValueError):
                    native.run("/absent", _monitor_diagnostic=True, **kwargs)

    def test_actual_writer_keeps60_and_join_on_monitor_timeout(self):
        import zpl_pair as pair
        with tempfile.TemporaryDirectory(prefix=pair.PREFIX, dir=pair.ROOT / "zig-out") as directory:
            root = Path(directory)
            writer = root / "writer"
            writer.mkdir()
            disk = root / "native-namespace.raw"
            with disk.open("wb") as stream:
                stream.truncate(1073750016)
            process = Mock()
            process.poll.return_value = None
            with patch.object(native, "verify"), patch.object(native.subprocess, "check_output", return_value="QEMU emulator version " + native.LOCK["qemu"]), \
                 patch.object(native.subprocess, "Popen", return_value=process), patch.object(native.shutil, "copyfile"), \
                 patch("openzfs_namespace.native_media_snapshot"), patch.object(native, "wait_for_boot", side_effect=TimeoutError("bounded60")) as wait:
                with self.assertRaisesRegex(TimeoutError, "bounded60"):
                    native.run(writer / "aether.iso", _pair_stop=True, _zpl_writer_60s=True,
                               _monitor_diagnostic=True, block_namespace=True, block_large=True,
                               block_disk=disk, marker=pair.MARKER.encode())
            self.assertEqual(wait.call_args.args[2], 60)
            self.assertIsInstance(wait.call_args.kwargs["poll"].__self__, monitor.Snapshots)
            args = json.loads((writer / "native-qemu-command.json").read_text())["argv"]
            self.assertEqual(args.count("-qmp"), 1)
            self.assertRegex(args[args.index("-qmp") + 1], r"^unix:.*/monitor.sock,server=on,wait=off$")
            self.assertEqual(args[args.index("-monitor") + 1], "none")
            process.terminate.assert_called_once()
            process.wait.assert_called_once_with(timeout=3)


if __name__ == "__main__":
    unittest.main()
