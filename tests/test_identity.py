import unittest,tempfile,json
from jupitar.core import Store,Brain,Actions,validate_identity,match_wake,NoRedirect
class IdentityTests(unittest.TestCase):
    def test_full_default(self):
        with tempfile.TemporaryDirectory() as d:
            s=Store(d); self.assertEqual(s.data['settings']['model'],'gemma3:4b'); self.assertEqual(s.data['settings']['assistant_name'],'JUPITAR')
    def test_identity(self): self.assertEqual(validate_identity(' Nova ',' hey nova '),('Nova','hey nova'))
    def test_bad_identity(self):
        for name,wake in [('', 'hey x'),('x'*33,'hey x'),('Nova','x'),('Nova','hey\nnova')]:
            with self.assertRaises(ValueError): validate_identity(name,wake)
    def test_default_wake(self): self.assertIsNotNone(match_wake('Hey Jupiter open calculator','hey jupitar'))
    def test_custom_wake(self): self.assertIsNotNone(match_wake('Hey Nova tell a joke','hey nova'))
    def test_no_substring(self): self.assertIsNone(match_wake('supernova','nova'))
    def test_regex_literal(self): self.assertIsNone(match_wake('anything','.*'))
    def test_hindi(self): self.assertIsNotNone(match_wake('जुपिटर नमस्ते','hey jupitar'))
    def test_gujarati(self): self.assertIsNotNone(match_wake('જ્યુપિટર નમસ્તે','hey jupitar'))
    def test_rename_preserves_memory(self):
        with tempfile.TemporaryDirectory() as d:
            s=Store(d);s.add('memories','Gujarati');s.setting('assistant_name','Nova')
            self.assertEqual(Store(d).data['memories'],['Gujarati'])
    def test_no_payment_tool(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): Actions(Store(d),lambda *a:True).run('purchase',{})
    def test_redirect_blocked(self):
        with self.assertRaises(ValueError): NoRedirect().redirect_request(None,None,None,None,None,None)
    def test_prompt_custom_name(self):
        with tempfile.TemporaryDirectory() as d:
            s=Store(d);s.setting('assistant_name','Nova');b=Brain(s);seen=[]
            def fake(endpoint,payload=None):
                if endpoint=='tags':return {'models':[{'name':'gemma3:4b'}]}
                seen.append(payload);return {'message':{'content':json.dumps({'reply':'Hello'})}}
            b.request=fake;self.assertEqual(b.ask('hello')['reply'],'Hello');self.assertIn('Nova',seen[0]['messages'][0]['content'])
    def test_plan_returned_not_executed(self):
        with tempfile.TemporaryDirectory() as d:
            b=Brain(Store(d))
            b.request=lambda endpoint,payload=None: {'models':[{'name':'gemma3:4b'}]} if endpoint=='tags' else {'message':{'content':'{"plan":[{"action":"open_app","args":{"name":"calculator"}}]}'}}
            self.assertIn('plan',b.ask('do two things'))
