import tempfile
import unittest
from pathlib import Path
import wave
from mediaqueue.catalog import connect, scan, items, mark, duplicates
from mediaqueue.inspect import inspect_file
from mediaqueue.organize import plan, apply


class MediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.db = connect(self.root / 'queue.sqlite3')
        self.addCleanup(self.db.close)

    def audio(self, name='sound.wav'):
        path = self.source / name
        with wave.open(str(path), 'wb') as stream:
            stream.setnchannels(1)
            stream.setsampwidth(2)
            stream.setframerate(8000)
            stream.writeframes(b'\0\0' * 800)
        return path

    def test_scan_review_and_copy(self):
        source = self.audio()
        self.assertEqual(scan(self.db, self.source), 1)
        self.assertEqual(scan(self.db, self.source), 1)
        self.assertEqual(len(items(self.db)), 1)
        mark(self.db, 1, 'reviewed', 'music')
        entries = plan(items(self.db), self.root / 'sorted')
        copied = apply(entries)
        self.assertEqual(Path(copied[0]).read_bytes(), source.read_bytes())
        self.assertTrue(source.exists())
        with self.assertRaises(FileExistsError):
            apply(entries)

    def test_metadata(self):
        result = inspect_file(self.audio())
        self.assertEqual(result['sample_rate'], 8000)
        self.assertEqual(result['seconds'], 0.1)

    def test_duplicate_contents(self):
        self.audio('one.wav')
        self.audio('two.wav')
        scan(self.db, self.source)
        self.assertEqual(len(duplicates(self.db)), 1)

    def test_changed_source_is_rejected(self):
        source = self.audio()
        scan(self.db, self.source)
        mark(self.db, 1, 'reviewed')
        entries = plan(items(self.db), self.root / 'sorted')
        source.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            apply(entries)
        self.assertFalse(Path(entries[0]['target']).exists())

    def test_unknown_item_and_status(self):
        with self.assertRaises(ValueError):
            mark(self.db, 100, 'reviewed')
        with self.assertRaises(ValueError):
            mark(self.db, 100, 'missing')

    def test_symlinks_are_skipped(self):
        source = self.audio()
        (self.source / 'link.wav').symlink_to(source)
        scan(self.db, self.source)
        self.assertEqual(len(items(self.db)), 1)

    def test_invalid_header(self):
        path = self.source / 'bad.png'
        path.write_bytes(b'not an image')
        with self.assertRaises(ValueError):
            inspect_file(path)

    def test_rescanning_changed_content_requires_review(self):
        source = self.audio()
        scan(self.db, self.source)
        mark(self.db, 1, 'reviewed', 'music')
        scan(self.db, self.source)
        self.assertEqual(items(self.db)[0]['status'], 'reviewed')
        source.write_bytes(source.read_bytes() + b'changed')
        scan(self.db, self.source)
        self.assertEqual(items(self.db)[0]['status'], 'new')
        self.assertEqual(plan(items(self.db), self.root / 'sorted'), [])

    def test_cli_reports_corrupt_audio_without_a_traceback(self):
        import subprocess
        import sys
        source = self.source / 'broken.wav'
        source.write_bytes(b'broken-audio-header')
        result = subprocess.run([sys.executable, '-m', 'mediaqueue', '--db',
                                 str(self.root / 'cli.sqlite3'), 'inspect', str(source)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('Traceback', result.stderr)
