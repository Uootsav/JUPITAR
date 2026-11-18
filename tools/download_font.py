from pathlib import Path
import urllib.request
ROOT=Path(__file__).resolve().parent.parent/'assets'
ROOT.mkdir(exist_ok=True)
BASE='https://raw.githubusercontent.com/google/fonts/main/ofl/rajdhani/'
for remote,local in [('OFL.txt','Rajdhani-OFL.txt'),('Rajdhani-SemiBold.ttf','Rajdhani-SemiBold.ttf')]:
    with urllib.request.urlopen(BASE+remote,timeout=40) as r: data=r.read(2_000_000)
    if remote.endswith('.ttf') and data[:4] not in (b'\x00\x01\x00\x00',b'OTTO'): raise ValueError('Unexpected font response.')
    (ROOT/local).write_bytes(data)
print('Font and original license saved. Restart JUPITAR or rebuild.')
