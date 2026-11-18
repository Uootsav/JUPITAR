# Third-party components

Original code: MIT, Uootsav. No model weights, native binaries or font files are
included in this source ZIP. A successful Windows build incorporates third-party
components whose original licenses must be retained and audited before sale.

- llama.cpp: https://github.com/ggml-org/llama.cpp (MIT project; retain dependency notices).
  Build pins commit 2d8a32502909ca065c41c4cf5f2fb1c427c047fc.
- Gemma model: https://huggingface.co/ggml-org/gemma-3-4b-it-GGUF
  Terms: https://ai.google.dev/gemma/terms (not relicensed by this app's MIT license).
- faster-whisper: https://github.com/SYSTRAN/faster-whisper and its model/dependencies.
- PyInstaller: https://pyinstaller.org/en/stable/operating-mode.html
- Rajdhani: https://fonts.google.com/specimen/Rajdhani ; build downloads original OFL.
- Python, Tcl/Tk, numpy, sounddevice, CTranslate2, PyAV, onnxruntime, tokenizers,
  huggingface-hub, Pillow, psutil, python-docx, openpyxl, pypdf and all transitive
  dependencies retain their own licenses. This file is NOT a complete binary SBOM.
- Windows SAPI voices are separately installed/licensed by their vendors.

No third-party fictional artwork, sounds, voice clones or logos are included.
Name/trademark clearance has not been performed. Dependencies currently use ranges;
resolve, lock, audit and collect notices for the actual binary before distribution.

## 0.4 UI additions
PySide6/Qt WebEngine and bundled Chromium add separate license/notice obligations.
Review the exact versions and distribution requirements before sale. Dynamic
libraries are packaged by PyInstaller hooks. tools/collect_notices.py collects
installed-distribution notices, not a complete binary SBOM or legal compliance
certification. Rajdhani is downloaded with its OFL license by both build workflows.
The orbital renderer, CSS and website copy are original project source.
