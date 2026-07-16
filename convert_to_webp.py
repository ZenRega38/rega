# -*- coding: utf-8 -*-
"""
convert_to_webp.py
==================
Converts all images (JPG, JPEG, PNG, etc.) and PDFs (first page only)
in assets/img/ and assets/certificates/ to .webp format, then deletes originals.

Requirements:
    pip install Pillow pdf2image

For pdf2image on Windows, Poppler is required.
This script will auto-download a portable Poppler if not found on PATH.
"""

import os
import sys
import shutil
import zipfile
import urllib.request
from pathlib import Path
from PIL import Image

# ─── CONFIG ───────────────────────────────────────────────────────────────────
WEBP_QUALITY = 82          # 0-100; 82 is a good balance of quality & size
PDF_DPI      = 150         # DPI for PDF rendering (150 = good quality, fast)

IMG_DIR  = Path(__file__).parent / "assets" / "img"
CERT_DIR = Path(__file__).parent / "assets" / "certificates"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif"}
PDF_EXT    = ".pdf"
SKIP_FILES = {".ds_store", "thumbs.db"}

# Portable Poppler for Windows (if needed)
POPPLER_URL = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.07.0-0/Release-24.07.0-0.zip"
POPPLER_DIR = Path(__file__).parent / "_poppler"

# ─── POPPLER SETUP ────────────────────────────────────────────────────────────

def find_poppler_path():
    """Return path to Poppler bin if available, else None."""
    # Check if already on PATH
    if shutil.which("pdftoppm"):
        return None  # Let pdf2image find it automatically

    # Check our local portable copy
    candidates = list(POPPLER_DIR.glob("**/bin"))
    if candidates:
        return str(candidates[0])

    return "NOT_FOUND"


def download_poppler():
    """Download and extract portable Poppler for Windows."""
    print("[DL] Poppler not found. Downloading portable Poppler for Windows...")
    POPPLER_DIR.mkdir(exist_ok=True)
    zip_path = POPPLER_DIR / "poppler.zip"

    def progress(block, block_size, total):
        downloaded = block * block_size
        pct = min(downloaded / total * 100, 100) if total > 0 else 0
        print(f"\r   {pct:.1f}%", end="", flush=True)

    urllib.request.urlretrieve(POPPLER_URL, zip_path, reporthook=progress)
    print("\n   Extracting...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(POPPLER_DIR)
    zip_path.unlink()
    print("   [OK] Poppler ready.\n")


def get_poppler_path():
    path = find_poppler_path()
    if path == "NOT_FOUND":
        download_poppler()
        path = find_poppler_path()
        if path == "NOT_FOUND":
            print("[FAIL] Could not locate Poppler. PDFs will be skipped.")
            return None
    return path  # None = system PATH, string = explicit path

# ─── CONVERSION HELPERS ───────────────────────────────────────────────────────

def convert_image_to_webp(src: Path, quality: int = WEBP_QUALITY) -> bool:
    """Convert a single image file to .webp next to it, delete original."""
    dst = src.with_suffix(".webp")
    if dst.exists():
        # Already converted — just delete the source
        src.unlink()
        print(f"   [SKIP] Already exists, removed source: {src.name}")
        return True
    try:
        with Image.open(src) as img:
            # Convert RGBA/P/LA to RGB for WebP compatibility
            if img.mode in ("RGBA", "LA"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1])
                img = bg
            elif img.mode == "P":
                img = img.convert("RGB")
            img.save(dst, "WEBP", quality=quality, method=6)
        src.unlink()
        orig_kb = 0  # already gone if we got here
        new_kb   = dst.stat().st_size / 1024
        print(f"   [OK]  {src.name} -> {dst.name}  ({new_kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"   [FAIL] {src.name}: {e}")
        return False


def convert_pdf_to_webp(src: Path, poppler_path, quality: int = WEBP_QUALITY) -> bool:
    """Render the first page of a PDF as .webp, delete original PDF."""
    try:
        from pdf2image import convert_from_path
    except ImportError:
        print("   [WARN] pdf2image not installed. Skipping PDF:", src.name)
        return False

    dst = src.with_suffix(".webp")
    if dst.exists():
        src.unlink()
        print(f"   [SKIP] Already exists, removed PDF: {src.name}")
        return True
    try:
        kwargs = dict(dpi=PDF_DPI, first_page=1, last_page=1, fmt="ppm")
        if poppler_path:
            kwargs["poppler_path"] = poppler_path

        pages = convert_from_path(str(src), **kwargs)
        if not pages:
            print(f"   [FAIL] {src.name}: No pages rendered")
            return False

        page = pages[0].convert("RGB")
        page.save(dst, "WEBP", quality=quality, method=6)
        src.unlink()
        new_kb = dst.stat().st_size / 1024
        print(f"   [OK]  {src.name} -> {dst.name}  ({new_kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"   [FAIL] {src.name}: {e}")
        return False

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def process_directory(directory: Path, poppler_path, label: str):
    """Walk a directory and convert all eligible files."""
    print(f"\n{'='*60}")
    print(f"[DIR] Processing: {label}")
    print(f"{'='*60}")

    ok = fail = skipped = 0

    for filepath in sorted(directory.rglob("*")):
        if not filepath.is_file():
            continue

        # Skip hidden/system files
        if filepath.name.lower() in SKIP_FILES:
            filepath.unlink()
            print(f"   [DEL] Deleted: {filepath.name}")
            continue

        ext = filepath.suffix.lower()

        if ext in IMAGE_EXTS:
            result = convert_image_to_webp(filepath)
            if result:
                ok += 1
            else:
                fail += 1

        elif ext == PDF_EXT:
            result = convert_pdf_to_webp(filepath, poppler_path)
            if result:
                ok += 1
            else:
                fail += 1

        elif ext == ".webp":
            skipped += 1  # Already WebP, leave it
        else:
            print(f"   [SKIP] Skipped (unknown type): {filepath.name}")
            skipped += 1

    print(f"\n   Summary: {ok} converted, {fail} failed, {skipped} already WebP/skipped")
    return ok, fail


def main():
    print("\n[START] WebP Converter -- Rega Portfolio")
    print("=" * 60)

    # Check Pillow
    try:
        from PIL import Image
        print("[OK] Pillow found")
    except ImportError:
        print("[FAIL] Pillow not found. Run: pip install Pillow")
        sys.exit(1)

    # Check pdf2image
    try:
        import pdf2image
        print("[OK] pdf2image found")
        has_pdf2image = True
    except ImportError:
        print("[WARN] pdf2image not found. PDFs will be skipped.")
        print("   Install with: pip install pdf2image")
        has_pdf2image = False

    # Setup Poppler if pdf2image available
    poppler_path = None
    if has_pdf2image:
        poppler_path = get_poppler_path()
        if poppler_path:
            print(f"[OK] Poppler found at: {poppler_path}")
        else:
            print("[OK] Poppler on system PATH")

    print()

    # Process directories
    total_ok = 0
    total_fail = 0

    if IMG_DIR.exists():
        ok, fail = process_directory(IMG_DIR, poppler_path, "assets/img/")
        total_ok += ok
        total_fail += fail
    else:
        print(f"[WARN] Directory not found: {IMG_DIR}")

    if CERT_DIR.exists():
        ok, fail = process_directory(CERT_DIR, poppler_path, "assets/certificates/")
        total_ok += ok
        total_fail += fail
    else:
        print(f"[WARN] Directory not found: {CERT_DIR}")

    print(f"\n{'='*60}")
    print(f"[DONE] Total: {total_ok} converted, {total_fail} failed")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
