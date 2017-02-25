Name:           python
Version:        2.7.12
Release:        72
License:        Python-2.0
Summary:        The Python Programming Language
Url:            http://www.python.org
Group:          devel/python
Source0:        http://www.python.org/ftp/python/2.7.12/Python-2.7.12.tar.xz
Source1:        argparse.egg-info
Source2:	python.gcov
Patch1:         0001-Skip-mhlib-tests.patch
Patch2:         0001-Support-os-release-file-Modification-of-issue-17762-.patch
Patch3:		libffi-shared.diff
Patch4:		link-opt.diff
Patch5:		link-whole-archive.diff
Patch6:		lto-link-flags.diff
Patch7:     0001-Add-pybench-to-the-PROFILE_TASK-rule.patch
Patch8:		avx2-distutils.patch
Patch9:		load-avx2.patch

BuildRequires:  bzip2
BuildRequires:  db-dev
BuildRequires:  grep
BuildRequires:  bzip2-dev
BuildRequires:  zlib-dev
BuildRequires:  expat-dev
BuildRequires:  libffi-dev
BuildRequires:  ncurses-dev
BuildRequires:  gdbm-dev
BuildRequires:  readline-dev
BuildRequires:  openssl
BuildRequires:  openssl-dev
BuildRequires:  sqlite-autoconf
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  autoconf
BuildRequires:  procps-ng-bin
BuildRequires:  netbase
BuildRequires:  tk-dev
BuildRequires:  tcl-dev
BuildRequires:  pkgconfig(x11)
Requires: clr-python-timestamp
Requires: openblas
Requires: libgfortran-avx


%define python_configure_flags --with-threads --with-pymalloc --without-cxx-main  --with-signal-module --enable-ipv6=yes  ac_cv_header_bluetooth_bluetooth_h=no  ac_cv_header_bluetooth_h=no --with-system-expat  --with-system-ffi  --libdir=%{_prefix}/lib --with-computed-gotos --with-lto

%description
The Python Programming Language.

%package lib
License:        Python-2.0
Summary:        The Python Programming Language
Group:          devel/python

%description lib
The Python Programming Language.

%package core
License:        Python-2.0
Summary:        The Python Programming Language
Group:          devel/python
Provides:       python
Provides:       python-modules
Provides:       /bin/python

%description core
The Python Programming Language.

%package dev
License:        Python-2.0
Summary:        The Python Programming Language
Group:          devel
Requires:       python-lib
Requires:       python-core
Requires:	py
Requires:	pytest
Requires:	python-subunit


%description dev
The Python Programming Language.

%package doc
License:        Python-2.0
Summary:        The Python Programming Language
Group:          devel/python

%description doc
The Python Programming Language.

%package tcl
License:        Python-2.0
Summary:        The Python Programming Language
Group:          devel/python

%description tcl
The Python Programming Language.


%prep
%setup -q -n Python-%{version}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1

%build
flags="%{optflags}"
# Python fails to compile with PIE
export CFLAGS="${flags/-fPIE -pie}"
export CFLAGS="$CFLAGS -O3 -ffunction-sections -fno-semantic-interposition -fopt-info-vec -flto"
export CXXFLAGS="$CXXFLAGS -O3 -ffunction-sections -fno-semantic-interposition -fopt-info-vec"
export AR=gcc-ar
export RANLIB=gcc-ranlib


autoconf configure.ac > configure
chmod +x Python/makeopcodetargets.py

# use our own, faster, zlib
rm -r Modules/zlib || exit 1

%configure %python_configure_flags --enable-shared

make %{?_smp_mflags}

%install
%make_install

flags="%{optflags}"
# Python fails to compile with PIE
export CFLAGS="${flags/-fPIE -pie}"
export CFLAGS="$CFLAGS -O3 -ffunction-sections -fno-semantic-interposition -fopt-info-vec -fomit-frame-pointer -flto"
export CXXFLAGS="$CXXFLAGS -O3 -ffunction-sections -fno-semantic-interposition -fopt-info-vec -fomit-frame-pointer"
export AR=gcc-ar
export RANLIB=gcc-ranlib

