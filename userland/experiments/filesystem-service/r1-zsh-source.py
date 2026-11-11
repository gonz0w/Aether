# SPDX-License-Identifier: BSD-2-Clause
"""Build pinned Zsh and its selected terminfo reader from local source archives.

This is a reproducible source-build entry, not an authenticated-source or runtime
qualification claim. It consumes the repository's exact archive hashes and an
already-built current native-C SDK.
"""
import hashlib
import json
import re
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from shutil import copyfileobj

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "sys-init/scripts"))
from bounded_tools import run_tool as bounded_run_tool

MANIFEST = ROOT / "userland/docs/zsh-consumer-v1.json"
BUILD = None
SDK = None
SOURCE_ARCHIVES = None
TOOLS = {}
LLVM = None
LLD = None
PATCH = Path("/usr/bin/patch")
TOOLS_LOCK_PATH = None
TOOL_RUN_NUMBER = 0
F = ROOT / "userland/experiments/filesystem-service"
MUSL_ARCHIVE_SHA256 = "d585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a"
EXEC_EXTERNAL_PATCH_SHA256 = "22067734f21b907c9c59c9865e5ee3585dd3ed06e7b65295f3afbef7ad78b31f"
EXEC_SOURCE_SHA256 = "989efb3a21ed259f16c24f773d964fafe614994abf516a1f6f49f51072296184"
EXEC_EXTERNAL_SOURCE_SHA256 = "54d9b786e74650f50d7d74fc715989c692a57ed1c96f62f379b0a9c724cceac2"
SOURCE_DATE_EPOCH = "1767225600"

UNITS = ("fd-client", "fd-facade", "fd-routing", "fd-table", "fd-write", "fd-pipe",
         "fd-replace", "fd-session", "fd-redirect", "fd-native", "fd-context", "fd-startup",
         "fd-native-trap", "fd-startup-native", "fd-libc", "fd-libc-bindings")
PROCESS_UNITS = ("fd-zsh-process", "fd-fork-stage", "fd-fork-native", "fd-exec", "fd-exec-native")
STDIO_UNITS = ("__stdio_write", "fopen", "__stdio_read", "__stdio_seek")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(argv, cwd, env):
    global TOOL_RUN_NUMBER
    TOOL_RUN_NUMBER += 1
    print("+", " ".join(map(str, argv)), flush=True)
    log_dir = BUILD / "tool-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{TOOL_RUN_NUMBER:03d}-{Path(str(argv[0])).name}.log"
    scratch = BUILD / "tmp"
    scratch.mkdir(exist_ok=True)
    return bounded_run_tool(list(map(str, argv)), dict(env, TMPDIR=str(scratch)), log_path, timeout=180,
                            limit=4 * 1024 * 1024, cwd=cwd)


def zsh_exec_frames(zsh):
    rows = [row.split("\t") for row in (zsh / "Src/exec.su").read_text().splitlines()]
    frames = {row[0].rsplit(":", 1)[-1]: {"bytes": int(row[1]), "kind": row[2]} for row in rows}
    names = ("execute", "execute_path", "execute_dash", "zexecve")
    selected = {name: frames[name] for name in names}
    if (any(row["kind"] != "static" for row in selected.values())
            or selected["execute"]["bytes"] >= 1024
            or any(row["bytes"] >= 49152 for row in selected.values())):
        raise SystemExit("actual Zsh exec local frames exceed the approved scoped bounds")
    return selected


def build_modules(text):
    selected = {"zsh/main", "zsh/zle", "zsh/complete", "zsh/compctl"}
    result = []
    for line in text.splitlines():
        if not line.startswith("name="):
            continue
        fields = dict(item.split("=", 1) for item in line.split(" functions=", 1)[0].split())
        if fields["name"] != "zsh/main":
            active = fields["name"] in selected
            fields.update(link="static" if active else "no", auto="no", load="yes" if active else "no")
        result.append(" ".join(k + "=" + v for k, v in fields.items()) + " functions=")
    if not result:
        raise SystemExit("Zsh configure emitted no module records")
    return result


def provider_flags(base, profile, helper=False):
    flags = list(base)
    if profile["filesystem"]:
        flags = [f for f in flags if f != "-DAEFD_TERMINAL_CANONICAL_BINDINGS"]
        flags += ["-DAEFD_ZSH_FILESYSTEM_BINDINGS", "-DAEFD_ZSH_DIAGNOSTIC"]
    if profile["external"]:
        flags += ["-DAEFD_ZSH_PROCESS_BINDINGS", "-DAEFD_EXTERNAL_STARTUP"]
    if profile["home_redirection"]:
        flags += ["-DAEFD_ZSH_HOME_REDIRECTION_BINDINGS"]
    if profile["login_startup"]:
        flags += ["-DAEFD_ZSH_LOGIN_STARTUP_BINDINGS"]
    if profile["home_cwd"]:
        flags += ["-DAEFD_ZSH_HOME_CWD_BINDINGS"]
    if profile["home_cwd_exec"]:
        flags += ["-DAEFD_ZSH_HOME_CWD_EXEC_BINDINGS"]
    if profile["operator_note"]:
        flags += ["-DAEFD_ZSH_OPERATOR_NOTE_BINDINGS"]
    if helper:
        flags = [x for x in flags if x not in ("-DAEFD_ZSH_DIAGNOSTIC", "-DAEFD_ZSH_OPERATOR_NOTE_BINDINGS")]
        flags += ["-DAEFD_ZSH_HELPER_ENTRY"]
    return flags


