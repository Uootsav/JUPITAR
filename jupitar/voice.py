"""Local microphone segmentation and offline Windows SAPI speech."""
import os, time, queue, threading, subprocess, re
from collections import deque
from .core import match_wake
from pathlib import Path

class Speaker:
    def __init__(self,store,events):
        self.store=store; self.events=events; self.process=None; self.lock=threading.Lock(); self.generation=0
    def stop(self):
        with self.lock:
            self.generation+=1
            if self.process and self.process.poll() is None: self.process.terminate()
    def speaking(self):
        return self.process is not None and self.process.poll() is None
    def say(self,text):
        if not self.store.data['settings']['speak']: return
        self.stop(); generation=self.generation
        threading.Thread(target=self._say,args=(str(text),generation),daemon=True).start()
    def _say(self,text,generation):
        import json
        # All user text is JSON on stdin, never interpolated into PowerShell source.
        script="$ErrorActionPreference='Stop'; Add-Type -AssemblyName System.Speech; $d=[Console]::In.ReadToEnd()|ConvertFrom-Json; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; if($d.voice){$s.SelectVoice($d.voice)}; $s.Speak([string]$d.text)"
        try:
            with self.lock:
                if generation!=self.generation: return
                self.process=subprocess.Popen(['powershell.exe','-NoProfile','-NonInteractive','-Command',script],
                    stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                proc=self.process
            _,err=proc.communicate(json.dumps({'text':text[:5000],'voice':self.store.data['settings']['voice_id']}).encode('utf-8'))
            if proc.returncode and generation==self.generation: self.events.put(('status','Speech unavailable. Choose an installed offline SAPI voice in Settings.'))
        except Exception as e: self.events.put(('status','Speech error: '+str(e)))

class Listener:
    def __init__(self,store,events,speaker):
        self.store=store; self.events=events; self.speaker=speaker; self.closed=threading.Event()
        self.enabled=threading.Event()
        if store.data['settings']['listening']: self.enabled.set()
        self.session_until=0; self.ready=False
    def toggle(self,on):
        if on: self.enabled.set()
        else: self.enabled.clear(); self.session_until=0
    def start(self): threading.Thread(target=self.run,daemon=True).start()
    def run(self):
        try:
            while not self.enabled.wait(0.25):
                if self.closed.is_set(): return
            if self.closed.is_set(): return
            import numpy as np
            import sounddevice as sd
            from faster_whisper import WhisperModel
            model_path=self.store.folder/'models'/'whisper-small'
            if not (model_path/'model.bin').exists():
                self.events.put(('status','Voice model missing. Run Download Models.cmd once; typed chat still works.')); return
            model=WhisperModel(str(model_path),device='cpu',compute_type='int8',cpu_threads=4,local_files_only=True)
            self.ready=True; self.events.put(('status','Voice ready. Use your configured wake phrase. Headphones recommended.'))
            while not self.closed.is_set():
                if not self.enabled.wait(0.25): continue
                # Close the microphone stream entirely when muted.
                with sd.InputStream(samplerate=16000,channels=1,dtype='float32',blocksize=1600) as stream:
                    chunks=[]; silent=0; active=False; interrupted=False; preroll=deque(maxlen=3)
                    while self.enabled.is_set() and not self.closed.is_set():
                        block,overflow=stream.read(1600)
                        energy=float(np.sqrt(np.mean(block*block)))
                        self.events.put(('level',min(1.0,energy*12)))
                        loud=energy>float(self.store.data['settings']['threshold'])
                        if loud:
                            if self.speaker.speaking() and not interrupted:
                                # Energy-based barge-in, not acoustic echo cancellation.
                                self.speaker.stop(); interrupted=True
                            if not active:
                                chunks=list(preroll); preroll.clear()
                            active=True; silent=0
                        elif active: silent+=1
                        if active: chunks.append(block.copy())
                        else: preroll.append(block.copy())
                        if active and (silent>=7 or len(chunks)>=140):
                            audio=np.concatenate(chunks).reshape(-1)
                            chunks=[]; active=False; silent=0; interrupted=False
                            if len(audio)<6400: continue
                            lang=self.store.data['settings']['language']
                            segments,_=model.transcribe(audio,language=None if lang=='auto' else lang,
                                beam_size=1,vad_filter=True,condition_on_previous_text=False)
                            text=' '.join(s.text for s in segments).strip()
                            if not self.enabled.is_set(): continue
                            match=match_wake(text,self.store.data['settings']['wake_word'])
                            if match:
                                text=text[match.end():].strip(' ,.!?'); self.session_until=time.time()+25
                            elif time.time()>self.session_until: continue
                            if text:
                                self.session_until=time.time()+25; self.events.put(('heard',text))
                            else: self.events.put(('status','Listening for your request...'))
        except Exception as e:
            self.ready=False; self.events.put(('status','Microphone unavailable: '+str(e)+' | Typed chat still works.'))
