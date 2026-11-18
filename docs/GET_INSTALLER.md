# Get the Windows installer without local development tools

This is the ONE-TIME publisher build, not the end-user installation process.
No account action or build has been performed on your behalf in this chat.

## Browser-only GitHub route
1. Sign in as Uootsav. Create a repository named JUPITAR. You may keep it private
   while testing. GitHub Actions availability/usage limits depend on your account.
2. Extract this ZIP. Open the inner JUPITAR folder. Upload its CONTENTS, preserving
   the jupitar, tools, packaging, assets, tests and docs directories. Do not upload
   only the ZIP, and do not add an extra JUPITAR directory above the project root.
3. Ensure .github/workflows/windows.yml is present. If the hidden .github folder
   is difficult to upload, use Add file > Create new file, name it exactly
   .github/workflows/windows.yml, and paste the included workflow contents.
4. Commit all files to main. The workflow is configured to run on pushes to main.
   You can also open Actions > Build standalone Windows installer > Run workflow.
5. Wait for completion. A successful run compiles the native engine, bundles
   Python and dependencies, downloads Rajdhani plus its license, runs a frozen
   application smoke test, and compiles the unsigned installer.
6. On the successful run page, download the artifact named
   JUPITAR-Standalone-Windows-Installer. Extract it. It should contain
   JUPITAR-Setup-0.3.0-preview.exe, SHA256.txt and READ_ME_FIRST.md.
7. Review the source/build output and test the installer in a disposable Windows
   account or VM before using valuable files. Do not disable antivirus protections.
8. After testing, you may attach the installer to a GitHub prerelease. Do not
   label it final or Store-ready. Never commit certificates, tokens or private data.

## If the build fails
No installer exists until the workflow succeeds. Read the first failing step.
Native CMake/compiler errors, changed upstream downloads, missing DLLs, packaging
hooks and installer-tool changes may require fixes. The workflow has not been
executed here. The frozen smoke test checks GUI initialization, dependency imports
and engine --version; it does NOT validate inference, microphone or clean-machine
compatibility. Actual model and device tests remain mandatory.

Official manual-run guide:
https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow

## Local build alternative (developers only)
Use BUILD_ON_WINDOWS.cmd after installing its documented build tools. This is
optional and is not the consumer installation path.