def musl_stdio_sources(musl, provider):
    substitutions = {
        "__stdio_write": [("syscall(SYS_writev, f->fd, iov, iovcnt)",
                            "aether_zsh_vector_write(f->fd, iov, iovcnt)")],
        "fopen": [("sys_open(filename, flags, 0666)", "aether_zsh_open(filename, flags, 0666)"),
                  ("__syscall(SYS_fcntl, fd, F_SETFD, FD_CLOEXEC)",
                   "aether_zsh_raw_fcntl(fd, F_SETFD, FD_CLOEXEC)"),
                  ("__syscall(SYS_close, fd)", "aether_zsh_raw_close(fd)")],
        "__stdio_read": [("syscall(SYS_readv, f->fd, iov, 2)",
                          "aether_zsh_vector_read(f->fd, iov, 2)"),
                         ("syscall(SYS_read, f->fd, iov[1].iov_base, iov[1].iov_len)",
                          "aether_zsh_read(f->fd, iov[1].iov_base, iov[1].iov_len)")],
        "__stdio_seek": [("__lseek(f->fd, off, whence)", "aether_zsh_seek(f->fd, off, whence)")],
    }
    source_paths = {
        "__stdio_write": musl / "src/stdio/__stdio_write.c",
        "fopen": musl / "src/stdio/fopen.c",
        "__stdio_read": musl / "src/stdio/__stdio_read.c",
        "__stdio_seek": musl / "src/stdio/__stdio_seek.c",
    }
    expected = {"fopen": "acc229d7ab6b99808b59615a860dcb023058737ed757aa74672c45cdafdef34e",
                "__stdio_read": "22c7bf41ecc8427ef69a2aefe4aa5f19e5504ed377a47ea9c06b62866d8c2a5f",
                "__stdio_seek": "02a6231c5ba3b012d097ea9646d6e85bfb396d6f49061363915a3277a25e57b6"}
    outputs = {}
    for name in STDIO_UNITS:
        path = source_paths[name]
        if name in expected and digest(path) != expected[name]:
            raise SystemExit(f"pinned musl stdio source changed: {name}")
        text = path.read_text()
        for old, new in substitutions[name]:
            if text.count(old) != 1:
                raise SystemExit(f"expected exactly one musl {name} call seam: {old}")
            text = text.replace(old, new)
        prefix = '#include <unistd.h>\n' if name == "__stdio_seek" else ""
        out = provider / (name + ".c")
        out.write_text(prefix + '#include "fd-zsh-external.h"\n' + text)
        outputs[name] = out
    return outputs


def compile_provider(name, src, output, flags):
    extra = ["-D__real__exit=__real__Exit"] if name in (
        "fd-zsh-external", "fd-libc-bindings", "fd-fork-native", "fd-exec-native",
        "fd-zsh-helper-entry") else []
    run([LLVM / "clang", *flags, *extra, "-c", src, "-o", output], output.parent,
        {"PATH": f"{LLVM}:/usr/bin:/bin", "LC_ALL": "C"})


def compile_staged_fork(musl, provider, internal):
    original = musl / "src/process/_Fork.c"
    text = original.read_text()
    anchor = "ret = __syscall(SYS_fork);"
    if (digest(original) != "3821faa03c1718620f1f4804133aa7473065c2f34f9cb49708b7930787e0e9e5"
            or text.count(anchor) != 1 or text.count("__post_Fork(ret);") != 1):
        raise SystemExit("pinned upstream musl _Fork seam is missing or changed")
    arch = SDK / "musl-1.2.6/arch/x86_64"
    if digest(arch / "syscall_arch.h") != "dbb8acfc335a8e2231556cca2fd55b5efaecba31a48f5cd4ea95a5eff13d2d30":
        raise SystemExit("guarded SDK architecture syscall header changed")
    source, obj = provider / "_Fork.c", provider / "_Fork.o"
    source.write_text("long __aether_fork_stage(void);\n" + text.replace(anchor, "ret = __aether_fork_stage();"))
    # Preserve the original musl child repair, but use Aether's trap transport.
    compile_provider("_Fork", source, obj, ["-I" + str(arch),
                     *(f for f in internal if f not in ("-Wextra", "-Werror"))])
    code = run([TOOLS["objdump"], "-dr", obj], provider,
               {"PATH": f"{LLVM}:/usr/bin:/bin", "LC_ALL": "C"}).decode("ascii")
    if (not re.search(r"\bint\s+\$(?:0x81|129)\b", code)
            or not re.search(r"\bmovl\s+\$(?:0x100da|65754), %eax", code, re.I)
            or re.search(r"^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+syscall\b", code, re.M)
            or code.count("__aether_fork_stage") != 1):
        raise SystemExit("staged _Fork must call Aether staging and use the Aether child TID trap")
    return obj


