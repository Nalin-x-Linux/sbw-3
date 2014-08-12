###########################################################################
#    SBW - Sharada-Braille-Writer
#    Copyright (C) 2012-2014 Nalin.x.Linux GPL-3
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

# yum install  python3-devel
# yum install  rpm-build

Name:           sharada_braille_writer
Version:        2.2
Release:        0%{?dist}
Epoch:          1
Summary:        Sharada braille writer is a six key braille writer

Group:          Applications/Editors
License:        GPLv3+
URL:            https://codeload.github.com/Nalin-x-Linux/sbw/zip/sharada_braille_writer-2.2.zip
Source0:        https://codeload.github.com/Nalin-x-Linux/sbw/zip/sharada_braille_writer-2.2.zip

BuildArch:      noarch
Requires:       espeak 
Requires:       python3-gobject
Requires:       python3-enchant
Requires:	PackageKit-gtk3-module

%description
 Sharada braille writer is a six key approach to producing
 printmaterials. Letters f, d, s, j, k, l represent 1 2 3 4 5 6 of the
 braille dots respectively. By pressing "f" and "s" together will
 produce letter "k" and like.


%prep
%setup -q

%build
python3 setup.py build

%install
python3 setup.py install -O1 --skip-build --prefix=%{_prefix} --root=%{buildroot}

#abbreviations.txt should be editable for user
chmod -R 777 $RPM_BUILD_ROOT/%{_datadir}/pyshared/sbw2/data/


%files
%defattr(-,root,root,-)
%{_datadir}/pyshared/sbw2/*
%{python3_sitelib}/sbw2/*
%{_datadir}/applications/*
%{_bindir}/*
%{python3_sitelib}/sbw2-*
%{_datadir}/locale-langpack/es/LC_MESSAGES/*
%{_datadir}/locale-langpack/hi/LC_MESSAGES/*
%{_datadir}/locale-langpack/kn/LC_MESSAGES/*
%{_datadir}/locale-langpack/ml/LC_MESSAGES/*
%{_datadir}/locale-langpack/ta/LC_MESSAGES/*
