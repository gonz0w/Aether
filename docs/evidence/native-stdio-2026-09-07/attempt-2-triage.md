# Attempt 2 — probe include-order failure

The real callback compiled. The probe included unistd.h after internal syscall.h
had defined syscall as a macro, corrupting its public declaration. No target ran.
Retain all inputs and move unistd before the private stdio header; no upstream
source or header change and no warning suppression for original probe code.
