# Makefile budujący rpm-a w całości w katalogu /tmp/<tempdir>
#  
# Seweryn Walentynowicz <S.Walentynowicz@walor.torun.pl>
# 2020.12.05	initial release

PACKAGE = re2c
VERSION = 0.13.5
RELEASE = 9

distdir = $(PACKAGE)-$(VERSION)
top_srcdir = .

HAVE_RPMBUILD = yes
RPMBUILD = rpmbuild

RPM = rpm

SRPM_DEFINE_COMMON = --define "build_src_rpm 1"
DEBUG_RPM = _without_debug
RPM_DEFINE_COMMON = --define "$(DEBUG_RPM) 1"
RPM_DEFINE_RPM =

RPM_SPEC_DIR = rpm/spec
RPM_SOURCES_DIR = rpm/sources

.PHONY: pkg srpm rpm rpm-local srpm-common rpm-common

pkg: rpm

srpm:
	$(MAKE) $(AM_MAKEFLAGS) pkg="${PACKAGE}" \
	def='${SRPM_DEFINE_COMMON}' srpm-common

rpm: srpm
	$(MAKE) $(AM_MAKEFLAGS) pkg="${PACKAGE}" \
	def='${RPM_DEFINE_COMMON} ${RPM_DEFINE_RPM}' rpm-common



rpm-local:
	@(if test "${HAVE_RPMBUILD}" = "no"; then \
                echo -e "\n" \
        "*** Required util ${RPMBUILD} missing.  Please install the\n" \
        "*** package for your distribution which provides ${RPMBUILD},\n" \
        "*** re-run configure, and try again.\n"; \
                exit 1; \
        fi; \
	mkdir -p $(rpmbuild)/TMP && \
	mkdir -p $(rpmbuild)/BUILD && \
	mkdir -p $(rpmbuild)/RPMS && \
	mkdir -p $(rpmbuild)/SRPMS && \
	mkdir -p $(rpmbuild)/SPECS && \
	cp ${RPM_SPEC_DIR}/$(rpmspec) $(rpmbuild)/SPECS && \
	mkdir -p $(rpmbuild)/SOURCES && \
	cp ${RPM_SOURCES_DIR}/$(distdir).tar.gz $(rpmbuild)/SOURCES)

srpm-common:
	@(dist=`$(RPM) --eval %{?dist}`; \
	rpmpkg=$(pkg)-$(VERSION)-$(RELEASE)$$dist*src.rpm; \
	rpmspec=$(pkg).spec; \
	rpmbuild=`mktemp -t -d $(PACKAGE)-build-$$USER-XXXXXXXX`; \
	$(MAKE) $(AM_MAKEFLAGS) \
		rpmbuild="$$rpmbuild" \
		rpmspec="$$rpmspec" \
		rpm-local || exit 1; \
	LANG=C $(RPMBUILD) \
		--define "_tmppath $$rpmbuild/TMP" \
		--define "_topdir $$rpmbuild" \
		$(def) -bs $$rpmbuild/SPECS/$$rpmspec || exit 1; \
	cp $$rpmbuild/SRPMS/$$rpmpkg . || exit 1; \
	rm -R $$rpmbuild)

rpm-common:
	@(dist=`$(RPM) --eval %{?dist}`; \
	rpmpkg=$(pkg)-$(VERSION)-$(RELEASE)$$dist*src.rpm; \
	rpmspec=$(pkg).spec; \
	rpmbuild=`mktemp -t -d $(PACKAGE)-build-$$USER-XXXXXXXX`; \
	$(MAKE) $(AM_MAKEFLAGS) \
		rpmbuild="$$rpmbuild" \
		rpmspec="$$rpmspec" \
		rpm-local || exit 1; \
	LANG=C ${RPMBUILD} \
		--define "_tmppath $$rpmbuild/TMP" \
		--define "_topdir $$rpmbuild" \
		$(def) --rebuild $$rpmpkg || exit 1; \
	cp $$rpmbuild/RPMS/*/* . || exit 1; \
	rm -R $$rpmbuild)
