# SPDX-License-Identifier: BSD-2-Clause
"""Check explicit two-grant home activation; host/no_std only, no guest."""
from pathlib import Path
import runpy
import shutil
import sys
import time

SOURCE = Path(__file__).resolve()
S = SOURCE.parent
home = runpy.run_path(str(S / "check-home-wire.py"))
require = home["require"]
COMMON = home["COMMON"]
NATIVE = home["NATIVE"]


def check(record, work, proc, tools):
    deadline = time.monotonic() + 300
    env = proc.clean_env(work)
    env["DYLD_LIBRARY_PATH"] = str(Path(tools["rustc"]["path"]).parent.parent / "lib")
    flags = [*home["cfg"](True), "--cfg", "fs_home_wire"]
    record["home_activation_libraries"] = {}
    crates = [("filesystem_metadata", "metadata-lib.rs", []),
              ("filesystem_policy", "owner.rs", ["filesystem_metadata"]),
              ("filesystem_service", "service.rs", ["filesystem_policy"]),
              ("filesystem_client", "client.rs", ["filesystem_service"])]

    def run(label, argv, expected=0):
        remaining = deadline - time.monotonic()
        require(remaining > 0, "suite deadline before " + label)
        result = proc.run(list(map(str, argv)), cwd=home["R"], env=env, work=work,
                          label=label, timeout=min(60, remaining))
        record["rows"].append({"label": label, "expected_exit": expected,
            "process": result.record, "stdout": result.stdout.decode(errors="replace")[-7000:],
            "stderr": result.stderr.decode(errors="replace")[-5000:]})
        require(result.returncode == expected and result.record["complete"]
                and result.record["cleanup"] == "complete", label)
        return result

    def deps(folder, names):
        return ["-Ldependency=" + str(folder), *[value for name in names for value in
            ("--extern", name + "=" + str(folder / ("lib" + name + ".rlib")))]]

    for stage, extra in (("host", []), ("native", NATIVE)):
        folder = work / ("activated-" + stage)
        folder.mkdir()
        for name, filename, imports in crates:
            common = [v for v in COMMON if name != "filesystem_metadata" or v != "-Funsafe-code"]
            run(stage + "-" + name, [tools["rustc"]["path"], *common, *flags, *extra,
                *deps(folder, imports), "--crate-type=lib", "--crate-name=" + name,
                "-Cmetadata=" + folder.name, S / filename, "-o", folder / ("lib" + name + ".rlib")])
        for compiler in ("rustc", "clippy-driver"):
            run(stage + "-" + compiler + "-home-activation", [tools[compiler]["path"], *COMMON,
                *flags, "--cfg", "fs_home_activation", *extra,
                *deps(folder, ["filesystem_policy", "filesystem_service"]), "--crate-type=lib",
                "--crate-name=filesystem_activation", S / "activation.rs", "-o",
                folder / ("libfilesystem_activation.rlib" if compiler == "rustc" else "clippy-activation.rlib")])
            artifact = folder / ("libfilesystem_activation.rlib" if compiler == "rustc" else "clippy-activation.rlib")
            record["home_activation_libraries"][stage + ":" + compiler] = home["sha"](artifact)
    host = work / "activated-host"
    for compiler in ("rustc", "clippy-driver"):
        run(compiler + "-home-activation-tests-build", [tools[compiler]["path"], *COMMON,
            *flags, "--cfg", "fs_home_activation", *deps(host, [n for n, _, _ in crates]),
            "--test", S / "activation.rs", "-o", work / (compiler + "-tests")])
    tested = run("home-activation-tests", [work / "rustc-tests", "home::tests::", "--test-threads=1"])
    require(b"6 passed; 0 failed" in tested.stdout, "six home activation methods executed")
    controls = [
        ("early-publication", "            publish,\n            epoch,", "            publish: { let mut callback=publish; let _=callback(); callback },\n            epoch,", "invalid_sources_and_epoch_never_publish_or_send", "HOME_ACTIVATION_ATTACH_BEFORE_PUBLISH"),
        ("home-token", "word(frame, 3) != token", "(word(frame, 3) != token && token == 1)", "malformed_greeting_fields_at_both_stages_latch", "HOME_ACTIVATION_GREETING_VALIDATION"),
        ("failure-latch", "self.stage = Stage::Failed;", "let _ = Stage::Failed;", "post_greeting_reply_error_latches_without_second_publication", "HOME_ACTIVATION_LATCH"),
        ("publication-status", "let status = (self.publish)();", "let status = { let _ = (self.publish)(); 0 };", "publication_errors_preserve_raw_and_never_send", "HOME_ACTIVATION_PUBLICATION_STATUS"),
    ]
    record["home_activation_controls"] = []
    for label, before, after, case, marker in controls:
        original = (S / "home-activation.rs").read_text()
        require(original.count(before) == 1, "unique activation control: " + label)
        control = work / ("activation-control-" + label)
        control.mkdir()
        for filename in ("activation.rs", "home-activation.rs", "home-activation-tests.rs", "activation-tests.rs"):
            shutil.copy2(S / filename, control / filename)
        (control / "home-activation.rs").write_text(original.replace(before, after, 1))
        run(label + "-control-build", [tools["rustc"]["path"], *COMMON, *flags,
            "--cfg", "fs_home_activation", *deps(host, [n for n, _, _ in crates]),
            "--test", control / "activation.rs", "-o", control / "tests"])
        name = "home::tests::" + case
        rejected = run(label + "-rejected", [control / "tests", "--exact", name, "--nocapture"], expected=101)
        require(name.encode() in rejected.stdout and b"1 failed" in rejected.stdout
                and marker.encode() in rejected.stderr, "named activation semantic control: " + label)
        record["home_activation_controls"].append({"label": label, "before": before,
            "after": after, "test": name, "marker": marker,
            "sha256": home["sha"](control / "home-activation.rs")})

    # Existing service/client/old-wire coverage follows focused activation cases.
    home["check"](record, work, proc, tools, deadline=deadline)
    def old_flags(profile):
        base = home["cfg"]()
        if profile == "af08":
            return base
        return [value for i, value in enumerate(base) if value != "fs_directory_contexts"
            and not (value == "--cfg" and i + 1 < len(base) and base[i + 1] == "fs_directory_contexts")]
    def consumer_deps(folder, producer, names):
        result = ["-Ldependency=" + str(folder), "-Ldependency=" + str(producer)]
        for name in names:
            root = folder if name in ("filesystem_activation", "filesystem_bridge") else producer
            result += ["--extern", name + "=" + str(root / ("lib" + name + ".rlib"))]
        return result
    boundary = [v for v in COMMON if v != "-Funsafe-code"]
    for profile in ("af07", "af08"):
        selected = old_flags(profile)
        for stage, extra in (("host", []), ("native", NATIVE)):
            producer = work / (profile + ("-native" if extra else ""))
            folder = work / (profile + "-activation-" + stage)
            folder.mkdir()
            imports = ["filesystem_policy", "filesystem_service"]
            run(profile + stage + "-old-activation", [tools["rustc"]["path"], *COMMON,
                *selected, *extra, *deps(producer, imports), "--crate-type=lib",
                "--crate-name=filesystem_activation", S / "activation.rs", "-o", folder / "libfilesystem_activation.rlib"])
            record["home_activation_libraries"][profile + ":" + stage] = home["sha"](folder / "libfilesystem_activation.rlib")
            if not extra:
                for compiler in ("rustc", "clippy-driver"):
                    run(profile + compiler + "-old-activation-tests-build", [tools[compiler]["path"],
                        *COMMON, *selected, *deps(producer, imports), "--test", S / "activation.rs",
                        "-o", folder / (compiler + "-tests")])
                tested = run(profile + "-old-activation-tests", [folder / "rustc-tests", "--test-threads=1"])
                require(b"3 passed; 0 failed" in tested.stdout, "three old activation methods: " + profile)
            run(profile + stage + "-old-bridge", [tools["rustc"]["path"], *boundary, *selected,
                *extra, *deps(producer, ["filesystem_metadata", "filesystem_policy"]),
                "--crate-type=lib", "--crate-name=filesystem_bridge", S / "bridge.rs", "-o", folder / "libfilesystem_bridge.rlib"])
            if extra:
                run(profile + stage + "-actual-old-native-entry", [tools["rustc"]["path"], *boundary,
                    *selected, *extra, *consumer_deps(folder, producer,
                        ["filesystem_bridge", "filesystem_service", "filesystem_activation"]),
                    "--crate-type=lib", S / "native-service.rs", "-o", folder / "native-entry.rlib"])
            rejected = run(profile + stage + "-old-dependency-home-selection-reject", [tools["rustc"]["path"],
                *COMMON, *selected, "--cfg", "fs_home_activation", *extra, *deps(producer, imports),
                "--crate-type=lib", S / "activation.rs", "-o", folder / "absent.rlib"], expected=1)
            require(b"home activation requires matching AFSRPC09 dependencies" in rejected.stderr,
                "old service cannot supply home activation")
            probe = folder / "home-api.rs"
            probe.write_text("#![no_std]\npub fn probe<B:filesystem_policy::Backend,C:filesystem_policy::Clock,T:filesystem_service::Channel>(o:filesystem_policy::Owner<B,C>,t:T,s:filesystem_policy::Session,h:filesystem_policy::Handle){let _=filesystem_activation::run_home(o,t,7,s,h,8,91,||0); }\n")
            rejected = run(profile + stage + "-old-home-api-absent", [tools["rustc"]["path"], *COMMON,
                *extra, *consumer_deps(folder, producer, [*imports, "filesystem_activation"]),
                "--crate-type=lib", probe, "-o", folder / "absent.rlib"], expected=1)
            require(b"E0425" in rejected.stderr and b"run_home" in rejected.stderr, "old activation has no home API")
    for stage, extra in (("host", []), ("native", NATIVE)):
        folder = work / ("activated-" + stage)
        imports = ["filesystem_policy", "filesystem_service"]
        rejected = run(stage + "-missing-home-activation-selection", [tools["rustc"]["path"],
            *COMMON, *flags, *extra, *deps(folder, imports), "--crate-type=lib", S / "activation.rs",
            "-o", folder / "absent.rlib"], expected=1)
        require(b"home service requires a separately integrated consumer" in rejected.stderr,
                "unselected wrapper still rejects AF09")
        run(stage + "-home-bridge", [tools["rustc"]["path"], *boundary, *flags, *extra,
            *deps(folder, ["filesystem_metadata", "filesystem_policy"]), "--crate-type=lib",
            "--crate-name=filesystem_bridge", S / "bridge.rs", "-o", folder / "libfilesystem_bridge.rlib"])
        # Actual entry contains x86_64 trap assembly and is target-only.
        # A host generic API probe independently rejects the old root call.
        old_api = folder / "old-root-api.rs"
        old_api.write_text("#![no_std]\npub fn old<B:filesystem_policy::Backend,C:filesystem_policy::Clock,T:filesystem_service::Channel>(o:filesystem_policy::Owner<B,C>,t:T,r:filesystem_policy::Rights){let _=filesystem_activation::run(o,t,8,r,91,||0); }\n")
        rejected = run(stage + "-old-root-api-absent", [tools["rustc"]["path"], *COMMON,
            *extra, *deps(folder, ["filesystem_policy", "filesystem_service", "filesystem_activation"]),
            "--crate-type=lib", old_api, "-o", folder / "absent.rlib"], expected=1)
        require(b"E0425" in rejected.stderr and b"run" in rejected.stderr, "home activation has no old root API")
        if extra:
            rejected = run(stage + "-unmatched-actual-native-entry-reject", [tools["rustc"]["path"],
                *boundary, *flags, *extra, *deps(folder,
                    ["filesystem_bridge", "filesystem_service", "filesystem_activation"]),
                "--crate-type=lib", S / "native-service.rs", "-o", folder / "absent.rlib"], expected=1)
            require(b"E0425" in rejected.stderr and b"filesystem_activation" in rejected.stderr
                    and b"run" in rejected.stderr, "actual old native entry cannot silently use home activation")
    run("home-activation-rustfmt", [tools["rustfmt"]["path"], "--edition=2021", "--check",
        *[S / filename for filename in ("activation.rs", "home-activation.rs", "home-activation-tests.rs")]])


if __name__ == "__main__":
    sys.exit(home["main"](check_function=check, program="aether-home-activation-check",
        evidence=home["R"] / "docs/evidence/filesystem-home-activation-2026-10-24",
        description=__doc__, example="python3 -B experiments/filesystem-service/check-home-activation.py",
        scope="explicit AF09 activation host/no_std and old native-entry compatibility builds; no matched home entry, guest or whole engine fit",
        extra_sources=(SOURCE,)))
