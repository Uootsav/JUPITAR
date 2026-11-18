"""First-launch component wizard; all widget updates run on Tk's main thread."""
import queue, threading, tkinter as tk, webbrowser
from tkinter import ttk,messagebox
from .components import install_components,is_ready
from .runtime import bundle_root

class SetupWizard:
    def __init__(self,parent,store,on_ready):
        self.store=store;self.on_ready=on_ready;self.running=False;self.cancel=threading.Event();self.events=queue.Queue()
        self.win=tk.Toplevel(parent);self.win.title('JUPITAR | First-launch AI setup');self.win.geometry('680x510');self.win.transient(parent)
        tk.Label(self.win,text='Set up your local assistant',font=('Segoe UI',20,'bold')).pack(pady=15)
        tk.Label(self.win,text='No separate Python or Ollama installation is needed in a compiled build.\n'
            'Download the language/vision and speech-recognition models once.\n'
            'Afterward, local conversation and supported tasks work offline.\n\n'
            'Several GB of downloads; at least 6 GiB free disk space required.\n'
            'Windows offline voices are used; natural Gujarati voice is not bundled.\n'
            'Downloads contact Hugging Face and its storage providers.\n'
            'The app does not upload your conversations or microphone audio.',justify='left',wraplength=630).pack(padx=20)
        self.accept=tk.BooleanVar(value=False)
        tk.Checkbutton(self.win,text='I have reviewed the model terms and agree to download these components.',variable=self.accept,wraplength=620).pack(pady=12)
        ttk.Button(self.win,text='Review Gemma model terms',command=lambda:webbrowser.open('https://ai.google.dev/gemma/terms')).pack()
        self.label=tk.StringVar(value='Ready to download.' if not is_ready(store) else 'Components already installed. Download again to verify/repair.')
        tk.Label(self.win,textvariable=self.label,wraplength=630,justify='left').pack(padx=20,pady=15)
        self.bar=ttk.Progressbar(self.win,mode='indeterminate');self.bar.pack(fill='x',padx=20)
        row=tk.Frame(self.win);row.pack(pady=15)
        self.button=ttk.Button(row,text='Download / repair local AI',command=self.start);self.button.pack(side='left',padx=5)
        ttk.Button(row,text='Cancel after current file',command=self.cancel.set).pack(side='left',padx=5)
        ttk.Button(row,text='Close',command=self.close).pack(side='left',padx=5)
        if not (bundle_root()/'engine'/'llama-server.exe').exists():
            self.label.set('This is source code, not a built Windows app. Build the bundled engine and installer using the included GitHub workflow first.');self.button.configure(state='disabled')
        self.win.protocol('WM_DELETE_WINDOW',self.close);self.win.after(150,self.poll)
    def start(self):
        if self.running:return
        if not self.accept.get():messagebox.showinfo('Review terms','Review and accept the model terms before downloading.',parent=self.win);return
        self.running=True;self.cancel.clear();self.button.configure(state='disabled');self.bar.start(12)
        def work():
            try:
                install_components(self.store,lambda text:self.events.put(('status',text)),self.cancel)
                self.events.put(('done','Local components installed and verified.'))
            except Exception as e:self.events.put(('error',str(e)))
        threading.Thread(target=work,daemon=True).start()
    def poll(self):
        if not self.win.winfo_exists():return
        try:
            while True:
                kind,text=self.events.get_nowait();self.label.set(text)
                if kind in ('done','error'):
                    self.running=False;self.bar.stop();self.button.configure(state='normal')
                    if kind=='done':self.on_ready();self.win.destroy();return
        except queue.Empty:pass
        self.win.after(150,self.poll)
    def close(self):
        if self.running:
            self.cancel.set();self.label.set('Cancellation requested. Wait for the current file operation to finish; then close.');return
        self.win.destroy()
