# Retained build-driver correction

The initial extraction compiled all runtime/application, memory and six public
fork/wait/rebind objects and passed seven component controls. The driver then
assumed the link output was the last argv entry; accepted links put wrapper flags
after -o output. Lookup raised StopIteration before any link or native run.
The original driver/pins/incomplete report and receipts are in initial-attempt/.
The corrected driver selects the explicit -o value in a fresh private build root.
No runtime source change or failed native attempt was involved.

The first standalone bundle rebuilt both executables but renamed the application
helper source to helper.c. The parent matched; helper equality failed on .symtab/
.strtab only (STT_FILE changed from serial-session-helper.c to helper.c). Source
and executable payload sections matched. The corrected candidate preserves the
original source basename and uses a fresh bundle/rebuild output. Initial driver,
seal, recipe and receipts are in bundle-initial/; the input and output directories
were retained as build-root bundle-initial/ and standalone-rebuild-initial/.
No native failure or code-semantic change occurred.

The basename-preserving candidate rebuild passed whole-ELF equality. A source
review then added exact file-set and symlink-directory rejection before builder
imports/commands so unlisted include inputs cannot enter the build. Its previous
passing candidate seal/driver/receipts are retained in bundle-v1/ and build-root
bundle-v1/ plus standalone-rebuild-v1/. The final candidate rebuild uses the
strengthened builder; unchanged ELF bytes reuse the fresh native qualification.
