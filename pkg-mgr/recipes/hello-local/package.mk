# Local-only sample recipe for the private-root package fixture.

PKGNAME := hello-local
PKGVERSION := 0.1
LOCAL_SOURCE := fixtures/sources/hello-local/hello.txt
DISTFILE := $(DISTDIR)/hello-local.txt

# This fixture uses one checked-in input; the package path checks its copied
# bytes against SOURCE_METADATA before extraction.
