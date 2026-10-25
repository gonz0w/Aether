# UL-005 imported SDK consumer slice

Independently verify the known descriptor/target pins, descriptor table hashes,
exact blob set and payload against the previously reviewed 235-file input map.
Compare imported and recovered records/payloads, modes, sizes and regular types.
No package mutation or sibling code changes. Then rerun the existing strlen
consumer link controls from a private copy of the actual imported SDK; record
package/descriptor identity as a consumer input. No native code execution.

Reuse pinned tools, strict C17, explicit sysroot/headers/libc and process helper
30-second cleanup/output bounds. All failed attempts retained. SDK-05 link-only
subset, not full startup/adapter/helper closure. SDK-07/08 remain open. Quality,
format and whitespace checks; independent review remains separate. Foundations
O/I/E and quality TD/TE/CC/CP govern this bounded no-new-dependency experiment.
