#!/usr/bin/env python3
"""
Watches one or more folders in the background and automatically strips
metadata (EXIF, GPS, etc.) from every new photo/screenshot that appears.

Install:
    pip install Pillow watchdog

Usage:
    python watch_metadata.py

Edit the WATCHED_FOLDERS list below with the folders you want to watch
(e.g. Pictures, Screenshots, Downloads, your messaging app's media folder, etc.)

The script keeps running, and as soon as a new image is created/copied
into one of these folders, it automatically strips its metadata
(overwriting the file itself).

To have this always run in the background on Windows startup, see the
instructions at the bottom of this file (Startup folder / Task Scheduler).
"""

import time
import logging
from pathlib import Path

from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ======= CONFIG: edit the folders you want to watch here =======
WATCHED_FOLDERS = [
    r"C:\Users\YourUser\OneDrive\Pictures",
    # add more folders here, one per line
]
# =================================================================

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("metadata-cleaner")


def clean_image(path: Path, attempts=5, wait=0.5) -> bool:
    """Removes metadata from an image, overwriting the file itself."""
    for attempt in range(attempts):
        try:
            with Image.open(path) as img:
                img.load()
                clean_img = Image.frombytes(img.mode, img.size, img.tobytes())
                image_format = img.format

            temp = path.with_name(f"~tmp_{path.name}")
            if image_format == "JPEG":
                clean_img.save(temp, format="JPEG", quality=95)
            else:
                clean_img.save(temp, format=image_format)

            temp.replace(path)
            return True
        except (PermissionError, OSError):
            # file may still be being written (e.g. a screenshot being saved); retry
            time.sleep(wait)
        except Exception as e:
            log.error(f"Failed to clean {path.name}: {e}")
            return False
    log.error(f"Could not access {path.name} after {attempts} attempts.")
    return False


class ImageHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self._recently_processed = {}  # path -> timestamp
        self._ignore_window = 5  # seconds: ignore reprocessing within this window

    def _already_processed_now(self, path: Path) -> bool:
        now = time.time()
        last = self._recently_processed.get(str(path))
        if len(self._recently_processed) > 500:
            self._recently_processed = {
                k: v for k, v in self._recently_processed.items()
                if now - v < self._ignore_window
            }
        if last is not None and (now - last) < self._ignore_window:
            return True
        return False

    def _process(self, path_str: str):
        path = Path(path_str)
        if path.suffix.lower() not in VALID_EXTENSIONS or path.name.startswith("~tmp_"):
            return
        if self._already_processed_now(path):
            return

        # small delay to make sure the file has finished being written
        time.sleep(0.3)
        if clean_image(path):
            self._recently_processed[str(path)] = time.time()
            log.info(f"Metadata removed: {path.name}")

    def on_created(self, event):
        if not event.is_directory:
            self._process(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._process(event.dest_path)


def main():
    valid_folders = []
    for folder in WATCHED_FOLDERS:
        p = Path(folder)
        if p.is_dir():
            valid_folders.append(p)
        else:
            log.warning(f"Folder not found, skipping: {folder}")

    if not valid_folders:
        log.error("No valid folders to watch. Edit WATCHED_FOLDERS in the script.")
        return

    observer = Observer()
    handler = ImageHandler()
    for folder in valid_folders:
        observer.schedule(handler, str(folder), recursive=True)
        log.info(f"Watching: {folder}")

    observer.start()
    log.info("Running in the background. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        log.info("Stopped.")
    observer.join()


if __name__ == "__main__":
    main()

"""
========================================================================
HOW TO KEEP THIS ALWAYS RUNNING IN THE BACKGROUND (no console window):
========================================================================

Simple option (starts with Windows, no visible black window):

1. Create a file "start_watcher.vbs" in the same folder as this script,
   with the content below (adjust the python and script paths):

    Set objShell = CreateObject("WScript.Shell")
    objShell.Run "pythonw.exe C:\path\to\watch_metadata.py", 0, False

2. Press Win+R, type "shell:startup" and press Enter.
3. Place a shortcut to "start_watcher.vbs" inside that folder.

Done: every time Windows starts, the watcher will launch automatically,
with no visible window, and will keep cleaning metadata from new
photos/screenshots that land in the configured folders.

Use "pythonw.exe" (not "python.exe") to avoid opening a console window.
========================================================================
"""
