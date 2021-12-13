BuildRequires: perl-IPC-Cmd
#
%define nginx_user nginx
%define nginx_group nginx

%if 0%{?rhel} || 0%{?amzn} || 0%{?fedora}
%define _group System Environment/Daemons
%if 0%{?amzn} >= 2
BuildRequires: openssl11-devel
%else
BuildRequires: openssl-devel
%endif
%endif

%if 0%{?suse_version} >= 1315
%define _group Productivity/Networking/Web/Servers
BuildRequires: libopenssl-devel
%define _debugsource_template %{nil}
%endif

%if (0%{?rhel} == 7) && (0%{?amzn} == 0)
%define epoch 1
Epoch: %{epoch}
%define dist .el7
%endif

%if (0%{?rhel} == 7) && (0%{?amzn} == 2)
%define epoch 1
Epoch: %{epoch}
%endif

%if 0%{?rhel} == 8
%define epoch 1
Epoch: %{epoch}
%define _debugsource_template %{nil}
%endif

%if 0%{?fedora}
%define _debugsource_template %{nil}
%global _hardened_build 1
%endif

BuildRequires: libedit-devel

%define base_version 1.21.4
%define base_release 1%{?dist}.ngx

%define bdir %{_builddir}/%{name}-%{base_version}

Summary: nginx njs dynamic modules
Name: nginx-module-njs
Version: %{base_version}
Release: %{base_release}
Vendor: NGINX Packaging <nginx-packaging@f5.com>
URL: https://nginx.org/
Group: %{_group}

Source90: openssl-3.0.0.tar.gz
Source0: https://nginx.org/download/nginx-%{base_version}.tar.gz
Source1: nginx-module-njs.copyright

Source100: njs-0.7.0.tar.gz



License: 2-clause BSD-like license

BuildRoot: %{_tmppath}/%{name}-%{base_version}-%{base_release}-root
BuildRequires: zlib-devel
BuildRequires: pcre-devel
Requires: nginx-r%{base_version}
Provides: %{name}-r%{base_version}

%description
nginx njs dynamic modules.

%if 0%{?suse_version}
%debug_package
%endif

%define WITH_CC_OPT $(echo %{optflags} $(pcre-config --cflags))
%define WITH_LD_OPT -Wl,-z,relro -Wl,-z,now

%define BASE_CONFIGURE_ARGS $(echo "--prefix=%{_sysconfdir}/nginx --sbin-path=%{_sbindir}/nginx --modules-path=%{_libdir}/nginx/modules --conf-path=%{_sysconfdir}/nginx/nginx.conf --error-log-path=%{_localstatedir}/log/nginx/error.log --http-log-path=%{_localstatedir}/log/nginx/access.log --pid-path=%{_localstatedir}/run/nginx.pid --lock-path=%{_localstatedir}/run/nginx.lock --http-client-body-temp-path=%{_localstatedir}/cache/nginx/client_temp --http-proxy-temp-path=%{_localstatedir}/cache/nginx/proxy_temp --http-fastcgi-temp-path=%{_localstatedir}/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=%{_localstatedir}/cache/nginx/uwsgi_temp --http-scgi-temp-path=%{_localstatedir}/cache/nginx/scgi_temp --user=%{nginx_user} --group=%{nginx_group} --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module --with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module --with-http_slice_module --with-http_ssl_module --with-openssl=%{_builddir}/openssl-3.0.0 --with-openssl-opt=enable-tls1_3 --with-http_stub_status_module --with-http_sub_module --with-http_v2_module --with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module --with-stream_ssl_preread_module")
%define MODULE_CONFIGURE_ARGS $(echo "--add-dynamic-module=njs-0.7.0/nginx")

%prep
tar -zxf %{_sourcedir}/nginx-%{base_version}.tar.gz -C %{_sourcedir}
find %{_sourcedir}
tar -zxf %{_sourcedir}/openssl-3.0.0.tar.gz -C %{_builddir}

%setup -qcTn %{name}-%{base_version}
tar --strip-components=1 -zxf %{SOURCE0}

tar xvzfo %{SOURCE100}
ln -s njs-* njs


