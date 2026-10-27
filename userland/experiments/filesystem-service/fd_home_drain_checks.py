# SPDX-License-Identifier: BSD-2-Clause
"""Direct C host checks only; never constructs or selects a native image.

Run from userland with Python 3.10+:
python3 -B experiments/filesystem-service/fd_home_drain_checks.py --evidence /private/path
Use an unused evidence directory whose parent already exists. Pinned Clang and
clang-format21.1.8 plus the installed macOS SDK are required. Exit status: 0 pass,
1 failed check, 2 blocked prerequisite/output, 64 invalid usage. Retain receipts;
correct a failure before rerunning with a new output directory.
"""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import re
import runpy
import shutil
import shlex
import tempfile
import sys
import time

S = Path(__file__).resolve().parent
R = S.parents[1]
COMPILER = Path("/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang")
FORMATTER = COMPILER.with_name("clang-format")
STYLE = R / "docs/quality/clang-format.yaml"
UNITS = ("fd-client", "fd-facade", "fd-routing", "fd-table", "fd-write",
         "fd-pipe", "fd-replace", "fd-session", "fd-redirect", "fd-native",
         "fd-context", "fd-startup", "fd-fork-frame", "fd-fork-stage",
         "fd-exec", "fd-home-probe-adapter")
FLAGS = ("--no-default-config", "-std=c17", "-Wall", "-Wextra", "-Wpedantic",
         "-Wconversion", "-Wsign-conversion", "-Wshadow", "-Wstrict-prototypes",
         "-Wmissing-prototypes", "-Werror", "-DAEFD_PATH_WIRE", "-DAEFD_DUP2_WIRE",
         "-DAEFD_WRITE_WIRE", "-DAEFD_HOME_DRAIN_HOST_TEST")
DOUBLES = ("-Dpipe=aefd_home_drain_test_pipe", "-Dfork=aefd_home_drain_test_fork",
           "-Dsched_yield=aefd_home_drain_test_yield",
           "-D__builtin_trap=aefd_home_drain_test_trap")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise RuntimeError(message)


def closure(paths):
    """Freeze consumed local quoted includes, including the actual stage tests."""
    pending = list(paths)
    found = {}
    while pending:
        path = pending.pop().resolve(strict=True)
        if str(path) in found:
            continue
        found[str(path)] = sha(path)
        for name in re.findall(r'^#include "([^"\n]+)"', path.read_text(), re.M):
            pending.append(path.parent / name)
    return found


def display(value):
    return ascii(str(value))[1:-1]


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, "[ERROR] " + display(message) + "\n")


def evidence_output(value):
    path = Path(value).absolute()
    if ".." in path.parts:
        raise ValueError("evidence path must not contain '..'")
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError("evidence path uses a symlink: " + str(part))
    if path.exists():
        raise ValueError("evidence output already exists: " + str(path))
    if not path.parent.is_dir():
        raise ValueError("evidence output parent is not a directory: " + str(path.parent))
    # Reserve the unused destination exclusively; never replace old receipts.
    path.mkdir(mode=0o700)
    return path


def failed(record, kind, message):
    record.setdefault("failures", []).append(dict(kind=kind, message=message))
    record["result"] = "failed"
    record.setdefault("error", message)


