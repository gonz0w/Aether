# Retained oracle preflight correction

Initial producer-trace preflight failed only at cancellation offset ordering.
The checker required terminal_start > prompt_end, where prompt_end is the first
byte after the prompt. The real terminal starts exactly at prompt_end, directly
after the last prompt byte. Correct condition is terminal_start >= prompt_end.
The complete prompt remains required, along with all phase1 child terminals before
it, exact parent stop143, five reclaims and no command2. No native predicate or
input changed. Initial oracle, pin and failure receipts are in oracle-initial/.
Corrected oracle is repinned; preflight2 and the eventual fresh local trace check
are required. This is a checker boundary correction, not a native rerun or failure.
