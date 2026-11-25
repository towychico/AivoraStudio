# Validation and benchmark protocol

## Evidence record

The Python reference was run on Linux x86_64 (Python 3.13.5); the team ran native and GUI benchmarks on macOS 15.7.4 ARM64. The reported terminal outputs are transcribed in `../results/macos_native_reported.json` and `macos_gui_reported.csv/json`. They are not newly executed by the documentation author. The first Rust run passed parity on 450 pairs and reported a 369,312-byte CLI. The repeat timing summary is 88 µs median, 199 µs p95 and 301 µs p99. The full repeat-run JSON was not supplied; do not fill its missing metrics from the first run.

## Repeatable protocol

1. Install toolchains; build with `cargo build --release --manifest-path engine/Cargo.toml`. Run unit tests and the parity command described in the README. The parity gate requires no input errors, max feature error ≤ 1e-9, probability error ≤ 1e-8 and zero class disagreements. A pass does not establish the exact maximum error unless the log is retained.
2. Run `python benchmarks/reference_benchmark.py` and `python benchmarks/benchmark.py` on the same device. Record CPU model, OS, architecture, toolchain versions and release flags. The script measures 450 test pairs, integer-microsecond engine timings, wall-clock batch time and ten short CLI launch/comparison trials. The benchmark uses the same corpus for parity. The first run lacked sampled CLI RSS/CPU; do not infer these values.
3. Run `node benchmarks/build_variants.mjs`. Verify the textarea Vite build does not contain Monaco chunks. Both GUI variants use the same native engine; build paths are in the README.
4. Install psutil in an isolated environment. Run `gui_benchmark.py` with the two executable paths. Default five launches per variant alternate order; 20 ms polling and two-second stabilization. Record readiness, sampled peak process-tree RSS, cumulative CPU and executable bytes. All ten reported runs reached readiness. This is not a guaranteed cold-start or full system memory measurement.
5. Measure comparable installer formats separately. The macOS evidence refers to executables, not signed installers or full system footprint.

## Offline acceptance test

Disconnect Wi-Fi and Ethernet; launch the release application; wait for both editors and Python highlighting; paste/edit/copy code; compare example pairs; check expected result ranges; inspect network activity with OS tools; record OS, device, build identity, tool and result. Repeat on every target platform. Do not mark this as passed until the observation is recorded. The benchmark readiness marker alone does not establish this result.

## Scientific interpretation

F1 and the historical F1-loss criterion pass; accuracy narrowly misses the target. Native parity and executable footprint are established on macOS. Deployment feasibility is supported; full conjunctive hypothesis acceptance requires all original criteria, including offline and target-platform observations. Cross-host Python/Rust timing is descriptive only. The included CI workflow and build targets are not evidence of completed Windows/Linux runtime validation.
