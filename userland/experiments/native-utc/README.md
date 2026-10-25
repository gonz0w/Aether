# Private shared UTC runtime

Aether-userland owns calendar interpretation and shared UTC establishment. This
opt-in variant consumes the sealed maintained service-runtime v2 and Aether's
bounded raw q35/TCG RTC observation (operation0x28011). Existing SDK delivery,
monotonic waits and grants remain unchanged. There is no daemon or adjustment API.

Call `aether_runtime_init()`, then explicitly select
`aether_utc_establish(AETHER_UTC_Q35_RTC_UNAUTHENTICATED)` from the initial thread
before creating application helpers. This policy interprets the emulated RTC as
UTC; it does not authenticate the source. The current native two-owner fixture's
initial IDs1/2 are supported; other startup profiles require explicit intake.
Temporary EAGAIN is reported for the caller to handle within its startup budget;
all failed establishment attempts leave UTC unavailable. A successful anchor is
immutable for that address-space lifetime. Later establishment returns EALREADY.

BCD/binary and12h/24h modes, explicit century, Gregorian dates1970–9999, source
metadata/reserved bytes, running/battery/update flags and signed arithmetic are
checked. Leap-second60 is unsupported. Unknown century is not guessed. One
shared seconds/monotonic anchor is release-published and acquire-read by helpers.
Every successful read validates its live held native thread grant through an
elapsed-clock observation. No native authority is inferred from calendar policy.

`clock_gettime(CLOCK_REALTIME)`, `time()` and `gettimeofday()` use the estimate.
Errors set errno and preserve outputs; successful calls preserve errno. The
pinned upstream time/gettimeofday bodies ignore clock-read failures, so this
variant supplies checked original wrappers. Non-null timezone output is ENOTSUP;
null timeval is EINVAL. All pointers are valid in-process borrows, not a kernel
pointer-validation API. Pure conversion/read/lifecycle functions return positive
errno without changing errno. Unestablished/closed reads return ENODATA.

Calendar source quantization is one second, with at most2ms read bracket
uncertainty. The estimate anchors the observed whole second at the bracket's end
and advances using monotonic time. Nanosecond fields describe that projection,
not nanosecond accuracy. Source offset, subsequent elapsed drift and source trust
are unmeasured. No physical RTC, synchronization, adjustment, cross-core accuracy,
realtime absolute sleep/condition support or persistence acceptance is claimed.

After application helpers join, call `aether_utc_close()` before
`aether_runtime_finish()`. Close rejects live application helpers (EBUSY), is
initial-thread-only, and permanently makes UTC unavailable. No reset/reuse API.

Build offline from the corrected sealed v3 elapsed packet:

```sh
python3 -B experiments/native-utc/build.py \
  --delivery build/sdk-deliveries/native-service-runtime-2026-10-06-v3 \
  --output build/my-utc-runtime
```

Use the variant archive **instead of** the elapsed v3 archive; force it whole-archive
before the same guarded base libc and crt objects. The builder verifies294 base
members, exact tool/helper pins, copies source and replaces only real_time.o while
adding calendar/UTC/checked-wrapper objects. Receipts bind all sources, the exact
clock transformation, flags, commands and archive. Outputs must be fresh under
build/. Preserve musl notices and BSD2 originals. Builder plain streams and exits
match the existing internal service builder: help/version0, usage2, failures1.

[Qualification and handoff](../../docs/evidence/native-utc-2026-10-06/README.md)
records actual native source tests, minimum/current rebuilds, Gregorian oracle and
failure attempts. Aether must still rebuild/check actual OpenZFS timestamp bodies:
upstream gethrestime/gethrestime_sec/getlrtime ignore gettimeofday errors and the
nanosecond conversion needs a separate signed-overflow boundary. The libc wrappers
alone cannot make those callers safe. Actual engine/pool timestamps, persistence,
owner acceptance and wider SESSION remain separate work.


[Corrected-base qualification](../../docs/evidence/reaper-utc-2026-10-06/README.md)
uses the new elapsed v3 seal after the confirmed detached reaper/list-lock cycle.
The maintained builder rejects the old elapsed v2 seal; immutable old packets
retain their own historical recipes. UTC provider/calendar/wrapper behavior is
unchanged. Fresh normal/leap/source-policy cases and ordered detached overlap
qualify this archive composition. Aether's earlier UTC-v2 intake checked actual
engine timestamp bodies, but corrected v3 requires new owner intake/reuse before
persistence. Wider SESSION remains separate.
