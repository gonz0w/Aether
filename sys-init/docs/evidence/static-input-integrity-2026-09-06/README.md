# Static input integrity evidence

Decision 0114 requires ordinary files for selected sources and JSON records,
rejects symlink components within the supplied root and compares pre-open lstat
with opened-descriptor type/device/inode. Opens are nonblocking and use optional
O_NOFOLLOW reinforcement. Reads are bounded and descriptor size/mtime are checked
after reading. Source-boundary text and hashes derive from the same read bytes.

Both JSON records are captured before parsing/tools, parsed from those bytes,
and safely reread before success. Byte changes reject even when the JSON remains
valid and semantic boundary fields are unchanged. No new result fields or tool
arguments were introduced; maintained settings and inventory bytes are unchanged.

All 27 focused static tests pass. Five new cases exercise the exact file-byte
limit, oversize/directory/parent-symlink rejection, a real FIFO without a writer
in a two-second bounded child, replacement between inspection and open, growth
during a read, and whitespace-only changes to each JSON record. Replacement and
growth are controlled injection points around real filesystem operations. The
metadata test stubs tool/boundary/source work to isolate final byte comparison;
it does not assert a complete hostile-race defense. Existing malformed-record
fixtures now provide both records before validation, matching capture order.

All ten repository gates pass in out/checks/run-rzjuf8cz, retained in validation/.
Manual lint and 78/60-column/HTML generation pass. Only documentation wrapping
was adjusted after the aggregate run. No failed test/check attempt occurred.
Current maintained records and all 24 native inputs match retained identities.
No native implementation, compiler options, sibling, published pin, vendored
release or historical evidence changed. No fresh native execution is claimed.
Independent technical/reader review and installed-target lookup remain pending.

The supplied root is the anchor; ancestors above it are outside component
checking. Metadata and byte comparisons do not supply an atomic filesystem
snapshot, detect changes restored before comparison or close every hostile
parent-directory replacement race. Identical final record bytes are accepted.
Nonblocking open avoids the tested FIFO-open hang but does not guarantee a
deadline for regular-file filesystem I/O. Tool executable/dependency closure
remains separate. BG-056 retains those limits and the remaining record/API
families; released standards pins stay fixed.
