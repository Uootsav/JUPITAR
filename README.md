# J.U.P.I.T.A.R. - standalone architecture preview 0.3.0
## Just-in-time Unified Personal Intelligence for Tasks, Automation & Reasoning

**Source/build package, not a compiled installer.** Windows 10/11 x64 and 16 GB
RAM are unvalidated targets. No EXE, MSIX, model weights or font binaries are in
this ZIP. Read START HERE.txt before doing anything else.

## What changed
- Removed the external Ollama runtime and its fixed-port API connection.
- Added an app-managed native llama.cpp engine, built into the Windows package.
- Added a first-launch AI Setup wizard for explicit model downloads and repair.
- Model weights are SHA-256 checked against upstream LFS metadata when available.
- Added a pinned native-engine build, bundled Python runtime, frozen-app smoke
  test, and Inno Setup installer build in GitHub Actions.
- End users of a successful build do not install Python, Ollama or pip packages.
- The app starts/stops its own engine on loopback with a per-session secret.
  Built-in engine tools, web UI and remote inference are not enabled.

## Get the installer
See docs/GET_INSTALLER.md. The GitHub workflow performs the Windows compilation;
you do not need development tools on your laptop. It has NOT been run from this
chat, so an installer is not yet available. A successful run produces an unsigned
JUPITAR-Setup-0.3.0-preview.exe. Do not confuse this source ZIP with that output.

## Existing capabilities retained
Local typed chat; customizable name/wake phrase; local Whisper speech recognition;
Windows offline voice output; cyan HUD, system stats and floating orb; approved
memory/notes; reminders; opt-in check-ins; one-shot consented screen analysis;
bounded action plans; permission-gated apps/files/documents/media controls;
cleanup with typed confirmation; no automatic payments or purchases.

## Remaining limits
Natural neural multilingual TTS, universal desktop automation, robust echo
cancellation, code signing, MSIX and Store certification are NOT completed.
CPU inference is the default; GPU acceleration is not configured. No performance
claim is made. Hindi/Gujarati recognition and conversation need native-speaker
testing. Gujarati natural speech is not bundled. See docs/FEATURES.md.

## Developer
Run python -m unittest discover -s tests -v. Build tools are needed only on a
Windows build machine, not on end-user devices. tools/build_windows.ps1 requires
Python 3.11, Git, CMake, Visual Studio C++ tools and Inno Setup 6; GitHub provisions
the hosted build environment. Original code remains MIT under the earlier choice.
Models, fonts and dependencies retain their own licenses. Name rights are uncleared.

[Support development](https://paypal.me/Uootsav)
