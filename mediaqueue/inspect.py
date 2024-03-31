from pathlib import Path
import struct
import wave


def inspect_file(path):
    path = Path(path)
    result = {'name': path.name, 'bytes': path.stat().st_size}
    if path.suffix.lower() == '.wav':
        with wave.open(str(path), 'rb') as audio:
            result.update(channels=audio.getnchannels(), sample_rate=audio.getframerate(),
                          seconds=audio.getnframes() / audio.getframerate())
    elif path.suffix.lower() == '.png':
        with path.open('rb') as stream:
            header = stream.read(24)
        if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
            raise ValueError('Invalid PNG header')
        result['width'], result['height'] = struct.unpack('>II', header[16:24])
    return result
