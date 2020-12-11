%global pkgdir        %{_datadir}/%{name}
%global cfgdir        %{_sysconfdir}/%{name}
%global docdir        %{?_pkgdocdir}%{!?_pkgdocdir:%{_docdir}/%{name}-%{version}}
%global httpconfdir   %{_sysconfdir}/httpd/conf.d

Summary:    Web-based issue tracking system
Name:       mantis
Version:    1.2.19
Release:    11sw1%{?dist}
License:    GPLv2+
URL:        http://www.mantisbt.org/
BuildArch:  noarch
Source0:    http://downloads.sourceforge.net/mantisbt/mantisbt-%{version}.tar.gz
Source1:    mantis-README.Fedora

# Admin is supposed to edit /etc/mantis/config_inc.php
Patch0:     mantis-1.2.19-install_no_write_config.patch
Patch1:     mantis-1.2.12-no_example_com.patch
# We secure admin/ with httpd directives
Patch2:     mantis-1.2.4-do_not_warn_on_admin_directory.patch
Patch3:     mantis-1.2.12-use_systems_phpmailer.patch
# set environment variable to find config_inc.php in /etc/mantis
Patch4:     mantis-1.2.14-set_env_on_scripts.patch

Patch5:     mantis-1.2.19-fix_default_view_doc_threshold.patch

# EPEL5 only, remove when dropping support, along with install
# and clean sections

Requires:   php
Requires:   php-mbstring
Requires:   mantis-config
#Requires:   php-adodb
Requires:   php-soap
Requires:   php-PHPMailer


%package config-httpd
Summary:    Mantis configuration for Apache httpd
Source10:   mantis-httpd.conf
Provides:   mantis-config = httpd
Requires:   mantis = %{version}-%{release}
Requires:   %{httpconfdir}
Requires:   mod_ssl


%description
Mantis is a free popular web-based issue tracking system.
It is written in the PHP scripting language and works with MySQL, MS SQL,
and PostgreSQL databases and a web server.
Almost any web browser should be able to function as a client. 

Documentation can be found in: %{docdir}

When the package has finished installing, you will need to perform some
additional configuration steps; these are described in:
%{docdir}/README.Fedora


%description config-httpd
Mantis is a web-based issue tracking system.
This package contains configuration-files for Apache httpd 2.


%prep
%setup -q -n mantisbt-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

cp %{SOURCE1} ./doc/README.Fedora
rm -rf packages docbook tests


%build


%install
rm -rf "${RPM_BUILD_ROOT}"

%{__install} -d -m755 ${RPM_BUILD_ROOT}%{pkgdir}
%{__install} -d -m755 ${RPM_BUILD_ROOT}%{cfgdir}

tar cf - . | tar xf - -C ${RPM_BUILD_ROOT}%{pkgdir}

# Remove bundled libraries
# adodb
# rm -rf ${RPM_BUILD_ROOT}%{pkgdir}/core/adodb

# phpmailer
rm -rf ${RPM_BUILD_ROOT}%{pkgdir}/library/phpmailer

# NuSOAP
rm -rf ${RPM_BUILD_ROOT}%{pkgdir}/library/nusoap



find ${RPM_BUILD_ROOT} \( \
    -name '*.orig' \
    -o -name '*.#.*' \
    -o -name '.cvsignore' \
    -o -name '.htaccess' \
    -o -name '.gitignore' \
    \) -print0 | xargs -0 rm -f

## Do not rename; the *existence* of this file will be checked to
## determine if mantis is offline
mv ${RPM_BUILD_ROOT}%{pkgdir}/mantis_offline.php.sample ${RPM_BUILD_ROOT}%{cfgdir}/
mv ${RPM_BUILD_ROOT}%{pkgdir}/config_inc.php.sample     ${RPM_BUILD_ROOT}%{cfgdir}/config_inc.php

chmod a+x ${RPM_BUILD_ROOT}%{pkgdir}/scripts/{checkin,send_emails}.php


for i in $(find ${RPM_BUILD_ROOT} -type f -regex '.*\.\(php\|txt\|gif\|png\|css\|htm\|dtd\|xsl\|sql\|js\|bak\|xml\|zip\)$' -perm +0111); do
    case $i in
        (*.php)
            if ! sed '1p;d' "$i" | grep -q '^#!'; then
               chmod a-x "$i"
            elif sed '1p;d' "$i" | grep -q '/usr/local/bin/php'; then
               sed -i -e '1s!/usr/local/bin/php!/usr/bin/php!' "$i"
            fi
            ;;
        (*.bak)        rm -f "$i";;
        (*)        chmod a-x "$i";;
    esac
done

# Dangling symlink: when /etc/mantis/mantis_offline.php is present mantis is put offline
ln -s ../../..%{cfgdir}/mantis_offline.php ${RPM_BUILD_ROOT}%{pkgdir}/mantis_offline.php

