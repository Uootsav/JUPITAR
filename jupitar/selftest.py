import json,subprocess
from pathlib import Path
from .runtime import bundle_root

def run(destination):
    result={'gui':False,'engine':False,'imports':False}
    try:
        import tkinter as tk
        root=tk.Tk();root.withdraw();root.update();root.destroy();result['gui']=True
        import sounddevice,faster_whisper,PIL,psutil,docx,openpyxl,pypdf,huggingface_hub
        result['imports']=True
        engine=bundle_root()/'engine'/'llama-server.exe'
        p=subprocess.run([str(engine),'--version'],capture_output=True,timeout=45,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        result['engine']=p.returncode==0
        result['engine_version']=(p.stdout+p.stderr).decode('utf-8',errors='replace')[:2000]
    except Exception as e:result['error']=str(e)
    Path(destination).write_text(json.dumps(result,indent=2),encoding='utf-8')
    return 0 if all(result[k] for k in ('gui','engine','imports')) else 1
