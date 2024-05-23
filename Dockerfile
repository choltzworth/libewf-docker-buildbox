FROM ubuntu:22.04
ENV UBUNTU_VERSION "2204"
ENV DEBIAN_FRONTEND "noninteractive"

ARG LIBEWF_VERSION="20240506"

RUN set -eux; \
    apt-get update -y; \
    apt-get install -y tzdata equivs wget devscripts autotools-dev build-essential debhelper dh-autoreconf dh-python fakeroot pkg-config flex bison zlib1g-dev libssl-dev libfuse-dev python3-dev python3-setuptools;

RUN set -eux; \
    cd ~; \
    mkdir -p src; \
    cd src; \
    wget -O libewf_${LIBEWF_VERSION}.orig.tar.gz https://github.com/libyal/libewf/releases/download/${LIBEWF_VERSION}/libewf-experimental-${LIBEWF_VERSION}.tar.gz; \
    tar -xf libewf_${LIBEWF_VERSION}.orig.tar.gz;

RUN set -eux; \
    cd ~/src/libewf-${LIBEWF_VERSION}; \
    ./configure;

RUN set -eux; \
    cd ~/src/libewf-${LIBEWF_VERSION}; \
    cp -rf dpkg debian; \
    dpkg-buildpackage -rfakeroot;

RUN set -eux; \
    dpkg -i ~/src/*.deb;