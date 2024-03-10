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
