from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,os
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent.parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
results={}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE'),headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1400,'height':950},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(base+'/ui/index.html');page.wait_for_timeout(1200)
 assert page.locator('#connection').inner_text()=='INTERFACE PREVIEW'
 assert page.locator('canvas').evaluate('(c)=>c.width>0')
 page.screenshot(path=str(root/'site/assets/command-center.png'),full_page=True)
 page.locator('[data-modal="setup"]').click()
 assert page.locator('#setup').is_visible()
 page.evaluate("receive({type:'progress',data:{stage:'Downloading',done:640000000,total:1000000000,speed:12400000,eta:29,file:'UI TEST FIXTURE — not a live download',running:true}})")
 assert page.locator('#downloadPercent').inner_text()=='64%'
 assert page.locator('#downloadEta').inner_text()=='29 sec'
 page.screenshot(path=str(root/'previews/download-panel.png'))
 page.keyboard.press('Escape');assert not page.locator('#setup').is_visible()
 page.locator('[data-modal="settings"]').click();assert page.locator('#settings').is_visible();page.keyboard.press('Escape')
 page.fill('#prompt','hello');page.locator('#send').click();assert 'no desktop access' in page.locator('#chat').inner_text()
 results['frontend_errors']=errors;results['hud_controls']='setup/settings/escape/send/progress passed'
 page.route('https://api.github.com/**',lambda route:route.fulfill(status=200,content_type='application/json',body='[]'))
 page.goto(base+'/site/index.html');page.wait_for_timeout(1000)
 assert page.locator('#downloadButton').inner_text()=='Installer not published yet'
 assert page.locator('img').evaluate('(i)=>i.complete&&i.naturalWidth>0')
 page.screenshot(path=str(root/'previews/website-preview.png'),full_page=True)
 page.screenshot(path=str(root/'previews/website-hero.png'))
 results['website_empty_release']='passed'
 page.unroute('https://api.github.com/**')
 fixture=[{'draft':False,'prerelease':True,'tag_name':'TEST-FIXTURE','html_url':'https://github.com/Uootsav/JUPITAR/releases/tag/test','assets':[{'name':'JUPITAR-Setup-test.exe','state':'uploaded','size':100000000,'browser_download_url':'https://github.com/Uootsav/JUPITAR/releases/download/test/JUPITAR-Setup-test.exe'}]}]
 page.route('https://api.github.com/**',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps(fixture)))
 page.reload();page.wait_for_timeout(500)
 assert page.locator('#downloadButton').inner_text()=='Download for Windows ↗'
 assert 'TEST-FIXTURE' in page.locator('#releaseStatus').inner_text();results['website_release_fixture']='passed'
 page.unroute('https://api.github.com/**');page.route('https://api.github.com/**',lambda route:route.fulfill(status=403,body='rate limit'))
 page.reload();page.wait_for_timeout(500);assert page.locator('#downloadButton').inner_text()=='Check available releases';results['website_api_failure']='passed'
 page.set_viewport_size({'width':390,'height':844});page.goto(base+'/site/index.html');page.wait_for_timeout(500)
 assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),page.evaluate('document.documentElement.scrollWidth')
 page.screenshot(path=str(root/'previews/website-mobile.png'),full_page=True);results['website_mobile_no_overflow']='passed'
 page.goto(base+'/ui/index.html');page.wait_for_timeout(500);assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth');results['hud_mobile_no_overflow']='passed'
 browser.close()
server.shutdown();(root/'BROWSER_TESTS.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
