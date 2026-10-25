#!/usr/bin/env python3
"""Offline, pinned host build/ELF inspection. Does not run Linux binaries."""
import hashlib
import json
import re
from pathlib import Path
import shlex
import struct
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LOCK = json.loads((HERE / "tools.lock.json").read_text())
SOURCE = json.loads((ROOT / "docs/research/musl-1.2.6-evidence.json").read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


tools = {}
for name, item in LOCK["tools"].items():
    p = Path(item["path"])
    require(digest(p) == item["sha256"], "Tool changed: " + name)
    tools[name] = str(p)
archive = ROOT / "build/musl-audit/musl-1.2.6.tar.gz"
require(digest(archive) == SOURCE["sha256"], "Source archive hash mismatch")
(ROOT / "build").mkdir(exist_ok=True)
out = Path(tempfile.mkdtemp(prefix="musl-reference-", dir=ROOT / "build"))
require(not any(c.isspace() for c in str(out)), "musl configure requires a path without whitespace in this experiment")
print("Output: " + str(out), flush=True)
for name in ("empty-root", "obj", "stage", "tmp"):
    (out / name).mkdir()
# Explicit environment prevents CPATH/LIBRARY_PATH/SDKROOT/config injection.
env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "LC_ALL": "C",
       "TMPDIR": str(out / "tmp")}
commands = []


