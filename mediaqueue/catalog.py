import sqlite3


def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS media (
        id INTEGER PRIMARY KEY, path TEXT UNIQUE NOT NULL,
        size INTEGER NOT NULL, digest TEXT NOT NULL, kind TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'new', tag TEXT NOT NULL DEFAULT ''
    )""")
    db.commit()
    return db


def items(db, status=None):
    if status:
        return [dict(row) for row in db.execute(
            'SELECT * FROM media WHERE status = ? ORDER BY path', (status,))]
    return [dict(row) for row in db.execute('SELECT * FROM media ORDER BY path')]


def scan(db, root):
    from pathlib import Path
    import hashlib
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('Input must be a directory')
    supported = {'.wav': 'audio', '.mp3': 'audio', '.flac': 'audio',
                 '.png': 'image', '.jpg': 'image', '.jpeg': 'image',
                 '.mp4': 'video', '.mkv': 'video'}
    count = 0
    for path in sorted(root.rglob('*')):
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in supported:
            continue
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        db.execute("""INSERT INTO media(path, size, digest, kind) VALUES (?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
            status=CASE WHEN digest<>excluded.digest THEN 'new' ELSE status END,
            size=excluded.size, digest=excluded.digest, kind=excluded.kind""",
            (str(path), path.stat().st_size, digest.hexdigest(), supported[path.suffix.lower()]))
        count += 1
    db.commit()
    return count


def duplicates(db):
    groups = {}
    for row in items(db):
        groups.setdefault(row['digest'], []).append(row['path'])
    return [paths for paths in groups.values() if len(paths) > 1]


def mark(db, item_id, status, tag=''):
    if status not in {'new', 'reviewed', 'skipped'}:
        raise ValueError('Unknown status')
    cursor = db.execute('UPDATE media SET status=?, tag=? WHERE id=?', (status, tag, item_id))
    if not cursor.rowcount:
        raise ValueError('Media item not found')
    db.commit()
