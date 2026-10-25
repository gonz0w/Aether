PKGNAME := zlib
PKGVERSION := 1.3.2
DISTNAME := zlib-1.3.2.tar.gz
LOCAL_SOURCE = $(SOURCE_ARCHIVE)
DISTFILE = $(DISTDIR)/$(DISTNAME)
SOURCE_METADATA = recipes/zlib/source.kv
PHASE_SCRIPT = recipes/zlib/phases.sh
