# SPDX-License-Identifier: BSD-2-Clause
"""Check AF09 shared process writes using pinned offline host tools."""
from pathlib import Path
import runpy
import shutil
import sys
import time

SOURCE = Path(__file__).resolve()
S = SOURCE.parent
mutation_source = S / "check-client-mutations.py"
mutation = runpy.run_path(str(mutation_source))
runner = mutation["runner"]
require = runner["require"]
COMMON = runner["COMMON"]
NATIVE = runner["NATIVE"]


def check(record, work, proc, tools, deadline=None):
    if deadline is None:
        deadline = time.monotonic() + 300
    env = proc.clean_env(work)
    env["DYLD_LIBRARY_PATH"] = str(Path(tools["rustc"]["path"]).parent.parent / "lib")
    flags = [*runner["cfg"](True), "--cfg", "fs_home_wire"]
    flags += [v for name in ("paths", "file16", "replace", "process_views", "process_writes")
              for v in ("--cfg", "fs_" + name)]
    crates = [("filesystem_metadata", "metadata-lib.rs", []),
              ("filesystem_policy", "owner.rs", ["filesystem_metadata"]),
              ("filesystem_service", "service.rs", ["filesystem_policy"]),
              ("filesystem_client", "client.rs", ["filesystem_service"]),
              ("filesystem_remote_descriptors", "remote-descriptors.rs", ["filesystem_client", "filesystem_service"])]

    def run(label, argv, expected=0, timeout=60):
        remaining = deadline - time.monotonic()
        require(remaining > 0, "suite deadline before " + label)
        r = proc.run(list(map(str, argv)), cwd=runner["R"], env=env, work=work,
                     label=label, timeout=min(remaining, timeout))
        record["rows"].append({"label": label, "expected_exit": expected, "process": r.record,
            "stdout": r.stdout.decode(errors="replace")[-7000:],
            "stderr": r.stderr.decode(errors="replace")[-5000:]})
        require(r.returncode == expected and r.record["complete"] and r.record["cleanup"] == "complete", label)
        return r

    def deps(folder, names):
        return ["-Ldependency=" + str(folder), *[v for name in names for v in
            ("--extern", name + "=" + str(folder / ("lib" + name + ".rlib")))]]

    def build(folder, extra=(), lint=False, selected=flags, sources=S):
        folder.mkdir(exist_ok=True)
        for name, source, imports in crates:
            common = [v for v in COMMON if name != "filesystem_metadata" or v != "-Funsafe-code"]
            run(folder.name + "-" + name + ("-clippy" if lint else ""),
                [tools["clippy-driver" if lint else "rustc"]["path"], *common, *selected, *extra,
                 *deps(folder, imports), "--crate-type=lib", "--crate-name=" + name,
                 "-Cmetadata=" + folder.name, sources / source, "-o", folder / ("lib" + name + ".rlib")])

    imports = [name for name, _, _ in crates]
    runner["verify"](S / "vendor/abi29-startup.rs", "ba23cba7730e8c10c7f0ea0ccf68a227b71ac70890a72c475ff892d13136e704")
    host = work / "process-write-host"
    build(host)
    for compiler in ("rustc", "clippy-driver"):
        run("process-write-" + compiler + "-test-build", [tools[compiler]["path"], *COMMON, *flags,
            *deps(host, imports), "--test", S / "home-wire-tests.rs", "-o", work / ("process-write-" + compiler)])
    r = run("process-write-tests", [work / "process-write-rustc", "--test-threads=1"], timeout=30)
    require(b"20 passed; 0 failed" in r.stdout, "twelve process-write and eight AF09 binding cases")
    record["process_write_tests"] = 12
    for stage, extra in (("host", []), ("native", NATIVE)):
        folder = work / ("process-write-" + stage)
        if extra:
            build(folder, extra=extra)
        build(folder, extra=extra, lint=True)
    run("process-write-rustfmt", [tools["rustfmt"]["path"], "--edition=2021", "--check",
        *[S / n for n in ("process-writes.rs", "process-write-tests.rs", "process-descriptors.rs",
                          "file-descriptions.rs", "remote-descriptors.rs", "fd-protocol.rs", "home-wire-tests.rs")]])
    # Cumulative deadline applies across both earlier finite contract suites.
    mutation["check"](record, work, proc, tools, deadline=deadline)
    def without(selected, names):
        return [v for i, v in enumerate(selected) if v not in names and not
                (v == "--cfg" and i + 1 < len(selected) and selected[i + 1] in names)]

    old_base = without(runner["cfg"](), {"fs_directory_contexts"})
    old_base += [v for name in ("paths", "process_views") for v in ("--cfg", "fs_" + name)]
    old_sets = (("old13", old_base), ("old16", [*old_base, "--cfg", "fs_file16", "--cfg", "fs_replace"]))
    for label, selected in old_sets:
        for stage, extra in (("host", []), ("native", NATIVE)):
            folder = work / (label + "-" + stage)
            build(folder, extra=extra, selected=selected)
            if not extra:
                run(label + "-tests-build", [tools["rustc"]["path"], *COMMON, *selected,
                    *deps(folder, imports[:-1]), "--test", S / "remote-descriptors.rs", "-o", folder / "tests"])
                result = run(label + "-tests", [folder / "tests", "--test-threads=1"], timeout=30)
                require(b"test result: ok." in result.stdout and b"0 failed" in result.stdout,
                        "old process tests executed")
            # Actual current path/dup2 FILE consumer still compiles against old selections.
            wire = [*selected, "--cfg", "fs_path_wire", *(["--cfg", "fs_dup2_wire"] if label == "old16" else [])]
            run(label + stage + "-FILE-consumer", [tools["rustc"]["path"], *COMMON, *wire, *extra,
                *deps(folder, ["filesystem_client", "filesystem_service", "filesystem_remote_descriptors"]),
                "--crate-type=lib", S / "fd-protocol.rs", "-o", folder / "libwire.rlib"])
    for stage, extra in (("host", []), ("native", NATIVE)):
        folder = work / ("process-write-" + stage)
        for label, wire in (("component", []), ("paths", ["--cfg", "fs_path_wire"]),
                            ("dup2", ["--cfg", "fs_path_wire", "--cfg", "fs_dup2_wire"]),
                            ("cwd", ["--cfg", "fs_path_wire", "--cfg", "fs_dup2_wire", "--cfg", "fs_cwd_wire"])):
            rejected = run(stage + label + "-FILE-refuses-writes", [tools["rustc"]["path"], *COMMON, *flags, *wire, *extra,
                *deps(folder, ["filesystem_client", "filesystem_service", "filesystem_remote_descriptors"]),
                "--crate-type=lib", S / "fd-protocol.rs", "-o", folder / "absent.rlib"], expected=1)
            require(b"FILE writes require a separately integrated contract" in rejected.stderr,
                    "FILE refuses the write broker before adoption")
        for omitted in ("fs_process_writes", "fs_paths", "fs_file16", "fs_replace", "fs_process_views", "fs_home_wire"):
            selected = without(flags, {omitted})
            rejected = run(stage + "-missing-" + omitted, [tools["rustc"]["path"], *COMMON, *selected, *extra,
                *deps(folder, ["filesystem_client", "filesystem_service"]), "--crate-type=lib",
                S / "remote-descriptors.rs", "-o", folder / "absent.rlib"], expected=1)
            marker = b"home service requires a separately integrated consumer" if omitted == "fs_process_writes" else b"process writes require matched AF09"
            require(marker in rejected.stderr, "explicit missing profile rejection")
        for forbidden in ("fs_cwd", "fs_in_place"):
            rejected = run(stage + "-forbidden-" + forbidden, [tools["rustc"]["path"], *COMMON, *flags, "--cfg", forbidden, *extra,
                *deps(folder, ["filesystem_client", "filesystem_service"]), "--crate-type=lib",
                S / "remote-descriptors.rs", "-o", folder / "absent.rlib"], expected=1)
            require(b"process writes require matched AF09" in rejected.stderr, "explicit forbidden profile rejection")
        old = work / ("old16-" + stage)
        rejected = run(stage + "-reject-old-service", [tools["rustc"]["path"], *COMMON, *flags, *extra,
            *deps(old, ["filesystem_client", "filesystem_service"]), "--crate-type=lib",
            S / "remote-descriptors.rs", "-o", old / "absent.rlib"], expected=1)
        require(b"process writes require matched AF09 service" in rejected.stderr, "old service profile rejection")

    # Compare the real monomorphized type layout against the same16-alias AF07 broker.
    layout = work / "process-write-layout.rs"
    layout.write_text("""#![cfg_attr(target_os="none", no_std)]
extern crate filesystem_remote_descriptors as new;
extern crate old_remote as old;
extern crate filesystem_service as ns;
extern crate old_service as os;
struct New; struct Old;
impl ns::Channel for New {
 fn send(&mut self,_:&ns::Message)->Result<(),i64>{Err(-5)}
 fn receive(&mut self,_:&mut ns::Message)->Result<(),i64>{Err(-5)}
 fn close(&mut self)->[i64;2]{[0;2]}
}
impl os::Channel for Old {
 fn send(&mut self,_:&os::Message)->Result<(),i64>{Err(-5)}
 fn receive(&mut self,_:&mut os::Message)->Result<(),i64>{Err(-5)}
 fn close(&mut self)->[i64;2]{[0;2]}
}
const _: ()=assert!(core::mem::size_of::<new::ProcessFiles<New>>()==core::mem::size_of::<old::ProcessFiles<Old>>());
const _: ()=assert!(core::mem::align_of::<new::ProcessFiles<New>>()==core::mem::align_of::<old::ProcessFiles<Old>>());
#[cfg(not(target_os="none"))]
fn main(){println!("{} {}",core::mem::size_of::<new::ProcessFiles<New>>(),core::mem::align_of::<new::ProcessFiles<New>>());}
""")
    for stage, extra in (("host", []), ("native", NATIVE)):
        new = work / ("process-write-" + stage)
        old = work / ("old16-" + stage)
        run(stage + "-process-layout-build", [tools["rustc"]["path"], *COMMON, *extra,
            *deps(new, ["filesystem_service", "filesystem_remote_descriptors"]), "-Ldependency=" + str(old),
            "--extern", "old_remote=" + str(old / "libfilesystem_remote_descriptors.rlib"),
            "--extern", "old_service=" + str(old / "libfilesystem_service.rlib"),
            *(["--crate-type=lib"] if extra else []), layout, "-o", work / (stage + "-process-layout")])
    result = run("host-process-layout", [work / "host-process-layout"])
    record["process_layout"] = {"size_alignment": list(map(int, result.stdout.split())),
        "host_target_equal_to_old16": True, "whole_executable_fit": False}

    controls = [
        ("home-binding", "process-writes.rs", "source.client.home()?", "source.client.root()?", "actual_shared_alias_inheritance_and_independent_positions", "PROCESS_HOME_BINDING"),
        ("offset", "process-writes.rs", "file.offset + completion.bytes as u64", "file.offset", "actual_shared_alias_inheritance_and_independent_positions", "PROCESS_WRITE_OFFSET"),
        ("retirement", "process-writes.rs", "self.files.retire();", "let _ = ();", "all_remote_progress_and_attempted_offsets_survive_retirement_and_drop", "PROCESS_WRITE_RETIRE"),
        ("progress", "process-writes.rs", "outcome: failure.outcome", "outcome: MutationOutcome::Unknown", "all_remote_progress_and_attempted_offsets_survive_retirement_and_drop", "PROCESS_WRITE_PROGRESS"),
        ("attempt", "process-writes.rs", "offset: Some(file.offset)", "offset: None", "all_remote_progress_and_attempted_offsets_survive_retirement_and_drop", "PROCESS_WRITE_ATTEMPT"),
        ("exact-process", "process-descriptors.rs", "self.records[slot as usize - 1].process != Some(process)", "false && self.records[slot as usize - 1].process != Some(process)", "local_bounds_names_and_stale_process_never_send", "PROCESS_WRITE_EXACT_KEY"),
    ]
    record["process_write_controls"] = []
    for label, filename, before, after, test, marker in controls:
        original = (S / filename).read_text()
        require(original.count(before) == 1, "unique process control: " + label)
        folder = work / ("process-control-" + label)
        sources = folder / "source"
        sources.mkdir(parents=True)
        for path in S.glob("*.rs"):
            shutil.copy2(path, sources / path.name)
        (sources / "vendor").mkdir()
        shutil.copy2(S / "vendor/abi29-startup.rs", sources / "vendor/abi29-startup.rs")
        (sources / filename).write_text(original.replace(before, after, 1))
        build(folder, sources=sources)
        run(label + "-process-test-build", [tools["rustc"]["path"], *COMMON, *flags,
            *deps(folder, imports), "--test", sources / "home-wire-tests.rs", "-o", folder / "tests"])
        name = "process_writes::" + test
        rejected = run(label + "-process-reject", [folder / "tests", "--exact", name, "--nocapture"], expected=101, timeout=15)
        require(b"1 failed" in rejected.stdout and name.encode() in rejected.stdout and marker.encode() in rejected.stderr,
                "named process mutation rejection: " + label)
        record["process_write_controls"].append({"label": label, "file": filename, "test": name,
            "before": before, "after": after, "required_marker": marker,
            "mutated_sha256": runner["sha"](sources / filename)})


if __name__ == "__main__":
    sys.exit(runner["main"](check_function=check, program="aether-process-writes-check",
        evidence=runner["R"] / "docs/evidence/filesystem-process-writes-2026-10-24",
        description=__doc__, example="python3 -B experiments/filesystem-service/check-process-writes.py",
        scope="AF09 process descriptor writes, actual host service and no_std libraries only",
        extra_sources=(SOURCE, mutation_source, S / "vendor/abi29-startup.rs")))