%build
cd %{bdir}/njs-0.7.0 && ./configure && make njs
cd %{bdir}

./configure %{BASE_CONFIGURE_ARGS} %{MODULE_CONFIGURE_ARGS} \
	--with-cc-opt="%{WITH_CC_OPT} " \
	--with-ld-opt="%{WITH_LD_OPT} " \
	--with-debug
make %{?_smp_mflags} modules
for so in `find %{bdir}/objs/ -type f -name "*.so"`; do
debugso=`echo $so | sed -e 's|\.so$|-debug.so|'`
mv $so $debugso
done

./configure %{BASE_CONFIGURE_ARGS} %{MODULE_CONFIGURE_ARGS} \
	--with-cc-opt="%{WITH_CC_OPT} " \
	--with-ld-opt="%{WITH_LD_OPT} "
make %{?_smp_mflags} modules

%install
cd %{bdir}
%{__rm} -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-njs
%{__install} -m 644 -p %{SOURCE1} \
    $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-njs/COPYRIGHT

%{__install} -m644 %{bdir}/njs-0.7.0/CHANGES $RPM_BUILD_ROOT%{_datadir}/doc/%{name}/
%{__mkdir} -p $RPM_BUILD_ROOT%{_bindir}
%{__install} -m755 %{bdir}/njs-0.7.0/build/njs $RPM_BUILD_ROOT%{_bindir}/

%{__mkdir} -p $RPM_BUILD_ROOT%{_libdir}/nginx/modules
for so in `find %{bdir}/objs/ -maxdepth 1 -type f -name "*.so"`; do
%{__install} -m755 $so \
   $RPM_BUILD_ROOT%{_libdir}/nginx/modules/
done

