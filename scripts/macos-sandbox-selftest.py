"""Actual smoke checks for the offline Docker sandbox on macOS Apple Silicon.

Do NOT run this test on the macOS host. Run through scripts/macos-safe.sh doctor.
"""
from pathlib import Path
import os
import socket
import subprocess
import sys


def must_fail_write(path: Path) -> None:
    try:
        path.write_text("probe", encoding="utf-8")
    except OSError:
        return
    try:
        path.unlink()
    finally:
        raise RuntimeError(f"Write unexpectedly allowed: {path}")


def main() -> None:
    if not Path("/workspace/Dockerfile.macos-safe").is_file():
        raise RuntimeError("Not in the expected Docker image")
    if os.geteuid() == 0:
        raise RuntimeError("Container must not run as root")
    if Path("/root/.ssh").exists() or Path("/root/.codex").exists():
        raise RuntimeError("Host credential directories appear to be mounted")
    must_fail_write(Path("/workspace/.write-test"))
    must_fail_write(Path("/workspace/input/.write-test"))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(3)
        try:
            client.connect(("1.1.1.1", 443))
        except OSError:
            pass
        else:
            raise RuntimeError("Container unexpectedly has external network access")

    output = Path("/workspace/output/_macos_sandbox_test.mp4")
    try:
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", "color=black:s=320x180:r=24",
                "-t", "1", "-c:v", "mpeg4", str(output),
            ],
            check=True,
            timeout=30,
        )
        if not output.is_file() or output.stat().st_size < 100:
            raise RuntimeError("FFmpeg output verification failed")
        subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1", str(output)],
            check=True,
            timeout=10,
        )
    finally:
        output.unlink(missing_ok=True)
    print(f"PASS: python={sys.version.split()[0]}, uid={os.geteuid()}, network=blocked, rootfs=readonly, input=readonly, ffmpeg=working")


if __name__ == "__main__":
    main()
