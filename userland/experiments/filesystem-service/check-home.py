# SPDX-License-Identifier: BSD-2-Clause
"""Check bounded home delegation using pinned host tools and no_std builds."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import sys
import tempfile
import time
import types


class Parser(argparse.ArgumentParser):
    def format_help(self):
        purpose = self.description
        self.description = None
        try:
            help_text = super().format_help()
        finally:
            self.description = purpose
        return purpose + "\n\n" + help_text

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, "[FAILED] " + ascii(message)[1:-1] + "\n")


class PreconditionError(Exception):
    pass


S = Path(__file__).resolve().parent
R = S.parents[1]
EVIDENCE = R / "docs/evidence/filesystem-home-2026-10-24"
PINS = R / "docs/evidence/filesystem-transport-2026-10-19/inputs.json"
PINS_SHA = "f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d"
HELPER = R / "experiments/command-runner/process.py"
HELPER_SHA = "9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e"
PROFILE = (
    "namespace", "lifetimes", "mixed", "wait", "bulk", "runtime",
    "activation", "names", "directories", "metadata", "directory_contexts",
)
SOURCE_NAMES = (
    "owner.rs", "metadata-lib.rs", "metadata.rs", "metadata-policy.rs",
    "namespace-policy.rs", "directory-context-policy.rs", "tests.rs",
    "runtime-counter-tests.rs", "home-tests.rs",
)
COMMON = ["--edition=2021", "-Dwarnings", "-Dunsafe_op_in_unsafe_fn", "-Funsafe-code"]
NATIVE = [
    "--target=x86_64-unknown-none", "-Cpanic=abort", "-Copt-level=2",
    "-Crelocation-model=static", "-Ccodegen-units=1",
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def verify(path, digest):
    try:
        if sha(path) != digest:
            raise PreconditionError("pinned input mismatch: " + str(path))
    except OSError as error:
        raise PreconditionError("pinned input unavailable: " + str(path)) from error


def cfg(home=False):
    names = [*PROFILE, *(["home"] if home else [])]
    return [value for name in names for value in ("--cfg", "fs_" + name)]


def check(record, work, proc, tools):
    env = proc.clean_env(work)
    env["DYLD_LIBRARY_PATH"] = str(Path(tools["rustc"]["path"]).parent.parent / "lib")
    deadline = time.monotonic() + 300

    def run(label, argv, expected=0, timeout=60):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError("300-second suite deadline expired before " + label)
        result = proc.run(list(map(str, argv)), cwd=R, env=env, work=work,
                          label=label, timeout=min(timeout, remaining))
        row = {
            "label": label, "expected_exit": expected, "process": result.record,
            "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
        }
        record["rows"].append(row)
        if (result.returncode != expected or not result.record["complete"]
                or result.record["cleanup"] != "complete"):
            row.update(stdout_tail=result.stdout.decode(errors="replace")[-3000:],
                       stderr_tail=result.stderr.decode(errors="replace")[-5000:])
            raise RuntimeError(label + " did not meet exit/cleanup contract")
        if expected != 0:
            row.update(stdout_tail=result.stdout.decode(errors="replace")[-1800:],
                       stderr_tail=result.stderr.decode(errors="replace")[-1800:])
        return result

    def rust(compiler, label, source, folder, flags, tail):
        return run(label, [tools[compiler]["path"], *COMMON, *flags,
                          "-Ldependency=" + str(folder), "--extern",
                          "filesystem_metadata=" + str(folder / "libfilesystem_metadata.rlib"),
                          source, *tail])

    for compiler in ("rustc", "rustfmt", "clippy-driver"):
        result = run(compiler + "-version", [tools[compiler]["path"], "--version"])
        record.setdefault("versions", {})[compiler] = result.stdout.decode().strip()

    host = work / "host"
    host.mkdir()
    metadata_flags = [flag for flag in COMMON if flag != "-Funsafe-code"]
    run("host-metadata", [tools["rustc"]["path"], *metadata_flags, "--crate-type=lib",
                          "--crate-name=filesystem_metadata", S / "metadata-lib.rs",
                          "-o", host / "libfilesystem_metadata.rlib"])
    # First behavioral compilation also records the planned red observation when
    # the tests precede the implementation. A compiler failure never counts as pass.
    rust("rustc", "home-tests-build", S / "owner.rs", host, cfg(True),
         ["--test", "-o", work / "home-tests"])
    result = run("home-tests", [work / "home-tests", "--test-threads=1"], timeout=30)
    record["home_tests_output"] = result.stdout.decode()
    summary = re.search(rb"test result: ok\. ([0-9]+) passed; 0 failed;", result.stdout)
    if b"home_tests::" not in result.stdout or summary is None or int(summary[1]) == 0:
        raise RuntimeError("home tests were absent")
    record["home_test_count"] = int(summary[1])
    run("rustfmt", [tools["rustfmt"]["path"], "--edition=2021", "--check",
                    S / "owner.rs", S / "home-policy.rs", S / "home-tests.rs"])
    rust("clippy-driver", "home-tests-clippy", S / "owner.rs", host, cfg(True),
         ["--test", "-o", work / "home-tests-clippy"])

    for label, flags in (("af08", cfg()), ("legacy", [])):
        rust("rustc", label + "-tests-build", S / "owner.rs", host, flags,
             ["--test", "-o", work / (label + "-tests")])
        result = run(label + "-tests", [work / (label + "-tests"), "--test-threads=1"], timeout=30)
        summary = re.search(rb"test result: ok\. ([0-9]+) passed; 0 failed;", result.stdout)
        if summary is None or int(summary[1]) == 0:
            raise RuntimeError(label + " regression cases were absent")
        record[label + "_test_count"] = int(summary[1])
        record[label + "_tests_output"] = result.stdout.decode()

    record["libraries"] = {}
    for stage, extra in (("host", []), ("native", NATIVE)):
        folder = work / stage
        folder.mkdir(exist_ok=True)
        if extra:
            run("native-metadata", [tools["rustc"]["path"], *metadata_flags, *extra,
                                    "--crate-type=lib", "--crate-name=filesystem_metadata",
                                    S / "metadata-lib.rs", "-o", folder / "libfilesystem_metadata.rlib"])
        for label, flags in (("home", cfg(True)), ("af08", cfg()), ("legacy", [])):
            output = folder / ("lib" + label + ".rlib")
            for compiler in ("rustc", "clippy-driver"):
                destination = output if compiler == "rustc" else folder / (label + "-clippy.rlib")
                rust(compiler, stage + "-" + label + "-" + compiler,
                     S / "owner.rs", folder, [*flags, *extra],
                     ["--crate-type=lib", "--crate-name=" + label, "-o", destination])
            record["libraries"][stage + "-" + label] = sha(output)
        invalid = [name for name in PROFILE if name != "directory_contexts"]
        flags = [value for name in [*invalid, "home"] for value in ("--cfg", "fs_" + name)]
        rejected = run(stage + "-reject-home-without-contexts", [
            tools["rustc"]["path"], *COMMON, *flags, *extra,
            "--extern", "filesystem_metadata=" + str(folder / "libfilesystem_metadata.rlib"),
            "--crate-type=lib", S / "owner.rs", "-o", folder / "invalid.rlib",
        ], expected=1)
        if b"fs_home requires fs_directory_contexts" not in rejected.stderr:
            raise RuntimeError("missing home prerequisite rejection")

    layout = work / "layout.rs"
    layout.write_text('''#![cfg_attr(target_os = "none", no_std)]
struct Provider;
struct Time;
macro_rules! provider {
    ($module:ident) => {
        impl $module::Backend for Provider {
            fn root(&mut self) -> Result<$module::Node, $module::Error> { Err($module::Error::Closed) }
            fn lookup(&mut self, _: $module::Node, _: &[u8]) -> Result<$module::Node, $module::Error> { Err($module::Error::Closed) }
            fn read(&mut self, _: $module::Node, _: u64, _: &mut [u8]) -> Result<usize, $module::Error> { Err($module::Error::Closed) }
            fn write(&mut self, _: $module::Node, _: u64, _: &[u8], _: $module::Utc) -> Result<$module::Completion, $module::Lost> { Err($module::Lost) }
            fn mutate(&mut self, _: $module::Node, _: $module::Namespace<'_>, _: $module::Utc) -> Result<$module::Completion, $module::Lost> { Err($module::Lost) }
        }
        impl $module::Clock for Time {
            fn utc(&mut self) -> Result<$module::Utc, $module::Error> { Err($module::Error::Clock) }
        }
    };
}
provider!(home);
provider!(af08);
type Before = af08::Owner<Provider, Time>;
type After = home::Owner<Provider, Time>;
const _: () = assert!(core::mem::size_of::<Before>() == core::mem::size_of::<After>());
const _: () = assert!(core::mem::align_of::<Before>() == core::mem::align_of::<After>());
#[cfg(not(target_os = "none"))]
fn main() { println!("{} {} {} {}", core::mem::size_of::<Before>(), core::mem::size_of::<After>(), core::mem::align_of::<Before>(), core::mem::align_of::<After>()); }
''')
    for stage, extra in (("host", []), ("native", NATIVE)):
        folder = work / stage
        run(stage + "-layout-build", [
            tools["rustc"]["path"], *COMMON, *extra,
            "-Ldependency=" + str(folder), "--extern", "home=" + str(folder / "libhome.rlib"),
            "--extern", "af08=" + str(folder / "libaf08.rlib"), layout,
            *(["--crate-type=lib"] if extra else []), "-o", folder / "layout",
        ])
    values = list(map(int, run("host-layout", [host / "layout"]).stdout.split()))
    if len(values) != 4 or values[0] != values[1] or values[2] != values[3]:
        raise RuntimeError("Owner layout changed")
    record["owner_layout"] = {"before_after_size_alignment": values,
                              "target_equality": True, "whole_executable_fit": "not-tested"}
    record["semantic_controls"] = []
    controls = [
        ("source-rights", " || !home.rights.contains(home_rights)", "",
         "every_missing_source_right_rejects_without_publication"),
        ("root-rights", "let root_rights = Rights::new(3)?;",
         "let root_rights = Rights::new(15)?;",
         "provision_derives_exact_home_without_backend_work_or_metadata_authority"),
        ("home-identity", "            node: home.node,", "            node: self.root,",
         "provision_derives_exact_home_without_backend_work_or_metadata_authority"),
        ("serial-reservation", "let serial = self.issue(3)?;", "let serial = self.issue(3).unwrap_or(1);",
         "three_serial_reservation_never_wraps_or_partially_publishes"),
        ("two-handle-reservation", "let home_slot = free.next().ok_or(Error::Full)?;",
         "let home_slot = free.next().unwrap_or(root_slot);",
         "fewer_than_two_handle_slots_never_partially_publish"),
    ]
    original = (S / "home-policy.rs").read_text()
    for label, before, after, test in controls:
        if original.count(before) != 1:
            raise RuntimeError(label + " control anchor is not unique")
        folder = work / label
        folder.mkdir()
        for name in [*SOURCE_NAMES, "home-policy.rs"]:
            shutil.copy2(S / name, folder / name)
        mutated = folder / "home-policy.rs"
        mutated.write_text(original.replace(before, after, 1))
        rust("rustc", label + "-build", folder / "owner.rs", host, cfg(True),
             ["--test", "-o", folder / "tests"])
        name = "home_tests::" + test
        rejected = run(label + "-reject", [folder / "tests", "--exact", name, "--nocapture"],
                       expected=101, timeout=15)
        if (b"1 failed" not in rejected.stdout or name.encode() not in rejected.stdout
                or b"assertion" not in rejected.stderr):
            raise RuntimeError(label + " did not produce the named semantic rejection")
        record["semantic_controls"].append({
            "label": label, "test": name, "original_sha256": sha(S / "home-policy.rs"),
            "mutated_sha256": sha(mutated), "before": before, "after": after,
        })


def main():
    parser = Parser(description=__doc__, epilog=(
        "Example: python3 -B experiments/filesystem-service/check-home.py. "
        "No guest, native transport, or whole-owner fit is tested. Missing pinned "
        "tools/inputs exit 2; restore the named pinned prerequisite before retrying. "
        "Operational failure exits 1; inspect the compact report before retrying. "
        "Interrupted checks exit 1 after owned cleanup. Results schema "
        "aether-home-check-v1 has status, report (path or null), and cleanup."
    ))
    parser.add_argument("--version", action="version", version="aether-home-check 1")
    parser.parse_args()
    record = {"schema": "aether-home-evidence-v1", "status": "incomplete", "rows": [],
              "started_utc": now(), "commands": [sys.executable, *sys.argv],
              "python": sys.version, "host": platform.platform(), "native_executed": False,
              "scope": "owner policy host tests and no_std libraries only", "cleanup": "not-created",
              "suite_deadline_seconds": 300}
    work = None
    report = None
    frozen = {}
    exit_code = 1
    try:
        verify(PINS, PINS_SHA)
        verify(HELPER, HELPER_SHA)
        pins = json.loads(PINS.read_text())
        tools = {name: pins["tools"][name] for name in ("rustc", "rustfmt", "clippy-driver")}
        for tool in tools.values():
            verify(tool["path"], tool["sha256"])
        for name, digest in pins["rust_native_libraries"].items():
            verify(name, digest)
        paths = [S / name for name in SOURCE_NAMES]
        if (S / "home-policy.rs").exists():
            paths.append(S / "home-policy.rs")
        paths += [Path(__file__).resolve(), PINS, HELPER]
        try:
            frozen = {str(path): sha(path) for path in paths}
        except OSError as error:
            raise PreconditionError("required source unavailable: " + str(error.filename)) from error
        record.update(sources=frozen, tools=tools, rust_native_libraries=pins["rust_native_libraries"],
                      interpreter={"path": sys.executable, "sha256": sha(sys.executable)})
        if not (R / "build").is_dir():
            raise PreconditionError("required private output parent unavailable: " + str(R / "build"))
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        index = 1
        while (EVIDENCE / ("attempt-" + str(index).zfill(2) + ".json")).exists():
            index += 1
        report = EVIDENCE / ("attempt-" + str(index).zfill(2) + ".json")
        work = Path(tempfile.mkdtemp(prefix="filesystem-home-", dir=R / "build"))
        record["work"] = str(work)
        proc = types.ModuleType("owned")
        exec(compile(HELPER.read_bytes(), str(HELPER), "exec"), proc.__dict__)
        check(record, work, proc, tools)
        record["status"] = "pass"
        exit_code = 0
    except PreconditionError as error:
        record.update(status="blocked", error=str(error))
        exit_code = 2
    except (Exception, KeyboardInterrupt) as error:
        record.update(status="failed", error=type(error).__name__ + ": " + str(error))
    finally:
        if frozen:
            try:
                for path, digest in frozen.items():
                    verify(path, digest)
                for tool in record["tools"].values():
                    verify(tool["path"], tool["sha256"])
                for path, digest in record["rust_native_libraries"].items():
                    verify(path, digest)
                record["final_input_verification"] = "pass"
            except (PreconditionError, KeyError) as error:
                record.update(status="failed", final_input_verification=str(error))
                exit_code = 1
        if work is not None:
            try:
                shutil.rmtree(work)
                record["cleanup"] = "complete"
            except OSError as error:
                record.update(status="failed", cleanup="failed", cleanup_error=str(error))
                exit_code = 1
        record["ended_utc"] = now()
        if report is not None:
            report.write_text(json.dumps(record, indent=2, ensure_ascii=True) + "\n")
        if record["status"] != "pass":
            print("[" + ("BLOCKED" if exit_code == 2 else "FAILED") + "] "
                  + ascii(record.get("error", record.get("final_input_verification", "cleanup failed")))[1:-1], file=sys.stderr)
        print(json.dumps({"schema": "aether-home-check-v1", "status": record["status"],
                          "report": str(report) if report is not None else None,
                          "cleanup": record["cleanup"]}, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
