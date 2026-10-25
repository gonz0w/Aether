#!/usr/bin/env python3
"""Rebuild pinned musl with the opt-in native C transport; no target execution here."""
import argparse
import os
import hashlib
import json
import re
from pathlib import Path
import shlex
import struct
import subprocess
import tarfile
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--fault-first", action="store_true", help="build a deliberately faulting first native instance")
parser.add_argument("--supervised", action="store_true", help="build the native service lifecycle fixture")
parser.add_argument("--io", action="store_true", help="build the bounded descriptor facade and I/O probe")
parser.add_argument("--memory", action="store_true", help="add native-memory v1 to the I/O fixture")
args = parser.parse_args()
if args.memory and not args.io: parser.error("--memory requires --io")
if args.io and (args.supervised or args.fault_first): parser.error("choose one probe variant")
if args.supervised and args.fault_first: parser.error("choose one variant")

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LOCK = json.loads((HERE.parent / "musl-reference/tools.lock.json").read_text())
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
out = Path(tempfile.mkdtemp(prefix="native-c-", dir=ROOT / "build"))
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
# Native transport experiment: separate interrupt vector and operation namespace.
# Preserve musl internal errno/calling conventions; unsupported operations fail in kernel.
header = source / "arch/x86_64/syscall_arch.h"
text = header.read_text().replace('"syscall"', '"int $0x81"').replace('"a"(n)', '"a"(n + 0x10000)')
if args.io:
    text = "long __aether_io(unsigned long, unsigned long, unsigned long, unsigned long);\n" + text
    import re as _re
    def intercept(match):
        argc = int(match.group(1))
        if argc < 1: return match.group(0)
        params = ["a1", "a2" if argc >= 2 else "0", "a3" if argc >= 3 else "0"]
        return match.group(0) + "\n    if (n == 0 || n == 1 || n == 3 || n == 32 || n == 33) return __aether_io(n, " + ", ".join(params) + ");"
    text = _re.sub(r"static __inline long __syscall([0-6])\([^)]*\)\s*\{", intercept, text)
header.write_text(text)
for assembly in (source / "src").rglob("*.s"):
    if "x86_64" in assembly.parts:
        text = assembly.read_text()
        text = re.sub(r"(?m)^(\s*)syscall(?=\s|$)", r"\1add $0x10000,%rax\n\1int $0x81", text)
        assembly.write_text(text)
# UL-029: native allocator must not ignore unavailable metadata protection.
# Keep Linux reference sources unchanged; apply only to this fresh native tree.
reference_patch = HERE.parent / "musl-reference/metadata-protection-strict.patch"
reference_evidence = json.loads((HERE.parent / "musl-reference/adapter-errors-evidence.json").read_text())
require(digest(reference_patch) == reference_evidence["strict_patch_sha256"], "Strict patch evidence mismatch")
malloc_source = source / "src/malloc/mallocng/malloc.c"
original_malloc = malloc_source.read_text()
old_check = "if (mprotect(p, pagesize, PROT_READ|PROT_WRITE)\n\t\t\t    && errno != ENOSYS)"
new_check = "if (mprotect(p, pagesize, PROT_READ|PROT_WRITE))"
require(original_malloc.count(old_check) == 1, "Strict metadata protection anchor changed")
patch_before = digest(malloc_source)
malloc_source.write_text(original_malloc.replace(old_check, new_check))
libc_patches = [{"name": "strict-metadata-protection", "path": "src/malloc/mallocng/malloc.c",
    "before_sha256": patch_before, "after_sha256": digest(malloc_source),
    "old": old_check, "new": new_check, "reference_patch_sha256": digest(reference_patch),
    "reference_evidence_sha256": digest(HERE.parent / "musl-reference/adapter-errors-evidence.json")}]
# UL-015: never report a rejected provider as success or read its result.
# Exact upstream identities keep these adaptations scoped to musl 1.2.6.
for name, relative, before, old, new in (
    ("checked-realtime-fallback", "src/time/clock_gettime.c",
     "b767ffab3299d29ecfff46807b3dd106ad99d503de7f853733ac592ebd51047c",
     "\t\t\t__syscall(SYS_gettimeofday, ts, 0);",
     "\t\t\tr = __syscall(SYS_gettimeofday, ts, 0);\n\t\t\tif (r) return __syscall_ret(r);"),
    ("checked-physical-page-query", "src/conf/sysconf.c",
     "803fa64a3da9fac2377d96929d964e9e39c825fbd382c101885ea96693db61ec",
     "\t\t__lsysinfo(&si);", "\t\tif (__lsysinfo(&si)) return -1;"),
):
    target = source / relative
    require(digest(target) == before, "Provider source changed: " + relative)
    original = target.read_text()
    require(original.count(old) == 1, "Provider guard anchor changed: " + relative)
    target.write_text(original.replace(old, new))
    libc_patches.append({"name": name, "path": relative,
        "before_sha256": before, "after_sha256": digest(target),
        "old": old, "new": new})
(out / "native-libc-patches.json").write_text(json.dumps(libc_patches, indent=2) + "\n")
build_env = dict(env, CC=shlex.join(cc), AR=tools["ar"], RANLIB=tools["ranlib"], LIBCC=" ")
# Nonempty whitespace disables configure's automatic GCC-runtime selection.
# Static archive construction and these probes need no compiler builtins;
# missing helpers are link errors, not stubbed implementations.
run("configure", [str(source / "configure"), "--target=x86_64-linux-musl",
    "--prefix=/usr", "--disable-shared", "--disable-wrapper"], out / "obj", run_env=build_env)
