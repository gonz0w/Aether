"""Consumer pin rejection in disposable copies; never execute altered release code."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

DOCS = Path(__file__).resolve().parents[1] / "docs"
PROFILES = (("experience", "experience"), ("standards", "foundations"),
            ("distribution", "distribution"))


class StandardsPins(unittest.TestCase):
    def exercise(self, mutation=None):
        for consumer, release in PROFILES:
            with self.subTest(profile=release), tempfile.TemporaryDirectory() as directory:
                docs = Path(directory)
                checker = docs / f"check-{consumer}.py"
                lock = docs / f"{consumer}.lock"
                shutil.copyfile(DOCS / checker.name, checker)
                shutil.copyfile(DOCS / lock.name, lock)
                vendor = docs / "vendor" / f"aether-{release}" / "v0.1.0"
                shutil.copytree(DOCS / "vendor" / f"aether-{release}" / "v0.1.0", vendor)
                sentinel = docs / "UNTRUSTED-CHECKER-EXECUTED"
                if mutation:
                    mutation(vendor, lock, sentinel)
                result = subprocess.run([sys.executable, str(checker)], capture_output=True,
                                        text=True, timeout=15)
                if mutation:
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse(sentinel.exists(), "unverified release code executed")

    def test_pinned_releases_pass(self):
        self.exercise()

    def test_changed_checker_cannot_execute(self):
        def mutate(vendor, lock, sentinel):
            (vendor / "conformance/check.py").write_text(
                f"from pathlib import Path\nPath({str(sentinel)!r}).touch()\n")
        self.exercise(mutate)

    def test_duplicate_pin_field_rejected(self):
        self.exercise(lambda vendor, lock, sentinel:
                      lock.write_text(lock.read_text() + "version=v0.1.0\n"))

    def test_unsafe_version_rejected(self):
        def mutate(vendor, lock, sentinel):
            shutil.copytree(vendor, lock.parent / "outside")
            lock.write_text(lock.read_text().replace("version=v0.1.0", "version=../../outside"))
        self.exercise(mutate)

    def test_changed_manifest_rejected(self):
        self.exercise(lambda vendor, lock, sentinel:
                      (vendor / "SHA256SUMS").write_text("0" * 64 + "  README.md\n"))

    def test_missing_file_rejected(self):
        self.exercise(lambda vendor, lock, sentinel: (vendor / "README.md").unlink())

    def test_extra_file_rejected(self):
        self.exercise(lambda vendor, lock, sentinel: (vendor / "extra.txt").write_text("extra\n"))

    def test_same_bytes_through_symlink_rejected(self):
        def mutate(vendor, lock, sentinel):
            original = vendor / "README.md"
            outside = lock.parent / "outside.md"
            shutil.copyfile(original, outside)
            original.unlink()
            original.symlink_to(outside)
        self.exercise(mutate)

    def test_wrong_source_rejected(self):
        self.exercise(lambda vendor, lock, sentinel:
                      lock.write_text(lock.read_text().replace("source_project=Aether-standards", "source_project=other")))

    def test_symlink_release_root_rejected(self):
        def mutate(vendor, lock, sentinel):
            outside = lock.parent / "outside-release"
            vendor.rename(outside)
            vendor.symlink_to(outside, target_is_directory=True)
        self.exercise(mutate)
