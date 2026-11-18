# Measured progress behavior

The new desktop entry point calls jupitar/transfer.py, not the legacy Tk setup.
The transfer plan resolves exact model metadata and totals expected bytes.
During streaming, the UI receives aggregate done/total, percent, current file,
measured speed and ETA. Speed uses a rolling sample window; ETA remains
Calculating until enough data arrives. Verification is separate from network time.

Pause is cooperative between read/hash chunks. A stalled network read may take
up to its timeout to return. Resume uses a .part file and requests HTTP Range.
If the server ignores Range, the file safely restarts rather than appending wrong
data. Exact Content-Range, file sizes, LFS SHA-256 and Git object hashes are checked.
Only after all files verify is the activation marker atomically written.

Total progress may jump forward when cached files are verified. A corrupt cached
file is removed and must be downloaded on retry. ETA is an estimate, not a promise;
metadata lookup and verification have no fabricated countdown. Existing 0.3 model
files can be reused. New .part files are not compatible with an interrupted old
huggingface_hub cache transfer; already completed model files remain reusable.

The old components.install_components helper remains only for backward-compatible
isolated tests; the premium app uses transfer.install. No simulated progress is
used by the installed UI. Website demo numbers and UI test fixtures are explicitly
labeled illustrative and do not represent a real transfer.
