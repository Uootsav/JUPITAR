# Before calling JUPITAR a final release

Unchecked items have NOT been validated by the supplied automated tests.

- [ ] Build EXE successfully on Windows x64.
- [ ] Test clean Windows 10 and Windows 11, each with 16 GB RAM.
- [ ] Measure idle RAM, model-loaded RAM, CPU, battery use and response latency.
- [ ] Verify no outbound inference/audio requests with network monitoring.
- [ ] Test disconnected networking after initial downloads.
- [ ] Test missing Ollama, missing models, no microphone, corrupt state and no voice.
- [ ] Verify mic mute closes stream and no muted transcript is submitted.
- [ ] Test wake phrase false positives and false negatives in a noisy room.
- [ ] Test interruption with headphones and speakers; document feedback limits.
- [ ] Evaluate English, Hindi, Gujarati and code-switching with native speakers.
- [ ] Select/license/bundle natural multilingual offline TTS if that is required.
- [ ] Test each action with approval, rejection, malformed args and prompt injection.
- [ ] Test temp cleanup and Recycle Bin ONLY in a disposable VM/account.
- [ ] Test memory edit/delete, reminder restart behavior and orb interaction.
- [ ] Test new document/spreadsheet content and no-overwrite behavior.
- [ ] Test package on a machine without Python, preserving entire folder build.
- [ ] Lock/audit dependencies, include binary license notices and an SBOM.
- [ ] Obtain code signing if distributing broadly; document uninstall.
- [ ] Complete security review and project-name clearance.

- [ ] Test custom names/wake phrases, Hindi/Gujarati and literal regex handling.
- [ ] Test first-run consent, denied microphone, screen capture and sensitive-data warnings.
- [ ] Test five-step plan bounds, rejected steps and STOP cancellation.
- [ ] Test installer install/uninstall and frozen --download-models command.
- [ ] Resolve name rights, price, publisher identity, support and privacy URLs.
- [ ] Review current Store AI/transaction policies and implement missing controls.

## Standalone conversion gates
- [ ] Execute the new Windows workflow successfully.
- [ ] Confirm frozen smoke-test report passes and installer artifact exists.
- [ ] Test on a clean PC without Python, Ollama or developer tools.
- [ ] Test actual model downloads, retries, cancellation, checksum errors and disk limits.
- [ ] Verify app-owned engine binds only loopback, requires secret, closes on crash.
- [ ] Verify no external inference traffic after setup.
- [ ] Test first-launch wizard and actual Gemma text/vision compatibility.
- [ ] Audit all bundled binary licenses and lock tested dependencies.

## 0.4 release gates
- [ ] Build the Qt/Chromium package on Windows and validate frozen smoke test.
- [ ] Test native bridge, transparent orb, drag, minimize/restore and multiple DPI.
- [ ] Test actual HTTPS downloads, pause/resume, speed/ETA and disk-full behavior.
- [ ] Enable Pages, deploy, and verify public release downloads without login.
- [ ] Audit Qt/Chromium notices and sign a tested installer before broad release.
