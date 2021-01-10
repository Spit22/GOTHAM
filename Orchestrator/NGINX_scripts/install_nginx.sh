#!/bin/bash

# Doit être exécuter en tant que root
# Installe nginx préconfiguré sur la machine
# Utilisation : ./install_nginx port_RP IP_distante port_distant

# Update
apt update

#Install C compiler
apt install build-essential

#Install wget
apt install wget

# Download and extract NGINX sources
wget https://nginx.org/download/nginx-1.19.5.tar.gz && tar zxvf nginx-1.19.5.tar.gz

# Download and extract PCRE library
wget https://ftp.pcre.org/pub/pcre/pcre-8.44.tar.gz && tar xzvf pcre-8.44.tar.gz

# Download and extract zlib
wget http://www.zlib.net/zlib-1.2.11.tar.gz && tar xzvf zlib-1.2.11.tar.gz

# Download and extract OpenSSL
wget https://www.openssl.org/source/openssl-1.1.1g.tar.gz && tar xzvf openssl-1.1.1g.tar.gz

# Clear all the tar.gz files
rm -rf nginx-1.19.5.tar.gz
rm -rf pcre-8.44.tar.gz
rm -rf zlib-1.2.11.tar.gz
rm -rf openssl-1.1.1g.tar.gz

# Move to the nginx source file
cd nginx-1.19.5

# Configure before compilation
./configure --prefix=/etc/nginx \
            --sbin-path=/usr/sbin/nginx \
            --modules-path=/usr/lib/nginx/modules \
            --conf-path=/etc/nginx/nginx.conf \
            --error-log-path=/var/log/nginx/error.log \
            --http-log-path=/var/log/nginx/access.log \
            --pid-path=/run/nginx.pid \
            --lock-path=/var/lock/nginx.lock \
            --user=nginx \
            --group=nginx \
            --with-stream \
            --with-stream_realip_module \
            --with-stream_ssl_module \
            --with-stream_ssl_preread_module \
            --with-debug \
            --with-threads \
            --with-pcre=../pcre-8.44 \
            --with-zlib=../zlib-1.2.11 \
            --with-openssl=../openssl-1.1.1g

# Let's build NGINX !
make

make install

# Edit nginx.conf
rm /etc/nginx/nginx.conf

echo "events {}
stream{
    server {
        listen     $1;
        proxy_pass $2:$3;
    }
}" > /etc/nginx/nginx.conf

# Apply the configuration
nginx

nginx -s reload