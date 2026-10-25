# SPDX-License-Identifier: BSD-2-Clause
"""Check versioned FILE/C mutation receipts using pinned offline host tools."""
import json
from pathlib import Path
import runpy
import shlex
import shutil
import sys
import time

SOURCE = Path(__file__).resolve()
S = SOURCE.parent
process_source = S / "check-process-writes.py"
process = runpy.run_path(str(process_source))
runner = process["runner"]
require = runner["require"]
COMMON = runner["COMMON"]
NATIVE = runner["NATIVE"]


def check(record, work, proc, tools, deadline=None):
    if deadline is None:
        deadline = time.monotonic() + 300
    env = proc.clean_env(work)
    env["DYLD_LIBRARY_PATH"] = str(Path(tools["rustc"]["path"]).parent.parent / "lib")
    pins = json.loads(runner["PINS"].read_text())
    for name in ("clang", "clang-format", "lld", "readelf", "nm"):
        runner["verify"](pins["tools"][name]["path"], pins["tools"][name]["sha256"])
        tools[name] = pins["tools"][name]
    for path, digest in pins["clang_resource_headers"].items():
        runner["verify"](path, digest)
        record["sources"][path] = digest
    ubsan = Path("/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib")
    digest = "7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746"
    runner["verify"](ubsan, digest)
    record["sources"][str(ubsan)] = digest
    cflags = ["-DAEFD_PATH_WIRE", "-DAEFD_DUP2_WIRE", "-DAEFD_WRITE_WIRE", "-std=c17", "-Wall", "-Wextra", "-Werror", "-Wconversion", "-Wsign-conversion"]

    def run(label, argv, expected=0, timeout=60):
        remaining = deadline - time.monotonic()
        require(remaining > 0, "suite deadline before " + label)
        child_env = dict(env)
        if str(argv[0]) in (*[tools[n]["path"] for n in ("clang", "clang-format", "lld", "readelf", "nm")], str(work / "file-write-C"), str(work / "old-file-C")):
            child_env.pop("DYLD_LIBRARY_PATH", None)
        result = proc.run(list(map(str, argv)), cwd=runner["R"], env=child_env, work=work,
                          label=label, timeout=min(timeout, remaining))
        record["rows"].append({"label": label, "expected_exit": expected, "process": result.record,
            "stdout": result.stdout.decode(errors="replace")[-7000:],
            "stderr": result.stderr.decode(errors="replace")[-5000:]})
        require(result.returncode == expected and result.record["complete"] and result.record["cleanup"] == "complete", label)
        return result

    # Freeze the union of actual dependencies for every translation unit/profile,
    # including legacy fixtures and private semantic controls, before compilation.
    record["c_header_closures"] = []
    def cbuild(label, selected, units, output):
        for index, unit in enumerate(units):
            scanned = run(label + "-headers-" + str(index), [tools["clang"]["path"], *[v for v in selected if v != "-c"], "-M", unit])
            names = shlex.split(scanned.stdout.decode().replace("\\\n", " ").split(":", 1)[1])
            closure = {}
            for name in names:
                path = Path(name)
                if not path.is_absolute():
                    path = runner["R"] / path
                digest = runner["sha"](path)
                previous = record["sources"].get(str(path))
                require(previous is None or previous == digest, "header changed before compile: " + str(path))
                record["sources"][str(path)] = digest
                closure[str(path)] = digest
            record["c_header_closures"].append({"label": label, "unit": str(unit), "headers": closure})
        return run(label, [tools["clang"]["path"], *selected, *units, "-o", output])
    fixtures = runner["R"] / "docs/evidence/filesystem-fd-client-2026-10-21/inputs"
    for name, digest in (("requests.bin", "92050730356810b5c659f6b7803ed5f95befcf93f2065e670dc8f3a9e20c1db8"),
                         ("replies.bin", "cb73e8a769273025e915cdc67a47955d70150775683c1e636d1531dde668a73c")):
        runner["verify"](fixtures / name, digest)
        record["sources"][str(fixtures / name)] = digest
    old_cflags = [v for v in cflags if not v.startswith("-DAEFD_")]
    cbuild("FILE-old-C-build", [*old_cflags, "-fsanitize=undefined", "-fno-sanitize-recover=all"],
        [S / "fd-client-tests.c", S / "fd-client.c"], work / "old-file-C")
    old = run("FILE-old-C-tests", [work / "old-file-C", fixtures / "requests.bin", fixtures / "replies.bin"], timeout=30)
    require(b"C client schedules pass" in old.stdout, "actual old C client cases executed")
    executable = work / "file-write-C"
    cbuild("FILE-C-build", [*cflags, "-fsanitize=undefined", "-fno-sanitize-recover=all"],
        [S / "fd-file-write-tests.c", S / "fd-client.c", S / "fd-facade.c"], executable)
    result = run("FILE-C-unit", [executable], timeout=30)
    require(b"FILE_C_UNIT_PASS" in result.stdout, "C semantic matrix executed")
    emitted = run("FILE-C-emit", [executable, "emit"])
    (work / "requests.bin").write_bytes(emitted.stdout)
    env["AEFW_REQUESTS"] = str(work / "requests.bin")
    env["AEFW_REPLIES"] = str(work / "replies.bin")
    env["AEFW_ERRORS"] = str(work / "errors.bin")
    env["AEFW_C_FIXTURE"] = str(executable)
    flags = [*runner["cfg"](True), "--cfg", "fs_home_wire"]
    flags += [v for n in ("paths", "file16", "replace", "process_views", "process_writes", "path_wire", "dup2_wire", "file_write_wire") for v in ("--cfg", "fs_" + n)]
    crates = [("filesystem_metadata", "metadata-lib.rs", []),
              ("filesystem_policy", "owner.rs", ["filesystem_metadata"]),
              ("filesystem_service", "service.rs", ["filesystem_policy"]),
              ("filesystem_client", "client.rs", ["filesystem_service"]),
              ("filesystem_remote_descriptors", "remote-descriptors.rs", ["filesystem_client", "filesystem_service"]),
              ("filesystem_fd_protocol", "fd-protocol.rs", ["filesystem_client", "filesystem_service", "filesystem_remote_descriptors"])]

    def deps(folder, names):
        return ["-Ldependency=" + str(folder), *[v for n in names for v in ("--extern", n + "=" + str(folder / ("lib" + n + ".rlib")))]]

    def build(folder, extra=(), lint=False, sources=S):
        folder.mkdir(exist_ok=True)
        for name, source, imports in crates:
            common = [v for v in COMMON if name != "filesystem_metadata" or v != "-Funsafe-code"]
            run(folder.name + "-" + name + ("-clippy" if lint else ""), [tools["clippy-driver" if lint else "rustc"]["path"],
                *common, *flags, *extra, *deps(folder, imports), "--crate-type=lib", "--crate-name=" + name,
                "-Cmetadata=" + folder.name, sources / source, "-o", folder / ("lib" + name + ".rlib")])

    host = work / "FILE-host"
    build(host)
    imports = [name for name, _, _ in crates]
    for compiler in ("rustc", "clippy-driver"):
        run(compiler + "-FILE-tests-build", [tools[compiler]["path"], *COMMON, *flags,
            *deps(host, imports), "--test", S / "home-wire-tests.rs", "-o", work / (compiler + "-FILE-tests")])
    result = run("FILE-tests", [work / "rustc-FILE-tests", "--test-threads=1"], timeout=30)
    require(b"29 passed; 0 failed" in result.stdout, "nine FILE/twelve process/eight binding cases executed")
    run("FILE-C-verify", [executable, "verify", work / "replies.bin"])
    run("FILE-C-real-errors", [executable, "errors", work / "errors.bin"])
    for stage, extra in (("host", []), ("native", NATIVE)):
        folder = work / ("FILE-" + stage)
        if extra:
            build(folder, extra=extra)
        build(folder, extra=extra, lint=True)
    # Exact pinned native headers, relocated from the pre-consolidation delivery.
    session = runner["R"] / "build/service-deliveries/filesystem-fd-session-2026-10-21-v1"
    dependency = session / "dependency.json"
    runner["verify"](dependency, "8f9af659ec999311e8564376c507a4c8ccdabafd46bc4ba315bd02cc18b0db9e")
    record["sources"][str(dependency)] = runner["sha"](dependency)
    include = runner["R"] / "build/sdk-deliveries/native-service-runtime-2026-10-06-v2/sdk/stage/usr/include"
    pinned = json.loads(dependency.read_text())["native_header_pins"]
    old_root = "/Users/cam/DEV/Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v2/sdk/stage/usr/include/"
    relocated = {str(include / name.removeprefix(old_root)): digest for name, digest in pinned.items()}
    require(len(relocated) == 217 and all(name.startswith(old_root) for name in pinned), "native header pin shape")
    actual = {str(path): runner["sha"](path) for path in include.rglob("*") if path.is_file()}
    require(actual == relocated, "exact native header inventory")
    record["sources"].update(actual)
    native = work / "FILE-C-native"
    native.mkdir()
    native_flags = [*cflags, "--target=x86_64-unknown-none", "-ffreestanding", "-fno-builtin", "-O2",
                    "-fstack-usage", "-nostdinc", "-isystem", str(include), "-c"]
    for unit in ("fd-client", "fd-facade"):
        cbuild("FILE-native-" + unit, native_flags, [S / (unit + ".c")], native / (unit + ".o"))
    run("FILE-native-link", [tools["lld"]["path"], "-r", native / "fd-client.o", native / "fd-facade.o", "-o", native / "combined.o"])
    inspected = run("FILE-native-inspect", [tools["readelf"]["path"], "-h", "-S", "-s", native / "combined.o"])
    require(all(value in inspected.stdout for value in (b"ELF64", b"Advanced Micro Devices X86-64", b"REL (Relocatable file)")), "native object shape")
    unresolved = run("FILE-native-unresolved", [tools["nm"]["path"], "--undefined-only", native / "combined.o"])
    symbols = [line.split()[-1] for line in unresolved.stdout.decode().splitlines() if line.strip()]
    require(set(symbols) <= {"memcpy", "memset", "memcmp", "memmove"}, "bounded native imports")
    stack = []
    for path in native.glob("*.su"):
        for line in path.read_text().splitlines():
            function, size, kind = line.split("\t")
            require(kind == "static", "static native frame")
            stack.append({"function": function, "bytes": int(size)})
    require(bool(stack), "native stack reports")
    record["file_native_objects"] = {"sha256": runner["sha"](native / "combined.o"), "unresolved": symbols,
        "stack": stack, "whole_executable_fit": False, "executed": False}

    process["check"](record, work, proc, tools, deadline=deadline)
    def without(selected, omitted):
        return [v for i, v in enumerate(selected) if v not in omitted and not
                (v == "--cfg" and i + 1 < len(selected) and selected[i + 1] in omitted)]
    for stage, extra in (("host", []), ("native", NATIVE)):
        folder = work / ("FILE-" + stage)
        for omitted in ("fs_process_writes", "fs_path_wire", "fs_dup2_wire"):
            rejected = run(stage + "-FILE-missing-" + omitted, [tools["rustc"]["path"], *COMMON,
                *without(flags, {omitted}), *extra, *deps(folder, imports), "--crate-type=lib",
                S / "fd-protocol.rs", "-o", folder / "absent.rlib"], expected=1)
            require(b"FILE write wire requires matched process writes, path and dup2 wire" in rejected.stderr,
                    "explicit FILE prerequisite guard")
        for forbidden in ("fs_cwd_wire", "fs_in_place"):
            rejected = run(stage + "-FILE-forbidden-" + forbidden, [tools["rustc"]["path"], *COMMON,
                *flags, "--cfg", forbidden, *extra, *deps(folder, imports), "--crate-type=lib",
                S / "fd-protocol.rs", "-o", folder / "absent.rlib"], expected=1)
            require(b"FILE write wire excludes CWD or unselected home in-place" in rejected.stderr, "explicit FILE forbidden guard")
        old = work / ("old16-" + stage)
        rejected = run(stage + "-FILE-reject-old-broker", [tools["rustc"]["path"], *COMMON, *flags, *extra,
            *deps(old, ["filesystem_client", "filesystem_service", "filesystem_remote_descriptors"]),
            "--crate-type=lib", S / "fd-protocol.rs", "-o", folder / "absent.rlib"], expected=1)
        require(b"FILE write wire requires AF09" in rejected.stderr, "old broker rejection")
    for omitted in ("AEFD_PATH_WIRE", "AEFD_DUP2_WIRE"):
        rejected = run("FILE-C-missing-" + omitted, [tools["clang"]["path"],
            *[v for v in cflags if v != "-D" + omitted], "-fsyntax-only", S / "fd-client.c"], expected=1)
        require(b"AEFD_WRITE_WIRE requires path/dup2 without CWD" in rejected.stderr, "C prerequisite guard")

    rust_controls = [
        ("terminal-discard", "file-write-wire.rs", "self.retired = true;", "self.retired = true; return Err(Error::Retired);", "terminal_error_receipts_are_delivered_after_source_retirement", "FILE_TERMINAL_RECEIPT"),
        ("owner-copy", "file-write-wire.rs", "        self.write\n", "        let _ = self.write; None\n", "actual_write_reply_readback_and_owner_success_receipt", "FILE_OWNER_RECEIPT"),
        ("guard-clear", "fd-protocol.rs", "if !self.delivered {\n            self.workspace.fill(0);", "if !self.delivered {\n            let _ = self.workspace[0];", "copied_success_and_error_survive_dropped_guard_without_replay", "FILE_WRITE_GUARD_CLEAR"),
        ("guard-retire", "fd-protocol.rs", "self.connection.abort(self.files);", "let _ = &self.files;", "copied_success_and_error_survive_dropped_guard_without_replay", "FILE_WRITE_DROP_RETIRE"),
        ("padding", "fd-protocol.rs", "workspace[word(raw, 5) as usize..needed]", "workspace[needed..needed]", "malformed_request_or_padding_and_old_versions_precede_effects", "FILE_WRITE_PREFLIGHT"),
    ]
    record["file_controls"] = []
    for label, filename, before, after, test, marker in rust_controls:
        original = (S / filename).read_text()
        require(original.count(before) == 1, "unique FILE control: " + label)
        folder = work / ("FILE-control-" + label)
        sources = folder / "source"
        sources.mkdir(parents=True)
        for path in S.glob("*.rs"):
            shutil.copy2(path, sources / path.name)
        (sources / "vendor").mkdir()
        shutil.copy2(S / "vendor/abi29-startup.rs", sources / "vendor/abi29-startup.rs")
        (sources / filename).write_text(original.replace(before, after, 1))
        build(folder, sources=sources)
        run(label + "-FILE-test-build", [tools["rustc"]["path"], *COMMON, *flags, *deps(folder, imports),
            "--test", sources / "home-wire-tests.rs", "-o", folder / "tests"])
        name = "file_writes::" + test
        rejected = run(label + "-FILE-reject", [folder / "tests", "--exact", name, "--nocapture"], expected=101, timeout=15)
        require(b"1 failed" in rejected.stdout and name.encode() in rejected.stdout and marker.encode() in rejected.stderr,
                "named FILE semantic rejection: " + label)
        record["file_controls"].append({"label": label, "file": filename, "before": before, "after": after,
            "test": name, "marker": marker, "sha256": runner["sha"](sources / filename)})
    c_controls = [
        ("committed-zero", "fd-file-write.h", "tag == 3 && !r.txg", "(tag == 2 || tag == 3) && !r.txg", "FILE_C_PROGRESS"),
        ("early-publication", "fd-file-write.h", "uint64_t tag = r.flags & 7U;", "*out = r; uint64_t tag = r.flags & 7U;", "FILE_C_ATOMIC_PUBLICATION"),
        ("source-closes", "fd-file-write.h", "aefd_write_signed(aefd_word(body, 4))", "(aefd_word(body, 0) & 16U ? aefd_write_signed(aefd_word(body, 5)) : aefd_write_signed(aefd_word(body, 4)))", "FILE_C_RAW_CLOSES"),
        ("send-loss", "fd-client.c", "result.observation = AEFD_WRITE_UNKNOWN;", "result.observation = AEFD_WRITE_NOT_SENT;", "FILE_C_MALFORMED_UNKNOWN"),
        ("separate-closes", "fd-client.c", "result.remote.flags & 16U", "result.remote.flags & 32U", "FILE_C_SEPARATE_CLOSES"),
        ("generic-write", "fd-client.c", "if (opcode == 11)", "if (opcode == 111)", "FILE_C_GENERIC_DENY"),
    ]
    for label, filename, before, after, marker in c_controls:
        original = (S / filename).read_text()
        require(original.count(before) == 1, "unique FILE C control: " + label)
        folder = work / ("FILE-C-control-" + label)
        folder.mkdir()
        for path in (*S.glob("*.c"), *S.glob("*.h")):
            shutil.copy2(path, folder / path.name)
        (folder / filename).write_text(original.replace(before, after, 1))
        binary = folder / "fixture"
        cbuild(label + "-FILE-C-build", [*cflags, "-fsanitize=undefined", "-fno-sanitize-recover=all"],
            [folder / "fd-file-write-tests.c", folder / "fd-client.c", folder / "fd-facade.c"], binary)
        # C binaries use the host runtime, not Rust's LLVM library path.
        saved = env.pop("DYLD_LIBRARY_PATH")
        try:
            rejected = run(label + "-FILE-C-reject", [binary], expected=1, timeout=30)
        finally:
            env["DYLD_LIBRARY_PATH"] = saved
        require(marker.encode() in rejected.stderr, "named C semantic rejection: " + label)
        record["file_controls"].append({"label": label, "file": filename, "before": before, "after": after,
            "marker": marker, "sha256": runner["sha"](folder / filename)})
    run("FILE-rustfmt", [tools["rustfmt"]["path"], "--edition=2021", "--check",
        S / "file-write-wire.rs", S / "file-write-tests.rs", S / "fd-protocol.rs", S / "home-wire-tests.rs"])
    run("FILE-C-format", [tools["clang-format"]["path"], "--dry-run", "--Werror",
        "--style=file:" + str(runner["R"] / "docs/quality/clang-format.yaml"),
        S / "fd-file-write.h", S / "fd-file-write-tests.c"])



if __name__ == "__main__":
    sys.exit(runner["main"](check_function=check, program="aether-file-writes-check",
        evidence=runner["R"] / "docs/evidence/filesystem-file-writes-2026-10-24",
        description=__doc__, example="python3 -B experiments/filesystem-service/check-file-writes.py",
        scope="versioned FILE/C receipt interoperability, host/no_std/freestanding libraries only",
        extra_sources=(SOURCE, process_source, S / "check-client-mutations.py", S / "vendor/abi29-startup.rs", runner["R"] / "docs/quality/clang-format.yaml",
                       *S.glob("*.c"), *S.glob("*.h"))))
