# Final scope review

### Application-owner lifetime follow-on

The decision 0170 application owner is local to `check_native_application`: its
Reserved effect remains inspectable through application/replay checks, and the
owner's scope ends before the outer fixture disposal. This is the end of that
bounded probe, not effect retirement or permission to recreate an owner and replay.
Before executing generated obligations, keep the same application/journal owner
alive across execution, return capture, acknowledgment and any explicit retirement.
The next witness must inspect the retained obligation across those boundaries;
it must not copy a token out, drop its owner and substitute the synthetic ISSUED
entry. This lifetime extension is local BG-057/BG-058 work, not a kernel blocker.
