"""Host-only static ELF/initial-stack model; never maps or executes target code."""
import hashlib
import struct

PAGE = 4096
IMAGE_LOW, IMAGE_HIGH = 0x200000, 0x40000000
STACK_LOW, STACK_SIZE = 0x70000000, 65536
MAX_FILE, MAX_MAPPED, MAX_PHDR = 1048576, 16777216, 16
LOAD, PHDR, TLS = 1, 6, 7
STACK, RELRO, EH_FRAME = 0x6474E551, 0x6474E552, 0x6474E550


class InvalidImage(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise InvalidImage(reason)


def down(n):
    return n & -PAGE


def up(n):
    return (n + PAGE - 1) & -PAGE


def inspect(data):
    require(64 <= len(data) <= MAX_FILE, "file-size")
    require(data[:7] == b"\x7fELF\x02\x01\x01", "elf-ident")
    require(data[7:16] == bytes(9), "elf-osabi")
    h = struct.unpack_from("<HHIQQQIHHHHHH", data, 16)
    kind, machine, version, entry, phoff, _, flags, ehsize, entsize, count, _, _, _ = h
    require((kind, machine, version, flags, ehsize, entsize) == (2, 62, 1, 0, 64, 56), "elf-header")
    require(1 <= count <= MAX_PHDR and phoff >= 64 and phoff + count * 56 <= len(data), "phdr-table")
    headers = []
    for i in range(count):
        t, f, offset, va, _, filesz, memsz, align = struct.unpack_from("<IIQQQQQQ", data, phoff + i * 56)
        require(t in (LOAD, PHDR, TLS, STACK, RELRO, EH_FRAME), "unsupported-segment")
        require(filesz <= memsz and offset <= len(data) and filesz <= len(data) - offset, "segment-file-range")
        require(align in (0, 1) or (align <= PAGE and align & (align - 1) == 0), "segment-alignment")
        if align > 1:
            require((va - offset) % align == 0, "segment-congruence")
        require(0 <= va <= (1 << 64) - 1 and memsz <= (1 << 64) - 1 - va, "segment-overflow")
        headers.append(dict(type=t, flags=f, offset=offset, address=va,
                            file_size=filesz, memory_size=memsz, alignment=align))
    loads = sorted((h for h in headers if h["type"] == LOAD), key=lambda h: h["address"])
    require(loads, "missing-load")
    mapped = 0
    end = IMAGE_LOW
    for h in loads:
        va, length = h["address"], h["memory_size"]
        require(h["flags"] in (4, 5, 6), "load-permissions")
        require(length and IMAGE_LOW <= va < va + length <= IMAGE_HIGH, "load-address")
        require((va - h["offset"]) % PAGE == 0, "load-page-congruence")
        require(down(va) >= end, "load-page-overlap")
        end = up(va + length)
        mapped += end - down(va)
    require(mapped + STACK_SIZE <= MAX_MAPPED, "mapping-quota")
    require(any(h["flags"] == 5 and h["address"] <= entry < h["address"] + h["file_size"] for h in loads), "entry-not-executable-bytes")

    def only(t, reason):
        selected = [h for h in headers if h["type"] == t]
        require(len(selected) == 1, reason)
        return selected[0]

    def in_load(h, initialized=False):
        size = h["file_size"] if initialized else h["memory_size"]
        return [p for p in loads if p["address"] <= h["address"] and
                h["address"] + size <= p["address"] + (p["file_size"] if initialized else p["memory_size"]) and
                (not initialized or h["offset"] - p["offset"] == h["address"] - p["address"])]

    table = only(PHDR, "phdr-count")
    require(table["flags"] == 4 and table["offset"] == phoff and
            table["file_size"] == table["memory_size"] == count * 56 and in_load(table, True), "phdr-not-mapped")
    stack = only(STACK, "stack-count")
    require(stack["flags"] == 6 and stack["file_size"] == stack["memory_size"] == 0, "stack-profile")
    tls = only(TLS, "tls-count")
    require(tls["flags"] == 4 and 0 < tls["memory_size"] <= PAGE and
            tls["alignment"] > 0 and in_load(tls) and in_load(tls, True), "tls-template")
    relros = [h for h in headers if h["type"] == RELRO]
    require(len(relros) <= 1, "relro-count")
    for h in relros:
        require(h["flags"] == 4 and h["memory_size"] and in_load(h), "relro-range")
        lo, hi = down(h["address"]), up(h["address"] + h["memory_size"])
        for p in loads:
            if down(p["address"]) < hi and up(p["address"] + p["memory_size"]) > lo:
                require(h["address"] <= p["address"] and p["address"] + p["memory_size"] <= h["address"] + h["memory_size"] and p["flags"] == 6, "relro-shared-page")
    for h in headers:
        if h["type"] == EH_FRAME:
            require(h["flags"] == 4 and in_load(h, True), "eh-frame-range")
    mappings = []
    for h in loads:
        protected = any(down(x["address"]) <= down(h["address"]) < up(x["address"] + x["memory_size"]) for x in relros)
        mappings.append(dict(start=down(h["address"]), size=up(h["address"] + h["memory_size"]) - down(h["address"]),
            permissions="R" if protected else {4:"R",5:"RX",6:"RW"}[h["flags"]],
            copy_from=h["offset"], copy_to=h["address"], copy_size=h["file_size"],
            zero_entire_mapping_before_copy=True))
    return dict(profile="host-static-c-v0", image_sha256=hashlib.sha256(data).hexdigest(), entry=entry,
                phdr_address=table["address"], phdr_count=count, mappings=mappings,
                tls=tls, mapped_bytes=mapped + STACK_SIZE,
                stack=dict(start=STACK_LOW, size=STACK_SIZE, permissions="RW", guard_below=PAGE))


def initial_stack(plan, argv, env, entropy):
    """Return proposed stack bytes and RSP. Entropy is a caller-supplied fixture."""
    require(len(entropy) == 16, "entropy-size")
    require(1 <= len(argv) <= 16 and len(env) <= 16, "argument-count")
    require(all(isinstance(x, str) and "\0" not in x for x in argv + env), "argument-nul")
    encoded = [s.encode("utf-8") + b"\0" for s in argv + env]
    require(sum(map(len, encoded)) <= 8192, "argument-bytes")
    require(all("=" in x and x.split("=", 1)[0] for x in env), "environment-entry")
    keys = [x.split("=", 1)[0] for x in env]
    require(len(keys) == len(set(keys)), "duplicate-environment")
    blob = bytearray(STACK_SIZE)
    cursor = STACK_SIZE
    def push(b):
        nonlocal cursor
        require(len(b) <= cursor, "stack-overflow")
        cursor -= len(b)
        blob[cursor:cursor+len(b)] = b
        return STACK_LOW + cursor
    random_address = push(entropy)
    ptrs = [push(b) for b in encoded]
    # Fixed unprivileged *test* identity. Not a credential/grant protocol.
    aux = [(3, plan["phdr_address"]), (4, 56), (5, plan["phdr_count"]), (6, PAGE),
           (9, plan["entry"]), (11, 1000), (12, 1000), (13, 1000), (14, 1000),
           (23, 0), (25, random_address), (31, ptrs[0]), (0, 0)]
    words = [len(argv), *ptrs[:len(argv)], 0, *ptrs[len(argv):], 0]
    words += [word for pair in aux for word in pair]
    table = struct.pack("<" + "Q" * len(words), *words)
    position = (cursor - len(table)) & -16
    require(position >= 0, "stack-overflow")
    blob[position:position+len(table)] = table
    return bytes(blob), STACK_LOW + position
