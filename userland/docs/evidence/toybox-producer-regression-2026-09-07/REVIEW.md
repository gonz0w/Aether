# UL-067 captured producer regression review

Scope: run the complete unmodified captured command-runner suite as the remaining
broad producer regression gate. The snapshot is the locally qualified finalizer
revision; newer close-policy work is outside it. The producer recipe is trusted
code whose hash is part of the captured inventory, not declarative package data.
Foundations O/I/E and local CP/TD/TE apply. No ABI, native source or oracle change.

The new driver copies the pinned SDK into a private build directory, validates
all tool identities and the existing private Rust wrapper, and excludes ambient
environment configuration. The original producer runs its existing command/guest
limits inside the owned outer process group with a1800-second suite ceiling.
A timeout, nonzero result, unresolved cleanup, source drift, ambiguous output or
anything other than213 passing cases cannot qualify. Process cleanup is checked
before interpreting the final producer receipt. Child per-command entries retain
the producer's original argv/log schema; they are not relabeled as owned-runner
records. The outer receipt records environment and process-group cleanup.

Codex source review checks SDK mapping, source/tool hash gates, fixed profile,
output selection and original semantic positive/negative oracles. No benchmark or
peak-resource claim follows from elapsed duration. Retain the generated receipt,
raw logs, source inventory and failed attempts. Old source and evidence remain
unchanged. Independent reader/maintainer review is pending. Final test outcome is
recorded separately after execution completes. CAT-06 close-policy acceptance,
newer-revision regressions, actual shell, package and TTY gates remain separate.