def build_zsh_profile(label, profile, roots, musl, nc, work, probe_object, sdk_lib, sdk_inc, exec_derived):
    zsh = work / ("zsh-" + label)
    provider = work / ("providers-" + label)
    zsh.mkdir()
    provider.mkdir()
    base = ["--no-default-config", "--target=x86_64-unknown-none", "-std=c17", "-O2", "-Wall", "-Wextra", "-Werror",
            "-ffreestanding", "-fno-builtin", "-fstack-protector-strong", "-ffunction-sections", "-fdata-sections",
            "-ffile-prefix-map=" + str(ROOT) + "=/src/aether", "-ffile-prefix-map=" + str(BUILD) + "=/build/aether",
            "-fstack-usage", "-nostdinc", "-isystem", str(sdk_inc), "-DAEFD_TERMINAL_CANONICAL_BINDINGS", "-I" + str(F)]
    common = provider_flags(base, profile)
    entries = []
    for name in (*UNITS, "fd-zsh-external", "fd-tinfo-directory", *PROCESS_UNITS):
        src = F / (name + ".c")
        out = provider / (name + ".o")
        compile_provider(name, src, out, common)
        entries.append(out)
    memory = provider / "memory.o"
    compile_provider("memory", ROOT / "user/native-memory/adapter.c", memory,
                     [*common, "-D__aether_io=aether_zsh_unused_memory_io"])
    entries.append(memory)

    stdio = musl_stdio_sources(musl, provider)
    internal = ["--no-default-config", "--target=x86_64-unknown-none", "-std=c17", "-O2", "-Wall", "-Wextra",
                "-Werror", "-ffreestanding", "-fno-builtin", "-fstack-protector-strong", "-ffunction-sections",
                "-fdata-sections", "-fstack-usage", "-nostdinc", "-I" + str(musl / "arch/x86_64"),
                "-isystem", str(musl / "src/include"), "-isystem", str(sdk_inc), "-I" + str(F),
                "-isystem", str(musl / "src/internal"), "-isystem", str(musl / "arch/x86_64"),
                "-ffile-prefix-map=" + str(ROOT) + "=/src/aether", "-ffile-prefix-map=" + str(BUILD) + "=/build/aether",
                "-D_GNU_SOURCE", "-Wno-sign-compare", *common[len(base):]]
    for name, source in stdio.items():
        out = provider / (name + ".o")
        compile_provider(name, source, out, internal)
        entries.append(out)

    rebind = provider / "rebind.o"
    compile_provider("rebind", ROOT / "user/native-connections/rebind.c", rebind,
                     [*internal, "-I" + str(musl / "src/internal"), "-DREBIND_LIBC_REPAIR"])
    entries.extend((rebind, compile_staged_fork(musl, provider, internal)))

    configure_flags = [f for f in common if f not in
                       ("-DAEFD_ZSH_DIAGNOSTIC", "-DAEFD_ZSH_OPERATOR_NOTE_BINDINGS")]
    configure_ext = provider / "configure-fd-zsh-external.o"
    configure_libc_bindings = provider / "configure-fd-libc-bindings.o"
    compile_provider("fd-zsh-external", F / "fd-zsh-external.c", configure_ext, configure_flags)
    compile_provider("fd-libc-bindings", F / "fd-libc-bindings.c", configure_libc_bindings, configure_flags)
    configure_objects = [configure_ext if path.name == "fd-zsh-external.o" else
                         configure_libc_bindings if path.name == "fd-libc-bindings.o" else path
                         for path in entries]

    # Build source objects with the established static-module set.
    env = {}
    zflags = provider_flags([], profile)
    build_cflags = ("-Oz -ffunction-sections -fdata-sections -std=gnu17 -fstack-protector-strong -fstack-usage "
                    f"-ffile-prefix-map={ROOT}=/src/aether -ffile-prefix-map={BUILD}=/build/aether")
    zsh_cc = zsh / "target-cc"
    zsh_cc.write_text("""#!/bin/sh
link=yes
source=no
for arg do
  case "$arg" in -c|-E|-S|-M|-MM|--version|-V|-qversion|-version) link=no;;
    *.c|*.o|*.s|*.S) source=yes;; esac
done
if [ "$source" = no ]; then link=no; fi
selected=()
for arg do
  if [ "$arg" = """ + str(roots["zsh"] / "Src/exec.c") + """ ]; then
    selected+=(""" + str(exec_derived) + """)
  else
    selected+=("$arg")
  fi
done
common=(--no-default-config --target=x86_64-linux-musl --sysroot=""" + str(SDK / "empty-root") +
        """ -ffreestanding -fno-builtin -ffile-prefix-map=""" + str(ROOT) + """=/src/aether -ffile-prefix-map=""" + str(BUILD) +
        """=/build/aether -nostdinc -isystem """ + str(sdk_inc) + """ )
if [ "$link" = yes ]; then
  exec """ + str(LLVM / "clang") + """ "${common[@]}" -fuse-ld=""" + str(LLD) +
        """ -nostdlib -static -Wl,--no-undefined,-z,noexecstack,--wrap=main,--wrap=_exit,--wrap=_Exit -L""" + str(sdk_lib) + " " +
        str(sdk_lib / "crt1.o") + " " + str(sdk_lib / "crti.o") + " \"${selected[@]}\" " +
        str(sdk_lib / "libc.a") + " " +
        str(sdk_lib / "crtn.o") + "\nelse\n  exec " + str(LLVM / "clang") +
        " \"${common[@]}\" \"${selected[@]}\"\nfi\n")
    zsh_cc.chmod(0o700)
    env.update(PATH=f"{LLVM}:/usr/bin:/bin:/usr/sbin:/sbin", LC_ALL="C", SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH,
               TZ="UTC", CC=str(zsh_cc),
               AR=str(TOOLS["ar"]), RANLIB=str(TOOLS["ranlib"]), CFLAGS=build_cflags,
               CPPFLAGS=" ".join(["-I" + str(nc / "include"), "-I" + str(F), *provider_flags([], profile)]),
               LDFLAGS="-L" + str(nc / "lib"), LIBS=" ".join([*(str(x) for x in configure_objects), str(nc / "lib/libtinfo.a")]),
               CONFIG_SITE="/dev/null", PKG_CONFIG="/usr/bin/false",
               zsh_cv_ignore_ncurses="yes", zsh_cv_sys_fifo="no", zsh_cv_sys_lseek="no", zsh_cv_sys_link="no",
               ac_cv_func_wait3="no", ac_cv_func_waitpid="yes")
    zflags = ["--disable-dynamic", "--enable-multibyte", "--with-term-lib=tinfo", "--disable-pcre",
              "--disable-gdbm", "--disable-cap", "--enable-etcdir=no", "--enable-libc-musl",
              "--build=aarch64-apple-darwin", "--host=x86_64-linux-musl", "--prefix=/usr"]
    run(["/bin/sh", roots["zsh"] / "configure", *zflags], zsh, env)
    modules = build_modules((zsh / "config.modules").read_text())
    (zsh / "config.modules").write_text("\n".join(modules) + "\n")
    run([TOOLS["make"], "-j2", "CFLAGS=" + build_cflags, "headers", "stamp-modobjs", "main.o"], zsh / "Src", env)
    names = (zsh / "Src/stamp-modobjs").read_text().split()
    if not names or len(names) != len(set(names)):
        raise SystemExit("Zsh module output list is empty or contains duplicates")
    zsh_objects = [zsh / "Src/main.o", *[zsh / "Src" / name for name in names]]
    if not all(path.is_file() for path in zsh_objects):
        raise SystemExit("Zsh source build omitted a selected module object")

    # Owner-backed provider objects are linked beside the actual Zsh objects.
    core = [provider / (name + ".o") for name in (*UNITS, "fd-zsh-external")]
    tail = [path for path in entries if path not in core]
    wraps = ["--wrap=getuid", "--wrap=geteuid", "--wrap=getgid", "--wrap=getegid", "--wrap=access",
             "--wrap=getcwd"]
    if profile["home_cwd"]:
        wraps.append("--wrap=chdir")
    link = [LLD, *wraps, "--wrap=tgetent", "-static", "--no-undefined", "--gc-sections",
            "-z", "noexecstack", "--wrap=main", "--wrap=_exit", "--wrap=_Exit", "-Map=" + str(zsh / "zsh.map"),
            sdk_lib / "crt1.o", sdk_lib / "crti.o", *core[-1:], *zsh_objects, *core[:-1], *tail,
            nc / "lib/libtinfo.a", sdk_lib / "libc.a", sdk_lib / "crtn.o", "-o", zsh / "zsh.elf"]
    run(link, zsh, {"PATH": f"{LLVM}:/usr/bin:/bin", "LC_ALL": "C"})
    binary = zsh / "zsh.elf"
    raw = binary.read_bytes()
    if raw[:6] != b"\x7fELF\x02\x01" or int.from_bytes(raw[18:20], "little") != 62:
        raise SystemExit(f"{label} linked output is not ELF64 x86-64")
    unresolved = run([TOOLS["nm"], "--undefined-only", "--extern-only", binary], zsh,
                     {"PATH": f"{LLVM}:/usr/bin:/bin", "LC_ALL": "C"}).decode().strip()
    if unresolved:
        raise SystemExit(f"{label} Zsh has unresolved symbols: {unresolved[:500]}")
    frames = zsh_exec_frames(zsh)
    print(f"LINKED {label} path={binary} bytes={len(raw)} sha256={digest(binary)}")
    print(f"STACK {label} exec_frames={json.dumps(frames, sort_keys=True)}")
    return binary, frames


