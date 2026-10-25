# Scoped implementation review

Self-review only; independent owner/reviewer acceptance remains missing.

- Capability validation precedes arguments, input reads and output effects.
- Eight-byte input is snapshotted before every output byte is checked; IF=0 and
  owner-private mappings keep those checks valid until synchronous commit.
- Stack-local copies avoid partial-alias corruption. No pointer survives the call.
- One u64 per Execution is inherited in the common admission path; no allocation
  or shared mask table is introduced. Existing reset clears both contexts.
- Native Linux-numbered signal calls remain ENOSYS; actual pthread preflight
  regression verifies that the storage primitive cannot authorize creation.
- The nonzero-inheritance target uses the legacy create form. Descriptor forms
  share the same assignment and run older regressions with zero masks; nonzero
  masks on those two forms are not separately target-qualified.
- This is mask state, not asynchronous signal delivery or handler execution.
