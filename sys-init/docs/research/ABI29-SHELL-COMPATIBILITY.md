# ABI29 shell/client compatibility — 2026-10-20 / BG-067

Update2026-10-21: [Decision0194](../decisions/0194-abi29-dispatch-core.md) consumes
separately sealed corrected v2 linked input and prepares matching startup/child-
wait core with actual Rust/C decoder interoperability. Boot parent7 is accepted;
the original incompatibility below is historical. No native shell or AF07 FD/path/
exec acceptance follows; full dispatcher/transport integration remains pending.


Update2026-10-21: the separately sealed29-member ABI29 client candidate now
proposes seven-domain identity and shell1/children2–4. The old-client arithmetic
analysis below remains historical. Current intake finds a concrete [boot-parent
mismatch](ABI29-BOOT-PARENT.md): the candidate excludes genuine owner PID7.
Corrected client/startup and full linked/runtime inputs remain required.


The current filesystem owner can activate one small native process. Reusing the
frozen interactive shell client is a different boundary. This source review
checks that blocker rather than assuming every dependency needs a new SDK.
[Observed sources and arithmetic](ABI29-SHELL-COMPATIBILITY.json) retain hashes;
these are research observations, never mutable build inputs or native witnesses.

Userland's current [session runtime](../../../userland/experiments/session-runtime/runtime.c)
`identity()` accepts only role0 or roles2..4, checks the actual memory grant for
that role/epoch, and requires `getpid() == epoch*6+role+1`. Participant parent PID
must equal `shell_generation*6+1`. Its waitpid adapter also decodes PID selectors
with division/remainder by6. Our frozen `session_children.rs` encodes the same
six-domain PID scheme; the startup directory adapter delegates only to old role0.

Aether's defined ABI29 profile has seven domains: engine0, process1..5 and owner6.
Its actual native getpid uses `generation*states.len+slot+1`. At generation1,
slot1 has PID9. The old client rejects role1 immediately; even with that check
removed, the honest role1 frame would predict PID8. Lying about the slot also
breaks the independent kernel memory-grant/parent/handle checks. No such bypass
is proposed. These expressions establish a source-level compatibility failure,
not an executed shell experiment.

A local slot-offset edit cannot repair both sides of this interface. Userland's
matched client build and sys-init's dispatcher identity/startup/wait/descriptor
adaptation must select the same explicit parent/child subset within process1..5,
nonwrapping generations, parent identity, memory/endpoint and directory ownership.
The small `p` process uses the kernel primitives directly and its native success
does not qualify this client protocol. No new shell-role mapping or ABI is selected
by this research.

[The next boot handoff](../FILESYSTEM-BOOT-HANDOFF.md) records that concrete
follow-on. Preserve old ABI24 artifacts and code. Do not patch the userland sibling,
fake PID/role labels or silently combine SDKs. This is a genuine matching-client
boundary, separate from the fifteen-lifetime limit and from persistent loading.
No generic broker, platform campaign or new runtime dependency is needed now.