def build_helper_profile(label, profile, musl, work, sdk_lib, sdk_inc):
    directory = work / ("helper-" + label)
    provider = directory / "providers"
    provider.mkdir(parents=True)
    base = ["--no-default-config", "--target=x86_64-unknown-none", "-std=c17", "-O2", "-Wall", "-Wextra", "-Werror",
            "-ffreestanding", "-fno-builtin", "-fstack-protector-strong", "-ffunction-sections", "-fdata-sections",
            "-ffile-prefix-map=" + str(ROOT) + "=/src/aether", "-ffile-prefix-map=" + str(BUILD) + "=/build/aether",
            "-fstack-usage", "-nostdinc", "-isystem", str(sdk_inc), "-DAEFD_TERMINAL_CANONICAL_BINDINGS", "-I" + str(F)]
    common = provider_flags(base, profile, helper=True)
    providers = []
    for name in (*UNITS, "fd-zsh-external", "fd-tinfo-directory", *PROCESS_UNITS, "fd-zsh-helper-entry"):
        out = provider / (name + ".o")
        compile_provider(name, F / (name + ".c"), out, common)
        providers.append(out)
    memory = provider / "memory.o"
    compile_provider("memory", ROOT / "user/native-memory/adapter.c", memory,
                     [*common, "-D__aether_io=aether_zsh_unused_memory_io"])
    stdio = musl_stdio_sources(musl, provider)
    internal = ["--no-default-config", "--target=x86_64-unknown-none", "-std=c17", "-O2", "-Wall", "-Wextra",
                "-Werror", "-ffreestanding", "-fno-builtin", "-fstack-protector-strong", "-ffunction-sections",
                "-fdata-sections", "-ffile-prefix-map=" + str(ROOT) + "=/src/aether",
                "-ffile-prefix-map=" + str(BUILD) + "=/build/aether", "-fstack-usage", "-nostdinc",
                "-I" + str(musl / "arch/x86_64"), "-isystem", str(musl / "src/include"), "-isystem", str(sdk_inc),
                "-I" + str(F), "-isystem", str(musl / "src/internal"), "-isystem", str(musl / "arch/x86_64"),
                "-D_GNU_SOURCE", "-Wno-sign-compare", *common[len(base):]]
    for name, source in stdio.items():
        out = provider / (name + ".o")
        compile_provider(name, source, out, internal)
        providers.append(out)
    providers.append(memory)
    rebind = provider / "rebind.o"
    compile_provider("rebind", ROOT / "user/native-connections/rebind.c", rebind,
                     [*internal, "-I" + str(musl / "src/internal"), "-DREBIND_LIBC_REPAIR"])
    fork = compile_staged_fork(musl, provider, internal)

    helper_main = directory / "helper-main.o"
    payload = ROOT / "user/native-command/dash-helper-inputs/helper.c"
    if digest(payload) != "3fdea5d515011e49516f35cf8b9abdc214024a226bb3ba560480fa9775cebcf8":
        raise SystemExit("pinned Zsh helper payload changed")
    compile_provider("helper-main", payload, helper_main, common)
    entry = provider / "fd-zsh-helper-entry.o"
    wrap = ["--wrap=main", "--wrap=_exit", "--wrap=_Exit", "--wrap=getuid", "--wrap=geteuid",
            "--wrap=getgid", "--wrap=getegid", "--wrap=access", "--wrap=getcwd"]
    if profile["home_cwd"]:
        wrap.append("--wrap=chdir")
    binary = directory / "helper.elf"
    rest = [p for p in providers if p != entry]
    run([LLD, "-static", "--no-undefined", "--gc-sections", "-z", "noexecstack", *wrap,
         "-Map=" + str(directory / "helper.map"), sdk_lib / "crt1.o", sdk_lib / "crti.o",
         entry, helper_main, *rest, rebind, fork, sdk_lib / "libc.a", sdk_lib / "crtn.o",
         "-o", binary], directory, {"PATH": f"{LLVM}:/usr/bin:/bin", "LC_ALL": "C"})
    raw = binary.read_bytes()
    if raw[:6] != b"\x7fELF\x02\x01" or int.from_bytes(raw[18:20], "little") != 62:
        raise SystemExit(f"{label} helper is not ELF64 x86-64")
    unresolved = run([TOOLS["nm"], "--undefined-only", "--extern-only", binary], directory,
                     {"PATH": f"{LLVM}:/usr/bin:/bin", "LC_ALL": "C"}).decode().strip()
    if unresolved:
        raise SystemExit(f"{label} helper has unresolved symbols: {unresolved[:500]}")
    print(f"LINKED {label} helper path={binary} bytes={len(raw)} sha256={digest(binary)}")
    return binary


