# Synthetic terminal receipt validator — 2026-09-06

Nine development gates pass in `out/checks/run-02k_q5um`. The new gate passes
nine named parameterized Rust tests and detects two separately compiled omission
controls at their exact assertions. All four tested source files and the compiler
hash remain unchanged. The eight native consumer inputs and worker/builder inputs
still match decision 0077; its 120-case target witness is not reinterpreted as a
new native run. Evidence: `docs/evidence/terminal-receipt-validator-2026-09-06/`.

`host/` contains final copied source, compiler identity, commands, binaries and
logs for nine Rust tests plus two semantic controls. `validation/` retains the
nine-gate offline run. `preliminary/` preserves the earlier focused pass (its
wrapper did not yet record all four sources or aggregate result). `adoption/`
retains current review/process/planning records. No test/build failure occurred.

This is pure host logic; Adapter and Driver are unchanged. Resource retention,
actual raw syscall capture, native interruption and full NT-04–07 integration
remain unqualified. Synthetic inputs never substitute for native producer proof.
The unchanged-native-inputs record compares current bytes to decision 0077.
Native catalog counts remain 1527 historical outcomes in 40 bundles.
