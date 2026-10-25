# UL-007/081/082 real TLS relink review

User request: relink shell with real TLS and verify acceptance by Aether's existing
ELF parser. Aether's fresh intake rejects stage81 because old runtime TLS was
omitted with runtime.c; missing PT_TLS was not checked in generic link evidence.

Plan before code: restore an initialized volatile C17 thread-local four-byte
canary in the opt-in native fork module, checked at initial startup and before
native fork; validate again after pinned copy_rebind before child greeting/ready.
No canary reset, dummy ELF header, loader weakening, old runtime, new native grant,
owner policy, source ledger or public protocol. Existing failure contracts -EIO/
startup143 and direct fork116/child114 remain. Default bindings stay unchanged.

Authority/lifetime: TLS is CRT-initialized and copied/rebased by existing native
copy/pinned musl sequence. Canary is a diagnostic invariant, never a grant or proof
of correct native scheduling/TLS in this host qualification. Parent state must
remain private when child corrupts TLS; child must reject corruption rather than
repair/reset it. No heap or additional boot/context; four bytes initialized TLS.

Tests: extend existing actual entry host tests (UBSan/strict C17/format), real host
fork child corruption and unchanged parent plus scripted post-rebind corruption.
Retain prior1008 stage cases/seven omissions/frame5847/default-libc78; add a
compiling omission that bypasses canary validation. Rebuild pinned dash32/CRT/libc/
public fork/rebind, check TLS symbol/real template bytes and FS-relative native
access disassembly. Pin/copy exact current Aether native_elf.zig before executing
host Zig tests under unchanged default limits, positive corrected image, negative
old stage81 no-TLS plus malformed TLS/WX/mapping/size controls. No guest/native
execution, whole peak fit or independent owner/reader acceptance. Old candidate
and release/pin bytes remain unchanged; separately sealed relink handoff.

Tool/header/runtime pins retained from existing checker; new Zig tool and parser
hash pinned before consumption. Every run/command/outcome/cleanup retained,
minimum/current Python and quality gate before completion. BSD-2-Clause original;
parser copy preserves original bytes/terms with provenance and root license.
O/I/E, CE/CD/CA/C17/CP, TD/TC/TE and Distribution NC/PX/EV apply. No new user text,
wire, marker or default/error contract. Simpler alternative is the existing
four-byte canary design; choose it over another runtime/service or fake metadata.
Removes omitted-TLS blind spot; no obsolete compatibility path removed. Review by
implementation agent only; owner/reader and full UL/M3/R1 remain pending.

Actual results: both final interpreters pass1010/nine controls/frame5847/default78/
opt-in78 and seven actual parser tests, identical279568-byte ELF, default parser79/
128 pages. Initial C/link passed; Zig helper u32/u64 shadowing compile error retained.
Renamed helpers without changing parser, then added opt-in startup corruption/no
source regression and qualified final source. No suppression/waiver. Source review
confirms four-byte initialized TLS is read through native FS-relative accesses;
canary is never reset in production; injected native child corruption fails114.
Default bindings branch remains unchanged. Readiness/native fit/owner review not
established. Affected-owner consumption and reader review remain incomplete.