def extract(archive, destination):
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:*") as source:
        members = source.getmembers()
        if len(members) > 10_000 or sum(member.size for member in members) > 64 * 1024 * 1024:
            raise SystemExit(f"archive expansion exceeds limit: {archive.name}")
        for member in members:
            parts = Path(member.name).parts
            if Path(member.name).is_absolute() or ".." in parts or not (member.isfile() or member.isdir()):
                raise SystemExit(f"unsafe source archive member: {member.name}")
        for member in members:
            target = (destination / member.name).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise SystemExit(f"source archive escaped extraction root: {member.name}")
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            stream = source.extractfile(member)
            if stream is None:
                raise SystemExit(f"source archive member has no data: {member.name}")
            with stream, target.open("wb") as output:
                copyfileobj(stream, output)
            target.chmod(member.mode & 0o777)


def _main():
    for path in (ROOT, BUILD, SDK, SOURCE_ARCHIVES, *TOOLS.values()):
        if not re.fullmatch(r"[A-Za-z0-9_./+@-]+", str(path)):
            raise SystemExit(f"unsupported configure/make path: {path}")
    manifest = json.loads(MANIFEST.read_text())
    sources = {s["name"]: s for s in manifest["sources"]}
    archive_dir = SOURCE_ARCHIVES
    archives = {"zsh": archive_dir / "zsh-5.9.2.tar.xz",
                "ncurses": archive_dir / "ncurses-6.6.tar.gz",
                "musl": archive_dir / "musl-1.2.6.tar.gz"}
    for name, path in archives.items():
        expected = MUSL_ARCHIVE_SHA256 if name == "musl" else sources[name]["sha256"]
        if not path.is_file() or digest(path) != expected:
            raise SystemExit(f"missing or wrong pinned {name} archive: {path}")
    clang = LLVM / "clang"
    ar = TOOLS["ar"]
    ranlib = TOOLS["ranlib"]
    if not clang.is_file() or not ar.is_file() or not ranlib.is_file():
        raise SystemExit(f"pinned LLVM 21 toolchain missing under {LLVM}")
    lib = SDK / "stage/usr/lib"
    inc = SDK / "stage/usr/include"
    if not (lib / "libc.a").is_file() or not (inc / "stdio.h").is_file():
        raise SystemExit(f"incomplete native-C SDK: {SDK}")

    if BUILD.exists():
        raise SystemExit(f"refusing to overwrite existing build output: {BUILD}")
    src = BUILD / "src"
    work = BUILD / "work"
    src.mkdir(parents=True)
    work.mkdir()
    extract(archives["zsh"], src)
    extract(archives["ncurses"], src)
    extract(archives["musl"], src)
    roots = {"zsh": src / "zsh-5.9.2", "ncurses": src / "ncurses-6.6", "musl": src / "musl-1.2.6"}
    for name, root in roots.items():
        if not (root / "configure").is_file():
            raise SystemExit(f"unexpected {name} archive root: {root}")

    # Configure is cross-only. All target compilation consumes the same explicit
    # SDK headers; there is no host libc or implicit host-header search.
    wrapper = work / "target-cc"
    wrapper.write_text("""#!/bin/sh
link=yes
source=no
for arg do
  case "$arg" in -c|-E|-S|-M|-MM|--version|-V|-qversion|-version) link=no;;
    *.c|*.o|*.s|*.S) source=yes;; esac
done
if [ "$source" = no ]; then link=no; fi
common=(--no-default-config --target=x86_64-linux-musl --sysroot=""" + str(SDK / "empty-root") + """ -ffreestanding -fno-builtin -ffile-prefix-map=""" + str(ROOT) + """=/src/aether -ffile-prefix-map=""" + str(BUILD) + """=/build/aether -nostdinc -isystem """ + str(inc) + """ )
if [ "$link" = yes ]; then
  exec """ + str(clang) + """ "${common[@]}" -fuse-ld=""" + str(LLD) + """ -nostdlib -static -Wl,--no-undefined,-z,noexecstack -L""" + str(lib) + """ """ + str(lib / "crt1.o") + " """ + str(lib / "crti.o") + """ "$@" """ + str(lib / "libc.a") + " """ + str(lib / "crtn.o") + """
else
  exec """ + str(clang) + """ "${common[@]}" "$@"
fi
""")
    wrapper.chmod(0o700)
    # The current libc deliberately routes host-style I/O through an injected
    # owner provider. Configure probes need a link-only stub; it is never linked
    # into a shell executable or represented as runtime evidence.
    probe_source = work / "configure-io-stub.c"
    probe_object = work / "configure-io-stub.o"
    probe_source.write_text("long __aether_io(unsigned long a,unsigned long b,unsigned long c,unsigned long d) { (void)a;(void)b;(void)c;(void)d; return -1; }\n")
    run([wrapper, "-c", probe_source, "-o", probe_object], work,
        {"PATH": f"{LLVM}:/usr/bin:/bin", "LC_ALL": "C"})
    wrapper.write_text(wrapper.read_text().replace(' "$@" ' + str(lib / "libc.a"),
                                                      ' "$@" ' + str(probe_object) + ' ' + str(lib / "libc.a")))
    env = {}
    env.update(PATH=f"{LLVM}:/usr/bin:/bin:/usr/sbin:/sbin", LC_ALL="C", SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH, TZ="UTC",
               CC=str(wrapper), BUILD_CC="/usr/bin/clang", AR=str(ar), RANLIB=str(ranlib),
               CFLAGS=("-Oz -ffunction-sections -fdata-sections -std=gnu17 "
                       f"-ffile-prefix-map={ROOT}=/src/aether -ffile-prefix-map={BUILD}=/build/aether"),
               CONFIG_SITE="/dev/null", PKG_CONFIG="/usr/bin/false")
    cross = ["--build=aarch64-apple-darwin", "--host=x86_64-linux-musl", "--prefix=/usr"]
    nc = work / "ncurses"
    nc.mkdir()
    ncflags = ["--disable-widec", "--with-normal", "--without-shared", "--without-debug",
               "--with-termlib=tinfo", "--with-ticlib", "--without-progs", "--without-tests",
               "--without-cxx", "--without-cxx-binding", "--without-ada", "--disable-termcap",
               "--disable-home-terminfo", "--without-manpages", *cross,
               "--with-terminfo-dirs=/usr/share/terminfo",
               "--with-default-terminfo-dir=/usr/share/terminfo"]
    nc_patch = F / "fd-tinfo-directory.patch"
    if digest(roots["ncurses"] / "ncurses/tinfo/db_iterator.c") != "b822256e5f9a806c0e608bf608f5f0e271ce38897bffa28e9beb764b537b76ca" or digest(nc_patch) != "64ff2817e14866c8b8ac72a205a16f8936e73fab311c682b3ca38f5839989b79":
        raise SystemExit("selected ncurses directory reader input or patch changed")
    run([PATCH, "--batch", "--fuzz=0", "-p1", "-i", nc_patch], roots["ncurses"], env)
    if digest(roots["ncurses"] / "ncurses/tinfo/db_iterator.c") != "fc2a5d5a6239768696bf60a22137c971a0512c53abedece5f49cf08ec0022544":
        raise SystemExit("selected ncurses directory-reader result changed")
    env["CFLAGS"] += " -DAEFD_ZSH_FILESYSTEM_BINDINGS -I" + str(F)
    run(["/bin/sh", roots["ncurses"] / "configure", *ncflags], nc, env)
    run([TOOLS["make"], "-j2", "CFLAGS=" + env["CFLAGS"], "sources"], nc, env)
    run([TOOLS["make"], "-j2", "CFLAGS=" + env["CFLAGS"], "../lib/libtinfo.a"], nc / "ncurses", env)

    exec_source = roots["zsh"] / "Src/exec.c"
    stack_patch = F / "zsh-execute-stack.patch"
    ext_patch = F / "zsh-execute-external.patch"
    if digest(exec_source) != EXEC_SOURCE_SHA256 or digest(stack_patch) != "e33a4811689e89ec98c32e21c54e44cbb9a98f18e41bb61f37ada2a3e104f66e" or digest(ext_patch) != EXEC_EXTERNAL_PATCH_SHA256:
        raise SystemExit("selected Zsh execute source or patch changed")
    exec_fs = work / "exec-filesystem.c"
    run([PATCH, "--batch", "--fuzz=0", "-o", exec_fs, exec_source, stack_patch], work, env)
    if digest(exec_fs) != "a75900e130dde28d0a767acdfa46fb74410447642d74b1ca5a6dc628064adaa0":
        raise SystemExit("selected Zsh execute stack result changed")
    exec_derived = work / "exec-external.c"
    run([PATCH, "--batch", "--fuzz=0", "-o", exec_derived, exec_fs, ext_patch], work, env)
    if digest(exec_derived) != EXEC_EXTERNAL_SOURCE_SHA256:
        raise SystemExit("selected Zsh external execute result changed")

    profiles = {
        "seed": dict(filesystem=True, external=True, home_redirection=True, login_startup=True,
                     home_cwd=False, home_cwd_exec=False, operator_note=False),
        "note": dict(filesystem=True, external=True, home_redirection=True, login_startup=True,
                     home_cwd=True, home_cwd_exec=True, operator_note=True),
    }
    # Same selected C ABI and static module set as the #160 seed / #170 note app fits.
    lddummy = work / "configure-io-stub.c"
    lddummy.write_text("long __aether_io(unsigned long a,unsigned long b,unsigned long c,unsigned long d) { (void)a;(void)b;(void)c;(void)d; return -1; }\n")
    sdk_lib, sdk_inc = SDK / "stage/usr/lib", SDK / "stage/usr/include"
    # Build each selected profile in a separate configured tree. The low-level
    # configure wrapper uses the SDK only; actual profile providers are linked below.
    zflags = ["--disable-dynamic", "--enable-multibyte", "--with-term-lib=tinfo",
              "--disable-pcre", "--disable-gdbm", "--disable-cap", "--enable-etcdir=no",
              "--enable-libc-musl", *cross]
    # Target-fit profiles differ in compile-time syscall ownership only. Configure
    # is rerun for each profile to preserve its independent generated config.
    run([LLVM / "clang", "--no-default-config", "--target=x86_64-unknown-none", "-ffreestanding", "-fno-builtin",
         "-nostdinc", "-isystem", sdk_inc, "-c", lddummy, "-o", work / "configure-io-stub.o"], work,
        {"PATH": f"{LLVM}:/usr/bin:/bin", "LC_ALL": "C"})
    outputs = {}
    frames = {}
    for label, profile in profiles.items():
        shell, frames[label] = build_zsh_profile(label, profile, roots, roots["musl"], nc, work,
                                                work / "configure-io-stub.o", sdk_lib, sdk_inc, exec_derived)
        outputs[label + "-zsh.elf"] = shell
        outputs[label + "-helper.elf"] = build_helper_profile(label, profile, roots["musl"], work, sdk_lib, sdk_inc)
    members = {}
    for name, source in outputs.items():
        target = BUILD / name
        shutil.copyfile(source, target)
        members[name] = dict(bytes=target.stat().st_size, sha256=digest(target))
        print(f"ARTIFACT {target} bytes={members[name]['bytes']} sha256={members[name]['sha256']}")
    (BUILD / "apps.json").write_text(json.dumps(dict(members=members, frames=frames),
                                              indent=2, sort_keys=True) + "\n")
    shutil.rmtree(src)
    shutil.rmtree(work)
    print(f"Retained four linked ELF inputs under {BUILD}; no runtime claim.")


