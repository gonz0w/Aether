# Native payload hashing — 2026-09-07

Decision 0128 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 41 tests. Four new tests cover empty/binary raw
digest compatibility and <=64 KiB read requests; FIFO/directory/link/oversize
rejection before open; controlled replacement/growth and descriptor closure;
and exact-limit behavior/read-error cleanup. The boundary control lowers the
constant; oversized-file control uses a sparse file. Both focused attempts pass.

`python3 scripts/check-all.py` passes all ten gates in run-wl7174yz. Exact commands
and source hashes are in validation/results.json. Four manual lint/render commands
pass. No failed tests or renderer attempts occurred. Digest code is self-contained
and uses existing POSIX file primitives without new external dependencies.

The supplied checkout root now follows audit digest calls; files are checked for
ordinary type, symlink components, descriptor device/inode and post-read metadata.
Hash memory is chunk-bounded and file bytes capped at 64 MiB. Semantic JSON/serial/
envelope reads still reopen inputs with their previous reader. No atomic snapshot,
blocked-I/O deadline, full receipt validation or current native qualification is
claimed. Those limits remain explicit follow-ons, not waived acceptance criteria.

Native audit stdout matches run-5_9vk5jd exactly; catalog and 24 tracked native
inputs are unchanged. Released standard gates pass with unchanged pins; RC1 is
unpublished. No sibling or retained evidence mutation. Independent reader/HTML
visual/narrow-layout publication review remains pending. Source copies/diff record
this slice within the pre-existing dirty checkout.
