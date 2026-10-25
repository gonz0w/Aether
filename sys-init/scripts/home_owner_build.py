# SPDX-License-Identifier: BSD-2-Clause
"""Imported native-only reconstruction of the existing matched home owner."""
import ast
import hashlib
import json
from pathlib import Path
import re
import runpy
import sys
import time

PROFILE = ("namespace", "lifetimes", "mixed", "wait", "bulk", "runtime", "activation",
           "names", "directories", "metadata", "directory_contexts", "home", "home_wire",
           "paths", "file16", "replace", "process_views", "process_writes", "path_wire",
           "dup2_wire", "file_write_wire", "in_place", "home_in_place", "home_owner")
SUPPLEMENTAL = {
    "objdump": {"path": "/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-objdump", "sha256": "57df889beb6133ffd405ffb84795941c068a13a09dba0a40546d3b740666b9b7"},
    "size": {"path": "/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-size", "sha256": "84f8a66f8a83bca2f5d013f318068488a5d40edc033b779cc5029ecc2f6d8b85"},
    "rust-lld": {"path": "/Users/cam/.rustup/toolchains/1.98.0-aarch64-apple-darwin/lib/rustlib/aarch64-apple-darwin/bin/rust-lld", "sha256": "6f44b61e91d6d7b6ba80bb75391587bb4fa832b248281bd67d519516cde43f98"},
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_inputs(inputs):
    for name, digest in inputs.items():
        try:
            if sha(name) != digest:
                raise ValueError("owner input changed: " + name)
        except OSError as error:
            raise ValueError("owner input unavailable: " + name) from error


def profile_flags():
    return [value for name in PROFILE for value in ("--cfg", "fs_" + name)]


def require_profile(flags):
    if list(flags) != profile_flags():
        raise ValueError("owner profile must be the exact matched home selection")


def validate_measurement(value):
    stack = value.get("stack", {})
    try:
        valid = (value["code_budget"] == 49152 and 0 < value["code_bytes"] <= 49152
                 and value["code_fits"] is True and 0 < value["runtime_bytes"] <= 4096
                 and 0 < value["alignment"] <= 4096 and value["workspace_bytes"] == 4096
                 and value["mapped_bytes"] == 8192 and value["resident_fits"] is True
                 and value["runtime_bytes"] + value["workspace_bytes"] <= 8192
                 and value["native_executed"] is False and stack["status"] == "pass"
                 and stack["usable_stack_bytes"] == 8184
                 and 0 < stack["entry_stack_bytes"] <= 8184)
    except (KeyError, TypeError):
        valid = False
    if not valid:
        raise ValueError("owner measurement exceeds or omits the fixed resource contract")


def literal(path, name):
    values = [node.value for node in ast.walk(ast.parse(path.read_text()))
              if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name
                                                       for t in node.targets)]
    if len(values) != 1:
        raise ValueError("owner recipe literal is not unique: " + name)
    return ast.literal_eval(values[0])


def rust_sources(roots):
    """Bounded module inventory; compiler dep-info independently checks consumption."""
    pending = list(roots)
    found = set()
    while pending:
        path = pending.pop().resolve()
        if path in found:
            continue
        text = path.read_text()
        found.add(path)
        if re.search(r"\binclude(?:_bytes|_str)?!", text):
            raise ValueError("owner source needs an explicit include recipe: " + str(path))
        for name in re.findall(r'\bpath\s*=\s*"([^"]+\.rs)"', text):
            pending.append(path.parent / name)
        for name in re.findall(r'^\s*(?:pub(?:\([^)]*\))?\s+)?mod\s+(\w+)\s*;', text, re.M):
            for candidate in (path.parent / (name + ".rs"), path.parent / name / "mod.rs"):
                if candidate.is_file():
                    pending.append(candidate)
    return found


