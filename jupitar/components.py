"""Explicit first-launch downloads. No app code or engine binaries downloaded here."""
import hashlib, json, os, threading
from pathlib import Path
from .runtime import MODEL_FILE,PROJECTOR_FILE
BRAIN_REPO='ggml-org/gemma-3-4b-it-GGUF'
BRAIN_REVISION='d0976223747697cb51e056d85c532013931fe52e'
VOICE_REPO='Systran/faster-whisper-small'
VOICE_FILES=('config.json','model.bin','tokenizer.json','vocabulary.txt','preprocessor_config.json')

class Cancelled(Exception): pass

def sha256(path,cancel=None):
    digest=hashlib.sha256()
    with Path(path).open('rb') as f:
        while True:
            if cancel and cancel.is_set(): raise Cancelled('Download cancelled between verification chunks.')
            block=f.read(4*1024*1024)
            if not block: break
            digest.update(block)
    return digest.hexdigest()

def is_ready(store):
    marker=store.folder/'models'/'verified.json'
    try:
        manifest=json.loads(marker.read_text(encoding='utf-8'))
        if manifest.get('schema')!=1: return False
        expected={'brain/'+MODEL_FILE,'brain/'+PROJECTOR_FILE,'whisper-small/model.bin','whisper-small/config.json','whisper-small/tokenizer.json'}
        if not expected.issubset(manifest['files']): return False
        base=(store.folder/'models').resolve()
        for rel,info in manifest['files'].items():
            p=(base/rel).resolve()
            if not p.is_relative_to(base) or not p.is_file() or p.stat().st_size!=info['size']: return False
        return True
    except (OSError,ValueError,KeyError,TypeError): return False

def install_components(store,progress,cancel=None):
    # huggingface_hub handles interrupted-download cache and resumes when supported.
    os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    from huggingface_hub import HfApi,hf_hub_download
    cancel=cancel or threading.Event()
    base=store.folder/'models';base.mkdir(exist_ok=True)
    if __import__('shutil').disk_usage(base).free<6*1024**3:
        raise RuntimeError('At least 6 GiB free disk space is required for first-use components and temporary data.')
    (base/'verified.json').unlink(missing_ok=True)
    api=HfApi();manifest={'schema':1,'files':{},'revisions':{}}
    specs=[(BRAIN_REPO,BRAIN_REVISION,'brain',(MODEL_FILE,PROJECTOR_FILE)),(VOICE_REPO,None,'whisper-small',VOICE_FILES)]
    for repo,revision,folder,names in specs:
        if cancel.is_set(): raise Cancelled('Cancelled before next component.')
        progress('Reading component metadata: '+repo)
        info=api.model_info(repo,revision=revision,files_metadata=True)
        commit=info.sha
        if not commit or len(commit)!=40: raise ValueError('Expected a fixed model commit.')
        manifest['revisions'][repo]=commit
        metadata={x.rfilename:x for x in info.siblings}
        for name in names:
            if name not in metadata:
                if name in ('preprocessor_config.json','vocabulary.txt'): continue
                raise ValueError('Required component missing upstream: '+name)
            if cancel.is_set(): raise Cancelled('Cancelled before next file. Retry reuses downloaded data.')
            progress('Downloading '+folder+'/'+name+' (large files may take several minutes; retry reuses cache)')
            path=Path(hf_hub_download(repo_id=repo,filename=name,revision=commit,local_dir=str(base/folder)))
            progress('Verifying '+name)
            digest=sha256(path,cancel)
            lfs=getattr(metadata[name],'lfs',None)
            expected=(lfs.get('sha256') if isinstance(lfs,dict) else getattr(lfs,'sha256',None)) if lfs else None
            if lfs and not expected: raise ValueError('Missing upstream SHA-256 for model data.')
            if expected and digest!=expected:
                path.unlink(missing_ok=True);raise ValueError('Checksum mismatch. File removed; retry download.')
            manifest['files'][folder+'/'+name]={'size':path.stat().st_size,'sha256':digest}
    if cancel.is_set(): raise Cancelled('Cancelled before activation.')
    marker=base/'verified.json';temp=marker.with_suffix('.tmp')
    temp.write_text(json.dumps(manifest,indent=2),encoding='utf-8');os.replace(temp,marker)
    progress('Components verified. Local AI is ready.')
    return manifest
