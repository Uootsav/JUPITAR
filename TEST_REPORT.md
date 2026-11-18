# Actual validation - 0.3.0 standalone source preview

42 isolated tests passed in the Linux authoring sandbox. Python source syntax
checks passed. Tests cover original action boundaries and custom identity, plus
native command construction, environment isolation, session tokens, real local
HTTP transport with authentication, mocked downloads, checksum failure, missing
components, cancellation, low disk space and activation markers.

The HTTP test uses a fake local server, NOT the real AI engine. Download tests
use synthetic test bytes, NOT actual model weights. These do not establish AI
quality or end-to-end functionality.

NOT executed: Windows native compilation, GitHub workflow, PyInstaller bundle,
Inno installer, frozen smoke test, Windows job object, Windows GUI, microphone,
SAPI voices, actual model downloads, inference, screen capture, cleanup, Recycle
Bin, 16 GB performance, clean-machine install/uninstall or Store submission.
The sandbox has no Windows build toolchain/Wine and lacks Tk GUI support.
No EXE, MSIX, signing certificate, native binary or model is included in this ZIP.
Font download in the earlier authoring attempt returned HTTP 403; Windows build
fetches Rajdhani and its original license and fails if that download fails.

The Windows workflow contains a frozen smoke test but it has not run here.
No GitHub repository, build, release, Store action or payment was performed.

## Test output
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

----------------------------------------------------------------------
Ran 42 tests in 2.318s

OK

```
