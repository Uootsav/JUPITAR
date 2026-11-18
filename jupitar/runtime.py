"""Own the bundled native engine. No separately installed AI service is used."""
import atexit, json, os, secrets, socket, subprocess, sys, threading, time
import urllib.request, urllib.error
from pathlib import Path

MODEL_FILE='gemma-3-4b-it-Q4_K_M.gguf'
PROJECTOR_FILE='mmproj-model-f16.gguf'

def bundle_root():
    return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent.parent))

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise ValueError('Local inference redirects are forbidden.')

class NativeEngine:
    def __init__(self,store):
        self.store=store; self.process=None; self.port=None; self.key=secrets.token_urlsafe(32)
        self.lock=threading.RLock(); self.stopped=False; self.log=None; self.job=None
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
        atexit.register(self.stop)
    @property
    def model_folder(self): return self.store.folder/'models'/'brain'
    def command(self,port):
        executable=bundle_root()/'engine'/'llama-server.exe'
        model=self.model_folder/MODEL_FILE
        projector=self.model_folder/PROJECTOR_FILE
        if not executable.is_file(): raise RuntimeError('Bundled AI engine missing. Use a successfully built JUPITAR installer, not the source ZIP.')
        for p in (model,projector):
            if not p.is_file(): raise RuntimeError('AI components missing. Open AI Setup and download them.')
            with p.open('rb') as f:
                if f.read(4)!=b'GGUF': raise ValueError('Invalid model file. Repair it through AI Setup.')
        return [str(executable),'-m',str(model),'--mmproj',str(projector),
                '--host','127.0.0.1','--port',str(port),'--ctx-size','4096',
                '--parallel','1','--threads',str(max(1,min(6,(os.cpu_count() or 4)-1))),
                '--n-gpu-layers','0','--no-webui']
    def environment(self):
        # Inherited llama settings must not enable tools, tunnels or remote downloads.
        env={k:v for k,v in os.environ.items() if not k.startswith(('LLAMA_','HF_','HUGGINGFACE_'))}
        env['LLAMA_API_KEY']=self.key
        env['HF_HUB_OFFLINE']='1'; env['HF_HUB_DISABLE_TELEMETRY']='1'
        return env
    def _attach_job(self):
        # Windows closes the engine if the app exits/crashes. Refuse startup if ownership cannot be enforced.
        if os.name!='nt': return
        import ctypes
        from ctypes import wintypes
        class BASIC(ctypes.Structure):
            _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),
                ('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),
                ('ActiveProcessLimit',wintypes.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]
        class IO(ctypes.Structure):
            _fields_=[(n,ctypes.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
        class EXT(ctypes.Structure):
            _fields_=[('BasicLimitInformation',BASIC),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.CreateJobObjectW.restype=wintypes.HANDLE
        kernel.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR]
        kernel.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD]
        kernel.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE]
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        job=kernel.CreateJobObjectW(None,None)
        if not job: raise ctypes.WinError(ctypes.get_last_error())
        info=EXT(); info.BasicLimitInformation.LimitFlags=0x2000
        if not kernel.SetInformationJobObject(job,9,ctypes.byref(info),ctypes.sizeof(info)) or not kernel.AssignProcessToJobObject(job,int(self.process._handle)):
            error=ctypes.get_last_error();kernel.CloseHandle(job);raise ctypes.WinError(error)
        self.job=(kernel,job)
    def start(self):
        with self.lock:
            if self.stopped: raise RuntimeError('JUPITAR is closing.')
            if self.process and self.process.poll() is None: return
            if self.process: self._cleanup()
            with socket.socket() as s: s.bind(('127.0.0.1',0)); self.port=s.getsockname()[1]
            command=self.command(self.port)
            self.log=None
            try:
                self.process=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                    cwd=str(bundle_root()/'engine'),env=self.environment(),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                self._attach_job()
                deadline=time.monotonic()+240
                while time.monotonic()<deadline:
                    if self.stopped: raise RuntimeError('Engine startup cancelled.')
                    if self.process.poll() is not None: raise RuntimeError('Bundled engine exited. Verify the build, available RAM and downloaded components.')
                    try:
                        self._request('/v1/models',timeout=2); return
                    except (urllib.error.URLError,TimeoutError,OSError): time.sleep(0.3)
                raise TimeoutError('Local engine took too long to load. Check available RAM and downloaded components.')
            except Exception:
                self._cleanup(); raise
    def _request(self,path,payload=None,timeout=240):
        if path not in ('/v1/models','/v1/chat/completions'): raise ValueError('Endpoint not allowed.')
        body=None if payload is None else json.dumps(payload,ensure_ascii=False).encode('utf-8')
        req=urllib.request.Request(f'http://127.0.0.1:{self.port}'+path,data=body,
            headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'})
        with self.opener.open(req,timeout=timeout) as r: return json.load(r)
    def chat(self,messages,json_output=True):
        self.start()
        payload={'model':'local','messages':messages,'stream':False,'max_tokens':512,'temperature':0.65}
        if json_output: payload['response_format']={'type':'json_object'}
        with self.lock:
            if self.stopped: raise RuntimeError('App closing.')
            return self._request('/v1/chat/completions',payload)['choices'][0]['message']['content']
    def _cleanup(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try: self.process.wait(timeout=5)
            except subprocess.TimeoutExpired: self.process.kill();self.process.wait(timeout=5)
        self.process=None
        if self.job:
            kernel,job=self.job;kernel.CloseHandle(job);self.job=None
        if self.log: self.log.close();self.log=None
    def stop(self):
        self.stopped=True
        # Terminate before taking the lock: an inference call may be holding it.
        if self.process and self.process.poll() is None:
            try: self.process.terminate()
            except OSError: pass
        with self.lock: self._cleanup()
