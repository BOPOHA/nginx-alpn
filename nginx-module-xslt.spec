#
%define nginx_user nginx
%define nginx_group nginx

%if 0%{?rhel} || 0%{?amzn}
%define _group System Environment/Daemons
BuildRequires: openssl-devel
%endif

%if 0%{?suse_version} == 1315
%define _group Productivity/Networking/Web/Servers
BuildRequires: libopenssl-devel
%endif

%if 0%{?rhel} == 7
BuildRequires: redhat-lsb-core
%define epoch 1
Epoch: %{epoch}
%define os_minor %(lsb_release -rs | cut -d '.' -f 2)
%if %{os_minor} >= 4
%define dist .el7_4
%else
%define dist .el7
%endif
%endif

BuildRequires: libxslt-devel
Requires: libxslt

%define main_version 1.15.3
%define main_release 1%{?dist}.ngx

%define bdir %{_builddir}/%{name}-%{main_version}

Summary: nginx xslt dynamic module
Name: nginx-module-xslt
Version: 1.15.3
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
Requires: nginx == %{?epoch:%{epoch}:}1.15.3-1%{?dist}.ngx

%description
nginx xslt dynamic module.

%if 0%{?suse_version} || 0%{?amzn}
%debug_package
%endif

%define WITH_CC_OPT $(echo %{optflags} $(pcre-config --cflags))
%define WITH_LD_OPT -Wl,-z,relro -Wl,-z,now

%define BASE_CONFIGURE_ARGS $(echo "--prefix=%{_sysconfdir}/nginx --sbin-path=%{_sbindir}/nginx --modules-path=%{_libdir}/nginx/modules --conf-path=%{_sysconfdir}/nginx/nginx.conf --error-log-path=%{_localstatedir}/log/nginx/error.log --http-log-path=%{_localstatedir}/log/nginx/access.log --pid-path=%{_localstatedir}/run/nginx.pid --lock-path=%{_localstatedir}/run/nginx.lock --http-client-body-temp-path=%{_localstatedir}/cache/nginx/client_temp --http-proxy-temp-path=%{_localstatedir}/cache/nginx/proxy_temp --http-fastcgi-temp-path=%{_localstatedir}/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=%{_localstatedir}/cache/nginx/uwsgi_temp --http-scgi-temp-path=%{_localstatedir}/cache/nginx/scgi_temp --user=%{nginx_user} --group=%{nginx_group} --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module --with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module --with-http_slice_module --with-http_ssl_module --with-http_stub_status_module --with-http_sub_module --with-http_v2_module --with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module --with-stream_ssl_preread_module")
%define MODULE_CONFIGURE_ARGS $(echo "--with-http_xslt_module=dynamic")

%prep
%setup -qcTn %{name}-%{main_version}
tar --strip-components=1 -zxf %{SOURCE0}



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
%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-xslt
%{__install} -m 644 -p %{SOURCE1} \
    $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-xslt/



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
%dir %{_datadir}/doc/nginx-module-xslt
%{_datadir}/doc/nginx-module-xslt/*


%post
if [ $1 -eq 1 ]; then
cat <<BANNER
----------------------------------------------------------------------

The xslt dynamic module for nginx has been installed.
To enable this module, add the following to /etc/nginx/nginx.conf
and reload nginx:

    load_module modules/ngx_http_xslt_filter_module.so;

Please refer to the module documentation for further details:
http://nginx.org/en/docs/http/ngx_http_xslt_module.html

----------------------------------------------------------------------
BANNER
fi

%changelog
* Tue Aug 28 2018 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.15.3

* Tue Jul 24 2018 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.15.2

* Tue Jul 03 2018 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.15.1

* Tue Jun 05 2018 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.15.0

* Mon Apr 09 2018 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.13.12

* Tue Apr 03 2018 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.13.11

* Tue Mar 20 2018 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.13.10

* Tue Feb 20 2018 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.13.9

* Tue Dec 26 2017 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.13.8

* Tue Nov 21 2017 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.13.7

* Tue Oct 10 2017 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.13.6

* Tue Sep  5 2017 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.13.5

* Tue Aug  8 2017 Sergey Budnevitch <sb@nginx.com>
- base version updated to 1.13.4

* Tue Jul 11 2017 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.13.3

* Tue Jun 27 2017 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.13.2

* Tue May 30 2017 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.13.1

* Tue Apr 25 2017 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.13.0

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
