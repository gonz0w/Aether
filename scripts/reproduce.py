# SPDX-License-Identifier: BSD-2-Clause
"""Rebuild the current source snapshot with fresh Zig caches and run M4 checks."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

from deps import ROOT, verify
from regression import Parser

EXCLUDED = {"__pycache__", ".DS_Store"}


def inventory(root, excluded_roots=()):
    result = {}
    for path in sorted(root.rglob("*")):
        if path.relative_to(root).parts[0] in excluded_roots:
            continue
        if any(part in EXCLUDED for part in path.relative_to(root).parts):
            continue
        if path.is_symlink():
            raise RuntimeError(f"snapshot inputs must not be symlinks: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise RuntimeError(f"snapshot input is not a regular file/directory: {path}")
    return result


def verify_sources(source, expected):
    current = inventory(source, excluded_roots=(".deps", ".zig-cache", "zig-out"))
    if current != expected:
        added = sorted(current.keys() - expected.keys())
        removed = sorted(expected.keys() - current.keys())
        changed = sorted(name for name in current.keys() & expected.keys()
                         if current[name] != expected[name])
        raise RuntimeError(f"snapshot source changed during build: added={added}, "
                           f"removed={removed}, modified={changed}")


def tool_identity(command, env):
    located = shutil.which(command, path=env.get("PATH", os.defpath))
    if located is None:
        raise FileNotFoundError(f"required executable not found: {command}")
    path = Path(located).absolute()
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        raise RuntimeError(f"tool is not a regular file: {resolved}")
    with resolved.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"path": str(path), "resolved_path": str(resolved), "sha256": digest}


def verify_tool(command, expected, env):
    if tool_identity(command, env) != expected:
        raise RuntimeError(f"tool identity changed during reproduction: {command}")


def rust_compiler(source, env):
    result = subprocess.run(["rustc", "--print", "sysroot"], cwd=source, env=env,
                            capture_output=True, text=True, check=True, timeout=20)
    return str(Path(result.stdout.strip()) / "bin" / "rustc")


def reproduce():
    verify()
    # A disposable clean build, never copy existing build outputs/caches or .git.
    work = Path(tempfile.mkdtemp(prefix="aether-reproduce-", dir="/tmp"))
    source = work / "source"
    source.mkdir()
    print("[RUNNING] Source reproduction evidence:", work, file=sys.stderr, flush=True)
    record = {"format": "aether-source-reproduction-v1", "status": "incomplete",
              "origin": str(ROOT), "snapshot": str(source),
              "host": platform.platform(), "machine": platform.machine(),
              "limits": ["local working-tree snapshot, not independent committed checkout",
                         "installed tools and previously fetched verified boot dependencies reused",
                         "no enforced network confinement or bit-identical output claim",
                         "native-C optional image and sibling integration suites excluded"],
              "steps": []}
    try:
        for name in ("build.zig", "rust-toolchain.toml", "README.md", "AGENTS.md", "LICENSE"):
            path = ROOT / name
            if path.is_symlink() or not path.is_file():
                raise RuntimeError(f"invalid source input: {path}")
            shutil.copy2(path, source / name)
        for name in ("kernel", "user", "scripts", "tests", "boot", "docs", ".planning"):
            # Inventory first so copytree cannot silently dereference symlinks.
            inventory(ROOT / name) if name != "docs" else None
            shutil.copytree(ROOT / name, source / name, symlinks=True,
                            ignore=shutil.ignore_patterns("__pycache__", ".DS_Store",
                                                         "archive", "evidence"))
        record["sources"] = inventory(source)
        shutil.copytree(ROOT / ".deps", source / ".deps", symlinks=True,
                        ignore=shutil.ignore_patterns("native-current", "sources"))
        record["dependencies"] = inventory(source / ".deps")
        record["fresh_caches"] = not (source / ".zig-cache").exists()
        env = os.environ.copy()
        env["ZIG_GLOBAL_CACHE_DIR"] = str(source / ".zig-cache/global")
        tools = {"zig": ["zig", "version"], "rust": ["rustc", "-vV"],
                 "qemu": ["qemu-system-x86_64", "--version"],
                 "xorriso": ["xorriso", "-version"], "python": [sys.executable, "--version"]}
        record["tools"] = {}
        identities = {}
        for name, command in tools.items():
            identities[name] = tool_identity(command[0], env)
            record["tools"][name] = {**identities[name], "version_command": command}
            result = subprocess.run(command, cwd=source, env=env, capture_output=True,
                                    text=True, check=True, timeout=20)
            verify_tool(command[0], identities[name], env)
            record["tools"][name]["version"] = result.stdout + result.stderr
        compiler = rust_compiler(source, env)
        compiler_identity = tool_identity(compiler, env)
        record["rust_compiler"] = compiler_identity
        record["rust_compiler_command"] = ["rustc", "--print", "sysroot"]
        commands = [
            ("host", ["zig", "build", "test", "--cache-dir", ".zig-cache",
                      "--global-cache-dir", ".zig-cache/global"]),
            ("target", [sys.executable, "scripts/regression.py"]),
            ("one-core", ["zig", "build", "smoke", "-Dsmp=false", "-p", "zig-out/one-core",
                          "--cache-dir", ".zig-cache", "--global-cache-dir", ".zig-cache/global"]),
        ]
        for name, command in commands:
            step = {"name": name, "command": command, "cwd": str(source), "status": "incomplete"}
            record["steps"].append(step)
            print("[RUNNING]", name, file=sys.stderr, flush=True)
            with (work / f"{name}.log").open("wb") as log:
                subprocess.run(command, cwd=source, env=env, stdout=log,
                               stderr=subprocess.STDOUT, check=True, timeout=900)
            step["status"] = "pass"
        for name, command in tools.items():
            verify_tool(command[0], identities[name], env)
        verify_tool(rust_compiler(source, env), compiler_identity, env)
        verify_sources(source, record["sources"])
        if inventory(source / ".deps") != record["dependencies"]:
            raise RuntimeError("dependencies changed during build")
        record["artifacts"] = inventory(source / "zig-out")
        record["status"] = "pass"
    except BaseException as error:
        record.update(status="failed", error=str(error))
        raise
    finally:
        # source was created by this run, not supplied by the caller. Keep its
        # identity/diagnostics, then discard the source/dependency/build caches.
        record["artifact_retention"] = "cleanup pending"
        (work / "results.json").write_text(json.dumps(record, indent=2) + "\n")
        try:
            if source.is_symlink() or source.parent != work:
                raise RuntimeError("reproduction source ownership changed")
            shutil.rmtree(source)
        except BaseException as error:
            record.update(status="failed", cleanup_error=str(error))
            (work / "results.json").write_text(json.dumps(record, indent=2) + "\n")
            raise
        record["artifact_retention"] = "compact; generated source/build tree removed"
        (work / "results.json").write_text(json.dumps(record, indent=2) + "\n")
    print("[PASS] Source reproduction completed. Evidence:", work)


if __name__ == "__main__":
    parser = Parser(description=__doc__, epilog="Example: python3 scripts/reproduce.py. "
                    "Requires completed pinned dependency setup. Retains a private /tmp/aether-reproduce-* "
                    "directory with compact results/logs; generated source/build/cache copies are removed.")
    parser.add_argument("--version", action="version", version="aether-source-reproduction 1")
    parser.parse_args()
    try:
        reproduce()
    except KeyboardInterrupt:
        sys.exit(130)
    except (OSError, RuntimeError, TimeoutError, subprocess.SubprocessError) as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        sys.exit(1)
