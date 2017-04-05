#
%define nginx_user nginx
%define nginx_group nginx

%if (0%{?rhel} && 0%{?rhel} == 5) || (0%{?suse_version} == 1315)
BuildRequires: perl
%else
BuildRequires: perl-devel
BuildRequires: perl-ExtUtils-Embed
%endif
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%if 0%{?rhel} || 0%{?amzn}
%define _group System Environment/Daemons
BuildRequires: openssl-devel
%endif

%if 0%{?suse_version} == 1315
%define _group Productivity/Networking/Web/Servers
BuildRequires: libopenssl-devel
%endif

%if ( 0%{?rhel} == 7 ) || ( 0%{?fedora} >= 18 )
%define epoch 1
Epoch: %{epoch}
%endif

%define main_version 1.11.13
%define main_release 1%{?dist}.ngx

%define bdir %{_builddir}/%{name}-%{main_version}

Summary: nginx Perl dynamic module
Name: nginx-module-perl
Version: 1.11.13
Release: 1%{?dist}.ngx
Vendor: Nginx, Inc.
URL: http://nginx.org/
Group: %{_group}

Source0: http://nginx.org/download/nginx-%{main_version}.tar.gz
Source1: COPYRIGHT




License: 2-clause BSD-like license

BuildRoot: %{_tmppath}/%{name}-%{main_version}-%{main_release}-root
BuildRequires: zlib-devel
BuildRequires: pcre-devel
Requires: nginx == %{?epoch:%{epoch}:}1.11.13-1%{?dist}.ngx

%description
nginx Perl dynamic module.

%if 0%{?suse_version} || 0%{?amzn}
%debug_package
%endif

%define WITH_CC_OPT $(echo %{optflags} $(pcre-config --cflags))
%define WITH_LD_OPT -Wl,-z,relro -Wl,-z,now

%define BASE_CONFIGURE_ARGS $(echo "--prefix=%{_sysconfdir}/nginx --sbin-path=%{_sbindir}/nginx --modules-path=%{_libdir}/nginx/modules --conf-path=%{_sysconfdir}/nginx/nginx.conf --error-log-path=%{_localstatedir}/log/nginx/error.log --http-log-path=%{_localstatedir}/log/nginx/access.log --pid-path=%{_localstatedir}/run/nginx.pid --lock-path=%{_localstatedir}/run/nginx.lock --http-client-body-temp-path=%{_localstatedir}/cache/nginx/client_temp --http-proxy-temp-path=%{_localstatedir}/cache/nginx/proxy_temp --http-fastcgi-temp-path=%{_localstatedir}/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=%{_localstatedir}/cache/nginx/uwsgi_temp --http-scgi-temp-path=%{_localstatedir}/cache/nginx/scgi_temp --user=%{nginx_user} --group=%{nginx_group} --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module --with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module --with-http_slice_module --with-http_ssl_module --with-openssl=%{_builddir}/openssl-1.1.0e --with-http_stub_status_module --with-http_sub_module --with-http_v2_module --with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module --with-stream_ssl_preread_module")
%define MODULE_CONFIGURE_ARGS $(echo "--with-http_perl_module=dynamic")

%prep
tar -zxf %{_sourcedir}/nginx-%{main_version}.tar.gz -C %{_sourcedir}
tar -zxf %{_sourcedir}/%{name}-%{version}/openssl-1.1.0e.tar.gz -C %{_builddir}

%setup -qcTn %{name}-%{main_version}
tar --strip-components=1 -zxf %{_sourcedir}/%{name}-%{version}/nginx-%{main_version}.tar.gz




%build

cd %{bdir}
./configure %{BASE_CONFIGURE_ARGS} %{MODULE_CONFIGURE_ARGS} \
	--with-cc-opt="%{WITH_CC_OPT}" \
	--with-ld-opt="%{WITH_LD_OPT}" \
	--with-debug
make %{?_smp_mflags} modules
for so in `find %{bdir}/objs/ -type f -name "*.so"`; do
debugso=`echo $so | sed -e "s|.so|-debug.so|"`
mv $so $debugso
done
./configure %{BASE_CONFIGURE_ARGS} %{MODULE_CONFIGURE_ARGS} \
	--with-cc-opt="%{WITH_CC_OPT}" \
	--with-ld-opt="%{WITH_LD_OPT}"
make %{?_smp_mflags} modules

%install
cd %{bdir}
%{__rm} -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-perl
%{__install} -m 644 -p %{SOURCE1} \
    $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-perl/

%{__make} DESTDIR=$RPM_BUILD_ROOT INSTALLDIRS=vendor -f objs/Makefile install_perl_modules
find %{buildroot} -type f -name .packlist -exec rm -f '{}' \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f '{}' \;
find %{buildroot} -type f -empty -exec rm -f '{}' \;
find %{buildroot} -type f -iname '*.so' -exec chmod 0755 '{}' \;

%{__mkdir} -p $RPM_BUILD_ROOT%{_libdir}/nginx/modules
for so in `find %{bdir}/objs/ -maxdepth 1 -type f -name "*.so"`; do
%{__install} -m755 $so \
   $RPM_BUILD_ROOT%{_libdir}/nginx/modules/
done

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_libdir}/nginx/modules/*
%dir %{_datadir}/doc/nginx-module-perl
%{_datadir}/doc/nginx-module-perl/*
%dir %{perl_vendorarch}/auto/nginx
%{perl_vendorarch}/nginx.pm
%{perl_vendorarch}/auto/nginx/nginx.so
%{perl_vendorarch}/auto/nginx/nginx-debug.so
%{_mandir}/man3/nginx.3pm*

%post
if [ $1 -eq 1 ]; then
cat <<BANNER
----------------------------------------------------------------------

The Perl dynamic module for nginx has been installed.
To enable this module, add the following to /etc/nginx/nginx.conf
and reload nginx:

    load_module modules/ngx_http_perl_module.so;

Please refer to the module documentation for further details:
http://nginx.org/en/docs/http/ngx_http_perl_module.html

----------------------------------------------------------------------
BANNER
fi

%changelog
* Tue Apr  4 2017 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.11.13

* Fri Mar 24 2017 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.11.12

* Tue Mar 21 2017 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.11.11

* Tue Jan 24 2017 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.11.9

* Tue Dec 27 2016 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.11.8

* Tue Dec 13 2016 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.11.7

* Tue Nov 15 2016 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.11.6

* Mon Oct 10 2016 Andrei Belov <defan@nginx.com>
- base version updated to 1.11.5
