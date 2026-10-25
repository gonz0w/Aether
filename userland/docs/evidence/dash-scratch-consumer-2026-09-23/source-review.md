# Scoped native oracle review

Inspected restored frozen sources after verifying producer and SDK pins. This
review does not claim independent human sign-off or broader source migration.

- `user/native-connections/dispatch.rs`, before_fork: leak fixture requires one
  real writer for exact `/scratch/leak`, mode14 and backend binding3 before fork.
- `user/native-connections/exec_streams.rs`, replace_record: exact frozen table
  includes FD9 at bytes36–39 bound to scratch description3; all other unexpected
  aliases reject. Descriptions require the child's own reference and writer mode14.
  Exec planning retains that live description and removes the CLOEXEC FD10 alias.
- `scratch-restore.h`: validates entire table, counts, rights, sequence and child
  generation/reference before publication; absent descriptions must be empty.
  The unchanged helper's FD scan therefore cannot pass this positive merely due
  to an arbitrary unrelated leaked FD. Replacement normal-return cleanup closes
  every present alias. Final owner completion also requires closed file state.
- Redirection before_fork forwards actual A/B writes through the scratch owner;
  replacement validates reopened reader mode1 and removes only the child's old
  stdin holder. Lost-B, retained-stdin and skipped-helper controls distinguish
  wrong bytes/retention from success. Exact AB is owner readback, not a separately
  captured host stdout stream. This does not cover append.
- Denied-redirection dispatch requires child, no prior denial/exec, exact denied
  path/op, authenticated EACCES (-13), an otherwise empty reply and closed,
  unpoisoned file state. Denial must precede child stream activity. Thus an
  arbitrary subshell crash cannot substitute for the intended denied write.

Eleven terminal/reclaim expectations were pinned before execution, independently
compared after completed receipts, with PASS marker allowed only for result100.
Zero-reclaim controls are expected abort observations, not normal task teardown;
outer VM/process ownership still requires complete cleanup.
