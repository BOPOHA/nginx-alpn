!/bin/bash
set -e
OPENSSL='openssl-1.1.0e'
NGINXVER='1.11.11'
NGINXREL='1'
NJSVER='0.1.9'

OPENSSL_URL="https://www.openssl.org/source/$OPENSSL.tar.gz"
REPOURL="http://nginx.org/packages/mainline/centos/7/SRPMS"
RPMLIST="nginx-$NGINXVER-$NGINXREL.el7.ngx.src.rpm
nginx-module-njs-$NGINXVER.$NJSVER-$NGINXREL.el7.ngx.src.rpm
nginx-module-geoip-$NGINXVER-$NGINXREL.el7.ngx.src.rpm
nginx-module-perl-$NGINXVER-$NGINXREL.el7.ngx.src.rpm
nginx-module-image-filter-$NGINXVER-$NGINXREL.el7.ngx.src.rpm
nginx-module-xslt-$NGINXVER-$NGINXREL.el7.ngx.src.rpm"

TMPDIR='/tmp'
PRJDIR="$PWD"
ls "$PWD" | egrep -v 'contrib|LICENSE|README' | xargs rm -rf
curl $OPENSSL_URL -o $PRJDIR/$OPENSSL.tar.gz
function download_and_unzip_rpm {
	RPMNAME=$1
	echo $RPMNAME
        if [ ! -f "$TMPDIR/$RPMNAME" ]; then
            curl "$REPOURL/$RPMNAME" -o "$TMPDIR/$RPMNAME"
        fi
        rpm2cpio "$TMPDIR/$RPMNAME" | cpio -idmv $PRJDIR
}


for rpmname in $RPMLIST; do
	download_and_unzip_rpm $rpmname
done

cp -a $PRJDIR/*.spec $PRJDIR/contrib/

sed -i "s#^\%if 0\%{?rhel} == 7#\%if ( 0\%{\?rhel} == 7 ) || ( 0\%{?fedora} >= 18 )#" $PRJDIR/contrib/*.spec
sed -i "s#^BuildRequires: pcre-devel#BuildRequires: pcre-devel\nBuildRequires: curl#" $PRJDIR/contrib/*.spec
sed -i "s|^\%prep|\%prep\n\
tar -zxf \%{_sourcedir}/nginx-$NGINXVER.tar.gz -C \%{_sourcedir}\n\
tar -zxf \%{_sourcedir}/\%{_sourcedir}/\%{name}-\%{version}/$OPENSSL.tar.gz -C \%{_builddir}\n\
|" $PRJDIR/contrib/*.spec

sed -i "s|^\%setup -q$|\%setup\n\
tar --strip-components=1 -zxf \%{_sourcedir}/\%{name}-\%{version}/nginx-\%{main_version}.tar.gz\n\
|" $PRJDIR/contrib/*.spec

sed -i "s|^tar --strip-components=1.*|tar --strip-components=1 -zxf \%{_sourcedir}/\%{name}-\%{version}/nginx-\%{main_version}.tar.gz\n\
|" $PRJDIR/contrib/*.spec


sed -i "s|--with-http_ssl_module|--with-http_ssl_module --with-openssl=\%{_builddir}/$OPENSSL|g" $PRJDIR/contrib/*.spec
#rm -rf $TMPDIR/*src.rpm*
echo 'DONE'
