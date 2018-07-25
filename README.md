# nginx-alpn


https://copr.fedorainfracloud.org/coprs/vorona/nginx-alpn/

Yum repository for nginx with ALPN on EL7/6.

Nginx with proper HTTP/2 (ALPN) support for CentOS 6 and Centos 7.

Builded with OpenSSL 1.1.1-pre4 (TLS 1.3 support, draft 28, https://dev.ssllabs.com/ssltest/analyze.html)

The original files were patched this script: https://github.com/BOPOHA/nginx-alpn/blob/master/contrib/update.bash

Installation Instructions
Centos 7:

    curl -s https://copr.fedorainfracloud.org/coprs/vorona/nginx-alpn/repo/epel-7/vorona-nginx-alpn-epel-7.repo -o /etc/yum.repos.d/nginx-alpn-epel-7.repo
    yum install nginx -y

Centos 6:

    curl -s https://copr.fedorainfracloud.org/coprs/vorona/nginx-alpn/repo/epel-6/vorona-nginx-alpn-epel-6.repo -o /etc/yum.repos.d/nginx-alpn-epel-6.repo
    yum install nginx -y



