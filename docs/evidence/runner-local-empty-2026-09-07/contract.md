# UL-059 empty-output prerequisite: implementation contract

Recorded before implementation, 2026-09-07. Prioritize UL-059 then UL-067 producer
work; pause OpenZFS worker profiling. This is not help/version acceptance or a
consumer bundle. Aether-userland owns CLI policy and independent adoption.

The opt-in command fixture runs only a parent and backend per generation, twice.
The owner accepts exactly two generation-bound closes, checks input `abcdef`
unchanged and output empty by backend readback, checks stale backend handles,
requires parent normal status zero, and reclaims both workers and channel ends.
No child launch/collection or file read/write request is legal in this profile.
Early exit cannot substitute for explicit closes. Four total native reclaims are
required; the default connections profile still requires six. A build-selected
`native-runner-local` test oracle is not a syscall or consumer-selected authority.
The unchanged envelope includes an unused child image; it is never admitted.
Infrastructure launch validation probes are distinct from runner child requests.

Forbidden: accepting an unexpected request, stale/duplicate close, omitted close,
wrong terminal status, partial-generation cleanup or use of the four-reclaim
oracle to silently relax default profiles. No new memory, concurrency or object
quota; no new unsafe boundary, dependency, release pin or sibling change.

Select full command-runner target suite, inherited-launch and connections
regressions, host/Zig/offline checks. Add exact controls for omitted close,
unexpected launch, stale reference, wrong status, premature completion, and
legacy gate rejection. Freeze implementation inputs during target qualification;
retain every attempt. Update NATIVE-COMMAND-IO, workflow inventory, ROADMAP and
STATE. Existing C uses its two-space migration style; no whole-file formatting.
New Rust uses rustfmt 1.98.0 edition 2024; Zig uses 0.16.0 formatting.

Separate stdout/stderr, text delivery failures, owner review and immutable
consumer handoff remain subsequent UL-059 work. UL-067 needs its own child roles
and admission contract; this witness does not complete either story.
