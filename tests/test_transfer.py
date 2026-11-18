import hashlib,io,json,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from jupitar.transfer import RateMeter,stream_file,verify,SecureRedirect,install
from jupitar.components import Cancelled,is_ready
from jupitar.core import Store
from jupitar.runtime import MODEL_FILE,PROJECTOR_FILE

class Response(io.BytesIO):
 def __init__(self,data,status=200,headers=None):super().__init__(data);self.status=status;self.headers=headers or {}
class Opener:
 def __init__(self,data,status=200,headers=None):self.data=data;self.status=status;self.headers=headers;self.request=None
 def open(self,req,timeout=30):self.request=req;return Response(self.data,self.status,self.headers)
class TransferTests(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'model';self.cancel=threading.Event()
 def tearDown(self):self.temp.cleanup()
 def test_rate_warmup(self):
  t=[0.0];m=RateMeter(lambda:t[0]);m.add(100);self.assertIsNone(m.eta(100))
 def test_rate_eta(self):
  t=[0.0];m=RateMeter(lambda:t[0]);t[0]=2;m.add(1000);self.assertEqual(m.speed(),500);self.assertEqual(m.eta(2000),4)
 def test_fresh_transfer(self):
  events=[];p=stream_file('https://example.test/a',self.path,6,lambda n,b:events.append((n,b)),self.cancel,Opener(b'abcdef'))
  self.assertEqual(p.read_bytes(),b'abcdef');self.assertEqual(events[-1],(6,6))
 def test_resume(self):
  self.path.with_name('model.part').write_bytes(b'abc');opener=Opener(b'def',206,{'Content-Range':'bytes 3-5/6'})
  p=stream_file('https://example.test/a',self.path,6,lambda *a:None,self.cancel,opener)
  self.assertEqual(p.read_bytes(),b'abcdef');self.assertEqual(opener.request.get_header('Range'),'bytes=3-')
 def test_server_ignores_range(self):
  self.path.with_name('model.part').write_bytes(b'abc')
  p=stream_file('https://example.test/a',self.path,6,lambda *a:None,self.cancel,Opener(b'abcdef'))
  self.assertEqual(p.read_bytes(),b'abcdef')
 def test_bad_range(self):
  self.path.with_name('model.part').write_bytes(b'abc')
  with self.assertRaises(ValueError):stream_file('https://example.test/a',self.path,6,lambda *a:None,self.cancel,Opener(b'def',206,{'Content-Range':'bytes 0-2/6'}))
  self.assertEqual(self.path.with_name('model.part').read_bytes(),b'abc')
 def test_truncated(self):
  with self.assertRaises(ValueError):stream_file('https://example.test/a',self.path,6,lambda *a:None,self.cancel,Opener(b'abc'))
  self.assertEqual(self.path.with_name('model.part').read_bytes(),b'abc')
 def test_oversize(self):
  with self.assertRaises(ValueError):stream_file('https://example.test/a',self.path,2,lambda *a:None,self.cancel,Opener(b'abc'))
 def test_pause(self):
  self.cancel.set()
  with self.assertRaises(Cancelled):stream_file('https://example.test/a',self.path,6,lambda *a:None,self.cancel,Opener(b'abcdef'))
 def test_https_only(self):
  with self.assertRaises(ValueError):stream_file('http://example.test/a',self.path,6,lambda *a:None,self.cancel)
 def test_no_downgrade(self):
  with self.assertRaises(ValueError):SecureRedirect().redirect_request(None,None,None,None,None,'http://example.test/a')
 def test_checksum(self):
  self.path.write_bytes(b'abc');self.assertEqual(verify(self.path,3,hashlib.sha256(b'abc').hexdigest()),hashlib.sha256(b'abc').hexdigest())
 def test_bad_checksum(self):
  self.path.write_bytes(b'abc')
  with self.assertRaises(ValueError):verify(self.path,3,'0'*64)
 def test_git_blob(self):
  self.path.write_bytes(b'abc');verify(self.path,3,git_blob=hashlib.sha1(b'blob 3\0abc').hexdigest())
 def test_bad_blob(self):
  self.path.write_bytes(b'abc')
  with self.assertRaises(ValueError):verify(self.path,3,git_blob='0'*40)
 def test_full_mock_install(self):
  def metadata(repo,revision=None,files_metadata=True):
   names=(MODEL_FILE,PROJECTOR_FILE) if 'GGUF' in repo else ('model.bin','config.json','tokenizer.json','vocabulary.txt')
   return SimpleNamespace(sha='a'*40,siblings=[SimpleNamespace(rfilename=n,size=6,lfs={'sha256':hashlib.sha256(b'abcdef').hexdigest()},blob_id=None) for n in names])
  fake=SimpleNamespace(HfApi=lambda:SimpleNamespace(model_info=metadata),hf_hub_url=lambda **k:'https://example.test/'+k['filename'])
  def transfer(url,target,size,notify,cancel):
   p=Path(str(target)+'.part');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'abcdef');notify(6,6);return p
  events=[];store=Store(self.temp.name)
  with patch.dict('sys.modules',{'huggingface_hub':fake}),patch('jupitar.transfer.stream_file',side_effect=transfer),patch('shutil.disk_usage',return_value=SimpleNamespace(free=10**10)):
   install(store,events.append,self.cancel)
  self.assertTrue(is_ready(store));self.assertEqual(events[-1]['stage'],'Ready');self.assertEqual(events[-1]['done'],events[-1]['total']);self.assertFalse(events[-1]['running'])
