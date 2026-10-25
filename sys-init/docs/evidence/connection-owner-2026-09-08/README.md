# Paired-connection owner — 2026-09-08

BG-067 host component qualification. Eight owner tests cover partial acquisition,
confirmed transfer, exact keys, terminal retention, known cleanup retries,
unknown no-replay, stop acknowledgement and explicit backend EOF. Two private
omission controls detect forgotten first-pair ownership and repeated writer close.
This module is not wired into a native image. ABI9 integration, real terminal/close
semantics and composed code/stack measurement remain required. Previous producer
image replays do not qualify this component on Aether.

Initial host suite passes thirteen methods with fourteen named records; final
validation includes added known observation/stop error assertions. Sources,
commands/logs and final full checks are retained here. No native behavior, unsafe
site, released standard pin or sibling change is made. Source retention is evidence,
not another build input. sha256.json excludes only itself.

Final acceptance: all ten repository gates pass in run-4tcsgnrh with checked
sources unchanged. The Rust suite passes thirteen methods/fourteen named records,
including all eight connection-owner tests and two exact omission controls.
Seventeen prior native source/linker files and all released locks are unchanged;
`git diff --check` passes. This completes the host component, not BG-067 native
consumer acceptance. No fresh Aether run is claimed for the new owner.