def run(label, args, cwd=out, expected=0, run_env=None):
    result = subprocess.run(args, cwd=cwd, env=run_env or env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out / (label + ".log")).write_bytes(result.stdout)
    commands.append({"label": label, "argv": args, "cwd": str(cwd),
                     "exit_code": result.returncode})
    (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
    require((result.returncode == 0) if expected == 0 else (result.returncode != 0),
            "Unexpected result for " + label + "; inspect its log")
    return result.stdout.decode(errors="replace")


cc = [tools["clang"], "--no-default-config", "--target=x86_64-linux-musl",
      "--sysroot=" + str(out / "empty-root"), "-fuse-ld=" + tools["lld"]]
flags = ["-nostdlib", "-static", "-Wl,-z,noexecstack", "-Wl,--no-undefined"]
run("sdk-link", cc + flags + ["-ffreestanding", "-fno-stack-protector",
    "-Wl,-e,aether_probe_add", str(ROOT / "experiments/c-object/probe.c"),
    "-o", str(out / "sdk.elf")])
(out / "header.c").write_text("#include <host-only.h>\nint x;\n")
# The wrapper intentionally supplies only the allowlisted environment, even if
# the user launching this script has set compiler search-path variables.
header_error = run("no-host-header", cc[:-1] + ["-c", str(out / "header.c"), "-o", str(out / "header.o")], expected=1)
require("'host-only.h' file not found" in header_error, "Header test failed for an unrelated reason")
libc_error = run("no-host-libc", cc + flags + ["-Wl,-e,aether_probe_add",
    str(ROOT / "experiments/c-object/probe.c"), "-lc", "-o", str(out / "bad.elf")], expected=1)
require("unable to find library -lc" in libc_error, "Library test failed for an unrelated reason")
(out / "helper.c").write_text("unsigned __int128 divide(unsigned __int128 a, unsigned __int128 b) { return a/b; }\n")
helper = run("missing-builtins", cc + flags + ["-Wl,-e,divide", str(out / "helper.c"),
             "-o", str(out / "helper.elf")], expected=1)
require("__udivti3" in helper, "Missing compiler runtime test failed for an unrelated reason")
with tarfile.open(archive) as tf:
    tf.extractall(out, filter="data")
source = out / "musl-1.2.6"
build_env = dict(env, CC=shlex.join(cc), AR=tools["ar"], RANLIB=tools["ranlib"], LIBCC=" ")
# Nonempty whitespace disables configure's automatic GCC-runtime selection.
# Static archive construction and these probes need no compiler builtins;
# missing helpers are link errors, not stubbed implementations.
run("configure", [str(source / "configure"), "--target=x86_64-linux-musl",
    "--prefix=/usr", "--disable-shared", "--disable-wrapper"], out / "obj", run_env=build_env)
run("make", [tools["make"], "-j8"], out / "obj", run_env=build_env)
run("stage", [tools["make"], "DESTDIR=" + str(out / "stage"), "install"], out / "obj", run_env=build_env)
lib = out / "stage/usr/lib"
for variant in ("startup", "allocator"):
    obj = out / (variant + ".o")
    run(variant + "-compile", cc[:-1] + ["-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
        "-nostdinc", "-isystem", str(out / "stage/usr/include"), "-fno-builtin",
        "-fstack-protector-strong"] + (["-DWITH_ALLOCATOR"] if variant == "allocator" else []) +
        ["-c", str(HERE / "probe.c"), "-o", str(obj)])
    run(variant + "-link", cc + flags + ["-Wl,-Map," + str(out / (variant + ".map")),
        str(lib / "crt1.o"), str(lib / "crti.o"), str(obj), str(lib / "libc.a"),
        str(lib / "crtn.o"), "-o", str(out / (variant + ".elf"))])

artifacts = []
for name in ("sdk", "startup", "allocator"):
    path = out / (name + ".elf")
    data = path.read_bytes()
    require(data[:6] == b"\x7fELF\x02\x01", "Wrong ELF class/endianness")
    require(struct.unpack_from("<HH", data, 16) == (2, 62), "Wrong ELF type/machine")
    phoff = struct.unpack_from("<Q", data, 32)[0]
    size, count = struct.unpack_from("<HH", data, 54)
    headers = [struct.unpack_from("<IIQQQQQQ", data, phoff + i * size) for i in range(count)]
    require(not any(h[0] in (2, 3) for h in headers), "Dynamic segment/interpreter")
    require(not any(h[0] == 1 and h[1] & 3 == 3 for h in headers), "Writable executable load segment")
    require(any(h[0] == 0x6474e551 and not h[1] & 1 for h in headers), "Missing NX stack")
    if name != "sdk":
        require(any(h[0] == 7 for h in headers), "Missing TLS segment")
    require(not run(name + "-undefined", [tools["nm"], "--undefined-only", "--extern-only", str(path)]).strip(), "Unresolved external symbols")
    # LLD retains musl's hidden weak _DYNAMIC as a local zero-valued UND
    # symbol in static output. It is not an external dependency or relocation.
    symbols = run(name + "-symbols", [tools["readelf"], "-s", str(path)])
    for line in symbols.splitlines():
        if " UND " in line:
            fields = line.split()
            require(len(fields) == 7 or
                    (fields[1] == "0000000000000000" and fields[4:8] == ["LOCAL", "HIDDEN", "UND", "_DYNAMIC"]),
                    "Unexpected undefined symbol: " + line)
    relocs = run(name + "-relocations", [tools["readelf"], "-r", str(path)])
    require("There are no relocations" in relocs, "Unexpected relocations")
    run(name + "-headers", [tools["readelf"], "-h", "-l", "-d", str(path)])
    disassembly = run(name + "-disassembly", [tools["objdump"], "-d", str(path)])
    sites, function = [], "unknown"
    for line in disassembly.splitlines():
        match = re.match(r"[0-9a-f]+ <(.+)>:", line)
        if match:
            function = match.group(1)
        if re.search(r"\bsyscall\s*$", line):
            sites.append({"function": function, "instruction": line.strip()})
    (out / (name + "-syscall-sites.json")).write_text(json.dumps(sites, indent=2) + "\n")
    artifacts.append({"name": name, "sha256": digest(path), "bytes": len(data),
                      "static_syscall_instruction_sites": len(sites),
                      "program_headers": [list(h) for h in headers]})
evidence = {"scope": "host build/link/inspection only; binaries NOT executed",
            "output": str(out), "source_sha256": SOURCE["sha256"],
            "tools_lock_sha256": digest(HERE / "tools.lock.json"),
            "probe_sha256": digest(HERE / "probe.c"), "script_sha256": digest(Path(__file__)),
            "compiler_runtime": "none linked; 128-bit division deliberately fails",
            "checks": ["no host header", "no host libc", "missing helper rejected",
                       "static ELF64 x86-64", "no unresolved externals/relocations", "no WX load", "NX stack", "TLS in musl probes"],
            "artifacts": artifacts}
(out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
print("PASS: SDK isolation and both musl reference links; no runtime claim", flush=True)
