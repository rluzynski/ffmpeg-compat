# TODO: add make test to %%check section

#global svn     20110110

%if 0%{?fedora}
#Disable vaapi on Fedora - only usefull for gst-vaapi on RHEL
%global _without_vaapi 1
%endif

Summary:        Digital VCR and streaming server
Name:           ffmpeg-compat
Version:        0.6.7
Release:        12%{?dist}
%if 0%{?_with_amr:1}
License:        GPLv3+
%else
License:        GPLv2+
%endif
Group:          Applications/Multimedia
URL:            http://ffmpeg.org/
Source0:        http://ffmpeg.org/releases/ffmpeg-%{version}.tar.bz2
Source1:        ffmpeg-snapshot.sh
Patch0:         ffmpeg-0.6.6-compile-fix.patch
Patch1:         0001-Fix-build-when-seletected-fpu-is-not-neon-on-arm.patch
Patch2:         0002-Add-unconditional-return-statement-to-yuva420_rgb32_.patch
Patch3:         ffmpeg-arm-fix.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  bzip2-devel
%{?!_without_dirac:BuildRequires: dirac-devel}
%{?_with_faac:BuildRequires: faac-devel}
BuildRequires:  gsm-devel
BuildRequires:  lame-devel
BuildRequires:  libdc1394-devel
BuildRequires:  librtmp-devel
BuildRequires:  libtheora-devel
%{?!_without_vaapi:BuildRequires: libva-devel >= 0.31.0}
BuildRequires:  libvdpau-devel
BuildRequires:  libvorbis-devel
%{?_with_vpx:BuildRequires:  libvpx-devel >= 0.9.1}
%{?_with_amr:BuildRequires: opencore-amr-devel vo-amrwbenc-devel}
BuildRequires:  openjpeg-devel
BuildRequires:  perl(Pod::Man)
BuildRequires:  schroedinger-devel
BuildRequires:  SDL-devel
BuildRequires:  speex-devel
BuildRequires:  subversion
BuildRequires:  texi2html
%{?!_without_x264:BuildRequires: x264-devel >= 0.0.0-0.30}
BuildRequires:  xvidcore-devel
BuildRequires:  zlib-devel
%ifarch %{ix86} x86_64
BuildRequires:  yasm
%endif
BuildRequires:  gcc-c++

%description
FFmpeg is a complete and free Internet live audio and video
broadcasting solution for Linux/Unix. It also includes a digital
VCR. It can encode in real time in many formats including MPEG1 audio
and video, MPEG4, h263, ac3, asf, avi, real, mjpeg, and flash.

!!! BIG FAT WARNING!!!
This package is made for compatibility with older components
It is not intended to be used in insecure environment.


%package        devel
Summary:        Development package for %{name}
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig

%description    devel
FFmpeg is a complete and free Internet live audio and video
broadcasting solution for Linux/Unix. It also includes a digital
VCR. It can encode in real time in many formats including MPEG1 audio
and video, MPEG4, h263, ac3, asf, avi, real, mjpeg, and flash.
This package contains development files for %{name}

%global ff_configure \
../configure \\\
    --disable-doc \\\
    --prefix=%{_prefix} \\\
    --bindir=%{_bindir} \\\
    --datadir=%{_datadir}/%{name} \\\
    --incdir=%{_includedir}/%{name} \\\
    --libdir=%{_libdir}/%{name} \\\
    --mandir=%{_mandir} \\\
    --arch=%{_target_cpu} \\\
    --extra-cflags="$RPM_OPT_FLAGS" \\\
    %{?vendor:--extra-version="%{vendor}"} \\\
    %{?_with_amr:--enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libvo-amrwbenc --enable-version3} \\\
    --enable-bzlib \\\
    --enable-libdc1394 \\\
    %{?!_without_dirac:--enable-libdirac} \\\
    %{?_with_faac:--enable-libfaac --enable-nonfree} \\\
    --enable-libgsm \\\
    --enable-libmp3lame \\\
    --enable-libopenjpeg \\\
    --enable-librtmp \\\
    --enable-libschroedinger \\\
    --enable-libspeex \\\
    --enable-libtheora \\\
    --enable-libvorbis \\\
    %{?_with_vpx:--enable-libvpx} \\\
    %{!?_without_x264:--enable-libx264} \\\
    --enable-libxvid \\\
    --enable-x11grab \\\
    --enable-avfilter \\\
    --enable-avfilter-lavf \\\
    --enable-postproc \\\
    --enable-pthreads \\\
    --disable-static \\\
    --enable-shared \\\
    --enable-gpl \\\
    --disable-debug \\\
    --disable-stripping


