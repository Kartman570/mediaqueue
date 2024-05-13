# Mediaqueue

A local review queue for audio, images and video. It scans files into SQLite,
finds duplicates by SHA-256 and copies reviewed files into tagged folders.
Original files are never moved or deleted.

Requires Python 3.9 or newer. Runtime code uses only the standard library.

```sh
python3 -m mediaqueue --db media.sqlite3 scan /path/to/media
python3 -m mediaqueue --db media.sqlite3 list
python3 -m mediaqueue --db media.sqlite3 duplicates
python3 -m mediaqueue --db media.sqlite3 inspect /path/to/sound.wav
python3 -m mediaqueue --db media.sqlite3 mark 1 reviewed --tag music
python3 -m mediaqueue --db media.sqlite3 organize /path/to/sorted
python3 -m mediaqueue --db media.sqlite3 organize /path/to/sorted --apply
```

`organize` previews the exact copy plan unless `--apply` is supplied. Copies
use exclusive creation and verify the scan checksum first. Existing targets
get a checksum suffix; an unresolved collision aborts instead of overwriting.
A failed batch may leave already completed copies. Review its output and files
before retrying. Do not modify sources concurrently with a copy operation.

Supported scan extensions: WAV, MP3, FLAC, PNG, JPG, JPEG, MP4 and MKV.
Detailed inspection reads PCM WAV metadata and PNG dimensions. Other formats
report their filename and size; this is not a decoder or transcoder. Symlinks
are skipped. Removed source files stay in the catalog for manual review.

```sh
python3 -m unittest discover -s tests -v
python3 -m pip install -r requirements-dev.txt
ruff check .
```
