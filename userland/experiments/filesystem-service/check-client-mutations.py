# SPDX-License-Identifier: BSD-2-Clause
"""Check AF09 mutation completion and errors using pinned offline host tools."""
from pathlib import Path
import runpy
import shutil
import sys
import time

SOURCE = Path(__file__).resolve()
S = SOURCE.parent
runner = runpy.run_path(str(S / "check-home-wire.py"))
require = runner["require"]
COMMON = runner["COMMON"]
NATIVE = runner["NATIVE"]


def check(record, work, proc, tools, deadline=None):
    if deadline is None:
        deadline = time.monotonic() + 300
    env = proc.clean_env(work)
    env["DYLD_LIBRARY_PATH"] = str(Path(tools["rustc"]["path"]).parent.parent / "lib")
    flags = [*runner["cfg"](True), "--cfg", "fs_home_wire"]
    test_flags = [*flags, "--cfg", "fs_client_mutations"]
    crates = [("filesystem_metadata", "metadata-lib.rs", []),
              ("filesystem_policy", "owner.rs", ["filesystem_metadata"]),
              ("filesystem_service", "service.rs", ["filesystem_policy"]),
              ("filesystem_client", "client.rs", ["filesystem_service"])]

    def run(label, argv, expected=0, timeout=60):
        remaining = deadline - time.monotonic()
        require(remaining > 0, "suite deadline before " + label)
        result = proc.run(list(map(str, argv)), cwd=runner["R"], env=env, work=work,
                          label=label, timeout=min(timeout, remaining))
        record["rows"].append({"label": label, "expected_exit": expected,
            "process": result.record, "stdout": result.stdout.decode(errors="replace")[-7000:],
            "stderr": result.stderr.decode(errors="replace")[-5000:]})
        require(result.returncode == expected and result.record["complete"]
                and result.record["cleanup"] == "complete", label)
        return result

    def deps(folder, names):
        return ["-Ldependency=" + str(folder), *[value for name in names for value in
            ("--extern", name + "=" + str(folder / ("lib" + name + ".rlib")))]]

    def build(folder, sources=S, extra=(), lint=False):
        folder.mkdir(exist_ok=True)
        for name, source, imports in crates:
            common = [f for f in COMMON if name != "filesystem_metadata" or f != "-Funsafe-code"]
            compiler = tools["clippy-driver" if lint else "rustc"]["path"]
            run(folder.name + "-" + name + ("-clippy" if lint else ""), [compiler, *common, *flags, *extra,
                *deps(folder, imports), "--crate-type=lib", "--crate-name=" + name,
                "-Cmetadata=" + folder.name, sources / source, "-o", folder / ("lib" + name + ".rlib")])

    imports = [name for name, _, _ in crates]
    host = work / "mutation-host"
    build(host)
    for compiler in ("rustc", "clippy-driver"):
        run("mutation-" + compiler + "-tests-build", [tools[compiler]["path"], *COMMON, *test_flags,
            *deps(host, imports), "--test", S / "home-wire-tests.rs", "-o", work / ("mutation-" + compiler)])
    result = run("mutation-tests", [work / "mutation-rustc", "--test-threads=1"], timeout=30)
    require(b"21 passed; 0 failed" in result.stdout and b"mutations::" in result.stdout,
            "all thirteen mutation and eight binding tests must execute")
    record["mutation_tests"] = 13
    run("mutation-rustfmt", [tools["rustfmt"]["path"], "--edition=2021", "--check",
        S / "client.rs", S / "mutation-client.rs", S / "mutation-client-tests.rs", S / "home-wire-tests.rs"])
    for stage, extra in (("host", []), ("native", NATIVE)):
        folder = work / ("mutation-" + stage)
        if extra:
            build(folder, extra=extra)
        build(folder, extra=extra, lint=True)
    # Exercise the shared runner's existing profiles, immutable producer and guards.
    runner["check"](record, work, proc, tools, deadline=deadline)
    # AF07/08 and the sealed producer must not expose the new methods.
    absent = work / "old-mutation-api.rs"
    absent.write_text("#![no_std]\npub fn probe<T: filesystem_service::Channel>(c: &mut filesystem_client::Client<T>, h: filesystem_client::Handle) { let _ = c.write(h, 0, b\"x\"); }\n")
    for profile in ("af07", "af08", "sealed"):
        for stage, extra in (("host", []), ("native", NATIVE)):
            folder = work / (("sealed-" + stage) if profile == "sealed" else profile + ("-native" if extra else ""))
            rejected = run(profile + stage + "-no-mutation-api", [tools["rustc"]["path"], *COMMON, *extra,
                *deps(folder, ["filesystem_service", "filesystem_client"]), "--crate-type=lib", absent,
                "-o", work / (profile + stage + "-absent.rlib")], expected=1)
            require(b"E0599" in rejected.stderr and b"write" in rejected.stderr, "old mutation API must be absent")
    controls = [
        ("completion-count", "staged != expected as u64", "false", "malformed_success_or_error_never_publishes_progress", "MUTATION_REPLY_VALIDATION"),
        ("committed-zero-txg", "if state == 1 {", "if state == 1 && txg != 0 {", "write_error_progress_matrix_is_preserved_after_drop", "MUTATION_EXACT_OUTCOME"),
        ("error-retirement", "self.shutdown();", "let _ = ();", "write_error_progress_matrix_is_preserved_after_drop", "MUTATION_CLOSE_RECEIPT"),
        ("rename-order", "first.iter().chain(second)", "second.iter().chain(first)", "rename_uses_contiguous_510_byte_body_without_internal_padding", "MUTATION_RENAME_CONTIGUOUS"),
        ("write-authority", "binding.rights & 4 == 0", "false", "local_input_and_rights_errors_are_not_sent_and_keep_client_live", "MUTATION_LOCAL_PREFLIGHT"),
        ("namespace-errno", "(!namespace || code >= -4095)", "(!namespace || code >= -i64::from(i32::MAX))", "namespace_error_progress_requires_exact_errno_and_zero_staged", "MUTATION_NAMESPACE_SHAPE"),
    ]
    record["mutation_controls"] = []
    original = (S / "mutation-client.rs").read_text()
    for label, before, after, test, marker in controls:
        require(original.count(before) == 1, "unique mutation control anchor: " + label)
        folder = work / ("mutation-" + label)
        sources = folder / "source"
        sources.mkdir(parents=True)
        for path in S.glob("*.rs"):
            shutil.copy2(path, sources / path.name)
        (sources / "mutation-client.rs").write_text(original.replace(before, after, 1))
        build(folder, sources=sources)
        run(label + "-mutation-test-build", [tools["rustc"]["path"], *COMMON, *test_flags,
            *deps(folder, imports), "--test", sources / "home-wire-tests.rs", "-o", folder / "tests"])
        name = "mutations::" + test
        rejected = run(label + "-mutation-reject", [folder / "tests", "--exact", name, "--nocapture"], expected=101, timeout=15)
        require(b"1 failed" in rejected.stdout and name.encode() in rejected.stdout and marker.encode() in rejected.stderr,
                "named mutation rejection: " + label)
        record["mutation_controls"].append({"label": label, "test": name, "before": before, "after": after,
            "required_marker": marker, "mutated_sha256": runner["sha"](sources / "mutation-client.rs")})


if __name__ == "__main__":
    sys.exit(runner["main"](check_function=check, program="aether-client-mutations-check",
        evidence=runner["R"] / "docs/evidence/filesystem-client-mutations-2026-10-24",
        description=__doc__, example="python3 -B experiments/filesystem-service/check-client-mutations.py",
        scope="AF09 client mutation receipts, actual host service and no_std builds only",
        extra_sources=(SOURCE,)))
