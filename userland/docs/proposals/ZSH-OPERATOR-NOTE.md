# Persistent operator note

The [approved issue170 design](https://github.com/gonz0w/Aether/issues/170#issuecomment-6720480196)
adds parent-only exclusive creation of `/home/note` and one write of 1–256 bytes
at offset zero. The Rust Owner keeps filesystem custody and reserves real
close and shutdown credits. Its scratch note lifetime is separate from the
immutable startup profile. Child admission waits for scratch descriptors and
aliases to settle. Existing note reads can end early or at EOF.

The cold engine reopens the seeded HOME, startup profile and helper. It accepts
healthy zero mutations, create-only and create-plus-write. The latter two
require actual transaction ordering before successful export. Its existing
observation channel reports the final validated mutation count on clean exit.

The closed kernel selector `-Dnative-zsh-operator-note=true` requires the home
redirection operator composition and its matching envelope. The 88 KiB Owner
RX limit uses its existing 128 backing pages. Workload qualification uses
one unchanged seed followed by one save boot and one readback of the same
stopped disposable media. The save trial requires two logical mutations and
one helper exit with status 23. Readback requires zero logical mutations and
the same 256 bytes.

For focused engine checks run
`python3 -B userland/experiments/filesystem-service/check-home-cold-reopen.py --note-only --inputs /retained/filesystem-transport/inputs.json`.
The local fit selectors are `zsh-owner-fit.py --operator-note`,
`zsh-target-fit.py --operator-note`, and `zsh-engine-recover.py --cold-note`.
See [Zsh serial operation](../ZSH-SERIAL.md) for the command shape.
