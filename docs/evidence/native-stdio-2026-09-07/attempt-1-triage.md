# Attempt 1 — build integration failure

No target case ran. The callback compilation selected the installed public
features.h before musl's private src/include/features.h, so hidden declarations
were unavailable. The failed recipe, source snapshot, commands and diagnostics
are retained. Correct include ordering while retaining system-header treatment;
do not edit upstream headers or erase visibility annotations. Before retry,
strengthen EIO/EINTR selection to test confirmed new-data progress within one
callback (22 input bytes, 3 prefix bytes, first11 confirmed then error).
