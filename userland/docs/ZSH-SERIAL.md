# Type into serial Zsh

This developer procedure uses the retained local SDK, private preparation tools
and a disposable OpenZFS disk. Run it from the private Aether workspace.
The guest supports Zsh builtins and the existing admitted helper path. The
typing window ends at guest tick24000 from boot, leaving bounded shutdown time.
The supervisor has a 330-second workload limit and a 360-second total limit.
Startup must reach a real prompt within60 host seconds.

## Prepare a fresh session

Use the current operator inputs and the accepted provisioning writer inputs.
The local `tools/zsh-witness.py --file-exec` and `--operator` commands consume
the sealed input directory, manifest hash, seal hash and a current frozen source
map with its hash. Each prints its generated image directory. Obtain the required
separate image review before `tools/zsh_run.py` prepares a run.

Run the reviewed writer once with the existing `--file-exec prepare` and
`--file-exec run` commands. Its execution record must show normal export and
complete cleanup. Keep that exact stopped disk for the cold session.

Prepare the operator proposal with the actual image and writer record identities:

```sh
python3 -B tools/zsh_run.py --operator-manual prepare \
  OPERATOR_IMAGE_DIRECTORY IMAGE_REVIEW_SHA \
  WRITER_EXECUTION_JSON WRITER_EXECUTION_SHA
```

The command prints the exact proposal path and hash. Obtain its separate review
and bind the existing owner approval to that one-use proposal. Preparation
verifies the stopped disk identity and hash; a failed or already-used disk is
rejected. Use a freshly provisioned disposable disk for another session.

## Attach and type

Keep the supervisor running in the first terminal:

```sh
python3 -B tools/zsh_run.py --operator-manual run \
  PROPOSAL_JSON PROPOSAL_SHA PEER_REVIEW_JSON PEER_REVIEW_SHA DECISION_JSON
```

It prints an exact local `env ... /usr/bin/screen -r PID.NAME` command.
Paste that whole command into a second terminal. It attaches to the single
private serial display. Wait for `AETHER-ZSH>` and type, for example:

```zsh
x=hello
print -r -- "$$ $x"
```

Pause, then print the values again. Zsh keeps the same process and variable.
Screen host command escapes are disabled, so keys belong to the guest console.

The selected interactive checkpoint checks Delete (byte127) in Zsh's default
Emacs editing mode. Type a wrong character, press Delete, then complete the
command. To cancel an unfinished line, press Ctrl-C before Enter. The expected
result is a fresh prompt and status130; the unfinished command must not run.
Issue156 qualified this combined behavior with automated input through the
foreground PTY: status130, the same shell PID and saved value, followed by the
persisted helper and clean exit. This does not claim a human typing trial or
general job control.

The admitted persisted helper can run once during this session:

```zsh
(exec -c /home/probe)
print -r -- $?
```

It returns23, and Zsh must return to its prompt. The helper has no arguments.
Its path refers to the exact sealed executable already held by the Rust Owner;
typing another path does not grant execution authority.

Finish before the typing deadline with:

```zsh
exit 0
```

Wait for the supervisor's result. Clean completion requires actual normal parent
and engine exit, unused-helper closure or the checked helper completion,
filesystem export, terminal mode restoration, reclamation and kernel halt.

## If the session stops

A lost terminal, early detach, abnormal exit or expired bound aborts the run.
The supervisor stops its original guest and Screen processes and records their
cleanup. It never signals a client found by PID lookup. A timeout or interrupted
run does not prove filesystem export; discard that disposable disk and prepare
fresh media. Preserve the compact failure result if cleanup is unknown.

## First persistent home note

Issue158 selects a separate home-redirection image for one bounded write and
cold readback. Its Rust Owner retains filesystem custody and admits only the
parent's exclusive creation of `/home/note`, followed by one write of at most16
bytes at offset zero. The sealed helper and terminfo remain protected.

The qualification uses fresh disposable media and managed foreground input:

```zsh
umask 077; setopt noclobber; umask
print -rn -- $'AETHER-HOME-158\n' > /home/note; print -r -- "WRITE $?"
IFS= read -r note < /home/note; print -r -- "NOTE $? $$ $note"
exit 0
```

