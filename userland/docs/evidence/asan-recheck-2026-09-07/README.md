# ASan recheck after reported startup fix

Command: python3 -B experiments/command-runner/check-parser-extended.py.
The default address+undefined run still times out in controls after 30 seconds;
owned process cleanup is complete. No fallback, compiler pin change or successful
ASan qualification is inferred. Exact argv, tool/runtime/source hashes and raw
streams are retained here; binaries remain in build/parser-extended-x0ip2k2w.
This recheck does not establish what external fix was applied or why it failed
to affect this pinned invocation. UL-062 ASan coverage remains incomplete.
