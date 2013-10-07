# yum install  python3-devel
# yum install  rpm-build

Name:           sharada_braille_writer
Version:        2.0
Release:        0%{?dist}
Epoch:          1
Summary:        Sharada braille writer is a six key braille writer

Group:          Applications/Editors
License:        GPLv3+
URL:            https://codeload.github.com/Nalin-x-Linux/sbw/zip/sharada_braille_writer-2.0.zip
Source0:        https://codeload.github.com/Nalin-x-Linux/sbw/zip/sharada_braille_writer-2.0.zip

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

%install
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/pyshared/sbw_2_0/
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/applications/
mkdir -p $RPM_BUILD_ROOT/%{python3_sitelib}/
mkdir -p $RPM_BUILD_ROOT/%{_bindir}/

cp -r data $RPM_BUILD_ROOT/%{_datadir}/pyshared/sbw_2_0/
cp -r ui $RPM_BUILD_ROOT/%{_datadir}/pyshared/sbw_2_0/
cp -r sbw_2_0 $RPM_BUILD_ROOT/%{python3_sitelib}/
cp sharada-braille-writer-2.0.desktop $RPM_BUILD_ROOT/%{_datadir}/applications/
cp sharada-braille-writer-2.0 $RPM_BUILD_ROOT/%{_bindir}/

#abbreviations.txt should be editable for user
chmod -R 777 $RPM_BUILD_ROOT/%{_datadir}/pyshared/sbw_2_0/data/


%files
%defattr(-,root,root,-)
%{_datadir}/pyshared/sbw_2_0/*
%{python3_sitelib}/sbw_2_0/*
%{_datadir}/applications/*
%{_bindir}/*





%clean
rm -rf $RPM_BUILD_ROOT
