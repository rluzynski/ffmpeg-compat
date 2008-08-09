# TODO: add make test to %%check section

%define svn     20080225
%define faad2min 1:2.6.1
%define _with_swscaler 0
%define _with_compat   1
%if 0%{?_with_compat:1}
%define buildsuf -compat
%endif


Summary:        Libraries for ffmpeg-compat
Name:           ffmpeg-compat
Version:        0.4.9
Release:        0.48.%{svn}%{?dist}
License:        GPLv2+
Group:          System Environment/Libraries
URL:            http://ffmpeg.org/
Source0:        http://rpm.greysector.net/livna/ffmpeg-%{svn}.tar.bz2
Source1:        ffmpeg-snapshot.sh
Patch2:         ffmpeg-pkgconfig.patch
Patch4:         ffmpeg-asmreg.patch
Patch5:         ffmpeg-suffix-20080113.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  a52dec-devel
%{?_with_amr:BuildRequires: amrnb-devel amrwb-devel}
BuildRequires:  zlib-devel
BuildRequires:  lame-devel
BuildRequires:  libdc1394-devel
BuildRequires:  libvorbis-devel
BuildRequires:  libtheora-devel
BuildRequires:  faad2-devel >= %{faad2min}
BuildRequires:  xvidcore-devel
BuildRequires:  SDL-devel
BuildRequires:  gsm-devel
BuildRequires:  imlib2-devel
BuildRequires:  texi2html
BuildRequires:  faac-devel
BuildRequires:  x264-devel

%description
FFMpeg is a complete and free Internet live audio and video
broadcasting solution for Linux/Unix. It also includes a digital
VCR. It can encode in real time in many formats including MPEG1 audio
and video, MPEG4, h263, ac3, asf, avi, real, mjpeg, and flash.
This package contains the libraries for %{name}



%package        devel
Summary:        Development package for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       pkgconfig

%description    devel
FFMpeg is a complete and free Internet live audio and video
broadcasting solution for Linux/Unix. It also includes a digital
VCR. It can encode in real time in many formats including MPEG1 audio
and video, MPEG4, h263, ac3, asf, avi, real, mjpeg, and flash.
This package contains development files for %{name}

!!! Developer Warning !!!
This package contains a version of ffmpeg built without libswscale.
Softwares that use ffmpeg-compat libaries need to be ported to the new
swscaler API. (see libswscale/swscale-example.c from the doc section).

ffmpeg-compat is deprecated and will be removed at some point.



%prep
%setup -q -n ffmpeg-%{svn}
%patch2 -p1 -b .pkgconfig
%patch4 -p1 -b .asmreg
%if 0%{?_with_compat:1}
%patch5 -p1 -b .suffix
%endif

%build
./configure \
    --prefix=%{_prefix} \
%if 0%{?_with_compat:1}
    --disable-ffmpeg \
    --disable-ffserver \
    --disable-ffplay \
    --disable-vhook \
    --build-suffix=%{?buildsuf} \
    --incdir=%{_includedir}/ffmpeg%{?buildsuf} \
    --disable-swscaler \
%else
    --incdir=%{_includedir}/ffmpeg \
%endif
    --libdir=%{_libdir} \
    --shlibdir=%{_libdir} \
    --mandir=%{_mandir} \
    --arch=%{_target_cpu} \
    --extra-cflags="$RPM_OPT_FLAGS" \
    %{?_with_amr: --enable-libamr-nb --enable-libamr-wb --enable-nonfree} \
    --enable-libdc1394 \
    --enable-liba52 \
    --enable-libfaac \
    --enable-libfaad \
    --enable-libgsm \
    --enable-libmp3lame \
    --enable-libtheora \
    --enable-libvorbis \
    --enable-libxvid \
    --enable-libx264 \
    --enable-pp \
    --enable-pthreads \
    --disable-static \
    --enable-shared \
    --enable-gpl \
    --disable-debug \
    --disable-optimizations \
    --disable-strip

make %{?_smp_mflags} 


%install
rm -rf $RPM_BUILD_ROOT __doc
make install DESTDIR=$RPM_BUILD_ROOT

# We don't provide the doc for the compat-version


