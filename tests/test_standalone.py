import hashlib,json,os,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from jupitar.core import Store,Brain
from jupitar.runtime import NativeEngine,MODEL_FILE,PROJECTOR_FILE,NoRedirect
from jupitar.components import is_ready,sha256,install_components,Cancelled

class StandaloneTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=Store(self.tmp.name);self.engine=NativeEngine(self.store)
    def tearDown(self):self.engine.stop();self.tmp.cleanup()
    def test_missing_engine(self):
        with self.assertRaises(RuntimeError):self.engine.command(1234)
    def test_safe_native_command(self):
        root=Path(self.tmp.name)/'bundle';(root/'engine').mkdir(parents=True);(root/'engine'/'llama-server.exe').write_bytes(b'MZ')
        self.engine.model_folder.mkdir(parents=True)
        for name in (MODEL_FILE,PROJECTOR_FILE):(self.engine.model_folder/name).write_bytes(b'GGUFtest')
        with patch('jupitar.runtime.bundle_root',return_value=root):command=self.engine.command(12345)
        self.assertEqual(command[command.index('--host')+1],'127.0.0.1')
        self.assertIn('--no-webui',command);self.assertNotIn('--agent',command);self.assertNotIn('--api-key',command)
    def test_invalid_gguf(self):
        root=Path(self.tmp.name)/'bundle';(root/'engine').mkdir(parents=True);(root/'engine'/'llama-server.exe').write_bytes(b'MZ')
        self.engine.model_folder.mkdir(parents=True);(self.engine.model_folder/MODEL_FILE).write_bytes(b'bad!')
        with patch('jupitar.runtime.bundle_root',return_value=root):
            with self.assertRaises(ValueError):self.engine.command(1234)
    def test_strip_inherited_agent(self):
        with patch.dict(os.environ,{'LLAMA_ARG_AGENT':'1','LLAMA_ARG_HOST':'0.0.0.0','HF_TOKEN':'secret'}):env=self.engine.environment()
        self.assertNotIn('LLAMA_ARG_AGENT',env);self.assertNotIn('HF_TOKEN',env);self.assertEqual(env['LLAMA_API_KEY'],self.engine.key)
    def test_unique_tokens(self):
        other=NativeEngine(self.store);self.assertNotEqual(other.key,self.engine.key);other.stop()
    def test_block_endpoint(self):
        with self.assertRaises(ValueError):self.engine._request('/exec')
    def test_no_redirect(self):
        with self.assertRaises(ValueError):NoRedirect().redirect_request(None,None,None,None,None,None)
    def test_hash(self):
        p=Path(self.tmp.name)/'test';p.write_bytes(b'abc');self.assertEqual(sha256(p),hashlib.sha256(b'abc').hexdigest())
    def test_cancel_hash(self):
        p=Path(self.tmp.name)/'test';p.write_bytes(b'abc');event=threading.Event();event.set()
        with self.assertRaises(Cancelled):sha256(p,event)
    def test_not_ready(self):self.assertFalse(is_ready(self.store))
    def test_malformed_marker(self):
        p=self.store.folder/'models';p.mkdir();(p/'verified.json').write_text('{bad');self.assertFalse(is_ready(self.store))
    def fake_hub(self,bad_hash=False):
        def model_info(repo,revision=None,files_metadata=True):
            names=(MODEL_FILE,PROJECTOR_FILE) if 'GGUF' in repo else ('config.json','model.bin','tokenizer.json','vocabulary.txt')
            siblings=[]
            for name in names:
                data=b'GGUFtest' if name.endswith('.gguf') else b'test'
                digest=hashlib.sha256(data).hexdigest()
                siblings.append(SimpleNamespace(rfilename=name,lfs={'sha256':'0'*64 if bad_hash else digest}))
            return SimpleNamespace(sha='a'*40,siblings=siblings)
        def download(repo_id,filename,revision,local_dir):
            p=Path(local_dir)/filename;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(b'GGUFtest' if filename.endswith('.gguf') else b'test');return str(p)
        return SimpleNamespace(HfApi=lambda:SimpleNamespace(model_info=model_info),hf_hub_download=download)
    def test_mock_install_and_ready(self):
        with patch.dict('sys.modules',{'huggingface_hub':self.fake_hub()}),patch('shutil.disk_usage',return_value=SimpleNamespace(free=20*1024**3)):
            manifest=install_components(self.store,lambda text:None)
        self.assertTrue(is_ready(self.store));self.assertEqual(len(manifest['files']),6)
        (self.store.folder/'models'/'brain'/MODEL_FILE).write_bytes(b'changed size')
        self.assertFalse(is_ready(self.store))
    def test_checksum_failure_not_activated(self):
        with patch.dict('sys.modules',{'huggingface_hub':self.fake_hub(True)}),patch('shutil.disk_usage',return_value=SimpleNamespace(free=20*1024**3)):
            with self.assertRaises(ValueError):install_components(self.store,lambda text:None)
        self.assertFalse(is_ready(self.store))
    def test_insufficient_space(self):
        with patch.dict('sys.modules',{'huggingface_hub':self.fake_hub()}),patch('shutil.disk_usage',return_value=SimpleNamespace(free=1)):
            with self.assertRaises(RuntimeError):install_components(self.store,lambda text:None)
    def test_no_old_service_request(self):
        b=Brain(self.store)
        try:
            self.assertEqual(b.request('tags'),{'models':[]})
            with self.assertRaises(ValueError):b.request('arbitrary')
        finally:b.engine.stop()
    def test_request_auth_loopback(self):
        import http.server
        seen={};token=self.engine.key
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                seen['auth']=self.headers.get('Authorization');seen['path']=self.path
                self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"data":[]}')
            def log_message(self,*a):pass
        server=http.server.HTTPServer(('127.0.0.1',0),Handler)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            self.engine.port=server.server_port;self.assertEqual(self.engine._request('/v1/models'),{'data':[]})
            self.assertEqual(seen['auth'],'Bearer '+token);self.assertEqual(seen['path'],'/v1/models')
        finally:server.shutdown();server.server_close();worker.join()
