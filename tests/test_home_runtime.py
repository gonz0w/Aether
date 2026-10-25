# SPDX-License-Identifier: BSD-2-Clause
"""Focused constructor controls; fake commands manipulate real ar containers."""
from pathlib import Path
import hashlib
import io
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from home_runtime import archive_names, runtime_archive, sealed


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_archive(path, members):
    data = bytearray(b"!<arch>\n")
    for name, body in members:
        fields = ((name + "/").ljust(16), "0".ljust(12), "0".ljust(6),
                  "0".ljust(6), "100644".ljust(8), str(len(body)).ljust(10), "`\n")
        data.extend("".join(fields).encode())
        data.extend(body)
        if len(body) % 2:
            data.extend(b"\n")
    path.write_bytes(data)


def read_archive(path):
    raw = path.read_bytes()
    if not raw.startswith(b"!<arch>\n"):
        raise ValueError("test ar header")
    result, position = [], 8
    while position < len(raw):
        header = raw[position:position + 60]
        if len(header) != 60 or header[-2:] != b"`\n":
            raise ValueError("test ar member")
        length = int(header[48:58])
        name = header[:16].decode().strip().removesuffix("/")
        position += 60
        result.append((name, raw[position:position + length]))
        position += length + length % 2
    return result


class FakeCommand:
    def __init__(self, mutation=None):
        self.mutation, self.calls = mutation, []

    def __call__(self, args, log, rejection=None):
        args = list(map(str, args))
        self.calls.append(args)
        if "-c" in args:
            source = Path(args[args.index("-c") + 1])
            output = Path(args[args.index("-o") + 1])
            selected = "aether_pool_failure_site" in source.read_text()
            output.write_bytes(b"selected-backend" if selected else b"original-backend")
            return ""
        operation, archive = args[1], Path(args[2])
        members = read_archive(archive)
        if operation == "t":
            return "".join(name + "\n" for name, _ in members)
        if operation == "x":
            output = Path(next(arg.split("=", 1)[1] for arg in args if arg.startswith("--output=")))
            for name, body in members:
                (output / name).write_bytes(body)
            return ""
        if operation == "rcs":
            replacement = Path(args[3])
            members = [(name, replacement.read_bytes() if name == replacement.name else body)
                       for name, body in members]
            if self.mutation == "unaffected":
                members = [(name, b"mutated" if name == "a.o" else body) for name, body in members]
            if self.mutation == "order":
                members.reverse()
            if self.mutation == "duplicate":
                members.append(("backend.o", b"duplicate"))
            write_archive(archive, members)
            return ""
        raise ValueError("unexpected fake command: " + repr(args))


class HomeRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="home-runtime-test-", dir=ROOT / "userland/build")
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)

    def test_sealed_map_rejects_changed_missing_duplicate_and_extra_members(self):
        root = self.folder / "sealed"
        root.mkdir()
        (root / "one").write_bytes(b"one")
        seal = root / "SHA256SUMS"
        seal.write_text(sha(root / "one") + "  one\n")
        expected = sha(seal)
        self.assertEqual(sealed(root, expected, 1), {"one": sha(root / "one")})
        (root / "extra").write_bytes(b"extra")
        with self.assertRaisesRegex(ValueError, "inventory"):
            sealed(root, expected, 1)
        (root / "extra").unlink()
        (root / "one").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "member"):
            sealed(root, expected, 1)
        (root / "one").unlink()
        with self.assertRaisesRegex(ValueError, "member"):
            sealed(root, expected, 1)
        (root / "one").write_bytes(b"one")
        seal.write_text((sha(root / "one") + "  one\n") * 2)
        with self.assertRaisesRegex(ValueError, "path"):
            sealed(root, sha(seal), 2)

    def test_sealed_map_rejects_traversal_and_symlinks(self):
        root = self.folder / "sealed"
        root.mkdir()
        seal = root / "SHA256SUMS"
        seal.write_text("0" * 64 + "  ../outside\n")
        with self.assertRaisesRegex(ValueError, "path"):
            sealed(root, sha(seal), 1)
        (root / "target").write_bytes(b"x")
        (root / "alias").symlink_to(root / "target")
        seal.write_text(sha(root / "target") + "  alias\n")
        with self.assertRaisesRegex(ValueError, "symlink"):
            sealed(root, sha(seal), 1)

    def test_sdk_receipt_alias_requires_its_enclosing_seal_identity(self):
        root = self.folder / "sdk"
        root.mkdir()
        (root / "one").write_bytes(b"one")
        (root / "evidence.json").write_bytes(b"enclosing sealed receipt")
        seal = root / "SHA256SUMS"
        seal.write_text(sha(root / "one") + "  one\n")
        enclosing = {"evidence.json": sha(root / "evidence.json")}
        self.assertEqual(sealed(root, sha(seal), 1, enclosing=enclosing),
                         {"one": sha(root / "one")})
        (root / "evidence.json").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "enclosing"):
            sealed(root, sha(seal), 1, enclosing=enclosing)

    def test_archive_member_map_rejects_missing_duplicate_and_unsafe_backend(self):
        self.assertEqual(archive_names("a.o\nbackend.o\n"), ["a.o", "backend.o"])
        for text in ("a.o\n", "backend.o\nbackend.o\n", "../backend.o\n", "x/backend.o\n"):
            with self.assertRaises(ValueError):
                archive_names(text)

    def fixture(self):
        dependency = self.folder / "dependency"
        dependency.mkdir()
        source = ROOT / ".deps/native-utc-v3/base/source/experiments/native-service-runtime"
        for name in ("base", "utc"):
            write_archive(dependency / (name + ".a"), [("a.o", b"unaffected"),
                ("backend.o", b"original-backend"), ("real_time.o", name.encode())])
        archive = dependency / "musl.tar.gz"
        with tarfile.open(archive, "w:gz") as out:
            data = b"/* bounded test header */\n"
            member = tarfile.TarInfo("musl-1.2.6/arch/x86_64/syscall_arch.h")
            member.size = len(data)
            out.addfile(member, io.BytesIO(data))
        sdk = dependency / "sdk"
        (sdk / "stage/usr/include").mkdir(parents=True)
        report = {"source_root": str(source), "sdk": str(sdk), "musl_archive": str(archive),
            "utc_archive": str(dependency / "utc.a"), "base_archive": str(dependency / "base.a"),
            "inputs": {str(p): sha(p) for p in [*source.glob("*.h"), source / "backend.c", source / "build.py", archive,
                                               dependency / "utc.a", dependency / "base.a"]},
            "seals": {"test_only": True}, "tools": {"clang": {"path": "fake-clang"}, "ar": {"path": "fake-ar"}}}
        return dependency, report

    def construct(self, mutation=None):
        dependency, report = self.fixture()
        port = self.folder / "port"
        port.mkdir()
        fake = FakeCommand(mutation)
        with patch("home_runtime.verify_dependency", return_value=report):
            result = runtime_archive(port, dependency, report["tools"], fake)
        return result, port, fake

    def test_fake_commands_modify_only_backend_in_actual_ar_containers(self):
        result, port, fake = self.construct()
        archive = port / "failure-runtime/libaether_runtime.a"
        self.assertEqual(read_archive(archive), [("a.o", b"unaffected"),
            ("backend.o", b"selected-backend"), ("real_time.o", b"utc")])
        self.assertEqual(result["archive_sha256"], sha(archive))
        self.assertEqual(result["original_backend_sha256"], hashlib.sha256(b"original-backend").hexdigest())
        self.assertNotEqual(result["selected_backend_sha256"], result["original_backend_sha256"])
        self.assertEqual(sum("-c" in row for row in fake.calls), 2)
        self.assertFalse((port / "failure-runtime-checkout").exists())

    def test_mutated_unaffected_member_duplicate_or_reordering_cannot_pass(self):
        for mutation in ("unaffected", "duplicate", "order"):
            with self.subTest(mutation=mutation):
                dependency, report = self.fixture()
                port = self.folder / ("port-" + mutation)
                port.mkdir()
                with patch("home_runtime.verify_dependency", return_value=report):
                    with self.assertRaisesRegex(ValueError, "member|order"):
                        runtime_archive(port, dependency, report["tools"], FakeCommand(mutation))
                import shutil
                shutil.rmtree(dependency)

    def test_original_backend_mismatch_is_not_a_fallback(self):
        dependency, report = self.fixture()
        write_archive(dependency / "base.a", [("a.o", b"unaffected"), ("backend.o", b"wrong")])
        report["inputs"][str(dependency / "base.a")] = sha(dependency / "base.a")
        port = self.folder / "port"
        port.mkdir()
        command = FakeCommand()
        with patch("home_runtime.verify_dependency", return_value=report):
            with self.assertRaisesRegex(ValueError, "backend.*differ|backend.*mismatch"):
                runtime_archive(port, dependency, report["tools"], command)
        self.assertEqual(sum("-c" in row for row in command.calls), 1)


if __name__ == "__main__":
    unittest.main()
