# Update the app and publish the website

## 1. Back up and replace project files
Keep a copy of your current repository/build. Extract this ZIP and upload the
CONTENTS of the inner JUPITAR folder into your existing Uootsav/JUPITAR repository.
Do not upload the ZIP as a single file or nest another JUPITAR folder above main.py.
Same-named files must be replaced. Old jupitar/app.py and setup_ui.py are unused
by the new entry point; they can be deleted if still present in your repository.

Critical new/changed files: main.py, requirements.txt, jupitar/desktop.py,
jupitar/transfer.py, jupitar/selftest.py, ui/, site/, tools/build_windows.ps1,
tools/collect_notices.py, packaging/JUPITAR.iss and the two workflow files.

The hidden .github folder may not upload through the browser. Use Add file >
Create new file or edit the existing workflow directly. The exact paths are:
- .github/workflows/windows.yml (REPLACE the existing file)
- .github/workflows/pages.yml (ADD this file)
Do not create a second windows.yml inside another directory. Commit to main.

## 2. Build and test the updated Windows app
Actions > Build standalone Windows installer > Run workflow. Leave the optional
create_draft_release box unchecked for your first test. The workflow compiles the
engine, bundles Python/Qt/Chromium, downloads Rajdhani with its license, performs
a frozen smoke test and builds the unsigned installer. This workflow has NOT been
executed here. Fix any failing step before expecting an EXE.

Download JUPITAR-Standalone-Windows-Installer after success. Extract it and run
JUPITAR-Setup-0.4.0-preview.exe only after reviewing its origin and checksums.
Do not disable antivirus or blindly bypass Windows warnings. Test in a disposable
Windows account/VM first. The installer is not signed or Store certified.

Existing local state and model folders remain at %LOCALAPPDATA%/JUPITAR. The
activation manifest format is compatible with 0.3. Do not delete models merely
to test the visual update. To test actual downloads, use a separate test account
or back up the data folder. Never test destructive cleanup on valuable files.

## 3. Publish the premium website
1. Repository Settings > Pages.
2. Under Build and deployment, set Source to GitHub Actions.
3. Open Actions > Publish JUPITAR website > Run workflow.
4. After a successful deployment, use the URL shown in the deployment output or
   Settings > Pages. Do not guess a URL before deployment succeeds.
5. On GitHub Free, public Pages generally requires a public repository; private
   repository Pages depends on plan. Review GitHub's current Pages availability.

Only site/ is deployed, not your app source or private data. The workflow fetches
Rajdhani and its OFL license at build time. The website has no added analytics.
It calls GitHub's public releases API to discover installer downloads. No tokens
or secrets belong in website JavaScript. Preview site/index.html locally first.

## 4. Let anyone download a tested installer
Actions artifacts may require login and expire. They are not a public product
release. After testing, open your repository Releases area and create a release.
Attach JUPITAR-Setup-0.4.0-preview.exe and SHA256.txt from the successful artifact.
Use a prerelease label until validated. Publish the release when you are ready.
The website scans published releases (including prereleases) and enables the
Windows button only if a matching uploaded EXE is present. Drafts are invisible.

Optional: manually run the Windows workflow with create_draft_release checked.
After success it attempts to create a DRAFT prerelease with the EXE/checksum.
Review/test and publish that draft yourself. Reusing the same tag can fail if it
already exists; edit the draft or use a new version/tag deliberately. No public
release is automatically published by this package.

## 5. What remains before selling
Validate the Windows bridge, transparent orb and dragging on real displays/DPI;
measure RAM/CPU; test actual transfers, interruption, voices, screen consent,
permissions and offline operation; audit all dependencies/licenses and sign the
installer. Review Qt/PySide/Chromium obligations and retain notices. Complete
Store requirements separately. This package is not a commercial-ready claim.
