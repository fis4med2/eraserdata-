#!/usr/bin/env python3
"""
Strips metadata (EXIF, GPS, etc.) from photos and images automatically.

Usage:
    python clean_metadata.py "C:/Users/YourUser/Pictures"
    python clean_metadata.py "C:/Users/YourUser/Pictures" --overwrite

By default, creates cleaned copies inside a "no_metadata" subfolder
(original files are left untouched). Use --overwrite to clean the
original files directly (WARNING: this is irreversible).

Supported formats: JPG, JPEG, PNG, WEBP, TIFF, BMP
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"}


def clean_image(source_path: Path, dest_path: Path) -> bool:
    """Removes all metadata from an image and saves it to the destination."""
    try:
        with Image.open(source_path) as img:
            img.load()
            # Rebuild the image from raw pixel bytes only, discarding EXIF/GPS/comments
            clean_img = Image.frombytes(img.mode, img.size, img.tobytes())
            image_format = img.format

            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if image_format == "JPEG":
                clean_img.save(dest_path, format="JPEG", quality=95)
            else:
                clean_img.save(dest_path, format=image_format)

        return True
    except Exception as e:
        print(f"  [ERROR] Could not process {source_path.name}: {e}")
        return False


def process_folder(folder: Path, overwrite: bool):
    folder = folder.resolve()
    if not folder.is_dir():
        print(f"Folder not found: {folder}")
        sys.exit(1)

    files = [
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS
        and "no_metadata" not in p.parts
    ]

    if not files:
        print("No images found in this folder.")
        return

    print(f"Found {len(files)} image(s). Processing...\n")

    success = 0
    for file in files:
        if overwrite:
            dest = file  # overwrite the file itself
            temp = file.with_name(f"~tmp_{file.name}")
            if clean_image(file, temp):
                temp.replace(dest)
                success += 1
                print(f"  [OK] {file.name} (original overwritten)")
        else:
            dest = file.parent / "no_metadata" / file.name
            if clean_image(file, dest):
                success += 1
                print(f"  [OK] {file.name} -> {dest.relative_to(folder)}")

    print(f"\nDone: {success}/{len(files)} images cleaned successfully.")


def main():
    parser = argparse.ArgumentParser(description="Removes metadata from photos/screenshots.")
    parser.add_argument("folder", help="Path to the folder containing the images")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite original files instead of creating cleaned copies",
    )
    args = parser.parse_args()

    process_folder(Path(args.folder), args.overwrite)


if __name__ == "__main__":
    main()
