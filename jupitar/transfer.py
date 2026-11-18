"""Measured, resumable HTTPS model transfers for the premium setup UI."""
import hashlib,json,os,re,shutil,threading,time,urllib.request
from collections import deque
from pathlib import Path
from .components import BRAIN_REPO,BRAIN_REVISION,VOICE_REPO,VOICE_FILES,Cancelled,sha256
from .runtime import MODEL_FILE,PROJECTOR_FILE

class SecureRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not newurl.lower().startswith('https://'):raise ValueError('Insecure download redirect blocked.')
        return super().redirect_request(req,fp,code,msg,headers,newurl)

class RateMeter:
    def __init__(self,clock=time.monotonic):self.clock=clock;self.start=clock();self.bytes=0;self.samples=deque([(self.start,0)])
    def add(self,count):
        self.bytes+=count;now=self.clock();self.samples.append((now,self.bytes))
        while len(self.samples)>2 and now-self.samples[0][0]>8:self.samples.popleft()
    def speed(self):
        elapsed=self.clock()-self.samples[0][0]
        return (self.bytes-self.samples[0][1])/elapsed if elapsed>=.75 else 0.0
    def eta(self,remaining):
        speed=self.speed();return max(0,remaining)/speed if speed>0 else None

def stream_file(url,target,size,notify,cancel,opener=None):
    """Resume only on an exact matching Content-Range; otherwise restart safely."""
    if not url.startswith('https://'):raise ValueError('HTTPS downloads only.')
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    part=target.with_name(target.name+'.part');offset=part.stat().st_size if part.exists() else 0
    if offset>size:part.unlink();offset=0
    if offset==size and part.exists():return part
    headers={'User-Agent':'JUPITAR/0.4','Accept-Encoding':'identity'}
    if offset:headers['Range']=f'bytes={offset}-'
    opener=opener or urllib.request.build_opener(SecureRedirect())
    req=urllib.request.Request(url,headers=headers)
    with opener.open(req,timeout=30) as response:
        code=getattr(response,'status',200)
        if code==206:
            match=re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)',response.headers.get('Content-Range',''))
            if not match or int(match[1])!=offset or int(match[3])!=size:raise ValueError('Invalid resumed response; retry without modifying partial data.')
        elif code==200:offset=0
        else:raise ValueError('Unexpected download response: '+str(code))
        mode='ab' if code==206 and offset else 'wb'
        with part.open(mode) as f:
            notify(offset,0)
            while True:
                if cancel.is_set():raise Cancelled('Paused. Resume reuses verified files and partial data.')
                block=response.read(256*1024)
                if not block:break
                if offset+len(block)>size:raise ValueError('Download exceeds expected file size.')
                f.write(block);offset+=len(block);notify(offset,len(block))
    if offset!=size:raise ValueError('Connection ended early. Resume to continue the partial file.')
    return part

def verify(path,size,digest=None,git_blob=None,cancel=None):
    path=Path(path)
    if path.stat().st_size!=size:raise ValueError('Component size mismatch.')
    value=sha256(path,cancel)
    if digest and value!=digest:raise ValueError('Component SHA-256 mismatch.')
    if git_blob:
        h=hashlib.sha1();h.update(f'blob {size}\0'.encode())
        with path.open('rb') as f:
            while True:
                if cancel and cancel.is_set():raise Cancelled('Verification paused.')
                data=f.read(1024*1024)
                if not data:break
                h.update(data)
        if h.hexdigest()!=git_blob:raise ValueError('Component Git object hash mismatch.')
    return value

def install(store,emit,cancel=None):
    os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    from huggingface_hub import HfApi,hf_hub_url
    cancel=cancel or threading.Event();base=store.folder/'models';base.mkdir(exist_ok=True)
    emit({'stage':'Reading metadata','done':0,'total':None,'speed':0,'eta':None,'file':'Resolving exact component revisions','running':True})
    api=HfApi();plan=[];revisions={}
    for repo,revision,folder,names in [(BRAIN_REPO,BRAIN_REVISION,'brain',(MODEL_FILE,PROJECTOR_FILE)),(VOICE_REPO,None,'whisper-small',VOICE_FILES)]:
        if cancel.is_set():raise Cancelled('Paused before metadata lookup.')
        info=api.model_info(repo,revision=revision,files_metadata=True)
        if not re.fullmatch('[0-9a-f]{40}',info.sha or ''):raise ValueError('Expected a fixed model revision.')
        revisions[repo]=info.sha;meta={x.rfilename:x for x in info.siblings}
        for name in names:
            if name not in meta:
                if name in ('preprocessor_config.json','vocabulary.txt'):continue
                raise ValueError('Required component missing upstream: '+name)
            m=meta[name];size=getattr(m,'size',None);lfs=getattr(m,'lfs',None)
            digest=(lfs.get('sha256') if isinstance(lfs,dict) else getattr(lfs,'sha256',None)) if lfs else None
            blob=getattr(m,'blob_id',None) if not lfs else None
            if not isinstance(size,int) or size<=0:raise ValueError('Missing component size: '+name)
            if lfs and not re.fullmatch('[0-9a-f]{64}',digest or ''):raise ValueError('Missing model checksum.')
            if not lfs and not re.fullmatch('[0-9a-f]{40}',blob or ''):raise ValueError('Missing component object hash.')
            plan.append({'rel':folder+'/'+name,'size':size,'digest':digest,'blob':blob,'url':hf_hub_url(repo_id=repo,filename=name,revision=info.sha)})
    total=sum(x['size'] for x in plan);needed=0
    for x in plan:
        target=base/x['rel'];part=target.with_name(target.name+'.part')
        cached=x['size'] if target.exists() and target.stat().st_size==x['size'] else part.stat().st_size if part.exists() else 0
        needed+=max(0,x['size']-min(cached,x['size']))
    if shutil.disk_usage(base).free<needed+512*1024**2:raise RuntimeError('Not enough free disk space for remaining components plus 512 MiB reserve.')
    (base/'verified.json').unlink(missing_ok=True)
    manifest={'schema':1,'files':{},'revisions':revisions};done=0;meter=RateMeter();last=[0.0]
    for x in plan:
        if cancel.is_set():raise Cancelled('Paused before next component.')
        target=base/x['rel'];current=[0]
        def report(offset,added):
            current[0]=offset;meter.add(added);now=time.monotonic()
            if now-last[0]>.15 or offset==x['size']:
                last[0]=now;emit({'stage':'Downloading','file':x['rel'],'done':done+offset,'total':total,'speed':meter.speed(),'eta':meter.eta(total-done-offset),'running':True})
        path=target
        if not target.exists() or target.stat().st_size!=x['size']:
            path=stream_file(x['url'],target,x['size'],report,cancel)
        emit({'stage':'Verifying','file':x['rel'],'done':done+x['size'],'total':total,'speed':0,'eta':None,'running':True})
        try:value=verify(path,x['size'],x['digest'],x['blob'],cancel)
        except Cancelled:raise
        except ValueError:
            path.unlink(missing_ok=True);raise ValueError('Verification failed; damaged file removed. Resume to download it again.')
        if path!=target:os.replace(path,target)
        manifest['files'][x['rel']]={'size':x['size'],'sha256':value};done+=x['size']
    if cancel.is_set():raise Cancelled('Paused before activation.')
    marker=base/'verified.json';tmp=marker.with_suffix('.tmp');tmp.write_text(json.dumps(manifest,indent=2),encoding='utf-8');os.replace(tmp,marker)
    emit({'stage':'Ready','file':'All components verified','done':total,'total':total,'speed':0,'eta':0,'running':False})
    return manifest
