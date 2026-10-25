See the preimplementation Native pthread creation preflight contract in
final/sources.tar.gz: docs/NATIVE-C.md. This snapshot predates qualification;
post-run result text is separate. The change must reject missing signal setup
before allocating or publishing a child, preserve caller state and report ENOSYS.
