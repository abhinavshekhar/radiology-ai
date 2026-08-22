"""Generate demo chest X-ray samples — no external dependencies."""

import struct
import zlib
from pathlib import Path

OUT_DIR = Path(__file__).parent.parent / "demo_samples"


def _write_png(path: Path, width: int, height: int, fill: int, patches: list):
    """Write a grayscale PNG with optional darker rectangular patches."""
    pixels = bytearray()
    for y in range(height):
        pixels.append(0)  # filter byte
        for x in range(width):
            val = fill
            for px, py, pw, ph, pv in patches:
                if px <= x < px + pw and py <= y < py + ph:
                    val = pv
            pixels.append(val)

    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    compressed = zlib.compress(bytes(pixels), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    path.write_bytes(png)
    print(f"  [OK] {path.name}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Normal chest X-ray — bright lung fields
    _write_png(
        OUT_DIR / "normal_demo.jpg",
        512, 512, 140,
        patches=[(230, 250, 60, 80, 70)],  # heart shadow
    )

    # Pneumonia — darker lower-lobe opacities
    _write_png(
        OUT_DIR / "pneumonia_demo.jpg",
        512, 512, 140,
        patches=[
            (90, 330, 140, 100, 40),
            (285, 350, 125, 100, 45),
            (230, 250, 60, 80, 70),
        ],
    )

    # CT nodule-like bright blob
    _write_png(
        OUT_DIR / "ct_nodule_demo.jpg",
        512, 512, 90,
        patches=[(180, 160, 70, 70, 200), (300, 280, 40, 40, 180)],
    )
    # MRI tumor-like bright region
    _write_png(
        OUT_DIR / "mri_tumor_demo.jpg",
        512, 512, 50,
        patches=[(200, 180, 110, 90, 210)],
    )
    # Ultrasound lesion
    _write_png(
        OUT_DIR / "us_breast_demo.jpg",
        512, 512, 160,
        patches=[(190, 200, 90, 70, 40)],
    )

    print(f"\nDemo samples ready: {OUT_DIR}")


if __name__ == "__main__":
    main()
