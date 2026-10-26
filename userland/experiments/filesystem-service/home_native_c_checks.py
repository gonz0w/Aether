# SPDX-License-Identifier: BSD-2-Clause
"""Imported selected C lifecycle checks; the caller owns runner/deadline/cleanup."""
import hashlib
import json
from pathlib import Path
import runpy
import sys
import time

S = Path(__file__).resolve().parent
R = S.parents[1]
ROOT = R.parent
PINS = R / "docs/evidence/filesystem-transport-2026-10-19/inputs.json"
PINS_SHA = "f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d"
sys.path.insert(0, str(ROOT / "scripts"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise RuntimeError(message)


def native_header_prefix(prefix, compiler, *, empty_sysroot=None, work=None):
    """Route the sealed prefix without choosing tools or dropping inputs."""
    from fs_host_dependencies import retained_input
    from source_paths import relocate

    require(isinstance(prefix, list) and prefix and
            all(isinstance(arg, str) and arg and "\0" not in arg
                for arg in prefix), "invalid native header prefix")
    require(prefix[0] == compiler["path"], "provider recipe compiler mismatch")
    require(sha(prefix[0]) == compiler["sha256"], "provider compiler changed")
    old = Path("/Users/cam/DEV/Aether")
    overlays = {old / "zig-out/fs-metadata-launch-ppqz1x6m/base/port" / name
                for name in ("resources", "allocation")}
    delivery = old / ("userland/build/service-deliveries/"
                      "filesystem-service-directories-2026-10-20-v1/source")
    resource = Path(compiler["path"]).parents[1] / "lib/clang/21/include"
    # Non-path options in the immutable provider recipe. Unknown driver and
    # preprocessor forwarding options must not hide another input path.
    nonpaths = {
        "--no-default-config", "--target=x86_64-linux-musl",
        "-std=gnu99", "-std=gnu11", "-O2", "-UNDEBUG",
        "-fno-strict-aliasing", "-fstack-protector-strong", "-nostdinc",
        "-fstack-usage", "-Wall", "-Wextra", "-Werror",
        "-ffunction-sections", "-fdata-sections",
    }
    omitted = []

    def route(value, flag):
        path = Path(value)
        require(path.is_absolute() and ".." not in path.parts and
                str(path) == value, "invalid native header path: " + value)
        if path in overlays:
            require(flag == "-I" and not path.exists() and
                    not path.is_symlink(), "old overlay is not disposed")
            omitted.append({"flag": flag, "path": value})
            return None
        if path == old / ".deps/native-current/sdk/empty-root":
            require(flag == "--sysroot" and empty_sysroot is not None and
                    work is not None, "empty sysroot requires owned selection")
            owned = Path(work)
            selected = Path(empty_sysroot)
            require(owned.is_absolute() and owned == owned.resolve() and
                    owned.is_dir() and
                    selected == owned / "home-c/empty-root" and
                    selected == selected.resolve() and selected.is_dir() and
                    not any(selected.iterdir()), "invalid owned empty sysroot")
            return str(selected)
        current = relocate(path)
        if path == delivery:
            selected = S
        elif current.is_relative_to(ROOT / "user/storage/openzfs-volume"):
            selected = current
        elif current.is_relative_to(ROOT / ".deps/native-current"):
            selected = retained_input(current)
        elif path.is_relative_to(resource):
            selected = path
        else:
            raise RuntimeError("unknown native header path: " + value)
        require(selected == selected.resolve(),
                "native header path alias: " + str(selected))
        exists = (selected.is_file() if flag == "-include"
                  else selected.is_dir())
        require(exists, "missing native header input: " + str(selected))
        return str(selected)

    routed = [prefix[0]]
    index = 1
    while index < len(prefix):
        arg = prefix[index]
        index += 1
        if arg in ("-I", "-isystem", "-include", "--sysroot"):
            require(index < len(prefix),
                    "missing native header operand: " + arg)
            value = route(prefix[index], arg)
            index += 1
            if value is not None:
                routed.extend((arg, value))
        elif arg.startswith("-I"):
            value = route(arg[2:], "-I")
            if value is not None:
                routed.append("-I" + value)
        elif arg.startswith("--sysroot="):
            value = route(arg.split("=", 1)[1], "--sysroot")
            routed.append("--sysroot=" + value)
        elif arg.startswith("-fmacro-prefix-map="):
            mapping = arg[len("-fmacro-prefix-map="):]
            value, separator, output = mapping.partition("=")
            require(separator and output, "malformed native macro-prefix-map")
            value = route(value, "-fmacro-prefix-map")
            require(value is not None, "macro map cannot omit an input")
            routed.append("-fmacro-prefix-map=" + value + "=" + output)
        else:
            # A -D operand is literal preprocessor data, including any slash
            # or option-like text in its value; it is never a path operand.
            require(arg in nonpaths or (arg.startswith("-D") and len(arg) > 2),
                    "unsupported native header argument: " + arg)
            routed.append(arg)
    return routed, omitted


def check(record, work, proc, tools, deadline):
    env = proc.clean_env(work)
    folder = work / "home-c"
    folder.mkdir()
    owned_sources = [S / "home-native.h", S / "home-native-lifecycle-tests.c",
                     S / "home_native_source.py", Path(__file__),
                     ROOT / "scripts/source_paths.py",
                     ROOT / "scripts/fs_host_dependencies.py",
                     *sorted((S / "home-native-host").rglob("*.h")),
                     S / "native-service.h",
                     ROOT / "user/storage/service-runtime/filesystem-engine.h",
                     ROOT / "user/storage/service-runtime/engine-observe.inc",
                     ROOT / "user/storage/openzfs-volume/pool-flow-witness.h",
                     ROOT / "user/storage/openzfs-volume/volume.h",
                     ROOT / "user/storage/openzfs-elapsed/startup-fixture.h",
                     ROOT / "user/storage/openzfs-elapsed/startup.h",
                     R / "experiments/native-service-runtime/runtime.h",
                     R / "experiments/native-utc/utc.h"]
    owned_sources.append(R / "docs/quality/clang-format.yaml")
    frozen = {str(path): sha(path) for path in owned_sources}
    require(sha(PINS) == PINS_SHA, "C tool input manifest changed")
    pins = json.loads(PINS.read_text())
    frozen[str(PINS)] = PINS_SHA
    for name in ("clang", "clang-format"):
        require(tools[name] == pins["tools"][name], "C tool selection mismatch: " + name)
        require(sha(tools[name]["path"]) == tools[name]["sha256"], "C tool changed: " + name)
    for name, digest in pins["clang_resource_headers"].items():
        require(sha(name) == digest, "Clang resource header changed: " + name)
        frozen[name] = digest
    ubsan = Path(tools["clang"]["path"]).parent.parent / "lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib"
    ubsan_sha = "7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746"
    require(sha(ubsan) == ubsan_sha, "UBSan runtime changed")
    frozen[str(ubsan)] = ubsan_sha
    record.setdefault("sources", {}).update(frozen)

    def run(label, argv, expected=0, timeout=30):
        remaining = deadline - time.monotonic()
        require(remaining > 0, "suite deadline before " + label)
        result = proc.run(list(map(str, argv)), cwd=R, env=env, work=work,
                          label=label, timeout=min(timeout, remaining))
        record["rows"].append({"label": label, "expected_exit": expected,
            "process": result.record,
            "stdout": result.stdout.decode(errors="replace")[-3000:],
            "stderr": result.stderr.decode(errors="replace")[-5000:]})
        record["home_c_artifacts"] = {str(path): sha(path) for path in folder.rglob("*")
            if path.is_file() and (path.suffix in (".o", ".su", ".d", ".c") or path.name == "lifecycle")}
        require(result.returncode == expected and result.record["complete"] and
                result.record["cleanup"] == "complete", label)
        return result

    generator = runpy.run_path(str(S / "home_native_source.py"))
    recipes = generator["generate"](folder)
    record["home_c_source_recipes"] = recipes
    for recipe in recipes:
        frozen[recipe["original"]] = recipe["sha256"]
        frozen[recipe["output"]] = recipe["output_sha256"]
    record["sources"].update(frozen)
    denials = []
    for label, operation in (
        ("original-source-hash", lambda: generator["render"](
            ROOT / next(iter(generator["ORIGINALS"])), "altered")),
        ("missing-anchor", lambda: generator["replace_once"]("none", "old", "new")),
        ("duplicate-anchor", lambda: generator["replace_once"]("old old", "old", "new")),
        ("outside-owned-build", lambda: generator["generate"](S)),
        ("existing-output", lambda: generator["generate"](folder)),
    ):
        try:
            operation()
        except ValueError as error:
            denials.append({"name": label, "error": str(error)})
        else:
            raise RuntimeError("generator denial did not reject: " + label)
    record["home_c_generator_denials"] = denials
    includes = ["-I" + str(S / "home-native-host"), "-I" + str(S),
                "-I" + str(ROOT / "user/storage/service-runtime"),
                "-I" + str(ROOT / "user/storage/openzfs-volume"),
                "-I" + str(ROOT / "user/storage/openzfs-elapsed"),
                "-I" + str(R / "experiments/native-service-runtime"),
                "-I" + str(R / "experiments/native-utc")]
    strict = ["-std=c17", "-D_DEFAULT_SOURCE", "-Wall", "-Wextra", "-Werror"]
    instrumentation = ["-DAETHER_FS_HOST_BLOCK_CLOSE=home_host_block_close",
                       "-include", str(S / "home-native-host/home-native-host.h")]
    sanitizer = ["-O1", "-g", "-fsanitize=undefined", "-fno-sanitize-recover=all"]
    generated = [folder / "home-filesystem-engine.c", folder / "home-filesystem-import.c"]
    fixture = S / "home-native-lifecycle-tests.c"
    command = [tools["clang"]["path"], *strict, *sanitizer, *instrumentation,
               *includes, *generated, fixture]
    run("home-c-lifecycle-build", [*command, "-o", folder / "lifecycle"])
    for case in range(69):
        result = run("home-c-lifecycle-" + str(case), [folder / "lifecycle", case])
        require(("case " + str(case) + " passed").encode() in result.stdout,
                "missing C lifecycle semantic marker")
    record["home_c_lifecycle_cases"] = 69
    # A compiling control executes these same original bodies. It removes only
    # the required original ordered oracle, and fails the fixed case's marker.
    control = folder / "skipped-order"
    control.mkdir()
    text = generated[1].read_text()
    old = "unsigned order_error = ordered_required ? aether_pool_hooks_check_ordered() : 0;"
    new = "unsigned order_error = 0; (void)ordered_required;"
    mutated = generator["replace_once"](text, old, new)
    mutant = control / "home-filesystem-import.c"
    mutant.write_text(mutated)
    run("home-c-skipped-order-control-build", [tools["clang"]["path"],
        *strict, *sanitizer, *instrumentation, *includes, generated[0], mutant,
        fixture, "-o", control / "lifecycle"])
    result = run("home-c-skipped-order-control", [control / "lifecycle", 19], expected=1)
    require(b"HOME_ORDER_ORACLE" in result.stderr, "order control failed for wrong reason")
    record.setdefault("controls", []).append({"name": "skipped-ordered-check",
        "source": str(generated[1]), "old": old, "new": new,
        "mutant_sha256": sha(mutant), "compiled": True,
        "semantic_oracle": "HOME_ORDER_ORACLE", "exit": 1})
    run("home-c-format", [tools["clang-format"]["path"], "--dry-run", "--Werror",
        "--style=file:" + str(R / "docs/quality/clang-format.yaml"),
        S / "home-native.h", fixture, *sorted((S / "home-native-host").rglob("*.h"))])
    layout = folder / "home-layout.c"
    layout.write_text('#include "home-native.h"\nint home_layout(void) { return 384; }\n')
    run("home-c-target-layout", [tools["clang"]["path"], *strict,
        "--target=x86_64-unknown-none", "-ffreestanding", "-fstack-usage",
        "-I" + str(S), "-I" + str(ROOT / "user/storage/service-runtime"),
        "-c", layout, "-o", folder / "layout.o"])
    packed = run("home-c-reject-packed-layout", [tools["clang"]["path"], *strict,
        "--target=x86_64-unknown-none", "-ffreestanding", "-fpack-struct=1",
        "-I" + str(S), "-I" + str(ROOT / "user/storage/service-runtime"),
        "-fsyntax-only", layout], expected=1)
    require(b"static assertion failed" in packed.stderr,
            "packed C carrier rejected for wrong reason")
    legacy = folder / "home-legacy-pointer.c"
    legacy.write_text('#include "home-native.h"\n'
        'int old_header_consumer(uint64_t grant, struct aether_fs_launch_state *out) {\n'
        '    return aether_fs_home_engine_run(grant, out);\n}\n')
    wrong_pointer = run("home-c-reject-legacy-launch-pointer", [tools["clang"]["path"],
        *strict, "--target=x86_64-unknown-none", "-ffreestanding",
        "-I" + str(S), "-I" + str(ROOT / "user/storage/service-runtime"),
        "-fsyntax-only", legacy], expected=1)
    require(b"incompatible pointer types" in wrong_pointer.stderr and
            b"aether_fs_launch_state" in wrong_pointer.stderr and
            b"aether_fs_home_launch_state" in wrong_pointer.stderr,
            "legacy C header rejected for wrong reason")
    record["home_c_compiler_denials"] = [
        {"name": "packed-carrier-alignment", "source_sha256": sha(layout),
         "diagnostic": "static assertion failed", "exit": 1},
        {"name": "legacy136-to-private384-pointer", "source_sha256": sha(legacy),
         "diagnostic": "incompatible pointer types", "exit": 1},
    ]
    # Use the actual retained original OpenZFS/native-header recipe. Only absent
    # obsolete per-run include overlays are omitted, and all consumed headers
    # are retained by identity. This is not a complete native engine closure.
    receipt = ROOT / ".deps/fs-launch-af07-2026-10-23-v13/build.json"
    require(sha(receipt) == "9f08c0717e4bf3b238d696361b6c1d3222d30f4fceeb2b35e5a9ad0058caa2a8",
            "native header recipe changed")
    frozen[str(receipt)] = sha(receipt)
    original = json.loads(receipt.read_text())
    old_command = next(row["argv"] for row in original["commands"] if
        "-c" in row["argv"] and any(str(arg).endswith("/metadata-provider.o") for arg in row["argv"]))
    requested = old_command[:old_command.index("-c")]
    empty_sysroot = folder / "empty-root"
    empty_sysroot.mkdir()
    prefix, missing = native_header_prefix(
        requested, tools["clang"], empty_sysroot=empty_sysroot, work=work)
    extra = ["-std=c17", "-Wall", "-Wextra", "-Werror", "-fstack-usage",
             "-I" + str(S), "-I" + str(ROOT / "user/storage/service-runtime")]
    record["home_c_original_header_recipe"] = {"receipt": str(receipt),
        "sha256": sha(receipt), "requested_argv": requested,
        "routed_argv": prefix, "omitted_missing_old_overlay_dirs": missing,
        "empty_sysroot": {
            "requested": "/Users/cam/DEV/Aether/"
                         ".deps/native-current/sdk/empty-root",
            "routed": str(empty_sysroot), "empty": True},
        "scope": "actual original provider/importer headers; no complete native engine"}
    from fs_host_dependencies import retained_input

    native_manifest = retained_input(
        ROOT / ".deps/native-current/current-inputs.json")
    native_manifest_sha = "0521371de06c44489426635890c4bb96bc820912ac7200c4294ff7eaea081d95"
    require(sha(native_manifest) == native_manifest_sha, "original native header manifest changed")
    frozen[str(native_manifest)] = native_manifest_sha
    native_files = json.loads(native_manifest.read_text())["files"]
    native_headers = {}
    record["home_c_original_header_inputs"] = native_headers
    record["sources"].update(frozen)
    for label, source in (("importer", generated[1]),
                           ("metadata-provider", ROOT / "user/storage/openzfs-volume/zpl-metadata.c"),
                           ("mkdir-provider", ROOT / "user/storage/openzfs-volume/zpl-directories.c"),
                           ("create-provider", ROOT / "user/storage/openzfs-volume/zpl-mutate.c")):
        dependencies = folder / (label + ".d")
        run("home-c-original-headers-" + label, [*prefix, *extra, "-M", source,
            "-MF", dependencies])
        headers = dependencies.read_text().replace("\\\n", " ").split(":", 1)[1].split()
        for name in headers:
            digest = sha(name)
            path = Path(name)
            native_root = native_manifest.parent
            if path.is_relative_to(native_root):
                member = path.relative_to(native_root).as_posix()
                require(native_files.get(member) == digest,
                        "original pinned native header mismatch: " + name)
            if name in pins["clang_resource_headers"]:
                require(pins["clang_resource_headers"][name] == digest,
                        "original Clang resource header mismatch: " + name)
            if name in frozen:
                require(frozen[name] == digest, "original header input changed: " + name)
            native_headers[name] = digest
            frozen.setdefault(name, digest)
            record["sources"][name] = digest
        run("home-c-original-" + label, [*prefix, *extra, "-c", source,
            "-o", folder / (label + ".o")])
    record["home_c_original_header_inputs"] = native_headers
    frozen.update(native_headers)
    record["sources"].update(frozen)
    record["home_c_artifacts"] = {str(path): sha(path) for path in folder.rglob("*")
        if path.is_file() and path.suffix in (".o", ".su", ".d")}
    record["home_c_artifacts"].update({str(path): sha(path) for path in
        (folder / "lifecycle", control / "lifecycle", *generated)})
    record["home_c_local_frames"] = {str(path): path.read_text() for path in folder.rglob("*.su")}
    require(empty_sysroot == empty_sysroot.resolve() and
            not any(empty_sysroot.iterdir()), "owned empty sysroot changed")
    for name, digest in frozen.items():
        require(sha(name) == digest, "C input changed during frozen run: " + name)
    record["home_c_limits"] = "Typed host instrumentation and target objects; no ZFS/native execution, native peak or full engine fit."
