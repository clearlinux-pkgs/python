Name:           python
Version:        2.7.12
Release:        104
License:        Python-2.0
Summary:        The Python Programming Language
Url:            http://www.python.org
Group:          devel/python
Source0:        http://www.python.org/ftp/python/2.7.12/Python-2.7.12.tar.xz
Source1:        argparse.egg-info
Patch1:         0001-Skip-mhlib-tests.patch
Patch2:         0001-Support-os-release-file-Modification-of-issue-17762-.patch
Patch3:		libffi-shared.patch
Patch4:		link-opt.patch
Patch5:		link-whole-archive.patch
Patch6:		lto-link-flags.patch
Patch7:     0001-Add-pybench-to-the-PROFILE_TASK-rule.patch
Patch8:		avx2-distutils.patch
Patch9:		load-avx2.patch
Patch10:	buildhack.patch

# CVE patches
Patch100:	cve-2014-4616.nopatch

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
Requires: python-core
Requires: python-lib
Requires: clr-python-timestamp
Requires: openblas
Requires: libgfortran-avx
Requires: usrbinpython


%define python_configure_flags --with-threads --with-pymalloc --without-cxx-main  --with-signal-module --enable-ipv6=yes  ac_cv_header_bluetooth_bluetooth_h=no  ac_cv_header_bluetooth_h=no --with-system-expat  --with-system-ffi  --libdir=/usr/lib --with-computed-gotos --with-lto

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
Requires:	usrbinpython

%description core
The Python Programming Language.

%package dev
License:        Python-2.0
Summary:        The Python Programming Language
Group:          devel
Requires:       python-lib
Requires:       python-core
#Requires:	py
#Requires:	pytest
#Requires:	python-subunit


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
%patch10 -p1

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
mkdir -p %{buildroot}//usr/lib64
mv %{buildroot}//usr/lib/libpython2.7.so* %{buildroot}//usr/lib64
mkdir -p %{buildroot}/stash
cp -r %{buildroot}//usr/lib %{buildroot}/stash

# The script recommends this change if installing python to /usr/bin
sed -i '1s@/usr/local/bin/python@/usr/bin/env python2@' %{buildroot}/usr/lib/python2.7/cgi.py

# Build with PGO for perf improvement
make clean
%configure %python_configure_flags
make profile-opt %{?_smp_mflags}
%make_install

sed -i '1s@/usr/local/bin/python@/usr/bin/env python2@' %{buildroot}/usr/lib/python2.7/cgi.py

rm -f `find %{buildroot}/usr/lib -name "*.pyo" `
chmod a+x `find %{buildroot}/usr/lib -name "*.so.avx2" `
chmod a+x `find %{buildroot}/usr/lib -name "*.so.avx512" `
mv %{buildroot}/stash/lib/python2.7/_sysconfigdata.py* %{buildroot}//usr/lib/python2.7/
mv %{buildroot}/stash/lib/python2.7/config/* %{buildroot}//usr/lib/python2.7/config/
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



%files

%files lib
/usr/lib64/libpython2.7.so.1.0

%files core
/usr/bin/2to3
/usr/bin/idle
/usr/bin/pydoc
%exclude /usr/bin/python
/usr/bin/python-config
/usr/bin/python2
/usr/bin/python2-config
/usr/bin/python2.7
/usr/bin/python2.7-config
/usr/bin/smtpd.py
/usr/include/python2.7/pyconfig.h
/usr/lib/python2.7/*
%exclude /usr/lib/python2.7/test/test_tcl.py
%exclude /usr/lib/python2.7/test/test_tcl.pyc
%exclude /usr/lib/python2.7/lib-dynload/_tkinter.so
%exclude /usr/lib/python2.7/lib-dynload/_tkinter.so.avx2
%exclude /usr/lib/python2.7/lib-dynload/_tkinter.so.avx512
%exclude /usr/lib/python2.7/lib-tk
%exclude /usr/lib/python2.7/test/test_tk.py
%exclude /usr/lib/python2.7/test/test_tk.pyc



%files dev
/usr/include/python2.7/*.h
%exclude /usr/include/python2.7/pyconfig.h
/usr/lib64/libpython2.7.so
/usr/lib64/pkgconfig/python-2.7.pc
/usr/lib64/pkgconfig/python.pc
/usr/lib64/pkgconfig/python2.pc

%files doc
/usr/share/man/man1/python2.7.1
/usr/share/man/man1/python.1
/usr/share/man/man1/python2.1


%files tcl
/usr/lib/python2.7/test/test_tcl.py
/usr/lib/python2.7/test/test_tcl.pyc
/usr/lib/python2.7/lib-dynload/_tkinter.so
/usr/lib/python2.7/lib-dynload/_tkinter.so.*
/usr/lib/python2.7/lib-tk
/usr/lib/python2.7/test/test_tk.py
/usr/lib/python2.7/test/test_tk.pyc
