# SPDX-License-Identifier: BSD-2-Clause
"""Select original hash-pinned C bodies with exact, unique edits.

This module has no command-line runner. Callers own a private build directory,
record this recipe and all generated hashes, and remove generated outputs.
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ORIGINALS = {
    "user/storage/service-runtime/filesystem-engine.c":
        "dcf00a258e3be55ea8fd259c398f4f99c177aa17bbf1e8d5f0dc176aee87690d",
    "user/storage/openzfs-volume/filesystem-import.c":
        "f8f32ef91e70811fbede518d6cbbf63094d43e1cec95c16b8c0e0b9bf7fe75fe",
}


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("home native C anchor is not unique: " + repr(old))
    return text.replace(old, new, 1)


def render(path, text=None):
    path = Path(path)
    key = path.relative_to(ROOT).as_posix()
    data = path.read_bytes() if text is None else text.encode()
    if key not in ORIGINALS or hashlib.sha256(data).hexdigest() != ORIGINALS[key]:
        raise ValueError("home native original C hash mismatch: " + key)
    text = data.decode()
    edits = [('"filesystem-engine.h"', '"home-native.h"')]
    if path.name == "filesystem-engine.c":
        edits += [
            ("extern int aether_fs_engine_import(struct aether_fs_launch_state *);",
             "extern int aether_fs_home_engine_import(struct aether_fs_home_launch_state *);"),
            ("int aether_fs_engine_run(uint64_t grant, struct aether_fs_launch_state *out)",
             "int aether_fs_home_engine_run(uint64_t grant, struct aether_fs_home_launch_state *out)"),
            ("int service_error = aether_fs_engine_import(out);",
             "int service_error = aether_fs_home_engine_import(out);"),
        ]
    else:
        edits += [
            ("int aether_fs_engine_import(struct aether_fs_launch_state *out)",
             "int aether_fs_home_engine_import(struct aether_fs_home_launch_state *out)"),
            ("    int service_error = 0;", "    int service_error = 0, protocol = 0, ordered_required = 0;"),
            ("        service_error = aether_fs_launch_serve(spa, out);",
             "        service_error = aether_fs_home_launch_serve(spa, out);\n"
             "        ordered_required = aether_fs_home_order_required(&out->home, &protocol);\n"
             "        if (protocol)\n            service_error = EPROTO;"),
            ("    if (remaining || (out->service.txg && aether_pool_hooks_check_ordered()))\n        return EIO;",
             "    unsigned order_error = ordered_required ? aether_pool_hooks_check_ordered() : 0;\n"
             "    if (remaining || order_error)\n        return EIO;"),
        ]
    for old, new in edits:
        text = replace_once(text, old, new)
    return text, edits


def generate(work):
    work = Path(work).resolve()
    if not any(work.is_relative_to((ROOT / root).resolve())
               for root in ("build", "userland/build")):
        raise ValueError("home native generation requires an owned build root")
    if not work.is_dir():
        raise ValueError("home native output directory must already exist")
    recipes = []
    for name, digest in ORIGINALS.items():
        original = ROOT / name
        body, edits = render(original)
        output = work / ("home-" + original.name)
        if output.exists() or output.is_symlink():
            raise ValueError("home native output already exists: " + str(output))
        output.write_text(body)
        recipes.append({"original": str(original), "sha256": digest,
                        "output": str(output),
                        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                        "edits": [{"old": old, "new": new} for old, new in edits]})
    return recipes
