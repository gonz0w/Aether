#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Offline Toybox cross-build. Requires Python 3.12+ and pinned local SDK."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REF = ROOT / "experiments/musl-reference"
sys.path.insert(0, str(ROOT / "experiments/command-runner"))
from process import run as owned_run


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, '[FAILED] ' + ascii(message)[1:-1] + '\n')


def main():
    parser = Parser(description=__doc__)
    parser.add_argument('--applet', choices=('cat', 'wc'), help='standalone applet; default is multicall')
    parser.add_argument('--version', action='version', version='toybox-reference-build 0.1.0')
    args = parser.parse_args()
    lock = json.loads((HERE / "source.lock.json").read_text())
    archive = ROOT / lock["archive"]
    require(sha(archive) == lock["sha256"], "source digest mismatch")
    tools = json.loads((REF / "tools.lock.json").read_text())["tools"]
    for name, tool in tools.items():
        require(sha(Path(tool["path"])) == tool["sha256"], name + " changed")
    sdk = Path(json.loads((REF / "evidence.json").read_text())["output"])
    require(not any(p.is_symlink() for p in (sdk / "stage").rglob("*")),
            "SDK symlink")
    inventory = {
        str(p.relative_to(sdk)): sha(p)
        for p in (sdk / "stage").rglob("*") if p.is_file()
    }
    expected = json.loads((REF / "large-tls-evidence.json").read_text())
    require(inventory == expected["sdk_inputs"], "SDK changed")
    host_tools = json.loads((HERE / "host-tools.lock.json").read_text())
    for name, tool in host_tools.items():
        require(sha(Path(tool["path"])) == tool["sha256"], name + " changed")
    out = Path(tempfile.mkdtemp(
        prefix="toybox-reference-", dir=ROOT / "build"))
    print(out, flush=True)
    (out / "tmp").mkdir()
    with tarfile.open(archive) as source:
        source.extractall(out, filter="data")
    src = out / ("toybox-" + lock["version"])
    test_inputs = {str(p.relative_to(src)): sha(p)
                   for p in (src / "tests").rglob("*") if p.is_file()}
    test_inputs["scripts/runtest.sh"] = sha(src / "scripts/runtest.sh")
    lib = sdk / "stage/usr/lib"
    target = [
        tools["clang"]["path"], "--no-default-config",
        "--target=x86_64-linux-musl", "--sysroot=" + str(sdk / "stage"),
        "-nostdinc", "-isystem", str(sdk / "stage/usr/include"),
    ]
    probe = owned_run(['/usr/bin/xcrun', '--show-sdk-path'], cwd=ROOT,
                      env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TMPDIR': str(out / 'tmp')},
                      work=out, label='host-sdk', timeout=15)
    require(probe.record['complete'] and probe.returncode == 0, 'host SDK probe failed')
    host_sdk = probe.stdout.decode().strip()
    host = [
        tools["clang"]["path"], "--no-default-config",
        "--target=arm64-apple-macos", "-isysroot", host_sdk,
    ]
    wrapper = out / "cc.py"
    wrapper.write_text(
        "#!" + sys.executable + "\n"
        "# SPDX-License-Identifier: BSD-2-Clause\n"
        "import os, sys\n"
        "args = sys.argv[1:]\n"
        "cc = " + repr(target) + "\n"
        "if not any(x in args for x in ('-c', '-E', '-S', '--version')):\n"
        "    args = [" + repr("--ld-path=" + tools["lld"]["path"])
        + ", '-nostdlib', '-static', "
        + repr(str(lib / "crt1.o")) + ", "
        + repr(str(lib / "crti.o")) + "] + args + ["
        + repr(str(lib / "libc.a")) + ", "
        + repr(str(lib / "crtn.o")) + "]\n"
        "os.execv(cc[0], cc + args)\n"
    )
    wrapper.chmod(0o755)
    host_wrapper = out / "hostcc.py"
    host_wrapper.write_text(
        "#!" + sys.executable + "\n"
        "# SPDX-License-Identifier: BSD-2-Clause\n"
        "import os, sys\n"
        "cc = " + repr(host) + "\nos.execv(cc[0], cc + sys.argv[1:])\n"
    )
    host_wrapper.chmod(0o755)
    config = HERE / ("miniconfig-" + args.applet if args.applet else "miniconfig")
    env = {
        "PATH": "/usr/bin:/bin", "LC_ALL": "C", "TMPDIR": str(out / "tmp"),
        "CC": str(wrapper), "HOSTCC": str(host_wrapper), "CPUS": "2",
        "CFLAGS": "-O2 -fstack-protector-strong",
        "LDFLAGS": "-static -Wl,-z,noexecstack -Wl,--no-undefined",
        "LDOPTIMIZE": "-Wl,--gc-sections -Wl,--as-needed",
        "NOSTRIP": "1", "VERSION": lock["version"],
        "KCONFIG_ALLCONFIG": str(config),
        "SED": host_tools["gsed"]["path"],
    }
    commands = []

    snapshot = out / 'consumer'
    snapshot.mkdir()
    for source_file in (Path(__file__), config, HERE / 'source.lock.json',
                        ROOT / 'experiments/command-runner/process.py'):
        (snapshot / source_file.name).write_bytes(source_file.read_bytes())

    def run(name, argv):
        result = owned_run(argv, cwd=src, env=env, work=out, label=name,
                           timeout=240, file_limit=512 * 1024 ** 2)
        commands.append({'name': name, 'argv': argv, 'status': result.returncode,
                         'process': result.record})
        (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        require(result.record['complete'] and result.returncode == 0,
                name + ' failed; see ' + str(out))

    run("config", ["/bin/bash", "scripts/genconfig.sh", "-n"])
    if args.applet:
        generated_config = src / '.config'
        config_text = generated_config.read_text()
        require(config_text.count('CONFIG_TOYBOX=y') == 1, 'standalone config anchor changed')
        (out / 'config-before-standalone').write_text(config_text)
        generated_config.write_text(config_text.replace('CONFIG_TOYBOX=y', '# CONFIG_TOYBOX is not set'))
    run("build", ["/bin/bash", "scripts/make.sh"])
    actual_config = (src / '.config').read_text()
    if args.applet:
        require('# CONFIG_TOYBOX is not set' in actual_config, 'multiplexer still enabled')
        for applet in ('CAT','WC','PRINTF','TEST','TRUE','FALSE'):
            require(('CONFIG_' + applet + '=y' in actual_config) == (applet.lower() == args.applet),
                    'unexpected selected applet: ' + applet)
    elf = src / "toybox"
    run("headers", [tools["readelf"]["path"], "-h", "-l", str(elf)])
    run("undefined", [tools["nm"]["path"], "--undefined-only",
                      "--extern-only", str(elf)])
    require(not (out / "undefined.stdout").read_text().strip(), "undefined")
    data = elf.read_bytes()
    require(data[:6] == b"\x7fELF\x02\x01", "ELF encoding")
    require(struct.unpack_from("<HH", data, 16) == (2, 62), "ELF target")
    offset = struct.unpack_from("<Q", data, 32)[0]
    size, count = struct.unpack_from("<HH", data, 54)
    headers = [struct.unpack_from("<IIQQQQQQ", data, offset + i * size)
               for i in range(count)]
    require(not any(h[0] in (2, 3) for h in headers), "dynamic ELF")
    require(not any(h[0] == 1 and h[1] & 3 == 3 for h in headers), "W+X")
    require(any(h[0] == 0x6474e551 and not h[1] & 1 for h in headers), "NX")
    run("imports", [tools["nm"]["path"], "--undefined-only"] + [
        str(p) for p in sorted((src / "generated/unstripped/obj").glob("*.o"))
    ])
    evidence = {
        "scope": "Clang/musl static Linux reference; not Aether",
        "output": str(out), "applet": args.applet, "source": lock, "sdk_inputs": inventory,
        "tools": tools, "host_tools": host_tools, "host_sdk": host_sdk,
        "environment": env, "test_inputs": test_inputs,
        "commands": commands, "elf_sha256": sha(elf),
        "elf_bytes": elf.stat().st_size,
        "files": {str(p): sha(p) for p in [
            Path(__file__), HERE / "PLAN.md", config, wrapper, host_wrapper,
            ROOT / "experiments/command-runner/process.py",
            src / ".config", src / "generated/build.sh", src / "LICENSE",
        ]},
        "limits": ["Host SDK/shared libraries not hermetically pinned",
                   "Source authentication/security review pending UL-016"],
    }
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("PASS: reference build; inspect headers before runtime admission")


if __name__ == "__main__":
    main()