Require `077`, `WRITE 0`, then `NOTE 0 PID AETHER-HOME-158`, with a returned
prompt after each command. A successful stopped writer disk may be used once
by the matching cold reader, which reads the same note using marker `COLD` and
exits cleanly. Issue158 qualified this fixed write/read/export/cold-readback pair
in QEMU using automated input through the foreground PTY. Both boots returned
to the prompt and completed clean shutdown; this does not claim human typing
or general home-file operations.

Use private `zsh-target-fit.py --home-redirection`, the writer/reader variants
of `zsh-owner-fit.py` and `zsh-witness.py`, and the reviewed exact-nine writer /
exact-zero cold engines. Run preparation uses `zsh_run.py --home-redirection`
and `--home-redirection-reader`; the reader requires the exact successful writer
execution record and hash. Image and run-proposal review precede execution.
The same operator deadlines and original-process cleanup requirements apply.
An existing note or failed/unknown mutation aborts this once-only experiment;
prepare fresh media rather than reopen or replay it. General overwrite/truncate,
packages, authentication and indefinite sessions retain separate gates.

## Persisted login startup

Issue160 adds a separate closed login-startup profile. Both provisioning and cold
roles start real `zsh -d -il +m` with HOME=/home. The current directory and PWD
remain `/`. The prompt remains `AETHER-ZSH> `. This is login-shell startup;
account authentication is still outside this checkpoint.

The sole admitted home configuration file is `/home/.zprofile`. The warm role
starts with that file absent and permits its exclusive creation under umask0077,
then one16-byte write of `setopt no_beep;` followed by LF. The cold Rust Owner
checks the persisted file before Zsh opens and sources it automatically, before
the first prompt. No operator `source` command is needed. Other startup files
and arbitrary filesystem paths are not admitted by this profile.

