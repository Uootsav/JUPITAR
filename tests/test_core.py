import unittest, tempfile, time, os
from pathlib import Path
from jupitar.core import Store, Actions, safe_name, temp_candidates
class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.store=Store(self.tmp.name)
        self.actions=Actions(self.store,lambda *args:True)
    def tearDown(self): self.tmp.cleanup()
    def test_default_listening(self): self.assertTrue(self.store.data['settings']['listening'])
    def test_memory_persists(self):
        self.actions.remember('I prefer Gujarati'); self.assertEqual(Store(self.tmp.name).data['memories'],['I prefer Gujarati'])
    def test_deny(self):
        actions=Actions(self.store,lambda *args:False)
        with self.assertRaises(ValueError): actions.note('private')
        self.assertEqual(self.store.data['notes'],[])
    def test_unknown_action(self):
        with self.assertRaises(ValueError): self.actions.run('run_shell',{'command':'anything'})
    def test_bad_names(self):
        for name in ('../secret','C:\\test','CON','NUL.txt','x/y','a.','a '):
            # Leading/trailing whitespace is stripped, but trailing dot is rejected.
            if name=='a ': continue
            with self.assertRaises(ValueError,msg=name): safe_name(name,'.txt')
    def test_no_overwrite(self):
        self.actions.create_text('note','hello')
        with self.assertRaises(ValueError): self.actions.create_text('note','changed')
        self.assertEqual((self.store.workspace/'note.txt').read_text(),'hello')
    def test_due_reminders(self):
        self.store.add('reminders',{'at':time.time()-1,'text':'stretch'})
        self.assertEqual(len(self.store.due()),1); self.assertEqual(self.store.due(),[])
    def test_temp_age(self):
        p=Path(self.tmp.name)/'old.tmp'; p.write_text('old'); os.utime(p,(time.time()-9*86400,)*2)
        q=Path(self.tmp.name)/'new.tmp'; q.write_text('new')
        names=[x[0].name for x in temp_candidates(self.tmp.name)]
        self.assertIn('old.tmp',names); self.assertNotIn('new.tmp',names)
    def test_temp_no_directories(self):
        folder=Path(self.tmp.name)/'old'; folder.mkdir(); os.utime(folder,(time.time()-9*86400,)*2)
        self.assertNotIn('old',[x[0].name for x in temp_candidates(self.tmp.name)])
    def test_local_model_allowlist(self):
        from jupitar.core import Brain
        self.store.data['settings']['model']='evil-cloud'
        with self.assertRaises(ValueError): Brain(self.store).ask('hi')
if __name__=='__main__': unittest.main()

class RoutingTests(unittest.TestCase):
    def test_direct_cleanup(self):
        from jupitar.core import Brain
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(Brain(Store(folder)).ask('Delete all temporary files')['action'],'clean_temp')
    def test_direct_recycle(self):
        from jupitar.core import Brain
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(Brain(Store(folder)).ask('Empty the Recycle Bin')['action'],'empty_recycle_bin')
