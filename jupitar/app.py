"""JUPITAR desktop HUD. No web assets or telemetry loaded at runtime."""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, font
import threading, queue, time, math, os, sys, webbrowser, json
from pathlib import Path
from .core import Store, Brain, Actions, validate_identity, describe_screen
from .voice import Speaker, Listener
from .components import is_ready
from .setup_ui import SetupWizard
BG='#050e18'; PANEL='#0a1c2c'; CYAN='#56e5ee'; TEXT='#d3edf1'

class App:
    def __init__(self,root):
        self.root=root; self.store=Store(); self.events=queue.Queue(); self.busy=False; self.closed=False; self.orb=None
        self.cancelled=threading.Event(); self.audio_level=0.0
        self.brain=Brain(self.store); self.actions=Actions(self.store,self.approve)
        self.speaker=Speaker(self.store,self.events); self.listener=Listener(self.store,self.events,self.speaker)
        root.title('JUPITAR | Local AI companion | Preview 0.3'); root.geometry('1000x760'); root.minsize(800,600); root.configure(bg=BG)
        self.load_font(); families=font.families()
        self.heading='Rajdhani' if 'Rajdhani' in families else 'Bahnschrift'
        root.option_add('*Font',('Segoe UI',10))
        style=ttk.Style(); style.theme_use('clam')
        style.configure('TButton',background=PANEL,foreground=CYAN,padding=8)
        top=tk.Frame(root,bg=BG); top.pack(fill='x',padx=20,pady=10)
        tk.Label(top,text='J . U . P . I . T . A . R .',font=(self.heading,30,'bold'),fg=CYAN,bg=BG).pack(side='left')
        tk.Label(top,text='FULL MODE / LOCAL AI / 16 GB TARGET',fg=TEXT,bg=BG).pack(side='right')
        tk.Label(root,text='Just-in-time Unified Personal Intelligence for Tasks, Automation & Reasoning',bg=BG,fg=TEXT,font=(self.heading,11)).pack(fill='x',padx=20)
        self.telemetry=tk.StringVar(value='Loading system telemetry...')
        tk.Label(root,textvariable=self.telemetry,bg=BG,fg=CYAN,font=(self.heading,12)).pack(fill='x',padx=20)
        self.hud=tk.Canvas(root,height=100,bg=BG,highlightthickness=0); self.hud.pack(fill='x')
        self.phase=0; self.animate()
        self.chat=scrolledtext.ScrolledText(root,bg=PANEL,fg=TEXT,insertbackground=CYAN,wrap='word',font=('Segoe UI',12),state='disabled',relief='flat')
        self.chat.pack(fill='both',expand=True,padx=20,pady=8)
        self.chat.tag_configure('name',foreground=CYAN,font=(self.heading,13,'bold'))
        toolbar=tk.Frame(root,bg=BG); toolbar.pack(fill='x',padx=20)
        self.mic=tk.BooleanVar(value=self.store.data['settings']['listening'])
        self.speak=tk.BooleanVar(value=self.store.data['settings']['speak'])
        tk.Checkbutton(toolbar,text='MIC / wake phrase in Settings',variable=self.mic,command=self.toggle_mic,bg=BG,fg=CYAN,selectcolor=PANEL,activebackground=BG,activeforeground=CYAN).pack(side='left')
        tk.Checkbutton(toolbar,text='Voice replies',variable=self.speak,command=lambda:self.store.setting('speak',self.speak.get()),bg=BG,fg=TEXT,selectcolor=PANEL).pack(side='left')
        for title,command in [('STOP',self.stop),('Memory',self.memory),('Settings',self.settings),('AI Setup',self.ai_setup),('Screen',self.screen),('Orb',self.show_orb),('Help',self.help)]:
            ttk.Button(toolbar,text=title,command=command).pack(side='left',padx=3)
        row=tk.Frame(root,bg=BG); row.pack(fill='x',padx=20,pady=10)
        self.entry=tk.Entry(row,bg=PANEL,fg=TEXT,insertbackground=CYAN,font=('Segoe UI',13),relief='flat')
        self.entry.pack(side='left',fill='x',expand=True,ipady=10); self.entry.bind('<Return>',lambda e:self.send())
        self.send_button=ttk.Button(row,text='SEND',command=self.send); self.send_button.pack(side='right',padx=8)
        self.status=tk.StringVar(value='Initializing local voice. No audio recordings saved.')
        tk.Label(root,textvariable=self.status,bg=BG,fg=CYAN,anchor='w',wraplength=950).pack(fill='x',padx=20,pady=5)
        bottom=tk.Frame(root,bg=BG); bottom.pack(fill='x',padx=20,pady=5)
        ttk.Button(bottom,text='Support JUPITAR',command=self.support).pack(side='right')
        ttk.Button(bottom,text='Clear chat',command=self.clear_chat).pack(side='left')
        ttk.Button(bottom,text='Open workspace',command=lambda:os.startfile(self.store.workspace)).pack(side='left',padx=5)
        self.add('JUPITAR','Hello! I am your local AI companion. Chat, joke, or ask for a supported laptop task. '
                 'I ask before taking actions. Say your configured wake phrase to start a 25-second conversation window. '
                 'Use headphones to reduce speaker feedback. Click Help for limitations and setup.')
        root.protocol('WM_DELETE_WINDOW',self.close)
        self.last_checkin=time.time(); self.onboarding()
        self.voice_started=False; self.setup_window=None
        if is_ready(self.store): self.start_voice()
        else: root.after(500,self.ai_setup)
        root.after(100,self.poll); root.after(1000,self.tick)
    def start_voice(self):
        if not self.voice_started:
            self.listener.start(); self.voice_started=True
        self.status.set('AI components ready. Local engine starts automatically on first request.')
    def ai_setup(self):
        if self.brain.engine.process and self.brain.engine.process.poll() is None:
            messagebox.showinfo('Repair local AI','Close and reopen JUPITAR before repairing downloaded components. This avoids replacing files used by the running engine.',parent=self.root);return
        if self.busy:
            messagebox.showinfo('AI Setup','Finish or stop the current request first.',parent=self.root);return
        if self.setup_window and self.setup_window.win.winfo_exists():
            self.setup_window.win.lift();return
        self.setup_window=SetupWizard(self.root,self.store,self.start_voice)
    def onboarding(self):
        if self.store.data['settings']['onboarding_done']: return
        self.listener.toggle(False)
        try:
            import psutil
            if psutil.virtual_memory().total < 15.5*2**30:
                messagebox.showwarning('Full Mode hardware target','Full Mode targets 16 GB RAM. This device reports less; performance may be poor. Consider Lite mode.',parent=self.root)
        except ImportError: pass
        consent=messagebox.askyesno('Local microphone disclosure',
            'JUPITAR uses AI and can make mistakes. It is not a person.\n\n'
            'Always-listening processes nearby speech locally, including before the wake phrase. '
            'No recordings are saved by this app. Approved memory and notes are plain text on this Windows account. '
            'Headphones recommended.\n\nEnable local microphone listening? No keeps typed chat available. You can change this anytime.',parent=self.root)
        self.mic.set(consent); self.listener.toggle(consent); self.store.setting('listening',consent)
        self.store.setting('onboarding_done',True)
    def screen(self):
        if self.busy: return
        question=simpledialog.askstring('Read screen locally','What should I look for? Close private windows first.',initialvalue='Summarize the visible screen.',parent=self.root)
        if not question: return
        if not messagebox.askyesno('Approve one screenshot?',
            'Capture the primary display ONCE and send it to your local vision model? It may contain sensitive data. '
            'The image is not saved by this app. This does not enable ongoing screen access.',parent=self.root): return
        self.root.iconify(); self.busy=True; self.cancelled.clear(); self.send_button.configure(state='disabled')
        def work():
            time.sleep(0.7)
            try: answer='Cancelled.' if self.cancelled.is_set() else describe_screen(self.brain,question)
            except Exception as e: answer='Screen analysis failed: '+str(e)
            self.events.put(('screen_reply',answer))
        threading.Thread(target=work,daemon=True).start()
    def load_font(self):
        try:
            import ctypes
            base=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent.parent))
            for p in (base/'assets').glob('*.ttf'): ctypes.windll.gdi32.AddFontResourceExW(str(p),0x10,0)
        except Exception: pass
    def animate(self):
        if self.closed: return
        c=self.hud; c.delete('all'); w=max(c.winfo_width(),800); x=w/2; self.phase=(self.phase+(0 if self.store.data['settings']['reduced_motion'] else 4))%360
        for radius in (26,37,45):
            c.create_oval(x-radius,50-radius,x+radius,50+radius,outline=CYAN,width=1)
        c.create_arc(x-42,8,x+42,92,start=self.phase,extent=110,style='arc',outline='#e0ffff',width=4)
        pulse=20+min(10,self.audio_level*10)
        c.create_oval(x-pulse,50-pulse,x+pulse,50+pulse,outline='#164a61',width=2)
        c.create_text(x,50,text='J',fill=CYAN,font=(getattr(self,'heading','Segoe UI'),23,'bold'))
        c.create_line(30,50,x-65,50,fill='#1d6472'); c.create_line(x+65,50,w-30,50,fill='#1d6472')
        self.root.after(90,self.animate)
    def add(self,who,text):
        self.chat.configure(state='normal'); self.chat.insert('end',(self.store.data['settings']['assistant_name'] if who=='JUPITAR' else who).upper()+'\n','name'); self.chat.insert('end',str(text)+'\n\n')
        self.chat.configure(state='disabled'); self.chat.see('end')
    def toggle_mic(self):
        on=self.mic.get(); self.listener.toggle(on); self.store.setting('listening',on)
        self.status.set('MIC ON: waiting for '+self.store.data['settings']['wake_word'] if on else 'MIC OFF: microphone stream closes; typed chat available.')
    def stop(self): self.cancelled.set(); self.speaker.stop(); self.listener.session_until=0; self.status.set('Speech stopped. Pending inference may finish, but no further planned actions will start.')
    def send(self,text=None):
        text=(text if text is not None else self.entry.get()).strip()
        if not text: return
        if text.lower() in ('stop','stop talking','be quiet'): self.stop(); return
        if self.busy: self.status.set('Finishing the current request. Please retry afterward.'); return
        self.entry.delete(0,'end'); self.add('You',text); self.speaker.stop(); self.cancelled.clear(); self.busy=True
        self.send_button.configure(state='disabled'); self.status.set('Thinking locally...')
        threading.Thread(target=self.work,args=(text,),daemon=True).start()
    def work(self,text):
        try:
            result=self.brain.ask(text)
            if self.cancelled.is_set(): self.events.put(('reply','Stopped before any new action.')); return
            if 'plan' in result:
                plan=result['plan']
                if not isinstance(plan,list) or not 1<=len(plan)<=5: raise ValueError('Plans need 1-5 supported steps.')
                if not self.approve('Review proposed plan',json.dumps(plan,ensure_ascii=False,indent=2),False): reply='Plan cancelled.'
                else:
                    outcomes=[]
                    for step in plan:
                        if self.cancelled.is_set(): outcomes.append('Stopped before next step.'); break
                        if not isinstance(step,dict): outcomes.append('Invalid step; stopped.'); break
                        try: outcomes.append(self.actions.run(step.get('action'),step.get('args',{})))
                        except Exception as e: outcomes.append('Stopped: '+str(e)); break
                    reply='\n\n'.join(outcomes)
                self.brain.record_result(reply)
            elif 'action' in result:
                try: reply=self.actions.run(result['action'],result.get('args',{}))
                except Exception as e: reply='Action not completed: '+str(e)
                self.brain.record_result(reply)
            else: reply=str(result.get('reply','Please rephrase your request.'))
            if self.cancelled.is_set(): reply='Stopped. Completed actions cannot be undone automatically.'
            self.events.put(('reply',reply))
        except Exception as e: self.events.put(('reply','Local request unavailable: '+str(e)+'\nOpen AI Setup to download or repair local components.'))
    def approve(self,title,detail,destructive=False):
        if self.cancelled.is_set(): return False
        event=threading.Event(); box={'yes':False}
        self.events.put(('approval',(title,detail,destructive,event,box)))
        while not event.wait(0.2):
            if self.closed: return False
        return box['yes']
    def poll(self):
        if self.closed: return
        try:
            while True:
                kind,value=self.events.get_nowait()
                if kind=='level': self.audio_level=value
                elif kind=='status': self.status.set(value)
                elif kind=='heard': self.send(value)
                elif kind=='approval':
                    title,detail,danger,event,box=value
                    if self.cancelled.is_set(): event.set(); continue
                    # Pause listening during approval so ambient speech cannot approve actions.
                    was_on=self.mic.get(); self.listener.toggle(False); self.speaker.stop()
                    try:
                        if danger:
                            answer=simpledialog.askstring(title,detail+'\n\nType DELETE to approve; Cancel to stop.',parent=self.root)
                            box['yes']=answer=='DELETE'
                        else: box['yes']=messagebox.askyesno(title,detail,parent=self.root)
                    finally:
                        self.listener.toggle(was_on); event.set()
                elif kind in ('reply','screen_reply'):
                    if kind=='screen_reply': self.root.deiconify()
                    self.busy=False; self.send_button.configure(state='normal'); self.add('JUPITAR',value)
                    self.status.set('Local request complete. MIC '+('ON' if self.mic.get() else 'OFF'))
                    self.speaker.say(value)
        except queue.Empty: pass
        self.root.after(100,self.poll)
    def tick(self):
        if self.closed: return
        try: self.telemetry.set(self.actions.system_info()+' | '+time.strftime('%H:%M:%S'))
        except Exception: self.telemetry.set('System telemetry unavailable')
        for r in self.store.due():
            self.add('Reminder',r['text']); self.speaker.say('Reminder: '+r['text'])
        if self.store.data['settings']['checkins'] and time.time()-self.last_checkin>=3600 and not self.busy:
            self.last_checkin=time.time(); text='You have had JUPITAR open for an hour. Would a stretch or water break help?'
            self.add('JUPITAR',text); self.speaker.say(text)
        self.root.after(1000,self.tick)
    def memory(self):
        win=tk.Toplevel(self.root); win.title('Local memory and notes'); win.geometry('650x440')
        tk.Label(win,text='Plain text on this Windows account. Select an entry to edit or delete.').pack(pady=8)
        listing=tk.Listbox(win); listing.pack(fill='both',expand=True,padx=10)
        refs=[]
        def refresh():
            listing.delete(0,'end'); refs.clear()
            for key in ('memories','notes'):
                for i,value in enumerate(self.store.data[key]): refs.append((key,i)); listing.insert('end',key+': '+str(value))
        def edit():
            if not listing.curselection(): return
            key,i=refs[listing.curselection()[0]]
            value=simpledialog.askstring('Edit local entry','Text:',initialvalue=self.store.data[key][i],parent=win)
            if value is not None: self.store.data[key][i]=value; self.store.save(); refresh()
        def delete():
            if not listing.curselection(): return
            if messagebox.askyesno('Delete entry','Remove selected entry?',parent=win):
                key,i=refs[listing.curselection()[0]]; del self.store.data[key][i]; self.store.save(); refresh()
        ttk.Button(win,text='Edit selected',command=edit).pack(side='left',padx=10,pady=8)
        ttk.Button(win,text='Delete selected',command=delete).pack(side='left')
        ttk.Button(win,text='Open local data folder',command=lambda:os.startfile(self.store.folder)).pack(side='right',padx=10)
        refresh()
    def settings(self):
        win=tk.Toplevel(self.root); win.title('JUPITAR settings'); win.geometry('620x680')
        s=self.store.data['settings']; variables={}
        for key,values in [('assistant_name',None),('wake_word',None),('model',('gemma3:4b',)),('language',('auto','en','hi','gu')),('voice_id',None),('threshold',None)]:
            tk.Label(win,text=key).pack(anchor='w',padx=15,pady=3)
            v=tk.StringVar(value=str(s[key])); variables[key]=v
            if values: ttk.Combobox(win,textvariable=v,values=values,state='readonly').pack(fill='x',padx=15)
            else: ttk.Entry(win,textvariable=v).pack(fill='x',padx=15)
        check=tk.BooleanVar(value=s['checkins']); motion=tk.BooleanVar(value=s['reduced_motion'])
        tk.Checkbutton(win,text='Hourly friendly check-ins (opt in)',variable=check).pack()
        tk.Checkbutton(win,text='Reduce HUD motion',variable=motion).pack()
        tk.Label(win,text='Voice ID: installed offline SAPI voice; blank = default.\nFull Mode runs the bundled engine; no separate AI service is required.\nHeadphones recommended. Gujarati neural speech is not bundled.',wraplength=580).pack(pady=8)
        def test_wake():
            from .core import match_wake
            text=simpledialog.askstring('Wake phrase test','Type an example transcription:',parent=win)
            if text is not None: messagebox.showinfo('Wake test','MATCH' if match_wake(text,variables['wake_word'].get()) else 'NO MATCH',parent=win)
        def save():
            try:
                name,wake=validate_identity(variables['assistant_name'].get(),variables['wake_word'].get())
                threshold=float(variables['threshold'].get())
                if not 0.001<=threshold<=0.5: raise ValueError('Threshold must be 0.001 to 0.5.')
            except ValueError as e: messagebox.showerror('Settings',str(e),parent=win); return
            for k,v in variables.items(): self.store.setting(k,threshold if k=='threshold' else v.get().strip())
            self.store.setting('checkins',check.get()); self.store.setting('reduced_motion',motion.get())
            self.root.title('JUPITAR | '+name+' | Local AI preview'); win.destroy()
        ttk.Button(win,text='Test wake phrase against typed transcript',command=test_wake).pack(pady=5)
        ttk.Button(win,text='Save',command=save).pack(pady=5)
        ttk.Button(win,text='Reset name and wake phrase',command=lambda:(variables['assistant_name'].set('JUPITAR'),variables['wake_word'].set('hey jupitar'))).pack(pady=5)
    def show_orb(self):
        if self.orb and self.orb.winfo_exists(): self.orb.destroy(); self.orb=None; return
        orb=tk.Toplevel(self.root); self.orb=orb; orb.overrideredirect(True); orb.attributes('-topmost',True); orb.geometry('100x100+60+100'); orb.configure(bg=BG)
        canvas=tk.Canvas(orb,width=100,height=100,bg=BG,highlightthickness=0); canvas.pack()
        canvas.create_oval(8,8,92,92,outline=CYAN,width=3); canvas.create_text(50,43,text=self.store.data['settings']['assistant_name'][:12],fill=CYAN,font=(self.heading,13,'bold')); canvas.create_text(50,64,text='double-click',fill=TEXT,font=('Segoe UI',8))
        def drag(e): orb.geometry(f'+{e.x_root-50}+{e.y_root-50}')
        canvas.bind('<B1-Motion>',drag)
        canvas.bind('<Double-Button-1>',lambda e:(self.root.deiconify(),self.root.lift(),self.entry.focus_set()))
        canvas.bind('<Button-3>',lambda e:orb.destroy())
    def clear_chat(self):
        if self.busy: return
        self.brain.history.clear(); self.chat.configure(state='normal'); self.chat.delete('1.0','end'); self.chat.configure(state='disabled')
    def help(self):
        messagebox.showinfo('JUPITAR preview',
            'Setup: click AI Setup and download the local components once.\n\n'
            'Try: Tell me a joke / Remember that I prefer Gujarati / Open Calculator / '
            'Find files named invoice / Create a maintenance log spreadsheet / Remind me in 10 minutes to stretch / '
            'Clean temporary files / Empty Recycle Bin.\n\n'
            'Always listening uses local speech recognition, not a dedicated low-power wake detector. '
            'Headphones strongly recommended: interruption is energy-based, without echo cancellation. '
            '16 GB is a design target, not a measured guarantee. Small models may misunderstand requests. '
            'All actions need approval. Destructive actions require typing DELETE.\n\n'
            'No arbitrary desktop automation, auto-send, payments, or admin actions. '
            'Voice quality depends on installed offline SAPI voices. Gujarati voice is not bundled. '
            'Reminders need JUPITAR running. Chat is session-only; memory/notes are plain text locally.',parent=self.root)
    def support(self):
        if messagebox.askyesno('Open support link?','Open PayPal in your browser? No payment will be made automatically.'):
            webbrowser.open('https://paypal.me/Uootsav')
    def close(self):
        self.closed=True; self.listener.closed.set(); self.listener.enabled.set(); self.speaker.stop(); self.brain.engine.stop(); self.root.destroy()

def main():
    root=tk.Tk()
    try: App(root)
    except Exception as e: messagebox.showerror('JUPITAR startup',str(e)); root.destroy(); return
    root.mainloop()
