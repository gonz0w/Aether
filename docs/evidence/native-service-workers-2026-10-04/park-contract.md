# Actual full-owner wait/wake composition (before fixture)

The 82-record context-pointer list must work when all children are parked, not
only cooperatively yielding. Add separate unchanged-runtime witnesses: all 82
service children (two on the small peer) park on one owner-local aligned atomic
word using existing indefinite compare-wait. Observe each exact ID's waiting bit
through the existing auxiliary result; then release and require counted wake to
return exactly 82/two, followed by status/clear-TID/retirement/quota restoration.
Also stop/reclaim while the complete set is parked and replace its generation.
Existing capability, pointer validation and wait pins remain; no syscall change.
The bare FS cookies and 256 KiB requested stacks do not establish production TCB
or actual stack high-water. Keep main capacity/control fixtures unchanged, add a
separate helper/recipe, bind every actual source/tool/header/command, retain any
failure and use the unchanged watchdog. Temporary context-pointer lists never
escape the synchronous wait/wake operation. No sibling or release pin change.
