# Use Ubuntu 22.04 as base image
FROM ubuntu:22.04
ENV UBUNTU_VERSION "2204"
ENV DEBIAN_FRONTEND "noninteractive"

# Set libewf version
ARG LIBEWF_VERSION="20240506"

# Install dependencies
RUN set -eux; \
    apt-get update -y; \
    apt-get install -y tzdata equivs wget devscripts autotools-dev build-essential debhelper dh-autoreconf dh-python fakeroot pkg-config flex bison zlib1g-dev libssl-dev libfuse-dev python3-dev python3-pip python3-setuptools;

# Download libewf source code
RUN set -eux; \
    cd ~; \
    mkdir -p src; \
    cd src; \
    wget -O libewf_${LIBEWF_VERSION}.orig.tar.gz https://github.com/libyal/libewf/releases/download/${LIBEWF_VERSION}/libewf-experimental-${LIBEWF_VERSION}.tar.gz; \
    tar -xf libewf_${LIBEWF_VERSION}.orig.tar.gz;

# Configure libewf
RUN set -eux; \
    cd ~/src/libewf-${LIBEWF_VERSION}; \
    ./configure --enable-python3;

# Prepare the debian packaging files
RUN set -eux; \
    cd ~/src/libewf-${LIBEWF_VERSION}; \
    cp -rf dpkg debian; \
    dpkg-buildpackage -rfakeroot;

# Install the libewf deb packages
RUN set -eux; \
    dpkg -i ~/src/*.deb;

# Copy and apply pyewf patch, then build and install Python bindings
COPY lef/patches/adding-get-file-type-to-pyewf.patch /tmp/
RUN set -eux; \
    cd ~/src/libewf-${LIBEWF_VERSION}; \
    patch -p0 < /tmp/adding-get-file-type-to-pyewf.patch; \
    make -C pyewf install;

# Set PYTHONPATH
ENV PYTHONPATH="/usr/local/lib/python3.10/site-packages:${PYTHONPATH}"

# Add LEF tool
COPY lef /opt/lef
