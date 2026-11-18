# Install a successfully built JUPITAR preview

1. Obtain JUPITAR-Setup-0.3.0-preview.exe from a trusted, successful publisher build.
2. Review its origin and SHA-256. This preview is unsigned; do not blindly bypass
   Windows security warnings or disable protections.
3. Run the installer. It installs for your Windows account without requesting
   administrator rights. Python and the native AI engine are included.
4. Open JUPITAR from the Start menu. Review microphone consent.
5. In AI Setup, review model terms and choose Download / repair local AI.
   Internet is required once. Downloads are several GB; at least 6 GiB free disk
   space is checked for model data and temporary files. Download time varies.
6. Wait for verification. If interrupted, retry; cached partial data is reused
   where supported. Cancellation takes effect between file operations, not always
   immediately. The wizard shows stages, not an exact percentage or ETA.
7. Say Hey Jupitar or type. Settings changes the assistant name and wake phrase.
   Headphones are recommended. Use MIC to turn listening off.
8. Disconnect networking to test supported local features. Browser search, support
   links and mail synchronization still depend on external apps/services.

No separate Python, Ollama, terminal commands, API keys or pip installs are needed
for the built application. The first AI response may take longer while loading.
Full Mode targets 16 GB RAM; performance and Windows 10/11 compatibility remain
unvalidated. This build uses CPU inference by default.

Voice replies use installed Windows offline SAPI voices. Natural Hindi/Gujarati
neural voices are not bundled. A Windows language pack does not guarantee a
compatible SAPI voice. Screen analysis requires explicit one-shot consent.

Data: %LOCALAPPDATA%/JUPITAR. Memory/notes are plain text. No chat/audio/screenshot
files are deliberately saved by this app. No native engine diagnostics are retained.
Uninstall through Windows Settings. User data/models remain until you remove that
folder yourself after backing up wanted workspace documents. No autostart is installed.

Troubleshooting: AI Setup repairs components before the engine is loaded; close
and reopen the app before repair. A source ZIP cannot be installed like an EXE.
See TEST_REPORT.md for what has and has not been tested.
