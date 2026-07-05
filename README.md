# Metadata Protector

Python tools to automatically strip metadata (EXIF, GPS, device model, timestamps, etc.) from photos and screenshots — protecting sensitive information like your location.

## Why this matters

Photos taken with a phone often carry EXIF metadata, including the exact GPS coordinates of where the photo was taken. When you share those photos (social media, messaging apps, forums), you might unintentionally reveal where you live, work, or spent your day.

This project offers two ways to handle that:

- **`clean_metadata.py`** — runs once, processing an entire folder (and subfolders).
- **`watch_metadata.py`** — runs continuously in the background, watching folders and automatically cleaning every new image that appears.

## Installation

```bash
git clone https://github.com/your-username/metadata-protector.git
cd metadata-protector
pip install -r requirements.txt
```

Requires Python 3.8+.

## Usage

### Manual mode (one-time processing)

```bash
python src/clean_metadata.py "C:\Users\YourUser\Pictures"
```

By default, this creates cleaned copies inside a `no_metadata/` subfolder without touching the original files.

To overwrite the original files directly:

```bash
python src/clean_metadata.py "C:\Users\YourUser\Pictures" --overwrite
```

### Automatic mode (background watcher)

1. Open `src/watch_metadata.py` and edit the `WATCHED_FOLDERS` list with the folders you want to watch.
2. Run:

```bash
python src/watch_metadata.py
```

The script stays active, and every time a new image lands in one of the configured folders (including subfolders), its metadata gets stripped automatically.

#### Run it automatically on Windows startup (no visible window)

1. Create a file named `start_watcher.vbs` with the content below (adjust the paths):

   ```vbs
   Set objShell = CreateObject("WScript.Shell")
   objShell.Run "pythonw.exe C:\path\to\src\watch_metadata.py", 0, False
   ```

2. Press `Win + R`, type `shell:startup`, and press Enter.
3. Place a shortcut to `start_watcher.vbs` inside that folder.

This way, the watcher launches automatically when Windows starts, with no console window visible.

## Supported formats

JPG, JPEG, PNG, WEBP, TIFF, BMP.

## Limitations

- This removes metadata **from the file** (EXIF/GPS/etc.), but does not edit the visual content of the image. If an address, license plate, or document is *visible* in the photo itself, that needs to be removed manually (cropping, blurring, etc.), since it isn't metadata.
- It's recommended to test on a sample folder first before using `--overwrite` or leaving the watcher active on folders with important files.

## License

MIT — see [LICENSE](LICENSE).
