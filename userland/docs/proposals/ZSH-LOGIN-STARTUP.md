# Persisted Zsh login startup

Owning work: [issue160](https://github.com/gonz0w/Aether/issues/160).
[Approved design](https://github.com/gonz0w/Aether/issues/160#issuecomment-6712891650)
and [decision](https://github.com/gonz0w/Aether/issues/160#issuecomment-6712921729).
The guarded QEMU pair passed: warm43.171s/61requests and cold29.340s/58requests,
228/127 once-only foreground PTY bytes. Warm actual absence/BEEP-on/create/write/
read and cold automatic login/RCS/BEEP-off startup passed with the exact persisted
16-byte file, returned prompts, normal exit/export/MODE0/two reclaims/halt/PASS
and known original-host cleanup. Separate result review and delivery are recorded
in the owning issue; this is scoped startup qualification, not general login/R1.

## Selected consumer

The closed `native_zsh_login_startup` composition requires the existing complete
home-redirection/operator/file-exec profile and its matched C provider. Both roles
publish exactly `zsh`, `-d`, `-il`, `+m` and TERM=vt100, LC_ALL=C, HOME=/home,
PWD=/. Actual cwd remains root. GLOBALRCS is off; login and RCS are on. The
existing prompt, machine protocol, diagnostics and older profiles are unchanged.

Rust alone retains HOME15 namespace custody. Replace the old note only within
this composition with `/home/.zprofile` (15 bytes, basename9), containing exactly
`setopt no_beep;` followed by LF (16 bytes). The admitted parent alone may perform
one exclusive Create and one1..16-byte offset-zero Write, with actual0077 mask
and effective0600. Existing AEFP0006 opcode12 carries path length15 and unchanged
64-byte padded body/receipt fields. Reserved7, ACCESS8 and GETCWD9 remain exact.
No child startup-file authority or namespace grant follows from HOME/path text.

## Startup and failure rules

Warm automatic startup performs actual lookup against held HOME. Only canonical
remote ENOENT returns truthful absence while retaining the live FILE phase and
capacity. Unexpected existing input must be closed/contained before publication
or interpretation. Preserve original error/unknown/close facts; never replay an
uncertain effect. Other RC, compiled and logout paths reject locally without
poisoning the admitted session. Unsupported stat stays unsupported; no fake
access/stat success, compiled loading or general RC discovery is selected.

Cold bootstrap checks actual type, size16, exact bytes, EOF, post-stat and close
before startup. Upstream Zsh then opens and automatically parses the validated
file, through actual descriptor duplication, shared offset, scalar reads, EOF
and final-alias close. Known final-close reply delivery remains necessary for
healthy completion. The selected upstream build has USE_LSEEK disabled and uses
one-byte source reads; its temporary8192-byte heap input buffer is restored/freed.
No explicit cold operator source/setopt command may manufacture the result.

## Bounded witness and delivery

The approved warm228-byte workload checks mask077, BEEP initially on,
HOME=/home/PWD=/, successful creation/write and data-only readback with the same
positive parent PID and returned prompts. Cold127-byte workload checks actual
login/RCS on, GLOBALRCS off and BEEP off before clean exit. It makes no cross-boot
PID identity claim. Warm exact9 mutations and cold exact0 use the exact stopped
writer disk. Both require normal parent/engine, unused sealed-helper close,
export/MODE0/two reclaims/halt/PASS and known original-host cleanup.

Only this extra closed profile may use the existing81920-byte Owner RX cap.
Runtime/workspace4096 each, mapped/usable stack12288/12280, backing128 pages,
app/helper384 and engine2048 loader pages,96requests/9mutations and all existing
ticks/host/input/capture limits remain fixed. Fresh affected fits and linked
reader inspection precede images; unchanged engine/helper evidence needs exact
input/flag/byte applicability. Any required-bound failure stops for replan.

Focused checks, separate review, actual paired success and required protected CI
qualify only this development checkpoint while141 remains open. Authentication,
general files/RC paths, packages, indefinite sessions, general memory peaks and
assembled R1 acceptance remain outside scope.
