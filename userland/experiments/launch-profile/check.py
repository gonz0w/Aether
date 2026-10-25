#!/usr/bin/env python3
"""Host acceptance for a proposed launch profile, using pinned real ELF inputs."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile

from launch import inspect, initial_stack, InvalidImage, STACK_LOW, STACK_SIZE, PAGE

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
reference = json.loads((ROOT / "experiments/musl-reference/evidence.json").read_text())
out = Path(tempfile.mkdtemp(prefix="launch-profile-", dir=ROOT / "build"))
sha = lambda b: hashlib.sha256(b).hexdigest()
results = []
fixtures = {}
for name in ("startup", "allocator"):
    data = (Path(reference["output"]) / (name + ".elf")).read_bytes()
    artifact = next(a for a in reference["artifacts"] if a["name"] == name)
    assert sha(data) == artifact["sha256"]
    fixtures[name] = data
    plan = inspect(data)
    blob, rsp = initial_stack(plan, [name, "check"], ["AETHER_PROBE=reference"], bytes(range(16)))
    assert rsp % 16 == 0 and STACK_LOW <= rsp < STACK_LOW + STACK_SIZE
    def word(addr):
        assert STACK_LOW <= addr <= STACK_LOW + STACK_SIZE - 8
        return struct.unpack_from("<Q", blob, addr - STACK_LOW)[0]
    def string(addr):
        assert STACK_LOW <= addr < STACK_LOW + STACK_SIZE
        return blob[addr-STACK_LOW:].split(b"\0", 1)[0].decode()
    assert word(rsp) == 2 and string(word(rsp+8)) == name and string(word(rsp+16)) == "check"
    assert word(rsp+24) == 0 and string(word(rsp+32)) == "AETHER_PROBE=reference" and word(rsp+40) == 0
    cursor, aux = rsp+48, {}
    while word(cursor):
        assert word(cursor) not in aux
        aux[word(cursor)] = word(cursor+8)
        cursor += 16
    assert word(cursor+8) == 0
    assert aux[3] == plan["phdr_address"] and aux[4] == 56 and aux[5] == 9 and aux[6] == PAGE
    assert aux[9] == plan["entry"] and aux[11] == aux[12] == aux[13] == aux[14] == 1000 and aux[23] == 0
    assert blob[aux[25]-STACK_LOW:aux[25]-STACK_LOW+16] == bytes(range(16))
    assert string(aux[31]) == name
    # Materialize zero/copy operations in host byte arrays only. No executable mappings.
    pages = []
    for m in plan["mappings"]:
        image = bytearray(m["size"])
        offset = m["copy_to"] - m["start"]
        payload = data[m["copy_from"]:m["copy_from"]+m["copy_size"]]
        image[offset:offset+len(payload)] = payload
        assert not any(image[:offset]) and not any(image[offset+len(payload):])
        pages.append((m, image))
    def loaded(addr, length):
        m, b = next((m,b) for m,b in pages if m["start"] <= addr and addr+length <= m["start"]+m["size"])
        return b[addr-m["start"]:addr-m["start"]+length]
    phoff = struct.unpack_from("<Q", data, 32)[0]
    assert loaded(aux[3], aux[4]*aux[5]) == data[phoff:phoff+aux[4]*aux[5]]
    assert loaded(plan["tls"]["address"], 4) == struct.pack("<I", 17)
    assert any(m["permissions"] == "RX" for m in plan["mappings"])
    assert next(m for m in plan["mappings"] if m["start"] <= plan["tls"]["address"] < m["start"]+m["size"])["permissions"] == "R"
    # Reproducibility here uses public test entropy, never production entropy.
    assert (blob, rsp) == initial_stack(inspect(data), [name,"check"], ["AETHER_PROBE=reference"], bytes(range(16)))
    (out / (name + "-plan.json")).write_text(json.dumps(plan, indent=2)+"\n")
    (out / (name + "-stack.bin")).write_bytes(blob)
    results.append({"case":name, "mapped_bytes":plan["mapped_bytes"], "rsp":rsp, "plan_sha256":sha((out/(name+'-plan.json')).read_bytes()), "stack_sha256":sha(blob)})

data = fixtures["startup"]
phoff = struct.unpack_from("<Q", data, 32)[0]
def patch(offset, fmt, value):
    b = bytearray(data)
    struct.pack_into(fmt, b, offset, value)
    return bytes(b)
def ph(index, offset, fmt, value):
    return patch(phoff+56*index+offset, fmt, value)
zero_entry = bytearray(data)
code_address = struct.unpack_from("<Q", data, phoff+2*56+16)[0]
code_size = struct.unpack_from("<Q", data, phoff+2*56+32)[0]
struct.pack_into("<Q", zero_entry, phoff+2*56+40, code_size+16)
struct.pack_into("<Q", zero_entry, 24, code_address+code_size+1)
cases = {
    "short-header":data[:40], "oversize-file":data+bytes(1048576),
    "wrong-class":patch(4,"B",1), "wrong-endian":patch(5,"B",2),
    "wrong-machine":patch(18,"H",183), "dynamic-elf":patch(16,"H",3),
    "unbounded-phdr-count":patch(56,"H",65535), "truncated-table":data[:120],
    "bad-phdr-offset":patch(32,"Q",(1<<64)-1),
    "interpreter":ph(7,0,"I",3), "dynamic-segment":ph(7,0,"I",2),
    "unknown-segment":ph(7,0,"I",0x123456), "writable-code":ph(2,4,"I",7),
    "execute-only":ph(2,4,"I",1), "executable-stack":ph(8,4,"I",7),
    "out-of-file":ph(2,8,"Q",0xfffff320), "file-larger-than-memory":ph(2,32,"Q",0xffff),
    "bad-alignment":ph(2,48,"Q",3), "page-incongruence":ph(2,16,"Q",0x201321),
    "address-overflow":ph(4,40,"Q",(1<<64)-1), "null-mapping":ph(1,16,"Q",0),
    "high-address":ph(4,16,"Q",0xffff8000000041d8), "mapped-quota":ph(4,40,"Q",16*1024*1024),
    "page-overlap":ph(2,16,"Q",0x200320), "entry-in-data":patch(24,"Q",0x2041d8),
    "entry-unmapped":patch(24,"Q",0x12345000), "entry-in-zero-fill":bytes(zero_entry),
    "missing-phdr":ph(0,0,"I",0x6474e550), "unmapped-phdr":ph(0,16,"Q",0x900040),
    "missing-stack":ph(8,0,"I",0x6474e550), "duplicate-stack":ph(7,0,"I",0x6474e551),
    "missing-tls":ph(5,0,"I",0x6474e550), "unmapped-tls":ph(5,16,"Q",0x9001cc),
    "large-tls":ph(5,40,"Q",8192), "relro-unmapped":ph(6,16,"Q",0x9001cc),
    "relro-shared-data":ph(6,40,"Q",0x100), "eh-frame-unmapped":ph(7,16,"Q",0x9002a8),
}
rejected = {}
for name, candidate in cases.items():
    try:
        inspect(candidate)
    except InvalidImage as e:
        rejected[name] = str(e)
    else:
        raise RuntimeError("accepted malformed image: " + name)

plan = inspect(data)
stack_cases = {
    "empty-argv":([], [], bytes(16)), "too-many-argv":(["a"]*17, [], bytes(16)),
    "too-many-env":(["a"], [str(i)+"=x" for i in range(17)], bytes(16)),
    "argument-nul":(["a\0b"], [], bytes(16)), "argument-bytes":(["a"*8192], [], bytes(16)),
    "bad-env":(["a"], ["MISSING_EQUALS"], bytes(16)), "empty-env-key":(["a"], ["=x"], bytes(16)),
    "duplicate-env":(["a"], ["X=1","X=2"], bytes(16)), "short-entropy":(["a"], [], bytes(15)),
}
for name, args in stack_cases.items():
    try:
        initial_stack(plan, *args)
    except InvalidImage as e:
        rejected[name] = str(e)
    else:
        raise RuntimeError("accepted malformed startup: " + name)
evidence = {"scope":"host-only proposed ELF/stack layout, no target launch or confinement",
            "profile":"host-static-c-v0", "output":str(out), "positive":results, "rejected":rejected,
            "sources":{p.name:sha(p.read_bytes()) for p in [HERE/'launch.py', Path(__file__)]},
            "reference_evidence_sha256":sha((ROOT/'experiments/musl-reference/evidence.json').read_bytes())}
(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
print(f"PASS: 2 real ELF/stack plans and {len(rejected)} rejected inputs; evidence {out}")
