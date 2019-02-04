#
%define nginx_user nginx
%define nginx_group nginx

%if 0%{?rhel} || 0%{?amzn}
%define _group System Environment/Daemons
BuildRequires: openssl-devel
%endif

%if 0%{?suse_version} >= 1315
%define _group Productivity/Networking/Web/Servers
BuildRequires: libopenssl-devel
%endif

%if ( 0%{?rhel} == 7 ) || ( 0%{?fedora} >= 18 )
BuildRequires: redhat-lsb-core
%define epoch 1
Epoch: %{epoch}
%define os_minor 4
%if %{os_minor} >= 4
%define dist .el7_4
%else
%define dist .el7
%endif
%endif

BuildRequires: libedit-devel

%define main_version 1.15.8
%define main_release 1%{?dist}.ngx
%define ngmod_version 2.9.3
%define ngmod_name    modsecurity

%define bdir %{_builddir}/%{name}-%{main_version}

Summary: nginx %{ngmod_name} dynamic modules
Name: nginx-module-%{ngmod_name}
Version: %{main_version}
Release: %{main_release}
Vendor: Nginx, Inc.
URL: http://nginx.org/
Group: %{_group}

Source90: https://www.openssl.org/source/openssl-1.1.1.tar.gz
Source0: https://nginx.org/download/nginx-%{main_version}.tar.gz
Source1: COPYRIGHT

# Source100: https://github.com/SpiderLabs/ModSecurity/releases/download/v%{ngmod_version}/%{ngmod_name}-%{ngmod_version}.tar.gz
Source100: https://github.com/SpiderLabs/ModSecurity-nginx/archive/master.zip



License: 2-clause BSD-like license

BuildRoot: %{_tmppath}/%{name}-%{main_version}-%{main_release}-root
BuildRequires: zlib-devel
BuildRequires: pcre-devel
Requires: nginx == %{?epoch:%{epoch}:}%{main_version}-%{main_release}

%description
nginx %{ngmod_name} dynamic modules.

%if 0%{?suse_version} || 0%{?amzn}
%debug_package
%endif

%define WITH_CC_OPT $(echo %{optflags} $(pcre-config --cflags))
%define WITH_LD_OPT -Wl,-z,relro -Wl,-z,now

%define BASE_CONFIGURE_ARGS $(echo "--prefix=%{_sysconfdir}/nginx --sbin-path=%{_sbindir}/nginx --modules-path=%{_libdir}/nginx/modules --conf-path=%{_sysconfdir}/nginx/nginx.conf --error-log-path=%{_localstatedir}/log/nginx/error.log --http-log-path=%{_localstatedir}/log/nginx/access.log --pid-path=%{_localstatedir}/run/nginx.pid --lock-path=%{_localstatedir}/run/nginx.lock --http-client-body-temp-path=%{_localstatedir}/cache/nginx/client_temp --http-proxy-temp-path=%{_localstatedir}/cache/nginx/proxy_temp --http-fastcgi-temp-path=%{_localstatedir}/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=%{_localstatedir}/cache/nginx/uwsgi_temp --http-scgi-temp-path=%{_localstatedir}/cache/nginx/scgi_temp --user=%{nginx_user} --group=%{nginx_group} --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module --with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module --with-http_slice_module --with-http_ssl_module --with-openssl=%{_builddir}/openssl-1.1.1 --with-openssl-opt=enable-tls1_3 --with-http_stub_status_module --with-http_sub_module --with-http_v2_module --with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module --with-stream_ssl_preread_module")
%define MODULE_CONFIGURE_ARGS $(echo "--add-dynamic-module=%{ngmod_name}-%{ngmod_version}/nginx")

%prep
find %{_sourcedir}
tar -zxf %{SOURCE90} -C %{_builddir}


%setup -qcTn %{name}-%{main_version}
tar --strip-components=1 -xvf %{SOURCE100} -C $RPM_BUILD_ROOT%{_sysconfdir}/nginx/modules/


%build
cd %{bdir}/%{ngmod_name}-%{ngmod_version} && ./configure && make modsecurity
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
find .
%install
cd %{bdir}
%{__rm} -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-%{ngmod_name}
%{__install} -m 644 -p %{SOURCE1} \
    $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-%{ngmod_name}/

%{__install} -m644 %{bdir}/%{ngmod_name}-%{ngmod_version}/CHANGES $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-%{ngmod_name}/
%{__mkdir} -p $RPM_BUILD_ROOT%{_bindir}
%{__install} -m755 %{bdir}/%{ngmod_name}-%{ngmod_version}/build/%{ngmod_name} $RPM_BUILD_ROOT%{_bindir}/

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
%dir %{_datadir}/doc/nginx-module-%{ngmod_name}
%{_datadir}/doc/nginx-module-%{ngmod_name}/*
%{_bindir}/%{ngmod_name}

%post
if [ $1 -eq 1 ]; then
cat <<BANNER
----------------------------------------------------------------------

The %{ngmod_name} dynamic modules for nginx have been installed.
To enable these modules, add the following to /etc/nginx/nginx.conf
and reload nginx:

    load_module modules/ngx_http_%{ngmod_name}_module.so;

Please refer to the modules documentation for further details:
https://github.com/SpiderLabs/ModSecurity.git

----------------------------------------------------------------------
BANNER
fi

%changelog
* Tue Dec 25 2018 Konstantin Pavlov <thresh@nginx.com>
- base version updated to 1.15.8