%prep
%setup -q -n ffmpeg-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p0

%build
mkdir generic
pushd generic
%{ff_configure}\
    --shlibdir=%{_libdir} \
    --disable-ffmpeg --disable-ffplay --disable-ffprobe --disable-ffserver \
%ifarch %{ix86}
    --cpu=%{_target_cpu} \
%endif
%ifarch %{ix86} x86_64
    --enable-runtime-cpudetect \
%endif
%ifarch ppc
    --cpu=g3 \
    --enable-runtime-cpudetect \
    --enable-pic \
%endif
%ifarch ppc64
    --cpu=g5 \
    --enable-runtime-cpudetect \
    --enable-pic \
%endif
%ifarch sparc sparc64
    --disable-vis \
%endif
%ifarch %{arm}
    --disable-runtime-cpudetect \
%ifnarch armv7hnl
    --disable-neon
%endif
%endif

make %{?_smp_mflags}
popd

%if 0%{!?ffmpegsuffix:1}
mkdir simd
pushd simd
%ifarch sparc sparc64
%{ff_configure}\
    --shlibdir=%{_libdir}/v9 \
    --cpu=v9 \
    --enable-vis \
    --disable-ffmpeg \
    --disable-ffserver \
    --disable-ffplay \

make %{?_smp_mflags}
%endif
popd
%endif

%install
rm -rf $RPM_BUILD_ROOT
pushd generic
make install DESTDIR=$RPM_BUILD_ROOT
popd
%if 0%{!?ffmpegsuffix:1}
pushd simd
%ifarch sparc sparc64
make install DESTDIR=$RPM_BUILD_ROOT
%endif
popd
%endif

