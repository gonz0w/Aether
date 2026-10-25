# SPDX-License-Identifier: BSD-2-Clause
PKGNAME := bytecount
PKGVERSION := 0.1
DISTNAME := bytecount.c
LOCAL_SOURCE = recipes/bytecount/bytecount.c
DISTFILE = $(DISTDIR)/$(DISTNAME)
SOURCE_METADATA = recipes/bytecount/source.kv
PHASE_SCRIPT = recipes/bytecount/phases.sh
