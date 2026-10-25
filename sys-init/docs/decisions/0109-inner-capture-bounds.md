# 0109 — Inner host/model capture bounds

BG-056 host harness change, 2026-09-06. Replace unlimited communicate/capture
buffers with a shared internal two-stream capture primitive. Bound combined
raw bytes to 4 MiB and elapsed worker time to 30 seconds through pipe drain and
exit. Preserve per-stream order, real nonzero exit status, normal text decoding
and universal-newline behavior. Overflow must never count as semantic success.

On exceptions kill the owned process group and reap the direct child. Preserve
bounded raw prefixes on timeout/overflow exceptions. Host capture failures emit
only diagnostic stderr and return 1; partial machine stdout must not be accepted.
Model capture failures retain the existing passed/error JSON shape, including
bounded prefix detail in the error string. New helper source hashes join each
successful report's existing source map. No CLI or success schema change.

Exercise real child success/nonzero, each overflow stream, exact combined limit,
concurrent output, early pipe closure, missing tool and interrupted capture.
Verify host integration rejects overflow without stdout success; run full gates.
No model/host runtime algorithm, native source, release pin or sibling change.
No new native witness is needed for this host tooling boundary. Inner workers
own new groups; abrupt outer termination and detached nested compiler cleanup
remain outside this scoped guarantee. Worker allocations before emission and
child artifacts are not bounded by the pipe cap. Record/API references and
independent review remain open. Evidence: docs/evidence/inner-capture-bounds-2026-09-06/README.md.

Validation: eight focused tests and all ten gates pass in
out/checks/run-sr4k1ikf. Model semantic results and host summary shape/count match
the prior run; all 24 checked native inputs remain unchanged. Both manuals lint
cleanly after correcting one retained STYLE finding. Real-child capture and
synthetic integration/interruption controls are distinguished in the evidence.
