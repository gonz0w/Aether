# SPDX-License-Identifier: BSD-2-Clause
"""Compile and exercise the private Rust pipe core, without claiming native I/O."""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
import unittest


class PipeOwner(unittest.TestCase):
    def test_exec_request_progress(self):
        root = Path(__file__).resolve().parents[1]
        directory = Path(tempfile.mkdtemp(prefix="exec-request-host-", dir=root / "zig-out"))
        wrapper = directory / "test.rs"
        wrapper.write_text("#[path = " + json.dumps(str(root / "user/native-capacity/exec_request.rs"))
                           + "] mod exec_request;\n#[path = " + json.dumps(str(root / "user/native-capacity/startup.rs"))
                           + "] mod startup;\n")
        binary = directory / "exec-request-tests"
        receipts = []
        for profile in ([], ["--cfg", "pipeline_dash_parent"],
                        ["--cfg", "pipeline_dash_parent", "--cfg", "pipeline_shell_early"]):
            for command in (["rustc", "+1.98.0", "--edition=2024", "--test", *profile, str(wrapper), "-o", str(binary)],
                            [str(binary)]):
                result = subprocess.run(command, capture_output=True, text=True, timeout=180)
                receipts.append(dict(command=command, returncode=result.returncode,
                                     stdout=result.stdout, stderr=result.stderr))
                (directory / "checks.json").write_text(json.dumps(receipts, indent=2))
                self.assertEqual(result.returncode, 0, f"Retained {directory}: {result.stdout}{result.stderr}")
            self.assertIn("5 passed; 0 failed", receipts[-1]["stdout"])
        shutil.rmtree(directory)

    def test_core(self):
        root = Path(__file__).resolve().parents[1]
        output = root / "zig-out"
        output.mkdir(exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix="pipe-owner-host-", dir=output))
        source = root / "user/native-connections/pipe.rs"
        routing = root / "user/native-connections/pipeline.rs"
        binary = directory / "pipe-tests"
        # Compile the same module with no standard library for the native target.
        wrapper = directory / "core.rs"
        wrapper.write_text(
            '#![cfg_attr(not(test), no_std)]\n#[path = '
            + json.dumps(str(source)) + ']\npub mod pipe;\n'
            '#[path = ' + json.dumps(str(routing)) + ']\npub mod routing;\n'
            '#[path = ' + json.dumps(str(root / 'user/native-capacity/session_children.rs')) + ']\npub mod children;\n'
            '#[path = ' + json.dumps(str(root / 'user/native-capacity/session_exec.rs')) + ']\npub mod session_exec;\n'
            '#[path = ' + json.dumps(str(root / 'user/native-capacity/session_scratch.rs')) + ']\npub mod session_scratch;\n'
            '#[cfg(test)]\n#[path = ' + json.dumps(str(root / 'tests/session_scratch_cases.rs')) + ']\nmod scratch_cases;\n'
            'pub fn pipeline() -> pipe::PipelinePipe { pipe::PipelinePipe::new() }\n'
            'pub fn session() -> pipe::SessionPipe { pipe::SessionPipe::new() }\n'
            'pub fn session_request(p: &mut [pipe::SessionPipe; 2], c: pipe::Caller, '
            'f: &[u8; 32]) -> pipe::Outcome { routing::request(p, c, f) }\n'
            'pub fn pipeline_request(p: &mut pipe::PipelinePipe, c: pipe::Caller, '
            'f: &[u8; 32]) -> pipe::Outcome { p.request(c, f) }\n'
        )
        commands = [
            ["rustc", "+1.98.0", "--edition=2024", "--test", str(wrapper),
             "-o", str(binary)],
            [str(binary), "--nocapture"],
            ["rustc", "+1.98.0", "--edition=2024", "--crate-type=lib",
             "--target=x86_64-unknown-none", "-Cpanic=abort", "--emit=obj",
             str(wrapper), "-o", str(directory / "pipe-core.o")],
        ]
        receipts = []
        for command in commands:
            try:
                result = subprocess.run(
                    command, capture_output=True, text=True, timeout=180,
                )
            except (OSError, subprocess.TimeoutExpired) as error:
                receipts.append({"command": command, "error": str(error)})
                (directory / "checks.json").write_text(json.dumps(receipts, indent=2))
                self.fail(f"Pipe core infrastructure failure; retained {directory}: {error}")
            receipts.append({
                "command": command, "returncode": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr,
            })
            (directory / "checks.json").write_text(json.dumps(receipts, indent=2))
            self.assertEqual(
                result.returncode, 0,
                f"Retained {directory}\n{result.stdout}{result.stderr}",
            )
            if command[0] == str(binary):
                self.assertIn("79 passed; 0 failed", result.stdout)
        # Successful disposable host binaries have no release/evidence consumer.
        # Failures above leave all files and logs available for triage.
        shutil.rmtree(directory)


if __name__ == "__main__":
    unittest.main()
