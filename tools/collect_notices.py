"""Collect dependency notices without serializing malformed package metadata."""
from importlib.metadata import distributions
from pathlib import Path
import hashlib
import json
import re
import shutil


def collect(items=None, output='THIRD_PARTY_NOTICES'):
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    copied = 0
    for number, dist in enumerate(distributions() if items is None else items):
        name = str(dist.metadata.get('Name') or 'unknown')
        version = str(dist.version or 'unknown')
        safe = re.sub(r'[^A-Za-z0-9_.-]', '_', name)[:70] or 'unknown'
        target = out / f'{number:04d}-{safe}'
        target.mkdir(parents=True, exist_ok=True)
        # Do not call str(dist.metadata): some packages contain malformed headers.
        (target / 'PACKAGE.json').write_text(
            json.dumps({'name': name, 'version': version}, ensure_ascii=False, indent=2),
            encoding='utf-8')
        for entry in dist.files or []:
            relative = str(entry)
            if not any(word in relative.lower() for word in ('license', 'copying', 'notice')):
                continue
            source = Path(dist.locate_file(entry))
            if not source.is_file():
                raise FileNotFoundError(f'Listed notice file is missing: {source}')
            digest = hashlib.sha256(relative.encode('utf-8')).hexdigest()[:16]
            # Short names avoid Windows path-length and filename-character failures.
            shutil.copyfile(source, target / f'notice-{digest}.txt')
            copied += 1
    print(f'Collected {copied} notice files. Commercial license review is still required.')


if __name__ == '__main__':
    collect()
