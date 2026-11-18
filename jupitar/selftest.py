import json,subprocess
from pathlib import Path
from .runtime import bundle_root

def run(destination):
    result={'gui':False,'engine':False,'imports':False}
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QEventLoop,QTimer,QUrl
        from PySide6.QtWebEngineWidgets import QWebEngineView
        app=QApplication.instance() or QApplication([]);view=QWebEngineView();loop=QEventLoop()
        def loaded(ok):result['gui']=bool(ok);loop.quit()
        view.loadFinished.connect(loaded);view.setUrl(QUrl.fromLocalFile(str(bundle_root()/'ui'/'index.html')))
        QTimer.singleShot(20000,loop.quit);loop.exec();view.close()
        import sounddevice,faster_whisper,PIL,psutil,docx,openpyxl,pypdf,huggingface_hub
        result['imports']=True
        engine=bundle_root()/'engine'/'llama-server.exe'
        p=subprocess.run([str(engine),'--version'],capture_output=True,timeout=45,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        result['engine']=p.returncode==0;result['engine_version']=(p.stdout+p.stderr).decode('utf-8',errors='replace')[:2000]
    except Exception as e:result['error']=str(e)
    Path(destination).write_text(json.dumps(result,indent=2),encoding='utf-8')
    return 0 if all(result[k] for k in ('gui','engine','imports')) else 1
