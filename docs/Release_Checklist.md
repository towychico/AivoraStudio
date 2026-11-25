# Release checklist

Aivora Studio has a demonstrated macOS release build. Use this checklist when publishing a distribution rather than treating a research benchmark as release certification.

- [ ] Pin the validated SiberUI version and registry; configure credentials via local or CI secrets only.
- [ ] Commit lockfiles produced by successful npm and Cargo builds; record compiler versions and build hashes.
- [ ] Run the engine tests, parity gate, production frontend build and CI matrix on macOS, Windows and Linux.
- [ ] Verify offline use, syntax highlighting, worker loading, error states, input limits and stale result handling on each target.
- [ ] Confirm textarea build isolation and rerun same-host Python/Rust benchmarks if claiming a speedup.
- [ ] Measure installer sizes, test installation/uninstallation, sign/notarize as appropriate and publish target-specific artifacts with checksums.
- [ ] Review Tauri capabilities, CSP, dependencies, vulnerability reports and OS trust boundaries. Do not ship registry secrets or private source examples.
- [ ] Review license, dataset redistribution rights and third-party notices; set project license only with author approval.
- [ ] Publish release notes and record known limitations. Preserve evidence files separate from new benchmark outputs.
