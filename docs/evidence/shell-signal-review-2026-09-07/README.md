# Shell signal boundary source review

Documentation/source review only, 2026-09-07. No runtime implementation, new ABI,
consumer sign-off or full-dash delivery. The canonical proposed contract and
three-question simplicity review are in
[NATIVE-SHELL-STARTUP](../../NATIVE-SHELL-STARTUP.md#handler-boundary-review--2026-09-07).
STATE owns progress and ROADMAP owns remaining work.

[inputs.json](inputs.json) records exact original paths and SHA256 digests for
sixteen retained source/license files from dash 0.5.13.5, adapted musl 1.2.6 and
this dirty Aether working tree. These are review inputs, not a complete build
closure. Original third-party notices and COPYING/COPYRIGHT are preserved.
No sibling source was modified or executed.

Observed source paths:

- dash `src/trap.c`: setsignal installs onsig with flags zero and a full mask;
  onsig records USR1/SIGCHLD but may call onint for untrapped SIGINT.
- dash `src/error.c`, `src/system.h`: onint clears the mask and can reach
  exraise/longjmp. This invalidates an active-handler slot released only at return.
- musl `arch/x86_64/ksigaction.h`, `src/signal/sigaction.c` and adapted restore.s:
  libc supplies a restorer and translates through the existing native trap offset.
- Aether startup-adapter.h and transport.h: descriptor changes and partial
  request/reply exchange rely on the existing single-context/no-delivery scope.
- Aether native execution/dispatch: mask storage and normal CPU restoration exist;
  validated user signal-frame restoration and pending delivery do not.

The selected outcome is to prove checked user-stack frame entry/return before
exposing a custom setter. Exact frame layout and errors remain implementation
work. Treat all acceptance cases in the reference as planned, not passing.

Verification output is in [checks.log](checks.log). The host suite includes
workflow and the three offline release checks; the four-file simplicity snapshot
was checked separately. Source snapshot digests and changed-section local narrative links were
checked. The initial whole-roadmap link check failed on the pre-existing
`../../sys-init/.planning/backlog/captured/BG-061--qualify-expanded-init-capacity.md`
link; that target is absent. Its failed attempt remains in checks.log. Repair of
that older cross-repository reference is outside this signal review. No QEMU run was selected because no runtime, harness or build input was
changed. Earlier sealed evidence remains unchanged.