def main():
    global BUILD, SDK, SOURCE_ARCHIVES, TOOLS, LLVM, LLD
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", required=True, type=Path, help="fresh built native-C SDK directory")
    parser.add_argument("--sources", required=True, type=Path,
                        help="offline directory containing the three pinned release archives")
    parser.add_argument("--tools-lock", required=True, type=Path,
                        help="current hash-pinned host tool manifest")
    parser.add_argument("--out-dir", type=Path, help="retain intermediate source trees and named ELF outputs here")
    args = parser.parse_args()
    SDK = args.sdk.resolve()
    SOURCE_ARCHIVES = args.sources.resolve()
    if not SOURCE_ARCHIVES.is_dir():
        raise SystemExit(f"offline source archive directory missing: {SOURCE_ARCHIVES}")
    lock = json.loads(args.tools_lock.read_text())
    required = ("clang", "lld", "ar", "ranlib", "nm", "objdump", "make")
    for name in required:
        entry = lock["tools"].get(name)
        if entry is None:
            raise SystemExit(f"tools lock is missing required tool: {name}")
        path = Path(entry["path"])
        if not path.is_file() or digest(path) != entry["sha256"]:
            raise SystemExit(f"tool does not match supplied lock: {name} ({path})")
        TOOLS[name] = path
    LLVM = TOOLS["clang"].parent
    LLD = TOOLS["lld"]
    if digest(PATCH) != "095358520e36285ea9f57b2bd24219cb8ee9e80f9dc58bcd6074b8c5e9ba1c7d":
        raise SystemExit("pinned patch utility has changed")
    if not SDK.is_dir():
        raise SystemExit(f"SDK directory missing: {SDK}")
    if args.out_dir is not None:
        output = args.out_dir.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            raise SystemExit(f"output directory already exists: {output}")
        BUILD = output
        _main()
        return
    with tempfile.TemporaryDirectory(prefix="aether-r1-zsh-source-") as temporary:
        BUILD = Path(temporary) / "build"
        _main()


if __name__ == "__main__":
    main()
