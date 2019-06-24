#!/bin/bash
set -e
OPENSSL='openssl-1.1.1'
NGINXVER='1.17.0'
NGINXREL='1'
NJSVER='0.3.2'
REPO='el7'

OPENSSL_URL="https://www.openssl.org/source/$OPENSSL.tar.gz"
IFS='.' NGVERARR=($NGINXVER)
unset IFS
if [ $((NGVERARR[1]%2)) -ne 0 ] ; then
       REPOURL="https://nginx.org/packages/mainline/centos/7/SRPMS"
else
       REPOURL="https://nginx.org/packages/centos/7/SRPMS"
fi
echo $REPOURL

RPMLIST="nginx-$NGINXVER-$NGINXREL.$REPO.ngx.src.rpm
nginx-module-njs-$NGINXVER.$NJSVER-$NGINXREL.$REPO.ngx.src.rpm
nginx-module-geoip-$NGINXVER-$NGINXREL.$REPO.ngx.src.rpm
nginx-module-perl-$NGINXVER-$NGINXREL.$REPO.ngx.src.rpm
nginx-module-image-filter-$NGINXVER-$NGINXREL.$REPO.ngx.src.rpm
nginx-module-xslt-$NGINXVER-$NGINXREL.$REPO.ngx.src.rpm"

TMPDIR='/tmp'
PRJDIR="$PWD"
ls "$PWD" | egrep -v 'contrib|LICENSE|README' | xargs rm -rf

if [ ! -f "$TMPDIR/$OPENSSL.tar.gz" ]; then
        curl $OPENSSL_URL -o $TMPDIR/$OPENSSL.tar.gz
fi
cp $TMPDIR/$OPENSSL.tar.gz $PRJDIR/$OPENSSL.tar.gz
function download_and_unzip_rpm {
	RPMNAME=$1
	echo $RPMNAME
        if [ ! -f "$TMPDIR/$RPMNAME" ]; then
            curl "$REPOURL/$RPMNAME" -o "$TMPDIR/$RPMNAME"
        fi
        rpm2cpio "$TMPDIR/$RPMNAME" | cpio -idmv -D $PRJDIR
}


for rpmname in $RPMLIST; do
	download_and_unzip_rpm $rpmname
done

cp -a $PRJDIR/*.spec $PRJDIR/contrib/

sed -i "s#^\%if 0\%{?rhel} == 7#\%if ( 0\%{\?rhel} == 7 ) || ( 0\%{?fedora} >= 18 )#" $PRJDIR/contrib/*.spec
sed -i "s#^Version: .*#Version: \%{main_version}#"                                    $PRJDIR/contrib/*.spec
sed -i "s#^Release: .*#Release: \%{main_release}#"                                    $PRJDIR/contrib/*.spec

sed -i "s#^Requires: nginx == .*#Requires: nginx == \%{?epoch:\%{epoch}:}\%{main_version}-\%{main_release}#" $PRJDIR/contrib/*.spec

sed -i "s#^Source0:#Source90: $OPENSSL.tar.gz\nSource0:#" $PRJDIR/contrib/*.spec
sed -i "s|^\%prep|\%prep\n\
tar -zxf \%{_sourcedir}/nginx-\%{main_version}.tar.gz -C \%{_sourcedir}\n\
find \%{_sourcedir}\n\
tar -zxf \%{_sourcedir}/$OPENSSL.tar.gz -C \%{_builddir}\n\
|" $PRJDIR/contrib/*.spec
# replace lsb_release with sed
sed -i 's|^\%define os_minor.*$|\%define os_minor 4|' contrib/*.spec
# lsb_release -rs | cut -d '.' -f 2
# sed "s#^.*release .\.\([0-9]*\)\..*#\1#" /etc/redhat-release
# 4

sed -i "s|^\%setup -q$|\%setup\n|" $PRJDIR/contrib/*.spec
#sed -i "s|^\%setup -q$|\%setup\n\
#tar --strip-components=1 -zxf \%{_sourcedir}/\%{name}-\%{version}/nginx-\%{main_version}.tar.gz\n\
#|" $PRJDIR/contrib/*.spec

#sed -i "s|^tar --strip-components=1.*|tar --strip-components=1 -zxf \%{_sourcedir}/\%{name}-\%{version}/nginx-\%{main_version}.tar.gz\n\
#|" $PRJDIR/contrib/*.spec


sed -i "s|--with-http_ssl_module|--with-http_ssl_module --with-openssl=\%{_builddir}/$OPENSSL --with-openssl-opt=enable-tls1_3|g" $PRJDIR/contrib/*.spec
#rm -rf $TMPDIR/*src.rpm*
echo 'DONE'
