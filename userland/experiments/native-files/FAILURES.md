# Descriptor reply and close failures (UL-042)

Seven native outcomes pass for the private descriptor layer. The
[test-only exchange wrapper](fd-failures.h) waits for a complete reply from the
real service, then discards or changes that reply before the descriptor layer
sees it. These are injected consumer-boundary failures during Aether execution,
not physical channel loss, service crashes or reconnection tests. No owner Rust
service, supervisor or sibling working tree is modified.

| Case | Witness |
| --- | --- |
| lost-open | Create completes remotely; discarded reply returns EIO without publishing a local descriptor/open-file record. Raw test-only lookup confirms the handle exists and a second create returns EEXIST. |
| lost-write | Write completes remotely; discarded reply returns EIO and leaves the local position unchanged. Raw test-only readback contains exactly `abc`. |
| malformed-close | Close consumes the remote handle; injected nonzero reply handle returns EIO and poisons the connection. Local descriptor/reference removal and remote EBADF are checked. |
| close-error | Destination close during dup2 consumes its remote handle, then its reply is replaced by EIO. The destination stays removed, source remains valid, and its temporary retained reference is released. |
| ignore-poison | Disable connection poisoning; the independent assertion rejects at client 195. |
| leak-retain | Omit dup2's temporary-reference release after failed close; rejects at client 193. |
| relax-reply | Skip the new operation-specific reply validation; malformed-close assertion rejects at client 189. |

Each successful fault-handling case checks exactly one injection and no later
facade exchange after poisoning. Open is refused; cases retaining a descriptor
also check refused read, duplicate and position changes, followed by local close
without transport reuse. Raw RPCs deliberately bypass the poisoned facade only
inside the test to independently inspect effects and clean up; they are not a
production recovery path. Final service/client exits are 17/29, replacement is
33, supervisor result is 100 with three reclaims. Controls require the exact
client status, supervisor 611/reclaimed 0 and profile-rejection panic, never a
timeout or generic boot error.

The new checks exposed a close-reply validation gap. The layer now validates
operation-specific result/handle/size fields before accepting a reply: opens
require a nonzero handle, zero result and bounded size; non-open operations
require zero handle/size; close requires zero result. Existing reserved-word,
transfer-count and transport checks remain. This is scoped validation, not a
complete malformed-response grammar or proof against a malicious service.

The closed-transport case from UL-041 remains a separate real endpoint-error
witness. No mutation is replayed here. In production an uncertain remote open or
close still requires connection/service lifecycle cleanup; local removal does
not prove remote reclamation. This experiment does not implement restart,
reconnection, cancellation, concurrent exec, signal masking or POSIX close/EINTR
semantics. Private negative-errno APIs remain separate from libc entry points.

Reproduce:

```sh
python3 experiments/native-files/check.py --aether ../aether \
  --sdk build/native-c-xhkdw6jv --fd-failures
```

[Retained evidence](../../docs/evidence/native-fd-failures-2026-09-05/summary.json)
includes all seven cases and twelve fresh descriptor/read-only/writable
regressions against the same captured kernel sources. The first incomplete build
failed under Werror because per-case images leave some static API functions
unused; explicit test-only references preserve the warning policy. Final source,
SDK/tool, ELF/envelope/ISO identities, commands and serial logs are retained.

Next, UL-043 audits and implements a bounded libc adapter witness for the tested
file operations, with explicit unsupported paths and unchanged native process/
TTY gates. Broader ownership review and the shared PD proposal remain pending.