The bounded qualification uses the exact approved warm/cold commands linked in
[issue160](https://github.com/gonz0w/Aether/issues/160#issuecomment-6712891650).
It checks the real BEEP preference before creation and after cold startup,
returned prompts and clean exit/export. The automated QEMU pair passed:
warm43.171s/61requests and cold29.340s/58requests, with228/127 known foreground
PTY bytes and known cleanup. Cold LOGIN0/PROFILE0 confirmed automatic startup
and the saved preference, without an operator source command. See the owning
issue for review and delivery. This does not claim human typing or authentication.
Use the existing finite session and failure procedure above; a failed or uncertain
disk is never replayed.

## Home working directory

Issue162 adds a separate cold home-CWD profile. After automatic login startup,
the admitted parent can use ordinary `cd /home`, `pwd -P` and a relative read of
`.zprofile`, then return with `cd /`. Rust keeps directory custody and obtains
actual physical paths. HOME/PWD text alone never changes the current directory.
Other relative paths stay unadmitted; reading `.zprofile` from `/` returns a
permission error and leaves the shell's directory unchanged.

This profile deliberately blocks fork before native effects; it does not add
child CWD inheritance. Use the older operator profiles for their qualified helper
workload. The home-CWD qualification is one fresh160 provisioning writer followed
by one new cold session on that exact stopped disk. See the
[scope and fixed workload](proposals/ZSH-HOME-CWD.md). The automated QEMU pair
passed: writer 39.834s/61 requests and cold 26.895s/83 requests, with228/216 known
foreground PTY bytes. The `/home` and `/` physical paths, relative read status0 and root-relative
read status1 passed with returned prompts, clean export and known cleanup. This is a
fixed workload result; it does not claim a human typing or general CWD trial.
The same finite session/failure procedure applies.

## Home working directory and a persisted command

The scoped [164 checkpoint](proposals/ZSH-HOME-CWD-EXEC.md) combines automatic
persisted login startup, real parent home navigation and one external command.
Use the managed `--home-cwd-exec` reader with its reviewed inputs and one unchanged
fresh `--login-startup` writer. Keep the exact stopped writer disk and follow the
same artifact/proposal review and cleanup procedure above. This managed profile
has no manual selector; keep the existing operator mode for its accepted scope.

The fixed regression changes to `/home`, runs `(pwd -P; exec -c /home/probe)`,
then prints the collected status and parent PWD before `pwd -P` and `exit 0`.
It passed with status23, the same parent PID9, `/home` before/in/after the child,
returned prompts, normal export and complete cleanup. The child can observe its
inherited directory; child directory changes and profile reads remain denied.
Zsh's pwd can use cached state, so the qualification also uses the selected linked
GETCWD route and actual C/Rust context/dispatch controls. This does not qualify
arbitrary commands, child navigation, authentication or assembled R1.

## Two sequential persisted commands

The scoped [166 checkpoint](proposals/ZSH-REPEAT-EXEC.md) uses managed
`--repeat-exec` reader inputs with one unchanged fresh `--login-startup` writer
and its exact stopped disk. Follow the same artifact/proposal review and bounded
cleanup procedure above. This reader keeps the existing numeric limits and has
no manual selector.

The fixed regression enters `/home`, executes `(exec -c /home/probe)`, prints
FIRST status/PID/PWD, executes the same helper again, then prints SECOND status/
PID/PWD and physical path before exit. Both commands returned23 and a fresh
prompt in the same PID9/home session, with complete first-child cleanup before
the second. Final export, MODE restoration, four reclaims and host cleanup pass.
The second executable is fully revalidated through Rust-held HOME, once only;
third/nested/concurrent children and child profile reads remain denied. This
qualifies the fixed two-command session, not arbitrary command counts, utilities,
initial HOME startup, authentication or assembledR1.

## Home operator session

The scoped [168 composition](proposals/ZSH-OPERATOR-LOGIN.md) passed its fixed
foreground qualification.
It uses `zsh-witness.py --operator-login` inputs and one unchanged fresh
`--login-startup` writer, then that exact stopped disk. Follow the same separate
image/proposal review and original-process cleanup procedure above.

Use `zsh_run.py --operator-login-manual prepare` with the reader image/review and
writer execution/hash, then its matching `run` command and decision identities.
Attach using the exact printed Screen command. The guest must start in `/home`
and read its persisted `.zprofile`; shell state stays in the same process.
You may exit without running the helper, or run the existing helper sequentially:

```zsh
(exec -c /home/probe)
print -r -- $?
```

Each admitted run returns23 and a prompt after full cleanup. Repeat only within
the current resource/time bounds. Namespace requests and native generations are
finite; a pre-effect resource refusal must preserve the parent and its shutdown
credits. The generation ceiling15 does not promise15 runs. Builtins and existing
root/home navigation/profile reads keep their scoped behavior. Other executables,
child directory changes/profile opens and general file mutations are outside this
profile. Exit with `exit 0` before the unchanged typing deadline and wait for
normal export, MODE restoration, complete reclaims/halt and known host cleanup.

The managed `--operator-login` frontend qualifies the same guest with fixed
foreground input and three helper runs. It is separate from manual input; it
must not be described as a human typing trial. Existing65-second idle evidence
is reused explicitly; the new composition checks a brief5-second state-retention
interval. The corrected trial passed with PID9/home, the saved preference, three status23/
prompt cycles and normal export/MODE0/five reclaims/halt and known host cleanup.
Use `[[ ! -o beep ]]` to query the saved setting; the optional options associative
parameter module is excluded from this build. The first diagnostic failure and
its discarded media remain recorded in issue168. Broader R1 remains open.

## Save a short note

For the maintained cold boot from supplied offline inputs, use the
[sys-init persistent Zsh recipe](../../sys-init/docs/PERSISTENT-ZSH.md).

The scoped [issue170 composition](proposals/ZSH-OPERATOR-NOTE.md) uses
`zsh-witness.py --operator-note`. On an approved disposable lineage, use
`zsh_run.py --operator-note-manual prepare` with the image review and exact
stopped seed identities. Use the matching `run` command and attach with the
printed Screen command. Open an unused `/home/note` exclusively and write
1–256 bytes with one builtin.

```zsh
setopt noclobber
text='a note for the next boot'
print -rn -- "$text" > /home/note
value=$(</home/note)
print -r -- "$value"
```

Exit with `exit 0` to export the pool. To cold boot the saved note, use
`--operator-note-manual-readback` with the same reviewed image and the exact
successful stopped save identities. Each edge has its own single-use claim.
Run `value=$(</home/note)` and `print -r -- "$value"` at the new prompt.
Existing notes are read-only. Repeating the creation fails and preserves their
bytes. Zsh command substitution strips trailing
newlines from its returned value.

The managed `--operator-note-save` and `--operator-note-readback` trial passed
with fixed 256-byte input. The manual selectors have focused host coverage.
