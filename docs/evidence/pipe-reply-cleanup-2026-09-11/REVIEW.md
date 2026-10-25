# Scoped implementation review

This is the implementing agent's review, not independent owner or reader sign-off.

- Authority remains the authenticated parent connection. No client-supplied
  number can release holders; confirmed_terminal is called only after the native
  observer returns the expected terminal for that exact task handle.
- Unknown replies publish nothing. The private adapter's existing complete-record
  exchange must finish before its installation branch; channel EOF returns EIO.
  The negative path preserves both output sentinels, absent binding/FD state and
  the caller's original mask. The second call checks poison before any exchange.
- Empty request-route inspection occurs after terminal observation, preventing
  a live client from queuing retry/fork traffic after an earlier empty read.
- Closing the reply writer alone cannot retire a pipe with parent holders.
  Retirement after confirmed stop requires no holders and no pending request;
  the request was completely consumed, reply delivery ended at channel closure,
  and the stopped client cannot consume late bytes. No operation is replayed.
- Backend handle close replies must be complete and zero, then backend17 must be
  observed before its channel cleanup/reclaim. Parent writer closure is not
  repeated. The remaining parent route closes before reclaim. Any failure halts
  this bounded fixture instead of pretending that cleanup succeeded.
- Replacement uses the existing three process generations and fresh local pipe
  objects; it is not same-client pipe generation reuse. The native profile still
  requires six actual reclaims. No artificial child or resource-budget change.
- The malformed complete-reply control retains its explicit abort; healthy fork,
  transfer and EOF logic is otherwise unchanged. No new allocation, transport,
  service, lock, scheduler, unsafe block or dependency is introduced.

Source review found no additional change needed before the final suites. Those
runs keep runtime sources frozen. Missing silent-stall, abnormal in-flight child,
copy rollback, SIGPIPE and actual dash coverage stays explicit in STATE/reference.
