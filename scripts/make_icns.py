"""Build the macOS app icon (.icns) from the PNG logo, without Pillow.

ICNS is a simple container ("icns" header + typed chunks); since macOS 10.7
each chunk may hold plain PNG data. PyQt6 (already a dependency) does the
resizing.

Usage: uv run python scripts/make_icns.py [src.png] [dest.icns]
"""

import struct
import sys
from pathlib import Path

from PyQt6.QtCore import QBuffer, QIODevice, Qt
from PyQt6.QtGui import QImage

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "blackboard_sync" / "assets" / "logo.png"
DEST = ROOT / "packaging" / "macos" / "icon.icns"

# (OSType, pixel size): 1x and @2x (retina) variants
CHUNKS = [
    (b"icp4", 16), (b"ic11", 32),
    (b"icp5", 32), (b"ic12", 64),
    (b"ic07", 128), (b"ic13", 256),
    (b"ic08", 256), (b"ic14", 512),
    (b"ic09", 512),
]


def png_bytes(image: QImage, size: int) -> bytes:
    scaled = image.scaled(size, size,
                          Qt.AspectRatioMode.KeepAspectRatio,
                          Qt.TransformationMode.SmoothTransformation)
    buf = QBuffer()
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    if not scaled.save(buf, "PNG"):
        raise RuntimeError(f"failed to encode {size}px PNG")
    return bytes(buf.data())


def build_icns(src: Path, dest: Path) -> None:
    image = QImage(str(src))
    if image.isNull():
        raise SystemExit(f"cannot read {src}")

    body = b""
    for ostype, size in CHUNKS:
        data = png_bytes(image, size)
        body += ostype + struct.pack(">I", len(data) + 8) + data

    dest.write_bytes(b"icns" + struct.pack(">I", len(body) + 8) + body)


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC
    dest = Path(sys.argv[2]) if len(sys.argv) > 2 else DEST
    build_icns(src, dest)
    print(f"wrote {dest}")
