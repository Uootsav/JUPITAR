# Actual validation report - JUPITAR 0.4 Orbital Edition

## Passed in the authoring environment
- 58 isolated Python tests (core actions, identity, local transport, mocked component
  installation, range resume/restart, size/hash checks, pause, speed/ETA math).
- Python source syntax and JavaScript syntax checks.
- YAML structure parsing for Windows build and Pages deployment workflows.
- Headless Chromium rendering of the actual HUD and website frontend.
- Browser checks: setup/settings dialogs, Escape, typed preview response, progress
  percentage/ETA rendering, empty-release state, synthetic published-release state,
  API-failure fallback, mobile no-horizontal-overflow checks for site and HUD.
- No JavaScript page errors in the HUD browser check.
- Floating-orb frontend rendered with transparent screenshot background.

## What the previews mean
site/assets/command-center.png is a real screenshot of the frontend in browser
preview mode, not a tested Windows app. Telemetry is shown as unavailable rather
than fabricated. The download-dialog screenshot uses explicitly labeled UI test
fixtures. Website example speed/ETA numbers are labeled illustrative. Browser
release tests use synthetic metadata, not a real published installer.

Rajdhani could not be downloaded in this environment (HTTP 403), so screenshots
use fallback fonts. Both build/deploy workflows download the TTF and OFL license.
No font binary is included in this source ZIP.

## Not performed
No Windows compilation, installer execution, native Qt bridge/window/transparency/
drag test, actual multi-GB model download, inference, audio, cleanup, Recycle Bin,
16 GB performance measurement, signing, Store certification, GitHub repository
mutation, Pages deployment or public release publication. PySide6 is not installed
in this sandbox; the HTML/CSS/Canvas layer was tested in Chromium, not in native Qt.

Qt/Chromium increases package size and resource use. Audit exact licenses and
measure real hardware before sale. The new frozen smoke test is in the Windows
workflow but has not run here. No EXE/MSIX/native engine/model weights are included.

## Unit-test output
```
test_bad_names (test_core.CoreTests.test_bad_names) ... ok
test_default_listening (test_core.CoreTests.test_default_listening) ... ok
test_deny (test_core.CoreTests.test_deny) ... ok
test_due_reminders (test_core.CoreTests.test_due_reminders) ... ok
test_local_model_allowlist (test_core.CoreTests.test_local_model_allowlist) ... ok
test_memory_persists (test_core.CoreTests.test_memory_persists) ... ok
test_no_overwrite (test_core.CoreTests.test_no_overwrite) ... ok
test_temp_age (test_core.CoreTests.test_temp_age) ... ok
test_temp_no_directories (test_core.CoreTests.test_temp_no_directories) ... ok
test_unknown_action (test_core.CoreTests.test_unknown_action) ... ok
test_direct_cleanup (test_core.RoutingTests.test_direct_cleanup) ... ok
test_direct_recycle (test_core.RoutingTests.test_direct_recycle) ... ok
test_bad_identity (test_identity.IdentityTests.test_bad_identity) ... ok
test_custom_wake (test_identity.IdentityTests.test_custom_wake) ... ok
test_default_wake (test_identity.IdentityTests.test_default_wake) ... ok
test_full_default (test_identity.IdentityTests.test_full_default) ... ok
test_gujarati (test_identity.IdentityTests.test_gujarati) ... ok
test_hindi (test_identity.IdentityTests.test_hindi) ... ok
test_identity (test_identity.IdentityTests.test_identity) ... ok
test_no_payment_tool (test_identity.IdentityTests.test_no_payment_tool) ... ok
test_no_substring (test_identity.IdentityTests.test_no_substring) ... ok
test_plan_returned_not_executed (test_identity.IdentityTests.test_plan_returned_not_executed) ... ok
test_prompt_custom_name (test_identity.IdentityTests.test_prompt_custom_name) ... ok
test_redirect_blocked (test_identity.IdentityTests.test_redirect_blocked) ... ok
test_regex_literal (test_identity.IdentityTests.test_regex_literal) ... ok
test_rename_preserves_memory (test_identity.IdentityTests.test_rename_preserves_memory) ... ok
test_block_endpoint (test_standalone.StandaloneTests.test_block_endpoint) ... ok
test_cancel_hash (test_standalone.StandaloneTests.test_cancel_hash) ... ok
test_checksum_failure_not_activated (test_standalone.StandaloneTests.test_checksum_failure_not_activated) ... ok
test_hash (test_standalone.StandaloneTests.test_hash) ... ok
test_insufficient_space (test_standalone.StandaloneTests.test_insufficient_space) ... ok
test_invalid_gguf (test_standalone.StandaloneTests.test_invalid_gguf) ... ok
test_malformed_marker (test_standalone.StandaloneTests.test_malformed_marker) ... ok
test_missing_engine (test_standalone.StandaloneTests.test_missing_engine) ... ok
test_mock_install_and_ready (test_standalone.StandaloneTests.test_mock_install_and_ready) ... ok
test_no_old_service_request (test_standalone.StandaloneTests.test_no_old_service_request) ... ok
test_no_redirect (test_standalone.StandaloneTests.test_no_redirect) ... ok
test_not_ready (test_standalone.StandaloneTests.test_not_ready) ... ok
test_request_auth_loopback (test_standalone.StandaloneTests.test_request_auth_loopback) ... ok
test_safe_native_command (test_standalone.StandaloneTests.test_safe_native_command) ... ok
test_strip_inherited_agent (test_standalone.StandaloneTests.test_strip_inherited_agent) ... ok
test_unique_tokens (test_standalone.StandaloneTests.test_unique_tokens) ... ok
test_bad_blob (test_transfer.TransferTests.test_bad_blob) ... ok
test_bad_checksum (test_transfer.TransferTests.test_bad_checksum) ... ok
test_bad_range (test_transfer.TransferTests.test_bad_range) ... ok
test_checksum (test_transfer.TransferTests.test_checksum) ... ok
test_fresh_transfer (test_transfer.TransferTests.test_fresh_transfer) ... ok
test_full_mock_install (test_transfer.TransferTests.test_full_mock_install) ... ok
test_git_blob (test_transfer.TransferTests.test_git_blob) ... ok
test_https_only (test_transfer.TransferTests.test_https_only) ... ok
test_no_downgrade (test_transfer.TransferTests.test_no_downgrade) ... ok
test_oversize (test_transfer.TransferTests.test_oversize) ... ok
test_pause (test_transfer.TransferTests.test_pause) ... ok
test_rate_eta (test_transfer.TransferTests.test_rate_eta) ... ok
test_rate_warmup (test_transfer.TransferTests.test_rate_warmup) ... ok
test_resume (test_transfer.TransferTests.test_resume) ... ok
test_server_ignores_range (test_transfer.TransferTests.test_server_ignores_range) ... ok
test_truncated (test_transfer.TransferTests.test_truncated) ... ok

----------------------------------------------------------------------
Ran 58 tests in 1.609s

OK

```

## Browser test summary
```json
{
  "frontend_errors": [],
  "hud_controls": "setup/settings/escape/send/progress passed",
  "website_empty_release": "passed",
  "website_release_fixture": "passed",
  "website_api_failure": "passed",
  "website_mobile_no_overflow": "passed",
  "hud_mobile_no_overflow": "passed"
}
```