cp %{SOURCE1} %{buildroot}/usr/lib/python2.7/
# Basic, non-multilib lib64 support
mkdir -p %{buildroot}/%{_libdir}
mv %{buildroot}/%{_prefix}/lib/libpython2.7.so* %{buildroot}/%{_libdir}
mkdir -p %{buildroot}/stash
cp -r %{buildroot}/%{_prefix}/lib %{buildroot}/stash

# The script recommends this change if installing python to /usr/bin
sed -i '1s@/usr/local/bin/python@/usr/bin/env python@' %{buildroot}%{_prefix}/lib/python2.7/cgi.py

# Build with PGO for perf improvement
make clean
%configure %python_configure_flags
make profile-opt %{?_smp_mflags}
%make_install

sed -i '1s@/usr/local/bin/python@/usr/bin/env python@' %{buildroot}%{_prefix}/lib/python2.7/cgi.py

rm -f `find %{buildroot}/usr/lib -name "*.pyo" `

mv %{buildroot}/stash/lib/python2.7/_sysconfigdata.py* %{buildroot}/%{_prefix}/lib/python2.7/
mv %{buildroot}/stash/lib/python2.7/config/* %{buildroot}/%{_prefix}/lib/python2.7/config/
rm -rf %{buildroot}/stash

%check
%define python_bin LD_LIBRARY_PATH=`pwd` ./python -Wd -3 -E -tt
%define python_test_args Lib/test/regrtest.py -v -x test_bsddb test_doctest test_gdb test_idle test_ioctl test_tcl test_tk test_ttk_guionly test_ttk_textonly test_smtplib

%python_bin %python_test_args ||:

# Copy the rest of the build for test
#rm -rf build-avx/build
#cp -r build/ pybuilddir.txt python Include build-avx/
#cd build-avx/
#%python_bin ../%python_test_args



%files lib
%{_libdir}/libpython2.7.so.1.0

%files core
%{_bindir}/2to3
%{_bindir}/idle
%{_bindir}/pydoc
%{_bindir}/python
%{_bindir}/python-config
%{_bindir}/python2
%{_bindir}/python2-config
%{_bindir}/python2.7
%{_bindir}/python2.7-config
%{_bindir}/smtpd.py
%{_includedir}/python2.7/pyconfig.h
%{_prefix}/lib/python2.7/*
%exclude /usr/lib/python2.7/test/test_tcl.py
%exclude /usr/lib/python2.7/test/test_tcl.pyc
%exclude /usr/lib/python2.7/lib-dynload/_tkinter.so
%exclude /usr/lib/python2.7/lib-dynload/_tkinter.so.avx2
%exclude /usr/lib/python2.7/lib-tk
%exclude /usr/lib/python2.7/test/test_tk.py
%exclude /usr/lib/python2.7/test/test_tk.pyc



%files dev
%{_includedir}/python2.7/*.h
%exclude %{_includedir}/python2.7/pyconfig.h
%{_libdir}/libpython2.7.so
%{_libdir}/pkgconfig/python-2.7.pc
%{_libdir}/pkgconfig/python.pc
%{_libdir}/pkgconfig/python2.pc

%files doc
%{_mandir}/man1/python2.7.1
%{_mandir}/man1/python.1
%{_mandir}/man1/python2.1


%files tcl
/usr/lib/python2.7/test/test_tcl.py
/usr/lib/python2.7/test/test_tcl.pyc
/usr/lib/python2.7/lib-dynload/_tkinter.so
/usr/lib/python2.7/lib-dynload/_tkinter.so.avx2
/usr/lib/python2.7/lib-tk
/usr/lib/python2.7/test/test_tk.py
/usr/lib/python2.7/test/test_tk.pyc
