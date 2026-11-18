from importlib.metadata import distributions
from pathlib import Path
import shutil
out=Path('THIRD_PARTY_NOTICES');out.mkdir(exist_ok=True)
for dist in distributions():
    name=dist.metadata.get('Name','unknown');target=out/name;target.mkdir(exist_ok=True)
    (target/'METADATA.txt').write_text(str(dist.metadata),encoding='utf-8')
    for f in dist.files or []:
        if any(x in str(f).lower() for x in ('license','copying','notice')):
            src=Path(dist.locate_file(f))
            if src.is_file():
                dest=target/str(f).replace('..','_').replace('\\','_').replace('/','_')
                shutil.copyfile(src,dest)
print('Collected installed distribution notices; this is not a complete legal audit.')
