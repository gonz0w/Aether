# Native Terminal capacity study — 2026-09-07

Decision 0174 attempted the native generated-dependent Terminal binding and
found a concrete image-capacity blocker. The refined candidate retains the source
association in an exclusive session before capturing actual register returns.
Its linker-computed text/constant/GOT section is 11,680 bytes against the unchanged
8,192-byte bound; size-z and fat-LTO alternatives still exceed the bound. Across
two candidate snapshots, all 48 bounded links reject as expected. Assembly output
is build-only; no candidate was executed and no native Terminal claim is made.

A read-only check of current Aether confirms AENIN002/ABI 15 still has the same
8 KiB code and 4 KiB stack contract. The candidate root frame is 3,288 bytes before
caller/saved-register/nested frames, so stack compatibility also needs an actual
consumer witness. A larger native-C mapping is not an accepted init replacement.
This is a profile limit for this composition, not proof that every design needs
more memory or that the kernel is defective.

The candidate code was removed from maintained native files after retaining both
source snapshots, commands, diagnostics, maps and assembly. All thirteen maintained
native inputs match the previously qualified decision 0173 snapshot byte-for-byte.
No new native behavior, compiler option, image/stack limit, producer pin, shared
release pin, catalog entry or sibling repository change is adopted.

Native Terminal integration is blocked pending an Aether capacity/profile decision
or a reviewed architecture alternative. BG-061 captures local qualification and
`docs/INIT-CAPACITY-HANDOFF.md` gives the producer/consumer requirements. The handoff
has not been added to the sibling backlog. BG-057/BG-058 remain active; their native
integration step is paused at this boundary. Actual reclaim/Cleaned, sustained
retention and recovery remain separate. Independent review is not claimed.

All ten local gates pass in `run-5ulsg4iv` with unchanged checked inputs,
including 287 model tests and the existing 22 core tests/16 omission controls.
The restored native inputs are byte-identical to decision 0173; no new target
execution is claimed or needed for those exact bytes. Shared pins and the native
catalog are unchanged. The blocker is the unconsumed candidate's image capacity;
the validated implementation remains available. Full retained build diagnostics,
read-only producer review and the local handoff are sealed in this bundle.

candidate-1/2 preserve build-only proposals, with baseline/size-z/lto-size maps and diagnostics; candidate-2 also includes assembly. aether-review/ captures read-only producer-contract inputs. source-restoration.json records the exact maintained-source rollback to the qualified checkpoint. There is no successful candidate image or native run.