def build(system, work, proc, tools, deadline, record):
    system, work = Path(system).resolve(), Path(work).resolve()
    sysdir = system / "sys-init"
    source = system / "userland/experiments/filesystem-service"
    owner = sysdir / "prototypes/native-filesystem-session"
    wire = source / "check-home-wire.py"
    original = sysdir / "scripts/check-home-owner.py"
    observation = sysdir / "scripts/check-file-write-observations.py"
    pins_path = system / "userland/docs/evidence/filesystem-transport-2026-10-19/inputs.json"
    verify_inputs({str(pins_path): "f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d"})
    pins = json.loads(pins_path.read_text())
    selected_tools = {name: pins["tools"][name] for name in
                      ("rustc", "clippy-driver", "clang", "clang-format", "nm", "readelf")}
    selected_tools.update(SUPPLEMENTAL)
    for name, pin in selected_tools.items():
        if name in tools and any(tools[name].get(key) != pin[key] for key in ("path", "sha256")):
            raise ValueError("owner tool selection differs: " + name)
        tools[name] = pin
    inputs = {str(pins_path): sha(pins_path)}
    inputs.update({pin["path"]: pin["sha256"] for pin in selected_tools.values()})
    inputs.update(pins["rust_native_libraries"])
    inputs.update(pins["clang_resource_headers"])
    runtime = Path(selected_tools["clang"]["path"]).parent.parent / "lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib"
    inputs[str(runtime)] = "7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746"
    producer_crates = literal(original, "producer_crates")
    owner_crates = literal(observation, "OWNER_CRATES")
    producer_common = literal(wire, "COMMON")
    native = literal(wire, "NATIVE")
    if tuple(literal(wire, "PROFILE")) != PROFILE[:11]:
        raise ValueError("owner original profile changed")
    flags = profile_flags()
    require_profile(flags)
    common = ["--edition=2024", "-Dwarnings", "-Dunsafe_op_in_unsafe_fn"]
    owner_native = [*native, "-Copt-level=z", "-Cjump-tables=no"]
    roots = [source / filename for _, filename, _ in producer_crates]
    roots += [owner / filename for _, filename, _ in owner_crates]
    roots += [owner / "owner_entry.rs", owner / "native_owner.rs"]
    files = rust_sources(roots)
    files.update((Path(__file__).resolve(), sysdir / "tests/home_owner_build_tests.py", wire,
                  original, observation, sysdir / "scripts/owner_compare.py",
                  sysdir / "scripts/owner_measure.py", system / "scripts/owner_stack.py",
                  sysdir / "tests/owner_compare.c", system / "docs/native-fs-owner-stack-v1.json",
                  system / "kernel/arch/x86_64/native_fs_roles.zig",
                  system / "userland/docs/quality/clang-format.yaml", Path(sys.executable).resolve(),
                  system / "userland/experiments/command-runner/process.py"))
    inputs.update({str(path): sha(path) for path in files})
    inputs[str(system / "userland/experiments/command-runner/process.py")] = "9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e"
    compare = runpy.run_path(str(sysdir / "scripts/owner_compare.py"))
    sdk = system / ".deps/native-current/sdk"
    inputs[str(sdk / "musl-1.2.6.tar.gz")] = compare["ARCHIVE_SHA"]
    inputs.update({str(sdk / "stage/usr/include" / name): digest
                   for name, digest in compare["HEADERS"].items()})
    inputs["/usr/bin/xcrun"] = sha("/usr/bin/xcrun")
    verify_inputs(inputs)
    record.setdefault("inputs", {}).update(inputs)
    record.setdefault("sources", {}).update(inputs)
    record.setdefault("tools", {}).update(selected_tools)
    generated = record.setdefault("home_owner_generated", {})
    artifacts = record.setdefault("home_owner_artifacts", {})
    record["home_owner_recipe"] = dict(producer_crates=producer_crates, owner_crates=owner_crates,
        profile=flags, producer_common=producer_common, producer_native=[*native, "-Cjump-tables=no"],
        owner_common=common, owner_native=owner_native, sdk_path=str(sdk), sdk_resolved=str(sdk.resolve()),
        scope="native matched graph plus original comparison/fit helpers; no host891 repeat or native execution")
    env = proc.clean_env(work)

    def generated_sources():
        for path in work.rglob("*"):
            if path.is_file() and (path.suffix in (".c", ".h", ".rs", ".ld") or path.name == "COPYRIGHT"):
                name, digest = str(path), sha(path)
                if name in generated and generated[name] != digest:
                    raise ValueError("owner generated input changed: " + name)
                generated[name] = digest

    def run(label, argv, expected=0, stdout_only=False):
        args = list(map(str, argv))
        verify_inputs(inputs)
        generated_sources()
        verify_inputs(generated)
        verify_inputs(artifacts)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError("owner target deadline before " + label)
        child_env = env.copy()
        if Path(args[0]).name in ("rustc", "clippy-driver", "rust-lld"):
            child_env["DYLD_LIBRARY_PATH"] = str(Path(selected_tools["rustc"]["path"]).parent.parent / "lib")
        result = proc.run(args, cwd=sysdir, env=child_env, work=work, label=label,
                          timeout=min(180, remaining))
        record.setdefault("rows", []).append(dict(label=label, expected_exit=expected,
            process=result.record, stdout=result.stdout.decode(errors="replace")[-7000:],
            stderr=result.stderr.decode(errors="replace")[-5000:]))
        verify_inputs(artifacts)
        artifacts.update({str(p): sha(p) for p in work.rglob("*")
            if p.is_file() and p.suffix in (".rlib", ".rmeta", ".o", ".elf", ".bin", ".d")})
        verify_inputs(inputs)
        verify_inputs(generated)
        if (result.returncode != expected or not result.record["complete"]
                or result.record["cleanup"] != "complete" or time.monotonic() > deadline):
            raise ValueError("owner child failed: " + label)
        return result.stdout if stdout_only else result.stdout + result.stderr

    run("home-owner-constructor-tests", [sys.executable, "-O", "-B", "-m", "unittest", "discover",
        "-s", sysdir / "tests", "-p", "home_owner_build_tests.py"])
    host_sdk = Path(run("owner-host-sdk", ["/usr/bin/xcrun", "--show-sdk-path"],
                        stdout_only=True).decode().strip())
    if not host_sdk.is_absolute() or not host_sdk.is_dir():
        raise ValueError("owner host SDK selection")
    record["home_owner_host_sdk"] = str(host_sdk)

    def deps(folder, producer, names):
        result = ["-Ldependency=" + str(folder), "-Ldependency=" + str(producer)]
        for name in names:
            root = producer if name.startswith("filesystem_") else folder
            result += ["--extern", name + "=" + str(root / ("lib" + name + ".rlib"))]
        return result

    def compile_rust(label, argv):
        depfile = work / (label + ".d")
        args = list(argv)
        emission = next((i for i, arg in enumerate(args) if str(arg).startswith("--emit=")), None)
        if emission is None:
            args += ["--emit=link,dep-info=" + str(depfile)]
        else:
            args[emission] = str(args[emission]) + ",dep-info=" + str(depfile)
        result = run(label, args)
        consumed = set()
        for line in depfile.read_text().replace("\\\n", " ").splitlines():
            if ": " in line:
                consumed.update(line.split(": ", 1)[1].split())
        for name in consumed:
            path = Path(name)
            if not path.is_absolute():
                path = sysdir / path
            if str(path.resolve()) not in inputs and str(path.resolve()) not in generated:
                raise ValueError("owner compiler consumed unfrozen input: " + str(path))
        record.setdefault("home_owner_rust_dependencies", {})[label] = sorted(consumed)
        return result

    producer = work / "matched-native"
    folder = work / "home-owner-native"
    producer.mkdir()
    folder.mkdir()
    for name, filename, imports in producer_crates:
        selected_common = [arg for arg in producer_common if arg != "-Funsafe-code" or name not in
                           ("filesystem_metadata", "filesystem_client", "filesystem_remote_descriptors")]
        compile_rust("native-matched-" + name, [tools["rustc"]["path"], *selected_common,
            *flags, *native, "-Cjump-tables=no", *deps(producer, producer, imports),
            "--crate-type=lib", "--crate-name=" + name, "-Cmetadata=" + producer.name,
            source / filename, "-o", producer / ("lib" + name + ".rlib")])
    for name, filename, imports in owner_crates:
        arguments = [*common, *flags, *owner_native, *deps(folder, producer, imports),
                     "--crate-type=lib", "--crate-name=" + name, "-Cmetadata=" + folder.name,
                     owner / filename]
        compile_rust("native-home-owner-" + name, [tools["rustc"]["path"], *arguments,
                     "-o", folder / ("lib" + name + ".rlib")])
        compile_rust("native-home-owner-clippy-" + name, [tools["clippy-driver"]["path"], *arguments,
                     "--emit=metadata", "-o", folder / (name + ".rmeta")])
    compile_rust("native-home-owner-entry", [tools["rustc"]["path"], *common, *flags,
        *owner_native, "--crate-type=lib", "--crate-name=owner_entry", owner / "owner_entry.rs",
        "-o", folder / "libowner_entry.rlib"])

    def byte_run(label, argv, expected=0):
        args = list(map(str, argv))
        if Path(args[0]).name == "clang" and any(arg.endswith(".c") for arg in args):
            if not any(arg.startswith("--target=") for arg in args):
                args += ["-isysroot", str(host_sdk)]
            removed, skip = [], False
            for arg in args[1:]:
                if skip:
                    skip = False
                    continue
                if arg == "-o":
                    skip = True
                elif arg != "-c" and not arg.endswith(".o"):
                    removed.append(arg)
            output = run(label + "-dependencies", [args[0], *removed, "-M"]).decode()
            for name in output.replace("\\\n", " ").split(":", 1)[1].split():
                path = Path(name)
                if not path.is_absolute():
                    path = sysdir / path
                if path.is_relative_to(work):
                    generated[str(path)] = sha(path)
                else:
                    inputs[str(path)] = sha(path)
            record["inputs"].update(inputs)
        if Path(args[0]).name == "rustc":
            return compile_rust(label, args)
        return run(label, args, expected)

    obj, record["home_owner_comparison"] = compare["prepare"](system, work, byte_run, tools)
    imports = [name for name, _, _ in owner_crates] + [name for name, _, _ in producer_crates] + ["owner_entry"]
    measure = runpy.run_path(str(sysdir / "scripts/owner_measure.py"))["measure"]
    measured = measure(system, work, Path(tools["rustc"]["path"]), tools, byte_run,
                       deps(folder, producer, imports), ["-Clink-arg=" + str(obj)],
                       guarded_stack=True, extra_cfg=flags, file_layout=True)
    record["home_owner_measurement"] = measured
    validate_measurement(measured)
    elf, raw = work / "owner.elf", work / "owner.bin"
    if sha(elf) != measured["elf_sha256"] or sha(raw) != measured["raw_sha256"]:
        raise ValueError("owner measurement artifact identity")
    generated_sources()
    verify_inputs(inputs)
    verify_inputs(generated)
    record["inputs"].update(inputs)
    record["sources"].update(inputs)
    record["home_owner_generated_recipes"] = dict(comparison=record["home_owner_comparison"],
        linker="original owner_measure.measure linker literal", runtime_layout="original owner_measure.measure file_layout=True",
        dependency_info="same rustc/clippy argv with dep-info added; no source copies")
    return dict(elf=elf, raw=raw, measurement=measured)
