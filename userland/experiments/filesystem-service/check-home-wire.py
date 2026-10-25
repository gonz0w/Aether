# SPDX-License-Identifier: BSD-2-Clause
"""Check two-grant service/client integration using pinned host tools and no_std builds."""
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
EVIDENCE = R / "docs/evidence/filesystem-home-wire-2026-10-24"
PINS = R / "docs/evidence/filesystem-transport-2026-10-19/inputs.json"
PINS_SHA = "f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d"
HELPER = R / "experiments/command-runner/process.py"
HELPER_SHA = "9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e"
PROFILE = (
    "namespace", "lifetimes", "mixed", "wait", "bulk", "runtime",
    "activation", "names", "directories", "metadata", "directory_contexts",
)
SOURCE_NAMES = tuple(p.name for p in S.glob("*.rs"))

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


def require(condition, message):
    # Qualification oracles must remain active under python -O/PYTHONOPTIMIZE.
    if not condition:
        raise RuntimeError(str(message))


def check(record, work, proc, tools, deadline=None):
    env = proc.clean_env(work)
    env["DYLD_LIBRARY_PATH"] = str(Path(tools["rustc"]["path"]).parent.parent / "lib")
    if deadline is None:
        deadline = time.monotonic() + 300

    def run(label, argv, expected=0, timeout=60):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError("suite deadline before " + label)
        result = proc.run(list(map(str, argv)), cwd=R, env=env, work=work,
                          label=label, timeout=min(timeout, remaining))
        row = {"label": label, "expected_exit": expected, "process": result.record,
               "stdout": result.stdout.decode(errors="replace")[-7000:],
               "stderr": result.stderr.decode(errors="replace")[-5000:]}
        record["rows"].append(row)
        if result.returncode != expected or not result.record["complete"] or result.record["cleanup"] != "complete":
            raise RuntimeError(label)
        return result

    def deps(folder, names):
        return ["-Ldependency=" + str(folder), *[v for name in names for v in
                ("--extern", name + "=" + str(folder / ("lib" + name + ".rlib")))]]

    crates = [("filesystem_metadata", "metadata-lib.rs", []),
              ("filesystem_policy", "owner.rs", ["filesystem_metadata"]),
              ("filesystem_service", "service.rs", ["filesystem_policy"]),
              ("filesystem_client", "client.rs", ["filesystem_service"])]
    selected = [*cfg(True), "--cfg", "fs_home_wire"]
    libraries = {}
    def build(folder, flags, extra=(), sources=S, include_client=True):
        folder.mkdir(exist_ok=True)
        for name, source, imports in (crates if include_client else crates[:3]):
            common = [f for f in COMMON if name != "filesystem_metadata" or f != "-Funsafe-code"]
            run(folder.name + "-" + name, [tools["rustc"]["path"], *common, *flags, *extra,
                *deps(folder, imports), "--crate-type=lib", "--crate-name=" + name, "-Cmetadata=" + folder.name,
                sources / source, "-o", folder / ("lib" + name + ".rlib")])
            libraries[folder.name + ":" + name] = sha(folder / ("lib" + name + ".rlib"))

    host = work / "home-host"
    build(host, selected)
    imports = [name for name, _, _ in crates]
    for compiler in ("rustc", "clippy-driver"):
        run(compiler + "-home-wire-build", [tools[compiler]["path"], *COMMON, *selected,
            *deps(host, imports), "--test", S / "home-wire-tests.rs", "-o", work / (compiler + "-tests")])
    result = run("home-wire-tests", [work / "rustc-tests", "--test-threads=1"], timeout=30)
    require(b"8 passed; 0 failed" in result.stdout, 'oracle failed at checker line 122')
    record["home_wire_tests"] = 8
    run("rustfmt", [tools["rustfmt"]["path"], "--edition=2021", "--check", *[S / n for n in
        ("service.rs", "names-service.rs", "home-service.rs", "client.rs", "home-client.rs", "home-wire-tests.rs", "activation.rs", "remote-descriptors.rs")]])
    build(work / "home-native", selected, NATIVE)
    for stage, extra in (("host", []), ("native", NATIVE)):
        folder = work / ("home-" + stage)
        for name, source, imports_ in crates[1:]:
            run(stage + "-clippy-" + name, [tools["clippy-driver"]["path"], *COMMON, *selected, *extra,
                *deps(folder, imports_), "--crate-type=lib", "--crate-name=" + name,
                S / source, "-o", work / (stage + name + "-clippy.rlib")])
    for profile, flags in (("af08", cfg()), ("af07", [v for v in cfg() if v != "fs_directory_contexts"])):
        if profile == "af07":
            flags = [v for i,v in enumerate(cfg()) if v != "fs_directory_contexts" and not (v == "--cfg" and i + 1 < len(cfg()) and cfg()[i+1] == "fs_directory_contexts")]
        folder = work / profile
        build(folder, flags)
        build(work / (profile + "-native"), flags, NATIVE)
        for name, source, imports_ in (crates[1], crates[3]):
            run(profile + "-" + name + "-test-build", [tools["rustc"]["path"], *COMMON, *flags,
                *deps(folder, [*imports_, "filesystem_policy"]), "--test", S / source,
                "-o", work / (profile + name)])
            result = run(profile + "-" + name + "-tests", [work / (profile + name), "--test-threads=1"], timeout=30)
            require(b"test result: ok." in result.stdout and b"0 failed" in result.stdout, 'oracle failed at checker line 144')
    def without(flags, names):
        return [value for i, value in enumerate(flags) if value not in names and not
                (value == "--cfg" and i + 1 < len(flags) and flags[i + 1] in names)]
    # The extracted names loop also supplies unchanged AF05/06 consumers.
    for label, omitted in (("af05", {"fs_directory_contexts", "fs_metadata", "fs_directories"}),
                            ("af06", {"fs_directory_contexts", "fs_metadata"})):
        for stage, extra in (("host", []), ("native", NATIVE)):
            build(work / (label + "-" + stage), without(cfg(), omitted), extra)
    for label, flags in (("af08", cfg()), ("af07", without(cfg(), {"fs_directory_contexts"}))):
        for stage, extra in (("host", []), ("native", NATIVE)):
            folder = work / (label + ("-native" if extra else ""))
            for name, source, imports_ in (("remote", "remote-descriptors.rs", ["filesystem_client", "filesystem_service"]),
                                            ("activation", "activation.rs", ["filesystem_policy", "filesystem_service"])):
                run(label + "-" + stage + "-old-" + name, [tools["rustc"]["path"], *COMMON, *flags, *extra,
                    *deps(folder, imports_), "--crate-type=lib", S / source, "-o", work / (label + stage + name + ".rlib")])
    legacy = work / "legacy"
    build(legacy, [])
    for name, source, imports_ in crates[1:3]:
        run("legacy-" + name + "-build", [tools["rustc"]["path"], *COMMON,
            *deps(legacy, imports_), "--test", S / source, "-o", work / name])
        run("legacy-" + name + "-tests", [work / name, "--test-threads=1"], timeout=30)
    # Preserve the exact immutable producer used by the old client checker.
    delivery = R / "build/service-deliveries/filesystem-service-metadata-2026-10-21-v1"
    verify(delivery / "SHA256SUMS", "98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8")
    for line in (delivery / "SHA256SUMS").read_text().splitlines():
        digest, member = line.split(maxsplit=1)
        verify(delivery / member, digest)
        record["sources"][str(delivery / member)] = digest
    record["sources"][str(delivery / "SHA256SUMS")] = sha(delivery / "SHA256SUMS")
    old_flags = [v for i,v in enumerate(cfg()) if v != "fs_directory_contexts" and not (v == "--cfg" and i + 1 < len(cfg()) and cfg()[i+1] == "fs_directory_contexts")]
    for stage, extra in (("host", []), ("native", NATIVE)):
        folder = work / ("sealed-" + stage)
        build(folder, old_flags, extra, delivery / "source", include_client=False)
        run("sealed-" + stage + "-current-client", [tools["rustc"]["path"], *COMMON, *old_flags, *extra,
            *deps(folder, ["filesystem_service"]), "--crate-type=lib", "--crate-name=filesystem_client",
            S / "client.rs", "-o", folder / "libfilesystem_client.rlib"])
        if stage == "host":
            run("sealed-current-client-tests-build", [tools["rustc"]["path"], *COMMON, *old_flags,
                *deps(folder, ["filesystem_policy", "filesystem_service"]), "--test", S / "client.rs", "-o", folder / "tests"])
            result = run("sealed-current-client-tests", [folder / "tests", "--test-threads=1"], timeout=30)
            require(b"13 passed; 0 failed" in result.stdout, 'oracle failed at checker line 185')
    # Old consumers and opposite client selection must fail before runtime.
    for stage, extra in (("host", []), ("native", NATIVE)):
        folder = work / ("home-" + stage)
        for name, source, imports_ in (("remote", "remote-descriptors.rs", ["filesystem_client", "filesystem_service"]),
                                        ("activation", "activation.rs", ["filesystem_policy", "filesystem_service"])):
            rejected = run(stage + "-reject-" + name, [tools["rustc"]["path"], *COMMON, *selected, *extra,
                *deps(folder, imports_), "--crate-type=lib", S / source, "-o", work / (stage + name + ".rlib")], expected=1)
            require(b"home service requires a separately integrated consumer" in rejected.stderr, 'oracle failed at checker line 193')
        rejected = run(stage + "-reject-old-client", [tools["rustc"]["path"], *COMMON, *cfg(), *extra,
            *deps(folder, ["filesystem_service"]), "--crate-type=lib", S / "client.rs", "-o", work / (stage + "old.rlib")], expected=1)
        require(b"home client/service selection mismatch" in rejected.stderr, 'oracle failed at checker line 196')
        old_folder = work / ("af08" + ("-native" if extra else ""))
        rejected = run(stage + "-reject-home-client-old-service", [tools["rustc"]["path"], *COMMON, *selected, *extra,
            *deps(old_folder, ["filesystem_service"]), "--crate-type=lib", S / "client.rs", "-o", work / (stage + "new.rlib")], expected=1)
        require(b"home client/service selection mismatch" in rejected.stderr, 'oracle failed at checker line 200')
        rejected = run(stage + "-reject-service-without-home", [tools["rustc"]["path"], *COMMON,
            *without(selected, {"fs_home"}), *extra, *deps(folder, ["filesystem_policy"]),
            "--crate-type=lib", S / "service.rs", "-o", work / (stage + "incomplete.rlib")], expected=1)
        require(b"fs_home_wire requires fs_home" in rejected.stderr, 'oracle failed at checker line 204')
        absent = work / "old-entry.rs"
        absent.write_text("#![no_std]\npub use filesystem_service::run;\n")
        rejected = run(stage + "-reject-old-service-entry", [tools["rustc"]["path"], *COMMON, *extra,
            *deps(folder, ["filesystem_service"]), "--crate-type=lib", absent, "-o", work / (stage + "entry.rlib")], expected=1)
        require(b"unresolved import" in rejected.stderr and b"::run" in rejected.stderr, 'oracle failed at checker line 209')
    layout = work / "layout.rs"
    layout.write_text('''#![cfg_attr(target_os="none",no_std)]
macro_rules! channel { ($module:ident,$name:ident) => {
struct $name;
impl $module::Channel for $name {
fn receive(&mut self,_:&mut $module::Message)->Result<(),i64>{Err(-5)}
fn send(&mut self,_:&$module::Message)->Result<(),i64>{Err(-5)}
fn close(&mut self)->[i64;2]{[0;2]}
}};}
channel!(new_service,New);
channel!(old_service,Old);
const _:()=assert!(core::mem::size_of::<new_client::Client<New>>()==core::mem::size_of::<old_client::Client<Old>>());
const _:()=assert!(core::mem::align_of::<new_client::Client<New>>()==core::mem::align_of::<old_client::Client<Old>>());
#[cfg(not(target_os="none"))]
fn main(){println!("{} {}",core::mem::size_of::<new_client::Client<New>>(),core::mem::align_of::<new_client::Client<New>>());}
''')
    for stage, extra in (("host", []), ("native", NATIVE)):
        new = work / ("home-" + stage)
        old = work / ("af08" + ("-native" if extra else ""))
        args = ["-Ldependency=" + str(new), "-Ldependency=" + str(old)]
        for alias, folder, name in (("new_service",new,"service"),("new_client",new,"client"),("old_service",old,"service"),("old_client",old,"client")):
            args += ["--extern", alias + "=" + str(folder / ("libfilesystem_" + name + ".rlib"))]
        run(stage + "-layout-build", [tools["rustc"]["path"], *COMMON, *extra, *args,
            *(["--crate-type=lib"] if extra else []), layout, "-o", work / (stage + "-layout")])
    values = list(map(int, run("host-layout", [work / "host-layout"]).stdout.split()))
    record["client_layout"] = {"size_alignment": values, "host_target_equal_to_af08": True, "whole_executable_fit": False}
    controls = [
        ("home-type", "home-client.rs", "if home.kind != Kind::Directory", "if false", "malformed_or_lost_either_greeting_never_publishes_or_sends", "HOME_GREETING_VALIDATION"),
        ("home-token", "home-client.rs", "self.entry(&second, 2)?", "self.entry(&second, word(&second, 3))?", "malformed_or_lost_either_greeting_never_publishes_or_sends", "HOME_GREETING_VALIDATION"),
        ("early-ready", "names-service.rs", "return Stop::ReplyLost(code);\n            }\n        }\n        ready = true;", "ready = true;\n                return Stop::ReplyLost(code);\n            }\n        }\n        ready = true;", "each_service_greeting_loss_stops_before_ready_or_dispatch", "HOME_READY_AFTER_BOTH"),
        ("root-rights", "home-policy.rs", "let root_rights = Rights::new(3)?;", "let root_rights = Rights::new(15)?;", "raw_home_mutations_work_but_system_and_read_aliases_are_denied", "SYSTEM_MUTATION"),
    ]
    controls += [
        ("home-binding", "home-service.rs", "handle: delegated.home.handle", "handle: delegated.root.handle", "raw_home_mutations_work_but_system_and_read_aliases_are_denied", "HOME_MUTATION_ACK"),
        ("next-token", "home-service.rs", "next: 3", "next: 2", "raw_home_mutations_work_but_system_and_read_aliases_are_denied", "HOME_TOKEN_AFTER_TWO"),
    ]
    record["semantic_controls"] = []
    for label, filename, before, after, test, marker in controls:
        source = (S / filename).read_text()
        require(source.count(before) == 1, label)
        folder = work / label
        sources = folder / "source"
        sources.mkdir(parents=True)
        for path in S.glob("*.rs"):
            shutil.copy2(path, sources / path.name)
        (sources / filename).write_text(source.replace(before, after, 1))
        build(folder, selected, sources=sources)
        run(label + "-tests-build", [tools["rustc"]["path"], *COMMON, *selected,
            *deps(folder, imports), "--test", sources / "home-wire-tests.rs", "-o", folder / "tests"])
        result = run(label + "-reject", [folder / "tests", "--exact", test, "--nocapture"], expected=101, timeout=15)
        require(b"1 failed" in result.stdout and marker.encode() in result.stderr and test.encode() in result.stdout, 'oracle failed at checker line 260')
        record["semantic_controls"].append({"label": label, "test": test, "before": before, "after": after, "required_marker": marker})
    record["libraries"] = libraries