def run_child(proc, work, record, deadline, label, argv, rejection=None):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        failed(record, "aggregate-deadline", "focused aggregate deadline before " + label)
        raise RuntimeError(record["error"])
    # Arm before either helper callback. A raised callback cannot establish that
    # no child exists, or that a child/process group has been cleaned up.
    record["process"] = dict(state="inflight", label=label, cleanup="unknown")
    try:
        result = proc["run"]([str(arg) for arg in argv], cwd=S,
                             env=proc["clean_env"](work), work=work, label=label,
                             timeout=min(180, remaining), file_limit=4 * 1024**2)
        entry = dict(result.record)
    except BaseException as error:
        record["process"]["state"] = "unknown"
        failed(record, "helper-exception", label + ": " + type(error).__name__ +
               "; process cleanup unknown")
        raise
    record["process"] = dict(state="returned", label=label,
                              cleanup=entry.get("cleanup", "unknown"),
                              complete=entry.get("complete", False))
    entry.update(stdout=result.stdout.decode(errors="replace")[-7168:],
                 stderr=result.stderr.decode(errors="replace")[-7168:],
                 stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
                 stderr_sha256=hashlib.sha256(result.stderr).hexdigest())
    record["commands"].append(entry)
    if entry.get("cleanup") != "complete":
        failed(record, "cleanup-unresolved", label + ": process cleanup " +
               str(entry.get("cleanup", "unknown")))
        raise RuntimeError(record["error"])
    if entry.get("complete") is not True:
        kind = "timeout" if entry.get("failure") == "timeout" else "process-incomplete"
        failed(record, kind, label + ": process incomplete: " + str(entry.get("failure")))
        raise RuntimeError(record["error"])
    if rejection is None:
        if result.returncode != 0:
            failed(record, "check-failure", label + ": unexpected nonzero exit")
            raise RuntimeError(record["error"])
    else:
        if result.returncode != 1 or rejection not in entry["stderr"]:
            failed(record, "semantic-control-failure", label +
                   ": missing named semantic rejection " + rejection)
            raise RuntimeError(record["error"])
        entry["expected_rejection"] = rejection
    print("[OK] " + display(label) + ": " +
          ("pass" if rejection is None else display(rejection)),
          file=sys.stderr, flush=True)
    return result


