#!/usr/bin/env python3
"""Link and execute the explicit 128-bit arithmetic witness."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
tools = json.loads((HERE / "tools.lock.json").read_text())["tools"]
for name, item in tools.items():
    assert sha(Path(item["path"])) == item["sha256"], name
builtins = json.loads((HERE / "builtins-evidence.json").read_text())
archive = Path(builtins["archive"])
assert sha(archive) == builtins["sha256"]
ref = Path(json.loads((HERE / "evidence.json").read_text())["output"])
out = Path(tempfile.mkdtemp(prefix="builtins-witness-", dir=ROOT / "build"))
(out / "tmp").mkdir()
env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "TMPDIR": str(out / "tmp")}
cc = [tools["clang"]["path"], "--no-default-config", "--target=x86_64-linux-musl", "--sysroot=" + str(ref / "stage")]
commands = []
def run(name, cmd, good=True):
    r = subprocess.run(cmd, env=env, capture_output=True, timeout=60)
    (out / (name + ".stdout")).write_bytes(r.stdout)
    (out / (name + ".stderr")).write_bytes(r.stderr)
    commands.append({"name": name, "argv": cmd, "exit": r.returncode})
    if (r.returncode == 0) != good:
        raise RuntimeError(name + " unexpected status; see " + str(out))
    return r
obj = out / "arithmetic.o"
run("compile", cc + ["-O2", "-Wall", "-Wextra", "-Werror", "-nostdinc", "-isystem", str(ref / "stage/usr/include"),
    "-c", str(HERE / "arithmetic.c"), "-o", str(obj)])
lib = ref / "stage/usr/lib"
link = cc + ["-fuse-ld=" + tools["lld"]["path"], "-nostdlib", "-static", "-Wl,-z,noexecstack", "-Wl,--no-undefined",
             str(lib / "crt1.o"), str(lib / "crti.o"), str(obj), str(lib / "libc.a")]
bad = run("without-runtime", link + [str(lib / "crtn.o"), "-o", str(out / "bad.elf")], good=False)
assert b"__udivti3" in bad.stderr and b"__divti3" in bad.stderr
elf = out / "arithmetic.elf"
run("link", link + [str(archive), str(lib / "crtn.o"), "-o", str(elf)])
symbols = run("symbols", [tools["nm"]["path"], str(elf)]).stdout
for symbol in (b"__udivti3", b"__umodti3", b"__divti3"):
    assert symbol in symbols
assert not run("undefined", [tools["nm"]["path"], "--undefined-only", "--extern-only", str(elf)]).stdout.strip()
assert b"There are no relocations" in run("relocations", [tools["readelf"]["path"], "-r", str(elf)]).stdout
run("headers", [tools["readelf"]["path"], "-h", "-l", str(elf)])
data = elf.read_bytes()
assert data[:6] == b"\x7fELF\x02\x01" and struct.unpack_from("<HH", data, 16) == (2,62)
offset = struct.unpack_from("<Q",data,32)[0]
size,count = struct.unpack_from("<HH",data,54)
headers = [struct.unpack_from("<IIQQQQQQ",data,offset+i*size) for i in range(count)]
assert not any(h[0] in (2,3) or (h[0]==1 and h[1]&3==3) for h in headers)
assert any(h[0]==0x6474e551 and not h[1]&1 for h in headers)
image = "8d0dff22866c67ea5de1d66ff04a54f17e610a11e3a5c970414820663c7649a4"
r = run("linux", ["/opt/homebrew/bin/podman", "run", "--rm", "--pull=never", "--network=none", "--read-only", "--cap-drop=all",
    "--security-opt=no-new-privileges", "--user=65534:65534", "--mount", "type=bind,src="+str(out)+",dst=/inputs,ro=true",
    "--entrypoint=qemu-x86_64", image, "-strace", "/inputs/arithmetic.elf"])
assert r.stdout == b"AETHER BUILTINS PASS\n"
e = {"scope":"signed/unsigned 128-bit arithmetic under QEMU Linux user emulation; not full builtins suite or Aether",
     "output":str(out), "runtime_archive_sha256":sha(archive), "elf_sha256":sha(elf), "elf_bytes":len(data),
     "source_sha256":sha(HERE/'arithmetic.c'), "script_sha256":sha(Path(__file__)), "image_id":image,
     "commands":commands, "stdout":r.stdout.decode(), "trace_sha256":hashlib.sha256(r.stderr).hexdigest()}
(out/'evidence.json').write_text(json.dumps(e,indent=2)+'\n')
print("PASS: arithmetic witness; without-runtime link rejected; evidence " + str(out))
