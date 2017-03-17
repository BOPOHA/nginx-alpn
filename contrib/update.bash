!/bin/bash
set -e
OPENSSL='openssl-1.0.2j'
NGINXVER='1.11.5'
NGINXREL='1'
NJSVER='0.1.3'

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
sed -i "s|^\%prep|\%prep\n\
curl https://www.openssl.org/source/$OPENSSL.tar.gz -o \%{_sourcedir}/$OPENSSL.tar.gz\n\
tar -zxf \%{_sourcedir}/$OPENSSL.tar.gz -C \%{_builddir}\n\
tar -zxf \%{_sourcedir}/nginx-$NGINXVER.tar.gz -C \%{_sourcedir}\n\
|" $PRJDIR/contrib/*.spec

sed -i "s|^\%setup -q$|\%setup\n\
tar --strip-components=1 -zxf \%{_sourcedir}/\%{name}-\%{version}/nginx-\%{main_version}.tar.gz\n\
|" $PRJDIR/contrib/*.spec

sed -i "s|^tar --strip-components=1.*|tar --strip-components=1 -zxf \%{_sourcedir}/\%{name}-\%{main_version}/nginx-\%{main_version}.tar.gz\n\
|" $PRJDIR/contrib/*.spec


sed -i "s|--with-http_ssl_module|--with-http_ssl_module --with-openssl=\%{_builddir}/$OPENSSL|g" $PRJDIR/contrib/*.spec
#rm -rf $TMPDIR/*src.rpm*
echo 'DONE'
