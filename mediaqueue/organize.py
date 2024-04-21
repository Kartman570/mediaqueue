from pathlib import Path
import hashlib
import re
import shutil


def plan(rows, destination):
    destination = Path(destination).resolve()
    result = []
    occupied = set()
    for row in rows:
        if row['status'] != 'reviewed':
            continue
        folder = re.sub(r'[^A-Za-z0-9_-]+', '-', row['tag']).strip('-') or row['kind']
        source = Path(row['path'])
        target = destination / folder / source.name
        if str(target) in occupied or target.exists():
            target = target.with_name(source.stem + '-' + row['digest'][:12] + source.suffix)
        if str(target) in occupied or target.exists():
            raise ValueError('Destination collision: ' + str(target))
        occupied.add(str(target))
        result.append({'source': str(source), 'target': str(target), 'digest': row['digest']})
    return result


def apply(entries):
    copied = []
    for entry in entries:
        source, target = Path(entry['source']), Path(entry['target'])
        digest = hashlib.sha256()
        with source.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        if digest.hexdigest() != entry['digest']:
            raise ValueError('Source changed since scanning: ' + str(source))
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as output, source.open('rb') as stream:
            shutil.copyfileobj(stream, output)
        copied.append(str(target))
    return copied