#Alternative ffmpeg package move headers into a special directory
if ! [ %{name} == ffmpeg ] ; then
mkdir -p $RPM_BUILD_ROOT%{_libdir}/%{name}/pkgconfig
for s in $RPM_BUILD_ROOT/%{_libdir}/*.so ; do 
  ffmpegsym=`basename ${s}`
  ffmpeglib=`readlink ${s}`
  echo "Symlink $ffmpeglib"
  ln -fs ../${ffmpeglib} \
    $RPM_BUILD_ROOT%{_libdir}/%{name}/${ffmpegsym}
done
rm -rf $RPM_BUILD_ROOT/%{_libdir}/*.so
fi

%clean
rm -rf $RPM_BUILD_ROOT


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc COPYING.* CREDITS README
%{_libdir}/lib*.so.*
%if 0%{!?ffmpegsuffix:1}
%ifarch sparc sparc64
%{_libdir}/v9/lib*.so.*
%endif
%endif

%files devel
%defattr(-,root,root,-)
%doc MAINTAINERS doc/APIchanges doc/TODO doc/*.txt
%{_includedir}/%{name}
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/pkgconfig
%{_libdir}/%{name}/pkgconfig/lib*.pc
%{_libdir}/%{name}/lib*.so
%if 0%{!?ffmpegsuffix:1}
%ifarch sparc sparc64
%{_libdir}/v9/lib*.so
%endif
%endif


%changelog
* Sat Sep 15 2018 Rafal Luzynski <digitalfreak@lingonborough.com> - 0.6.7-12
- Added "BuildRequires: gcc-c++"
- Rebuilt for Fedora 28

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 0.6.7-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sun Mar 19 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 0.6.7-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sun May 03 2015 Nicolas Chauvet <kwizart@gmail.com> - 0.6.7-9
- Disable doc - rfbz#3616

* Mon Nov 24 2014 Nicolas Chauvet <kwizart@gmail.com> - 0.6.7-8
- Add patch for arm - reported by Tobias Brodel

* Mon Sep 01 2014 Sérgio Basto <sergio@serjux.com> - 0.6.7-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Mar 22 2014 Sérgio Basto <sergio@serjux.com> - 0.6.7-6
- Rebuilt for x264

* Thu Mar 06 2014 Nicolas Chauvet <kwizart@gmail.com> - 0.6.7-5
- Rebuilt for x264

* Tue Jan 07 2014 Nicolas Chauvet <kwizart@gmail.com> - 0.6.7-4
- Rebuilt for librtmp

* Tue Nov 05 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.6.7-3
- Rebuilt for x264/FFmpeg

* Tue Oct 22 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.6.7-2
- Rebuilt for x264

* Tue Oct 01 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.6.7-1
- Update to 0.6.7

* Sat Jul 20 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.6.6-10
- Rebuilt for x264

* Sat Jun 29 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.6.6-9
- Fix build on non-neon arm

* Thu Jun 27 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.6.6-8
- Drop support for VAAPI on fedora

* Sat May 25 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.6.6-7
- Add BR for perl(Pod::Man)

* Sun May  5 2013 Hans de Goede <j.w.r.degoede@gmail.com> - 0.6.6-6
- Rebuilt for x264 0.130

* Sun Jan 20 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.6.6-5
- Rebuilt for FFmpeg/x264

* Fri Nov 23 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.6.6-4
- Rebuilt for x264

* Wed Sep 05 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.6.6-3
- Rebuilt for x264 ABI 125

* Sun Jun 24 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.6.6-2
- Rebuilt for x264

* Wed Jun 13 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.6.6-1
- Update to 0.6.6

* Wed May 30 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.6.5-4
- Drop Provides for ffmpeg-devel

* Thu May 24 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.6.5-3
- Fix typo on readlink

* Sat Apr 14 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.6.5-2
- Move headers .pc and data to a ffmpeg-compat directory.
- Update arm options
- Disable x264 on armv5tel
- Verify %%_isa requirement if available
- Virtual Provides ffmpeg-devel
- Add a warning about the security risk of this package
- Disable vaapi on RHEL until the next libva

* Tue Apr 10 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.6.5-1
- move to ffmpeg-compat for EL-6
- Update to 0.6.5
- Backport some rpm conditionals dirac, vaapi, vpx, x264
- Enable avfilter-lavf

* Wed May 04 2011 Nicolas Chauvet <kwizart@gmail.com> - 0.6.3-1
- Update to 0.6.3

* Wed Apr 06 2011 Nicolas Chauvet <kwizart@gmail.com> - 0.6.2-1
- Update to 0.6.2

* Mon Jan 10 2011 Dominik Mierzejewski <rpm at greysector.net> - 0.6.1-1.20110110svn
- 20110110 snapshot
- bump version to post-0.6.1 to allow stable 0.6.1 update in older branches
- drop --with amr->opencore_amr indirection
- add qt-faststart tool (bug #1259)

* Wed Jul 21 2010 Nicolas Chauvet <kwizart@gmail.com> - 0.6-4.20100704svn
- Enable libva
- Restore compatibility --with amr

* Mon Jul 05 2010 Nicolas Chauvet <kwizart@gmail.com> - 0.6-3.20100704svn
- Fix build using --define ffmpegsuffix 'foo'
- Disable FFmpeg binaries when built with suffix.

* Sun Jul 04 2010 Dominik Mierzejewski <rpm at greysector.net> - 0.6-2.20100704svn
- 20100703 snapshot
- enable libvpx (WebM/VP8) support (rfbz#1250)
- drop faad2 support (dropped upstream)
- drop old Obsoletes:
- enable librtmp support

* Sat Jun 19 2010 Dominik Mierzejewski <rpm at greysector.net> - 0.6-1.20100619svn
- 20100619 snapshot

* Thu Apr 29 2010 Dominik Mierzejewski <rpm at greysector.net> - 0.6-0.3.20100429svn
- 20100429 snapshot
- dropped unnecessary imlib2-devel BR

* Sat Mar 20 2010 Dominik Mierzejewski <rpm at greysector.net> - 0.6-0.2.20100320svn
- bump for rebuild

* Sat Mar 20 2010 Dominik Mierzejewski <rpm at greysector.net> - 0.6-0.1.20100320svn
- 20100320 snapshot
- drop upstream'd patch
- bumped version to pre-0.6
- added ffprobe to file list

* Sat Jan 16 2010 Dominik Mierzejewski <rpm at greysector.net> - 0.5-6.20100116svn
- 20100116 snapshot, requires recent x264
- fix textrels on x86_64 in a different way (patch by Reimar Döffinger)
- use -mlongcall instead of -fPIC to fix rfbz#804, it's faster

* Sat Nov  7 2009 Hans de Goede <j.w.r.degoede@hhs.nl> - 0.5-5.20091026svn
- Add -fPIC -dPIC when compiling on ppc (rf804)

* Thu Oct 22 2009 Dominik Mierzejewski <rpm at greysector.net> - 0.5-4.20091026svn
- 20091026 snapshot, requires recent x264
- dropped support for old amr libs (not supported upstream since July)
- don't disable yasm for generic builds
- fixed opencore amr support
- dropped workaround for non-standard openjpeg headers location
- dropped separate SIMDified libs for x86 and ppc(64),
  runtime CPU detection should be enough

* Thu Oct 15 2009 kwizart <kwizart at gmail.com > - 0.5-3.svn20091007
- Update to svn snapshot 20091007
- Add BR dirac vdpau.
- Use --with nonfree as a separate conditional for amr and faac.
- Use --with gplv3 as a separate conditional for opencore-amr.
- Don't build faac by default because it's nonfree.
- Allow to --define 'ffmpegsuffix custom' for special SONAME.

* Fri Mar 27 2009 Dominik Mierzejewski <rpm at greysector.net> - 0.5-2
- rebuild for new faad2 and x264

* Tue Mar 10 2009 Dominik Mierzejewski <rpm at greysector.net> - 0.5-1
- 0.5 release
- enable yasm on x86_64, fix resulting textrels
- add missing obsoletes for ffmpeg-compat-devel (really fix bug #173)
- disable yasm and certain asm optimizations for generic ix86 builds
- %%{_bindir} is now usable
- include more docs
- specfile cleanups
- add JPEG2000 decoding support via openjpeg

* Sat Jan 31 2009 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.58.20090131
- 20090131 snapshot

* Wed Dec 17 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.57.20081217
- 20081217 snapshot
- fix pkgconfig files again (broken in 0.4.9-0.55.20081214)

* Mon Dec 15 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.56.20081214
- drop libdirac support for now

* Sun Dec 14 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.55.20081214
- 20081214 snapshot
- change the lib split on x86, it doesn't work right for P3/AthlonXP
- specfile cleanups
- enable bzlib, dirac and speex support via external libs
- sort BR list alphabetically
- drop upstream'd patch

* Thu Dec 11 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.54.20081202
- fix pkgconfig file generation

* Thu Dec 04 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.53.20081202
- 20081202 snapshot
- drop upstreamed/obsolete patches

* Thu Nov 20 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.52.20080908
- add obsoletes for -compat package (RPMFusion bug #173)

* Sat Nov 01 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.51.20080908
- reworked build system
- build optimized versions where it makes sense
- specfile cleanups
- enable yasm for optimized asm routines on x86_32
- add obsoletes for Freshrpms' libpostproc subpackage

* Thu Sep 18 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.50.20080908
- 20080908 snapshot (r25261), last before ABI change

* Fri Sep 05 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.49.20080905
- 20080905 snapshot
- fix build --with amr
- update snapshot.sh
- drop liba52 support, native ac3 decoder is better in every way

* Mon Aug 25 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.48.20080825
- 20080825 snapshot
- use CFLAGS more similar to upstream
- enable X11 grabbing input
- enable libavfilter

* Sun Aug 03 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 0.4.9-0.47.20080614
- rebuild

* Sat Jun 14 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.46.20080614
- 20080614 snapshot
- no need to conditionalize swscaler anymore
- dropped obsolete pkgconfig patch
- BR latest x264

* Mon Mar 03 2008 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.45.20080113
- rebuild for new x264

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

* Sun Dec 17 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.30.20061214
- fix pkgconfig patch

* Sat Dec 16 2006 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.29.20061214
- liba52 change broke build on 64bit
- resurrect lost URL changes

* Fri Dec 15 2006 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.28.20061214
- fixed build on x86
- change liba52 file-based dependency to provides-based
- resurrect and update pkgconfig patch

* Thu Dec 14 2006 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.27.20061214
- new snapshot URL
- new URL

* Thu Dec 14 2006 Dominik Mierzejewski <rpm at greysector.net> - 0.4.9-0.26.20061214
- 2006-12-14 snapshot
- added libdca support
- enabled swscaler
- dropped obsolete patches

* Mon Oct 30 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.25.20061030
- 2006-10-30 snapshot, fixes x86_64 build.
- Apply a less intrusive workaround for LAME detection issues.

* Sat Oct 28 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.25.20061028
- 2006-10-28 snapshot, build with x264.
- Clean up some pre-FC4 compat build dependency cruft.
- Quick and dirty workarounds for ./configure's libmp3lame test and asm
  register issues on ix86.

* Fri Oct 06 2006 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> 0.4.9-25
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Tue Sep 26 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.24.20060817
- Drop SELinux fcontext settings, they're supposedly fixed upstream again.

* Thu Aug 17 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.23.20060817
- 2006-08-17 snapshot.
- Fix svn rev in "ffmpeg -version" etc.

* Wed Aug  9 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.23.20060804
- Reintroduce SELinux fcontext settings on ix86 (not needed on x86_64, ppc),
  they're not completely taken care of upstream (#1120).
- Split svn snapshot creator into a separate script.

* Fri Aug  4 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.22.20060804
- 2006-08-04 snapshot.
- Drop bogus version from SDL-devel build dependency.
- Drop no longer relevant libpostproc obsoletion.
- Prune pre-2005 changelog entries.
- Specfile cleanup.

* Sat Jun 17 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.22.20060617
- 2006-06-17 snapshot.

* Mon Jun 12 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.22.20060612
- 2006-06-12 snapshot, rgb.txt patch applied upstream.
- Patch to force linking vhook modules with their dependencies, --as-needed
  seems to drop needed things for some reason for drawtext and imlib2.
- Revert to dlopen()'ing liba52 and add file based dependency on it, it's
  easier this way again due to --as-needed linkage.

* Wed May 17 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.22.20060517
- 2006-05-17 snapshot.
- Link with faad2, don't dlopen() it.

* Sat May 13 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.22.20060513
- 2006-05-13 snapshot.
- Drop SELinux fixups, they're part of upstream policy now.

* Sat Apr 15 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.22.20060407
- SELinux file context fixups (mplayer, vdr-dxr3 etc) while waiting for #188358

* Sat Apr  8 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.21.20060407
- 2006-04-07 CVS snapshot.
- Move *.so to -devel, hopefully nothing needs them any more.

* Fri Mar 31 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.21.20051228
- Remove superfluous dependencies from pkgconfig files (#747).
- Re-enable MMX on x86_64.

* Thu Mar 09 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- switch to new release field

* Tue Feb 28 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- add dist

* Wed Dec 28 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.lvn.0.20.20051228
- 2005-12-28 CVS snapshot.
- Let upstream configure take care of PIC settings (patched for ppc).
- Own shared lib symlinks.

* Fri Dec 23 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.4.9-0.lvn.0.20.20050801
- Apply upstream fix for CVE-2005-4048.
- Patch to find rgb.txt in FC5 too.

* Thu Sep 29 2005 Ville Skyttä <ville.skytta at iki.fi> - 0:0.4.9-0.lvn.0.19.20050801
- Clean up obsolete pre-FC3 stuff (FAAC is now unconditionally enabled).
- Drop zero Epochs.

* Tue Aug 16 2005 Ville Skyttä <ville.skytta at iki.fi> - 0:0.4.9-0.lvn.0.18.20050801
- Apply some upstream and some mine (libdir) fixes to pkgconfig files.
- Add pkgconfig dependency to -devel.
- Include gsm support.

* Thu Aug 4 2005 David Woodhouse <dwmw2@infradead.org> - 0:0.4.9-0.lvn.0.17.20050801
- Update to 20050801 snapshot to make xine-lib happy
- Enable Altivec support by using --cpu=powerpc (not 'ppc')
- Enable theora
- Add pkgconfig files
- Undefine various things which might be macros before redefining them

* Sat Jul 23 2005 Dams <anvil[AT]livna.org> - 0:0.4.9-0.lvn.0.17.20050427
- Added patch from Marc Deslauriers to fix wmv2 distorsion

* Sun Jul 10 2005 Ville Skyttä <ville.skytta at iki.fi> - 0:0.4.9-0.lvn.0.16.20050427
- Enable faac by default, rebuild with "--without faac" to disable.
- Clean up obsolete pre-FC2 and other stuff.

* Sun May 22 2005 Ville Skyttä <ville.skytta at iki.fi> - 0:0.4.9-0.lvn.0.15.20050427
- PPC needs -fPIC too.

* Sat May 21 2005 Thorsten Leemhuis <fedora[AT]leemhuis.info> - 0:0.4.9-0.lvn.0.14.20050427
- disable mmx for now on x86_64 to fix build

* Sat Apr 30 2005 Dams <anvil[AT]livna.org> - 0:0.4.9-0.lvn.0.13.20050427
- Removed bogus devel requires
- Re-added conditionnal a52dec buildreq

* Fri Apr 29 2005 Ville Skyttä <ville.skytta at iki.fi> - 0:0.4.9-0.lvn.0.12.20050427
- Link avcodec with a52 when building with a52bin, remove unnecessary
  hardcoded liba52.so.0 dependency.

* Fri Apr 29 2005 Dams <anvil[AT]livna.org> - 0:0.4.9-0.lvn.0.11.20050427
- Fixed devel package deps

* Fri Apr 29 2005 Dams <anvil[AT]livna.org> - 0:0.4.9-0.lvn.0.10.20050427
- texi2html replaces tetex as build dependency (FC4 compliance)
- re-added man pages

* Thu Apr 28 2005 Dams <anvil[AT]livna.org> - 0:0.4.9-0.lvn.0.9.20050427
- Patch from Enrico to fix build on gcc4
- Missing BuildReq a52dec-devel when a52bin is defined
- Patch to fix a52 build

* Wed Apr 27 2005 Dams <anvil[AT]livna.org> - 0:0.4.9-0.lvn.0.8.20050427
- Updated tarball to cvs 20050427 snapshot
- Enabled libogg, xvid, a52bin
- Dropped Patch[0-3]