%check
%{__rm} -rf $RPM_BUILD_ROOT/usr/src
cd %{bdir}
grep -v 'usr/src' debugfiles.list > debugfiles.list.new && mv debugfiles.list.new debugfiles.list
cat /dev/null > debugsources.list
%if 0%{?suse_version} >= 1500
cat /dev/null > debugsourcefiles.list
%endif

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_libdir}/nginx/modules/*
%dir %{_datadir}/doc/nginx-module-njs
%{_datadir}/doc/nginx-module-njs/*
%{_bindir}/njs

%post
if [ $1 -eq 1 ]; then
cat <<BANNER
----------------------------------------------------------------------

The njs dynamic modules for nginx have been installed.
To enable these modules, add the following to /etc/nginx/nginx.conf
and reload nginx:

    load_module modules/ngx_http_js_module.so;
    load_module modules/ngx_stream_js_module.so;

Please refer to the modules documentation for further details:
https://nginx.org/en/docs/njs/
https://nginx.org/en/docs/http/ngx_http_js_module.html
https://nginx.org/en/docs/stream/ngx_stream_js_module.html

----------------------------------------------------------------------
BANNER
fi

%changelog
* Tue Nov  2 2021 Konstantin Pavlov <thresh@nginx.com> - 1.21.4+0.7.0-1%{?dist}.ngx
- base version updated to 1.21.4-1

* Tue Oct 19 2021 Konstantin Pavlov <thresh@nginx.com> - 1.21.3+0.7.0-1%{?dist}.ngx
- njs updated to 0.7.0

* Tue Sep  7 2021 Konstantin Pavlov <thresh@nginx.com> - 1.21.3+0.6.2-1%{?dist}.ngx
- base version updated to 1.21.3-1

* Tue Aug 31 2021 Andrei Belov <defan@nginx.com> - 1.21.2+0.6.2-1%{?dist}.ngx
- base version updated to 1.21.2-1

* Tue Aug 31 2021 Andrei Belov <defan@nginx.com> - 1.21.1+0.6.2-1%{?dist}.ngx
- njs updated to 0.6.2

* Tue Jul  6 2021 Konstantin Pavlov <thresh@nginx.com> - 1.21.1+0.6.1-1%{?dist}.ngx
- base version updated to 1.21.1-1

* Tue Jun 29 2021 Konstantin Pavlov <thresh@nginx.com> - 1.21.0+0.6.1-1%{?dist}.ngx
- njs updated to 0.6.1

* Tue Jun 15 2021 Konstantin Pavlov <thresh@nginx.com> - 1.21.0+0.6.0-1%{?dist}.ngx
- njs updated to 0.6.0

* Tue May 25 2021 Konstantin Pavlov <thresh@nginx.com> - 1.21.0+0.5.3-1%{?dist}.ngx
- base version updated to 1.21.0-1

* Tue Apr 13 2021 Andrei Belov <defan@nginx.com> - 1.19.10+0.5.3-1%{?dist}.ngx
- base version updated to 1.19.10-1

* Tue Mar 30 2021 Konstantin Pavlov <thresh@nginx.com> - 1.19.9+0.5.3-1%{?dist}.ngx
- base version updated to 1.19.9-1

* Tue Mar 30 2021 Konstantin Pavlov <thresh@nginx.com> - 1.19.8+0.5.3-1%{?dist}.ngx
- njs updated to 0.5.3

* Tue Mar  9 2021 Konstantin Pavlov <thresh@nginx.com> - 1.19.8+0.5.2-1%{?dist}.ngx
- base version updated to 1.19.8-1

* Tue Mar  9 2021 Konstantin Pavlov <thresh@nginx.com> - 1.19.7+0.5.2-1%{?dist}.ngx
- njs updated to 0.5.2

* Tue Feb 16 2021 Konstantin Pavlov <thresh@nginx.com> - 1.19.7+0.5.1-1%{?dist}.ngx
- base version updated to 1.19.7-1

* Tue Feb 16 2021 Konstantin Pavlov <thresh@nginx.com> - 1.19.6+0.5.1-1%{?dist}.ngx
- njs updated to 0.5.1

* Tue Dec 15 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.6+0.5.0-1%{?dist}.ngx
- base version updated to 1.19.6-1

* Wed Dec  2 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.5+0.5.0-1%{?dist}.ngx
- njs updated to 0.5.0

* Tue Nov 24 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.5+0.4.4-1%{?dist}.ngx
- base version updated to 1.19.5-1
- Added a patch to fix promise subrequest with error_page redirect

* Tue Oct 27 2020 Andrei Belov <defan@nginx.com> - 1.19.4+0.4.4-1%{?dist}.ngx
- base version updated to 1.19.4-1

* Tue Sep 29 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.3+0.4.4-1%{?dist}.ngx
- njs updated to 0.4.4
- base version updated to 1.19.3-1

* Tue Aug 11 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.2+0.4.3-1%{?dist}.ngx
- base version updated to 1.19.2-1

* Tue Aug 11 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.1+0.4.3-1%{?dist}.ngx
- njs updated to 0.4.3

* Tue Jul  7 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.1+0.4.2-1%{?dist}.ngx
- base version updated to 1.19.1-1

* Tue Jul  7 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.0+0.4.2-1%{?dist}.ngx
- njs updated to 0.4.2

* Tue May 26 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.0+0.4.1-1%{?dist}.ngx
- base version updated to 1.19.0-1

* Tue May 19 2020 Konstantin Pavlov <thresh@nginx.com> - 1.17.10+0.4.1-1%{?dist}.ngx
- njs updated to 0.4.1

* Thu Apr 23 2020 Konstantin Pavlov <thresh@nginx.com> - 1.17.10+0.4.0-1%{?dist}.ngx
- njs updated to 0.4.0

* Tue Apr 14 2020 Konstantin Pavlov <thresh@nginx.com> - 1.17.10+0.3.9-1%{?dist}.ngx
- base version updated to 1.17.10-1

* Tue Mar  3 2020 Konstantin Pavlov <thresh@nginx.com> - 1.17.9+0.3.9-1%{?dist}.ngx
- base version updated to 1.17.9-1
- njs updated to 0.3.9

* Tue Jan 21 2020 Konstantin Pavlov <thresh@nginx.com> - 1.17.8+0.3.8-1%{?dist}.ngx
- base version updated to 1.17.8-1
- njs updated to 0.3.8.

* Tue Dec 24 2019 Konstantin Pavlov <thresh@nginx.com> - 1.17.7+0.3.7-1%{?dist}.ngx
- base version updated to 1.17.7-1

* Tue Nov 19 2019 Konstantin Pavlov <thresh@nginx.com> - 1.17.6+0.3.7-1%{?dist}.ngx
- base version updated to 1.17.6-1
- njs updated to 0.3.7.

* Tue Oct 22 2019 Andrei Belov <defan@nginx.com> - 1.17.5+0.3.6-1%{?dist}.ngx
- base version updated to 1.17.5-1
- njs updated to 0.3.6

* Tue Sep 24 2019 Konstantin Pavlov <thresh@nginx.com> - 1.17.4+0.3.5-1%{?dist}.ngx
- base version updated to 1.17.4-1

* Thu Aug 15 2019 Andrei Belov <defan@nginx.com> - 1.17.3+0.3.5-1%{?dist}.ngx
- njs updated to 0.3.5

* Tue Aug 13 2019 Andrei Belov <defan@nginx.com> - 1.17.3+0.3.4-1%{?dist}.ngx
- base version updated to 1.17.3-1
- njs updated to 0.3.4

* Tue Jul 23 2019 Konstantin Pavlov <thresh@nginx.com> - 1.17.2+0.3.3-1%{?dist}.ngx
- base version updated to 1.17.2-1

* Tue Jun 25 2019 Andrei Belov <defan@nginx.com> - 1.17.1+0.3.3-1%{?dist}.ngx
- base version updated to 1.17.1-1
- njs updated to 0.3.3

* Tue May 21 2019 Konstantin Pavlov <thresh@nginx.com> - 1.17.0+0.3.2-1%{?dist}.ngx
- base version updated to 1.17.0-1
- njs updated to 0.3.2.

* Tue Apr 16 2019 Konstantin Pavlov <thresh@nginx.com> - 1.15.12+0.3.1-1%{?dist}.ngx
- njs updated to 0.3.1.
- base version updated to 1.15.12-1

* Tue Apr  9 2019 Konstantin Pavlov <thresh@nginx.com> - 1.15.11+0.3.0-1%{?dist}.ngx
- base version updated to 1.15.11-1

* Tue Mar 26 2019 Konstantin Pavlov <thresh@nginx.com> - 1.15.10+0.3.0-1%{?dist}.ngx
- base version updated to 1.15.10-1
- njs updated to 0.3.0.

* Tue Feb 26 2019 Konstantin Pavlov <thresh@nginx.com> - 1.15.9+0.2.8-1%{?dist}.ngx
- base version updated to 1.15.9-1
- njs updated to 0.2.8.

* Tue Dec 25 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.8+0.2.7-1%{?dist}.ngx
- base version updated to 1.15.8-1
- njs updated to 0.2.7.

* Tue Nov 27 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.7+0.2.6-1%{?dist}.ngx
- njs updated to 0.2.6.
- base version updated to 1.15.7-1

* Tue Nov  6 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.6+0.2.5-1%{?dist}.ngx
- base version updated to 1.15.6-1

* Tue Oct 30 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.5+0.2.5-1%{?dist}.ngx
- njs updated to 0.2.5.

* Tue Oct  2 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.5+0.2.4-1%{?dist}.ngx
- base version updated to 1.15.5-1

* Tue Sep 25 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.4+0.2.4-1%{?dist}.ngx
- base version updated to 1.15.4-1

* Tue Sep 18 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.3+0.2.4-1%{?dist}.ngx
- njs updated to 0.2.4.

* Tue Aug 28 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.3+0.2.3-1%{?dist}.ngx
- base version updated to 1.15.3-1

* Tue Jul 31 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.2+0.2.3-1%{?dist}.ngx
- njs updated to 0.2.3.

* Tue Jul 24 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.2+0.2.2-1%{?dist}.ngx
- base version updated to 1.15.2-1

* Tue Jul  3 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.1+0.2.2-1%{?dist}.ngx
- base version updated to 1.15.1-1

* Thu Jun 21 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.0+0.2.2-1%{?dist}.ngx
- njs updated to 0.2.2.

* Tue Jun  5 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.0+0.2.1-1%{?dist}.ngx
- base version updated to 1.15.0-1

* Tue Jun  5 2018 Konstantin Pavlov <thresh@nginx.com> - 1.13.12+0.2.1-1%{?dist}.ngx
- njs updated to 0.2.1.

* Mon Apr  9 2018 Konstantin Pavlov <thresh@nginx.com> - 1.13.12+0.2.0-1%{?dist}.ngx
- base version updated to 1.13.12-1

* Tue Apr  3 2018 Konstantin Pavlov <thresh@nginx.com> - 1.13.11+0.2.0-1%{?dist}.ngx
- base version updated to 1.13.11-1
- njs updated to 0.2.0.

* Tue Mar 20 2018 Konstantin Pavlov <thresh@nginx.com> - 1.13.10+0.1.15-1%{?dist}.ngx
- base version updated to 1.13.10-1

* Tue Feb 20 2018 Konstantin Pavlov <thresh@nginx.com> - 1.13.9+0.1.15-1%{?dist}.ngx
- base version updated to 1.13.9-1
- fixed build on ppc64le (backported njs changeset 22cc52416e84)

* Tue Dec 26 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.8+0.1.15-1%{?dist}.ngx
- base version updated to 1.13.8-1

* Tue Nov 21 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.7+0.1.15-1%{?dist}.ngx
- base version updated to 1.13.7-1
- njs updated to 0.1.15.

* Mon Oct  9 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.6+0.1.14-1%{?dist}.ngx
- njs updated to 0.1.14

* Thu Sep 14 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.5+0.1.13-2%{?dist}.ngx
- base version updated to 1.13.5-2

* Mon Sep  4 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.5+0.1.13-1%{?dist}.ngx
- njs updated to 0.1.13

* Tue Aug  8 2017 Sergey Budnevitch <sb@nginx.com> - 1.13.4+0.1.12-1%{?dist}.ngx
- njs updated to 0.1.12

* Tue Jul 11 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.3+0.1.11-1%{?dist}.ngx
- base version updated to 1.13.3-1

* Tue Jun 27 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.2+0.1.11-1%{?dist}.ngx
- njs updated to 0.1.11

* Tue May 30 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.1+0.1.10-1%{?dist}.ngx
- base version updated to 1.13.1-1

* Tue Apr 25 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.0+0.1.10-1%{?dist}.ngx
- base version updated to 1.13.0-1

* Tue Apr  4 2017 Konstantin Pavlov <thresh@nginx.com> - 1.11.13+0.1.10-1%{?dist}.ngx
- njs updated to 0.1.10

* Fri Mar 24 2017 Konstantin Pavlov <thresh@nginx.com> - 1.11.12+0.1.9-1%{?dist}.ngx
- base version updated to 1.11.12.

* Tue Mar 21 2017 Konstantin Pavlov <thresh@nginx.com> - 1.11.11+0.1.9-1%{?dist}.ngx
- base version updated to 1.11.11.

* Tue Feb 14 2017 Konstantin Pavlov <thresh@nginx.com> - 1.11.10+0.1.9-1%{?dist}.ngx
- njs updated to 0.1.9

* Tue Jan 24 2017 Konstantin Pavlov <thresh@nginx.com> - 1.11.9+0.1.8-1%{?dist}.ngx
- njs updated to 0.1.8

* Tue Dec 27 2016 Konstantin Pavlov <thresh@nginx.com> - 1.11.8+0.1.7-1%{?dist}.ngx
- njs updated to 0.1.7

* Tue Dec 13 2016 Konstantin Pavlov <thresh@nginx.com> - 1.11.7+0.1.6-1%{?dist}.ngx
- njs updated to 0.1.6

* Tue Nov 15 2016 Konstantin Pavlov <thresh@nginx.com> - 1.11.6+0.1.4-2%{?dist}.ngx
- base version updated to 1.11.6.

* Mon Oct 24 2016 Andrei Belov <defan@nginx.com> - 1.11.5+0.1.4-1%{?dist}.ngx
- njs module updated to 0.1.4

* Mon Oct 10 2016 Andrei Belov <defan@nginx.com> - 1.11.5+0.1.3-1%{?dist}.ngx
- base version updated to 1.11.5
- njs module updated to 0.1.3

