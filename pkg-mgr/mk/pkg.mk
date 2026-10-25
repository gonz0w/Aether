# GNU Make 3.81+ host fixture; phase helpers use POSIX sh.
# Recipes and make overrides are trusted code. Output paths are fixture-scoped.
.DEFAULT_GOAL := package

# Cleanup must be a separate invocation, even with parallel make.
ifneq ($(filter clean init-root,$(MAKECMDGOALS)),)
ifneq ($(words $(MAKECMDGOALS)),1)
$(error clean and init-root must each be invoked alone)
endif
endif

PHASE_SCRIPT ?= mk/hello-phases.sh
DISTNAME ?= hello-local.txt

ROOT ?=

PKGNAME ?= hello-local
PREFIX ?= /usr/local

DISTDIR ?= $(ROOT)/distfiles
WRKDIR ?= $(ROOT)/work/$(PKGNAME)
STAGEDIR ?= $(ROOT)/stage/$(PKGNAME)
DESTDIR ?= $(STAGEDIR)
MANIFEST ?= $(ROOT)/manifests/$(PKGNAME).manifest
LOGDIR ?= $(ROOT)/logs/$(PKGNAME)

RECIPE ?= recipes/$(PKGNAME)/package.mk
VERIFY_METADATA ?= mk/verify-metadata.sh
SOURCE_METADATA ?= fixtures/metadata-boundary/source.kv
SOURCE_TARGET ?= $(LOCAL_SOURCE)
SNAPSHOT_METADATA ?= fixtures/metadata-boundary/snapshot.kv
SNAPSHOT_INDEX ?= fixtures/metadata-boundary/index.tsv
SNAPSHOT_SIGNATURE ?= fixtures/metadata-boundary/snapshot.minisig
SNAPSHOT_PUBLIC_KEY ?= fixtures/metadata-boundary/minisign.pub
MINISIGN ?= minisign
HASHED_MANIFEST ?= manifests/$(PKGNAME).hashed-manifest
BUILD_RECORD_INPUT ?= fixtures/metadata-boundary/build-input.kv
BUILD_RECORD ?= manifests/$(PKGNAME).build.kv
SBOM_RECORD ?= fixtures/metadata-boundary/advisory.spdx

include $(RECIPE)

.PHONY: clean fetch verify extract patch configure build test stage-install manifest package
.PHONY: verify-source-metadata verify-snapshot-metadata hashed-manifest build-record check-sbom

# Quote data, including apostrophes, before passing it through the shell.
quote = '$(subst ','"'"',$(1))'
PHASE_ENV = $(foreach key,ROOT PKGNAME PKGVERSION PREFIX DISTNAME DISTDIR DISTFILE WRKDIR STAGEDIR DESTDIR MANIFEST LOGDIR SOURCE_METADATA CC,$(key)=$(call quote,$($(key))))

.PHONY: init-root check-root
init-root:
	@$(PHASE_ENV) sh mk/check-root.sh init

check-root:
	@$(PHASE_ENV) sh mk/check-root.sh check

clean: check-root
	@rm -f $(call quote,$(DISTFILE)) $(call quote,$(MANIFEST))
	@rm -rf $(call quote,$(WRKDIR)) $(call quote,$(STAGEDIR)) $(call quote,$(LOGDIR))

fetch: check-root
	@$(PHASE_ENV) sh mk/phase.sh phase fetch start
	@$(PHASE_ENV) sh mk/phase.sh ensure-dirs
	@cp $(call quote,$(LOCAL_SOURCE)) $(call quote,$(DISTFILE))
	@$(PHASE_ENV) sh mk/phase.sh phase fetch complete

verify: fetch
	@$(PHASE_ENV) sh mk/phase.sh phase verify start
	@test $(call quote,$(FAIL_PHASE)) != 'verify' || { $(PHASE_ENV) sh mk/phase.sh phase verify failure; exit 1; }
	@sh $(call quote,$(VERIFY_METADATA)) verify-source $(call quote,$(SOURCE_METADATA)) $(call quote,$(DISTFILE)) || { $(PHASE_ENV) sh mk/phase.sh phase verify failure; exit 1; }
	@$(PHASE_ENV) sh mk/phase.sh phase verify complete