def finish(record, inputs, work, start, deadline, destination):
    try:
        record["inputs_unchanged"] = all(sha(path) == digest
                                         for path, digest in inputs.items())
    except OSError:
        record["inputs_unchanged"] = False
    if not record["inputs_unchanged"]:
        failed(record, "input-change", "consumed input changed during run")
    if work is None:
        record["cleanup"] = "no work directory created"
    elif record["process"]["cleanup"] != "complete":
        record["cleanup"] = "retained: process cleanup unknown or unresolved"
        record["retained_work"] = str(work)
        if record["result"] != "failed":
            failed(record, "cleanup-unresolved", "process cleanup unknown or unresolved")
    else:
        try:
            shutil.rmtree(work)
            record["cleanup"] = "owned temporary sources/objects/binaries removed"
        except OSError as error:
            record["cleanup"] = "owned work removal unresolved"
            record["retained_work"] = str(work)
            failed(record, "work-cleanup-failure", str(error))
    if record["result"] == "incomplete":
        failed(record, "incomplete-check", "check did not establish a result")
    record["end_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    record["elapsed_seconds"] = time.monotonic() - start
    if time.monotonic() >= deadline:
        failed(record, "aggregate-deadline", "focused aggregate deadline after finalization")
    destination.write_text(json.dumps(record, indent=2) + "\n")
    # Include receipt serialization/write in the final deadline decision too.
    if time.monotonic() >= deadline and not any(
            item["kind"] == "aggregate-deadline" for item in record.get("failures", [])):
        failed(record, "aggregate-deadline", "focused aggregate deadline after receipt write")
        record["elapsed_seconds"] = time.monotonic() - start
        destination.write_text(json.dumps(record, indent=2) + "\n")


def check(evidence, started=None):
    start = time.monotonic() if started is None else started
    deadline = start + 300
    destination = evidence / "c-host-01.json"
    inputs = {}
    work = None
    record = dict(start_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  platform=platform.platform(), inputs=inputs, commands=[],
                  process=dict(state="idle", cleanup="complete"),
                  limits=dict(aggregate_seconds=300, child_seconds=180,
                              stream_bytes=4 * 1024**2), result="incomplete",
                  native="not run; new control human review pending")

    def run(label, argv, *, rejection=None):
        return run_child(proc, work, record, deadline, label, argv, rejection)

    try:
        helper = R / "experiments/command-runner/process.py"
        proc = runpy.run_path(str(helper))
        sources = [*(S / (unit + ".c") for unit in UNITS),
                   S / "fd-home-drain.c", S / "fd-home-drain-tests.c"]
        inputs.update(closure(sources))
        for path in (Path(__file__), helper, STYLE, COMPILER, FORMATTER,
                     Path("/usr/bin/xcrun")):
            inputs[str(path)] = sha(path)
        work = Path(tempfile.mkdtemp(prefix="af09-drain-", dir="/private/tmp"))
        compiler = run("compiler", [COMPILER, "--no-default-config", "--version"])
        formatter = run("formatter", [FORMATTER, "--version"])
        require(b"clang version 21.1.8" in compiler.stdout and
                b"clang-format version 21.1.8" in formatter.stdout,
                "required pinned compiler/formatter version")
        sdk = run("sdk", ["/usr/bin/xcrun", "--show-sdk-path"]).stdout.decode().strip()
        require(Path(sdk).is_dir(), "installed host SDK unavailable")
        flags = [*FLAGS, "-isysroot", sdk, "-I", str(S)]
        run("format", [FORMATTER, "--dry-run", "--Werror",
                       "--style=file:" + str(STYLE), S / "fd-home-drain.c",
                       S / "fd-home-drain.h", S / "fd-home-drain-tests.c"])
        def read_dependencies(dep):
            body = dep.read_text().split(":", 1)[1].replace("\\\n", " ")
            return {Path(name).resolve(strict=True) for name in shlex.split(body)}

        # -M is dependency discovery, not a qualified compile. Freeze all
        # discovered SDK/resource headers before the first real compilation.
        for source in sources:
            dep = work / (source.stem + "-discovery.d")
            extra = DOUBLES if source.name == "fd-home-drain.c" else ()
            run(source.stem + "-discovery", [COMPILER, *flags, *extra,
                                            "-M", "-MF", dep, "-MT", "input", source])
            for header in read_dependencies(dep):
                digest = sha(header)
                require(str(header) not in inputs or inputs[str(header)] == digest,
                        "input changed during dependency discovery: " + str(header))
                inputs[str(header)] = digest
        require(all(sha(path) == digest for path, digest in inputs.items()),
                "input changed before compilation")
        record["dependency_freeze"] = "complete before qualified compilation"
        # Driver discovery executes no compile/link jobs. Record all exact
        # executables named by this host driver's -### link recipe.
        jobs = run("linker-discovery", [COMPILER, "--no-default-config", "-isysroot", sdk,
                                        "-###", "-x", "c", "/dev/null", "-o", work / "unused"])
        discovered_tools = set()
        for line in jobs.stderr.decode().splitlines():
            if line.lstrip().startswith('"'):
                argv = shlex.split(line)
                if argv and Path(argv[0]).is_absolute():
                    tool = Path(argv[0]).resolve(strict=True)
                    inputs[str(tool)] = sha(tool)
                    discovered_tools.add(str(tool))
        require(any(Path(tool).name == "ld" for tool in discovered_tools),
                "host linker executable not identified")
        record["driver_tools"] = sorted(discovered_tools)
        record["tool_scope"] = ("direct compiler/formatter and -### named compiler/linker; "
                                "no full transitive dynamic-library/SDK-toolchain closure claim")

        def compile_unit(label, source, output, extra=()):
            dep = work / (label + ".d")
            run(label, [COMPILER, *flags, *extra, "-MD", "-MF", dep,
                        "-c", source, "-o", output])
            for header in read_dependencies(dep):
                if header == source.resolve() and header.is_relative_to(work):
                    continue
                require(str(header) in inputs and inputs[str(header)] == sha(header),
                        "unknown or changed compiled input: " + str(header))

        objects = []
        for unit in (*UNITS, "fd-home-drain-tests"):
            output = work / (unit + ".o")
            compile_unit(unit, S / (unit + ".c"), output)
            objects.append(output)
        original = (S / "fd-home-drain.c").read_text()

        def candidate(label, text, rejection=None):
            source = work / (label + ".c")
            source.write_text(text)
            record.setdefault("candidate_sources", {})[label] = sha(source)
            obj = work / (label + ".o")
            exe = work / label
            compile_unit(label + "-compile", source, obj, DOUBLES)
            run(label + "-link", [COMPILER, "--no-default-config", "-isysroot", sdk,
                                  *objects, obj, "-o", exe])
            record.setdefault("artifacts", {})[label] = sha(exe)
            run(label, [exe], rejection=rejection)

        candidate("positive", original)
        controls = (
            ("exit-trap-fallthrough", "        __builtin_trap();", "        return 115;",
             "DRAIN_UNEXPECTED_EXIT_RETURN_FAILS"),
            ("missing-native-ready", "aefd_startup_ready(&f->boot)", "0",
             "DRAIN_BYTES_REQUIRE_NATIVE_READY"),
            ("wrong-file-prefix", "11, args)", "2, args)",
             "DRAIN_FILE_PREFIX_ACTUAL_CHILD_GENERATION_SEQUENCE"),
            ("stale-file-generation", "c->client.generation, c->client.sequence,",
             "c->client.generation + 1, c->client.sequence,",
             "DRAIN_FILE_PREFIX_ACTUAL_CHILD_GENERATION_SEQUENCE"),
            ("only-one-write16", "io.write(io.context, retained.bytes + 16, 16) == 16",
             "n->initialized == 1", "DRAIN_TWO_WRITES_THEN_YIELD_NO_CLEANUP"),
            ("omitted-output-match", "observed.output != c->native.output ||", "",
             "DRAIN_STALE_IDENTITY_ENDPOINT_PIPE_NESTED_DENIAL"),
            ("wrong-stream-reference", "c->native.sources[write_end.selector].reference);",
             "c->native.sources[read_end.selector].reference);",
             "DRAIN_REAL_PIPE_STREAM_REQUEST"),
        )
        for label, old, new, rejection in controls:
            require(original.count(old) == 1, label + ": mutation anchor changed")
            candidate(label, original.replace(old, new), rejection)
        # UBSan is available on this pinned host; ASan remains separately blocked
        # by the recorded macOS dyld/malloc incompatibility in quality/PROCESS.
        sanitized = []
        for source in sources:
            output = work / (source.stem + "-ubsan.o")
            extra = ["-fsanitize=undefined", "-fno-sanitize-recover=all"]
            if source.name == "fd-home-drain.c":
                extra.extend(DOUBLES)
            compile_unit(source.stem + "-ubsan", source, output, extra)
            sanitized.append(output)
        run("ubsan-link", [COMPILER, "--no-default-config", "-isysroot", sdk,
                           "-fsanitize=undefined", "-fno-sanitize-recover=all",
                           *sanitized, "-o", work / "ubsan"])
        record["artifacts"]["ubsan"] = sha(work / "ubsan")
        run("ubsan", [work / "ubsan"])
        record["result"] = "pass"
    except (OSError, RuntimeError, ValueError) as error:
        if record["result"] != "failed":
            failed(record, "check-failure", str(error))
    finally:
        finish(record, inputs, work, start, deadline, destination)
        print(display(destination) + ": " + record["result"], flush=True)
        if record["result"] != "pass":
            print("[ERROR] " + display(record.get("error", "check failed")) +
                  "; inspect " + display(destination), file=sys.stderr)
    return 0 if record["result"] == "pass" else 1


def main(argv=None):
    parser = Parser(prog="fd-home-drain-checks", description=__doc__,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version="fd-home-drain-checks 1")
    parser.add_argument("--evidence", action="append", required=True, metavar="PATH",
                        help="unused directory for compact receipts; existing parent required")
    args = parser.parse_args(argv)
    if len(args.evidence) != 1:
        parser.error("--evidence must occur exactly once")
    # Selected-check setup (including output reservation) shares one clock.
    started = time.monotonic()
    try:
        evidence = evidence_output(args.evidence[0])
        for path in (COMPILER, FORMATTER, STYLE,
                     R / "experiments/command-runner/process.py"):
            if not path.is_file():
                raise ValueError("required host input unavailable: " + str(path))
        return check(evidence, started)
    except ValueError as error:
        print("[BLOCKED] " + display(error), file=sys.stderr)
        return 2
    except (OSError, RuntimeError) as error:
        print("[ERROR] " + display(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
