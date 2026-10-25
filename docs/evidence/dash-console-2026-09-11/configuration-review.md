# Native stdin configuration adjustment

The first target reached actual dash's $ prompt, then input.c::stdin_tee tried
sh_pipe before reaching its EINVAL fallback. UART truthfully reports neither
canonical TTY nor seekable file semantics. Do not fake either property or libc
pipe success. Explicit AETHER_NATIVE_NO_TEE returns EINVAL from stdin_tee, selecting
upstream preadfd's existing one-byte fallback. This avoids consuming future child
stdin and does not implement shell pipelines. All buffering/flush, parser and
wait code remain upstream. No new imports are permitted. Compare original,
patched-disabled and enabled objects using the previously pinned headers/tools;
retain upstream source/license and native source/config hashes. Add a legacy-tee
negative target. The console-only pre-fork request allowance becomes64 (from16)
to cover byte-at-a-time command input and existing startup metadata requests;
old profiles keep16. No kernel quota changes. The test input is14 script bytes
plus one child byte per session, stdout24 and default stderr prompt2.
