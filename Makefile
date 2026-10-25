# SPDX-License-Identifier: BSD-2-Clause
# Existing component suites; full system checks are milestone-only.
.PHONY: check-system check-kernel check-userland check-init check-packages

check-system: check-kernel check-userland check-init check-packages

check-kernel:
	zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global

check-userland:
	cd userland && python3 -B docs/quality/check.py

check-init:
	cd sys-init && python3 scripts/check-all.py --current

check-packages:
	cd pkg-mgr && sh tests/check.sh
