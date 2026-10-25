# SPDX-License-Identifier: BSD-2-Clause
"""Reconstruct one sealed runtime object, then apply its diagnostic overlay.

Imported helper only. The caller owns command isolation, deadlines, logs and the
port directory through final composition/cleanup. No SDK/repository/C-source tree
is copied or rebuilt. Temporary musl headers stay alive for the returned compiler
prefix's later pool-failure consumer, and are removed with the caller's port.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile

from openzfs_failure import instrument_backend

ROOT = Path(__file__).resolve().parents[1]
FIXED_UTC_SEAL = "ce420b8ac745287ea057b6c0b8949eb436a63b519e270b7ed7bf164ef342bad3"
FIXED_SEAL = "5adc4f6e9c255df3ead08404fca177d22db00a089429f1c0666fd90dd1812c6d"
SDK_SEAL = "f6bc6d6da3b051e1e4617e60ae256cbd35d193b608631ac29f7c42dbe73b13dc"
UTC_ARCHIVE = "693518d97acafe99f427cae5b42b5cc7aea7f0e8656c17f185fc8c24a0e06150"
BASE_ARCHIVE = "8262b1977be3b8fff449a6e9ac6d86b20acbc7ab0a1e38102287aecff20b9b23"
BUILDER_SHA = "1897a604e5aa4c22f3ef7f4b591c0f1125aafb5b32c15bb3255eb2282e3d2218"
MUSL_SHA = "d585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a"


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sealed(root, expected, count, enclosing=None):
    root = Path(root).absolute()
    seal = root / "SHA256SUMS"
    need(not root.is_symlink() and not seal.is_symlink(), "symlink seal root")
    need(seal.is_file() and seal.stat().st_size <= 1024 * 1024 and sha(seal) == expected,
         "runtime seal digest")
    files = {}
    for line in seal.read_text().splitlines():
        need(bool(re.fullmatch(r"[0-9a-f]{64}  [^\s]+", line)), "runtime seal syntax")
        digest, name = line.split("  ", 1)
        relative = PurePosixPath(name)
        need(not relative.is_absolute() and ".." not in relative.parts and
             str(relative) == name and name not in files, "runtime seal path")
        target = root
        for part in relative.parts:
            target /= part
            need(not target.is_symlink(), "runtime seal symlink")
        need(target.is_file() and sha(target) == digest, "runtime seal member: " + name)
        files[name] = digest
    need(len(files) == count, "runtime sealed member count")
    enclosing = enclosing or {}
    for name, digest in enclosing.items():
        path = PurePosixPath(name)
        need(not path.is_absolute() and ".." not in path.parts and str(path) == name
             and name not in files and name != "SHA256SUMS", "enclosing seal path")
        target = root / name
        need(target.is_file() and not target.is_symlink() and sha(target) == digest,
             "enclosing sealed member: " + name)
    actual = set()
    for path in root.rglob("*"):
        need(not path.is_symlink(), "runtime inventory symlink")
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
        else:
            need(path.is_dir(), "runtime inventory file type")
    need(actual == set(files) | set(enclosing) | {"SHA256SUMS"}, "runtime sealed inventory")
    return files


def archive_names(text):
    names = text.splitlines()
    need(0 < len(names) <= 64 and text.endswith("\n"), "runtime archive member list")
    need(all(re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.+-]*\.o", name) for name in names),
         "runtime archive member path")
    need(len(names) == len(set(names)), "duplicate runtime archive member")
    need(names.count("backend.o") == 1, "runtime archive backend member missing")
    return names


def verify_dependency(dependency, tools):
    dependency = Path(dependency).absolute()
    utc = sealed(dependency, FIXED_UTC_SEAL, 343)
    base = sealed(dependency / "base", FIXED_SEAL, 294)
    sdk_root = dependency / "base/sdk"
    # The historical SDK240 seal predates its evidence.json receipt alias.
    # That one alias is an exact member of both enclosing immutable packets.
    evidence = {"evidence.json": base["sdk/evidence.json"]}
    sdk = sealed(sdk_root, SDK_SEAL, 240, enclosing=evidence)
    inputs = {str(dependency / name): digest for name, digest in utc.items()}
    for root, digest in ((dependency, FIXED_UTC_SEAL),
                         (dependency / "base", FIXED_SEAL), (sdk_root, SDK_SEAL)):
        inputs[str(root / "SHA256SUMS")] = digest
    current = ROOT / ".deps/native-current/sdk"
    for name, digest in sdk.items():
        path = current / name
        need(path.is_file() and not path.is_symlink() and sha(path) == digest,
             "current guarded SDK differs: " + name)
        inputs[str(path)] = digest
    utc_archive = dependency / "runtime/libaether_runtime.a"
    base_archive = dependency / "base/runtime/libaether_runtime.a"
    need(sha(utc_archive) == UTC_ARCHIVE and sha(base_archive) == BASE_ARCHIVE,
         "sealed runtime archive identity")
    source = dependency / "base/source/experiments/native-service-runtime"
    need(sha(source / "build.py") == BUILDER_SHA, "runtime original compiler recipe changed")
    need(sha(sdk_root / "musl-1.2.6.tar.gz") == MUSL_SHA, "runtime musl source archive changed")
    locked = json.loads((sdk_root / "tools.lock.json").read_text())["tools"]
    for name in ("clang", "ar"):
        need(tools[name]["path"] == locked[name]["path"] and
             tools[name]["sha256"] == locked[name]["sha256"], "runtime tool selection: " + name)
        need(sha(tools[name]["path"]) == tools[name]["sha256"], "runtime tool changed: " + name)
        inputs[tools[name]["path"]] = tools[name]["sha256"]
    inputs[str(Path(__file__).resolve())] = sha(Path(__file__))
    instrumentation = ROOT / "scripts/openzfs_failure.py"
    inputs[str(instrumentation)] = sha(instrumentation)
    return {"source_root": str(source), "sdk": str(sdk_root),
        "musl_archive": str(sdk_root / "musl-1.2.6.tar.gz"),
        "utc_archive": str(utc_archive), "base_archive": str(base_archive),
        "inputs": inputs, "tools": {name: dict(tools[name]) for name in ("clang", "ar")},
        "seals": {"utc": {"sha256": FIXED_UTC_SEAL, "members": len(utc)},
                  "base": {"sha256": FIXED_SEAL, "members": len(base)},
                  "sdk": {"sha256": SDK_SEAL, "members": len(sdk),
                          "enclosing_sealed_aliases": evidence}}}


def _headers(archive, target, futex):
    target.mkdir()
    originals = {}
    total = 0
    with tarfile.open(archive) as source:
        for member in source:
            name = member.name
            need(name == "musl-1.2.6" or name.startswith("musl-1.2.6/"), "musl root path")
            relative = name.removeprefix("musl-1.2.6/")
            path = PurePosixPath(relative)
            need(not path.is_absolute() and ".." not in path.parts and
                 str(path) == relative, "musl header path")
            wanted = relative.endswith(".h") and relative.startswith(
                ("src/internal/", "src/include/", "arch/x86_64/", "arch/generic/", "include/"))
            if not wanted:
                continue
            need(member.isfile() and relative not in originals, "musl header type/duplicate")
            total += member.size
            need(0 <= member.size <= 256 * 1024 and total <= 1024 * 1024 and
                 len(originals) < 300, "bounded musl header selection")
            stream = source.extractfile(member)
            need(stream is not None, "missing musl header bytes")
            with stream:
                data = stream.read(member.size + 1)
            need(len(data) == member.size, "truncated musl header")
            output = target / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(data)
            originals[relative] = sha(output)
    replacement = target / "arch/x86_64/syscall_arch.h"
    need(replacement.is_file(), "musl syscall header missing")
    before = sha(replacement)
    shutil.copyfile(futex, replacement)
    return {"members": len(originals), "bytes": total, "originals": originals,
        "syscall_patch": {"path": "arch/x86_64/syscall_arch.h", "before": before,
                          "after": sha(replacement), "source": str(futex)}}


def _compiler_prefix(source, sdk, build, tools):
    # This exact prefix is the sealed builder's backend branch (no per-thread
    # source flags). Read that pinned recipe in place; never execute/copy it.
    recipe = (source / "build.py").read_text()
    anchor = "    cc = [tools['clang']['path'], '--no-default-config',"
    end = "    objects = []"
    need(recipe.count(anchor) == 1 and recipe[recipe.index(anchor):].count(end) == 1,
         "runtime backend compiler recipe anchors")
    prefix = [tools["clang"]["path"], "--no-default-config", "--target=x86_64-linux-musl",
        "--sysroot=" + str(build / "empty-root"), "-std=c17", "-D_GNU_SOURCE", "-O2",
        "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-fno-builtin",
        "-fstack-protector-strong", "-nostdinc", "-DAETHER_LONG_WAITS",
        '-Dhidden=__attribute__((__visibility__("hidden")))']
    for directory in ("src/include", "src/internal", "arch/x86_64", "arch/generic"):
        prefix += ["-isystem", str(build / "musl" / directory)]
    return prefix + ["-isystem", str(sdk / "stage/usr/include"), "-I", str(source)]


def runtime_archive(port, dependency, tools, command):
    """Prove original backend bytes, then replace exactly one UTC member.

    command(args, log, rejection=None) is the caller's bounded owned runner and
    returns stdout text. Failure leaves compact-recordable owned outputs for the
    caller; no fallback, retry, publication or guest follows from this helper.
    """
    port = Path(port).absolute()
    need(port.is_dir() and not port.is_symlink(), "runtime owned port directory")
    dependency = Path(dependency).absolute()
    need(not port.is_relative_to(dependency), "runtime output overlaps sealed input")
    verified = verify_dependency(dependency, tools)
    source, sdk = Path(verified["source_root"]), Path(verified["sdk"])
    build = port / "failure-runtime-build"
    need(not build.exists() and not build.is_symlink(), "runtime output already exists")
    build.mkdir()
    (build / "empty-root").mkdir()
    headers = _headers(Path(verified["musl_archive"]), build / "musl", source / "futex_syscall.h")
    prefix = _compiler_prefix(source, sdk, build, tools)
    frozen = dict(verified["inputs"])
    for path in (build / "musl").rglob("*.h"):
        frozen[str(path)] = sha(path)

    def invoke(args, log):
        for name, digest in frozen.items():
            need(sha(name) == digest, "runtime input changed before child: " + name)
        output = command(list(map(str, args)), log)
        for name, digest in frozen.items():
            need(sha(name) == digest, "runtime input changed after child: " + name)
        need(isinstance(output, str), "runtime command must return text")
        return output

    original = build / "original-backend.o"
    invoke([*prefix, "-c", source / "backend.c", "-o", original], port / "failure-original-backend.log")
    proof = build / "member-proof"
    proof.mkdir()

    def members(archive, label):
        names = archive_names(invoke([tools["ar"]["path"], "t", archive], port / (label + "-list.log")))
        directory = proof / label
        directory.mkdir()
        invoke([tools["ar"]["path"], "x", archive, "--output=" + str(directory)], port / (label + "-extract.log"))
        need({p.name for p in directory.iterdir()} == set(names) and
             all(p.is_file() and not p.is_symlink() for p in directory.iterdir()), "runtime extracted member inventory")
        return names, {name: sha(directory / name) for name in names}, directory

    base_names, base_hashes, base_dir = members(Path(verified["base_archive"]), "base")
    utc_names, utc_hashes, utc_dir = members(Path(verified["utc_archive"]), "utc")
    need(original.read_bytes() == (base_dir / "backend.o").read_bytes(),
         "original runtime backend reconstruction differs; no fallback")
    need((base_dir / "backend.o").read_bytes() == (utc_dir / "backend.o").read_bytes(),
         "UTC original backend differs from sealed base backend")
    changed, catalogue = instrument_backend((source / "backend.c").read_text())
    selected = build / "backend.c"
    selected.write_text(changed)
    frozen[str(selected)] = sha(selected)
    selected_object = build / "backend.o"
    invoke([*prefix, "-c", selected, "-o", selected_object], port / "failure-backend.log")
    output = port / "failure-runtime"
    need(not output.exists() and not output.is_symlink(), "runtime archive output already exists")
    output.mkdir()
    archive = output / "libaether_runtime.a"
    shutil.copyfile(verified["utc_archive"], archive)
    invoke([tools["ar"]["path"], "rcs", archive, selected_object], port / "failure-archive.log")
    selected_names, selected_hashes, _ = members(archive, "selected")
    need(selected_names == utc_names, "selected runtime archive member order differs")
    need(selected_hashes["backend.o"] == sha(selected_object), "selected backend member differs")
    need(all(selected_hashes[name] == utc_hashes[name] for name in utc_names if name != "backend.o"),
         "selected runtime unaffected member differs")
    result = {"backend_compiler_prefix": prefix, "archive_sha256": sha(archive),
        "original_backend_sha256": sha(original), "selected_backend_sha256": sha(selected_object),
        "original_source_sha256": sha(source / "backend.c"), "selected_source_sha256": sha(selected),
        "sealed_base_archive_sha256": sha(verified["base_archive"]),
        "sealed_utc_archive_sha256": sha(verified["utc_archive"]),
        "base_members": base_names, "utc_members": utc_names,
        "base_member_sha256": base_hashes, "utc_member_sha256": utc_hashes,
        "selected_member_sha256": selected_hashes, "seals": verified["seals"],
        "headers": headers, "inputs": frozen, "tools": verified["tools"], "catalogue": catalogue,
        "scope": "Exact original backend object proof plus one UTC archive diagnostic overlay; not a fresh whole SDK/runtime rebuild"}
    for name, digest in frozen.items():
        need(sha(name) == digest, "runtime final input changed: " + name)
    shutil.rmtree(proof)
    result["extracted_member_cleanup"] = "complete"
    return result