%{__install} -D -p -m644 %{SOURCE10} ${RPM_BUILD_ROOT}%{httpconfdir}/mantis.conf

# Remove doc dir
rm -rf ${RPM_BUILD_ROOT}%{pkgdir}/doc



%files
%{pkgdir}
%dir %{cfgdir}
%config(noreplace) %{cfgdir}/*
%doc doc/{LICENSE,CREDITS,CUSTOMIZATION,README.Fedora}

%files config-httpd
%config(noreplace) %{httpconfdir}/*


%changelog
* Thu Dec 10 2020 Seweryn Walentynowicz <Seweryn.Walenyunowicz@frakoterm.pl> - 1.2.19-11sw1
- remove php_flag from httpd config if not PHP5 detected
- defaults to on for address rewriting to https

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.19-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.19-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.19-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.19-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.19-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.19-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.19-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.19-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jul 23 2015 Gianluca Sforna <giallu@gmail.com> - 1.2.19-3
- apply upstream patch for CVE-2015-5059 (#1237199)

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.19-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jan 26 2015 Gianluca Sforna <giallu@gmail.com> - 1.2.19-1
- new upstream release
- rebase patch
- fix CVE-2014-9571, CVE-2014-9572, CVE-2014-9573 (#1183595)

* Tue Dec  9 2014 Gianluca Sforna <giallu@gmail.com> - 1.2.18-1
- new upstream release
- drop upstreamed patches
- fix several security issues, full list in upstream changelog:
  http://www.mantisbt.org/bugs/changelog_page.php?version_id=191

* Fri Nov 14 2014 Gianluca Sforna <giallu@gmail.com> - 1.2.17-4
- fix CVE-2014-7146, CVE-2014-8598 (#1162046)
- fix CVE-2014-8554 (#1159295)

* Fri Oct 03 2014 Gianluca Sforna <giallu@gmail.com> - 1.2.17-3
- fix CVE-2014-6387 (#1141310)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.17-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Mar 04 2014 Gianluca Sforna <giallu@gmail.com> - 1.2.17-1
- new upstream release
- fix CVE-2014-2238 (#1071460)
- remove upstreamed patch

* Mon Oct 28 2013 Gianluca Sforna <giallu@gmail.com> - 1.2.15-3
- fix CVE-2013-4460 (#1022246)

* Fri Jul 26 2013 Ville Skyttä <ville.skytta@iki.fi> - 1.2.15-2
- Honor %%{_pkgdocdir} where available.

* Tue Apr 16 2013 Gianluca Sforna <giallu@gmail.com> - 1.2.15-1
- new upstream release
- fix CVE-2013-1930 (#948971)
- fix CVE-2013-1931 (#948975)
- drop upstreamed patch

* Fri Mar 22 2013 Gianluca Sforna <giallu@gmail.com> - 1.2.14-1
- New upstream release
- require php-soap extension, drop patch
- set env variable for command line scripts (#902528)
- fix CVE-2013-1883 (#924340)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.12-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Dec 02 2012 Johan Cwiklinski <johan AT x-tnd DOT be> - 1.2.12-2
- Fix apache 2.4 configuration (bz #871418)

* Thu Nov 15 2012 Gianluca Sforna <giallu@gmail.com> - 1.2.12-1
- New upstream release
- Rebase patches
- Fix CVE-2012-2691 (#830735)
- Fix CVE-2012-2692 (#830737)
- Fix CVE-2012-1118, CVE-2012-1119, CVE-2012-1120, CVE-2012-1121, CVE-2012-1122, CVE-2012-1123
  (#800665)
- Fix CVE-2012-5522 CVE-2012-5523 (#876371)

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Sep  7 2011 Gianluca Sforna <giallu@gmail.com> - 1.2.8-1
- New upstream release
- Fix several security issues CVE-2011-2938 (#731777)
- Fix CVE-2011-3356 CVE-2011-3357 CVE-2011-3358 CVE-2011-3578 (#735514)
- Rebase Patch0

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Dec 15 2010 Gianluca Sforna <giallu@gmail.com> - 1.2.4-1
- New upstream release
- Fix CVE-2010-4348, CVE-2010-4349, CVE-2010-4350 (#663299, #663230)

* Fri Oct  1 2010 Gianluca Sforna <giallu@gmail.com> - 1.2.3-1
- New upstream release
- Fix CVE-2010-3763 (#640746)
- Updated description (#638942)
- Rebase patches
- Changelog removed upstream

* Mon Sep 20 2010 Gianluca Sforna <giallu@gmail.com> - 1.1.8-4
- Fix CVE-2010-3070 using system's NuSOAP (#633011)
- Fix CVE-2010-2574 and CVE-2010-3303 (#633003 #634340)

* Sun Jan 17 2010 Gianluca Sforna <giallu gmail com> - 1.1.8-3
- Tweak summary
- Don't restart apache (#552943)

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jun  8 2009  Gianluca Sforna <giallu gmail com> - 1.1.8-1
- new upstream release

* Tue Apr 21 2009 Gianluca Sforna <giallu gmail com> - 1.1.7-1
- new upstream release

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Dec 28 2008 Sven Lankes <sven@lank.es> - 1.1.6-2
- add patch to suppress bogus warning during setup 
    (closes bz #437142)
- convert ChangeLog to UTF8
- remove .gitignore
- change mantis_offline.php-symlink to be relative

* Wed Dec 10 2008 Gianluca Sforna <giallu gmail com> - 1.1.6-1
- new upstream release

* Mon Nov 24 2008 Gianluca Sforna <giallu gmail com> - 1.1.5-1
- new upstream release

* Sun Oct 19 2008 Gianluca Sforna <giallu gmail com> - 1.1.4-1
- new upstream release

* Tue Oct 14 2008 Gianluca Sforna <giallu gmail com> - 1.1.3-1
- new upstream release
- drop upstreamed patch

* Sat Jul 19 2008 Gianluca Sforna <giallu gmail com> - 1.1.2-1
- new upstream release
- add patch for bugnotes notification

* Sat Jan 19 2008 Gianluca Sforna <giallu gmail com> - 1.1.1-1
- new upstream release
- Add more info in README.Fedora about configuration, upgrades
  and SELinux

* Sat Jan  5 2008 Gianluca Sforna <giallu gmail com> - 1.1.0-1
- new upstream release
- rediffed patches
- allow local usage out of the box
- remove .htaccess files
- revert using embedded adodb 
  see http://www.mantisbt.org/bugs/view.php?id=8256 for details
- improve description and README.Fedora
- Remove unneeded diffutils BR
- Updated License field

* Tue Jul  3 2007 Gianluca Sforna <giallu gmail com> - 1.0.8-1
- new upstream release
- add Require: php-adodb (and remove embedded one)
- remove duplicate docs

* Thu Apr  5 2007 Gianluca Sforna <giallu gmail com> - 1.0.7-1
- new upstream release
- drop upstreamed patch
- fix (most) rpmlint issues
- tweak Source0 URL
- remove config_inc.php symlink (config is now found via the MANTIS_CONFIG 
  environment variable)

* Tue Jan  9 2007 Gianluca Sforna <giallu gmail com> - 1.0.6-2
- Add some docs
- Add patch for BZ #219937
- Fix rpmlint messages for SRPM

* Thu Nov  2 2006 Gianluca Sforna <giallu gmail com> - 1.0.6-1
- updated to 1.0.6

* Tue Oct 10 2006 Gianluca Sforna <giallu gmail com> - 1.0.5-1
- updated to 1.0.5

* Sat May 20 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 1.0.3-1
- updated to 1.0.3 (SECURITY)

* Wed Mar  8 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 1.0.1-1
- updated to 1.0.1

* Sat Feb 18 2006 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 1.0.0-1
- updated to 1.0.0

* Fri Dec 23 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 1.0.0-0.1.rc4
- SECURITY: release 1.0.0rc4
- removed x-permission from most files
- rediffed

* Sat Jun 25 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 1.0.0
- updated to 1.0.0a3
- removed the part which created the psql-script; upstream has now a
  working PostgreSQL database creation script
- rediffed the -iis patch
- added patch to make upgrade functionionality partially working with
  PostgreSQL; this is not perfect as things like index creation will
  still fail

* Thu May 19 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.19.2-2
- use %%dist instead of %%disttag

* Mon Mar  7 2005 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0.19.2-1
- updated to 0.19.2
- rediffed patches
- removed dependency on php-mysql as it supports PostgreSQL also
- added inline-hack to generate a PostgreSQL database creation script

* Thu May 27 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.18.3-0.fdr.2
- ship doc/ in the program-directory instead of copying it into %%docdir
- modified shipped httpd configuration to disable admin/ directory
  explicitly and added some documentation there
- added noadmin patch to disable warning about existing admin/ directory;
  since this directory is disabled by httpd configuration
- lower restrictions on the required 'mantis-config' subpackage; use
  descriptive names as version instead of EVR
- restart 'httpd' after the upgrade
- preserve timestamps of the configuration files to avoid creation of
  .rpmnew files on every update

* Tue May 25 2004 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> - 0:0.18.3-0.fdr.0.1
- updated to 0.18.2
- rediffed the patches

* Fri Aug 15 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0:0.18.0-0.fdr.0.2.a4
- use generic download-address for Source0

* Thu Jun 19 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0:0.18.0-0.fdr.0.1.a4
- applied the Fedora naming standard

* Thu Jun 19 2003 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de> 0:0.18.0-0.fdr.0.a4.2
- Initial build.