run("make", [tools["make"], "-j8"], out / "obj", run_env=build_env)
run("stage", [tools["make"], "DESTDIR=" + str(out / "stage"), "install"], out / "obj", run_env=build_env)
lib = out / "stage/usr/lib"
io_obj = []
if args.io:
    io_obj = [str(out / "native_io.o")]
    run("native-io-compile", cc[:-1] + ["-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-fno-stack-protector", "-c", str(HERE / "native_io.c"), "-o", io_obj[0]])
memory_obj = []
if args.memory:
    for name in ("native_memory", "memory_probe"):
        target = str(out / (name + ".o"))
        run(name + "-compile", cc[:-1] + ["-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-nostdinc", "-isystem", str(out / "stage/usr/include"), "-fno-builtin", "-fstack-protector-strong", "-c", str(HERE / (name + ".c")), "-o", target])
        memory_obj.append(target)
probe = HERE / ("io_probe.c" if args.io else "probe.c")
variants = ("startup", "bad-dup", "memory-retry") if args.memory else (("startup", "bad-dup") if args.io else ("startup",))
for variant in variants:
    if args.io: io_obj = [str(out / "native_io.o")]
    if args.memory:
        memory_obj[-1] = str(out / "memory_probe.o")
        if variant == "memory-retry":
            target = str(out / "memory_retry.o")
            run("memory-retry-compile", cc[:-1] + ["-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-nostdinc", "-isystem", str(out / "stage/usr/include"), "-fno-builtin", "-fstack-protector-strong", "-DREQUIRE_METADATA_RETRY", "-c", str(HERE / "memory_probe.c"), "-o", target])
            memory_obj[-1] = target
    if variant == "bad-dup":
        io_obj = [str(out / "bad_io.o")]
        run("bad-io-compile", cc[:-1] + ["-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-fno-stack-protector", "-DAETHER_BAD_DUP", "-c", str(HERE / "native_io.c"), "-o", io_obj[0]])
    obj = out / (variant + ".o")
    run(variant + "-compile", cc[:-1] + ["-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
        "-nostdinc", "-isystem", str(out / "stage/usr/include"), "-fno-builtin",
        "-fstack-protector-strong"] + (["-DNATIVE_MEMORY"] if args.memory else []) + (["-DNATIVE_FAULT_FIRST"] if args.fault_first else []) + (["-DNATIVE_SUPERVISED"] if args.supervised else []) + (["-DWITH_ALLOCATOR"] if variant == "allocator" else []) +
        ["-c", str(probe), "-o", str(obj)])
    run(variant + "-link", cc + flags + ["-Wl,-Map," + str(out / (variant + ".map")),
        str(lib / "crt1.o"), str(lib / "crti.o"), str(obj)] + io_obj + memory_obj + [str(lib / "libc.a"),
        str(lib / "crtn.o"), "-o", str(out / (variant + ".elf"))])

artifacts = []
for name in ("sdk",) + variants:
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
    if name != "sdk": require(not sites, "Linux syscall instruction remains in native probe")
    (out / (name + "-syscall-sites.json")).write_text(json.dumps(sites, indent=2) + "\n")
    artifacts.append({"name": name, "sha256": digest(path), "bytes": len(data),
                      "static_syscall_instruction_sites": len(sites),
                      "program_headers": [list(h) for h in headers]})
evidence = {"scope": "native transport source rebuild and ELF inspection; target execution is separate",
            "output": str(out), "source_sha256": SOURCE["sha256"],
            "tools_lock_sha256": digest(HERE.parent / "musl-reference/tools.lock.json"),
            "probe_sha256": digest(probe), "script_sha256": digest(Path(__file__)),
            "io_adapter_sha256": digest(HERE / "native_io.c") if args.io else None,
            "native_memory": args.memory,
            "memory_sources": {name: digest(HERE / name) for name in ("native_memory.c", "memory_probe.c")} if args.memory else {},
            "libc_patches": libc_patches, "libc_archive_sha256": digest(lib / "libc.a"),
            "compiler_runtime": "none linked; 128-bit division deliberately fails",
            "checks": ["no host header", "no host libc", "missing helper rejected",
                       "static ELF64 x86-64", "no unresolved externals/relocations", "no WX load", "NX stack", "TLS in musl probes"],
            "artifacts": artifacts}
(out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
(out / "native-c.bin").write_bytes(b"AENATC01" + os.urandom(32) + (out / "startup.elf").read_bytes())
if args.io:
    (out / "bad-dup.bin").write_bytes(b"AENATC01" + (out / "native-c.bin").read_bytes()[8:40] + (out / "bad-dup.elf").read_bytes())
if args.memory:
    (out / "memory-retry.bin").write_bytes(b"AENATC01" + (out / "native-c.bin").read_bytes()[8:40] + (out / "memory-retry.elf").read_bytes())
evidence["envelope_sha256"] = digest(out / "native-c.bin")
evidence["probe_variant"] = "io" if args.io else "supervised" if args.supervised else ("fault-first" if args.fault_first else "positive")
evidence["native_entry"] = "int 0x81; operation namespace 0x10000 + retained musl internal call number"
evidence["entropy"] = "host-generated per-build developer bootstrap input; no native entropy service or production security claim"
(out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
print("PASS: pinned native musl source rebuild; native-c.bin ready for explicit Aether experiment", flush=True)
