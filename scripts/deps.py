"""Fetch pinned boot inputs. Builds themselves never access the network."""
import bz2
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DEPS = ROOT / ".deps"
LOCK = json.loads((ROOT / "boot/dependencies.json").read_text())


def checked(data, digest):
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("dependency SHA-256 mismatch")
    return data


def download(entry):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "download"
        subprocess.run(["curl", "--fail", "--location", "--silent", "--show-error",
                        "--max-time", "120", entry["url"], "--output", str(path)], check=True)
        return checked(path.read_bytes(), entry["sha256"])


def setup():
    # Extract only named regular files; never unpack archive paths wholesale.
    files = {}
    with tarfile.open(fileobj=io.BytesIO(download(LOCK["limine"])), mode="r:gz") as archive:
        for name in ("BOOTX64.EFI", "limine-uefi-cd.bin", "LICENSE"):
            member = archive.getmember("limine-binary/" + name)
            if not member.isfile():
                raise ValueError("unexpected Limine archive member")
            files["limine/" + name] = archive.extractfile(member).read()
    for name, entry in LOCK["firmware"].items():
        files["firmware/" + name + ".fd"] = checked(bz2.decompress(download(entry)), entry["unpacked_sha256"])
    manifest = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    for name, data in files.items():
        path = DEPS / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (DEPS / "manifest.json").write_text(json.dumps({"lock": hashlib.sha256((ROOT / "boot/dependencies.json").read_bytes()).hexdigest(), "files": manifest}, indent=2) + "\n")
    print("Pinned Limine and OVMF inputs installed in .deps/")


def verify():
    try:
        manifest = json.loads((DEPS / "manifest.json").read_text())
        checked((ROOT / "boot/dependencies.json").read_bytes(), manifest["lock"])
        for name, digest in manifest["files"].items():
            checked((DEPS / name).read_bytes(), digest)
    except (OSError, ValueError, KeyError) as error:
        raise RuntimeError("Missing or changed boot dependencies; run python3 scripts/deps.py") from error


if __name__ == "__main__":
    setup()
