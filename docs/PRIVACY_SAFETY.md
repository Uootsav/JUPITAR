# Privacy and safety - standalone preview

Inference is sent only to the app-owned native process on 127.0.0.1 at a dynamic
port with a per-session secret. Proxy variables and redirects are not used by
the client. Inherited llama configuration is removed so it cannot enable tools,
tunnels or remote model downloads. The app does not enable native agent tools.
Windows job-object ownership is requested so the engine closes on app exit/crash.
These Windows lifecycle controls still require device testing.

Explicit first-launch downloads contact Hugging Face/storage providers. Engine
binaries are built into the application, not downloaded by the running app. Model
weights are checked against upstream LFS SHA-256 when available. The activation
manifest records hashes and sizes. Startup checks sizes/existence, not a full
rehash on every launch; this is not protection against a malicious local user.
The Gemma revision is pinned. Speech metadata resolves to a fixed commit per
installation and is recorded; production should pin all component revisions.

Microphone processing is local, including nearby speech before wake matching.
First-run consent is required despite the ON default preference. Mute closes the
capture stream. No audio, chat, screenshots or native engine diagnostics are
intentionally saved. OS paging/crash facilities are outside this app's control.

Approved memory, notes, settings and reminders are plain text in
%LOCALAPPDATA%/JUPITAR/state.json. Workspace files and model data are also local.
Memory can be viewed/edited/deleted. Uninstall preserves user data. Disk/account
security is the user's responsibility. Do not store credentials in memory.

Screen analysis is explicit one-shot consent, not monitoring. Browser search,
mail drafts and support links open external applications after approval; those
apps have separate privacy/network behavior. No automatic sending or payments.

All action plans and supported mutating/read-file actions require approval.
Destructive cleanup requires typing DELETE. No arbitrary shell/eval tool is
exposed to the model. File and screenshot content are untrusted. Prompt-injection
resistance is incomplete; allowlists and human review are the main boundary.
Test destructive operations only in a disposable Windows account/VM.