def main(check_function=check, *, program="aether-home-wire-check", evidence=EVIDENCE,
         description=__doc__, example="python3 -B experiments/filesystem-service/check-home-wire.py",
         scope="two-grant service/client host interoperability and no_std libraries only", extra_sources=(),
         limitations="No guest, native transport, or whole-owner fit is tested."):
    parser = Parser(description=description, epilog=(
        "Example: " + example + ". "
        + limitations + " Missing pinned "
        "tools/inputs exit 2; restore the named pinned prerequisite before retrying. "
        "Operational failure exits 1; inspect the compact report before retrying. "
        "Interrupted checks exit 1 after owned cleanup. Results schema "
        + program + "-v1 has status, report (path or null), and cleanup."
    ))
    parser.add_argument("--version", action="version", version=program + " 1")
    parser.parse_args()
    record = {"schema": program.removesuffix("-check") + "-evidence-v1", "status": "incomplete", "rows": [],
              "started_utc": now(), "commands": [sys.executable, *sys.argv],
              "python": sys.version, "host": platform.platform(), "native_executed": False,
              "scope": scope, "cleanup": "not-created", "python_optimization": sys.flags.optimize,
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
        paths += [Path(__file__).resolve(), PINS, HELPER, *extra_sources]
        try:
            frozen = {str(path): sha(path) for path in paths}
        except OSError as error:
            raise PreconditionError("required source unavailable: " + str(error.filename)) from error
        record.update(sources=frozen, tools=tools, rust_native_libraries=pins["rust_native_libraries"],
                      interpreter={"path": sys.executable, "sha256": sha(sys.executable)})
        if not (R / "build").is_dir():
            raise PreconditionError("required private output parent unavailable: " + str(R / "build"))
        evidence.mkdir(parents=True, exist_ok=True)
        index = 1
        while (evidence / ("attempt-" + str(index).zfill(2) + ".json")).exists():
            index += 1
        report = evidence / ("attempt-" + str(index).zfill(2) + ".json")
        work = Path(tempfile.mkdtemp(prefix="filesystem-home-", dir=R / "build"))
        record["work"] = str(work)
        proc = types.ModuleType("owned")
        exec(compile(HELPER.read_bytes(), str(HELPER), "exec"), proc.__dict__)
        check_function(record, work, proc, tools)
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
        print(json.dumps({"schema": program + "-v1", "status": record["status"],
                          "report": str(report) if report is not None else None,
                          "cleanup": record["cleanup"]}, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
