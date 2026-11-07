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