extract: verify
	@$(PHASE_ENV) sh mk/phase.sh phase extract start
	@$(PHASE_ENV) sh $(call quote,$(PHASE_SCRIPT)) extract || { $(PHASE_ENV) sh mk/phase.sh phase extract failure; exit 1; }
	@$(PHASE_ENV) sh mk/phase.sh phase extract complete

patch: extract
	@$(PHASE_ENV) sh mk/phase.sh phase patch start
	@$(PHASE_ENV) sh $(call quote,$(PHASE_SCRIPT)) patch || { $(PHASE_ENV) sh mk/phase.sh phase patch failure; exit 1; }
	@$(PHASE_ENV) sh mk/phase.sh phase patch complete

configure: patch
	@$(PHASE_ENV) sh mk/phase.sh phase configure start
	@$(PHASE_ENV) sh $(call quote,$(PHASE_SCRIPT)) configure || { $(PHASE_ENV) sh mk/phase.sh phase configure failure; exit 1; }
	@$(PHASE_ENV) sh mk/phase.sh phase configure complete

build: configure
	@$(PHASE_ENV) sh mk/phase.sh phase build start
	@test $(call quote,$(FAIL_PHASE)) != 'build' || { $(PHASE_ENV) sh mk/phase.sh phase build failure; exit 1; }
	@$(PHASE_ENV) sh $(call quote,$(PHASE_SCRIPT)) build || { $(PHASE_ENV) sh mk/phase.sh phase build failure; exit 1; }
	@$(PHASE_ENV) sh mk/phase.sh phase build complete

test: build
	@$(PHASE_ENV) sh mk/phase.sh phase test start
	@$(PHASE_ENV) sh $(call quote,$(PHASE_SCRIPT)) test || { $(PHASE_ENV) sh mk/phase.sh phase test failure; exit 1; }
	@$(PHASE_ENV) sh mk/phase.sh phase test complete

stage-install: test
	@$(PHASE_ENV) sh mk/phase.sh phase stage-install start
	@$(PHASE_ENV) sh $(call quote,$(PHASE_SCRIPT)) stage-install || { $(PHASE_ENV) sh mk/phase.sh phase stage-install failure; exit 1; }
	@$(PHASE_ENV) sh mk/phase.sh phase stage-install complete

manifest: stage-install
	@$(PHASE_ENV) sh mk/phase.sh phase manifest start
	@$(PHASE_ENV) sh mk/phase.sh manifest || { $(PHASE_ENV) sh mk/phase.sh phase manifest failure; exit 1; }
	@$(PHASE_ENV) sh mk/phase.sh phase manifest complete

package: manifest

verify-source-metadata:
	@sh $(call quote,$(VERIFY_METADATA)) verify-source $(call quote,$(SOURCE_METADATA)) $(call quote,$(SOURCE_TARGET))

verify-snapshot-metadata:
	@MINISIGN=$(call quote,$(MINISIGN)) sh $(call quote,$(VERIFY_METADATA)) verify-snapshot \
		$(call quote,$(SNAPSHOT_METADATA)) $(call quote,$(SNAPSHOT_INDEX)) $(call quote,$(SNAPSHOT_SIGNATURE)) $(call quote,$(SNAPSHOT_PUBLIC_KEY))

hashed-manifest:
	@mkdir -p $(call quote,$(dir $(HASHED_MANIFEST)))
	@sh $(call quote,$(VERIFY_METADATA)) manifest $(call quote,$(STAGEDIR)) $(call quote,$(HASHED_MANIFEST))

build-record:
	@mkdir -p $(call quote,$(dir $(BUILD_RECORD)))
	@sh $(call quote,$(VERIFY_METADATA)) build-record $(call quote,$(BUILD_RECORD_INPUT)) $(call quote,$(BUILD_RECORD))

check-sbom:
	@sh $(call quote,$(VERIFY_METADATA)) check-sbom $(call quote,$(SBOM_RECORD))

# Evidence currently uses repository-relative material references; ROOT must be
# beneath this checkout for these targets. Registration leaves world unchanged.
.PHONY: evidence register
evidence: manifest
	@$(PHASE_ENV) sh mk/package-evidence.sh record

register: evidence
	@$(PHASE_ENV) sh mk/package-evidence.sh register
