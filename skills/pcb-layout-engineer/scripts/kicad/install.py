#!/usr/bin/env python3
"""Install the pinned upstream Konnect binary into this checkout (Linux x86-64)."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import tarfile
import tempfile
import urllib.request

VERSION = "v0.13.0"
REPOSITORY = "mixelpixx/Konnect"
ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / ".cache" / "konnect" / VERSION


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "pcb-kicad-setup"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def select_asset(release):
    if release.get("tag_name") != VERSION or release.get("draft"):
        raise ValueError("Unexpected release identity")
    candidates = [a for a in release["assets"]
                  if a["name"].startswith("konnect-")
                  and "x86_64" in a["name"] and "linux" in a["name"]
                  and a["name"].endswith(".tar.gz")]
    if len(candidates) != 1:
        raise ValueError(f"Expected one Linux x86-64 archive; found {[a['name'] for a in candidates]}")
    asset = candidates[0]
    digest = asset.get("digest", "") or ""
    if not digest.startswith("sha256:") or len(digest) != 71:
        raise ValueError("Release asset has no GitHub SHA-256 digest; manual review required")
    expected_prefix = f"https://github.com/{REPOSITORY}/releases/download/{VERSION}/"
    if not asset["browser_download_url"].startswith(expected_prefix):
        raise ValueError("Unexpected download URL")
    return asset


def unpack_binary(archive, destination):
    # Copy exactly one regular file; never extract archive paths or symlinks.
    with tarfile.open(archive, "r:gz") as tar:
        members = [m for m in tar.getmembers() if Path(m.name).name == "konnect" and m.isfile()]
        if len(members) != 1:
            raise ValueError("Archive must contain exactly one regular konnect executable")
        with tar.extractfile(members[0]) as source, destination.open("xb") as target:
            shutil.copyfileobj(source, target)
    destination.chmod(0o755)


def main():
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise ValueError("This installer targets Ubuntu x86-64; choose another upstream release asset for other hosts")
    if DEST.exists():
        raise ValueError(f"Already exists: {DEST}. Use gateway.py doctor to inspect it; this installer does not overwrite installs")
    print(f"Fetching {REPOSITORY} {VERSION} release metadata…", flush=True)
    release = json.loads(fetch(f"https://api.github.com/repos/{REPOSITORY}/releases/tags/{VERSION}"))
    asset = select_asset(release)
    data = fetch(asset["browser_download_url"])
    actual = hashlib.sha256(data).hexdigest()
    if "sha256:" + actual != asset["digest"]:
        raise ValueError("Archive SHA-256 does not match GitHub release metadata")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="install-", dir=DEST.parent) as staging:
        staging = Path(staging)
        archive = staging / "download.tar.gz"
        archive.write_bytes(data)
        install = staging / "install"
        install.mkdir()
        unpack_binary(archive, install / "konnect")
        receipt = {"repository": REPOSITORY, "tag": VERSION,
                   "release_url": release["html_url"], "asset": asset["name"],
                   "archive_sha256": actual,
                   "binary_sha256": hashlib.sha256((install / "konnect").read_bytes()).hexdigest()}
        (install / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        os.rename(install, DEST)
    print(f"Installed: {DEST / 'konnect'}")
    print("Next: python3 scripts/kicad/gateway.py doctor")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, tarfile.TarError) as exc:
        print(f"Setup stopped: {exc}", file=sys.stderr)
        sys.exit(1)