%clean
rm -rf $RPM_BUILD_ROOT


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc COPYING.GPL CREDITS Changelog README
%{_libdir}/libavcodec%{?buildsuf}.so.*
%{_libdir}/libavdevice%{?buildsuf}.so.*
%{_libdir}/libavformat%{?buildsuf}.so.*
%{_libdir}/libavutil%{?buildsuf}.so.*
%{_libdir}/libpostproc%{?buildsuf}.so.*


%files devel
%defattr(-,root,root,-)
# Note: as of 20070204, --incdir doesn't affect postproc.
%doc libswscale/swscale-example.c
%{_includedir}/ffmpeg%{?buildsuf}
%{_prefix}/include/postproc%{?buildsuf}
%{_libdir}/libavcodec%{?buildsuf}.so
%{_libdir}/libavdevice%{?buildsuf}.so
%{_libdir}/libavformat%{?buildsuf}.so
%{_libdir}/libavutil%{?buildsuf}.so
%{_libdir}/libpostproc%{?buildsuf}.so

%{_libdir}/pkgconfig/libswscale%{?buildsuf}.pc
%{_libdir}/pkgconfig/libavcodec%{?buildsuf}.pc
%{_libdir}/pkgconfig/libavdevice%{?buildsuf}.pc
%{_libdir}/pkgconfig/libavformat%{?buildsuf}.pc
%{_libdir}/pkgconfig/libavutil%{?buildsuf}.pc
%{_libdir}/pkgconfig/libpostproc%{?buildsuf}.pc


%changelog
* Sat Aug 09 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 0.4.9-0.48.20080225
- rebuild

* Fri Jun 20 2008 kwizart < kwizart at gmail.com > - 0.4.9-0.47.20080225
- Sync with ffmpeg
- last snapshot before API change (20080225)

* Sun Mar 02 2008 Thorsten Leemhuis <fedora at leemhuis dot info> - 0.4.9-0.46.20080113
- Rebuild

* Sat Feb 23 2008 kwizart < kwizart at gmail.com > - 0.4.9-0.45.20080113
- Remove libnut conditional (deprecated).
- Remove dirac conditional (they need to submit patch upstream).
- Improve description for ffmpeg-compat.

* Sat Feb 23 2008 kwizart < kwizart at gmail.com > - 0.4.9-0.44.20080113
- Move to ffmpeg-compat
- Disable swscaler
- Disable vhook
- Disable ffmpeg binaries.
- Built with -compat SONAME suffix

* Sun Jan 13 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.44.20080113
- 20080113 snapshot
- drop unnecessary patch
- enable libdc1394 support
- enable swscaler

* Mon Nov 12 2007 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.43.20071111
- ensure that we use the correct faad2 version

* Sun Nov 11 2007 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.42.20071111
- 20071111 snapshot
- current faad2 is good again

* Thu Oct 18 2007 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.41.20071011
- fix BRs and Requires for faad2

* Thu Oct 11 2007 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.40.20071011
- 20071011 snapshot
- don't link against faad2-2.5, it makes GPL'd binary non-distributable
- go back to normal linking instead of dlopen() of liba52

* Sun Sep 23 2007 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.39.20070923
- 20070923 snapshot
- use faad2 2.5
- optional AMR support
- dropped obsolete patch

* Thu Jun 07 2007 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.38.20070607
- 20070607 snapshot
- libdca BR dropped (no longer supported)
- drop gsm.h path hack, gsm in Fedora now provides a compatibility symlink
- remove arch hacks, ffmpeg's configure is smart enough
- enable cmov on x86_64

* Thu May 03 2007 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.37.20070503
- require older faad2 to prevent bugreports like #1388
- prepare for libdc1394 support
- enable pthreads
- 20070503 snapshot

* Thu Feb 08 2007 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.35.20070204
- libswscale.pc is necessary regardless of --enable-swscaler

* Sun Feb  4 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.34.20070204
- 2007-02-04 snapshot, enable libtheora.
- Make swscaler optional, disabled again by default (#1379).

* Fri Jan 05 2007 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.34.20061214
- move vhooks to -libs

* Wed Jan 03 2007 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.33.20061214
- split -libs subpackage for multilib installs

* Tue Dec 26 2006 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.32.20061214
- new kino works with swscaler, re-enabled

* Tue Dec 19 2006 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.31.20061214
- disable swscaler, it breaks kino


