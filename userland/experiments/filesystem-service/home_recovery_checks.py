# SPDX-License-Identifier: BSD-2-Clause
"""Imported independent AF09 reader checks; caller owns deadline and cleanup."""
import hashlib
import json
from pathlib import Path
import time

S = Path(__file__).resolve().parent
ROOT = S.parents[2]
R = ROOT / "userland"
PRODUCER = ROOT / "user/storage/openzfs-volume"
PINS = R / "docs/evidence/filesystem-transport-2026-10-19/inputs.json"
PINS_SHA = "f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def check(record, work, proc, tools, deadline):
    folder = work / "home-recovery"
    folder.mkdir()
    env = proc.clean_env(work)
    source = PRODUCER / "home-recovery-probe.c"
    header = PRODUCER / "home-recovery-probe.h"
    fixture = S / "home-recovery-tests.c"
    inputs = [source, header, fixture, Path(__file__),
              *sorted((S / "home-recovery-host").rglob("*.h")),
              PRODUCER / "zpl-read.c", PRODUCER / "zpl-read.h",
              R / "docs/quality/clang-format.yaml"]
    frozen = {str(path): sha(path) for path in inputs}
    require(frozen[str(PRODUCER / "zpl-read.c")] ==
            "bee69ab7d07fae3747dbe147513af1f74e9567fb087347c7fc5bed1f2a850e65",
            "original independent reader body changed")
    require(frozen[str(PRODUCER / "zpl-read.h")] ==
            "eb7bdc9155369747c918944baba8f3b109951fff295273930a4df7cea0c7cc8a",
            "original independent reader header changed")
    require(sha(PINS) == PINS_SHA, "reader tool manifest changed")
    pins = json.loads(PINS.read_text())
    frozen[str(PINS)] = PINS_SHA
    for name in ("clang", "clang-format"):
        require(tools[name] == pins["tools"][name], "reader tool selection changed")
        require(sha(tools[name]["path"]) == tools[name]["sha256"], "reader tool changed")
    for name, digest in pins["clang_resource_headers"].items():
        require(sha(name) == digest, "reader resource header changed: " + name)
        frozen[name] = digest
    ubsan = Path(tools["clang"]["path"]).parent.parent / "lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib"
    ubsan_sha = "7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746"
    require(sha(ubsan) == ubsan_sha, "reader UBSan changed")
    frozen[str(ubsan)] = ubsan_sha
    reference = ROOT / ".deps/openzfs-namespace-reference-v1/zstd.bin"
    require(reference.stat().st_size == 780248 and sha(reference) ==
            "cc9bfddedd664b9a5334581af786516d149c3fbd2c7e65735985acf17bce5935",
            "reader full reference changed")
    frozen[str(reference)] = sha(reference)
    record.setdefault("sources", {}).update(frozen)

    def run(label, argv, expected=0):
        remaining = deadline - time.monotonic()
        require(remaining > 0, "reader cumulative deadline before " + label)
        for name, digest in frozen.items():
            require(sha(name) == digest, "reader input changed before child: " + name)
        result = proc.run(list(map(str, argv)), cwd=ROOT, env=env, work=work,
                          label=label, timeout=min(180, remaining))
        record["rows"].append({"label": label, "expected_exit": expected,
            "process": result.record,
            "stdout": result.stdout.decode(errors="replace")[-3000:],
            "stderr": result.stderr.decode(errors="replace")[-5000:]})
        for name, digest in frozen.items():
            require(sha(name) == digest, "reader input changed after child: " + name)
        record["home_recovery_artifacts"] = {str(path): sha(path) for path in folder.rglob("*")
            if path.is_file() and path.suffix in ("", ".c", ".o", ".su", ".d")}
        require(result.returncode == expected and result.record["complete"] and
                result.record["cleanup"] == "complete", label)
        return result

    xcrun = Path("/usr/bin/xcrun")
    frozen[str(xcrun)] = sha(xcrun)
    record["sources"][str(xcrun)] = frozen[str(xcrun)]
    sdk = run("home-recovery-host-sdk", [xcrun, "--show-sdk-path"]).stdout.decode().strip()
    require(bool(sdk) and Path(sdk).is_dir(), "reader host SDK path unavailable")
    record["home_recovery_host_sdk"] = {"path": sdk, "xcrun_sha256": frozen[str(xcrun)]}
    strict = ["-std=c17", "-D_DEFAULT_SOURCE", "-Wall", "-Wextra", "-Werror"]
    host_flags = [*strict, "-isysroot", sdk, "-O1", "-g", "-fsanitize=undefined", "-fno-sanitize-recover=all",
                  "-I" + str(S / "home-recovery-host"), "-I" + str(PRODUCER)]
    run("home-recovery-format", [tools["clang-format"]["path"], "--dry-run", "--Werror",
        "--style=file:" + str(R / "docs/quality/clang-format.yaml"),
        source, header, fixture, *sorted((S / "home-recovery-host").rglob("*.h"))])
    run("home-recovery-build", [tools["clang"]["path"], *host_flags,
        source, fixture, "-o", folder / "reader"])
    for case in range(39):
        result = run("home-recovery-case-" + str(case), [folder / "reader", case, reference])
        require(("home recovery case " + str(case) + " passed").encode() in result.stdout,
                "reader semantic marker missing")
    record["home_recovery_cases"] = 39
    controls = [
        ("full-original-hash", "if (!error && memcmp(digest, original_hash, sizeof(digest)))",
         "if (!error && (0 && memcmp(digest, original_hash, sizeof(digest))))", 22),
        ("exact-object-inventory", "return mask == ((1U << count) - 1) ? 0 : EIO;",
         "return mask == ((1U << count) - 1) || count <= 11 ? 0 : EIO;", 24),
        ("home-mode", "home.mode != (S_IFDIR | 0700)", "(0 && home.mode != (S_IFDIR | 0700))", 3),
        ("home-labels", "m->uid != 1000", "(0 && m->uid != 1000)", 4),
        ("whole-probe-payload", "memcmp(w->buffer, payload, sizeof(payload))",
         "(0 && memcmp(w->buffer, payload, sizeof(payload)))", 23),
        ("probe-eof", "return error ? error : count ? EIO : 0;",
         "return error ? error : (0 && count) ? EIO : 0;", 27),
        ("utc-upper-bound", "time[0] < maximum", "(time[0] < maximum || minimum <= maximum)", 11),
        ("preserved-metadata-stream", "SHA2Update(preserved, data, length);",
         "if (0) SHA2Update(preserved, data, length);", 18),
    ]
    record["home_recovery_controls"] = []
    text = source.read_text()
    for label, old, new, case in controls:
        require(text.count(old) == 1, "reader control anchor changed: " + label)
        mutant = folder / (label + ".c")
        mutant.write_text(text.replace(old, new, 1))
        run("home-recovery-control-build-" + label, [tools["clang"]["path"], *host_flags,
            mutant, fixture, "-o", folder / label])
        result = run("home-recovery-control-" + label, [folder / label, case, reference], expected=1)
        require(b"HOME_RECOVERY_ORACLE" in result.stderr,
                "reader control failed for wrong reason: " + label)
        record["home_recovery_controls"].append({"name": label, "old": old, "new": new,
            "case": case, "compiled": True, "exit": 1, "source_sha256": sha(mutant)})

    receipt = ROOT / ".deps/fs-launch-af07-2026-10-23-v13/build.json"
    require(sha(receipt) == "9f08c0717e4bf3b238d696361b6c1d3222d30f4fceeb2b35e5a9ad0058caa2a8",
            "reader native recipe changed")
    frozen[str(receipt)] = sha(receipt)
    old = next(row["argv"] for row in json.loads(receipt.read_text())["commands"] if
        "-c" in row["argv"] and any(str(arg).endswith("/metadata-provider.o") for arg in row["argv"]))
    prefix = old[:old.index("-c")]
    require(prefix[0] == tools["clang"]["path"], "reader native compiler changed")
    omitted = [arg for arg in prefix if arg.startswith("-I/") and not Path(arg[2:]).exists()]
    prefix = [arg for arg in prefix if arg not in omitted]
    native_manifest = ROOT / ".deps/native-current/current-inputs.json"
    require(sha(native_manifest) == "0521371de06c44489426635890c4bb96bc820912ac7200c4294ff7eaea081d95",
            "reader native headers manifest changed")
    frozen[str(native_manifest)] = sha(native_manifest)
    native_files = json.loads(native_manifest.read_text())["files"]
    flags = ["-std=c17", "-Wall", "-Wextra", "-Werror", "-fstack-usage", "-I" + str(PRODUCER)]
    run("home-recovery-target-dependencies", [*prefix, *flags, "-M", source,
        "-MF", folder / "reader.d"])
    headers = (folder / "reader.d").read_text().replace("\\\n", " ").split(":", 1)[1].split()
    record["home_recovery_native_headers"] = {}
    for name in headers:
        digest = sha(name)
        path = Path(name)
        native_root = ROOT / ".deps/native-current"
        if path.is_relative_to(native_root):
            require(native_files.get(path.relative_to(native_root).as_posix()) == digest,
                    "reader pinned native header mismatch: " + name)
        if name in frozen:
            require(frozen[name] == digest, "reader input changed: " + name)
        frozen.setdefault(name, digest)
        record["sources"][name] = digest
        record["home_recovery_native_headers"][name] = digest
    record["sources"].update(frozen)
    run("home-recovery-target-build", [*prefix, *flags, "-c", source,
        "-o", folder / "reader.o"])
    record["home_recovery_native_recipe"] = {"sha256": sha(receipt),
        "omitted_old_missing_overlays": omitted,
        "scope": "Actual original reader/SA/ZAP/SHA2 header object, not a full native execution"}
    record["home_recovery_local_frames"] = {str(path): path.read_text() for path in folder.glob("*.su")}
    for name, digest in frozen.items():
        require(sha(name) == digest, "reader source changed during frozen check: " + name)
    record["home_recovery_limits"] = "Host typed substitutions and target object; metadata hash instrumentation is not host crypto or ZFS execution."
