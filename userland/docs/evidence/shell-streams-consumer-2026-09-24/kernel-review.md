# Kernel artifact investigation and narrower reuse claim

The planned whole-file comparison failed for all105 kernel ELFs. Its failure and
kernel-comparison.json remain unchanged. A sample inspection found identical load
segments, with differences in five nonallocated debug sections. Build roots differ
in length, consistent with changed debug paths/offsets; no claim of identical full
ELFs is permitted. The follow-up compares all105 archived pairs, not just a sample.

Before follow-up acceptance, require exact ELF identity/entry, all program headers,
PT_LOAD payload hashes and memory sizes/flags/addresses, and every nondebug section's
contents/properties. Any changed section must be nonallocated .debug_* data. All
runtime sources except the three previously declared capacity/harness paths already
match the prior consumer. This supports scoped prior runtime evidence; it does not
establish byte-reproducible full files or rerun prior898 native cases.

The dependent cleanup command launched despite the failed acceptance precheck
because the shell command list did not stop at that failure. Its archive/readback
and unchanged-original checks completed before removing the generated suite/cache;
all1773 files remain in the verified archive. No acceptance existed then. Both
failed accept logs and this sequencing error are retained. Investigation consumes
verified archive bytes; no evidence is lost, and no failed native run was removed.
Future dependent commands in this turn are separate checked invocations.

This review supersedes only the whole-file equality requirement after investigation.
Native105/host110 and all11 exact control checks remain mandatory. No native source
change or native rerun. Independent review and full SESSION/M3/R1 remain pending.
